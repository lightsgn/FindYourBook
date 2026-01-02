from sqlalchemy.engine.row import Row

from app.db.session import SessionLocal
from app.model.book import Book
from app.repo.fyb_repo import Repository


def book_from_rows(rows: list[Row]) -> list[Book]:
    books = [book_from_row(row) for row in rows]
    return books


class MatchingService:
    def __init__(self):
        self.db = SessionLocal()
        self.repo = Repository(self.db)

    def get_possible_books(self, title):
        return self.repo.search_books_by_title(title)


    def recommend_by_tags(self, entered_books) -> list[Book]:
        tags_and_counts = self.collect_tags(entered_books)
        book_ids_and_scores = self.repo.get_books_for_weighted_tags(tags_and_counts)
        book_ids_and_scores.sort(key=lambda t: t[1], reverse=True)
        books = [self.repo.get_book_by_id(row[0]).title for row in book_ids_and_scores]
        return books

    def collect_tags(self, entered_books: list[Book]) -> dict[int, int]:
        eb_ids = [b.id for b in entered_books]
        tags_and_counts = self.repo.get_tag_ids_and_counts_for_books(eb_ids)
        return tags_and_counts

    def get_users_books(self, user_id):
        return [r for r in self.repo.get_books_for_user(user_id)]


def book_from_row(row: Row) -> Book:
    return Book(
        id=row[0],
        title=row[1]
    )