"""Chấm điểm RAGAS (faithfulness, answer_relevancy) cho eval/results_raw.jsonl.

QUAN TRỌNG: chạy script này bằng venv RIÊNG `.venv-eval` (không phải nlpenv/.venv
chính) — ragas 0.4.3 kéo theo langchain/langgraph phiên bản mới làm xung đột
numpy/torch cu128 đã ghim cho GPU RTX 5060. Việc tách venv giữ nlpenv sạch,
không phải cài lại torch mỗi lần đụng ragas. Cài đặt: xem eval/requirements-eval.txt.

CẢNH BÁO CHI PHÍ: ragas tự gọi thêm LLM (và embedding cho answer_relevancy) để
chấm từng câu. Với 64 câu × 2 chỉ số, tổng số lần gọi LLM có thể gấp 3-5 lần 64
(mỗi câu faithfulness cần 1 lần tách statement + 1 lần chấm NLI; answer_relevancy
cần sinh nhiều câu hỏi ngược + embed). Ở đây dùng Gemini (rẻ/free-tier) làm giám
khảo qua GEMINI_API_KEY, không dùng OpenAI mặc định của ragas.

Chỉ tính context_precision/context_recall khi ground_truth là ĐOẠN VĂN cụ thể
trích từ tài liệu để so khớp — dataset hiện tại `ground_truth` là câu trả lời
tóm tắt tự viết, không phải đoạn văn nguyên gốc, nên 2 chỉ số này bị bỏ qua ở
bản đầu (sẽ cần gắn nhãn lại dataset nếu muốn thêm).
"""

import json
from collections import defaultdict
from pathlib import Path
import math
from dotenv import load_dotenv
from sqlalchemy import values
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas import EvaluationDataset, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness, ResponseRelevancy
from ragas.run_config import RunConfig
# from langchain_groq import ChatGroq
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import FastEmbedEmbeddings

class SafeFastEmbedEmbeddings(FastEmbedEmbeddings):
    @property
    def model(self):
        return "BAAI/bge-small-en-v1.5"
import os
os.environ["RAGAS_DO_NOT_TRACK"] = "true"
from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import FastEmbedEmbeddings

class FastEmbedAdapter(Embeddings):
    """Bọc FastEmbed để .model là string — né lỗi EmbeddingUsageEvent của RAGAS."""

    def __init__(self, model_name: str) -> None:
        self.model = model_name  # string thật → RAGAS log không lỗi
        self._inner = FastEmbedEmbeddings(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._inner.embed_documents(texts)

    def embed_query(self, text: str) -> list[str] | list[float]:
        return self._inner.embed_query(text)
load_dotenv()

RESULTS_RAW_PATH = Path(__file__).resolve().parent / "results_raw.jsonl"
RESULTS_SCORED_PATH = Path(__file__).resolve().parent / "results_scored.jsonl"
REPORT_PATH = Path(__file__).resolve().parent / "report.md"

METRIC_NAMES = ["faithfulness", "answer_relevancy"]
QUESTION_TYPES = ["simple", "multi_hop", "needs_calc", "out_of_scope", "ambiguous"]


def load_raw_results(path: Path) -> list[dict]:
    """Đọc results_raw.jsonl do eval/generate_answers.py sinh ra."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def score_with_ragas(rows: list[dict]) -> dict[str, dict[str, float]]:
    """Chấm faithfulness + answer_relevancy cho các câu có retrieved_contexts, trả về {id: {metric: score}}."""
    # judge_llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(model="llama-3.3-70b-versatile", temperature=0))
    # judge_embeddings = LangchainEmbeddingsWrapper(GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001"))

    judge_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
    judge_embeddings = LangchainEmbeddingsWrapper(
    FastEmbedAdapter("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    )

    samples = [
        {
            "user_input": row["question"],
            "response": row["answer"],
            "retrieved_contexts": row["retrieved_contexts"],
            "reference": row["ground_truth"],
        }
        for row in rows
    ]
    dataset = EvaluationDataset.from_list(samples)

    # result = evaluate(
    #     dataset=dataset,
    #     metrics=[Faithfulness(), ResponseRelevancy()],
    #     llm=judge_llm,
    #     embeddings=judge_embeddings,
    #     run_config=RunConfig(max_workers=1, timeout=120),
    #                 )

    result = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(), ResponseRelevancy(strictness=1)],
    llm=judge_llm,
    embeddings=judge_embeddings,
    run_config=RunConfig(max_workers=1, timeout=300),
    )

    scores_by_id: dict[str, dict[str, float]] = {}
    for row, score_row in zip(rows, result.scores):
        scores_by_id[row["id"]] = {name: score_row.get(name) for name in METRIC_NAMES}
    return scores_by_id


def build_report(scored_rows: list[dict]) -> str:
    """Sinh báo cáo markdown: điểm trung bình chung và chia theo type."""

    def average(values: list[float]) -> float | None:
        values = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
        return sum(values) / len(values) if values else None

    lines = ["# Báo cáo eval RAGAS", ""]

    lines.append("## Điểm trung bình chung")
    lines.append("")
    lines.append("| Chỉ số | Điểm trung bình | Số câu tính được |")
    lines.append("|---|---|---|")
    for metric in METRIC_NAMES:
        values = [row["ragas_scores"].get(metric) for row in scored_rows]
        avg = average(values)
        n_scored = len([v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))])
        avg_str = f"{avg:.3f}" if avg is not None else "N/A"
        lines.append(f"| {metric} | {avg_str} | {n_scored}/{len(scored_rows)} |")

    lines.append("")
    lines.append("## Điểm trung bình theo loại câu hỏi (`type`)")
    lines.append("")
    lines.append("| type | faithfulness | answer_relevancy | số câu |")
    lines.append("|---|---|---|---|")

    rows_by_type: dict[str, list[dict]] = defaultdict(list)
    for row in scored_rows:
        rows_by_type[row["type"]].append(row)

    for q_type in QUESTION_TYPES:
        rows = rows_by_type.get(q_type, [])
        if not rows:
            continue
        faith_avg = average([r["ragas_scores"].get("faithfulness") for r in rows])
        relev_avg = average([r["ragas_scores"].get("answer_relevancy") for r in rows])
        faith_str = f"{faith_avg:.3f}" if faith_avg is not None else "N/A"
        relev_str = f"{relev_avg:.3f}" if relev_avg is not None else "N/A"
        lines.append(f"| {q_type} | {faith_str} | {relev_str} | {len(rows)} |")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Chấm điểm results_raw.jsonl, ghi results_scored.jsonl + report.md."""
    rows = load_raw_results(RESULTS_RAW_PATH)

    # Câu lỗi khi sinh câu trả lời hoặc không truy hồi được chunk nào (vd. out_of_scope
    # đúng nghĩa) thì không đưa vào ragas — faithfulness cần context khác rỗng.
    scorable_rows = [r for r in rows if r["retrieved_contexts"] and not r["error"]]
    skipped_rows = [r for r in rows if r not in scorable_rows]

    print(f"Chấm điểm ragas cho {len(scorable_rows)}/{len(rows)} câu (bỏ qua {len(skipped_rows)} câu lỗi/rỗng context)...")
    scores_by_id = score_with_ragas(scorable_rows) if scorable_rows else {}

    scored_rows = []
    for row in rows:
        scores = scores_by_id.get(row["id"], {name: None for name in METRIC_NAMES})
        scored_rows.append({**row, "ragas_scores": scores})

    with open(RESULTS_SCORED_PATH, "w", encoding="utf-8") as f:
        for row in scored_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Đã ghi chi tiết từng câu vào {RESULTS_SCORED_PATH}")

    report = build_report(scored_rows)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Đã ghi báo cáo tổng hợp vào {REPORT_PATH}")


if __name__ == "__main__":
    main()
