from typing import Any

from flask import session
from sqlalchemy.engine.row import Row

from app.db.session import SessionLocal
from app.model.book import Book
from app.repo.fyb_repo import Repository


def book_from_row(row: Row) -> Book:
    return Book(
        id=row[0],
        title=row[1],
    )


def books_from_rows(rows: list[Row]) -> list[Book]:
    return [book_from_row(row) for row in rows]


class MatchingService:
    def __init__(self):
        self.db = SessionLocal()
        self.repo = Repository(self.db)

    def get_possible_books(self, title: str):
        return self.repo.search_books_by_title(title)

    def recommend_by_tags(self, entered_books: list[Book]) -> list[str]:
        tag_counts = self._collect_tags(entered_books)
        entered_ids = [b.id for b in entered_books]

        book_ids_and_scores = self.repo.get_books_for_weighted_tags(tag_counts)
        filtered_books_scores = [bs for bs in book_ids_and_scores if bs[0] not in entered_ids]
        filtered_books_scores.sort(key=lambda t: t[1], reverse=True)

        return [
            self.repo.get_book_by_id(book_id).title
            for book_id, _ in filtered_books_scores
        ]

    def _collect_tags(self, books: list[Book]) -> dict[int, int]:
        book_ids = [book.id for book in books]
        return self.repo.get_tag_ids_and_counts_for_books(book_ids)

    def get_users_books(self, user_id: int) -> list[Any] | list[tuple[Book, int]]:
        titles_and_ratings = self.repo.get_book_titles_and_ratings_for_user(user_id)
        books_and_ratings =[tuple((Book(id=row[0], title=row[1]), row[2])) for row in titles_and_ratings]

        if not books_and_ratings:
            return []

        return books_and_ratings

    def recommend_by_users(self, current_user_id, entered_books: list[Book]) -> list[Book]:
        entered_book_ids = [b.id for b in entered_books]

        # Find similar users
        similar_user_ids = self.repo.get_users_who_liked_books(entered_book_ids, min_rating=4)

        #Exclude books user already knows
        user_books = self.repo.get_books_for_user(current_user_id)
        excluded_ids = {ub.book_id for ub in user_books}
        excluded_ids.update(entered_book_ids)

        #Get ranked book IDs
        book_ids_and_counts = self.repo.get_books_liked_by_users_with_counts(
            similar_user_ids,
            min_rating=4,
        )
        filtered_books_counts = [bc for bc in book_ids_and_counts if bc[0] not in excluded_ids]

        # Convert to Book objects
        books = [
            self.repo.get_book_by_id(book_id).title+" ("+str(count)+")"
            for book_id, count in filtered_books_counts
        ]

        return books

    def remove_book_from_user(self, user_id: int, book_id: int):
        self.repo.delete_user_book(user_id, book_id)