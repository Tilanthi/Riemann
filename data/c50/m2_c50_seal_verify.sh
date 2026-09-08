#!/usr/bin/env bash
# m2_c50_seal_verify.sh -- the mapper the seal's own header declared.  It re-checks every sha256
# line of data/c50/m2_c50_seal.txt against COMMITTED bytes, mapping the cycle working-directory
# paths recorded in the seal onto their committed locations.  c49's rule: never edit a sealed file
# to fix a path -- ship a mapper.  m1's c50 prereg witness had to apply this mapping by hand
# because the script was declared but not pushed; this is that file.
#
# usage:  bash data/c50/m2_c50_seal_verify.sh [REPO_ROOT]        (default: two levels up)
set -u
ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
SEAL="$ROOT/data/c50/m2_c50_seal.txt"
[ -f "$SEAL" ] || { echo "no seal at $SEAL"; exit 2; }

# working-dir path (as written in the seal)              -> committed path
map() {
  case "$1" in
    prereg/m2_c50_prereg.md)      echo "data/c50/m2_c50_prereg.md" ;;
    m2_c50_ladder.py)             echo "data/c50/m2_c50_ladder.SEALED_v1.py" ;;   # v2 beside it
    m2_c50_predict.py)            echo "data/c50/m2_c50_predict.SEALED_v1.py" ;;  # v2 beside it
    m2_c50_*)                     echo "data/c50/$1" ;;
    data/c46/*|data/c42/*|data/code/*) echo "${1#data/}" | sed 's|^|data/|' ;;
    *)                            echo "$1" ;;
  esac
}

ok=0; bad=0; miss=0
while read -r h p; do
  case "$h" in \#*|"") continue ;; esac
  [ -n "${p:-}" ] || continue
  c="$(map "$p")"
  f="$ROOT/$c"
  if [ ! -f "$f" ]; then echo "MISSING  $c   (seal path $p)"; miss=$((miss+1)); continue; fi
  a="$(sha256sum "$f" | cut -d' ' -f1)"
  if [ "$a" = "$h" ]; then ok=$((ok+1)); else echo "MISMATCH $c"; echo "   seal $h"; echo "   file $a"; bad=$((bad+1)); fi
done < <(grep -E '^[0-9a-f]{64} ' "$SEAL")

echo "--- absence lines (pre-launch state): the seal recorded 8 target cells ABSENT before launch;"
echo "    they are necessarily PRESENT now, under data/c50/.  Presence is checked, not absence:"
pres=0; abs=0
for l in $(grep '^absent ' "$SEAL" | awk '{print $2}'); do
  b="$(basename "$l")"
  if [ -f "$ROOT/data/c50/$b" ]; then pres=$((pres+1)); else echo "    NOT PUBLISHED: $b"; abs=$((abs+1)); fi
done
echo "SEAL VERIFY: $ok OK, $bad mismatch, $miss missing; post-run cells published $pres, unpublished $abs"
[ "$bad" -eq 0 ] && [ "$miss" -eq 0 ] && [ "$abs" -eq 0 ]
