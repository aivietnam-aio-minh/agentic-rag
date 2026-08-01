from sentence_transformers import CrossEncoder

RERANKER_MODEL_NAME = "BAAI/bge-reranker-v2-m3"


class Reranker:
    """Bọc cross-encoder bge-reranker-v2-m3 để xếp lại candidate, load model một lần."""

    def __init__(self, device: str = "cuda") -> None:
        self.model = CrossEncoder(RERANKER_MODEL_NAME, device=device)

    def rerank(self, query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
        """Chấm lại từng cặp (query, candidate["text"]), trả top_k candidate kèm "rerank_score"."""
        if not candidates:
            return []

        pairs = [(query, candidate["text"]) for candidate in candidates]
        scores = self.model.predict(pairs)

        scored = [
            {**candidate, "rerank_score": float(score)}
            for candidate, score in zip(candidates, scores)
        ]
        scored.sort(key=lambda candidate: candidate["rerank_score"], reverse=True)
        return scored[:top_k]
