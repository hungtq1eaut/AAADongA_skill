# -*- coding: utf-8 -*-
"""
Tách các chunk quá dài thành nhiều phần nhỏ, giữ nguyên tiền tố "Văn bản > Điều > Khoản".
Cắt đệ quy: Điểm a), b)... -> xuống dòng -> hết câu -> ô bảng -> cuối cùng theo số từ.

Cách chạy:
    python split_long.py chunks_QD168-2026.json
Kết quả: chunks_QD168-2026_split.json
"""
import json, re, sys, copy
from transformers import AutoTokenizer

IN = sys.argv[1] if len(sys.argv) > 1 else "chunks_QD168-2026.json"
OUT = IN.replace(".json", "_split.json")
MAX = 600  # số token tối đa mỗi chunk sau khi tách

tok = AutoTokenizer.from_pretrained("BAAI/bge-m3")


def ntok(s):
    return len(tok.encode(s, add_special_tokens=False))


PATTERNS = [
    r'(?=(?:^|\n|\s)[a-zđ]\)\s)',  # Điểm a), b), đ)
    r'\n+',                         # xuống dòng
    r'(?<=[.;:])\s+',               # hết câu / chấm phẩy / hai chấm
    r'\s*\|\s*',                    # ô bảng dạng |
]


def split_rec(s, limit, level=0):
    """Cắt s thành các mảnh <= limit token, thử lần lượt từng mẫu, đệ quy nếu còn dài."""
    if ntok(s) <= limit:
        return [s]
    for i in range(level, len(PATTERNS)):
        parts = [p.strip() for p in re.split(PATTERNS[i], s) if p.strip()]
        if len(parts) > 1:
            return [x for p in parts for x in split_rec(p, limit, i + 1)]
    # Cách cuối cùng: cắt theo số từ
    words, step = s.split(), 250
    return [" ".join(words[k:k + step]) for k in range(0, len(words), step)]


def split_header(text):
    """Tách phần đường dẫn (header) và phần nội dung (body)."""
    head, sep, body = text.rpartition(" > ")
    if not sep:
        return "", text
    khoan_line, colon, rest = body.partition(":")
    if colon and len(khoan_line) < 150:
        return f"{head} > {khoan_line}:", rest.strip()
    return head + " >", body


def main():
    chunks = json.load(open(IN, encoding="utf-8"))
    out = []
    for c in chunks:
        text = c["text"]
        if ntok(text) <= MAX:
            out.append(c)
            continue

        header, body = split_header(text)
        limit = MAX - ntok(header) - 10

        # Gom các mảnh nhỏ lại cho đến gần giới hạn
        pieces, cur = [], ""
        for u in split_rec(body, limit):
            cand = (cur + " " + u).strip()
            if cur and ntok(cand) > limit:
                pieces.append(cur)
                cur = u
            else:
                cur = cand
        if cur:
            pieces.append(cur)

        for i, p in enumerate(pieces, 1):
            nc = copy.deepcopy(c)
            nc["id"] = f'{c["id"]}-P{i}'
            nc["text"] = f"{header} {p}".strip()
            nc.setdefault("metadata", {})["phan"] = i
            out.append(nc)
        sizes = [ntok(f"{header} {p}") for p in pieces]
        print(f'{c["id"]}: {ntok(text)} token -> tách thành {len(pieces)} phần {sizes}')

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nĐã ghi {len(out)} chunk vào {OUT}")


if __name__ == "__main__":
    main()
