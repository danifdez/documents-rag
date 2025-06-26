from fastapi import FastAPI
from routers import ingest
from routers import search

app = FastAPI()

app.include_router(ingest.router)
app.include_router(search.router)