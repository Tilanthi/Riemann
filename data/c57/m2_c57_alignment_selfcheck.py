#!/usr/bin/env python3
"""m2_c57_alignment_selfcheck.py -- THE CONTROL m2_c57_aligned_ncontrol.py DID NOT HAVE.

A6 came back REFUTED at x=42: after aligning by eigenvalue, the three comparable pairs disagree by
roughly a factor of two in node count (20 vs 48, 26 vs 52, 27 vs 57).  Before that is reported as a
fact about the operator, it has to survive the objection that it is a fact about MY ALIGNMENT:

  the offset s was FITTED on the lowest 6 rungs and then APPLIED at rungs 8, 9 and 15.

That is precisely the c56 law -- A CONTROL THAT COMPARES ITEM k OF TWO RUNS IS A CONTROL ONLY IF
ITEM k IS THE SAME OBJECT IN BOTH -- committed a second time, one layer up, by the very program
written to repair it.  A constant offset is an ASSUMPTION about the whole ladder, fitted at one end.

THIS PROGRAM MEASURES IT: for every pair the aligned N-control actually compared, it reports the
eigenvalue residual AT THAT PAIR in units of the local rung gap, and it reports the offset that
would have been chosen if it had been fitted AT THAT HEIGHT instead of at the bottom.
"""
import json, os, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
C56 = os.path.abspath(os.path.join(HERE, "..", "c56"))
print("resolver: c56 dir = %s" % C56)

def spec(par, N):
    return json.load(open(os.path.join(C56, "m2_c56_spec_%s_x42_N%d_dps300.json" % (par, N))))

rows = []
for par in ("even", "odd"):
    a = [Decimal(r["log10"]) for r in spec(par, 100)["rungs"] if r.get("log10")]
    b = [Decimal(r["log10"]) for r in spec(par, 180)["rungs"] if r.get("log10")]
    gap_lo = float(a[1] - a[0])
    for k100 in (8, 9, 15):
        j = k100 + 6                       # the offset the fitted alignment applied
        if j - 1 >= len(b) or k100 - 1 >= len(a):
            continue
        gap_here = float(a[k100] - a[k100 - 1]) if k100 < len(a) else gap_lo
        resid = float(a[k100 - 1] - b[j - 1])
        # what offset WOULD have been chosen if fitted here (single-rung nearest match)?
        best = min(range(len(b)), key=lambda t: abs(float(a[k100 - 1] - b[t])))
        rows.append(dict(parity=par, rung100=k100, rung180_used=j,
                         local_gap_here=round(gap_here, 4),
                         residual_log10=round(resid, 6),
                         residual_in_local_gaps=round(resid / gap_here, 4),
                         nearest_N180_rung=best + 1,
                         offset_if_fitted_here=best + 1 - k100,
                         offset_fitted_at_the_bottom=6))
    # how the offset drifts up the ladder, rung by rung
    drift = []
    for k in range(1, min(len(a), 15) + 1):
        best = min(range(len(b)), key=lambda t: abs(float(a[k - 1] - b[t])))
        drift.append(dict(rung100=k, nearest_N180=best + 1, offset=best + 1 - k,
                          resid_gaps=round(float(a[k - 1] - b[best]) /
                                           float(a[min(k, len(a) - 1)] - a[min(k, len(a) - 1) - 1]), 4)))
    rows.append(dict(parity=par, offset_drift_up_the_ladder=drift))

out = dict(cycle=57, question="is the constant-offset alignment valid at the rungs it compared?",
           finding_under_test="A6 (aligned pairs disagree by ~2x at x=42)",
           rows=rows)
json.dump(out, open(os.path.join(HERE, "m2_c57_alignment_selfcheck.json"), "w"), indent=1)
for r in rows:
    if "offset_drift_up_the_ladder" in r:
        print("\n%s: offset chosen rung-by-rung (fitted at the bottom it was 6)" % r["parity"])
        print("  " + "  ".join("k=%d:s=%d" % (d["rung100"], d["offset"])
                               for d in r["offset_drift_up_the_ladder"]))
    else:
        print("%-5s rung100=%-3d used N180 rung %-3d  resid=%-8.4f gaps=%-8.4f  "
              "nearest N180 rung=%-3d  offset if fitted here=%d"
              % (r["parity"], r["rung100"], r["rung180_used"], r["residual_log10"],
                 r["residual_in_local_gaps"], r["nearest_N180_rung"], r["offset_if_fitted_here"]))
