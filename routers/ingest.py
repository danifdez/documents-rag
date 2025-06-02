from fastapi import APIRouter
from pydantic import BaseModel
from services.ingest import ingest

router = APIRouter(
    prefix="/ingest",
    tags=["ingest"],
)

class IngestRequest(BaseModel):
    source_id: str
    project_id: str
    text: str

class IngestResponse(BaseModel):
    success: bool

@router.post("/", response_model=IngestResponse)
async def ingest_request(request: IngestRequest):
    success = ingest(
        source_id=request.source_id,
        project_id=request.project_id,
        content=request.text
    )

    return IngestResponse(success=success)