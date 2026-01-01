from app.db.session import SessionLocal
from app.model.user import User
from app.repo.fyb_repo import Repository


class SecurityService:

    def get_user_by_name(self, username):
        db = SessionLocal()
        repo = Repository(db)
        user = repo.get_user_by_name(username)
        db.close()
        return user

    def create_user(self, username, password_hash, email):
        db = SessionLocal()
        repo = Repository(db)
        user = repo.create_user(username, password_hash, email)
        db.close()
        return user
