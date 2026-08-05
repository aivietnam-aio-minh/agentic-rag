import sys, os, json
sys.path.insert(0, '.')
from app.retrieval.vector_store import VectorStore
from app.agent.loop import run

vs = VectorStore(device=os.environ.get('DEVICE', 'cuda'))

questions = [
    ("fq001", "simple", "Đề tài chính của tài liệu là gì?"),
    ("fq002", "simple", "Mô hình nào được đề xuất fine-tune trong dự án này?"),
    ("fq022", "multi_hop", "Để hoàn thành dự án fine-tune này, các nhóm cần đi qua những giai đoạn nào?"),
    ("fq023", "multi_hop", "So sánh phạm vi dữ liệu mà Nhóm 1 và Nhóm 2 cần thu thập khác nhau như thế nào?"),
    ("fq024", "needs_calc", "Tổng cộng có bao nhiêu người tham gia dự án, chia thành mấy nhóm?"),
    ("rg029", "needs_calc", "Có tổng cộng bao nhiêu kỹ thuật nghiên cứu nâng cao (Phần VI: Research in RAG) được tài liệu liệt kê và giới thiệu chi tiết?"),
    ("fq025", "out_of_scope", "Ngân sách dành cho dự án fine-tune này là bao nhiêu?"),
    ("fq026", "out_of_scope", "Deadline nộp bài của dự án là ngày nào?"),
    ("fq028", "ambiguous", "Model Qwen 0.5B có đủ tốt cho bài toán này không?"),
    ("fq029", "ambiguous", "Dữ liệu như vậy có đủ không?"),
]

results = []
for qid, qtype, question in questions:
    print("=" * 70)
    print(f"[{qid}] ({qtype}) {question}")
    result = run(question, vs)
    print("Answer:", result["answer"][:200])
    print("Steps:", result["steps"])
    for t in result["trace"]:
        print(f"  [{t['step']}] {t['tool']}({t['input']})")
    print()
    results.append({"id": qid, "type": qtype, "question": question, **result})

with open("agent_test_10.jsonl", "w", encoding="utf-8") as f:
    for r in results:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("Đã lưu chi tiết vào agent_test_10.jsonl")
