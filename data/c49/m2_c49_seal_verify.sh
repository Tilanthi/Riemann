#!/usr/bin/env bash
# m2_c49_seal_verify.sh -- check every hash in m2_c49_prereg_seal.txt against COMMITTED bytes.
# The seal was written in a working tree with a different layout, so the mapping is made explicit
# here rather than by editing the sealed file (which is the whole point of a seal).
#   prereg/m2_c49_prereg.md      -> data/c49/m2_c49_prereg.md
#   m2_c49_precision.py          -> data/c49/m2_c49_precision.SEALED_v1.py   (the registered bytes)
#   c48-instrument-unchanged: .. -> data/code/m2_c48_recover_depth.py        (committed in c48)
#   cells220/<name>              -> data/c49/raw/<name>
#   logs/*-220.log               -> the empty file; sha256 of zero bytes is e3b0c442...
# Run from the repo root.  exit 0 = every sealed object verifies.
set -u
S=data/c49/m2_c49_prereg_seal.txt
fail=0
check () { h=$(sha256sum "$2" 2>/dev/null | cut -d' ' -f1)
  if [ "$h" = "$1" ]; then echo "OK   $2"; else echo "FAIL $2 (have ${h:-missing})"; fail=1; fi; }
check "$(grep 'prereg/m2_c49_prereg.md$'   $S | cut -d' ' -f1)" data/c49/m2_c49_prereg.md
check "$(grep ' m2_c49_precision.py$'      $S | cut -d' ' -f1)" data/c49/m2_c49_precision.SEALED_v1.py
check "$(grep 'c48-instrument-unchanged'   $S | cut -d' ' -f1)" data/code/m2_c48_recover_depth.py
grep '  cells220/' $S | while read -r h p; do check "$h" "data/c49/raw/$(basename "$p")"; done
e=$(grep 'logs/odd-220.log' $S | cut -d' ' -f1)
[ "$e" = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" ] \
  && echo "OK   both N=220 logs were the EMPTY file at registration (sha256 of zero bytes)" \
  || { echo "FAIL registered-arm emptiness"; fail=1; }
exit $fail
