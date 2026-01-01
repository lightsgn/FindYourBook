from app.db.session import SessionLocal
from app.model.user import User

db = SessionLocal()

user = User(name="robert")
db.add(user)
db.commit()

print(db.query(User).all())

db.close()