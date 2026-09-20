# -*- coding: utf-8 -*-
"""
RAG viết tay — không dùng framework.
Yêu cầu: Ollama đang chạy, đã pull nomic-embed-text và một model chat.
    ollama pull nomic-embed-text
    ollama pull qwen2.5:3b
Cài thư viện: pip install requests
"""

import json
import math
import os
import glob
import requests

OLLAMA = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "qwen2.5:3b"
KHO_FILE = "kho_vector.json"

THU_MUC = "tai_lieu"
CHUNK_SIZE = 500
OVERLAP = 100
TOP_K = 3


# ---------- BƯỚC 1: Đọc tài liệu ----------
def doc_tai_lieu(thu_muc=THU_MUC):
    ket_qua = []
    for duong_dan in sorted(glob.glob(os.path.join(thu_muc, "*.txt"))):
        with open(duong_dan, "r", encoding="utf-8") as f:
            noi_dung = f.read()
        ket_qua.append({"nguon": os.path.basename(duong_dan), "text": noi_dung})
        print(f"  Đã đọc {duong_dan}: {len(noi_dung)} ký tự")
    return ket_qua


# ---------- BƯỚC 2: Cắt chunk ----------
def cat_chunk(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    """Cắt theo đoạn văn trước.
    Đoạn nào quá dài mới cắt cứng theo ký tự."""
    doan_van = [d.strip() for d in text.split("\n\n") if d.strip()]
    chunks = []
    hien_tai = ""

    for doan in doan_van:
        if len(hien_tai) + len(doan) + 2 <= chunk_size:
            hien_tai = (hien_tai + "\n\n" + doan).strip()
        else:
            if hien_tai:
                chunks.append(hien_tai)
            if len(doan) <= chunk_size:
                hien_tai = doan
            else:
                # đoạn quá dài: cắt cứng, có chồng lấn
                i = 0
                while i < len(doan):
                    chunks.append(doan[i:i + chunk_size])
                    i += chunk_size - overlap
                hien_tai = ""
    if hien_tai:
        chunks.append(hien_tai)
    return chunks


# ---------- BƯỚC 3: Gọi API embedding ----------
def lay_embedding(texts):
    """Trả về list vector. Nhận một chuỗi hoặc một list chuỗi."""
    if isinstance(texts, str):
        texts = [texts]
    r = requests.post(
        f"{OLLAMA}/api/embed",
        json={"model": EMBED_MODEL, "input": texts},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["embeddings"]


# ---------- BƯỚC 4: Xây kho vector ----------
def xay_kho():
    print("Đang đọc tài liệu...")
    tai_lieu = doc_tai_lieu()

    print("Đang cắt chunk...")
    ban_ghi = []
    for tl in tai_lieu:
        for i, c in enumerate(cat_chunk(tl["text"])):
            ban_ghi.append({
                "id": f"{tl['nguon']}#{i}",
                "text": c,
                "metadata": {"nguon": tl["nguon"], "thu_tu": i},
            })
    print(f"  Tổng cộng {len(ban_ghi)} chunk")

    print("Đang tạo embedding...")
    vectors = lay_embedding([b["text"] for b in ban_ghi])
    for b, v in zip(ban_ghi, vectors):
        b["vector"] = v
    print(f"  Mỗi vector có {len(vectors[0])} chiều")

    with open(KHO_FILE, "w", encoding="utf-8") as f:
        json.dump(ban_ghi, f, ensure_ascii=False)
    print(f"Đã lưu kho vào {KHO_FILE}")
    return ban_ghi


def nap_kho():
    with open(KHO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- BƯỚC 5: Đo độ gần nghĩa ----------
def cosine(a, b):
    tich = sum(x * y for x, y in zip(a, b))
    do_dai_a = math.sqrt(sum(x * x for x in a))
    do_dai_b = math.sqrt(sum(y * y for y in b))
    if do_dai_a == 0 or do_dai_b == 0:
        return 0.0
    return tich / (do_dai_a * do_dai_b)


# ---------- BƯỚC 6: Retriever ----------
def tim_kiem(cau_hoi, kho, k=TOP_K):
    v_hoi = lay_embedding(cau_hoi)[0]
    cham_diem = []
    for b in kho:
        cham_diem.append((cosine(v_hoi, b["vector"]), b))
    cham_diem.sort(key=lambda x: x[0], reverse=True)
    return cham_diem[:k]


# ---------- BƯỚC 7: Ghép prompt ----------
CHI_THI = """Bạn là trợ lý tư vấn học vụ của trường.

QUY TẮC BẮT BUỘC:
1. CHỈ trả lời dựa trên các tài liệu được cung cấp bên dưới.
2. Nếu tài liệu không đủ thông tin, hãy nói rõ
   "Tôi không có thông tin về vấn đề này" và khuyên sinh viên
   liên hệ phòng đào tạo. Tuyệt đối không suy đoán.
3. Sau mỗi ý, ghi rõ nguồn trong ngoặc vuông, ví dụ [quy_che.txt].
4. Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng.

=== TÀI LIỆU ===
{context}
=== HẾT TÀI LIỆU ==="""


def ghep_prompt(cau_hoi, ket_qua):
    khoi_tai_lieu = []
    for diem, b in ket_qua:
        khoi_tai_lieu.append(f"[{b['metadata']['nguon']}]\n{b['text']}")
    context = "\n\n---\n\n".join(khoi_tai_lieu)
    return CHI_THI.format(context=context), cau_hoi


# ---------- BƯỚC 8: Gọi LLM ----------
def hoi_llm(system, user):
    r = requests.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": CHAT_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": 0},
        },
        timeout=300,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]


# ---------- BƯỚC 9: Ghép toàn bộ ----------
def tra_loi(cau_hoi, kho, hien_chunk=False):
    ket_qua = tim_kiem(cau_hoi, kho)

    if hien_chunk:
        print("\n--- CÁC CHUNK ĐƯỢC LẤY ---")
        for diem, b in ket_qua:
            print(f"[{diem:.4f}] {b['id']}: {b['text'][:100]}...")
        print("--- HẾT ---\n")

    system, user = ghep_prompt(cau_hoi, ket_qua)
    return hoi_llm(system, user)


if __name__ == "__main__":
    if not os.path.exists(KHO_FILE):
        kho = xay_kho()
    else:
        kho = nap_kho()
        print(f"Đã nạp kho: {len(kho)} chunk")

    print("\nGõ câu hỏi ('thoat' để dừng).")
    print("Thêm '?' ở đầu câu hỏi để xem chunk lấy được.\n")
    while True:
        try:
            cau_hoi = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cau_hoi or cau_hoi.lower() == "thoat":
            break
        hien = cau_hoi.startswith("?")
        if hien:
            cau_hoi = cau_hoi[1:].strip()
        print("\nTrợ lý:", tra_loi(cau_hoi, kho, hien_chunk=hien), "\n")
