# PROGRESS — Nhật ký tiến độ

> File này là "bộ nhớ ngắn hạn" của project — đọc file này đầu tiên (sau CLAUDE.md)
> để biết đang ở đâu, đã xong gì, đang dở gì, quyết định gì đang treo.
> QUY TẮC: cập nhật file này SAU MỖI buổi code, không đợi cuối tuần.
> Không xóa lịch sử cũ trong "Nhật ký theo ngày" — chỉ thêm mới lên đầu.

## Trạng thái hiện tại (cập nhật lần cuối: 2026-07-15)

- **Đang ở tuần:** 4/10 (theo `ke-hoach-thuc-hien-agentic-rag.md`)
- **Nhánh đang làm việc:** `feature/rag-answer`
- **Vừa xong:** index thành công 2 file PDF vào Qdrant (collection `docs`, 118 points); hoàn thành `eval/dataset.jsonl` (64 câu, draft).
- **Việc tiếp theo:** viết `eval/run_eval.py`.

## Đã hoàn thành (theo tầng)

| Tầng | File | Trạng thái | Ghi chú |
|---|---|---|---|
| Setup | SRS.md, ARCHITECTURE.md, CLAUDE.md | ✅ Xong | Đã điền đầy đủ, có 6 ADR |
| Setup | Git + GitHub | ✅ Xong | Repo: `aivietnam-aio-minh/agentic-rag`, nhánh chính `main` |
| Setup | GPU (RTX 5060, torch cu128) | ✅ Xong | Xác nhận `torch.cuda.is_available()==True`, tên GPU đúng |
| Hạ tầng | Docker + Qdrant | ✅ Xong | Container `qdrant`, volume `data/qdrant_data/` |
| ingestion | `chunker.py` (`chunk_text`) | ✅ Xong | Tự viết tay; có guard `overlap >= chunk_size` raise lỗi; test pass |
| ingestion | `loader.py` (`load_pdf`) | ✅ Xong | Vibe coding có review; test pass |
| ingestion | `indexer.py` (`index_document`) | ✅ Xong | Vibe coding; test pass; đã index thật `data/finetune_Qwen.pdf` → collection `docs`, 7 points, xác nhận qua dashboard |
| retrieval | `vector_store.py` (class `VectorStore`) | ✅ Xong | Bọc embedding + Qdrant search; test tay cho kết quả đúng; đã commit |
| experiments | `01_cosine_similarity_test.ipynb` | ✅ Xong | Tự viết tay hàm cosine, 3 câu test, kết quả 0.72 vs 0.36 |
| llm | `client.py`, `prompts.py` | ✅ Xong | Đa provider (gemini mặc định, anthropic dự phòng); đã test |
| rag | `pipeline.py` | ✅ Xong | Ghép `VectorStore.search()` + `generate_answer()`, có câu trả lời RAG hoàn chỉnh đầu tiên |
| eval | `dataset.jsonl` (64 câu) | ✅ Xong (draft) | Chưa chạy RAGAS |
| eval | `run_eval.py` | ⬜ Chưa làm | Tuần 4 theo kế hoạch |
| retrieval | hybrid search (BM25 + RRF) | ⬜ Chưa làm | Tuần 5 |
| retrieval | reranker | ⬜ Chưa làm | Tuần 5–6 |
| agent | `tools.py`, `loop.py` | ⬜ Chưa làm | Tuần 6 |
| agent | `graph.py` (LangGraph) | ⬜ Chưa làm | Tuần 7 |
| api | FastAPI routes | ⬜ Chưa làm | Tuần 8 |
| ui | Streamlit | ⬜ Chưa làm | Tuần 8–9 |
| infra | Docker Compose, CI | ⬜ Chưa làm | Tuần 9 |

## Quyết định đang treo / cần xử lý sau (không chặn tiến độ hiện tại)

- **[Kỹ thuật nợ]** `indexer.py` dùng `id=str(uuid.uuid4())` ngẫu nhiên cho mỗi point → chạy `index_document` 2 lần trên cùng 1 file sẽ tạo dữ liệu trùng lặp trong Qdrant. Cần sửa trước khi làm UI upload thật (đổi sang ID xác định theo hash nội dung `text+source+page`). Ghi ngày phát hiện: buổi mentor viết `indexer.py`.
- **[Cần nhớ]** `VectorStore` load model 1 lần trong `__init__` — khi ghép FastAPI phải tạo theo kiểu singleton (1 instance dùng chung toàn app), KHÔNG tạo mới mỗi request, để tránh nhân đôi VRAM.
- **[Đã xử lý xong, không cần đọc lại]** Lỗi `.gitignore` gộp nhầm `data/qdrant_data/` thành 1 dòng thay vì 2 dòng riêng — đã sửa, đã xác nhận `git status` sạch.

## Môi trường máy dev (để người/agent khác biết đây KHÔNG phải máy chuẩn CPU)

- OS: Windows, GPU: RTX 5060 Laptop 8GB VRAM (Blackwell, sm_120)
- torch 2.11.0+cu128 — **bắt buộc bản CUDA 12.8+**, bản torch mặc định/cũ sẽ không nhận GPU này
- Qdrant chạy qua Docker, cổng 6333/6334, volume `data/qdrant_data/`
- Model đã tải về cache Hugging Face: `BAAI/bge-m3` (~2.27GB)
- Chưa cài: reranker, Ollama, Tavily

## Nhật ký theo ngày (thêm mới lên đầu, không xóa cũ)

### 2026-07-15
- Index thành công `RAG.pdf` vào Qdrant.
- Hoàn thành `eval/dataset.jsonl` (64 câu).
- Xóa collection `test_docs` rác trong Qdrant.

### 2026-07-XX
- Viết xong `vector_store.py`, test tay OK, đã commit.
- Bắt đầu `llm/client.py` + `prompts.py` (Prompt A), chưa xong.
- Tạo file `PROGRESS.md` này.

### 2026-07-XX (trước đó)
- Hoàn thành `indexer.py`, index thật file PDF, xác nhận qua Qdrant dashboard (7 points) + test search bằng câu hỏi thật.
- Phát hiện & sửa lỗi `.gitignore` gộp nhầm dòng.
- Phát hiện & sửa lỗi Qdrant "File exists" do thư mục collection cũ còn sót — xóa volume cũ, tạo lại container.

### 2026-07-XX (trước đó nữa)
- Setup Docker Qdrant, đổi volume path sang `data/qdrant_data/`.
- Cài torch cu128, xác nhận GPU RTX 5060 hoạt động.
- Cài sentence-transformers, tải bge-m3, viết notebook cosine similarity (tự tay).

### 2026-07-10 (khởi đầu)
- Setup repo, SRS/ARCHITECTURE/CLAUDE.md, Git init, xử lý lỗi commit nhầm `.venv`, push GitHub thành công.
- Viết `chunker.py` (tự tay) và `loader.py` (vibe coding), cả hai có test pass.
### 2026-07-13
- Hoàn thành llm/client.py + prompts.py, đa provider (gemini mặc định, anthropic dự phòng).
- Xác nhận: context rỗng → model trả lời "Tài liệu không đề cập", không hallucinate.
- [Hạn chế đã biết] sources trong rag/pipeline.py phản ánh "chunk đã gửi cho LLM",
  không phải "chunk LLM thực sự trích dẫn" — có thể gây lệch giữa answer và sources
  khi top_k lấy về chunk không thật sự liên quan. Sẽ cải thiện khi làm reranker (tuần 5-6)
  và agent grading (tuần 6-7).