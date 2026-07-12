import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from app.ingestion.chunker import chunk_text
from app.ingestion.loader import load_pdf

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_DIM = 1024


def index_document(
    file_path: str,
    collection_name: str = "docs",
    device: str = "cuda",
    host: str = "localhost",
    port: int = 6333,
) -> int:
    """Đọc PDF, cắt chunk, embed và upsert vào Qdrant.

    `device` do người gọi truyền vào (không hardcode "cuda") để cùng một
    hàm chạy được cả trên máy dev có GPU lẫn bản deploy CPU thuần (ADR-006).
    """
    pages = load_pdf(file_path)

    chunks: list[dict] = []
    for page_data in pages:
        for chunk in chunk_text(page_data["text"]):
            chunks.append(
                {
                    "text": chunk,
                    "page": page_data["page"],
                    "source": page_data["source"],
                }
            )

    if not chunks:
        return 0

    model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=device)
    embeddings = model.encode([c["text"] for c in chunks])

    client = QdrantClient(host=host, port=port)
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload=chunk,
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    client.upsert(collection_name=collection_name, points=points)

    return len(points)
