from rank_bm25 import BM25Okapi

from app.retrieval.bm25_index import search_bm25
from app.retrieval.rrf import rrf_fusion
from app.retrieval.vector_store import VectorStore


def hybrid_search(
    query: str,
    vector_store: VectorStore,
    bm25: BM25Okapi,
    bm25_chunk_ids: list[str],
    chunk_lookup: dict[str, dict],
    top_k: int = 20,
    candidate_k: int = 20,
) -> list[dict]:
    """Gộp vector search + BM25 bằng RRF, trả về top_k chunk đầy đủ kèm "rrf_score"."""
    vector_ids = [hit["id"] for hit in vector_store.search(query, top_k=candidate_k)]
    bm25_ids = [chunk_id for chunk_id, _ in search_bm25(query, bm25, bm25_chunk_ids, top_k=candidate_k)]

    fused = rrf_fusion([vector_ids, bm25_ids])

    results = []
    for chunk_id, rrf_score in fused[:top_k]:
        chunk = chunk_lookup.get(chunk_id)
        if chunk is None:
            print(f"[hybrid_search] Cảnh báo: chunk_id {chunk_id!r} không có trong chunk_lookup, bỏ qua.")
            continue
        results.append({**chunk, "rrf_score": rrf_score})

    return results
