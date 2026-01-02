from typing import Optional, List, Tuple

from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session
from sqlalchemy import select, func, case, distinct

from app.model.user import User
from app.model.book import Book
from app.model.tag import Tag
from app.model.book_tag import BookTag
from app.model.user_book import UserBook


class Repository:
    def __init__(self, db: Session):
        self.db = db

    # =======================
    # USERS
    # =======================

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_user_by_name(self, name: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.name == name)
            .first()
        )

    def create_user(self, name: str, password_hash: str, email: str) -> User:
        user = User(
            name=name,
            password_hash=password_hash,
            email=email
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # =======================
    # BOOKS
    # =======================

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        return self.db.get(Book, book_id)

    def search_books_by_title(
        self,
        query: str,
        limit: int = 10
    ) -> List[Book]:
        return (
            self.db.query(Book)
            .filter(Book.title.ilike(f"%{query}%"))
            .limit(limit)
            .all()
        )

    def get_books_by_ids(self, book_ids: list[int]) -> List[Book]:
        if not book_ids:
            return []

        return (
            self.db.query(Book)
            .filter(Book.id.in_(book_ids))
            .all()
        )

    # =======================
    # TAGS
    # =======================

    def get_tag_by_id(self, tag_id: int) -> Optional[Tag]:
        return self.db.get(Tag, tag_id)

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        return (
            self.db.query(Tag)
            .filter(Tag.name == name)
            .first()
        )

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
        self.db.merge(
            BookTag(book_id=book_id, tag_id=tag_id)
        )
        self.db.commit()

    def get_tag_ids_for_books(self, book_ids: list[int]) -> list[int]:
        if not book_ids:
            return []

        rows = (
            self.db.query(distinct(BookTag.tag_id))
            .filter(BookTag.book_id.in_(book_ids))
            .all()
        )
        return [row[0] for row in rows]

    def get_tag_ids_and_counts_for_books(
        self,
        book_ids: list[int]
    ) -> dict[int, int]:
        if not book_ids:
            return {}

        rows = (
            self.db.query(
                BookTag.tag_id,
                func.count().label("cnt")
            )
            .filter(BookTag.book_id.in_(book_ids))
            .group_by(BookTag.tag_id)
            .order_by(func.count().desc())
            .all()
        )

        return {tag_id: cnt for tag_id, cnt in rows}

    def get_book_ids_for_tags(self, tag_ids: list[int]) -> list[int]:
        if not tag_ids:
            return []

        rows = (
            self.db.query(distinct(BookTag.book_id))
            .filter(BookTag.tag_id.in_(tag_ids))
            .all()
        )
        return rows

    def get_books_for_weighted_tags( self, tag_counts: dict[int, int]) -> list[Row]:
        if not tag_counts:
            return []

        weight_case = case(
            tag_counts,
            value=BookTag.tag_id,
            else_=0
        )

        query = (
            self.db.query(
                BookTag.book_id,
                func.sum(weight_case).label("score")
            )
            .filter(BookTag.tag_id.in_(tag_counts.keys()))
            .group_by(BookTag.book_id)
            .order_by(func.sum(weight_case).desc())
        )

        return query.all()

    # =======================
    # USER <-> BOOK (RATINGS)
    # =======================

    def get_books_for_user(self, user_id: int) -> List[UserBook]:
        return (
            self.db.query(UserBook)
            .filter(UserBook.user_id == user_id)
            .all()
        )

    def get_book_titles_and_ratings_for_user(self, user_id: int) -> List[Tuple[int, str, int]]:
        rows = (
            self.db.query(
                Book.id,
                Book.title,
                UserBook.rating
            )
            .join(UserBook, Book.id == UserBook.book_id)
            .filter(UserBook.user_id == user_id)
            .order_by(Book.title)
            .all()
        )

        return rows  # [(id, title, rating)]

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

    def get_or_create_book(self, title: str) -> Book:
        book = (
            self.db.query(Book)
            .filter(func.lower(Book.title) == func.lower(title))
            .first()
        )

        if book:
            return book

        book = Book(title=title)
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book


    # =======================
    # COLLABORATIVE FILTERING SUPPORT
    # =======================
    def get_books_liked_by_users_with_counts(
            self,
            user_ids: list[int],
            min_rating: int = 4,
            exclude_book_ids: list[int] = []
    ) -> list[tuple[int, int]]:
        if not user_ids:
            return []

        query = (
            self.db.query(
                UserBook.book_id,
                func.count().label("cnt")
            )
            .filter(
                UserBook.user_id.in_(user_ids),
                UserBook.rating >= min_rating
            )
            .group_by(UserBook.book_id)
            .order_by(func.count().desc())
        )

        if exclude_book_ids:
            query = query.filter(~UserBook.book_id.in_(exclude_book_ids))

        return query.all()  # [(book_id, count)]

    def get_users_who_liked_books(
        self,
        book_ids: list[int],
        min_rating: int = 4
    ) -> list[int]:
        if not book_ids:
            return []

        rows = (
            self.db.query(distinct(UserBook.user_id))
            .filter(
                UserBook.book_id.in_(book_ids),
                UserBook.rating >= min_rating
            )
            .all()
        )
        return [row[0] for row in rows]

    def get_books_liked_by_users(
        self,
        user_ids: list[int],
        min_rating: int = 4
    ) -> list[int]:
        if not user_ids:
            return []

        rows = (
            self.db.query(distinct(UserBook.book_id))
            .filter(
                UserBook.user_id.in_(user_ids),
                UserBook.rating >= min_rating
            )
            .all()
        )
        return [row[0] for row in rows]
