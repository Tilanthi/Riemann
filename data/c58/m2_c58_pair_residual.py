#!/usr/bin/env python3
"""m2_c58_pair_residual.py -- m1's L203 PRECISION NOTE 1, ADOPTED BY RE-MEASUREMENT.

c57's letter said: "the matched eigenvalue residual is 0.53-0.57 local gaps, so at x=42 the best
available match is still half a rung wide."  m1-L203 sec 3 note 1 says that range is the MAX over the
20-rung drift window, not the residual at the pairs A6 actually compared, and that the pair-level
numbers are 0.75-0.86 gaps under the FITTED offset and 0.13-0.28 gaps at the PER-RUNG nearest match.

A REPLICATION, NOT A PREDICTION.  m1's numbers were read before this file was written, so nothing
here is registered as a blind prediction; it is scored PASS/FAIL as a replication and kept OUT of the
Brier.  What it settles is whether c57's published sentence needs an erratum and in which direction.

CONVENTION, declared: identical to c57's drift census -- local gap at 1-based rung k of the N=100
ladder is g_k = a[min(k, n-1)] - a[min(k, n-1) - 1] on the sorted log10 list, and the residual is
|a_k - b_j| / g_k.  Using a DIFFERENT gap convention would produce a different number and would not
be a replication.  PINNING: every (x, N, parity) slot must have exactly one spectrum (trap #177).
"""
import json
import os
import sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, ".."))
C56 = os.path.join(DATA, "c56")
X, N100, N180, DPS = 42, 100, 180, 300
FITTED_S = 6                       # c57's fitted offset at x=42, both parities
M1_FITTED_RANGE = (0.75, 0.86)     # m1-L203 sec3 note 1, read before writing this file
M1_PERRUNG_RANGE = (0.13, 0.28)


def pinned(name):
    hits = [f for f in sorted(os.listdir(C56)) if f == name]
    assert len(hits) == 1, "selection is not unique for %s: %r" % (name, hits)
    return os.path.join(C56, hits[0])


def ladder(par, N):
    d = json.load(open(pinned("m2_c56_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))))
    return [Decimal(r["log10"]) for r in d["rungs"] if r.get("log10")]


def nus(par, N):
    d = json.load(open(pinned("m2_c56_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))))
    return {r["rung"]: r["nu"] for r in d["rungs"]}


def gap(a, k):
    i = min(k, len(a) - 1)
    return float(a[i] - a[i - 1])


def main():
    rows = []
    for par in ("even", "odd"):
        a, b = ladder(par, N100), ladder(par, N180)
        na, nb = nus(par, N100), nus(par, N180)
        for k in range(1, min(len(a), 20) + 1):
            ka = na.get(k)
            if ka is None:
                continue
            jf = k + FITTED_S
            fitted = None
            if 1 <= jf <= len(b) and nb.get(jf) is not None:
                fitted = dict(j=jf, nu_a=ka, nu_b=nb[jf],
                              residual_gaps=round(abs(float(a[k - 1] - b[jf - 1])) / gap(a, k), 4))
            jn = min(range(len(b)), key=lambda t: abs(float(a[k - 1] - b[t]))) + 1
            perrung = dict(j=jn, nu_a=ka, nu_b=nb.get(jn),
                           residual_gaps=round(abs(float(a[k - 1] - b[jn - 1])) / gap(a, k), 4))
            rows.append(dict(parity=par, rung=k, fitted=fitted, per_rung=perrung))

    comparable = [r for r in rows if r["fitted"] is not None]
    fit_res = [r["fitted"]["residual_gaps"] for r in comparable]
    pr_res = [r["per_rung"]["residual_gaps"] for r in comparable]

    def within(vals, lo, hi):
        return bool(vals) and round(min(vals), 2) == lo and round(max(vals), 2) == hi

    c1_fitted = within(fit_res, *M1_FITTED_RANGE)
    c1_perrung = within(pr_res, *M1_PERRUNG_RANGE)

    # the c57 sentence's own referent: the window MAX over 20 rungs, from the committed census
    census = json.load(open(os.path.join(DATA, "c57", "m2_c57_offset_drift_census.json")))

    out = dict(cycle=58, arm="C1", kind="REPLICATION (not a blind prediction; excluded from Brier)",
               window=X, fitted_offset=FITTED_S, convention="c57 drift-census local gap",
               comparable_pairs=len(comparable), rows=rows,
               fitted_residual_gaps=dict(min=(min(fit_res) if fit_res else None),
                                         max=(max(fit_res) if fit_res else None), all=fit_res),
               per_rung_residual_gaps=dict(min=(min(pr_res) if pr_res else None),
                                           max=(max(pr_res) if pr_res else None), all=pr_res),
               m1_fitted_range=list(M1_FITTED_RANGE), m1_per_rung_range=list(M1_PERRUNG_RANGE),
               C1_fitted_replicates=c1_fitted, C1_per_rung_replicates=c1_perrung,
               C1_verdict=("REPLICATED" if (c1_fitted and c1_perrung) else "NOT REPLICATED"),
               c57_published_sentence=("the matched eigenvalue residual is 0.53-0.57 local gaps "
                                       "-- referent to be settled by this file"),
               c57_census_present=bool(census),
               scope="Eigenvalue ladders only. No node cell written, no model scored.")
    json.dump(out, open(os.path.join(HERE, "m2_c58_pair_residual.json"), "w"), indent=1)
    print("comparable pairs: %d" % len(comparable))
    print("  fitted   residual gaps: min %s max %s   (m1: %s)  replicates=%s"
          % (out["fitted_residual_gaps"]["min"], out["fitted_residual_gaps"]["max"],
             M1_FITTED_RANGE, c1_fitted))
    print("  per-rung residual gaps: min %s max %s   (m1: %s)  replicates=%s"
          % (out["per_rung_residual_gaps"]["min"], out["per_rung_residual_gaps"]["max"],
             M1_PERRUNG_RANGE, c1_perrung))
    print("C1: %s" % out["C1_verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
