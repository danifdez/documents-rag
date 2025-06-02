from fastapi import FastAPI
from routers import ingest

app = FastAPI()

app.include_router(ingest.router)