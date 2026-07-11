import pytest
from app.ingestion.chunker import chunk_text

def test_chunk_text_normal_case():
    """Test trường hợp cắt text bình thường xem có ra đúng số lượng và độ dài không."""
    text = "a" * 1000
    # Dự đoán logic: 
    # Chunk 1: 0 -> 300
    # Chunk 2: 250 -> 550
    # Chunk 3: 500 -> 800
    # Chunk 4: 750 -> 1050 (hết text ở 1000)
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    
    assert len(chunks) == 4
    assert len(chunks[0]) == 300

def test_chunk_text_invalid_overlap_raises_error():
    """Test xem khi truyền overlap >= chunk_size thì hàm có chủ động ném lỗi ra không."""
    with pytest.raises(ValueError):
        chunk_text("test text", chunk_size=50, overlap=50)