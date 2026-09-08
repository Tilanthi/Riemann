#!/bin/sh
# Pre-launch absence proof: every registered cycle-53 output name, searched REPOSITORY-WIDE at the
# pre-push HEAD. Streams kept separate; never merged into one count (c51).
cd "$(dirname "$0")/../.." || exit 1
echo "repo root: $(pwd)   HEAD: $(git rev-parse HEAD)"
present=0; absent=0
for par in even odd; do
  for spec in "13 100 150" "19 100 300" "13 180 150" "19 180 300"; do
    set -- $spec; X=$1; N=$2; D=$3
    for base in "m2_c53_spec_${par}_x${X}_N${N}_dps${D}.json" "m2_c53_nodes_${par}_x${X}_N${N}_dps${D}.json"; do
      if find . -name "$base" -not -path './.git/*' | grep -q .; then echo "PRESENT $base"; present=$((present+1));
      else echo "absent  $base"; absent=$((absent+1)); fi
    done
  done
  for spec in "13 100 150" "19 100 300"; do
    set -- $spec; X=$1; N=$2; D=$3
    base="m2_c51_nodes_${par}_x${X}_N${N}_k12.json"
    if find . -name "$base" -not -path './.git/*' | grep -q .; then echo "PRESENT $base"; present=$((present+1));
    else echo "absent  $base"; absent=$((absent+1)); fi
  done
done
for X in 13 19; do
  for spec in "100 150 13" "100 300 19" "180 150 13" "180 300 19"; do
    set -- $spec
    [ "$3" = "$X" ] || continue
    base="m2_c53_gpred_x${X}_N${1}_dps${2}.json"
    if find . -name "$base" -not -path './.git/*' | grep -q .; then echo "PRESENT $base"; present=$((present+1));
    else echo "absent  $base"; absent=$((absent+1)); fi
  done
done
echo "PRE-LAUNCH ABSENCE: $absent absent, $present present"
