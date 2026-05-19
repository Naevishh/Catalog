import uuid

class Book:
    def __init__(self, name: str, author: str, publisher: str, circulation: int, volumes: int):
        self.book_id=str(uuid.uuid4())[:8]
        self.name=name
        self.author=author
        self.publisher=publisher
        self.circulation=circulation
        self.volumes=volumes

    @property
    def total_volumes(self) -> int:
        """Вычисляемое поле: не хранится, а считается автоматически"""
        return self.volumes * self.circulation


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
