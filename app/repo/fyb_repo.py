from sqlalchemy.orm import Session
from sqlalchemy import func

from app.model.user import User
from app.model.book import Book
from app.model.tag import Tag
from app.model.user_book import UserBook
from app.model.book_tag import BookTag


class Repository:
    def __init__(self, db: Session):
        self.db = db

    # =======================
    # USERS
    # =======================

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_name(self, name: str) -> User | None:
        return self.db.query(User).filter(User.name == name).first()

    def create_user(self, name: str, password_hash: str, email: str) -> User:
        user = User(name=name, password_hash=password_hash, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # =======================
    # BOOKS
    # =======================

    def get_book_by_id(self, book_id: int) -> Book | None:
        return self.db.query(Book).filter(Book.id == book_id).first()

    def search_books_by_title(self, query: str, limit: int = 10) -> list[Book]:
        return (
            self.db.query(Book)
            .filter(Book.title.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )

    def get_books_by_ids(self, book_ids: list[int]) -> list[Book]:
        return self.db.query(Book).filter(Book.id.in_(book_ids)).all()

    # =======================
    # TAGS
    # =======================

    def get_tag_by_id(self, tag_id: int) -> Tag | None:
        return self.db.query(Tag).filter(Tag.id == tag_id).first()

    def get_tag_by_name(self, name: str) -> Tag | None:
        return self.db.query(Tag).filter(Tag.name == name).first()

    def create_tag(self, name: str) -> Tag:
        tag = Tag(name=name)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    # =======================
    # BOOK <-> TAG
    # =======================

    def add_tag_to_book(self, book_id: int, tag_id: int) -> None:
        bt = BookTag(book_id=book_id, tag_id=tag_id)
        self.db.add(bt)
        self.db.commit()

    def get_tag_ids_for_books(self, book_ids: list[int]) -> list[int]:
        rows = (
            self.db.query(BookTag.tag_id)
            .filter(BookTag.book_id.in_(book_ids))
            .all()
        )
        return [row[0] for row in rows]

    def get_book_ids_for_tags(self, tag_ids: list[int]) -> list[int]:
        rows = (
            self.db.query(BookTag.book_id)
            .filter(BookTag.tag_id.in_(tag_ids))
            .all()
        )
        return [row[0] for row in rows]

    # =======================
    # USER <-> BOOK (RATINGS)
    # =======================

    def get_books_for_user(self, user_id: int) -> list[UserBook]:
        return (
            self.db.query(UserBook)
            .filter(UserBook.user_id == user_id)
            .all()
        )

    def add_or_update_user_book(
        self,
        user_id: int,
        book_id: int,
        rating: int
    ) -> None:
        entry = (
            self.db.query(UserBook)
            .filter(
                UserBook.user_id == user_id,
                UserBook.book_id == book_id
            )
            .first()
        )

        if entry:
            entry.rating = rating
        else:
            entry = UserBook(
                user_id=user_id,
                book_id=book_id,
                rating=rating
            )
            self.db.add(entry)

        self.db.commit()

    def delete_user_book(self, user_id: int, book_id: int) -> None:
        (
            self.db.query(UserBook)
            .filter(
                UserBook.user_id == user_id,
                UserBook.book_id == book_id
            )
            .delete()
        )
        self.db.commit()

    # =======================
    # COLLABORATIVE FILTERING SUPPORT
    # =======================

    def get_users_who_liked_books(
        self,
        book_ids: list[int],
        min_rating: int = 4
    ) -> list[int]:
        rows = (
            self.db.query(UserBook.user_id)
            .filter(
                UserBook.book_id.in_(book_ids),
                UserBook.rating >= min_rating
            )
            .distinct()
            .all()
        )
        return [row[0] for row in rows]

    def get_books_liked_by_users(
        self,
        user_ids: list[int],
        min_rating: int = 4
    ) -> list[int]:
        rows = (
            self.db.query(UserBook.book_id)
            .filter(
                UserBook.user_id.in_(user_ids),
                UserBook.rating >= min_rating
            )
            .distinct()
            .all()
        )
        return [row[0] for row in rows]
