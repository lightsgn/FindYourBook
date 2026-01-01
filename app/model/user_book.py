from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from app.model.base import Base


class UserBook(Base):
    __tablename__ = "user_books"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True
    )
    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        primary_key=True
    )
    rating = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="rating_range"
        ),
    )
