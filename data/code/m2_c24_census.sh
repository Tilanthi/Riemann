#!/bin/bash
# cycle24 Object A / V1 -- enumerate every artefact carrying a number produced by the
# m2_u_instrument evaluator (single-panel Gauss-Legendre u_i / Gram / K / lambda path).
# Fingerprint = distinctive digit strings that ONLY this evaluator emits.
# Roots are ls'd in census_roots.txt before any grep is believed.

PAT='1\.1761206927|4\.24962738|5\.8452981|6\.6952522|1145\.4|242\.63|7\.6212|7\.24102|7\.241e|=4\.77|\|dK\|max=4\.77|1\.953e-37|1\.672e-37|7\.586e-39|1\.926e-37|1\.454e-35|8\.242384|1\.17105801592|6\.9929e-6|3\.3877e-6|1\.09e-41|9\.37 ?%|7\.13 ?%|48\.3 ?%|5\.01e-8|1\.43e-10|3\.37e-6|7\.62e-9|4\.4485|1\.4182514'

ROOTS="/shared/rh-exchange-repo /shared/progress /shared/rh-drafts /shared/rh-briefs /shared/rh-discovery /shared/claims /shared/kb /shared/pa /shared/beast-outbox /workspace/continuity /workspace/rh /workspace/MEMORY.md /shared/deliverables /shared/memory /shared/reports /shared/adjudications /shared/predictions"

for r in $ROOTS; do
  if [ ! -e "$r" ]; then echo "ROOT-ABSENT $r"; continue; fi
  n=$(find "$r" -type f 2>/dev/null | wc -l)
  h=$(grep -rlE "$PAT" "$r" --exclude-dir=.git --binary-files=without-match 2>/dev/null | wc -l)
  echo "ROOT $r files=$n hits=$h"
done
echo "----- HIT LIST -----"
for r in $ROOTS; do
  [ -e "$r" ] || continue
  grep -rlE "$PAT" "$r" --exclude-dir=.git --binary-files=without-match 2>/dev/null
done | sort -u
