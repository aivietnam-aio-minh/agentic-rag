from app.ingestion.indexer import index_document

def test_index_document_returns_correct_count():
    n = index_document("data/finetune_Qwen.pdf", collection_name="test_docs", device="cuda")
    assert n > 0