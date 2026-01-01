from sqlalchemy import Column, Integer, String
from app.model.base import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

    def __str__(self):
        return f"Book:[{self.id} {self.title}]"

    def __repr__(self):
        return f"Book:[{self.id} {self.title}]"