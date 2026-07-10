# SRS — Agentic RAG Assistant (Trợ lý nghiên cứu tài liệu thông minh)

> Đặc tả yêu cầu rút gọn. Điền trước khi viết dòng code đầu tiên. Agent (Claude Code) sẽ đọc file này ở bước Plan Mode của mọi feature.

## 1. Mục tiêu sản phẩm

Hệ thống hỏi đáp trên kho tài liệu riêng (văn bản pháp luật lao động / tài liệu nội bộ) dành cho nhân viên HR và người lao động cần tra cứu quy định. Điểm khác biệt so với RAG thường: có tầng agent tự phân tích câu hỏi, chọn công cụ (tra tài liệu / tính toán / tìm web), tự kiểm tra chất lượng kết quả tìm kiếm, và luôn trả lời kèm trích dẫn nguồn. Đây là đồ án cá nhân phục vụ portfolio xin việc AI Engineer fresher — chất lượng đo được bằng bộ eval là ưu tiên số một.

## 2. Functional Requirements

- FR-01: Người dùng upload tài liệu PDF/DOCX qua UI; hệ thống tự đọc, chunk, embed và đánh index. *(Bắt buộc)*
- FR-02: Người dùng đặt câu hỏi tiếng Việt qua giao diện chat. *(Bắt buộc)*
- FR-03: Câu trả lời dựa trên tài liệu, kèm trích dẫn dạng [tên nguồn, số trang] cho mọi thông tin lấy từ tài liệu. *(Bắt buộc)*
- FR-04: Khi tài liệu không chứa thông tin, hệ thống trả lời rõ "tài liệu không đề cập" — không suy diễn, không bịa. *(Bắt buộc)*
- FR-05: Retrieval dùng hybrid search: vector search (bge-m3) + BM25, gộp bằng Reciprocal Rank Fusion, sau đó rerank bằng cross-encoder. *(Bắt buộc)*
- FR-06: Agent tự phân loại câu hỏi và chọn tool: `search_docs` / `calculator` / `web_search`. *(Bắt buộc)*
- FR-07: Với câu hỏi phức, agent tách thành các truy vấn con, xử lý từng phần rồi tổng hợp. *(Bắt buộc)*
- FR-08: Agent tự đánh giá kết quả retrieval (grading); nếu thiếu thì viết lại truy vấn và tìm lại, tối đa 2 lần. *(Bắt buộc)*
- FR-09: UI hiển thị tiến trình agent theo thời gian thực ("đang tra tài liệu…", "đang tính toán…"). *(Nên có)*
- FR-10: Câu trả lời stream từng phần về UI (SSE). *(Nên có)*
- FR-11: Chế độ RAG tĩnh (không agent) chạy song song làm baseline, chọn được từ UI/API — phục vụ so sánh trong eval. *(Bắt buộc — phục vụ mục tiêu portfolio)*
- FR-12: Script eval chạy được cả hai chế độ trên cùng dataset và xuất báo cáo so sánh. *(Bắt buộc)*
- FR-13: Quản lý nhiều bộ tài liệu (collection) riêng. *(Tùy chọn)*
- FR-14: Lưu lịch sử hội thoại, hỏi tiếp theo ngữ cảnh. *(Tùy chọn)*

## 3. Non-Functional Requirements

| Loại | Yêu cầu |
|---|---|
| Latency | Câu hỏi đơn giản (RAG tĩnh) < 10s; câu hỏi agent nhiều bước < 30s; upload + index tài liệu 50 trang < 30s trên máy dev (GPU) và < 60s ở chế độ CPU (bản deploy) |
| Throughput | 1 người dùng đồng thời là đủ (demo cá nhân); API viết async để không tự chặn chính mình |
| Độ khả dụng | Không yêu cầu HA; agent phải LUÔN dừng (MAX_STEPS=6, retries≤2); tool lỗi trả thông báo lỗi cho agent, không làm sập request |
| Bảo mật / dữ liệu | API key chỉ nằm trong `.env` (gitignore); calculator dùng `numexpr`, cấm `eval()` trần; không log nội dung tài liệu ra file log |
| Giới hạn tài nguyên | Máy dev: RTX 5060 8GB VRAM — embedding + reranker chạy GPU; LLM dev qua Ollama (model ≤7B quantized) hoặc API. BẮT BUỘC: mọi thành phần chạy được cả chế độ CPU thuần qua config `DEVICE=cpu`, vì bản deploy demo chạy trên máy chủ không GPU (xem ADR-006) |
| Chất lượng (đo bằng eval) | Trên bộ ≥50 câu tự xây: faithfulness ≥ 0.85, context precision ≥ 0.75; chi phí trung bình < 0.05 USD/câu (log token) |

## 4. Ràng buộc đã biết trước

- Ngân sách API: ~5–10 USD, dồn chủ yếu cho eval cuối (LLM giám khảo RAGAS cần model tốt); dev hằng ngày dùng Ollama local trên GPU hoặc Gemini free tier.
- GPU RTX 5060 thuộc kiến trúc Blackwell (sm_120) → yêu cầu PyTorch build cho CUDA 12.8 trở lên; phiên bản torch/CUDA phải được ghim trong `requirements.txt` và ghi trong README (bản PyTorch cũ sẽ không nhận GPU này).
- Deadline: 10 tuần, một người làm, 15–20 giờ/tuần.
- Tài liệu nguồn là PDF tiếng Việt dạng text (không cam kết xử lý PDF scan ở phiên bản này).
- Toàn bộ hệ thống phải chạy được bằng `docker compose up` (tiêu chí demo phỏng vấn).

## 5. Out of Scope

- Đăng nhập / phân quyền người dùng.
- Fine-tune model — vẫn ngoài phạm vi phiên bản này, nhưng ghi vào Future Work rằng máy dev đủ sức QLoRA model ≤7B trên 8GB VRAM (hướng mở rộng portfolio sau khi xong project chính).
- OCR cho PDF scan; trích xuất bảng biểu/ảnh phức tạp trong PDF.
- Đa ngôn ngữ ngoài tiếng Việt (tiếng Anh hoạt động tự nhiên nhờ model, không tối ưu riêng).
- Tối ưu chịu tải nhiều người dùng đồng thời; không làm autoscaling, không làm message queue.
- Mobile app; chỉ có web UI (Streamlit).

**Lưu ý cho agent:** không tự ý implement các mục trong danh sách này kể cả khi "tiện tay".

## 6. Người dùng / kịch bản sử dụng chính

1. **Tra cứu đơn giản:** Nhân viên hỏi "nghỉ thai sản được mấy tháng?" → agent chọn `search_docs` → trả lời kèm [Bộ luật Lao động 2019, Điều 139].
2. **Câu hỏi phức đa bước:** "So sánh chế độ nghỉ phép trong nội quy công ty với quy định của luật hiện hành" → agent tách 2 truy vấn con (nội quy công ty / luật), tra riêng từng nguồn, tổng hợp thành bảng so sánh có trích dẫn cả hai.
3. **Cần tính toán:** "Lương gross 20 triệu thì nhận về bao nhiêu?" → agent tra công thức/tỷ lệ trong tài liệu bằng `search_docs`, rồi gọi `calculator` để tính, trả kết quả kèm cách tính.
4. **Ngoài phạm vi tài liệu:** "Mức lương tối thiểu vùng năm 2026?" → tài liệu cũ không có → grading phát hiện thiếu → agent dùng `web_search` và ghi rõ nguồn web, hoặc trả lời "tài liệu không đề cập" nếu web search bị tắt.

## 7. Tiêu chí hoàn thành (Definition of Done)

**DoD cho mỗi feature:**
- Code có type hints, qua lint (ruff); hàm public có docstring ngắn.
- Có test tối thiểu cho logic thuần (chunker, RRF, parser) — không bắt buộc test phần gọi LLM.
- Nếu feature ảnh hưởng chất lượng trả lời (chunking, retrieval, prompt, agent): chạy lại `eval/run_eval.py`, ghi số liệu vào `eval/report.md` trước khi merge.
- Commit message theo Conventional Commits; không có secret trong diff.

**DoD cho toàn dự án:**
- `docker compose up` chạy được toàn hệ thống từ máy sạch.
- `eval/report.md` có bảng: baseline → +hybrid → +rerank → agent, kèm latency và chi phí.
- README: sơ đồ kiến trúc, bảng benchmark, hướng dẫn chạy, GIF demo, mục Limitations & Future work.
- Không có API key trong toàn bộ lịch sử Git.
- Người làm dự án giải thích được mọi file trong repo (kiểm tra bằng bài tự phỏng vấn 6 mục trong kế hoạch).
