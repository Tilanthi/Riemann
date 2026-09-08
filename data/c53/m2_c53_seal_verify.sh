#!/bin/sh
# cycle 53 seal mapper -- SHIPS IN THE SAME PUSH AS THE SEAL (c50 named a mapper and omitted it).
# Verifies every sealed object and PRINTS THE PATH IT RESOLVED (c52's portability law: a green that
# read the author's own tree measures nothing).
HERE=$(cd "$(dirname "$0")" && pwd)
echo "resolver: HERE=$HERE"
fails=0
while read want path; do
  [ -z "$want" ] && continue
  full="$HERE/$path"
  echo "  reading: $full"
  got=$(sha256sum "$full" 2>/dev/null | cut -d' ' -f1)
  if [ "$got" = "$want" ]; then echo "    OK   $path"; else echo "    FAIL $path (want $want got ${got:-MISSING})"; fails=$((fails+1)); fi
done <<INNER
$(grep -v '^#' "$HERE/m2_c53_seal.txt")
INNER
echo "seal fails: $fails"
[ "$fails" -eq 0 ]
