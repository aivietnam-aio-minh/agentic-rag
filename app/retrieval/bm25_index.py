import pickle
import re

from rank_bm25 import BM25Okapi

TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    """Tokenize thô: lowercase rồi tách theo từ (regex \\w+), đủ dùng cho đếm tần suất BM25."""
    return TOKEN_PATTERN.findall(text.lower())


def build_bm25_index(chunks: list[dict]) -> BM25Okapi:
    """Xây BM25Okapi từ list chunk (mỗi chunk có key "text"), tokenize theo thứ tự chunks truyền vào."""
    tokenized_corpus = [_tokenize(chunk["text"]) for chunk in chunks]
    return BM25Okapi(tokenized_corpus)


def save_bm25_index(bm25: BM25Okapi, chunk_ids: list[str], path: str) -> None:
    """Lưu bm25 object + danh sách chunk_ids (theo đúng thứ tự lúc build) ra file pickle."""
    with open(path, "wb") as f:
        pickle.dump({"bm25": bm25, "chunk_ids": chunk_ids}, f)


def load_bm25_index(path: str) -> tuple[BM25Okapi, list[str]]:
    """Nạp lại bm25 object + chunk_ids đã lưu bằng save_bm25_index()."""
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["bm25"], data["chunk_ids"]


def search_bm25(query: str, bm25: BM25Okapi, chunk_ids: list[str], top_k: int = 20) -> list[tuple[str, float]]:
    """Tìm kiếm BM25, trả về top_k (chunk_id, score) sắp xếp giảm dần theo score."""
    scores = bm25.get_scores(_tokenize(query))
    ranked = sorted(zip(chunk_ids, scores), key=lambda pair: pair[1], reverse=True)
    return ranked[:top_k]
