from contextlib import asynccontextmanager
import pytest
from unittest.mock import MagicMock, patch

from app.utils import Output, Citation
from fastapi.testclient import TestClient


@asynccontextmanager
async def _test_lifespan(app):
    """Mock that starts app without Qdrant/Ollama."""
    import app.main as main_mod
    main_mod.qdrant_service = MagicMock()
    yield
    main_mod.qdrant_service = None

@pytest.fixture
def client():
    """Uses a mock lifespan (no Qdrant/DocumentService on startup)."""
    from app.main import app
    app.router.lifespan_context = _test_lifespan(app)
    return TestClient(app)

@pytest.fixture
def mock_output():
    return Output(
        query="what if I steal?",
        response="Theft is punishable by hanging.",
        citations=[
            Citation(source="Law 1", text="Theft is punishable by hanging."),
        ],
    )

def test_query_get_returns_output(client: TestClient, mock_output: Output):
    with patch("app.main.qdrant_service") as mock_svc:
        mock_svc.query.return_value = mock_output
        r = client.get("/query", params={"q": "what if I steal?"})
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "what if I steal?"
    assert "response" in data
    assert "citations" in data
    assert isinstance(data["citations"], list)

def test_query_returns_output_schema(client: TestClient, mock_output: Output):
    with patch("app.main.qdrant_service") as mock_svc:
        mock_svc.query.return_value = mock_output
        r = client.post("/query", json={"query": "what if I steal?"})
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "what if I steal?"
    assert data["response"] == "Theft is punishable by hanging."
    assert len(data["citations"]) == 1
    assert data["citations"][0]["source"] == "Law 1"
