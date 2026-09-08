#!/usr/bin/env python3
"""heat87 gen-2 — band derivation + partition + triple enumeration (PUBLIC inputs only).

The gen-2 run closes the one bracket gen-1 re-opened: delta*(18).  Gen-1 P2b
registered delta*(18) in (0.050, 0.054] and the panel measured lam(18, 0.0540) =
+7.883e-12 against a -1e-12 threshold — a 9e-12 miss whose registered
interpretation (m1-L188) is "any miss re-opens the bracket with the sharpened
constraint": delta*(18) in (0.054, ...] with lam(18, 0.0540) > 0 pinned at full
print.  The gen-0 anchors already bound the top: lam(18, 0.06) = -5.117e-10
FIRES, so the re-opened bracket is (0.054, 0.060] going in.

Inputs (all committed public artefacts; shas verified at startup):
  gen-0 panel   data/machine1_heat85_results.json                    (public d7a90de)
  gen-1 charter ASTRA-tree heat87_charter_g1.json                    (public 5a9bacb)

This file computes NO eigenvalue.  It produces:
  A. the L1 geometric extrapolation on the k=18 gen-1 chain (0.0510, 0.0525,
     0.0540), exactly as registered at gen-1: rho from the last two equal-spacing
     differences, band rho/1.3 .. rho*1.3, next difference d3 = rho*d2, and the
     -1e-12 threshold-crossing interval (the firing predicate is lam < -1e-12,
     so the crossing that matters is the THRESHOLD crossing, not the zero).
  B. the frozen gen-2 outcome-space PARTITION over delta*(18) (trap #153):
     every measurable landing assigned to exactly one branch, edges = frozen
     cells; completeness checked mechanically below.
  C. the exhaustive enumeration of NEW equal-spacing triples in the frozen
     merged k=18 ladder (new = contains at least one cell first measured in
     gen-2; the 0.0540 re-pin is excluded from newness), validated cell-by-cell.
"""
import hashlib
import json
import os
import sys
from decimal import Decimal as D, getcontext

getcontext().prec = 60
HERE = os.path.dirname(os.path.abspath(__file__))
G0 = os.path.normpath(os.path.join(HERE, "..", "machine1_heat85_results.json"))
G1 = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat87_charter_g1.json"
G0_SHA = "92f652868a3a5f572615f935eab8395c7da9db03830e44725d5e182c072390d3"
G1_SHA = "4d737e4125f03731266163fe6ba03ee3a06606a887a3458c4ca0d4a327f31d6b"
THRESH = D("-1e-12")

# frozen gen-2 design (the runner's MUTANTS; the grader transcribes the same list)
G2_CELLS = ["0.0540", "0.0542", "0.0544", "0.0546", "0.0548", "0.0552", "0.0560", "0.0580"]
G2_NEW = ["0.0542", "0.0544", "0.0546", "0.0548", "0.0552", "0.0560", "0.0580"]  # 0.0540 = re-pin


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    if sha(G0) != G0_SHA:
        sys.exit("SEAL FAIL gen-0 results changed")
    if sha(G1) != G1_SHA:
        sys.exit("SEAL FAIL gen-1 charter changed")
    g0 = json.load(open(G0))
    g1 = json.load(open(G1))

    print("=== A. L1 on the k=18 gen-1 chain (0.0510, 0.0525, 0.0540), h = 0.0015 ===")
    l10 = D(g1["cells"]["18/0.0510"]["lam_min"])
    l25 = D(g1["cells"]["18/0.0525"]["lam_min"])
    l40 = D(g1["cells"]["18/0.0540"]["lam_min"])
    pin = l40  # the sharpened constraint's pinned value, gen-1 full print
    d1, d2 = l10 - l25, l25 - l40
    rho = d2 / d1
    print("  lam(0.0510) = %s" % l10)
    print("  lam(0.0525) = %s" % l25)
    print("  lam(0.0540) = %s   <-- the pinned constraint (> 0)" % pin)
    print("  d1 = %s   d2 = %s   rho = %s" % (d1, d2, rho))
    rows = []
    for lbl, r in (("point", rho), ("band-lo (rho/1.3)", rho / D("1.3")), ("band-hi (rho*1.3)", rho * D("1.3"))):
        d3 = r * d2
        # threshold crossing: lam goes from +pin at 0.0540 down to THRESH
        dist = pin - THRESH
        cross = D("0.0540") + D("0.0015") * dist / d3
        l42 = pin - d3 * (D("0.0002") / D("0.0015"))  # projected cell value at 0.0542
        fires42 = l42 < THRESH
        print("  %-18s rho_edge=%.6f  d3=%.4e  delta_dagger=%s  proj lam(0.0542)=%.4e  fires@0.0542=%s"
              % (lbl, r, d3, cross, l42, fires42))
        rows.append((lbl, cross, l42, fires42))
    band = (min(r[1] for r in rows), max(r[1] for r in rows))
    print("  REGISTERED BAND on the -1e-12 crossing: (%s, %s)" % (band[0], band[1]))

    print("\n=== B. the frozen partition over delta*(18) (trap #153) ===")
    ladder = sorted({D("0.040"), D("0.050"), D("0.0510"), D("0.0525")}
                    | {D(s) for s in G2_CELLS} | {D("0.060"), D("0.070")})
    print("  frozen merged k=18 ladder: [%s]" % ", ".join(str(x) for x in ladder))
    # firing edges measurable in-panel: every gen-2 cell + the gen-0 0.060 anchor
    edges = [D(s) for s in G2_NEW] + [D("0.060")]
    lo = D("0.054")
    branches = []
    prev = lo
    for e in edges:
        branches.append((prev, e))
        prev = e
    for i, (a, b) in enumerate(branches, 1):
        print("  B%d = (%s, %s]" % (i, a, b))
    # completeness: the firing edge (first firing cell) is exactly one of `edges`;
    # every landing is in exactly one B_i; nothing below 0.054 (the pin) except
    # the pre-named PIN-CONTRADICTION branch (P2's sign-flip / mismatch).
    assert branches[0][0] == D("0.054") and branches[-1][1] == D("0.060")
    assert all(branches[i][1] == branches[i + 1][0] for i in range(len(branches) - 1))
    print("  partition COMPLETE: %d branches, contiguous over (0.054, 0.060]; "
          "sub-0.054 landings = the pre-named PIN-CONTRADICTION branch" % len(branches))

    print("\n=== C. NEW equal-spacing triples in the frozen merged ladder ===")
    news = {D(s) for s in G2_NEW}
    triples = []
    for i, a in enumerate(ladder):
        for j in range(i + 1, len(ladder)):
            h = ladder[j] - a
            if h <= 0:
                continue
            b, c = a + h, a + 2 * h
            if b in ladder and c in ladder:
                cells = {a, b, c}
                if cells & news:  # contains at least one cell FIRST measured in gen-2
                    triples.append((a, b, c, h))
    for (a, b, c, h) in triples:
        print("  (%s, %s, %s)  h=%s" % (a, b, c, h))
    print("  TOTAL NEW TRIPLES: %d  (the grader transcribes this list verbatim; "
          "exhaustive over all (start, h) pairs in the frozen ladder)" % len(triples))

    print("\n=== D. registered P1 band projected onto the partition ===")
    proj = sorted({i + 1 for i, (a, b) in enumerate(branches)
                   if not (band[1] <= a or band[0] > b)})
    print("  L1 band (%s, %s) intersects branches: %s" % (band[0], band[1], proj))
    print("  REGISTERED P1': measured first-firing edge in {0.0542 (B1), 0.0544 (B2)};")
    print("  point estimate B1 (rho_hat = %.6f -> delta_dagger = %s)"
          % (rho, rows[0][1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
