from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {'data': {'name': 'Bitfumes', 'course': 'FastAPI Tutorial'}}

@app.get("/about")
def about():
    return {'data': 'This is a FastAPI tutorial by Bitfumes.'}

