from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.model.user import User
from app.repo.fyb_repo import Repository


class SecurityService:
    def __init__(self):
        self.db = SessionLocal()
        self.repo = Repository(self.db)

    def get_user_by_name(self, username):
        user = self.repo.get_user_by_name(username)
        self.db.close()
        return user

    def create_user(self, username, password_hash, email):
        user = self.repo.create_user(username, password_hash, email)
        self.db.close()
        return user
