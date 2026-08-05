from app.llm.client import generate_answer
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.index_cache import CANDIDATE_K, get_bm25_index, get_reranker
from app.retrieval.vector_store import VectorStore


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
