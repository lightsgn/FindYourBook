from sqlalchemy import Column, Integer, String
from app.model.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    def __str__(self):
        return f"Tag:[{self.id} {self.name}]"

    def __repr__(self):
        return f"Tag:[{self.id} {self.name}]"