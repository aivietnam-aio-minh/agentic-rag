import os

import fitz


def load_pdf(file_path: str) -> list[dict]:
    """Đọc PDF text-based theo từng trang, bỏ qua trang trắng.

    Không xử lý PDF scan/OCR (ngoài phạm vi, xem SRS mục 5).
    """
    source = os.path.basename(file_path)
    pages: list[dict] = []

    with fitz.open(file_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            text = page.get_text().strip()
            if not text:
                continue
            pages.append({"text": text, "page": page_number, "source": source})

    return pages
