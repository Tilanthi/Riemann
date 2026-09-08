#!/usr/bin/env python3
"""m2_c50_p0_gate.py -- prereg P0: every new block cell's lambda_1 must reproduce the PUBLISHED
c46 run_cell lambda_min to >= 30 s.f., and the k=5 calibration cells must reproduce the published
k=3 ladder (6 values).  A block-inverse-iteration Ritz value and a single-vector inverse-iteration
value are different computations of the same eigenvalue, so agreement DEPTH is measured, not
equality asserted (c43: an agreement depth is a reading of the narrower party's print width --
both sides here are printed at 40 s.f., so 40 is this comparison's ceiling and is reported as
such, never as "identical")."""
import json, os, sys
from mpmath import mp, mpf

mp.dps = 80
HERE = os.path.dirname(os.path.abspath(__file__))
def _find_dir(name):
    """m1-L191 finding (c): every c49 script hardcoded an absolute clone path, so a counterparty's
    checkout had to be patched to run it.  Resolve RELATIVE to this file instead, trying the cycle
    working-tree layout first and the committed data/c50 layout second, and SAY which one was used."""
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(here, "data", name), os.path.join(here, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s (tried ./data/%s and ../%s)" % (name, here, name, name))


C46 = _find_dir("c46")          # the PUBLISHED c46 run_cell cells the gate compares against
# and the NEW block cells, which live beside this script once committed (data/c50) and in the c46
# working copy while the cycle runs.  v1 of this file looked for them in C46 only: correct in the
# working tree, WRONG in a fresh clone -- and the fresh-clone verification is what caught it.
# See m2_c50_prereg_addendum_2.md.
def _find_cells():
    for cand in (HERE, C46):
        import glob as _g
        if _g.glob(os.path.join(cand, "c46_block_*_k5.json")):
            return cand
    return HERE


CELLS = _find_cells()
CEIL = 40          # both sides are stored via mp.nstr(...,40); the depth cannot exceed this


def depth(a, b):
    """continuous agreement depth in s.f. of two positive mpf values."""
    if a == b:
        return mpf(CEIL)
    return min(mpf(CEIL), -mp.log(abs(a - b) / abs(a), 10))


def main():
    rows, fails = [], 0
    cells = [("13", 100, 150, 5), ("5", 100, 150, 5), ("19", 100, 300, 3), ("13", 180, 150, 3)]
    for xs, N, dps, k in cells:
        for par in ("even", "odd"):
            fb = os.path.join(CELLS, "c46_block_%s_x%s_N%d_dps%d_g9_it16_k%d.json" % (par, xs, N, dps, k))
            fc = os.path.join(C46, "c46_%s_x%s_N%d_dps%d_g9_it16.json" % (par, xs, N, dps))
            if not os.path.exists(fb):
                print("  MISSING %s" % os.path.basename(fb)); fails += 1; continue
            lb = mpf(json.load(open(fb))["ritz"][0]["lam"])
            lc = mpf(json.load(open(fc))["lambda_min"])
            d = depth(lb, lc)
            ok = d >= 30
            fails += (0 if ok else 1)
            print("  P0 x=%-3s N=%-3d %-4s block lam1 vs published lambda_min : depth %s s.f. %s"
                  % (xs, N, par, mp.nstr(d, 4), "PASS" if ok else "FAIL"))
            rows.append(dict(x=xs, N=N, parity=par, depth=mp.nstr(d, 6), pass_=bool(ok)))
    # k=5 vs published k=3 ladder
    for par in ("even", "odd"):
        f5 = os.path.join(CELLS, "c46_block_%s_x13_N100_dps150_g9_it16_k5.json" % par)
        f3 = os.path.join(C46, "c46_block_%s_x13_N100_dps150_g9_it16_k3.json" % par)
        if not os.path.exists(f5):
            print("  MISSING %s" % os.path.basename(f5)); fails += 1; continue
        a = json.load(open(f5))["ritz"]; b = json.load(open(f3))["ritz"]
        ds = [depth(mpf(a[i]["lam"]), mpf(b[i]["lam"])) for i in range(3)]
        ok = all(d >= 30 for d in ds)
        fails += (0 if ok else 1)
        print("  P0 k=5 vs PUBLISHED k=3 ladder, %-4s            : depths %s  %s"
              % (par, [mp.nstr(d, 4) for d in ds], "PASS" if ok else "FAIL"))
        rows.append(dict(x="13", N=100, parity=par, kind="k5_vs_k3",
                         depth=[mp.nstr(d, 6) for d in ds], pass_=bool(ok)))
    print("  (published cells from %s ; new block cells from %s)" % (C46, CELLS))
    print("P0 GATE: %d fail(s) -- ceiling %d s.f. (both sides stored at 40 s.f.)" % (fails, CEIL))
    json.dump(rows, open(os.path.join(HERE, "m2_c50_p0_gate.json"), "w"), indent=1)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
