#!/usr/bin/env bash
# The artefacts cycle 55 must NOT yet have when the prereg is pushed.  Run BEFORE the launch.
# A pre-launch tool correctly FAILS after publication -- that is the point (c51).
cd "$(dirname "$0")"
miss=0; present=0
for f in m2_c55_spec_*.json m2_c55_nodes_*.json m2_c55_gpred_*.json m2_c55_scores.json \
         m2_c55_kat_na.json m2_c55_fixture_d.json m2_c55_repro_gate.json m2_c55_regression.json; do
  if [ -e "$f" ]; then echo "PRESENT (gate FAILS pre-launch): $f"; present=$((present+1));
  else miss=$((miss+1)); fi
done
echo "absent patterns: $miss   present: $present"
[ "$present" -eq 0 ] && echo "PRE-LAUNCH ABSENCE: OK (nothing of the run exists yet)" || echo "PRE-LAUNCH ABSENCE: FAIL"
