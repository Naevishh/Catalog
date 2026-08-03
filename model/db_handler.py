from typing import Dict, List

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from .book_base import BookBase

engine = create_engine('postgresql://postgres:1234567890@localhost:5432/postgres')

SessionLocal = sessionmaker(bind=engine)

def _cleanup_db():
    engine.dispose()

class DatabaseHandler:
    def get_books(self) -> List[Dict[str, str]]:
        with SessionLocal() as session:
            db_objects = session.scalars(select(BookBase)).all()
            result_books = []
            for ob in db_objects:
                book = {
                    "id": ob.id,
                    "name": ob.name,
                    "author": ob.author,
                    "publisher": ob.publisher,
                    "circulation": str(ob.circulation),
                    "number_of_volumes": str(ob.number_of_volumes),

                    "total_volumes": str(ob.total_volumes)
                }
                result_books.append(book)

            return result_books

    def replace_all(self, books_list: list[dict]) -> None:
        with SessionLocal() as session:
            try:
                session.query(BookBase).delete()
                for b in books_list:
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