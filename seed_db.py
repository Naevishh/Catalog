from model.db_handler import SessionLocal
from model.book_base import BookBase

sample_books = [
    {
        "name": "1984",
        "author": "Джордж Оруэлл",
        "publisher": "Secker & Warburg",
        "circulation": 500,
        "number_of_volumes": 1,
        "total_volumes": 500       # 500 * 1
    },
    {
        "name": "Мастер и Маргарита",
        "author": "Михаил Булгаков",
        "publisher": "Московский рабочий",
        "circulation": 1000,
        "number_of_volumes": 2,
        "total_volumes": 2000      # 1000 * 2
    },
    {
        "name": "Clean Code",
        "author": "Robert C. Martin",
        "publisher": "Prentice Hall",
        "circulation": 300,
        "number_of_volumes": 1,
        "total_volumes": 300       # 300 * 1
    },
    {
        "name": "Война и мир",
        "author": "Лев Толстой",
        "publisher": "Эксмо",
        "circulation": 200,
        "number_of_volumes": 4,
        "total_volumes": 800       # 200 * 4
    },
    {
        "name": "Гарри Поттер и философский камень",
        "author": "Дж. К. Роулинг",
        "publisher": "Росмэн",
        "circulation": 1500,
        "number_of_volumes": 1,
        "total_volumes": 1500      # 1500 * 1
    },
    {
        "name": "Python Crash Course",
        "author": "Eric Matthes",
        "publisher": "No Starch Press",
        "circulation": 250,
        "number_of_volumes": 1,
        "total_volumes": 250       # 250 * 1
    },
    {
        "name": "Преступление и наказание",
        "author": "Фёдор Достоевский",
        "publisher": "Азбука",
        "circulation": 400,
        "number_of_volumes": 2,
        "total_volumes": 800       # 400 * 2
    },
    {
        "name": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "publisher": "Allen & Unwin",
        "circulation": 150,
        "number_of_volumes": 3,
        "total_volumes": 450       # 150 * 3
    },
    {
        "name": "Алхимик",
        "author": "Пауло Коэльо",
        "publisher": "София",
        "circulation": 800,
        "number_of_volumes": 1,
        "total_volumes": 800       # 800 * 1
    },
    {
        "name": "Грокаем алгоритмы",
        "author": "Адитья Бхаргава",
        "publisher": "Питер",
        "circulation": 600,
        "number_of_volumes": 1,
        "total_volumes": 600       # 600 * 1
    }
]

def seed_database():
    with SessionLocal() as session:
        try:
            session.query(BookBase).delete()
            for b in sample_books:
                new_book = BookBase(
                    name=b.get("name", ""),
                    author=b.get("author", ""),
                    publisher=b.get("publisher", ""),
                    circulation=int(b.get("circulation", 0)),
                    number_of_volumes=int(b.get("number_of_volumes", 0)),
                    total_volumes=int(b.get("total_volumes", 0))
                )
                session.add(new_book)
        except:
            session.rollback()
            raise
        else:
            session.commit()