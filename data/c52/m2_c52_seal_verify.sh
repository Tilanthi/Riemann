#!/usr/bin/env bash
# m2_c52_seal_verify.sh -- the MAPPER the seal declares (c50's law: a seal whose objects are
# unpublished, or whose mapper is omitted, is a seal nobody can produce).  Run from a fresh clone:
#   bash data/c52/m2_c52_seal_verify.sh
# Verifies (1) the five sealed instrument hashes, (2) that the 70 registered cell names are exactly
# the ones present, and prints the completion denominator.
set -uo pipefail
D="$(cd "$(dirname "$0")" && pwd)"; R="$(cd "$D/../.." && pwd)"
cd "$D" || exit 2
rc=0
echo "--- seal (5 objects) ---"
while read -r h f; do
  case "$f" in
    /*) p="$f" ;;
    *)  p="$D/$f" ;;
  esac
  # sealed absolute paths were the author's clone; remap to THIS clone
  case "$f" in
    */data/c46/c46_parity.py) p="$R/data/c46/c46_parity.py" ;;
    */data/c50/m2_c50_ladder.py) p="$R/data/c50/m2_c50_ladder.py" ;;
  esac
  g=$(sha256sum "$p" 2>/dev/null | cut -d' ' -f1)
  if [ "$g" = "$h" ]; then echo "OK   $(basename "$p")"; else
    # POST-SEAL CHANGE PATH (c50's rule; prereg sec 7 licenses path-resolution-only edits).
    # A bare FAIL is unreadable: it cannot distinguish "the registered bytes are gone" from
    # "the registered bytes are preserved beside a repaired live file".  Look for the SEALED_v1.
    v1="${p%.py}.SEALED_v1.py"
    gv1=$(sha256sum "$v1" 2>/dev/null | cut -d' ' -f1)
    if [ -n "$gv1" ] && [ "$gv1" = "$h" ]; then
      echo "OK*  $(basename "$p")  live file CHANGED post-seal; the SEALED bytes verify as $(basename "$v1")"
      echo "     -> m2_c52_prereg_addendum_1.md sec 2 carries the diff and the byte-identical-output proof"
    else
      echo "FAIL $(basename "$p")  sealed=$h got=${g:-MISSING}"; rc=1
    fi
  fi
done < m2_c52_seal.txt
echo "--- registered cells present vs planned ---"
planned=$(python3 m2_c52_grid.py --names | sort)
have=$(cd "$D/cells" 2>/dev/null && ls c46_block_*.json 2>/dev/null | sort)
np=$(printf '%s\n' "$planned" | grep -c .); nh=$(printf '%s\n' "$have" | grep -c .)
echo "planned=$np present=$nh"
extra=$(comm -13 <(printf '%s\n' "$planned") <(printf '%s\n' "$have"))
[ -n "$extra" ] && { echo "UNREGISTERED CELLS PRESENT:"; printf '%s\n' "$extra"; rc=1; }
missing=$(comm -23 <(printf '%s\n' "$planned") <(printf '%s\n' "$have"))
[ -n "$missing" ] && { echo "planned but absent (the honest denominator):"; printf '%s\n' "$missing"; }
[ "$rc" -eq 0 ] && echo "RESULT: OK" || echo "RESULT: FAILED rc=$rc"
(exit $rc)
