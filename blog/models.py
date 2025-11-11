from sqlmodel import Field, SQLModel


class Blog(SQLModel, table=True):
    __tablename__ = "blogs"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)
    title: str
    body: str
