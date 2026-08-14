#!/usr/bin/env bash
set -euo pipefail
BASE="/data/snapshots"
STAMP="${1:-snapshot-$(date +%F-%H%M%S)}"
DEST="$BASE/$STAMP"

mkdir -p "$BASE"

# snapshot mới nhất bất kể tên (bỏ 'latest')
LAST="$(ls -1dt "$BASE"/* 2>/dev/null | grep -v '/latest$' | head -n1 || true)"

echo "==> Creating snapshot at: $DEST"
mkdir -p "$DEST"

EXC=(
  "/data/*" "/data2t/*"
  "/proc/*" "/sys/*" "/dev/*" "/run/*" "/tmp/*"
  "/mnt/*" "/media/*" "/lost+found" "/swapfile"
)

rsync -aAXH --numeric-ids --delete \
  $(printf '%s ' "${EXC[@]/#/--exclude=}") \
  ${LAST:+--link-dest="$LAST"} \
  / "$DEST/"

ln -sfn "$DEST" "$BASE/latest"
echo "==> DONE. Snapshot: $DEST"
