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