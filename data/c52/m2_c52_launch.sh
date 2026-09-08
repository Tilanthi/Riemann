#!/usr/bin/env bash
# runs the registered grid in tier order with a pool of 8 (cgroup quota is 8 vCPU, measured).
cd "$(dirname "$0")/run/c46" || exit 2
G=../../m2_c52_grid_cmds.tsv
LOG=../../logs
mkdir -p "$LOG"
cut -f3 "$G" | nl -ba -w1 -s$'\t' | while IFS=$'\t' read -r i cmd; do
  printf '%s\t%s\n' "$i" "$cmd"
done | xargs -P 8 -I{} bash -c '
  i=$(printf "%s" "{}" | cut -f1); cmd=$(printf "%s" "{}" | cut -f2-)
  t0=$(date -u +%s)
  python3 c46_parity.py $cmd > "../../logs/cell_$i.out" 2> "../../logs/cell_$i.err"
  echo "$i rc=$? $((`date -u +%s`-t0))s $cmd" >> ../../logs/PROGRESS.txt
'
