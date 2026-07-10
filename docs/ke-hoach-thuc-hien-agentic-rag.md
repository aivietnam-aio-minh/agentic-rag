# Kế Hoạch Thực Hiện Project Agentic RAG — Dành Cho Người Mới

Tài liệu gồm 7 phần: (1) SRS — tài liệu đặc tả yêu cầu, (2) quy mô & phạm vi, (3) tech stack & kiến trúc kèm lý do chọn, (4) timeline 10 tuần, (5) quy trình làm việc hàng tuần, (6) quy tắc "vibe coding có kiểm soát" — phần quan trọng nhất với bạn, (7) tiêu chí hoàn thành từng giai đoạn.

---

## PHẦN 1 — SRS (Software Requirements Specification)

Đây là file đầu tiên bạn tạo trong repo: `docs/SRS.md`. Viết SRS trước khi code có 3 lợi ích: bạn buộc phải nghĩ rõ mình làm gì, có tài liệu để đưa cho AI khi vibe coding (AI hiểu đúng ý bạn hơn nhiều), và khi phỏng vấn bạn cho nhà tuyển dụng thấy mình làm việc có quy trình. Dưới đây là bản SRS đã viết sẵn cho project — bạn copy vào repo và chỉnh theo domain mình chọn.

### 1.1 Giới thiệu

- **Tên dự án:** Trợ lý nghiên cứu tài liệu thông minh (Agentic RAG Assistant)
- **Mục đích:** Hệ thống hỏi đáp trên kho tài liệu riêng (ví dụ: văn bản pháp luật lao động / tài liệu nội bộ), có khả năng tự phân tích câu hỏi, chọn công cụ phù hợp (tra tài liệu, tìm web, tính toán), tự kiểm tra chất lượng câu trả lời, và luôn trích dẫn nguồn.
- **Người dùng mục tiêu:** Nhân viên HR / người lao động cần tra cứu quy định (chỉnh theo domain bạn chọn).
- **Bối cảnh:** Đồ án cá nhân phục vụ portfolio xin việc AI Engineer fresher.

### 1.2 Yêu cầu chức năng (Functional Requirements)

| Mã | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-01 | Người dùng upload tài liệu PDF/DOCX, hệ thống tự xử lý và đánh index | Bắt buộc |
| FR-02 | Người dùng đặt câu hỏi bằng tiếng Việt qua giao diện chat | Bắt buộc |
| FR-03 | Hệ thống trả lời dựa trên tài liệu, kèm trích dẫn [nguồn, số trang] | Bắt buộc |
| FR-04 | Khi tài liệu không có thông tin, hệ thống nói rõ "không đề cập" thay vì bịa | Bắt buộc |
| FR-05 | Hệ thống hỗ trợ tìm kiếm hybrid (ngữ nghĩa + từ khóa) | Bắt buộc |
| FR-06 | Agent tự phân loại câu hỏi và chọn công cụ: tra tài liệu / tính toán / tìm web | Bắt buộc |
| FR-07 | Agent tách câu hỏi phức thành các truy vấn con và tổng hợp kết quả | Bắt buộc |
| FR-08 | Agent tự đánh giá kết quả tìm kiếm, truy vấn lại nếu thiếu (tối đa 2 lần) | Bắt buộc |
| FR-09 | Giao diện hiển thị tiến trình agent theo thời gian thực ("đang tra tài liệu…") | Nên có |
| FR-10 | Câu trả lời stream ra từng chữ (như ChatGPT) | Nên có |
| FR-11 | Người dùng quản lý được nhiều bộ tài liệu (collection) riêng | Tùy chọn |
| FR-12 | Lưu lịch sử hội thoại, hỏi tiếp theo ngữ cảnh | Tùy chọn |

### 1.3 Yêu cầu phi chức năng (Non-Functional Requirements)

| Mã | Yêu cầu | Chỉ tiêu |
|---|---|---|
| NFR-01 | Độ trễ trả lời | Câu hỏi đơn giản < 10s, câu hỏi agent nhiều bước < 30s |
| NFR-02 | Chất lượng | Faithfulness ≥ 0.85, context precision ≥ 0.75 trên bộ eval tự xây |
| NFR-03 | Chi phí | < 0.05 USD / câu hỏi trung bình (log token để theo dõi) |
| NFR-04 | Bảo mật | API key trong .env, không commit; calculator không dùng eval() trần |
| NFR-05 | Ổn định | Agent luôn dừng (giới hạn số bước); tool lỗi không làm sập request |
| NFR-06 | Triển khai | Chạy được toàn bộ bằng một lệnh `docker compose up` |

### 1.4 User stories chính

1. Là nhân viên, tôi muốn hỏi "nghỉ thai sản được mấy tháng?" và nhận câu trả lời kèm điều luật cụ thể, để tin được câu trả lời.
2. Là nhân viên, tôi muốn hỏi câu phức "so sánh chế độ nghỉ phép công ty với luật hiện hành" và hệ thống tự tách ý, tự tra cả hai nguồn.
3. Là nhân viên, tôi muốn hỏi "lương gross 20 triệu thì net bao nhiêu?" và hệ thống tính chính xác thay vì đoán.
4. Là người quản trị, tôi muốn upload thêm tài liệu mới và hệ thống dùng được ngay.

### 1.5 Ngoài phạm vi (Out of scope) — quan trọng để dự án không phình to

- Không làm đăng nhập/phân quyền người dùng.
- Không fine-tune model (có thể là hướng phát triển ghi trong README).
- Không xử lý ảnh/bảng phức tạp trong PDF (chỉ text; PDF scan xử lý sau nếu còn thời gian).
- Không hỗ trợ đa ngôn ngữ ngoài tiếng Việt (+ tiếng Anh tự nhiên có sẵn của model).
- Không tối ưu chịu tải nhiều người dùng đồng thời.

Khi phỏng vấn, việc bạn nói được "tôi chủ động cắt X ra khỏi phạm vi vì Y" ấn tượng hơn nhiều so với một dự án làm mọi thứ nhưng dở dang.

---

## PHẦN 2 — QUY MÔ DỰ ÁN

- **Thời gian:** 10 tuần, mỗi tuần 15–20 giờ (phù hợp sinh viên năm cuối vừa học vừa làm). Nếu bạn rảnh hơn, có thể rút còn 7–8 tuần nhưng đừng rút giai đoạn eval và tài liệu hóa.
- **Nhân sự:** 1 người (bạn) + AI hỗ trợ code.
- **Chi phí dự kiến:** API LLM khoảng 10–20 USD cho cả quá trình dev + eval (dùng model nhỏ khi dev, model tốt khi eval); có thể giảm gần 0 nếu dev bằng model local qua Ollama. Embedding + rerank chạy local miễn phí. Deploy: Hugging Face Spaces miễn phí hoặc VPS ~5 USD/tháng.
- **Sản phẩm bàn giao:** repo GitHub hoàn chỉnh, bản demo chạy được, file `eval/report.md` có số liệu, README có kiến trúc + benchmark + GIF demo, và chính bạn — người giải thích được mọi quyết định trong đó.

---

## PHẦN 3 — TECH STACK & KIẾN TRÚC (kèm lý do, để trả lời phỏng vấn)

### 3.1 Tech stack quyết định

| Tầng | Chọn | Lý do (học thuộc ý, không thuộc lòng câu chữ) |
|---|---|---|
| Ngôn ngữ | Python 3.12 | Hệ sinh thái AI mặc định; type hints ngày càng tốt |
| Backend | FastAPI | Async phù hợp gọi LLM, tự sinh docs, chuẩn ngành cho AI service |
| Embedding | BAAI/bge-m3 (chạy local) | Đa ngôn ngữ tốt cho tiếng Việt, miễn phí, hỗ trợ cả dense lẫn sparse |
| Vector DB | Qdrant (Docker) | Production-ready, filter metadata, dễ chạy local; FAISS chỉ dùng để học ở notebook |
| Keyword search | rank_bm25 | Nhẹ, đủ dùng; nói được "nếu scale thì chuyển Elasticsearch" |
| Reranker | BAAI/bge-reranker-v2-m3 | Cross-encoder chuẩn, chạy local được |
| LLM | API (Claude/GPT/Gemini) cho bản chính; Ollama + Qwen cho dev tiết kiệm | Tách qua wrapper `llm/client.py` để đổi model chỉ sửa 1 chỗ — đây là quyết định kiến trúc đáng khoe |
| Agent | Tự viết loop trước → LangGraph sau | Hiểu bản chất trước, framework sau |
| Web search tool | Tavily API (free tier) | Thiết kế riêng cho LLM, trả kết quả sạch |
| Evaluation | RAGAS + bộ test tự xây | Chuẩn ngành cho RAG |
| UI | Streamlit | Nhanh nhất cho 1 người; ghi rõ "production sẽ dùng React" |
| Hạ tầng | Docker Compose, GitHub Actions (lint + test) | Chuẩn tối thiểu của một repo nghiêm túc |

### 3.2 Kiến trúc

Dùng đúng kiến trúc phân tầng và cấu trúc thư mục trong tài liệu `cau-truc-agentic-rag.md` đã có: `ingestion → retrieval → rag pipeline (baseline) → agent (bọc trên)`, kèm `eval/` chạy được trên cả hai chế độ. Nguyên tắc kiến trúc cần nhớ để trả lời phỏng vấn:

1. **Mỗi tầng thay được độc lập:** đổi Qdrant sang Weaviate chỉ sửa `vector_store.py`; đổi LLM chỉ sửa `client.py`.
2. **Agent không chứa logic tìm kiếm** — nó chỉ gọi tool. Logic tìm kiếm nằm ở tầng retrieval, dùng chung cho cả RAG tĩnh.
3. **Mọi prompt tập trung ở `prompts.py`, mọi cấu hình ở `config.py`** — chỉnh sửa không phải lục code.

---

## PHẦN 4 — TIMELINE 10 TUẦN (điều chỉnh cho người mới + vibe coding)

Mỗi tuần có 3 cột: việc phải xong, kiến thức phải hiểu (để không thành "người bấm nút"), và bằng chứng hoàn thành.

| Tuần | Việc phải xong | Kiến thức phải hiểu được | Bằng chứng |
|---|---|---|---|
| 0 (3–4 ngày) | Tạo repo, viết `docs/SRS.md`, `.gitignore`, `.env.example`, setup venv | Git cơ bản, biến môi trường là gì | Repo có SRS, commit đầu tiên |
| 1 | Ôn Python: OOP, async, type hints qua bài tập nhỏ (không dùng AI viết hộ phần này) | Class, dict/list, try/except, async | 5–7 file bài tập tự viết |
| 2 | Notebook thử nghiệm: embedding, cosine similarity, FAISS với 20 đoạn văn tự nhập | Embedding là gì, vì sao đo được độ giống nghĩa | Notebook `experiments/01_embedding.ipynb` |
| 3 | `ingestion/`: đọc PDF, chunker, indexer vào Qdrant. UI Streamlit tối giản + RAG bản đầu | Chunking, vì sao cần overlap, Qdrant hoạt động ra sao | Demo hỏi đáp 1 file PDF chạy được |
| 4 | Xây `eval/dataset.jsonl` 50 câu (tự viết tay — việc này AI không làm thay được vì cần đọc tài liệu của bạn), chạy RAGAS lần đầu | 4 chỉ số RAGAS nghĩa là gì | `eval/report.md` phiên bản baseline |
| 5 | Hybrid search (BM25 + RRF) + reranker. Đo lại eval | Vì sao vector search trượt từ khóa, RRF, bi vs cross-encoder | Bảng so sánh trước/sau trong report |
| 6 | `agent/tools.py` + `agent/loop.py` với 2 tool. Test tay 10 câu | Function calling, vòng lặp agent, vì sao cần MAX_STEPS | Agent chạy được, có trace |
| 7 | Học LangGraph, viết `graph.py` với grading + rewrite. Thêm tool web search | State graph, conditional edge, Corrective RAG | 2 chế độ agent chạy song song |
| 8 | Chạy eval so sánh RAG tĩnh vs agent theo nhóm câu hỏi. FastAPI hoàn chỉnh + streaming | SSE là gì, trade-off chất lượng/độ trễ/chi phí | Bảng benchmark cuối trong report |
| 9 | Docker Compose, deploy, GitHub Actions lint+test | Image/container/volume, CI là gì | Link demo công khai |
| 10 | README hoàn chỉnh + GIF demo, dọn code, tự phỏng vấn thử (Phần 7) | Ôn toàn bộ | Repo "sẵn sàng gửi CV" |

Quy tắc trễ tiến độ: nếu chậm quá 1 tuần, cắt từ dưới lên theo thứ tự: FR-11/12 → web search tool → streaming → LangGraph (giữ loop tự viết). **Không bao giờ cắt: eval, README, và việc bạn hiểu code.**

---

## PHẦN 5 — QUY TRÌNH LÀM VIỆC HÀNG TUẦN

Mô phỏng quy trình công ty thật (Scrum tối giản cho 1 người) — và bạn kể được điều này khi phỏng vấn:

1. **Đầu tuần (30 phút):** mở `docs/PLAN.md`, viết 3–5 task của tuần dưới dạng checkbox, mỗi task nhỏ đến mức làm xong trong 1 buổi. Task to quá thì tách.
2. **Mỗi buổi làm việc:** một task = một nhánh Git (`feature/hybrid-search`) hoặc tối thiểu một commit riêng, message rõ nghĩa (`feat: add RRF fusion for hybrid search`).
3. **Cuối tuần (30 phút) — retro cá nhân:** ghi vào `docs/LEARNING_LOG.md` ba mục: tuần này làm gì, hiểu thêm khái niệm gì, vướng gì và giải quyết ra sao. File này chính là kho "chuyện để kể" khi phỏng vấn — đừng bỏ qua.
4. **Mỗi khi thay đổi ảnh hưởng chất lượng** (đổi chunk size, thêm rerank...): chạy lại eval, ghi số vào report. Không cảm tính "hình như tốt hơn".

---

## PHẦN 6 — QUY TẮC "VIBE CODING CÓ KIỂM SOÁT" (phần quan trọng nhất)

Vibe coding (để AI viết phần lớn code) hoàn toàn ổn — các công ty giờ cũng làm vậy — **miễn là bạn vẫn là người hiểu và ra quyết định**. Rủi ro thật sự: bạn nộp một repo đẹp, vào phỏng vấn bị hỏi "vì sao dòng này dùng async?" và đứng hình — lúc đó dự án phản tác dụng. Bộ quy tắc sau giúp bạn tránh điều đó:

### Quy tắc 1 — Thiết kế trước, code sau
Không bao giờ prompt "làm cho tôi hệ thống RAG". Luôn đi theo chu trình: bạn tự viết ra (bằng lời, trong PLAN.md) *cần làm gì, input gì, output gì* → rồi mới đưa cho AI kèm SRS và cấu trúc thư mục. Người thiết kế là bạn, AI là người gõ. Đây cũng chính là kỹ năng "biết dùng AI hiệu quả" mà nhà tuyển dụng đánh giá cao.

### Quy tắc 2 — Chia nhỏ đến mức một hàm/một file
Prompt theo đơn vị nhỏ: "viết hàm chunk_text với chiến lược recursive, input X output Y" thay vì "viết module ingestion". Code sinh ra theo cụm nhỏ thì bạn đọc kịp, hiểu kịp, và khi lỗi biết lỗi ở đâu.

### Quy tắc 3 — Nghi thức đọc code (bắt buộc, không bỏ)
Với MỌI đoạn code AI sinh ra, trước khi commit:
1. Đọc từng dòng, dòng nào không hiểu thì hỏi lại AI "giải thích dòng này, vì sao cần" đến khi hiểu.
2. Tự giải thích lại cả đoạn bằng tiếng Việt, thành lời, không nhìn code (kỹ thuật rubber duck). Giải thích không trôi = chưa hiểu = chưa commit.
3. Tự đặt 1 câu hỏi "nếu đổi X thì sao?" và thử đổi thật (đổi chunk_size, đổi top_k...) xem kết quả có đúng dự đoán.

### Quy tắc 4 — Ba phần phải TỰ VIẾT TAY (không vibe)
Đây là những phần lõi mà phỏng vấn chắc chắn xoáy vào, tự viết một lần rồi sau đó cho AI cải tiến thì được:
1. Hàm **cosine similarity + đoạn so sánh embedding** (tuần 2) — để hiểu embedding bằng tay.
2. Hàm **RRF fusion** (tuần 5) — chỉ ~10 dòng nhưng là trái tim của hybrid search.
3. **Vòng lặp agent trong loop.py** (tuần 6) — gõ lại theo khung có sẵn, không copy-paste.

### Quy tắc 5 — Bạn là người viết prompt (của hệ thống) và dataset
Hai thứ quyết định chất lượng dự án mà AI không làm thay được: system prompt trong `prompts.py` (bạn phải tự tinh chỉnh qua thử nghiệm — đây là kỹ năng prompt engineering thật) và `eval/dataset.jsonl` (phải tự đọc tài liệu để viết câu hỏi + đáp án chuẩn).

### Quy tắc 6 — Nhật ký hiểu bài
Mỗi lần AI dạy bạn khái niệm mới trong lúc code, ghi 2–3 dòng vào LEARNING_LOG.md bằng lời của mình. Cuối mỗi tuần, tự trả lời các câu hỏi kiểm tra ở cột "kiến thức phải hiểu" của timeline — trả lời thành tiếng, như đang phỏng vấn.

### Quy tắc 7 — Debug trước, hỏi sau
Khi gặp lỗi: đọc traceback, tự đoán nguyên nhân, thử 1–2 cách trong 15–20 phút rồi mới đưa AI. Kỹ năng đọc lỗi là thứ phỏng vấn live-coding kiểm tra được ngay và không giả được.

---

## PHẦN 7 — TIÊU CHÍ HOÀN THÀNH (Definition of Done)

### DoD của toàn dự án
- [ ] Chạy `docker compose up` là toàn hệ thống lên
- [ ] Bộ eval ≥ 50 câu, report có bảng: baseline → +hybrid → +rerank → agent
- [ ] README: sơ đồ kiến trúc, bảng benchmark, hướng dẫn chạy, GIF demo, mục "Limitations & Future work"
- [ ] Không có API key trong lịch sử Git
- [ ] LEARNING_LOG.md có ghi chép đủ 10 tuần

### DoD của "sự hiểu bài" — tự phỏng vấn thử trước khi nộp CV
Nhờ bạn bè (hoặc chính AI, yêu cầu nó đóng vai người phỏng vấn khó tính) hỏi bạn những câu sau, trả lời thành tiếng không nhìn tài liệu:
1. Vẽ lại kiến trúc hệ thống lên giấy trắng và giải thích luồng một câu hỏi đi qua.
2. 12 câu hỏi phỏng vấn trong tài liệu lộ trình trước.
3. "Vì sao chọn Qdrant/bge-m3/FastAPI?" — trả lời bằng trade-off, không phải "vì tutorial dùng".
4. "Số liệu eval của em, con số nào em tự hào nhất và vì sao?"
5. "Phần nào trong repo em dùng AI viết? Em đã kiểm soát chất lượng thế nào?" — trả lời thẳng thắn kèm quy trình ở Phần 6. Trung thực + có quy trình là câu trả lời mạnh; giấu giếm mới là câu trả lời yếu.
6. Mở ngẫu nhiên 3 file trong repo và giải thích từng hàm.

Qua được cả 6 mục nghĩa là dự án — và bạn — sẵn sàng đi phỏng vấn.
