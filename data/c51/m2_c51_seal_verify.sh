#!/usr/bin/env bash
# m2_c51_seal_verify.sh -- the mapper the seal declares, shipped IN the push that declares it.
# c50's prereg named a mapper and omitted it (m1 push-hygiene note); c49's law: a seal whose objects
# are unpublished is a seal nobody can produce. Run from anywhere; resolves beside itself.
#
# usage: m2_c51_seal_verify.sh            verify instrument shas against the prereg's seal block
#        m2_c51_seal_verify.sh --absence  re-prove the eight target outputs absent (pre-launch use)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREREG="$HERE/m2_c51_prereg.md"
TARGETS=(m2_c51_nodes_even_x5_N100_k5.json m2_c51_nodes_odd_x5_N100_k5.json \
         m2_c51_nodes_even_x19_N100_k5.json m2_c51_nodes_odd_x19_N100_k5.json \
         m2_c51_nodes_even_x13_N180_k5.json m2_c51_nodes_odd_x13_N180_k5.json \
         m2_c51_nodes_even_x13_N100_k7.json m2_c51_nodes_odd_x13_N100_k7.json)

if [ "${1:-}" = "--absence" ]; then
  root="$(cd "$HERE" && git rev-parse --show-toplevel 2>/dev/null || echo "$HERE")"
  miss=0; found=0
  for t in "${TARGETS[@]}"; do
    n=$(find "$root" -name "$t" -not -path '*/.git/*' | wc -l)
    if [ "$n" -eq 0 ]; then echo "ABSENT  $t"; miss=$((miss+1)); else echo "PRESENT $t ($n)"; found=$((found+1)); fi
  done
  echo "absence: $miss absent / $found present of ${#TARGETS[@]} target outputs (root $root)"
  [ "$found" -eq 0 ] && echo "RESULT: OK — all target outputs absent" || echo "RESULT: FAIL — a target output already exists"
  [ "$found" -eq 0 ]; (exit $?)
  exit $?
fi

ok=0; bad=0
while read -r sha name; do
  [ -z "${sha:-}" ] && continue
  case "$sha" in \#*|"") continue;; esac
  f="$HERE/$name"
  if [ ! -f "$f" ]; then echo "MISSING  $name"; bad=$((bad+1)); continue; fi
  got=$(sha256sum "$f" | awk '{print $1}')
  if [ "$got" = "$sha" ]; then echo "OK       $name"; ok=$((ok+1))
  else echo "MISMATCH $name  sealed=$sha  now=$got"; bad=$((bad+1)); fi
done < <(sed -n '/^INSTRUMENT_SHA256_BEGIN$/,/^INSTRUMENT_SHA256_END$/p' "$PREREG" | grep -E '^[0-9a-f]{64}  ')

echo "seal: $ok OK / $bad mismatched-or-missing"
[ "$bad" -eq 0 ] && echo "RESULT: OK" || echo "RESULT: FAIL"
[ "$bad" -eq 0 ]
