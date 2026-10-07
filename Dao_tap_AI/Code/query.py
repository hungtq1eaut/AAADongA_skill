# -*- coding: utf-8 -*-
"""
Hỏi thử vector DB (KHÔNG embed lại dữ liệu).
Chạy embed.py trước một lần để tạo thư mục ./vectordb.

Chạy:
    python query.py
Sau đó gõ câu hỏi, Enter. Gõ "q" để thoát.
"""
import chromadb
from sentence_transformers import SentenceTransformer

print("Đang tải model (chỉ một lần khi mở)...")
model = SentenceTransformer("BAAI/bge-m3")
col = chromadb.PersistentClient(path="./vectordb").get_collection("quy_che_dao_tao")
print(f"Sẵn sàng. Vector DB có {col.count()} chunk.\n")

while True:
    q = input("Câu hỏi (q để thoát): ").strip()
    if not q:
        continue
    if q.lower() == "q":
        break
    vec = model.encode([q], normalize_embeddings=True).tolist()
    res = col.query(query_embeddings=vec, n_results=5)
    print()
    for i, (doc, meta, dist) in enumerate(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), 1):
        print(f"{i}. [{meta.get('nguon', '')}] độ giống {1 - dist:.2f}")
        print(f"   {doc[:150]}...\n")
