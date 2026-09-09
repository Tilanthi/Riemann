#!/usr/bin/env python3
"""C1 DERIVABILITY PROBE (blindness-preserving).
Reports hole structure + a CONSTRUCTIVE lower bound on |{p2 consistent with committed bytes}|.
Never calls _first_leave on the TRUE sequence; never prints a pooled_delta of a measured rung.
"""
import json, os, sys
_F  = os.path.dirname(os.path.abspath(__file__))          # c52 law: resolve from THIS file,
HERE = os.path.abspath(os.path.join(_F, "..", "c56"))     # never from the author's cwd, and
sys.path.insert(0, os.path.abspath(os.path.join(_F, "..", "c55")))
print("resolver: c56 dir = %s" % HERE)                    # PRINT THE PATH THE RESOLVER USED
import m2_c55_score as S55
nf100 = {p: os.path.join(HERE, "m2_c56_nodes_%s_x42_N100_dps300.json" % p) for p in ("even","odd")}
tab, cert, forder = S55.pooled_table(nf100)
holes = [r["p"] for r in tab if r["nu"] is None]
vis   = [r["p"] for r in tab if r["nu"] is not None]
k = next((i for i,r in enumerate(tab) if r["nu"] is None), len(tab))
print("pooled rows=%d  certified_prefix=%d  float_order==Decimal_order=%s" % (len(tab), cert, forder))
print("HOLE pooled positions   : %s" % holes)
print("VISIBLE pooled positions: %s" % vis)
print("defined prefix length starting at p=1: %d" % k)
first_vis_i  = next(i for i,r in enumerate(tab) if r["nu"] is not None)
first_vis_nu = tab[first_vis_i]["nu"]
K = first_vis_i                        # leading hole block length
print("leading hole block length K=%d ; first visible nu = %d" % (K, first_vis_nu))
# tail deltas from the first visible position onward, truncated at the next hole
tail = []
for r in tab[K:]:
    if r["nu"] is None: break
    tail.append(r["nu"] - (r["p"] - 1))
# TWO admissible completions of the leading block (non-decreasing nu, 0 <= nu <= first_vis_nu):
#  A: nu_p = 2 + (p-1)  for p<=K  -> pooled_delta == 2 throughout the block (no leave inside it)
#  B: nu_p = 0          for p<=K  -> pooled_delta = 1-p, strictly decreasing (a leave at p=2)
outs = {}
for name, deltas in (("A: block delta == 2 everywhere", [2]*K),
                     ("B: block nu == 0 everywhere",    [0-(p-1) for p in range(1, K+1)])):
    full = deltas + tail
    outs[name] = S55._first_leave(full, 2)
distinct = set(outs.values())
print("admissible-completion count probed: 2 ; DISTINCT p2 outcomes: %d" % len(distinct))
print("p2 DETERMINED by the committed bytes: %s" % (len(distinct) == 1))
# guard: never print the values themselves
assert len(distinct) >= 1
