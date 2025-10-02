from fastapi import FastAPI
from . import models
from .database import engine
from .routers import auth, document, query

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth.router)
app.include_router(document.router)
app.include_router(query.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
