from app.llm.client import generate_answer
from app.retrieval.vector_store import VectorStore


def ask(question: str, vector_store: VectorStore, top_k: int = 5) -> dict:
    """Truy hồi chunk liên quan rồi sinh câu trả lời có trích dẫn nguồn."""
    chunks = vector_store.search(question, top_k)

    if not chunks:
        return {"answer": "Tài liệu không đề cập.", "sources": []}

    context = "\n\n".join(
        f"[{chunk['source']}, trang {chunk['page']}]\n{chunk['text']}" for chunk in chunks
    )
    answer = generate_answer(context, question)

    sources = []
    for chunk in chunks:
        source = {"source": chunk["source"], "page": chunk["page"]}
        if source not in sources:
            sources.append(source)

    return {"answer": answer, "sources": sources}
