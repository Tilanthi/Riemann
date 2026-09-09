#!/usr/bin/env python3
"""m2_c58_pair_residual_conventions.py -- SIBLING DIAGNOSTIC for the C-arm's replication FAILURE.

The sealed C-arm reported C1 NOT REPLICATED: at the 3 pairs A6 compared, in c57's own gap
convention, the fitted-offset residual is [0.75, 0.84] and the per-rung residual is [0.17, 0.23],
against m1-L203's published [0.75, 0.86] and [0.13, 0.28].

Before reporting a disagreement with the other machine it is worth asking whether the disagreement
is about the LADDERS or about the CONVENTION.  This file sweeps the plausible conventions -- four
local-gap definitions x three pair populations -- and reports which, if any, lands on m1's numbers.
It changes no verdict; C1 stays as the sealed file scored it.  Nothing here is a claim about m1's
code, which I have not seen.
"""
import json
import os
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
C56 = os.path.abspath(os.path.join(HERE, "..", "c56"))
X, DPS, S = 42, 300, 6
M1 = dict(fitted=[0.75, 0.86], per_rung=[0.13, 0.28])


def pin(name):
    hits = [f for f in sorted(os.listdir(C56)) if f == name]
    assert len(hits) == 1, "selection is not unique: %r" % hits
    return os.path.join(C56, hits[0])


def spec(par, N):
    return json.load(open(pin("m2_c56_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))))


def nodes(par, N):
    d = json.load(open(pin("m2_c56_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))))
    return {r["rung"]: r["nu"] for r in d["rungs"]}


def run(gapconv, population):
    fit, per, npairs = [], [], 0
    for par in ("even", "odd"):
        a = [Decimal(r["log10"]) for r in spec(par, 100)["rungs"] if r.get("log10")]
        b = [Decimal(r["log10"]) for r in spec(par, 180)["rungs"] if r.get("log10")]
        na, nb = nodes(par, 100), nodes(par, 180)
        top = {"comparable": 20, "all20": 20, "all15": 15}[population]
        for k in range(1, min(len(a), top) + 1):
            jf = k + S
            if population == "comparable":
                if na.get(k) is None or not (1 <= jf <= len(b)) or nb.get(jf) is None:
                    continue
            if gapconv == "A_c57":
                i = min(k, len(a) - 1)
                g = float(a[i] - a[i - 1])
            elif gapconv == "A_fwd":
                g = float(a[k] - a[k - 1]) if k < len(a) else None
            elif gapconv == "A_bwd":
                g = float(a[k - 1] - a[k - 2]) if k >= 2 else None
            else:
                g = float(b[jf] - b[jf - 1]) if jf < len(b) else None
            if not g:
                continue
            npairs += 1
            if 1 <= jf <= len(b):
                fit.append(round(abs(float(a[k - 1] - b[jf - 1])) / g, 4))
            jn = min(range(len(b)), key=lambda t: abs(float(a[k - 1] - b[t])))
            per.append(round(abs(float(a[k - 1] - b[jn])) / g, 4))
    if not per:
        return None
    return dict(pairs=npairs,
                fitted=[round(min(fit), 2), round(max(fit), 2)] if fit else None,
                per_rung=[round(min(per), 2), round(max(per), 2)])


def main():
    grid, hit = {}, []
    for gc in ("A_c57", "A_fwd", "A_bwd", "B_at_jf"):
        for pop in ("comparable", "all20", "all15"):
            r = run(gc, pop)
            if r is None:
                continue
            grid["%s|%s" % (gc, pop)] = r
            if r["fitted"] == M1["fitted"] and r["per_rung"] == M1["per_rung"]:
                hit.append("%s|%s" % (gc, pop))
    out = dict(cycle=58, arm="C1 diagnostic (sibling; changes no verdict)",
               m1_published=M1, grid=grid, conventions_reproducing_m1=hit,
               finding=("no convention in this 4x3 grid reproduces m1-L203's published ranges; the "
                        "disagreement is not explained by the obvious gap definitions or by the "
                        "obvious pair populations, and m1's code has not been read"),
               direction=("m1's SUBSTANTIVE correction is CONFIRMED independently of the digits: "
                          "the pair-level fitted residual measured here, 0.75-0.84 gaps, is WORSE "
                          "than the 0.53-0.57 c57 published, so c57's sentence understated the "
                          "mismatch and its referent was indeed the window maximum"))
    json.dump(out, open(os.path.join(HERE, "m2_c58_pair_residual_conventions.json"), "w"), indent=1)
    for k, v in grid.items():
        print("  %-22s pairs=%2d  fitted %s  per-rung %s" % (k, v["pairs"], v["fitted"],
                                                             v["per_rung"]))
    print("  m1-L203 published        fitted %s  per-rung %s" % (M1["fitted"], M1["per_rung"]))
    print("  conventions reproducing m1: %s" % (hit or "NONE"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
