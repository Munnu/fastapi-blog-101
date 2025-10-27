from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

@app.get("/")
def index():
    return {'data': 'blog list'}

@app.get('/blog')
def published(limit: int | None, published: bool = False, sort: str | None = None):
    if published:
        return {'data': f'{limit} published blogs from the db'}
    
    # only get 10 of all blogs
    return {'data': f'{limit} blogs from the db'}

@app.get('/blog/unpublished')
def unpublished():
    return {'data': 'all unpublished blogs'}

@app.get("/blog/{id}")
def show(id: int):
    return {'data': id}

@app.get('/blog/{id}/comments')
def comments(id: int, limit=10):
    return {'data': {'1', '2'}, 'limit': limit}

class Blog(BaseModel):
    title: str
    body: str
    published: bool | None = None

@app.post('/blog')
def create_blog(request: Blog):
    return {'data': f'blog is created with title as {request.title}'}

   