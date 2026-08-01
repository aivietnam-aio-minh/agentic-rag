import os
from pathlib import Path

from rank_bm25 import BM25Okapi

from app.llm.client import generate_answer
from app.retrieval.bm25_index import build_bm25_index, load_bm25_index, save_bm25_index
from app.retrieval.hybrid_search import hybrid_search
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


def ask(
    question: str,
    vector_store: VectorStore,
    top_k: int = 5,
    retrieval_mode: str = "hybrid_rerank",
) -> dict:
    """Truy hồi chunk liên quan rồi sinh câu trả lời có trích dẫn nguồn.

    retrieval_mode: "vector_only" | "hybrid" | "hybrid_rerank".
    """
    # Giữ cả 3 chế độ để eval so sánh được chúng trên cùng dataset (FR-11/FR-12):
    # "vector_only" là baseline đã có số đo, không đổi hành vi; "hybrid" tách riêng
    # để thấy phần cải thiện đến từ BM25+RRF; "hybrid_rerank" thêm cross-encoder.
    # Nhờ vậy khi điểm eval thay đổi, biết được là do tầng nào chứ không đoán mò.
    if retrieval_mode == "vector_only":
        chunks = vector_store.search(question, top_k)
    elif retrieval_mode in ("hybrid", "hybrid_rerank"):
        bm25, bm25_chunk_ids, chunk_lookup = get_bm25_index(vector_store)
        candidates = hybrid_search(
            question,
            vector_store,
            bm25,
            bm25_chunk_ids,
            chunk_lookup,
            top_k=CANDIDATE_K,
            candidate_k=CANDIDATE_K,
        )
        if retrieval_mode == "hybrid":
            chunks = candidates[:top_k]
        else:
            chunks = get_reranker().rerank(question, candidates, top_k=top_k)
    else:
        raise ValueError(f"retrieval_mode không hợp lệ: {retrieval_mode!r}")

    if not chunks:
        return {"answer": "Tài liệu không đề cập.", "sources": [], "retrieved_contexts": []}

    context = "\n\n".join(
        f"[{chunk['source']}, trang {chunk['page']}]\n{chunk['text']}" for chunk in chunks
    )
    answer = generate_answer(context, question)

    sources = []
    for chunk in chunks:
        source = {"source": chunk["source"], "page": chunk["page"]}
        if source not in sources:
            sources.append(source)

    return {
        "answer": answer,
        "sources": sources,
        "retrieved_contexts": [chunk["text"] for chunk in chunks],
    }
