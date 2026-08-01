def rrf_fusion(ranked_lists: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Gộp nhiều danh sách xếp hạng (vd. BM25, vector) bằng Reciprocal Rank Fusion.

    Với mỗi chunk_id, cộng dồn 1/(k + rank) qua mọi danh sách nó xuất hiện (rank từ 1).
    Ví dụ: chunk "a" đứng hạng 1 ở list_1 và hạng 3 ở list_2, k=60
    -> score("a") = 1/(60+1) + 1/(60+3) = 0.01639 + 0.01587 = 0.03226.

    Trả về list (chunk_id, rrf_score) sắp xếp giảm dần theo rrf_score.
    """
    scores: dict[str, float] = {}
    for ranked_list in ranked_lists:
        for rank, chunk_id in enumerate(ranked_list, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)

    return sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
