import sys, os
sys.path.insert(0, '.')

from app.retrieval.vector_store import VectorStore
from app.retrieval.bm25_index import build_bm25_index, search_bm25
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.reranker import Reranker
from qdrant_client import QdrantClient

vector_store = VectorStore(device=os.environ.get('DEVICE', 'cuda'))
client = QdrantClient(host='localhost', port=6333)
all_points = client.scroll(collection_name='docs', limit=200, with_payload=True)[0]
chunks = [{'id': str(p.id), 'text': p.payload['text']} for p in all_points]
chunk_lookup = {str(p.id): {'id': str(p.id), 'text': p.payload['text'], 'page': p.payload.get('page'), 'source': p.payload.get('source')} for p in all_points}
bm25 = build_bm25_index(chunks)
bm25_chunk_ids = [c['id'] for c in chunks]

query = 'làm sao chia nhỏ văn bản để không mất ý nghĩa'
candidates = hybrid_search(query, vector_store, bm25, bm25_chunk_ids, chunk_lookup, top_k=20, candidate_k=20)

reranker = Reranker(device=os.environ.get('DEVICE', 'cuda'))
results = reranker.rerank(query, candidates, top_k=5)

for r in results:
    print(round(r['rerank_score'], 4), '|', r['source'], 'tr', r['page'], ':', r['text'][:70])