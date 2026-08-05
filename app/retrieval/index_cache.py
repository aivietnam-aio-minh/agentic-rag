import os
from pathlib import Path

from rank_bm25 import BM25Okapi

from app.retrieval.bm25_index import build_bm25_index, load_bm25_index, save_bm25_index
from app.retrieval.reranker import Reranker
from app.retrieval.vector_store import VectorStore

BM25_INDEX_PATH = Path(__file__).resolve().parents[2] / "data" / "bm25_index.pkl"
CANDIDATE_K = 20  # số candidate mỗi nhánh trước khi gộp RRF (ADR-003: hybrid lấy top-20)

# Cache module-level: BM25 index và Reranker chỉ dựng/nạp 1 lần rồi tái dùng, giống
# nguyên tắc singleton của VectorStore (tránh load lại model/rebuild index mỗi câu hỏi).
_bm25_cache: tuple[BM25Okapi, list[str], dict[str, dict]] | None = None
_reranker_cache: Reranker | None = None


def _load_all_chunks(vector_store: VectorStore) -> list[dict]:
    """Đọc toàn bộ chunk trong collection Qdrant qua scroll() (không cần embed lại)."""
    chunks: list[dict] = []
    offset = None
    while True:
        points, offset = vector_store.client.scroll(
            collection_name=vector_store.collection_name,
            limit=256,
            offset=offset,
            with_payload=True,
        )
        chunks.extend(
            {
                "id": point.id,
                "text": point.payload["text"],
                "page": point.payload["page"],
                "source": point.payload["source"],
            }
            for point in points
        )
        if offset is None:
            break
    return chunks


def get_bm25_index(vector_store: VectorStore) -> tuple[BM25Okapi, list[str], dict[str, dict]]:
    """Trả về (bm25, chunk_ids, chunk_lookup), dựng từ Qdrant lần đầu rồi cache lại."""
    global _bm25_cache
    if _bm25_cache is not None:
        return _bm25_cache

    # Luôn phải scroll để dựng chunk_lookup (pickle chỉ lưu bm25 + chunk_ids, không lưu
    # nội dung chunk). Pickle vì vậy chỉ giúp bỏ qua bước build/tokenize lại BM25.
    chunks = _load_all_chunks(vector_store)
    chunk_lookup = {chunk["id"]: chunk for chunk in chunks}

    if BM25_INDEX_PATH.exists():
        bm25, chunk_ids = load_bm25_index(str(BM25_INDEX_PATH))
    else:
        bm25 = build_bm25_index(chunks)
        chunk_ids = [chunk["id"] for chunk in chunks]
        BM25_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_bm25_index(bm25, chunk_ids, str(BM25_INDEX_PATH))

    _bm25_cache = (bm25, chunk_ids, chunk_lookup)
    return _bm25_cache


def get_reranker() -> Reranker:
    """Trả về Reranker dùng chung, load cross-encoder ở lần gọi đầu tiên."""
    global _reranker_cache
    if _reranker_cache is None:
        _reranker_cache = Reranker(device=os.environ.get("DEVICE", "cuda"))
    return _reranker_cache
