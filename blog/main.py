import contextlib
from typing import Sequence

from fastapi import FastAPI, HTTPException
from sqlmodel import select

from .database import SessionDep, create_db_and_tables
from . import schemas, models

# --- Lifespan Function (The New Home for create_db_and_tables) ---
# got this from a google gemini ai inquiry.
# Use an async context manager for the lifespan
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # This block runs BEFORE the application starts (on startup)
    print("Application Startup: Creating database tables...")
    create_db_and_tables()
    yield
    # This block runs AFTER the application shuts down (on shutdown)
    print("Application Shutdown: Cleaning up resources...")
    # Add any shutdown code here, e.g., closing a non-pooled connection if needed
# ------------------------------------------------------------------

app = FastAPI(lifespan=lifespan) # pass the lifespan function to FastAPI

@app.get("/")
def read_root(session: SessionDep):
    # The session is automatically created and closed thanks to SessionDep
    return {"message": "Hello from your SQLModel/FastAPI app!"}

@app.post('/blog')
def create_a_blog_entry(request: schemas.Blog, db: SessionDep) -> models.Blog:
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get('/blog')
def show_all_blog_entries(db: SessionDep) -> Sequence[models.Blog]:
    blogs = db.exec(select(models.Blog)).all()
    return blogs

@app.get('/blog/{blog_id}')
def show_a_blog_entry(blog_id: int, db: SessionDep) -> models.Blog:
    blog = db.get(models.Blog, blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return blog
