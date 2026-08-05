# PROGRESS — Nhật ký tiến độ

> File này là "bộ nhớ ngắn hạn" của project — đọc file này đầu tiên (sau CLAUDE.md)
> để biết đang ở đâu, đã xong gì, đang dở gì, quyết định gì đang treo.
> QUY TẮC: cập nhật file này SAU MỖI buổi code, không đợi cuối tuần.
> Không xóa lịch sử cũ trong "Nhật ký theo ngày" — chỉ thêm mới lên đầu.

## Trạng thái hiện tại (cập nhật lần cuối: 2026-08-05)

- **Đang ở tuần:** 7/10 (theo `ke-hoach-thuc-hien-agentic-rag.md`)
- **Nhánh đang làm việc:** `feature/agent-tools`
- **Vừa xong:** Giai đoạn 6 — `agent/tools.py` (`search_docs`, `calculator`) + `agent/loop.py` (vòng lặp tool-use, `MAX_STEPS=6`), test tay 10 câu từ `dataset.jsonl`.
- **Việc tiếp theo:** Giai đoạn 7 — `agent/graph.py` (LangGraph, grading + rewrite).

## Đã hoàn thành (theo tầng)

| Tầng | File | Trạng thái | Ghi chú |
|---|---|---|---|
| Setup | SRS.md, ARCHITECTURE.md, CLAUDE.md | ✅ Xong | Đã điền đầy đủ, có 6 ADR |
| Setup | Git + GitHub | ✅ Xong | Repo: `aivietnam-aio-minh/agentic-rag`, nhánh chính `main` |
| Setup | GPU (RTX 5060, torch cu128) | ✅ Xong | Xác nhận `torch.cuda.is_available()==True`, tên GPU đúng |
| Hạ tầng | Docker + Qdrant | ✅ Xong | Container `qdrant`, volume `data/qdrant_data/` |
| ingestion | `chunker.py` (`chunk_text`) | ✅ Xong | Tự viết tay; có guard `overlap >= chunk_size` raise lỗi; test pass |
| ingestion | `loader.py` (`load_pdf`) | ✅ Xong | Vibe coding có review; test pass |
| ingestion | `indexer.py` (`index_document`) | ✅ Xong | Vibe coding; test pass; đã index thật `data/finetune_Qwen.pdf` → collection `docs`, 118 points, xác nhận qua dashboard |
| retrieval | `vector_store.py` (class `VectorStore`) | ✅ Xong | Bọc embedding + Qdrant search; test tay cho kết quả đúng; đã commit |
| experiments | `01_cosine_similarity_test.ipynb` | ✅ Xong | Tự viết tay hàm cosine, 3 câu test, kết quả 0.72 vs 0.36 |
| llm | client.py, prompts.py | ✅ Xong | Đa provider (gemini/anthropic/openai qua LLM_PROVIDER); retry chung cho lỗi 429 (MAX_RETRIES=3); thêm call_llm_with_tools() cho agent function-calling (Giai đoạn 6) |
| rag | `pipeline.py` | ✅ Xong | Ghép `VectorStore.search()` + `generate_answer()`, có câu trả lời RAG hoàn chỉnh đầu tiên |
| eval | `dataset.jsonl` (64 câu) | ✅ Xong | Đã chạy RAGAS thật trên toàn bộ 64 câu |
| eval | `generate_answers.py` + `score_ragas.py` | ✅ Xong | Tách 2 script/2 môi trường: sinh câu trả lời chạy ở venv chính (torch/GPU), chấm RAGAS chạy ở `.venv-eval` riêng để không phá torch cu128 |
| retrieval | `bm25_index.py` (build/save/load/search BM25) | ✅ Xong | `rank_bm25`, tokenize thô lowercase + regex `\w+`; index lưu `data/bm25_index.pkl` |
| retrieval | `rrf.py` (Reciprocal Rank Fusion) | ✅ Xong | Hàm thuần, không I/O; đã tự tay kiểm chứng bằng ví dụ tính tay |
| retrieval | `hybrid_search.py` (vector + BM25 qua RRF) | ✅ Xong | Lấy top-20 mỗi nhánh rồi gộp RRF (ADR-003); bỏ qua + cảnh báo khi chunk_id lệch |
| retrieval | `reranker.py` (cross-encoder bge-reranker-v2-m3) | ✅ Xong | `CrossEncoder` của sentence-transformers, singleton, đọc `device` từ tham số |
| rag | Nối hybrid+rerank vào `pipeline.ask()` | ✅ Xong | Thêm `retrieval_mode`: `vector_only` \| `hybrid` \| `hybrid_rerank` (mặc định), giữ baseline cũ nguyên vẹn để so sánh |
| eval | Chạy lại 64 câu với `hybrid_rerank` + report so sánh baseline | ✅ Xong | Xem `eval/report.md`; kết quả chi tiết trong nhật ký 2026-08-02 |
| agent | `tools.py` (`search_docs`, `calculator`) | ✅ Xong | Bọc hybrid_search+rerank có sẵn (search_docs) + numexpr (calculator, không dùng `eval()` trần) |
| agent | `loop.py` (vòng lặp agent, `run(question, vector_store) -> {answer, trace, steps}`) | ✅ Xong | Tự viết tay; `MAX_STEPS=6`; refactor `get_bm25_index`/`get_reranker`/`CANDIDATE_K` từ `rag/pipeline.py` sang `retrieval/index_cache.py` để `agent/` và `rag/` không phụ thuộc lẫn nhau (đúng ARCHITECTURE.md mục 4) |
| agent | `graph.py` (LangGraph) | ⬜ Chưa làm | Tuần 7 |
| api | FastAPI routes | ⬜ Chưa làm | Tuần 8 |
| ui | Streamlit | ⬜ Chưa làm | Tuần 8–9 |
| infra | Docker Compose, CI | ⬜ Chưa làm | Tuần 9 |

## Quyết định đang treo / cần xử lý sau (không chặn tiến độ hiện tại)

- **[Kỹ thuật nợ]** `indexer.py` dùng `id=str(uuid.uuid4())` ngẫu nhiên cho mỗi point → chạy `index_document` 2 lần trên cùng 1 file sẽ tạo dữ liệu trùng lặp trong Qdrant. Cần sửa trước khi làm UI upload thật (đổi sang ID xác định theo hash nội dung `text+source+page`). Ghi ngày phát hiện: buổi mentor viết `indexer.py`.
- **[Cần nhớ]** `VectorStore` load model 1 lần trong `__init__` — khi ghép FastAPI phải tạo theo kiểu singleton (1 instance dùng chung toàn app), KHÔNG tạo mới mỗi request, để tránh nhân đôi VRAM.
- **[Đã xử lý xong, không cần đọc lại]** Lỗi `.gitignore` gộp nhầm `data/qdrant_data/` thành 1 dòng thay vì 2 dòng riêng — đã sửa, đã xác nhận `git status` sạch.
- **[Kỹ thuật nợ]** Cache BM25/Reranker trong `pipeline.py` dùng biến module-level (`_bm25_cache`, `_reranker_cache`), KHÔNG tự invalidate khi có tài liệu mới index vào Qdrant. Cần xử lý khi làm UI upload: sau khi upload xong phải xóa `data/bm25_index.pkl` và reset 2 biến cache về `None`, nếu không lần `ask()` tiếp theo vẫn dùng index cũ, không thấy tài liệu mới.
- **[Nghi vấn, cần điều tra riêng]** Một số chunk bị cắt ngang giữa từ/câu — phát hiện khi đọc context thật ở Giai đoạn 5 (ví dụ "ột biểu diễn" thay vì "một biểu diễn"). Nghi do `chunker.py` (Giai đoạn 1) cắt cứng theo ký tự/token, không tôn trọng ranh giới từ. Ảnh hưởng tiềm tàng tới chất lượng retrieval ở các câu hỏi biên. CHƯA sửa vì đổi chunker sẽ phải re-index toàn bộ + chạy lại toàn bộ eval.
- **[Giới hạn thiết kế đã biết]** Rerank cross-encoder xử lý kém với câu hỏi liệt kê/tổng hợp cấu trúc toàn tài liệu (xem chi tiết ở nhật ký 2026-08-02). Cần quyết định sau: có mở rộng phạm vi để xử lý loại câu hỏi này không, hay giữ nguyên vì nằm ngoài SRS (hệ thống định vị "tra cứu", không phải "tóm tắt/liệt kê").
- **[Đã XÁC MINH bằng grep, cần quyết định phạm vi sửa]** Cross-document contamination trong agent: `search_docs` trả về candidate trộn lẫn từ 2 tài liệu khác chủ đề, agent cố dùng hết context kể cả phần không liên quan tới câu hỏi (T5-Large/CRAG từ `RAG.pdf` bị gắn nhầm vào câu hỏi về dự án fine-tune Qwen) — xem chi tiết ở nhật ký 2026-08-05, fq002/fq024. Hướng xử lý cân nhắc: thêm hướng dẫn system prompt "chỉ dùng thông tin thực sự liên quan", hoặc gắn nhãn nguồn tài liệu rõ ràng trong context.
- **[Tối ưu hóa, chưa sửa]** Agent lặp lại query gần giống nhau khi không tìm ra thêm thông tin mới (rg029) — lãng phí step, không sai kết quả cuối. Có thể cải thiện bằng system prompt "đổi chiến lược nếu 2 lần tìm liên tiếp cho kết quả giống nhau".
- **[Cần quyết định thiết kế]** Hành vi agent "hỏi ngược lại" khi câu hỏi mơ hồ (fq029, "Dữ liệu như vậy có đủ không?") — hợp lý về logic nhưng LỆCH khỏi FR-04 (hệ thống hỏi-đáp 1 lượt, không có cơ chế hội thoại nhiều lượt). Cần quyết định: chấp nhận hành vi này (làm UI hỗ trợ), hay buộc agent luôn trả lời tốt nhất có thể thay vì hỏi ngược.

## Môi trường máy dev (để người/agent khác biết đây KHÔNG phải máy chuẩn CPU)

- OS: Windows, GPU: RTX 5060 Laptop 8GB VRAM (Blackwell, sm_120)
- torch 2.11.0+cu128 — **bắt buộc bản CUDA 12.8+**, bản torch mặc định/cũ sẽ không nhận GPU này
- Qdrant chạy qua Docker, cổng 6333/6334, volume `data/qdrant_data/`
- Model đã tải về cache Hugging Face: `BAAI/bge-m3` (~2.27GB), `BAAI/bge-reranker-v2-m3`
- Venv riêng `.venv-eval/` (Python 3.13) chỉ để chạy `eval/score_ragas.py` — ragas kéo theo langchain/numpy xung đột với torch cu128, xem `eval/requirements-eval.txt`
- Chưa cài: Ollama, Tavily

## Nhật ký theo ngày (thêm mới lên đầu, không xóa cũ)

### 2026-08-05 — Giai đoạn 6: Agent tools + loop

**Đã làm:**
- `tools.py`: `search_docs` (bọc hybrid_search+rerank có sẵn), `calculator` (numexpr, không `eval()` trần). Test tay xác nhận: chia cho 0 ném `ZeroDivisionError` thật (không phải nan/inf như dự đoán ban đầu).
- `client.py`: thêm `call_llm_with_tools()` hỗ trợ OpenAI function-calling, tách biệt với `generate_answer()` (không đổi hành vi baseline).
- `loop.py`: vòng lặp tool-use, `messages` tích lũy lịch sử hội thoại, 2 lớp try/except (lỗi gọi LLM dừng hẳn; lỗi parse JSON từ LLM thì ghi lỗi vào `tool_result` để LLM tự sửa ở lượt sau, không crash).
- Test tay 10 câu từ `dataset.jsonl` (2 câu/loại x 5 loại: simple, multi_hop, needs_calc, out_of_scope, ambiguous).

**Phát hiện quan trọng — agent CẢI THIỆN so với hybrid_rerank pipeline:**
Câu "đề tài chính của tài liệu là gì?" (fq001) từng bị pipeline `hybrid_rerank` trả lời sai "Tài liệu không đề cập" (Giai đoạn 5, do rerank chọn nhầm chunk). Agent trả lời ĐÚNG vì tự viết lại query ngắn gọn ("đề tài chính") trước khi gọi `search_docs`, thay vì dùng nguyên câu hỏi dài như pipeline vẫn làm. Đây là bằng chứng cụ thể cho giá trị của kiến trúc agent so với RAG tĩnh (ADR-004).

**Phát hiện đã XÁC MINH — cross-document contamination khi `search_docs` trả về candidate trộn lẫn từ cả 2 tài liệu khác chủ đề:**
- fq002 ("mô hình nào được đề xuất fine-tune trong dự án này?"): agent trả lời đúng Qwen 0.5B nhưng THÊM "mô hình T5-Large" như thể đó cũng là 1 phần dự án. Đã xác minh bằng grep `RAG.pdf` trang 22: T5-Large thực chất được nhắc tới trong mô tả kỹ thuật Corrective RAG (CRAG) — mô hình đánh giá độ liên quan (evaluator), fine-tune để phân loại văn bản thành 3 loại Đúng/Không Đúng/..., HOÀN TOÀN không liên quan tới "dự án fine-tune Qwen" được hỏi.
- fq024 ("tổng cộng bao nhiêu người tham gia dự án"): trả lời đúng "4 người, 2 nhóm" nhưng thêm câu gây confusion "còn có một dự án khác chia 3 nhóm" — lấy từ `RAG.pdf` trang 23, cùng nội dung phân loại 3 loại của CRAG, KHÔNG liên quan gì tới số người tham gia.

Kết luận: agent có xu hướng cố dùng hết mọi context được cấp, kể cả phần không liên quan tới câu hỏi, khi `search_docs` trả về candidate trộn lẫn 2 nguồn tài liệu khác chủ đề (cùng chứa cụm "3 nhóm/3 loại" khiến rerank/retrieval nhầm lẫn ngữ nghĩa). Hướng xử lý cân nhắc: thêm hướng dẫn trong system prompt "chỉ dùng thông tin thực sự liên quan tới câu hỏi, bỏ qua context không liên quan dù được cung cấp", hoặc lọc/gắn nhãn rõ nguồn tài liệu trong context để LLM phân biệt. CHƯA sửa ngay, cần bàn phạm vi trước khi làm Giai đoạn 7.

**Xác nhận lại giới hạn đã biết** (rg029, "Phần VI có bao nhiêu kỹ thuật"): agent chạm `MAX_STEPS=6`, từ chối đúng cách (không bịa số), khớp giả thuyết "giới hạn dữ liệu/chunking" đã ghi ở Giai đoạn 5, không phải bug agent. Phát hiện thêm: agent lặp lại gần như đúng 1 query nhiều lần (step 3≈5, step 4≈6, cùng query gần giống + cùng kết quả) thay vì đổi chiến lược tìm kiếm khi không ra kết quả mới — có thể cải thiện bằng system prompt hướng dẫn "đổi chiến lược nếu 2 lần tìm liên tiếp cho kết quả giống nhau", chưa sửa.

**Hành vi cần quyết định** (fq029, "Dữ liệu như vậy có đủ không?"): agent KHÔNG gọi tool nào, tự hỏi ngược lại người dùng để làm rõ câu hỏi mơ hồ, thay vì tìm kiếm mù quáng hay đoán. Hợp lý về logic nhưng LỆCH khỏi thiết kế FR-04 (hệ thống hỏi-đáp 1 lượt, không có cơ chế hội thoại nhiều lượt qua lại). Cần quyết định: chấp nhận hành vi này (và làm UI hỗ trợ), hay thêm system prompt buộc agent luôn đưa ra câu trả lời tốt nhất có thể thay vì hỏi ngược.

### 2026-08-02 — Giai đoạn 5: Hybrid Search + Reranker

**Đã làm:**
- Xây xong 4 file: `bm25_index.py`, `rrf.py` (tự viết tay), `hybrid_search.py`, `reranker.py`; nối vào `pipeline.ask()` qua tham số `retrieval_mode`.
- Test bằng dữ liệu thật (2 file PDF đã index, 118 chunk), không dùng dữ liệu giả.
- Tự tay kiểm chứng công thức RRF bằng ví dụ tính tay, khớp với kết quả code.
- Xác nhận cross-encoder loại được chunk nhiễu do BM25 kéo vào: câu hỏi "chia nhỏ văn bản" bị BM25 kéo nhầm chunk `finetune_Qwen.pdf` trang 2 chỉ vì trùng từ "nhỏ"; rerank đã đẩy chunk này ra khỏi top-5.

**Kết quả eval (64 câu, baseline `vector_only` → `hybrid_rerank`):**
- Tổng thể: faithfulness 0.829 → 0.832; answer_relevancy 0.599 → 0.611.
- Nhóm `simple` (46/64 câu) cải thiện rõ: faithfulness 0.841 → 0.907.
- Nhóm `out_of_scope` / `ambiguous` / `needs_calc` (18/64 câu) thì GIẢM — chính nhóm này kéo điểm tổng thể xuống, che mất mức cải thiện của nhóm `simple`.

**Phát hiện quan trọng — giới hạn của rerank với câu hỏi liệt kê/tổng hợp:**
Với câu hỏi mang tính liệt kê/tổng hợp cấu trúc toàn tài liệu (ví dụ "đề tài chính của tài liệu là gì", "Phần VI có bao nhiêu kỹ thuật"), rerank cross-encoder có xu hướng chọn nhầm chunk nội dung chi tiết thay vì phần thực sự trả lời câu hỏi. Hệ quả là hệ thống từ chối sai — trả lời "Tài liệu không đề cập" dù thực ra tài liệu CÓ thông tin đó. Đây là giới hạn thiết kế đã biết, nằm ngoài phạm vi SRS hiện tại (hệ thống định vị là "tra cứu", không phải "tóm tắt/liệt kê"), CHƯA sửa trong giai đoạn này.

**Phát hiện kỹ thuật khác:**
Faithfulness của câu trả lời từ chối phụ thuộc vào context retrieval đi kèm, không chỉ vào bản thân câu trả lời — cùng một câu trả lời "Tài liệu không đề cập" có thể bị chấm điểm khác nhau tùy retrieval đổi context ra sao. Cần nhớ điều này khi đọc so sánh điểm giữa các `retrieval_mode`.

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