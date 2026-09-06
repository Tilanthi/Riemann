"""machine2 CYCLE 33 -- GRADER v2.  ONE LINE differs from the frozen v1, by DERIVATION.

v1 returned P1 FALSIFIED.  The falsification is v1's, not the object's: the pre-registration
says the slope for the k-term truncation err_k is k+1 (targets 2,3,4,5,6), and v1 loops with a
0-BASED k and tests slope == k+1, i.e. targets 1,2,3,4,5.  Off by one.  The single changed
expression is `(k + 1)` -> `(k + 2)` in the P1 block, derived from the prereg text, NOT widened
until it passes; the +-0.10 band, the four eps, the noise floor and P2/P3 are byte-identical.

BECAUSE THIS FIX WAS MADE AFTER SEEING THE DATA, v2's P1 reading is REPORTED, NOT GRADED.
The graded outcome of record is v1's: P1 FALSIFIED.

Original v1 header follows.

machine2 CYCLE 33 -- FROZEN GRADER for machine2-c33-PREREG-fold-expansion-out-of-sample.md.

Hashed and committed BEFORE it is run.  It computes u^2 at the four pre-registered eps by a
root find on xi_D(1/2+u) -- an independent code path: no Cauchy extraction, no finite
difference, no series solve, no least squares, no header -- and grades P1, P2, P3 exactly as
written in the pre-registration.

Convention (fixed by measurement, prereg section 2):
    u^2 = a e + b e^2 + a3 e^3 + a4 e^4 + a5 e^5 + O(e^6),   e = D* - D,   zeros at s = 1/2 +- u.
"""
import json
import sys

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2  # noqa: E402

DSTAR_STR = "0.141733239663887191395415685084185024"
EPS = ["0.005", "0.01", "0.02", "0.04"]        # frozen graded set
NOISE_FLOOR = mp.mpf("1e-25")
DPS = 60
GUARD = 20


def u2_true(eps):
    """Root find for the real zero s = 1/2 + u of xi_D at D = D* - eps.  Independent path."""
    with mp.workdps(DPS + 20):
        D = mp.mpf(DSTAR_STR) - mp.mpf(eps)
        Z = Zeta2(D, dps=DPS, guard=GUARD)
        half = mp.mpf(1) / 2
        f = lambda t: mp.re(Z.xi(half + t))
        a0 = mp.mpf("2.645521411811662868")     # start only; not used in the graded value
        u = mp.findroot(f, mp.sqrt(a0 * mp.mpf(eps)), tol=mp.mpf(10) ** (-2 * DPS))
        return u ** 2, abs(f(u)), abs(mp.diff(f, u))


def main(coeffs_json):
    with open(coeffs_json) as fh:
        C = json.load(fh)
    fine = C[-1]["coeffs"]
    mp.mp.dps = DPS + 20
    c = [mp.mpf(fine[k]) for k in ["a", "b", "a3", "a4", "a5"]]
    print("# coefficients graded against (finest config %s):" % C[-1]["label"])
    for nm, v in zip(["a", "b", "a3", "a4", "a5"], c):
        print(f"#   {nm:>2s} = {mp.nstr(v, 30)}")

    rows = []
    for e_s in EPS:
        e = mp.mpf(e_s)
        u2, resid, deriv = u2_true(e_s)
        errs = []
        acc = mp.mpf(0)
        for k in range(5):
            acc += c[k] * e ** (k + 1)
            errs.append(abs(u2 - acc))
        rows.append(dict(eps=e, u2=u2, resid=resid, deriv=deriv, errs=errs))
        print(f"\neps = {e_s}   u2_true = {mp.nstr(u2, 30)}   |xi(u)| = {mp.nstr(resid,4)}"
              f"   |xi'(u)| = {mp.nstr(deriv,6)}")
        for k, ee in enumerate(errs):
            print(f"    err_{k+1} = {mp.nstr(ee, 8)}")

    # ---- P1: fitted order
    print("\n## P1  slope of log10 err_k vs log10 eps  (target k+1 +- 0.10)")
    p1 = True
    for k in range(5):
        pts = [(mp.log10(r["eps"]), mp.log10(r["errs"][k])) for r in rows
               if r["errs"][k] > NOISE_FLOOR]
        n = len(pts)
        dropped = len(rows) - n
        if n < 2:
            print(f"   k={k+1}: only {n} admissible points -- NOT GRADED")
            continue
        mx = sum(p[0] for p in pts) / n
        my = sum(p[1] for p in pts) / n
        slope = (sum((p[0] - mx) * (p[1] - my) for p in pts)
                 / sum((p[0] - mx) ** 2 for p in pts))
        ok = abs(slope - (k + 2)) <= mp.mpf("0.10")
        p1 &= bool(ok)
        print(f"   k={k+1}: slope = {mp.nstr(slope,6)}   target {k+2}   "
              f"{'PASS' if ok else 'FAIL'}   (points {n}, dropped {dropped})")
    print(f"   => P1 {'HELD' if p1 else 'FALSIFIED'}")

    # ---- P2: magnitude at eps = 0.02
    r02 = [r for r in rows if r["eps"] == mp.mpf("0.02")][0]
    e5, e3 = r02["errs"][4], r02["errs"][2]
    ok5 = mp.mpf("1e-10") <= e5 <= mp.mpf("1e-8")
    ok3 = mp.mpf("1e-6") <= e3 <= mp.mpf("1e-5")
    print(f"\n## P2  at eps=0.02: err_5 = {mp.nstr(e5,6)} in [1e-10,1e-8]? {ok5};"
          f"  err_3 = {mp.nstr(e3,6)} in [1e-6,1e-5]? {ok3}")
    print(f"   implied |a6| ~ err_5/eps^6 = {mp.nstr(e5/mp.mpf('0.02')**6, 6)}")
    print(f"   => P2 {'HELD' if (ok5 and ok3) else 'FALSIFIED'}")

    # ---- P3: usable range at 1e-12, from the fitted power law of each order
    print("\n## P3  eps at which err_k = 1e-12 (from the k-th fitted power law)")
    tgt = mp.mpf("1e-12")
    epsk = {}
    for k in [2, 4]:
        pts = [(mp.log10(r["eps"]), mp.log10(r["errs"][k])) for r in rows
               if r["errs"][k] > NOISE_FLOOR]
        n = len(pts)
        mx = sum(p[0] for p in pts) / n
        my = sum(p[1] for p in pts) / n
        slope = (sum((p[0] - mx) * (p[1] - my) for p in pts)
                 / sum((p[0] - mx) ** 2 for p in pts))
        icpt = my - slope * mx
        epsk[k] = 10 ** ((mp.log10(tgt) - icpt) / slope)
        print(f"   order {k+1}: eps_(1e-12) = {mp.nstr(epsk[k], 8)}")
    gain = epsk[4] / epsk[2]
    print(f"   ratio eps_5 / eps_3 = {mp.nstr(gain, 8)}   target >= 3   "
          f"=> P3 {'HELD' if gain >= 3 else 'FALSIFIED'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/workspace/rh/cycle33/c33_fold5.json")
