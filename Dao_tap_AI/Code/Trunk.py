import re, json

# ===== Mỗi lần chunk văn bản khác, chỉ sửa 3 dòng này =====
FILE_TXT = "tailieutest.txt"                                       # ← MỚI: tên file đầu vào
MA_VB    = "QD168-2026"                                            # ← MỚI: mã văn bản, không được trùng
DOC      = "Quy định tổ chức đào tạo trực tuyến (QĐ 168/QĐ-ĐHCNĐA)"  # ← SỬA: tên đầy đủ văn bản
# ===========================================================

text = open(FILE_TXT, encoding="utf-8").read()                     # ← SỬA: dùng biến FILE_TXT

dieu_re  = re.compile(r"^Điều\s+(\d+)\.\s*(.+)$", re.M)
khoan_re = re.compile(r"^(\d+)\.\s+", re.M)

chunks = []
dieus = list(dieu_re.finditer(text))
for i, d in enumerate(dieus):
    so_dieu, ten_dieu = d.group(1), d.group(2).strip()
    body = text[d.end(): dieus[i+1].start() if i+1 < len(dieus) else len(text)]
    khoans = list(khoan_re.finditer(body))
    if not khoans:                       # Điều không chia khoản
        khoans_data = [(None, body.strip())]
    else:
        khoans_data = [(k.group(1),
                        body[k.end(): khoans[j+1].start() if j+1 < len(khoans) else len(body)].strip())
                       for j, k in enumerate(khoans)]
    for so_khoan, noi_dung in khoans_data:
        nguon = f"Điều {so_dieu}" + (f", Khoản {so_khoan}" if so_khoan else "")
        chunks.append({
            "id": f"{MA_VB}-D{so_dieu}-K{so_khoan or 0}",           # ← SỬA: thêm mã văn bản vào id
            "text": f"{DOC} > Điều {so_dieu}. {ten_dieu} > {nguon}\n{noi_dung}",
            "metadata": {"ma_vb": MA_VB,                             # ← MỚI: lưu mã văn bản
                         "van_ban": DOC, "dieu": int(so_dieu), "ten_dieu": ten_dieu,
                         "khoan": int(so_khoan) if so_khoan else None, "nguon": nguon}
        })

file_out = f"chunks_{MA_VB}.json"                                  # ← MỚI: mỗi văn bản một file kết quả
json.dump(chunks, open(file_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("Đã ghi:", file_out)                                         # ← MỚI: in thông báo ra màn hình
print("Tổng số chunk:", len(chunks))
print("Ví dụ id đầu tiên:", chunks[0]["id"] if chunks else "KHÔNG CÓ CHUNK NÀO")