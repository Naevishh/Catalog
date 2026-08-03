from model.db_handler import engine

from model.book_base import Base

def init_database():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_database()