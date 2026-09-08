#!/usr/bin/env python3
"""m2_c50_predict.py -- the PREREGISTERED prediction table for cycle 50.

Emits every number that cycle 50's prereg registers, computed from PUBLISHED c46 cells only
(the frozen k=1 lambda_min cells and the two k=3 block cells at x=13, N=100).  Nothing here
reads a cell produced by this cycle; that is the point.  Run before launch, output committed
with the prereg, and the prereg quotes THIS OUTPUT rather than hand arithmetic (c45's lesson:
prose arithmetic is where a registered number gets a digit wrong).

Definitions used throughout cycle 50
------------------------------------
For a fixed (x, N, dps, gl, iters) the two parity blocks give ascending Ritz ladders
    lambda_even[1..k] and lambda_odd[1..k].
POOLED LADDER  = both merged and sorted ascending, each rung labelled by its parity.
    gap_j (dex)  = log10 lambda_pooled[j+1] - log10 lambda_pooled[j]
    d_1   (dex)  = log10 lambda_odd[1]  - log10 lambda_even[1]      (the c46 "parity gap")
    s_1   (dex)  = log10 lambda_even[2] - log10 lambda_even[1]      (the SIMPLICITY gap)
    r_1          = d_1 / s_1                                         (odd rung's position in the
                                                                      even step; 1/2 = half-step)
    q_j          = gap_{j+1} / gap_j                                 (gap-decay ratio)
If the pooled ladder alternates e,o,e,o then gap_1 = d_1, gap_1+gap_2 = s_1, and
    r_1 = 1/(1+q_1)   ALGEBRAICALLY.
=> r_1 > 1/2 is FORCED by q_1 < 1 and carries no information beyond it.  q_1 is the primitive
   quantity and is what this cycle registers.  (Registering r_1 alone would have been a
   corollary dressed as a test -- the c33/c49 defect.)

MODEL A (constant-r / constant-q): q_1 is a constant of the family, equal to its one measured
    value 0.9206566... at (x=13, N=100).  Predicts s_1 = d_1 * (1 + q_1) / 1 ... concretely
    s_1_hat = d_1 / r_1 with r_1 = 1/(1+q_1).
MODEL B (zeros-ladder): each pooled rung costs exactly 2 zeros of the window count
    n = #{0 < gamma <= 2 pi x}, converted by the c45 decay law -ln lambda ~= F(n) := 2 pi^2 n/ln n:
        gap_j_hat = [F(n + 2j) - F(n + 2j - 2)] / ln 10 .
    DISCLOSED AT REGISTRATION: model B is already 5.1 % low in LEVEL at the calibration point
    (predicts gap_1 = 3.7519 dex where 3.9532 is measured).  It is registered for its SHAPE
    (q_1), where it disagrees with A by far more than that: A says gaps shrink at every x,
    B says they GROW at x=5 (q_1 > 1) because F is convex there.  n = 4 is not an asymptotic
    regime (c46), which is exactly why the x=5 cell discriminates.
"""
import json, os, sys
from mpmath import mp, mpf, log, pi

mp.dps = 50
HERE = os.path.dirname(os.path.abspath(__file__))
C46 = os.path.join(HERE, "data", "c46")

# exact zero counts n = #{0 < gamma <= 2 pi x}, MEASURED in c46 (c46_zerocount.out), not recalled
NZERO = {"4p953032424395115": 4, "5": 4, "13": 21, "19": 38}


def F(n):
    n = mpf(n)
    return 2 * pi ** 2 * n / log(n)


def modelB_gaps(n, jmax=4):
    return [(F(n + 2 * j) - F(n + 2 * j - 2)) / log(10) for j in range(1, jmax + 1)]


def published_log10(parity, xs, N, dps):
    fn = os.path.join(C46, "c46_%s_x%s_N%d_dps%d_g9_it16.json" % (parity, xs, N, dps))
    return mpf(json.load(open(fn))["log10"]), fn


def published_block(parity):
    fn = os.path.join(C46, "c46_block_%s_x13_N100_dps150_g9_it16_k3.json" % parity)
    return [mpf(r["log10"]) for r in json.load(open(fn))["ritz"]], fn


def main():
    ns = mp.nstr
    print("== calibration point: x=13, N=100, dps=150, g=9, it=16 (PUBLISHED c46 k=3 block cells)")
    e, fe = published_block("even")
    o, fo = published_block("odd")
    print("   even log10:", [ns(v, 12) for v in e], os.path.basename(fe))
    print("   odd  log10:", [ns(v, 12) for v in o], os.path.basename(fo))
    pooled = sorted([(v, "e") for v in e] + [(v, "o") for v in o])
    order = "".join(p for _, p in pooled)
    gaps = [pooled[i + 1][0] - pooled[i][0] for i in range(len(pooled) - 1)]
    print("   pooled parity order :", order)
    print("   pooled gaps (dex)   :", [ns(g, 6) for g in gaps])
    q_cal = gaps[1] / gaps[0]
    d1_cal = o[0] - e[0]
    s1_cal = e[1] - e[0]
    r1_cal = d1_cal / s1_cal
    print("   d_1 = %s   s_1 = %s   r_1 = %s   q_1 = %s" %
          (ns(d1_cal, 10), ns(s1_cal, 10), ns(r1_cal, 10), ns(q_cal, 10)))
    print("   lambda2/lambda1 (even) = %s   [c46 published 3.91576e7]" % ns(10 ** s1_cal, 10))
    # PRINT-FLOOR TRAP, caught by the analysis instrument's self-test before this file was frozen:
    # nstr(...,5) of the r/q residual renders "0.0" for a NONZERO number.  The exact identity is the
    # subtraction one; the division form is exact only to the working precision.  Print both, wide.
    print("   identity gap_1+gap_2-s_1 (EXACT)      :", ns(gaps[0] + gaps[1] - s1_cal, 5))
    keep = mp.dps
    diffs = []
    for d in (50, 60, 80):
        mp.dps = d                      # parse the STRINGS again at this precision, then divide
        ee, _ = published_block("even")
        oo, _ = published_block("odd")
        diffs.append((d, ns((oo[0] - ee[0]) / (ee[1] - ee[0]) -
                            1 / (1 + (ee[1] - oo[0]) / (oo[0] - ee[0])), 8)))
    mp.dps = keep
    print("   identity r_1-1/(1+q_1) (division form): %s"
          % "  ".join("dps=%d: %s" % t for t in diffs))
    print("     ^ it is ZERO ONLY TO THE WORKING PRECISION and moves with dps: division rounding,")
    print("       not an identity.  The identity is the subtraction one above, which is exact at")
    print("       every precision.  (A print at one precision cannot tell those two apart.)")
    print("   MODEL B at n=21, first 4 gaps:", [ns(g, 6) for g in modelB_gaps(21)])
    print("   MODEL B level error at calibration: %s %% (gap_1)" %
          ns(100 * (modelB_gaps(21)[0] / gaps[0] - 1), 4))

    print()
    print("== REGISTERED point predictions for the four new (x,N) points")
    print("   cell                 n    d_1(published)    A: q_1    A: s_1_hat   B: q_1    B: s_1_hat   B: gap_1_hat")
    rows = [("5", 100, 150), ("13", 180, 150), ("19", 100, 300), ("13", 100, 150)]
    for xs, N, dps in rows:
        n = NZERO[xs]
        le, _ = published_log10("even", xs, N, dps)
        lo, _ = published_log10("odd", xs, N, dps)
        d1 = lo - le
        gB = modelB_gaps(n)
        qA = q_cal
        sA = d1 * (1 + qA)          # s_1 = gap_1 + gap_2 = d_1 (1 + q_1)  under alternation
        qB = gB[1] / gB[0]
        sB = d1 * (1 + qB)
        print("   x=%-5s N=%-4d dps=%-4d %-3d  %s   %s  %s   %s  %s   %s"
              % (xs, N, dps, n, ns(d1, 10), ns(qA, 6), ns(sA, 8), ns(qB, 6), ns(sB, 8), ns(gB[0], 6)))
    print()
    print("   (the last row x=13 N=100 is the calibration point itself, printed as a control:")
    print("    model A reproduces its own s_1 there by construction, model B does not.)")


if __name__ == "__main__":
    main()
