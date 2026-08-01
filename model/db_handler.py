from sqlalchemy import create_engine

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class BookBase(Base):
    __tablename__ = 'book_catalog'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    author: Mapped[str] = mapped_column()
    publisher: Mapped[str] = mapped_column()
    circulation: Mapped[int] = mapped_column()
    number_of_volumes: Mapped[int] = mapped_column()
    total_volumes: Mapped[int] = mapped_column()


from sqlalchemy.orm import sessionmaker

from sqlalchemy import select


from pathlib import Path
from typing import Dict, List


def get_filepath(file_name: str) -> Path:
    current_module_dir = Path(__file__).resolve().parent
    project_root = current_module_dir.parent
    data_dir = project_root / "data"
    # Создаем папку data, если её нет (parents=True создаст и промежуточные папки)
    # exist_ok=True предотвратит ошибку, если папка уже есть
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / file_name


class DatabaseManager:
    def __init__(self):
        self._engines = {}
        self._sessions = {}

    def get_session(self, filename: str):

        if filename not in self._engines:
            engine = create_engine(f"sqlite:///{get_filepath(filename)}", echo=True)
            Base.metadata.create_all(engine)
            self._engines[filename] = engine
            self._sessions[filename] = sessionmaker(engine)

        return self._sessions[filename]()

    def close_all(self):
        for engine in self._engines.values():
            engine.dispose()
        self._engines.clear()
        self._sessions.clear()


class DatabaseHandler:
    def __init__(self, filename: str = "catalog_example.db"):
        self.filename = filename
        self._manager=DatabaseManager()

    def get_books(self, filename: str) -> List[Dict[str, str]]:
        with self._manager.get_session(filename) as session:
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

    def replace_all(self, filename: str, books_list: list[dict]) -> None:
        with self._manager.get_session(filename) as session:
            try:
                for b in books_list:
                    new_book = BookBase(
                        name=b.get("name", ""),
                        author=b.get("author", ""),
                        publisher=b.get("publisher", ""),
                        circulation=int(b.get("circulation", 0)),
                        number_of_volumes=int(b.get("number_of_volumes", 0)),
                        total_volumes=int(b.get("total_volumes", 0))
                    )
                    session.merge(new_book)
            except:
                session.rollback()
                raise
            else:
                session.commit()

    def close_all_connections(self):
        """
        Публичный метод для безопасного закрытия всех соединений.
        Скрывает внутреннюю реализацию (_manager) от внешнего мира.
        """
        self._manager.close_all()
