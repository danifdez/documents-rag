from fastapi import APIRouter
from pydantic import BaseModel
from services.embedding_service import get_embedding_service
from database.database import get_database
from typing import List

router = APIRouter(
    prefix="/search",
    tags=["search"],
)

class SearchRequest(BaseModel):
    query: str
    limit: int = 3

class Snippet(BaseModel):
    text: str
    score: float
    metadata: dict = {}

class SearchResponse(BaseModel):
    results: List[Snippet]

@router.post("/", response_model=SearchResponse)
async def search_snippets(request: SearchRequest):
    embedding_service = get_embedding_service()
    db = get_database()
    query_embedding = embedding_service.encode_single(request.query)
    points = db.query_points(query_embedding, limit=request.limit, with_payload=True)
    results = []
    for point in points:
        text = point.payload.get("text", "") if hasattr(point, 'payload') else ""
        score = getattr(point, 'score', 0.0)
        metadata = point.payload if hasattr(point, 'payload') else {}
        results.append(Snippet(text=text, score=score, metadata=metadata))
    return SearchResponse(results=results)
