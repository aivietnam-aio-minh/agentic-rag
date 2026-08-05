import numexpr

from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.index_cache import CANDIDATE_K, get_bm25_index, get_reranker
from app.retrieval.vector_store import VectorStore


def calculator(expression: str) -> str:
    """Tính biểu thức toán học bằng numexpr, trả kết quả hoặc mô tả lỗi dạng chuỗi cho LLM đọc (không raise)."""
    if not expression or not expression.strip():
        return "Lỗi: biểu thức rỗng — hãy cung cấp một biểu thức toán học, ví dụ '15000 * 1.2'."

    try:
        result = numexpr.evaluate(expression)
    except ZeroDivisionError:
        return f"Lỗi: chia cho 0 trong biểu thức — {expression!r}."
    except (SyntaxError, ValueError, TypeError) as e:
        return f"Lỗi: biểu thức không hợp lệ — {expression!r} ({type(e).__name__})."
    except KeyError as e:
        return f"Lỗi: biểu thức chứa tên biến/hàm numexpr không hỗ trợ — {e} trong {expression!r}."
    except Exception as e:  # noqa: BLE001 - tool không được raise xuyên request (CLAUDE.md)
        return f"Lỗi: không tính được biểu thức {expression!r} ({type(e).__name__}: {e})."

    return f"Kết quả: {result}"


def search_docs(query: str, vector_store: VectorStore, top_k: int = 5) -> str:
    """Tìm tài liệu liên quan bằng hybrid search + rerank, trả về text đã format kèm nguồn/trang cho LLM đọc."""
    try:
        bm25, bm25_chunk_ids, chunk_lookup = get_bm25_index(vector_store)
        candidates = hybrid_search(
            query,
            vector_store,
            bm25,
            bm25_chunk_ids,
            chunk_lookup,
            top_k=CANDIDATE_K,
            candidate_k=CANDIDATE_K,
        )
        chunks = get_reranker().rerank(query, candidates, top_k=top_k)
    except Exception as e:  # noqa: BLE001 - tool không được raise xuyên request (CLAUDE.md)
        return f"Lỗi: không tìm được tài liệu ({type(e).__name__}: {e})."

    if not chunks:
        return "Không tìm thấy tài liệu liên quan đến truy vấn này."

    return "\n\n".join(
        f"[{chunk['source']}, trang {chunk['page']}]\n{chunk['text']}" for chunk in chunks
    )
