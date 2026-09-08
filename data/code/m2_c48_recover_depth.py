#!/usr/bin/env python3
"""m2_c48_recover_depth.py -- how many significant figures does a stored cell actually GIVE BACK?

The closing condition on the c47 storage promise is that re-reading a committed cell recovers MORE
THAN 60 s.f., demonstrated on the artefact.  The 60-s.f. print field cannot certify that: it is the
instrument that caused the defect.  So this script measures depth with three instruments, none of
which is that field, and it runs each one against BOTH storages -- the frozen c46 cell (60 s.f.) and
the c48 cell (full working precision) -- so the difference IS the fix.

  D1  STORAGE DEPTH (structural).   Bits actually retained by the file, and the decimal digits they
      are worth.  Old: the file holds 60 s.f. and nothing else exists to read.  New: `_exact` holds
      the run's binary value entire, so the read is bit-exact by construction and the depth question
      moves off the storage layer, which is the whole point.

  D2  REPRODUCIBLE DEPTH (the load-bearing one).  Take an INDEPENDENT run of the same cell at a
      different working precision -- dps=220 against dps=150, one knob moved -- and measure how many
      significant figures the two agree to.  This measures the object, not the print.  Read through
      the frozen 60-s.f. cell the same measurement SATURATES at ~60 by construction; read through the
      c48 cell it does not.  The gap between those two numbers is the defect, on the artefact.

  D3  RIGOROUS BOUND (assembled matrix).  For symmetric M and a computed Ritz pair (lam, v),
      |lam - lam_exact(M)| <= ||Mv - lam v|| / ||v||.  Divided by |lam| this is a lower bound on the
      relative accuracy of the stored eigenvalue AGAINST THE MATRIX THAT WAS BUILT.  It says nothing
      about the exact matrix -- that is what D2 measures -- and the two are reported separately on
      purpose: a width is a knob, an accuracy is a measurement, and c38's ERRATUM 19 was exactly the
      cost of letting one read as the other.

usage: m2_c48_recover_depth.py [C48DIR] [C46DIR]
"""
import sys, os, json, glob
from mpmath import mp, mpf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m2_c48_cell_storage as S


def sf(a, b):
    a, b = mpf(a), mpf(b)
    if a == b:
        return mp.inf
    return -mp.log(abs(a - b) / abs(a), 10)


def main(c48dir, c46dir):
    mp.dps = 400
    cells = {}
    for cf in sorted(glob.glob(os.path.join(c48dir, "c48_*.json"))):
        c = json.load(open(cf))
        cells[(c["parity"], c["N"], c["dps"])] = (cf, c)

    print("m2_c48_recover_depth   (x=13, gl=9, it=16)\n")

    # ---------------- D1 structural
    print("D1  STORAGE DEPTH -- what the file physically retains")
    print("    %-22s %10s %10s %12s" % ("cell", "old s.f.", "new bits", "new s.f."))
    for (p, N, dps), (cf, c) in sorted(cells.items()):
        man = int(c["lambda_min_exact"]["man"])
        bits = man.bit_length()
        print("    %-22s %10d %10d %12.1f"
              % ("%s N=%d dps=%d" % (p, N, dps), 60, bits, bits * 0.30103))
    print()

    # ---------------- D2 reproducible depth, one knob moved
    print("D2  REPRODUCIBLE DEPTH -- dps=150 vs an independent dps=220 run, one knob moved")
    print("    read through the frozen 60-s.f. cell vs through the c48 full-precision cell")
    print("    %-16s %14s %14s %10s" % ("cell", "via c46 (s.f.)", "via c48 (s.f.)", "gain"))
    d2rows = []
    for (p, N, dps), (cf, c) in sorted(cells.items()):
        if dps == 150 and (p, N, 220) in cells:
            hi = S.load_number(cells[(p, N, 220)][1], "lambda_min")
            # via the NEW storage
            lo_new = S.load_number(c, "lambda_min")
            d_new = sf(hi, lo_new)
            # via the OLD storage: the frozen cell, exactly as any third party had to read it
            frozen_fn = os.path.join(c46dir, os.path.basename(cf).replace("c48_", "c46_", 1))
            frozen = json.load(open(frozen_fn))
            lo_old = mpf(frozen["lambda_min"])
            d_old = sf(hi, lo_old)
            d2rows.append((p, N, d_old, d_new))
            print("    %-16s %14.2f %14.2f %10.2f"
                  % ("%s N=%d" % (p, N), d_old, d_new, d_new - d_old))
    print()

    # ---------------- the c47 headline, reproduced and removed on the artefact
    if d2rows:
        print("    THE c47 HEADLINE, REPRODUCED: a third party holding a value good to 220 dps and")
        print("    comparing it against our PUBLISHED cell measures a relative difference of")
        for (p, N, d_old, d_new) in d2rows:
            print("        %-12s 1e-%.2f  <- our print granularity, not an agreement depth"
                  % ("%s N=%d" % (p, N), d_old))
        print("    and against the c48 cell, of")
        for (p, N, d_old, d_new) in d2rows:
            print("        %-12s 1e-%.2f  <- the object" % ("%s N=%d" % (p, N), d_new))
        print()

    # ---------------- D3 rigorous bound
    print("D3  RIGOROUS BOUND on the assembled matrix -- ||Mv-lam v||/(||v|| |lam|)")
    print("    %-22s %14s" % ("cell", "s.f. bounded"))
    for (p, N, dps), (cf, c) in sorted(cells.items()):
        if "eig_residual_bound_sf" in c:
            print("    %-22s %14s" % ("%s N=%d dps=%d" % (p, N, dps), c["eig_residual_bound_sf"]))
    print()

    # ---------------- verdict
    ok = all(d_new > 60 for (_, _, _, d_new) in d2rows) and bool(d2rows)
    print("CLOSING CONDITION -- a committed cell stores the value at full working precision and")
    print("re-reading it recovers MORE THAN 60 s.f., measured by an instrument that is not the")
    print("60-s.f. print field: %s" % ("MET" if ok else "NOT MET"))
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    REPO = os.path.dirname(os.path.dirname(HERE))
    sys.exit(main(a[0] if a else os.path.join(REPO, "data", "c48"),
                  a[1] if len(a) > 1 else os.path.join(REPO, "data", "c46")))
