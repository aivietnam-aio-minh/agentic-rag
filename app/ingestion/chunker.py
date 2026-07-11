def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Cắt văn bản thành các đoạn chồng lấn nhau."""
    # Chặn lỗ hổng treo vô hạn
    if overlap >= chunk_size:
        raise ValueError("Overlap phải nhỏ hơn chunk_size để tránh vòng lặp vô hạn.")
    # 1. Tạo một list rỗng để chứa các đoạn text sau khi cắt (ví dụ: chunks = [])
    chunks = []
    # 2. Tạo biến 'start' bắt đầu từ vị trí 0
    start = 0
    # 3. Dùng vòng lặp `while start < len(text):`
    #    - Bắt đầu cắt: chunk = text[start : start + chunk_size]
    #    - Thêm 'chunk' vào list kết quả
    #    - Tính toán vị trí 'start' mới để dịch chuyển (gợi ý: cộng thêm một khoảng hiệu số)
    while start < len(text):
        chunk = text[start : start + chunk_size]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks       
    