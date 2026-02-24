from typing import List

from llama_index.core import VectorStoreIndex, Settings
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.query_engine import CitationQueryEngine
from app.utils import Citation, Output


class _OllamaEmbeddingCompat(OllamaEmbedding):
    """OllamaEmbedding that supports both dict and object responses from the ollama client."""

    def _embeddings_from_result(self, result) -> List[List[float]]:
        if isinstance(result, dict):
            return result["embeddings"]
        return result.embeddings

    def get_general_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        result = self._client.embed(
            model=self.model_name,
            input=texts,
            options=self.ollama_additional_kwargs,
            keep_alive=self.keep_alive,
        )
        return self._embeddings_from_result(result)

    def get_general_text_embedding(self, texts: str) -> List[float]:
        result = self._client.embed(
            model=self.model_name,
            input=texts,
            options=self.ollama_additional_kwargs,
            keep_alive=self.keep_alive,
        )
        emb = self._embeddings_from_result(result)
        return emb[0]

    async def aget_general_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        result = await self._async_client.embed(
            model=self.model_name,
            input=texts,
            options=self.ollama_additional_kwargs,
            keep_alive=self.keep_alive,
        )
        return self._embeddings_from_result(result)

    async def aget_general_text_embedding(self, prompt: str) -> List[float]:
        result = await self._async_client.embed(
            model=self.model_name,
            input=prompt,
            options=self.ollama_additional_kwargs,
            keep_alive=self.keep_alive,
        )
        emb = self._embeddings_from_result(result)
        return emb[0]


class QdrantService:
    def __init__(self, k: int = 2):
        self.index = None
        self.k = k

    def connect(self) -> None:
        import os
        qdrant_host = os.environ.get("QDRANT_HOST", "localhost")
        qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))
        ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

        # timeout: default 5s is too short for cold Qdrant; use 30s so startup doesn't fail immediately
        client = qdrant_client.QdrantClient(
            host=qdrant_host, port=qdrant_port, timeout=30.0
        )
        vstore = QdrantVectorStore(client=client, collection_name="documents")

        Settings.llm = Ollama(
            model="llama3.2:3b",
            base_url=ollama_base,
            request_timeout=300.0,
            additional_kwargs={
                "num_predict": 256,
                "temperature": 0,
            },
        )

        Settings.embed_model = _OllamaEmbeddingCompat(
            model_name="nomic-embed-text",
            base_url=ollama_base,
        )

        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vstore, 
        )

    def load(self, docs):
        self.index.insert_nodes(docs)
    
    def query(self, query_str: str) -> Output:
        query_engine = CitationQueryEngine.from_args(
            self.index,
            similarity_top_k=self.k,
            citation_chunk_size=512,
        )
        response = query_engine.query(query_str)
        print(response)
        response_text = str(response).strip()

        citations: list[Citation] = []
        seen: set[tuple[str, str]] = set()
        for i, node_with_score in enumerate(response.source_nodes or [], 1):
            node = node_with_score.node
            text = node.get_content()
            meta = node.metadata or {}
            source = meta.get("Section", meta.get("source", f"Source {i}"))
            if isinstance(source, dict):
                source = str(source)
            key = (source, text[:100])
            if key not in seen:
                seen.add(key)
                citations.append(Citation(source=source, text=text))

        return Output(
            query=query_str,
            response=response_text,
            citations=citations,
        )