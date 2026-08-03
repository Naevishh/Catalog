import uuid
import xml.sax
from typing import Dict, List, Optional
from xml.dom import minidom

from utils.get_filepath import get_filepath


class XMLInitializer:
    def __init__(self, filename: str, root_tag: str = "catalog"):
        self.filepath = get_filepath(filename)
        self.root_tag = root_tag
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        if self.filepath.exists():
            return

        doc = minidom.Document()
        root = doc.createElement(self.root_tag)
        doc.appendChild(root)
        self.filepath.write_text(doc.toprettyxml(indent="  "), encoding="utf-8")


class XMLBookReader:
    def __init__(self, filename: str):
        self.filepath = get_filepath(filename)

    class _BookHandler(xml.sax.ContentHandler):
        def __init__(self):
            self.books: List[Dict[str, str]] = []
            self.current_book: Optional[Dict[str, str]] = None
            self.current_field: Optional[str] = None
            self.char_buffer: List[str] = []

        def startElement(self, tag, attrs):
            if tag == "book":
                self.current_book = {"id": attrs.get("id", "")}
            else:
                self.current_field = tag
                self.char_buffer = []

        def characters(self, content):
            if self.current_field:
                self.char_buffer.append(content)

        def endElement(self, tag):
            if tag == "book" and self.current_book:
                self.books.append(self.current_book)
                self.current_book = None
            elif self.current_book is not None and self.current_field == tag:
                self.current_book[tag] = "".join(self.char_buffer).strip()
                self.current_field = None

    def parse(self) -> List[Dict[str, str]]:
        parser = xml.sax.make_parser()
        handler = self._BookHandler()
        parser.setContentHandler(handler)
        parser.parse(str(self.filepath))
        return handler.books


class XMLBookWriter:
    def __init__(self, filename: str, root_tag: str = "catalog"):
        self.filepath = get_filepath(filename)
        self.root_tag = root_tag
        self.doc = minidom.parse(str(self.filepath))

    def create_book(self, **kwargs) -> minidom.Element:
        """Создаёт элемент <book> и возвращает его, не добавляя в документ."""
        book = self.doc.createElement('book')
        book_id = kwargs.pop('id', str(uuid.uuid4())[:8])
        book.setAttribute('id', book_id)

        for tag_name, value in kwargs.items():
            el = self.doc.createElement(tag_name)
            el.appendChild(self.doc.createTextNode(str(value)))
            book.appendChild(el)
        return book

    def add_book(self, book_data: Dict[str, str]) -> None:
        book = self.create_book(**book_data)
        self.doc.documentElement.appendChild(book)

    def save(self) -> None:
        """Сохраняет текущее состояние DOM обратно в файл."""
        self.filepath.write_text(self.doc.toprettyxml(indent="  "), encoding="utf-8")


class XMLHandler:
    def __init__(self, filename: str = "catalog_example.xml", root_tag: str = "catalog"):
        self.filename = filename
        self.root_tag = root_tag

        XMLInitializer(filename, root_tag)

        self._reader = XMLBookReader(filename)
        self._writer = XMLBookWriter(filename, root_tag)

    def get_books(self) -> List[Dict[str, str]]:
        """Возвращает список книг из файла."""
        return self._reader.parse()

    def add_book(self, book_data: Dict[str, str]) -> None:
        """Добавляет книгу в DOM-дерево."""
        self._writer.add_book(book_data)

    def save(self) -> None:
        """Фиксирует изменения в файле."""
        self._writer.save()

    def reload(self) -> None:
        """Перезагружает DOM из файла."""
        self._writer = XMLBookWriter(self.filename, self.root_tag)

    def replace_all(self, books_list: list[dict]) -> None:
        """Полностью заменяет содержимое каталога новыми данными."""
        root = self._writer.doc.documentElement

        for old in root.getElementsByTagName('book'):
            old.parentNode.removeChild(old)

        for data in books_list:
            self._writer.add_book(data)
