#!/usr/bin/env python3
"""m2_c49_upgrade_ladder.py -- build data/c49/: the c48 ladder with a MEASURED depth in every cell,
and no liftable precision number that the object does not support.

WHAT MOVES AND WHAT DOES NOT
----------------------------
`data/c48/` is NOT touched. m1-L190 verified those exact bytes at primary; editing them in place
would silently invalidate somebody else's completed verification, which is a worse defect than the
one being fixed. The upgraded ladder is written BESIDE it, at `data/c49/`, so the two can be diffed.

The gate below is not a tolerance and not a band. For every cell:
  * every retained PRINT field (`lambda_min`, `lambda_min_30`, `L`, `residual`, `log10`, `*_full`)
    must be byte-identical to the source cell;
  * every `*_exact` reconstruction field (sign/man/exp/prec/form) must be byte-identical;
  * the value reconstructed from `_exact` must be bit-identical to the source's;
  * nothing may be REMOVED.
Any single failure and the whole upgrade is withdrawn -- exit 1, no files written.

usage: m2_c49_upgrade_ladder.py [--write]
"""
import os
import sys
import glob
import json
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/shared/rh-exchange-repo/Riemann"
C48DIR = os.path.join(REPO, "data", "c48")
OUTDIR = os.path.join(REPO, "data", "c49")
NEWDIR = os.path.join(HERE, "cells220")

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "flat"))
import m2_c49_precision as P            # noqa: E402
import m2_c49_depth_all_rungs as D      # noqa: E402
import m2_c48_cell_storage as S         # noqa: E402

PRINT_FIELDS = ("L", "lambda_min", "lambda_min_30", "residual", "log10",
                "L_full", "lambda_min_full", "residual_full", "log10_full")
EXACT_KEYS = ("L_exact", "lambda_min_exact", "residual_exact", "log10_exact")


def sources():
    """every cell that belongs in the c49 ladder: (path, is_reference_run)."""
    out = []
    for f in sorted(glob.glob(os.path.join(C48DIR, "c48_*.json"))):
        out.append(f)
    for f in sorted(glob.glob(os.path.join(NEWDIR, "c48_*.json"))):
        out.append(f)
    return out


def measure():
    """(parity, N) -> depth dict for lambda_min, from the D2 instrument. dps=220 cells get None."""
    pairs = D.load_pairs()
    m = {}
    for (p, N), v in pairs.items():
        if v["hi"] is None:
            continue
        hi = S.load_number(v["hi"], "lambda_min")
        lo = S.load_number(v["lo"], "lambda_min")
        m[(p, N)] = {"lo_dps": v["lo"]["dps"], "hi_dps": v["hi"]["dps"],
                     "continuous": round(D.cont_sf(lo, hi), 2),
                     "string_digits": D.agree_digits(lo, hi),
                     "source": "data/c49/m2_c49_depth_all_rungs.out"}
    return m


def nonmovement(src, up):
    """return list of violations; empty list == PASS."""
    bad = []
    for k in PRINT_FIELDS:
        if k in src and src[k] != up.get(k):
            bad.append("PRINT FIELD MOVED: %s" % k)
    for k in EXACT_KEYS:
        if k not in src:
            continue
        a, b = src[k], up.get(k, {})
        for f in ("sign", "man", "exp", "prec", "form"):
            if f in a and a[f] != b.get(f):
                bad.append("EXACT FIELD MOVED: %s/%s" % (k, f))
    for k in src:
        if k not in up:
            bad.append("FIELD REMOVED: %s" % k)
    for k in EXACT_KEYS:
        if k in src:
            key = k[:-6]
            try:
                if S.load_number(src, key) != S.load_number(up, key):
                    bad.append("RECONSTRUCTED VALUE MOVED: %s" % key)
            except Exception as e:                       # noqa: BLE001
                bad.append("RECONSTRUCTION FAILED: %s (%s)" % (key, e))
    return bad


def main():
    write = "--write" in sys.argv
    meas = measure()
    print("m2_c49_upgrade_ladder -- c48 ladder -> data/c49/ with a measured depth per cell\n")
    print("  depth measurements available for %d (parity,N) pairs: %s\n"
          % (len(meas), sorted(meas)))
    results, allbad, staged = [], [], {}
    for f in sources():
        src = json.load(open(f))
        p, N, dps = src["parity"], src["N"], src["dps"]
        m = meas.get((p, N)) if dps == 150 else None
        why = ("measured against the dps=220 partner" if m else
               "UNMEASURED: this IS the reference run of its pair; measuring its own depth "
               "would need a third run at higher dps, which this cycle did not do")
        up, moves = P.upgrade_cell(src, {"lambda_min": m} if m else {})
        bad = nonmovement(src, up)
        findings, stats = P.gate_cell(up)
        struct = P.gate_cell_structure(up)
        gate_ok = stats["fail"] == 0 and all(v == "OK" for v, *_ in struct)
        allbad += [(os.path.basename(f), b) for b in bad]
        name = "c49_" + os.path.basename(f)[len("c48_"):]
        staged[name] = up
        results.append((name, dps, "%s" % (m["continuous"] if m else "-"),
                        len(moves), "PASS" if not bad else "FAIL",
                        "PASS" if gate_ok else "FAIL(%d)" % stats["fail"], why[:34]))
        print("  %-42s dps=%3d depth=%-7s moves=%2d nonmove=%-4s gate=%-7s %s"
              % results[-1])

    print("\n  cells: %d   non-movement violations: %d   gate failures: %d"
          % (len(results), len(allbad), sum(1 for r in results if r[5] != "PASS")))
    if allbad:
        print("\n  WITHDRAWN -- non-movement violated:")
        for a, b in allbad:
            print("      %s: %s" % (a, b))
        return 1
    if any(r[5] != "PASS" for r in results):
        print("\n  WITHDRAWN -- an upgraded cell still fails its own gate.")
        return 1

    print("\n  NON-MOVEMENT: PASS on every field of every cell (no tolerance was used).")
    print("  GATE: every upgraded cell passes m2_c49_precision, including the structural")
    print("  requirement that a stored width is accompanied by a depth slot (trap #155).")

    if write:
        if os.path.isdir(OUTDIR):
            shutil.rmtree(OUTDIR)
        os.makedirs(OUTDIR)
        for name, up in staged.items():
            json.dump(up, open(os.path.join(OUTDIR, name), "w"), indent=1)
        print("\n  wrote %d cells to %s" % (len(staged), OUTDIR))
    else:
        print("\n  (dry run; pass --write to emit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
