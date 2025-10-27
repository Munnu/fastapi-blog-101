from pathlib import Path
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# got this from a google gemini ai inquiry.
# changing how to access the blog.db file because what happens if I run tests or am in production
# and something is trying to connect to the db from a different current working directory
THIS_FILE_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT_DIR = THIS_FILE_DIR.parent

sqlite_file_name = "blog.db"
sqlite_db_path = PROJECT_ROOT_DIR / sqlite_file_name
sqlite_url = f"sqlite:///{sqlite_db_path.as_uri().replace('file://', '', 1)}"
# ~~~ end changes

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]