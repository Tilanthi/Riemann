"""cycle24 V5 -- per-basis, per-degree BREAKDOWN GAMMA of the repo u instrument.

For each basis i and degree d, find the smallest gamma on a grid where the single-panel GL
reading departs from the composite ground truth by more than a relative tolerance.
Also reports the per-subinterval error at the top gamma so the mechanism can be named.
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mpmath import mp
import m2_u_instrument as U
from m2_c24_gt_u import u_repo, u_composite, panel_nodes

mp.dps = 50
half = mp.mpf(1) / 2
TOL = mp.mpf("1e-12")

gens = U.load_genomes("s1/M8")
grid = list(range(20, 421, 20))
degs = [7, 8, 9, 10]

res = {}
for i in range(8):
    phi, bumps = U.make_phi(gens[i])
    ivs = U.intervals(bumps)
    # effective (phi-supported) width of each subinterval, sampled
    eff = []
    for (a, b) in ivs:
        n = 200
        cnt = sum(1 for k in range(n + 1) if phi(a + (b - a) * mp.mpf(k) / n) != 0)
        eff.append(float(b - a) * cnt / (n + 1))
    hmax = max(float(b - a) for a, b in ivs)
    effmax = max(eff)
    row = {"hmax": hmax, "effmax": effmax, "nivs": len(ivs), "break": {}}
    for d in degs:
        brk = None
        for g in grid:
            gg = mp.mpf(g)
            ut, _ = u_composite(phi, ivs, gg, ppw=4, deg=4)
            ud = u_repo(phi, ivs, gg, d)
            if abs(ud - ut) > TOL * abs(ut):
                brk = g
                break
        row["break"][d] = brk
        print(f"basis {i} hmax={hmax:.3f} effmax={effmax:.3f} deg={d} first-bad-gamma={brk}", flush=True)
    res[i] = row
json.dump(res, open("breakdown.json", "w"), indent=1)
print(json.dumps({k: v["break"] for k, v in res.items()}, indent=0))
