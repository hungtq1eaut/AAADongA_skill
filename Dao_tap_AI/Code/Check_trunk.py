# pip install transformers sentencepiece
import json, sys
from collections import Counter
from transformers import AutoTokenizer

FILE = sys.argv[1] if len(sys.argv) > 1 else "chunks_QD168-2026.json"
MAX_TOKENS = 1000
REQUIRED_META = ["ma_vb", "van_ban", "dieu", "ten_dieu", "nguon"]

tok = AutoTokenizer.from_pretrained("BAAI/bge-m3")  # đếm token đúng theo model sẽ embed
chunks = json.load(open(FILE, encoding="utf-8"))
loi = 0

# 1. Trùng id
for id_, n in Counter(c.get("id") for c in chunks).items():
    if n > 1:
        print(f"[TRÙNG ID] {id_} xuất hiện {n} lần"); loi += 1

# 2. Trùng nội dung
for t, n in Counter(c.get("text", "").strip() for c in chunks).items():
    if n > 1 and t:
        print(f"[TRÙNG TEXT] {n} chunk giống nhau: {t[:80]}..."); loi += 1

lengths = []
for c in chunks:
    cid, text, meta = c.get("id", "?"), c.get("text", ""), c.get("metadata", {})

    # 3. Rỗng hoặc chỉ có tiền tố đường dẫn, không có nội dung
    body = text.split(">")[-1].strip()
    if not text.strip() or len(body) < 20:
        print(f"[RỖNG/QUÁ NGẮN] {cid}: '{text[:80]}'"); loi += 1

    # 4. Quá dài
    n_tok = len(tok.encode(text, add_special_tokens=False))
    lengths.append((n_tok, cid))
    if n_tok > MAX_TOKENS:
        print(f"[QUÁ DÀI] {cid}: {n_tok} token -> nên tách theo Điểm"); loi += 1

    # 5. Thiếu metadata
    thieu = [k for k in REQUIRED_META if meta.get(k) in (None, "")]
    if thieu:
        print(f"[THIẾU METADATA] {cid}: thiếu {thieu}"); loi += 1

# Thống kê
lengths.sort()
print(f"\nTổng {len(chunks)} chunk | token: min {lengths[0][0]}, "
      f"max {lengths[-1][0]} ({lengths[-1][1]}), TB {sum(l for l,_ in lengths)//len(lengths)}")
print("5 chunk dài nhất:", lengths[-5:])
print("KẾT QUẢ:", "OK, không có lỗi" if loi == 0 else f"{loi} lỗi cần sửa")