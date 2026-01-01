from sqlalchemy import create_engine
from sqlalchemy import event

DATABASE_URL = "sqlite:///.db/books.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,           # shows SQL (good for learning/debug)
    future=True
)

@event.listens_for(engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
