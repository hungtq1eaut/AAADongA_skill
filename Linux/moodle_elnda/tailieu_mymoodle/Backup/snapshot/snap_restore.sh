#!/usr/bin/env bash
set -euo pipefail
BASE="/data/snapshots"
[ -d "$BASE" ] || { echo "No snapshots dir: $BASE"; exit 1; }

mapfile -t SNAPS < <(ls -1dt "$BASE"/snapshot-* 2>/dev/null || true)
[ "${#SNAPS[@]}" -gt 0 ] || { echo "No snapshots available."; exit 1; }

choose() {
  local arg="${1:-}" src=""
  if [[ -z "$arg" ]]; then
    echo "Usage: $0 <index|snapshot-name>"; echo; /root/snap_list.sh; exit 1
  fi
  if [[ "$arg" =~ ^[0-9]+$ ]]; then
    local idx="$((arg-1))"
    [[ $idx -ge 0 && $idx -lt ${#SNAPS[@]} ]] || { echo "Invalid index."; exit 1; }
    src="${SNAPS[$idx]}"
  else
    [[ -d "$BASE/$arg" ]] && src="$BASE/$arg" || { [[ -d "$arg" ]] && src="$arg"; }
  fi
  [[ -n "$src" && -d "$src" ]] || { echo "Snapshot not found."; exit 1; }
  echo "$src"
}

SRC="$(choose "${1:-}")"
echo "### WARNING ###"
echo "This will restore system files FROM:"
echo "  $SRC"
echo "It will NOT touch /data or /data2t."
read -r -p "Proceed and reboot afterwards? [y/N] " ok
[[ "$ok" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 1; }

# dừng dịch vụ nặng (best-effort)
systemctl stop nginx 2>/dev/null || true
systemctl stop php8.1-fpm 2>/dev/null || true
systemctl stop php8.2-fpm 2>/dev/null || true
systemctl stop mariadb 2>/dev/null || true
systemctl stop mysql 2>/dev/null || true

EXC=( "/data/*" "/data2t/*" "/proc/*" "/sys/*" "/dev/*" "/run/*" "/tmp/*" "/mnt/*" "/media/*" "/lost+found" )
rsync -aAXH --numeric-ids --delete \
  $(printf -- '--exclude=%s ' "${EXC[@]}") \
  "$SRC"/ /

command -v update-initramfs >/dev/null && update-initramfs -u || true
command -v update-grub >/dev/null && update-grub || true

echo "Restore done."
read -r -p "Reboot now? [y/N] " rb
[[ "$rb" =~ ^[Yy]$ ]] && reboot || echo "Please reboot manually to finish."
