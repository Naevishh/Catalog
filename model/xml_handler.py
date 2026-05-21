import uuid
import xml.sax
from pathlib import Path
from typing import Dict, List, Optional
from xml.dom import minidom


def get_filepath(file_name: str) -> Path:
    current_module_dir = Path(__file__).resolve().parent
    project_root = current_module_dir.parent
    data_dir = project_root / "data"
    if not data_dir.exists():
        data_dir = current_module_dir / "data"
    return data_dir / file_name


class XMLInitializer:
    def __init__(self, filename: str, root_tag: str = "catalog"):
        self.filepath = get_filepath(filename)
        self.root_tag = root_tag
        self._ensure_initialized()

    def _ensure_initialized(self) -> None:
        if self.filepath.exists():
            return
        else:
            print("file doesnt exist!!")

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
                self.current_field = None  # Сбрасываем только когда поле действительно закрыто

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


# (Facade)
class XMLHandler:
    def __init__(self, filename: str = "catalog_example.xml", root_tag: str = "catalog"):
        self.filename = filename
        self.root_tag = root_tag

        # 1. Гарантируем создание файла
        XMLInitializer(filename, root_tag)

        # 2. Создаём компоненты чтения и записи
        self._reader = XMLBookReader(filename)
        self._writer = XMLBookWriter(filename, root_tag)

    def get_books(self) -> List[Dict[str, str]]:
        """Возвращает список книг из файла."""
        return self._reader.parse()

    def add_book(self, book_data: Dict[str, str]) -> None:
        """Добавляет книгу в DOM-дерево (без сохранения на диск)."""
        self._writer.add_book(book_data)

    def save(self) -> None:
        """Фиксирует изменения в файле."""
        self._writer.save()

    def reload(self) -> None:
        """Перезагружает DOM из файла (полезно, если файл изменился извне)."""
        self._writer = XMLBookWriter(self.filename, self.root_tag)

    # в xml_handler.py, внутри класса CatalogManager
    def replace_all(self, books_list: list[dict]) -> None:
        """Полностью заменяет содержимое каталога новыми данными."""
        root = self._writer.doc.documentElement
        # Удаляем все старые <book>
        for old in root.getElementsByTagName('book'):
            old.parentNode.removeChild(old)
        # Добавляем новые
        for data in books_list:
            self._writer.add_book(data)

# if __name__ == "__main__":
#     # # Пример XML-данных
#     # xml_data = """
#     # <catalog>
#     #     <book id="1" category="books">
#     #         <title>Python Basics</title>
#     #         <author>John Doe</author>
#     #     </book>
#     #     <book id="2" category="electronics">
#     #         <title>Laptop</title>
#     #         <author>Jane Smith</author>
#     #     </book>
#     # </catalog>
#     # """
#
#     real_books = [
#         # Русская классика
#         ('Война и мир', 'Лев Толстой', 'Эксмо', 4, 50000),
#         ('Преступление и наказание', 'Фёдор Достоевский', 'АСТ', 1, 30000),
#         ('Анна Каренина', 'Лев Толстой', 'Азбука', 2, 25000),
#         ('Мастер и Маргарита', 'Михаил Булгаков', 'Эксмо', 1, 100000),
#         ('Тихий Дон', 'Михаил Шолохов', 'АСТ', 4, 20000),
#         ('Доктор Живаго', 'Борис Пастернак', 'Азбука', 1, 15000),
#         ('Отцы и дети', 'Иван Тургенев', 'Просвещение', 1, 50000),
#         ('Герой нашего времени', 'Михаил Лермонтов', 'Дрофа', 1, 40000),
#         ('Мёртвые души', 'Николай Гоголь', 'Эксмо', 1, 35000),
#         ('Евгений Онегин', 'Александр Пушкин', 'Просвещение', 1, 100000)]
