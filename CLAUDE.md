# CLAUDE.md — Hướng dẫn cho agent trong repo này

> File này được Claude Code đọc ở đầu mỗi phiên. Giữ ngắn gọn (~100 dòng).
> Nội dung chi tiết/dài tách ra file riêng trong docs/ và trỏ tới từ đây.

## Dự án

Agentic RAG Assistant — hệ thống hỏi đáp tài liệu tiếng Việt có trích dẫn nguồn, với tầng agent tự chọn tool (tra tài liệu / tính toán / tìm web) và tự kiểm tra kết quả. Đồ án portfolio của một fresher AI Engineer: **chủ repo đang học, nên mọi code phải kèm giải thích ngắn gọn "vì sao", không chỉ "làm gì"**.

- SRS: `./SRS.md` — đọc mục 5 (Out of Scope) trước khi đề xuất bất kỳ tính năng nào
- Architecture: `./ARCHITECTURE.md` — tuân thủ ranh giới module ở mục 4 và các ADR
- Kế hoạch & quy tắc làm việc: `./docs/ke-hoach-thuc-hien-agentic-rag.md`
- Quy trình Git: `./docs/GIT_WORKFLOW.md` — chủ repo đang học Git từ đầu; xem mục "Không được làm" bên dưới

## Lệnh thường dùng
```bash
# run local (cần Qdrant chạy trước)
docker compose up -d qdrant
uvicorn app.main:app --reload
streamlit run ui/streamlit_app.py

# test
pytest tests/ -v

# lint + format
ruff check app/ tests/ --fix
ruff format app/ tests/

# eval (chạy sau mọi thay đổi ảnh hưởng chất lượng trả lời)
python eval/run_eval.py --mode all   # baseline | agent-loop | agent-graph | all

# LLM local khi dev (tùy chọn, xem ADR-006)
ollama serve                          # sau đó đặt LLM_PROVIDER=ollama trong .env
nvidia-smi                            # kiểm tra VRAM trước khi load thêm model

# git — xem docs/GIT_WORKFLOW.md để hiểu đầy đủ (chủ repo mới học Git)
git status && git diff                # LUÔN xem trước khi add/commit
git checkout -b feature/<ten-viec>    # 1 tính năng = 1 nhánh
git add . && git commit -m "feat: ..."
git push origin feature/<ten-viec>    # rồi mở Pull Request trên GitHub, không tự merge qua CLI
```

## Quy ước code

- Python 3.12; type hints bắt buộc cho mọi hàm public; docstring ngắn 1–3 dòng.
- Cấu trúc thư mục: theo `ARCHITECTURE.md` mục 4. Phụ thuộc một chiều: `ui → api → (rag|agent) → retrieval → stores`.
- Gọi LLM: CHỈ qua `app/llm/client.py` (ADR-001). Prompt: CHỈ đặt trong `app/llm/prompts.py`.
- Config/secret: đọc từ `app/config.py` (pydantic-settings + `.env`). Không hardcode model name, đường dẫn, key.
- Thiết bị model: đọc `settings.DEVICE` (`cuda`/`cpu`), CẤM hardcode `.to("cuda")`. Mọi đường chạy phải hoạt động ở chế độ CPU thuần — CI và bản deploy đều không có GPU (ADR-006).
- Naming: snake_case cho hàm/biến, PascalCase cho class; tên file trùng tên module chức năng.
- Error handling: tool của agent bắt exception và trả CHUỖI mô tả lỗi cho LLM đọc, không raise xuyên request. Mọi vòng lặp agent phải có giới hạn bước.
- Commit: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).

## Trước khi code

Với mọi feature không tầm thường, trình bày kế hoạch (Plan Mode) trước: những file sẽ tạo/sửa, rủi ro, điểm cần người dùng quyết định — rồi mới viết code. Sau khi code xong một khối, thêm 2–4 dòng giải thích thiết kế để chủ repo học (theo quy tắc "vibe coding có kiểm soát" trong docs/).

## Không được làm (ranh giới quyền hạn)

- Không tự ý thêm dependency mới mà không hỏi trước; không tự ý đổi phiên bản torch/CUDA đã ghim (RTX 5060 cần build CUDA 12.8+, xem NFR và ADR-006).
- Không load đồng thời LLM local + embedding + reranker lên GPU (tràn 8GB VRAM); không tự ý đổi model Ollama mặc định sang model lớn hơn 7B.
- Không tự ý đổi schema collection Qdrant hoặc format `eval/dataset.jsonl`.
- Không chạy lệnh phá hủy dữ liệu (xóa collection, rm -rf, ghi đè data/) mà không xác nhận.
- Không sửa file ngoài phạm vi task đang làm; không "tiện tay" refactor lớn.
- Không implement những gì nằm trong SRS mục 5 (Out of Scope).
- Không dùng `eval()` trần trong calculator (dùng numexpr — NFR bảo mật).
- Không viết hộ: system prompt chính, `eval/dataset.jsonl`, và 3 phần chủ repo tự viết tay (cosine similarity, RRF, `agent/loop.py` bản đầu) — chỉ được review/góp ý khi được yêu cầu.
- Tuyệt đối không commit `.env` hoặc in API key ra log/console.
- Không tự ý `git commit`, `git push`, hay merge nhánh thay chủ repo — chủ repo đang học Git và cần tự tay gõ các lệnh này (xem `docs/GIT_WORKFLOW.md`). Agent có thể ĐỀ XUẤT message commit, không tự chạy lệnh.

## Bài học tích lũy

<!-- Mỗi lần agent làm sai và được sửa, thêm 1 dòng vào đây để không lặp lại -->
-

## Skill liên quan trong repo này

<!-- Liệt kê các skill trong .claude/skills/ và khi nào chúng kích hoạt -->
- (chưa có — sẽ bổ sung nếu tạo skill riêng, ví dụ skill chạy eval và cập nhật report)
