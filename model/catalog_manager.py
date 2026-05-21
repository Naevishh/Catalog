from typing import Optional, List
from .book import Book  # Убедитесь, что импорт правильный
from .xml_handler import XMLHandler


class CatalogManager:
    def __init__(self, xml_handler: XMLHandler):
        self.xml_handler = xml_handler
        self.books: List[Book] = []
        self.observers = []

    # --- Загрузка/Сохранение ---

    def load_from_xml(self) -> None:
        raw_books = self.xml_handler.get_books()
        self.books = [self._to_book(d) for d in raw_books]
        # Уведомляем view, что данные загружены
        # self.notify_observers()

    def save_to_xml(self) -> None:
        raw_books = [self._to_dict(b) for b in self.books]
        self.xml_handler.replace_all(raw_books)
        self.xml_handler.save()

    # --- Конвертация ---

    @staticmethod
    def _to_book(d: dict) -> Book:
        # Внимание: проверьте имена полей в вашем классе Book!
        # Предположим, что в Book поля: book_id, name, author, publisher, volumes, circulation
        return Book(
            name=d.get("name", ""),
            author=d.get("author", ""),
            publisher=d.get("publisher", ""),
            circulation=int(d.get("circulation", 0)),
            volumes=int(d.get("number_of_volumes", 0)),  # Маппинг XML key -> Model field
            # total_volumes вычисляемое, его можно не хранить или хранить для скорости
        )

    @staticmethod
    def _to_dict(b: Book) -> dict:
        return {
            "id": b.book_id,
            "name": b.name,
            "author": b.author,
            "publisher": b.publisher,
            "circulation": str(b.circulation),
            "number_of_volumes": str(b.volumes),
            # total_volumes можно не сохранять, если он вычисляется,
            # но если требует задание - сохраняем:
            "total_volumes": str(b.total_volumes)
        }

    # --- Бизнес-логика ---

    def add_book(self, name: str, author: str, publisher: str,
                 circulation: int, number_of_volumes: int) -> None:

        new_book = Book(
            name=name,
            author=author,
            publisher=publisher,
            circulation=circulation,
            volumes=number_of_volumes,
        )
        self.books.append(new_book)

    def delete_by_criteria(self, **kwargs) -> int:
        """
        Удаляет книги, подходящие под критерии.
        Возвращает количество удаленных записей.
        """
        books_to_delete = self.find_book(**kwargs)
        if not books_to_delete:
            return 0

        ids_to_remove = {b.book_id for b in books_to_delete}
        initial_count = len(self.books)

        # Оставляем только те книги, которых нет в списке на удаление
        self.books = [b for b in self.books if b.book_id not in ids_to_remove]

        deleted_count = initial_count - len(self.books)

        # if deleted_count > 0:
            # self.notify_observers()  # <--- ВАЖНО: Сообщаем об изменении
            #self.save_to_xml()  # <--- Опционально: автосохранение

        return deleted_count

    def find_book(self,
                  name: Optional[str] = None,
                  author: Optional[str] = None,
                  publisher: Optional[str] = None,
                  circulation_limit: Optional[tuple] = None,  # ('<'|'>', value)
                  volumes_range: Optional[tuple] = None,  # (min, max)
                  total_volumes_limit: Optional[tuple] = None  # ('<'|'>', value)
                  ) -> List[Book]:

        result = []
        for book in self.books:
            # 1. Поиск по имени (подстрока)
            if name and name.lower() not in book.name.lower():
                continue

            # 2. Поиск по автору (подстрока, как чаще всего требуется)
            if author and author.lower() not in book.author.lower():
                continue

            # 3. Поиск по издательству (точное совпадение или подстрока? Лучше подстрока)
            if publisher and publisher.lower() not in book.publisher.lower():
                continue

            # 4. Диапазон томов
            if volumes_range:
                low, high = volumes_range
                if low is not None and book.volumes < low:
                    continue
                if high is not None and book.volumes > high:
                    continue

            # 5. Тираж (больше/меньше)
            if circulation_limit:
                op, val = circulation_limit
                if op == '<' and not (book.circulation < val):
                    continue
                if op == '>' and not (book.circulation > val):
                    continue

            # 6. Итого томов (больше/меньше)
            if total_volumes_limit:
                op, val = total_volumes_limit
                if op == '<' and not (book.total_volumes < val):
                    continue
                if op == '>' and not (book.total_volumes > val):
                    continue

            result.append(book)

        return result