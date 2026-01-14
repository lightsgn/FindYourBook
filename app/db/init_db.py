from app.db.engine import engine
from app.model.base import Base

# Importlar kalsın, base'e registerlamaları için gerekli
from app.model.user import User
from app.model.book import Book
from app.model.tag import Tag
from app.model.book_tag import BookTag
from app.model.user_book import UserBook


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
