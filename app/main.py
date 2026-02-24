from contextlib import asynccontextmanager

import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.utils import Output
from app.services.document_service import DocumentService
from app.services.qdrant_service import QdrantService

qdrant_service: QdrantService | None = None


class QueryRequest(BaseModel):
    query: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    global qdrant_service
    doc_service = DocumentService("docs/laws.pdf")
    docs = doc_service.create_documents()
    qdrant_service = QdrantService()
    qdrant_service.connect()
    qdrant_service.load(docs)
    yield
    qdrant_service = None


app = FastAPI(title="Westeros Laws API", lifespan=lifespan)


_cors_origins = os.environ.get(
    "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/query", response_model=Output)
def query(q: str = Query(..., description="Natural language question about the laws")):
    if qdrant_service is None:
        raise RuntimeError("Service not initialized")
    return qdrant_service.query(q)


@app.post("/query", response_model=Output)
def query_post(body: QueryRequest) -> Output:
    if qdrant_service is None:
        raise RuntimeError("Service not initialized")
    return qdrant_service.query(body.query)