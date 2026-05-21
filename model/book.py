# model/book.py
import uuid


class Book:
    """
    MODEL (Доменный объект книги - Вариант 15)
    Отвечает за:
    1. Структуру данных и строгую типизацию
    2. Вычисляемые поля (итого томов)
    3. Подготовка данных для XML-сериализации (DOM/SAX)
    """

    def __init__(self, name: str, author: str, publisher: str,
                 circulation: int, volumes: int, book_id: str = None):

        # Быстрая проверка типов и диапазонов (fail-fast при загрузке из файла)
        if not isinstance(name, str) or len(name.strip()) < 2:
            raise ValueError("Название: строка, минимум 2 символа")
        if not isinstance(author, str) or len(author.strip()) < 3:
            raise ValueError("Автор: строка, минимум 3 символа")
        if not isinstance(publisher, str) or len(publisher.strip()) < 2:
            raise ValueError("Издательство: строка, минимум 2 символа")
        if not (1 <= int(circulation) <= 10_000_000):
            raise ValueError("Тираж: целое число от 1 до 10 000 000")
        if not (1 <= int(volumes) <= 1000):
            raise ValueError("Число томов: целое число от 1 до 1000")

        self.book_id = book_id or str(uuid.uuid4())[:8]
        self.name = name.strip()
        self.author = author.strip()
        self.publisher = publisher.strip()
        self.circulation = int(circulation)
        self.volumes = int(volumes)

    @property
    def total_volumes(self) -> int:
        """Итого томов = Число томов × Тираж (вычисляется автоматически)"""
        return self.volumes * self.circulation

    def to_dict(self) -> dict:
        """Для DOM-парсера при сохранении в XML"""
        return {
            "id": self.book_id,
            "name": self.name,
            "author": self.author,
            "publisher": self.publisher,
            "volumes": self.volumes,
            "circulation": self.circulation,
            "total_volumes": self.total_volumes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Book":
        """Для SAX-парсера при загрузке из XML"""
        return cls(
            name=data["name"],
            author=data["author"],
            publisher=data["publisher"],
            circulation=int(data["circulation"]),
            volumes=int(data["volumes"]),
            book_id=data.get("id")
        )

    def __repr__(self):
        return f"Book('{self.name}', '{self.author}', {self.total_volumes} экз.)"


insertion_query = ([
    {
        "book_name": "Война и мир",
        "book_author": "Лев Толстой",
        "book_publisher": "Эксмо",
        "book_circulation": 150_000,
        "book_volumes_number": 4,
        "book_total_volumes": 150_000 * 4
    },
    {
        "book_name": "Преступление и наказание",
        "book_author": "Фёдор Достоевский",
        "book_publisher": "АСТ",
        "book_circulation": 200_000,
        "book_volumes_number": 1,
        "book_total_volumes": 200_000 * 1
    },
    {
        "book_name": "Мастер и Маргарита",
        "book_author": "Михаил Булгаков",
        "book_publisher": "Рипол Классик",
        "book_circulation": 120_000,
        "book_volumes_number": 1,
        "book_total_volumes": 120_000 * 1
    },
    {
        "book_name": "Анна Каренина",
        "book_author": "Лев Толстой",
        "book_publisher": "Художественная литература",
        "book_circulation": 80_000,
        "book_volumes_number": 2,
        "book_total_volumes": 80_000 * 2
    },
    {
        "book_name": "Евгений Онегин",
        "book_author": "Александр Пушкин",
        "book_publisher": "Просвещение",
        "book_circulation": 300_000,
        "book_volumes_number": 1,
        "book_total_volumes": 300_000 * 1
    }
])
