"""Chạy toàn bộ eval/dataset.jsonl qua rag/pipeline.ask(), lưu kết quả thô.

Chạy bằng Python của môi trường chính (nlpenv, có torch/GPU/qdrant-client),
KHÔNG import ragas ở đây — chấm điểm ragas nằm ở score_ragas.py, chạy bằng
venv riêng (.venv-eval) để tránh xung đột phụ thuộc với torch cu128.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.pipeline import ask
from app.retrieval.vector_store import VectorStore

DATASET_PATH = Path(__file__).resolve().parent / "dataset.jsonl"
OUTPUT_PATH = Path(__file__).resolve().parent / "results_raw.jsonl"


def load_dataset(path: Path) -> list[dict]:
    """Đọc dataset.jsonl, mỗi dòng là 1 câu hỏi eval."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    """Sinh câu trả lời cho các câu chưa có kết quả hoặc còn lỗi; giữ nguyên câu đã xong."""
    dataset = load_dataset(DATASET_PATH)

    old_results: dict[str, dict] = {}
    if OUTPUT_PATH.exists():
        old_results = {row["id"]: row for row in load_dataset(OUTPUT_PATH)}

    to_rerun = [
        item
        for item in dataset
        if item["id"] not in old_results or old_results[item["id"]].get("error")
    ]
    print(f"Tổng {len(dataset)} câu, cần chạy lại {len(to_rerun)} câu.")

    if to_rerun:
        # VectorStore load model bge-m3 + tạo QdrantClient 1 lần, dùng chung cho các câu
        # cần chạy lại (singleton) — tránh nạp lại model mỗi vòng lặp, xem ghi chú PROGRESS.md.
        vector_store = VectorStore(device=os.environ.get("DEVICE", "cuda"))

        total = len(to_rerun)
        for i, item in enumerate(to_rerun, start=1):
            print(f"[{i}/{total}] {item['question']}")
            try:
                result = ask(item["question"], vector_store, top_k=5)
                answer = result["answer"]
                retrieved_contexts = result["retrieved_contexts"]
                error = None
            except Exception as e:  # noqa: BLE001 - eval không được dừng vì 1 câu lỗi
                print(f"  [LỖI] {e}")
                answer = ""
                retrieved_contexts = []
                error = str(e)

            old_results[item["id"]] = {
                "id": item["id"],
                "question": item["question"],
                "ground_truth": item["ground_truth"],
                "type": item["type"],
                "answer": answer,
                "retrieved_contexts": retrieved_contexts,
                "error": error,
            }
            time.sleep(2)  # giảm áp lực rate limit Gemini free tier

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(old_results[item["id"]], ensure_ascii=False) + "\n")

    print(f"Đã ghi {len(dataset)} kết quả vào {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
