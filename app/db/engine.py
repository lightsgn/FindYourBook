from sqlalchemy import create_engine
from sqlalchemy import event


engine = create_engine(
    url="sqlite:///database/books.db",  # .db yerine database yazdık
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
