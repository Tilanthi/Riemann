"""machine2 CYCLE 34 -- GRADER DRY-RUN ON A SYNTHETIC OBJECT WITH A KNOWN ANSWER.

Three cycles running, my CONTROLS have failed on their own specification more often than my
MEASUREMENTS have failed (m1 heat86 BG4, my c31 G2, my c33 P1 off-by-one).  The registered
remedy is: run the gate once against a synthetic case whose answer you know, BEFORE freezing.
This file is that run, and it executes the SAME code path (m2_c34_refit.run) that grades the
real object -- not a re-implementation of it.

Object:  h(w,e) = (w^2 - A(e)) / (1/4 - w^2),   A(e) = sum_{k=1..7} c_k e^k,  e = centre - D.
Even in w, real coefficients, simple poles at w = +-1/2 -- the same analytic shape as
xi_D(1/2+w), so the same trapezoid aliasing law (2 r_w)^{N_w} applies.
EXACT zero curve in x = w^2:  x(e) = A(e).  So the answer is known to all orders.

TESTS (each has a pre-stated pass condition; a test whose failing world is empty is a
diagnostic, not a test, so the fourth one deliberately breaks something):

  T1 RECOVERY      centre = D*_syn exactly.  x_raw must equal c_1..c_5.
  T2 ALIASING LAW  vary N_w only; the error must fall like (2 r_w)^{N_w}.
  T3 OFFSET        centre = D*_syn + delta with delta KNOWN.  Then
                   (a) etilde must equal delta,  (b) implied D* must equal D*_syn,
                   (c) x_rec must equal c_1..c_5 -- i.e. the self-centring must UNDO a
                       known centre error,  (d) x_raw must be wrong by the sensitivity.
  T4 SENSITIVITY   the free d(coeff)/dD* (series-shift route) must match a real central
                   difference of the whole pipeline re-run at centre +- 1e-25.
  T5 SABOTAGE      inject a NON-centre error (multiply g[1][0] by 1+eps).  The dominance
                   test (implied delta_k = Delta_k / S_k, five numbers that must agree if
                   and only if the difference is a pure centre shift) must SCATTER.
                   Without this test the dominance test could be a tautology.
"""
import sys

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle34")
import m2_c34_refit as F  # noqa: E402
from multiprocessing import Pool  # noqa: E402

DSYN = "0.1417332396638871913954156850841850236231"


def exact():
    """Reference coefficients AT THE CURRENT PRECISION.

    The first draft evaluated these at module-import time, i.e. at mpmath's default
    dps=15, and every T1/T3 error then floored at 7e-17 -- a double-precision BASELINE
    masquerading as an instrument floor.  Caught by the dry run, 2026-09-06.  This is the
    fourth control-with-a-wrong-baseline in four cycles; the remedy worked this time only
    because the control was run against a known answer BEFORE it was used to grade.
    """
    return [mp.mpf(c) for c in F.SynXi.COEFFS]


def go(label, **kw):
    c = dict(F.BASE)
    c.update(kw)
    c["label"] = label
    c["model"] = "syn"
    c["dsyn"] = DSYN
    c.setdefault("centre", DSYN)
    with Pool(8, initializer=F._init, initargs=(c,)) as pool:
        return F.run(c, pool)


def relerr(got, want):
    return abs(got - want) / abs(want)


if __name__ == "__main__":
    mp.mp.dps = 120
    EXACT = exact()
    print("=" * 78)
    print("T1 RECOVERY + T2 ALIASING LAW  (centre = D*_syn exactly)")
    print("   pass: x_raw -> c_1..c_5, and the error follows (2 r_w)^N_w")
    prev = None
    for N in [24, 32, 40, 56]:
        R = go(f"S{N}", N_w=N)
        errs = [relerr(R["x_raw"][i + 1], EXACT[i]) for i in range(5)]
        rerr = [relerr(R["x_rec"][i + 1], EXACT[i]) for i in range(5)]
        pred = (2 * mp.mpf(R["cfg"]["r_w"])) ** N
        line = (f"   N_w={N:3d}  max rel err raw = {mp.nstr(max(errs),4)}   "
                f"rec = {mp.nstr(max(rerr),4)}   (2r)^N = {mp.nstr(pred,4)}   "
                f"g00 = {mp.nstr(R['g00'],4)}   etilde = {mp.nstr(R['et'],4)}")
        if prev is not None:
            dn = N - prev[0]
            fall = max(errs) / prev[1]
            want = (2 * mp.mpf(R["cfg"]["r_w"])) ** dn
            line += f"\n            fall vs previous N_w = {mp.nstr(fall,4)}  (law: {mp.nstr(want,4)})"
        print(line)
        prev = (N, max(errs))
    print()
    print("=" * 78)
    delta = mp.mpf(10) ** (-30)   # a KNOWN centre error, larger than every instrument term
    print(f"T3 OFFSET  (centre = D*_syn + {mp.nstr(delta,3)}, a KNOWN wrong centre)")
    off = mp.nstr(mp.mpf(DSYN) + delta, 60, strip_zeros=False)
    R0 = go("S0", N_w=56)                       # true centre, reference
    R1 = go("S1", N_w=56, centre=off)           # offset centre
    print(f"   etilde            = {mp.nstr(R1['et'], 12)}      (must be {mp.nstr(delta,4)})")
    print(f"   etilde/delta      = {mp.nstr(R1['et']/delta, 12)}   [T3a pass iff -> 1]")
    impl = mp.mpf(off) - R1["et"]
    print(f"   implied D* - D*_syn = {mp.nstr(impl - mp.mpf(DSYN), 6)}   [T3b pass iff ~0]")
    for i, nm in enumerate(F.NAMES):
        print(f"   {nm:>3s}: raw err = {mp.nstr(relerr(R1['x_raw'][i+1], EXACT[i]),4):>10s}   "
              f"REC err = {mp.nstr(relerr(R1['x_rec'][i+1], EXACT[i]),4):>10s}   "
              f"[T3c pass iff rec << raw]")
    print("   T3d  raw shift vs sensitivity prediction:")
    for i, nm in enumerate(F.NAMES):
        got = R1["x_raw"][i + 1] - R0["x_raw"][i + 1]
        # g^{C+delta} = shift_e(g^C, -delta) and sens := -d x/d(shift), so the raw
        # coefficients move by +sens*delta when the centre moves by +delta.  The first
        # draft of this line had the sign the other way and T3d returned ratio -1.0 for
        # four of five coefficients -- the test, not the instrument, was wrong.  Third
        # sign-convention defect in this lane (c33 ERRATUM 17 was the second).
        want = R1["sens"][i + 1] * delta       # centre moved by +delta
        print(f"      {nm:>3s}  measured {mp.nstr(got,8):>16s}   predicted {mp.nstr(want,8):>16s}"
              f"   ratio {mp.nstr(got/want,8)}")
    print()
    print("=" * 78)
    print("T4 SENSITIVITY: free series-shift route vs a real pipeline central difference")
    d = mp.mpf(10) ** (-25)
    Rp = go("S+", N_w=56, centre=mp.nstr(mp.mpf(DSYN) + d, 60, strip_zeros=False))
    Rm = go("S-", N_w=56, centre=mp.nstr(mp.mpf(DSYN) - d, 60, strip_zeros=False))
    for i, nm in enumerate(F.NAMES):
        fd = (Rp["x_raw"][i + 1] - Rm["x_raw"][i + 1]) / (2 * d)
        print(f"   {nm:>3s}  free = {mp.nstr(R0['sens'][i+1], 12):>18s}   "
              f"pipeline FD = {mp.nstr(fd, 12):>18s}   rel diff = "
              f"{mp.nstr(abs(fd - R0['sens'][i+1])/(abs(fd) + mp.mpf(10)**(-90)), 4)}")
    print()
    print("=" * 78)
    print("T5 SABOTAGE: a NON-centre perturbation must make the dominance test SCATTER")
    S = [R0["sens"][i + 1] for i in range(5)]
    # (i) a genuine centre shift, injected in series algebra: must give five equal delta_k
    sh = mp.mpf(10) ** (-40)
    xa = F.series_solve(F.shift_e(R0["g"], R0["et"] + sh), 5)
    dks = [(xa[i + 1] - R0["x_rec"][i + 1]) / (-S[i] * sh) for i in range(5)]
    print("   (i) pure centre shift, implied delta_k / delta (must all be 1.000):")
    print("       " + "  ".join(mp.nstr(v, 8) for v in dks))
    # (ii) a pure instrument perturbation of g[1][0]: must NOT look like a centre shift
    g2 = [list(row) for row in R0["g"]]
    g2[1][0] = g2[1][0] * (1 + mp.mpf(10) ** (-40))
    xb = F.series_solve(g2, 5)
    dk2 = [(xb[i + 1] - R0["x_raw"][i + 1]) / S[i] for i in range(5)]
    print("   (ii) g[1][0] perturbed by 1e-40, implied delta_k (must SCATTER):")
    print("       " + "  ".join(mp.nstr(v, 8) for v in dk2))
    sp = max(abs(v) for v in dk2) / min(abs(v) for v in dk2)
    print(f"       spread max/min = {mp.nstr(sp, 8)}   [T5 pass iff >> 1]")
