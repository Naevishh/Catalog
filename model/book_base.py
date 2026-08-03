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