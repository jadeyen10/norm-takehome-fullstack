from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from app.utils import Output
from app.services.document_service import DocumentService
from app.services.qdrant_service import QdrantService

qdrant_service: QdrantService | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global qdrant_service
    doc_service = DocumentService()
    docs = doc_service.create_documents()
    qdrant_service = QdrantService()
    qdrant_service.connect()
    qdrant_service.load(docs)
    yield
    qdrant_service = None


app = FastAPI(title="Westeros Laws API", lifespan=lifespan)

@app.get("/query", response_model=Output)
def query(q: str = Query(..., description="Natural language question about the laws")):
    if qdrant_service is None:
        raise RuntimeError("Service not initialized")
    return qdrant_service.query(q)