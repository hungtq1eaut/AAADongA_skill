#!/usr/bin/env bash
set -euo pipefail
BASE="/data/snapshots"
[ -d "$BASE" ] || { echo "No snapshots dir: $BASE"; exit 1; }

mapfile -t SNAPS < <(ls -1dt "$BASE"/moodle_* 2>/dev/null || true)
[ "${#SNAPS[@]}" -gt 0 ] || { echo "No snapshots to delete."; exit 0; }

choose() {
  local arg="${1:-}" target=""
  if [[ -z "$arg" ]]; then
    echo "Usage: $0 <index|snapshot-name>"; echo; /root/snap_list.sh; exit 1
  fi
  if [[ "$arg" =~ ^[0-9]+$ ]]; then
    local idx="$((arg-1))"
    [[ $idx -ge 0 && $idx -lt ${#SNAPS[@]} ]] || { echo "Invalid index."; exit 1; }
    target="${SNAPS[$idx]}"
  else
    [[ -d "$BASE/$arg" ]] && target="$BASE/$arg" || { [[ -d "$arg" ]] && target="$arg"; }
  fi
  [[ -n "$target" && -d "$target" ]] || { echo "Snapshot not found."; exit 1; }
  echo "$target"
}

TARGET="$(choose "${1:-}")"
echo "About to DELETE snapshot: $TARGET"
read -r -p "Confirm? [y/N] " ok
[[ "$ok" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }

rm -rf --one-file-system -- "$TARGET"

NEW_LATEST="$(ls -1dt "$BASE"/snapshot-* 2>/dev/null | head -n1 || true)"
[[ -n "$NEW_LATEST" ]] && ln -sfn "$NEW_LATEST" "$BASE/latest" || rm -f "$BASE/latest"
echo "Deleted. Current latest -> $(readlink -f "$BASE/latest" 2>/dev/null || echo 'none')"
