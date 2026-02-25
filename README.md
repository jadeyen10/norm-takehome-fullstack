# Norm AI Take Home
Backend: FastAPI + DocumentService + QdrantService.  
Frontend: Next.js client that queries the API and shows the answer with citations.

## Prerequisites

- Python 3.11+
- Node 18+ (for frontend)
- **`docs/laws.pdf`** – Place the provided laws PDF in the `docs/` folder. If missing, the app still starts but the index is empty and answers will be generic.

## Backend

### Setup and run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-local.txt
uvicorn app.main:app --reload --port 8000
```

Install [Ollama](https://ollama.ai) and run `ollama run llama3.2`

- API: http://localhost:8000  

### Using the API

- **GET** `/query?q=your+question` – natural language question about the laws.
- **POST** `/query` with body `{"query": "your question"}` – same as GET.
- Response is JSON: `{ "query": "...", "response": "...", "citations": [{ "source": "...", "text": "..." }] }`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000/query?={}

### Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Design notes

- **DocumentService**: Reads `docs/laws.pdf` with fitz, splits text by headings, and returns LlamaIndex `Document` objects.
- **QdrantService**: In-memory Qdrant, LlamaIndex `Settings` for LLM/embeddings, `CitationQueryEngine` with `similarity_top_k=self.k` for retrieval and cited answers. The service uses Ollama embeddings and for the LLM due to its free tier.
- **Frontend** Single lightweight input page with submission and display for query, response, citationns.
