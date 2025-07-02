from fastapi import FastAPI
from routers import ingest
from routers import search
from routers import ask
from routers import summarize

app = FastAPI()

app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(ask.router)
app.include_router(summarize.router)