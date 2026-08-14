#!/usr/bin/env bash
set -euo pipefail
BASE="/data/snapshots"
[ -d "$BASE" ] || { echo "No snapshots dir: $BASE"; exit 0; }

LATEST="$(readlink -f "$BASE/latest" 2>/dev/null || true)"

# Lấy danh sách thư mục snapshot (loại 'latest'), sắp xếp theo mtime: mới -> cũ
mapfile -t SNAPS < <(
  find "$BASE" -mindepth 1 -maxdepth 1 -type d ! -name latest -printf '%T@ %p\n' \
  | sort -nr \
  | awk '{ $1=""; sub(/^ /,""); print }'
)

printf '%s\n' 'Idx  Snapshot name                 Created at           Size   Mark'
printf '%s\n' '---- ----------------------------- ------------------- ------ ----'

i=1
for S in "${SNAPS[@]}"; do
  [ -d "$S" ] || continue
  NAME=$(basename "$S")
  TS=$(stat -c '%y' "$S" 2>/dev/null | cut -d'.' -f1)
  SIZE=$(du -sh "$S" 2>/dev/null | awk '{print $1}')
  MARK=""
  [ -n "$LATEST" ] && [ "$(readlink -f "$S")" = "$LATEST" ] && MARK="*"
  printf '%-4s %-29s %-19s %-6s %-4s\n' "$i)" "$NAME" "$TS" "$SIZE" "$MARK"
  i=$((i+1))
done

echo
echo "Latest -> ${LATEST:-not set}"
echo "Total used: $(du -sh "$BASE" | awk '{print $1}')"
