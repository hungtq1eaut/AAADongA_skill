# -*- coding: utf-8 -*-
"""
Bước 2-3: Embedding các chunk và lưu vào ChromaDB, sau đó thử một câu hỏi.

Cài thư viện (một lần):
    python -m pip install chromadb sentence-transformers
Chạy:
    python embed.py
    python embed.py chunks_QD168-2026_split.json "Câu hỏi muốn thử"
"""
import json, sys
import chromadb
from sentence_transformers import SentenceTransformer

FILE = sys.argv[1] if len(sys.argv) > 1 else "chunks_QD168-2026_split.json"
QUESTION = sys.argv[2] if len(sys.argv) > 2 else "Học trực tuyến được tính bao nhiêu phần trăm?"

print("Đang tải model bge-m3 (lần đầu sẽ tải khoảng 2 GB)...")
model = SentenceTransformer("BAAI/bge-m3")

client = chromadb.PersistentClient(path="./vectordb")
col = client.get_or_create_collection("quy_che_dao_tao", metadata={"hnsw:space": "cosine"})

chunks = json.load(open(FILE, encoding="utf-8"))
texts = [c["text"] for c in chunks]
print(f"Đang embed {len(chunks)} chunk từ {FILE}...")
vecs = model.encode(texts, normalize_embeddings=True, batch_size=8, show_progress_bar=True).tolist()

col.upsert(
    ids=[c["id"] for c in chunks],
    documents=texts,
    embeddings=vecs,
    metadatas=[c["metadata"] for c in chunks],
)
print(f"Đã lưu. Collection hiện có {col.count()} chunk (thư mục ./vectordb)\n")

# Thử truy vấn
q = model.encode([QUESTION], normalize_embeddings=True).tolist()
res = col.query(query_embeddings=q, n_results=5)
print(f"CÂU HỎI: {QUESTION}\n")
for i, (doc, meta, dist) in enumerate(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), 1):
    print(f"{i}. [{meta.get('nguon', '')}] độ giống {1 - dist:.2f}")
    print(f"   {doc[:150]}...\n")
