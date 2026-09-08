#!/usr/bin/env python3
"""m2_c52_armD.py -- registered arm D ONLY: the dps confound in the published 3-point series.

WRITTEN AFTER THE SEAL, and labelled as such.  Arm D is registered in m2_c52_prereg.md sec 3; the
script for it was not written before launch, so it is a SEPARATE file and is NOT in the seal.  It
touches no registered cell, computes no new eigenvalue, and uses the same imported c50 pool().

The confound: c50's published q_1 series runs dps 150 (x=5), 150 (x=13), 300 (x=19).  A precision
change at the top of the range is therefore folded into the published x-drift.  This cycle runs
dps=300 everywhere; arm D measures what that repair was worth by differencing the two x=13 cells,
which differ ONLY in dps (and in k, which the pooling prefix makes irrelevant: q_1 uses 3 rungs).

usage: m2_c52_armD.py --cells DIR
"""
import argparse, os, sys
from mpmath import mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m2_c52_qdrift as Q                      # noqa: E402

mp.dps = 60

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    a = ap.parse_args()
    c50dir = os.path.join(Q.REPO, "data", "c50")
    print("=" * 96)
    print("ARM D -- the dps confound in the published series (x=13, N=100, everything else equal)")
    print("=" * 96)
    old = Q.q1_of(Q.load_pair(c50dir, None, "13", 100, 150, k=5))
    new = Q.q1_of(Q.load_pair(a.cells, None, "13", 100, 300, k=3))
    if old is None or new is None:
        print("  UNMEASURED (old=%s new=%s)" % (old is not None, new is not None))
        raise SystemExit(0)
    print("  q_1(x=13, N=100, dps=150, k=5)  [published c50] = %s" % mp.nstr(old, 25))
    print("  q_1(x=13, N=100, dps=300, k=3)  [c52 cell]      = %s" % mp.nstr(new, 25))
    print("  difference attributable to dps 150 -> 300       = %s" % mp.nstr(new - old, 10))
    # x=19 was ALREADY dps300 in c50, so its two cells should agree to the last digit: a
    # cross-cycle determinism check, not a dps measurement.
    o19 = Q.q1_of(Q.load_pair(c50dir, None, "19", 100, 300, k=3))
    n19 = Q.q1_of(Q.load_pair(a.cells, None, "19", 100, 300, k=3))
    if o19 is not None and n19 is not None:
        print("\n  CROSS-CYCLE DETERMINISM (x=19, N=100, dps300, k=3 -- identical configuration):")
        print("    c50 published = %s" % mp.nstr(o19, 25))
        print("    c52 re-run    = %s" % mp.nstr(n19, 25))
        print("    difference    = %s  -> %s" % (mp.nstr(n19 - o19, 6),
                                                 "IDENTICAL" if n19 == o19 else "DIFFERS"))
    else:
        print("\n  cross-cycle determinism check: UNMEASURED (x=19 c52 cell absent)")
