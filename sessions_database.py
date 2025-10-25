from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import String, create_engine

class Base(DeclarativeBase):
	pass

class SessionBase(Base):
	__tablename__ = "sessions"
	
	id: Mapped[int] = mapped_column(primary_key=True)
	session_id: Mapped[str] = mapped_column(String(256))
	task: Mapped[str] = mapped_column(String(256))
	flag: Mapped[str] = mapped_column(String(256))
	last_activity: Mapped[str] = mapped_column(String(256))
	

engine = create_engine("sqlite:///db/sessionbase.db", echo=True)
def create_db_and_tables() -> None:
	Base.metadata.create_all(engine)

if __name__ == "__main__":
	create_db_and_tables()