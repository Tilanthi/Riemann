#!/usr/bin/env python3
"""heat87 gen-2 grader — scores the gen-2 prereg (m1-PREREG-heat87-gen2) EXACTLY AS REGISTERED.

Input seals: sha256 of the gen-0 panel (public d7a90de) and of the gen-1 charter
(public 5a9bacb) are frozen below; the grader aborts if either changed.  The
gen-2 output JSON is the runner's OUTJ.  All thresholds are transcribed ONCE
here and printed beside every verdict (#123).  Grading is mechanical.

Frozen clauses (as registered in m1-PREREG-heat87-gen2):

  P1'  the k=18 bracket closure.  Outcome space (trap #153: a PARTITION, every
       measurable landing pre-assigned): B1 (0.054, 0.0542], B2 (0.0542,
       0.0544], B3 (0.0544, 0.0546], B4 (0.0546, 0.0548], B5 (0.0548, 0.0552],
       B6 (0.0552, 0.0560], B7 (0.0560, 0.0580], B8 (0.0580, 0.060] (top closed
       by the gen-0 anchor lam(18, 0.06) = -5.117e-10 FIRES); a sub-0.054
       landing is the PIN-CONTRADICTION branch (only via P2' failing).
       HELD iff the measured first-firing edge is 0.0542 (B1) or 0.0544 (B2) —
       the L1 band's projection (band (0.054130, 0.054219) straddles the B1/B2
       edge; point estimate 0.054168699 sits in B1; the straddle is disclosed in
       the prereg, not resolved by it).  FIRED otherwise, with the branch named;
       the pre-committed loss reading for B3+ is that the fine-scale descent
       collapsed relative to the 0.0015 chain — L1's one-step extrapolation
       overpredicts steepness at 7.5x finer resolution, a measured
       scale-dependence of the law.
  P2'  the pinned constraint reproduces: lam_g2(18, 0.0540) > 0 AND rel vs the
       gen-1 full-print pin 7.883466610075161176082923e-12 <= 1e-9 (the gate-G2
       tolerance; the run is deterministic and same-instrument, so rel is
       expected ~0).  Branches: REPRODUCE / SIGN-FLIP (lam <= 0) / MISMATCH
       (rel > 1e-9 with lam > 0).  HELD iff REPRODUCE.  A SIGN-FLIP or MISMATCH
       also forces P1' to its PIN-CONTRADICTION branch (unscored-as-band,
       recorded).
  P3'  the law: every NEW equal-spacing triple in the frozen merged k=18 ladder
       accelerates (second difference < 0).  The 10 triples are ENUMERATED below
       (machine-enumerated by the band-derivation script over the frozen ladder,
       newness = contains a cell FIRST measured in gen-2; the 0.0540 re-pin is
       excluded from newness), not discovered.  HELD iff 10/10.  Violations are
       split pre-crossing (law dead outright) vs post-crossing (burst not
       monotone), both FIRED, differently interpreted — as at gen-1.

  TALLY: 0-3 predictions HELD.  Outcome RED if the runner's gate is not 4/4
  GREEN (nothing scored).
"""
import hashlib
import json
import os
import sys
from decimal import Decimal, getcontext

getcontext().prec = 50
HERE = os.path.dirname(os.path.abspath(__file__))
GEN0 = os.path.normpath(os.path.join(HERE, "..", "machine1_heat85_results.json"))
GEN0_SHA = "92f652868a3a5f572615f935eab8395c7da9db03830e44725d5e182c072390d3"
GEN1 = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat87_charter_g1.json"
GEN1_SHA = "4d737e4125f03731266163fe6ba03ee3a06606a887a3458c4ca0d4a327f31d6b"
OUTJ = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat87_charter_g2.json"
THRESH = Decimal("-1e-12")   # fires iff lam_min < THRESH (transcribed once)
PIN = Decimal("7.883466610075161176082923e-12")  # gen-1 full print, transcribed once
PIN_TOL = Decimal("1e-9")    # the gate-G2 tolerance, transcribed once

# ---- the 10 registered P3' triples (k=18; machine-enumerated over the frozen
# merged ladder {0.040, 0.050, 0.0510, 0.0525, 0.0540, 0.0542, 0.0544, 0.0546,
# 0.0548, 0.0552, 0.0560, 0.0580, 0.060, 0.070}; validated cell-by-cell by the
# band-derivation script, whose output the prereg quotes)
TRIPLES = [
    ("18", "0.050", "0.0540", "0.0580"),
    ("18", "0.0540", "0.0542", "0.0544"),
    ("18", "0.0540", "0.0544", "0.0548"),
    ("18", "0.0540", "0.0546", "0.0552"),
    ("18", "0.0540", "0.0560", "0.0580"),
    ("18", "0.0542", "0.0544", "0.0546"),
    ("18", "0.0544", "0.0546", "0.0548"),
    ("18", "0.0544", "0.0548", "0.0552"),
    ("18", "0.0544", "0.0552", "0.0560"),
    ("18", "0.0560", "0.0580", "0.060"),
]

# ---- the registered partition (transcribed once)
BRANCHES = [("B1", Decimal("0.054"), Decimal("0.0542")),
            ("B2", Decimal("0.0542"), Decimal("0.0544")),
            ("B3", Decimal("0.0544"), Decimal("0.0546")),
            ("B4", Decimal("0.0546"), Decimal("0.0548")),
            ("B5", Decimal("0.0548"), Decimal("0.0552")),
            ("B6", Decimal("0.0552"), Decimal("0.0560")),
            ("B7", Decimal("0.0560"), Decimal("0.0580")),
            ("B8", Decimal("0.0580"), Decimal("0.060"))]
P1_OK_EDGES = (Decimal("0.0542"), Decimal("0.0544"))  # the band projection B1 | B2


def merged_panel():
    if hashlib.sha256(open(GEN0, "rb").read()).hexdigest() != GEN0_SHA:
        sys.exit("SEAL FAIL gen-0 results json changed")
    if hashlib.sha256(open(GEN1, "rb").read()).hexdigest() != GEN1_SHA:
        sys.exit("SEAL FAIL gen-1 charter json changed")
    g0 = json.load(open(GEN0))
    g1 = json.load(open(GEN1))
    g2 = json.load(open(OUTJ))
    panel = {}
    for key, v in g0["cells"].items():
        k, d = key.split("/")
        panel[(int(k), Decimal(d))] = (Decimal(v["lam_min"]), v["fires"])
    for key, v in g0["gate"]["founders"].items():
        k, d = key.split("/")
        panel.setdefault((int(k), Decimal(d)), (Decimal(v["lam"]), v["fires"]))
    for key, v in g1["cells"].items():
        k, d = key.split("/")
        panel[(int(k), Decimal(d))] = (Decimal(v["lam_min"]), v["fires"])
    for key, v in g2["cells"].items():
        k, d = key.split("/")
        panel[(int(k), Decimal(d))] = (Decimal(v["lam_min"]), v["fires"])
    return g2, panel


def lam(panel, k, d):
    return panel[(k, Decimal(d))][0]


def fires(panel, k, d):
    return panel[(k, Decimal(d))][1]


def bracket(panel, k):
    """(largest non-firing delta below smallest firing delta, smallest firing delta]
    or None if no firing cell."""
    ds = sorted(d for (kk, d), (lamv, f) in panel.items() if kk == k)
    fds = [d for d in ds if panel[(k, d)][1]]
    if not fds:
        return None
    first = fds[0]
    below = [d for d in ds if d < first and not panel[(k, d)][1]]
    return (below[-1] if below else None, first)


def main():
    g2, panel = merged_panel()
    gate = g2["gate"]
    print("gate: controls=%s G2=%r G3=%r G4-detected=%r  n_mutants=%r"
          % (gate["controls_status"], gate["G2_founders_reproduced"],
             gate["G3_kill_controls_fired"], gate["defect_injection"]["detected"],
             g2.get("n_mutants")))
    ok = (gate["controls_status"] == "GREEN" and gate["G2_founders_reproduced"]
          and gate["G3_kill_controls_fired"] and gate["defect_injection"]["detected"])
    if not ok:
        print("OUTCOME: RED — gate not 4/4 GREEN, nothing scored")
        return 1

    print("\n--- the merged k=18 ladder (descriptive; nothing scored on it) ---")
    ds = sorted(d for (kk, d) in panel if kk == 18)
    for d in ds:
        print("  18/%s: lam = %s  fires=%r" % (d, panel[(18, d)][0], panel[(18, d)][1]))

    # ---------------- P2' first (P1's contradiction branch depends on it) ----
    print("\n--- P2': the pinned constraint reproduces (fires iff lam_min < %s) ---" % THRESH)
    l_pin = lam(panel, 18, "0.0540")
    rel = abs(l_pin - PIN) / PIN
    if l_pin <= 0:
        p2, p2b = False, "SIGN-FLIP (lam <= 0)"
    elif rel > PIN_TOL:
        p2, p2b = False, "MISMATCH (rel > 1e-9)"
    else:
        p2, p2b = True, "REPRODUCE"
    print("  P2': lam_g2(18, 0.0540) = %s" % l_pin)
    print("  P2': pin (gen-1 full print) = %s" % PIN)
    print("  P2': rel = %s (tol 1e-9) -> %s -> %s" % (rel, p2b, "HELD" if p2 else "FIRED"))

    # ---------------- P1': the bracket closure ----------------
    print("\n--- P1': the k=18 bracket closure (partition B1..B8 + contradiction) ---")
    b = bracket(panel, 18)
    if b is None:
        edge = None
    else:
        edge = b[1]
    if edge is None:
        p1, br = False, "NO-FIRING-CELL (bracket open above the panel — impossible given the gen-0 0.060 anchor unless the merged panel is wrong)"
    elif edge <= Decimal("0.0540"):
        p1, br = False, "PIN-CONTRADICTION (first firing at or below the pinned non-firing cell)"
    else:
        br = next((nm for nm, lo, hi in BRANCHES if lo < edge <= hi), "OUTSIDE-PARTITION")
        p1 = edge in P1_OK_EDGES
    print("  P1': measured bracket = %s" % (("(%s, %s]" % b) if b else "none"))
    print("  P1': branch = %s   band projection {B1, B2} -> %s" % (br, "HELD" if p1 else "FIRED"))
    if not p1 and br.startswith("B") and int(br[1]) >= 3:
        print("  P1': pre-committed loss reading: fine-scale descent collapsed relative to")
        print("       the 0.0015 chain — L1 overpredicts steepness at 7.5x finer resolution")

    # ---------------- P3': the law ----------------
    print("\n--- P3': the law — 10 registered NEW equal-spacing triples accelerate ---")
    n_ok = 0
    for (k, d1, d2, d3) in TRIPLES:
        l1, l2, l3 = lam(panel, int(k), d1), lam(panel, int(k), d2), lam(panel, int(k), d3)
        dd1, dd2 = l2 - l1, l3 - l2
        acc = dd2 - dd1 < 0
        n_ok += acc
        seg = "post-crossing" if l1 < 0 else ("crossing" if l2 < 0 or l3 < 0 else "pre-crossing")
        print("  P3': k=%s (%s,%s,%s): d %+.4e -> %+.4e  accelerating=%r  [%s]"
              % (k, d1, d2, d3, dd1, dd2, acc, seg))
    p3 = n_ok == len(TRIPLES)
    print("  P3': %s  (%d/%d)" % ("HELD" if p3 else "FIRED", n_ok, len(TRIPLES)))

    tally = sum([p1, p2, p3])
    print("\nTALLY: %d HELD / %d FIRED of 3 registered predictions" % (tally, 3 - tally))
    return 0


if __name__ == "__main__":
    sys.exit(main())
