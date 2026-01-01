from sqlalchemy import Column, Integer, String
from app.model.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=False)


    def __str__(self):
        return f"User:[{self.id} {self.name}]"

    def __repr__(self):
        return f"User:[{self.id} {self.name}]"
