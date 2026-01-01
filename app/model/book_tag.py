from sqlalchemy import Column, Integer, ForeignKey
from app.model.base import Base


class BookTag(Base):
    __tablename__ = "book_tags"

    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        primary_key=True
    )
    tag_id = Column(
        Integer,
        ForeignKey("tags.id"),
        primary_key=True
    )
