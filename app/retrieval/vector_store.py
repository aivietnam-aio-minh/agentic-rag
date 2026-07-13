from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"


class VectorStore:
    """Bọc SentenceTransformer + QdrantClient để tìm kiếm ngữ nghĩa, load model/client một lần."""

    def __init__(
        self,
        collection_name: str = "docs",
        host: str = "localhost",
        port: int = 6333,
        device: str = "cuda",
    ) -> None:
        self.collection_name = collection_name
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
        self.client = QdrantClient(host=host, port=port)

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """Encode câu hỏi và trả về top_k chunk liên quan nhất kèm điểm số."""
        query_vector = self.model.encode(query).tolist()

        result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
        )

        return [
            {
                "text": hit.payload["text"],
                "page": hit.payload["page"],
                "source": hit.payload["source"],
                "score": hit.score,
            }
            for hit in result.points
        ]
