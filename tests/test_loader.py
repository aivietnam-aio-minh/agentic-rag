from app.ingestion.loader import load_pdf

def test_load_pdf_returns_correct_page_numbers():
    pages = load_pdf(r"C:\Users\LEGION\Desktop\Sample_Claude\agentic-rag\data\finetune_Qwen.pdf")
    assert pages[0]["page"] == 1
    assert all("text" in p and "source" in p for p in pages)