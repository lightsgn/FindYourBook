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

        book_ids_and_scores = self.repo.get_books_for_weighted_tags(tag_counts, entered_ids)
        book_ids_and_scores.sort(key=lambda t: t[1], reverse=True)

        return [
            self.repo.get_book_by_id(book_id).title
            for book_id, _ in book_ids_and_scores
        ]

    def _collect_tags(self, books: list[Book]) -> dict[int, int]:
        book_ids = [book.id for book in books]
        return self.repo.get_tag_ids_and_counts_for_books(book_ids)

    def get_users_books(self, user_id: int):
        return self.repo.get_books_for_user(user_id)