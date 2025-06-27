from fastapi import FastAPI
from routers import ingest
from routers import search
from routers import ask

app = FastAPI()

app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(ask.router)