# Git Workflow — Học Git Từ Đầu Qua Chính Project Này

> Dành cho người CHƯA DÙNG GIT BAO GIỜ. Đọc phần 1–3 trước khi gõ lệnh đầu tiên.
> Gồm 6 phần: (1) Git là gì, (2) 8 lệnh sống còn, (3) setup ban đầu, (4) chiến lược nhánh, (5) lịch commit bám 10 tuần, (6) xử lý tình huống thường gặp.

---

## 1. GIT LÀ GÌ — HIỂU TRƯỚC KHI GÕ LỆNH

Git là công cụ **ghi lại lịch sử thay đổi của code**, giống như "save point" trong game — mỗi lần bạn commit là một điểm lưu bạn có thể quay lại bất cứ lúc nào. Ba khái niệm cốt lõi, hiểu đúng 3 cái này là hiểu 80% Git:

- **Repository (repo):** thư mục project được Git theo dõi. Nó có một thư mục ẩn `.git/` chứa toàn bộ lịch sử.
- **Commit:** một "ảnh chụp" trạng thái code tại một thời điểm, kèm mô tả (message) bạn tự viết. Commit không xóa lịch sử cũ — nó luôn cộng thêm.
- **Branch (nhánh):** một đường phát triển song song. `main` là nhánh chính, luôn ổn định. Khi làm tính năng mới, bạn tạo nhánh riêng để không làm hỏng `main` nếu code chưa xong.

Còn **GitHub** là nơi lưu bản sao repo của bạn trên mạng (gọi là "remote") — để có backup, để người khác (nhà tuyển dụng) xem được, và để làm việc từ nhiều máy.

Luồng làm việc điển hình mỗi ngày, hình dung trước khi học lệnh:

```
1. Mở thư mục project
2. Sửa code (thêm tính năng, sửa lỗi...)
3. Xem đã sửa gì:        git status
4. Đánh dấu file cần lưu: git add ...
5. Lưu lại kèm mô tả:    git commit -m "..."
6. Đẩy lên GitHub:       git push
```

## 2. TÁM LỆNH SỐNG CÒN (học thuộc trước, phần sau chỉ là áp dụng)

```bash
git status                  # Xem hiện tại có gì thay đổi chưa lưu — GÕ LỆNH NÀY LIÊN TỤC,
                             # nó không hại gì cả, chỉ hiển thị thông tin

git add <file>               # Đánh dấu 1 file để chuẩn bị commit
git add .                    # Đánh dấu TẤT CẢ file đã thay đổi trong thư mục hiện tại

git commit -m "mô tả"        # Lưu lại "ảnh chụp" các file đã add, kèm mô tả ngắn

git log --oneline            # Xem lịch sử các commit đã lưu (mỗi dòng 1 commit)

git branch <ten-nhanh>       # Tạo nhánh mới (chưa chuyển sang nó)
git checkout <ten-nhanh>     # Chuyển sang nhánh đó
git checkout -b <ten-nhanh>  # Tạo NHÁNH MỚI và chuyển sang luôn — lệnh dùng nhiều nhất

git push origin <ten-nhanh>  # Đẩy nhánh hiện tại lên GitHub
git pull                    # Kéo thay đổi mới nhất từ GitHub về máy
```

Ghi chú quan trọng cho người mới:
- `git add .` thêm MỌI file thay đổi — kể cả file bạn không muốn (log, cache...). Luôn `git status` trước để xem sắp add gì.
- Commit message tốt: ngắn, nói rõ **làm gì**, thì hiện tại. Ví dụ: `"add pdf loader function"` chứ không phải `"update"` hay `"fix bug"`.
- `git commit` chỉ lưu **trên máy bạn**. Phải `git push` thì GitHub mới thấy.

## 3. SETUP LẦN ĐẦU (làm đúng 1 lần cho cả project)

```bash
# Bước 1 — cài đặt danh tính (chỉ cần làm 1 lần trên máy, dùng cho mọi repo)
git config --global user.name "Tên bạn"
git config --global user.email "email_dang_ky_github@example.com"

# Bước 2 — vào thư mục project, khởi tạo repo
cd agentic-rag
git init                          # Tạo thư mục .git/ — từ giờ Git theo dõi thư mục này

# Bước 3 — tạo .gitignore TRƯỚC KHI COMMIT ĐẦU TIÊN (cực quan trọng, xem phần 6.1)
# (tự tạo file .gitignore với nội dung ở mục 6.1 bên dưới)

# Bước 4 — commit đầu tiên
git add .
git commit -m "docs: add SRS, ARCHITECTURE, CLAUDE.md"

# Bước 5 — tạo repo rỗng trên GitHub.com (nút "New repository", KHÔNG tick
# "Initialize with README" để tránh xung đột), rồi nối máy bạn với nó:
git remote add origin https://github.com/<username>/agentic-rag.git
git branch -M main
git push -u origin main            # -u nhớ luôn để lần sau chỉ cần gõ "git push"
```

Sau bước 5, mở link `https://github.com/<username>/agentic-rag` sẽ thấy đúng 3 file bạn vừa commit. Đó là bằng chứng đầu tiên cho CV.

## 4. CHIẾN LƯỢC NHÁNH (branch) — ĐƠN GIẢN HÓA CHO 1 NGƯỜI

Công ty thật dùng quy trình phức tạp (pull request, code review...). Với project cá nhân, dùng bản rút gọn nhưng vẫn đúng tinh thần:

- `main` — luôn là bản chạy được. Không bao giờ code dở dang nằm ở đây.
- `feature/<ten-viec>` — mỗi tính năng lớn (theo từng tuần trong kế hoạch) một nhánh riêng.

Quy trình cho **mỗi tính năng**:

```bash
git checkout main
git pull                              # đảm bảo main đang mới nhất
git checkout -b feature/pdf-loader    # tạo nhánh cho việc đang làm

# ... code, sửa nhiều lần, mỗi lần xong 1 phần thì:
git add .
git commit -m "feat: add pdf loader with page tracking"

# ... code tiếp, commit tiếp (1 tính năng có thể nhiều commit nhỏ, ĐÓ LÀ BÌNH THƯỜNG)
git add .
git commit -m "feat: handle empty pages in pdf loader"

# Xong tính năng, tự tin chạy được → đẩy lên GitHub
git push origin feature/pdf-loader

# Trên GitHub.com: bấm "Compare & pull request" → "Merge pull request"
# (Đây là thao tác "merge" — gộp nhánh feature vào main)

# Về máy, cập nhật main và dọn nhánh cũ
git checkout main
git pull
git branch -d feature/pdf-loader
```

Vì sao làm qua GitHub UI để merge (thay vì `git merge` trên máy)? Vì thao tác này **chính là kỹ năng Pull Request** mà mọi công ty dùng — luyện luôn từ đầu, và giao diện GitHub cho bạn xem rõ diff (chỗ nào thêm/xóa) trước khi gộp, tốt cho việc tự review lại code AI viết hộ (đúng quy tắc "vibe coding có kiểm soát").

## 5. LỊCH COMMIT BÁM SÁT 10 TUẦN

Mỗi tuần trong kế hoạch có sẵn 1+ nhánh gợi ý. Tick vào ô khi đã tạo nhánh, commit, và merge xong.

| Tuần | Nhánh gợi ý | Commit tối thiểu nên có |
|---|---|---|
| 0 | (làm thẳng trên `main`) | `docs: add SRS, ARCHITECTURE, CLAUDE.md`, `chore: setup venv and gitignore` |
| 1 | `feature/python-warmup` | `chore: python practice exercises` (bài tập OOP/async) |
| 2 | `feature/embedding-experiment` | `experiment: cosine similarity notebook` |
| 3 | `feature/ingestion-pipeline`, `feature/rag-mvp` | `feat: add pdf loader`, `feat: add fixed-size chunker`, `feat: wire faiss + first RAG answer` |
| 4 | `feature/eval-baseline` | `feat: build eval dataset (50 questions)`, `feat: add ragas scoring script` |
| 5 | `feature/hybrid-search` | `feat: add bm25 index`, `feat: implement RRF fusion`, `test: add hybrid search tests` |
| 6 | `feature/reranker`, `feature/agent-loop` | `feat: add cross-encoder reranker`, `feat: implement agent tool loop`, `feat: add calculator tool with numexpr` |
| 7 | `feature/langgraph-agent` | `feat: add langgraph state graph`, `feat: add corrective rag grading node` |
| 8 | `feature/fastapi-streaming` | `feat: add sse streaming endpoint`, `feat: run comparative eval baseline vs agent` |
| 9 | `feature/docker-deploy` | `feat: add dockerfile and compose`, `ci: add github actions lint+test` |
| 10 | `docs/final-readme` | `docs: write final README with benchmarks and demo gif` |

Quy tắc tối thiểu: **mỗi buổi ngồi code ít nhất 1 commit**. Đừng đợi "xong hẳn tính năng" mới commit — commit nhỏ, thường xuyên, dễ quay lại nếu code sau này làm hỏng cái trước (dùng `git log` để soi lại).

## 6. XỬ LÝ TÌNH HUỐNG THƯỜNG GẶP

### 6.1 `.gitignore` — bắt buộc tạo TRƯỚC commit đầu tiên

```gitignore
# Secrets — TUYỆT ĐỐI không để lộ
.env

# Python
.venv/
__pycache__/
*.pyc

# Data & model cache
data/
qdrant_data/
*.pkl

# IDE
.vscode/
.idea/

# Jupyter
.ipynb_checkpoints/
```

### 6.2 Lỡ commit file `.env` chứa API key — xử lý ngay lập tức

```bash
# Nếu CHƯA push lên GitHub:
git rm --cached .env
echo ".env" >> .gitignore
git commit -m "fix: remove .env from tracking"

# Nếu ĐÃ push lên GitHub: coi như key đã lộ công khai.
# Việc bắt buộc: vào nơi cấp API key, THU HỒI (revoke) key đó ngay
# và tạo key mới — xóa khỏi lịch sử Git không đủ, vì Git lưu lại lịch sử,
# ai đó vẫn xem được commit cũ nếu không dọn lịch sử kỹ (dùng git filter-repo).
# Với project cá nhân: thu hồi key là đủ, không cần dọn lịch sử phức tạp.
```

### 6.3 Quên đang ở nhánh nào

```bash
git branch          # dấu * đứng trước tên nhánh hiện tại
git status          # dòng đầu tiên cũng ghi "On branch ..."
```

### 6.4 Commit nhầm, muốn sửa message commit gần nhất (chưa push)

```bash
git commit --amend -m "message đúng"
```

### 6.5 Muốn xem mình đã sửa gì trước khi commit

```bash
git diff             # xem chi tiết thay đổi (dòng thêm màu xanh, xóa màu đỏ)
```

### 6.6 Conflict khi merge (hiếm gặp vì làm 1 mình, nhưng nên biết)

Xảy ra khi Git không tự gộp được 2 thay đổi trên cùng dòng code. Git sẽ đánh dấu trong file kiểu:
```
<<<<<<< HEAD
code hiện tại của bạn
=======
code từ nhánh đang merge vào
>>>>>>> feature/xyz
```
Việc cần làm: mở file, tự quyết định giữ đoạn nào (hoặc gộp cả hai), xóa các dòng `<<<<<<<`, `=======`, `>>>>>>>`, rồi `git add <file>` và `git commit` để hoàn tất merge.

---

## Checklist học Git qua project này

- [ ] Hiểu 3 khái niệm: repo, commit, branch (Phần 1)
- [ ] Tự gõ được 8 lệnh ở Phần 2 mà không nhìn tài liệu
- [ ] Setup xong repo + đẩy commit đầu tiên lên GitHub (Phần 3)
- [ ] Tự làm được 1 vòng feature branch → commit → push → merge trên GitHub (Phần 4)
- [ ] Tới tuần 10, `git log --oneline` cho thấy lịch sử commit đều đặn qua các tuần — đây chính là "bằng chứng" cho nhà tuyển dụng
- [ ] Biết cách xử lý khi lỡ commit `.env` (Phần 6.2) — kể được câu chuyện này khi phỏng vấn về bảo mật
