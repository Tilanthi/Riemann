#!/usr/bin/env bash
# The artefacts cycle 56 must NOT yet have when the prereg is pushed.  Run BEFORE the launch.
# A pre-launch tool correctly FAILS after publication -- that is the point (c51).
#
# 🔴 c56/C4 REPAIR, and the reason this file differs from c55's: c55's version looped over GLOB
# PATTERNS and counted "absent patterns", so when a pattern matched nothing bash left the literal
# pattern in place and it was scored ABSENT -- correct only by accident -- while once files DID
# exist the same counter silently became a FILE count.  Here every pattern is expanded with
# `nullglob`, the count is of FILES, and the denominator (how many patterns were checked) is
# printed separately so a zero can never be read as a pass by default.
#
# 🔴 AND THEN THIS FILE'S FIRST VERSION FAILED ON ITS FIRST RUN, WHICH IS WHY IT IS WORTH READING.
# `nullglob` removes patterns that MATCH NOTHING -- it does nothing to a pattern with NO WILDCARD.
# So `m2_c56_scores.json` and `m2_c56_regression.json`, both absent, were reported PRESENT and the
# gate said FAIL before a single cell had run.  c55's version had `[ -e "$f" ]` and was immune; my
# repair deleted that test because nullglob was "handling it".  ⇒ A REPAIR THAT DROPS A CHECK
# BECAUSE ANOTHER MECHANISM NOW COVERS IT MUST BE RUN AGAINST THE CASE THE DROPPED CHECK COVERED.
# Both are kept below.  This is a C4 false-positive of exactly the audited kind, self-inflicted,
# and it was caught only because the gate was RUN rather than reasoned about.
shopt -s nullglob
cd "$(dirname "$0")"
pats=( 'm2_c56_spec_*.json' 'm2_c56_nodes_*.json' 'm2_c56_gpred_*.json' 'm2_c56_scores.json'
       'm2_c56_storage_law_*.json' 'm2_c56_regression.json' )
present=0
for p in "${pats[@]}"; do
  for f in $p; do [ -e "$f" ] || continue; echo "PRESENT (gate FAILS pre-launch): $f"; present=$((present+1)); done
done
echo "patterns checked: ${#pats[@]}   files present: $present"
if [ "$present" -eq 0 ]; then echo "PRE-LAUNCH ABSENCE: OK (nothing of the run exists yet)"; exit 0
else echo "PRE-LAUNCH ABSENCE: FAIL"; exit 1; fi
