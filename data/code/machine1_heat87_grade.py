#!/usr/bin/env python3
"""heat87 grader — scores the gen-1 prereg (m1-PREREG-heat87) EXACTLY AS REGISTERED.

Input seals: sha256 of the gen-0 panel (the public launch-4 results, d7a90de) is
frozen below; the grader aborts if it changed.  The gen-1 output JSON is the
runner's OUTJ.  All thresholds are transcribed ONCE here and printed beside
every verdict (#123).  Grading is mechanical: no judgement inside.

Frozen clauses (as registered in m1-PREREG-heat87):

  P1  held-out firing bands (conjunctive; k=19/20/21 were never span-marked):
        P1a  delta*(19) in (0.070, 0.085]
        P1b  delta*(20) in (0.070, 0.095]
        P1c  delta*(21) in (0.090, 0.130]
      For each k: bracket = (largest non-firing delta below the smallest firing
      delta, smallest firing delta].  INSIDE iff bracket's upper <= band upper
      AND bracket's lower >= band lower.  FAST iff bracket's lower < band lower
      (crossing earlier than registered).  SLOW iff no firing cell in the panel
      or the bracket's upper > band upper.  P1 = HELD iff all three INSIDE.
  P2  responsive brackets (conjunctive):
        P2a  delta*(16) in (0.050, 0.053]      (i.e. lam(16,0.053) < -1e-12)
        P2b  delta*(18) in (0.050, 0.054]      (i.e. lam(18,0.054) < -1e-12)
        P2c  delta*(23) in (0.070, 0.092]      (lam(23,0.076) > 0 and lam(23,0.092) < -1e-12)
      HELD iff all three band edges hold with the gen-0 (0.05/0.07) non-firing
      anchors verified in the merged panel.
  P3  collimation head-to-head: at least one of k=22 (some delta <= 0.19),
      k=24 (<= 0.19), k=25 (<= 0.20) FIRES.  HELD = m2's span-collapse/
      never-fire reading is dead on the collimated class.  FIRED = all three
      survive their full panels -> the geometric extrapolator is dead as a
      firing predictor; the loss is filed as the span law's extension.
  P4  the law: every NEW equal-spacing triple in the merged panel accelerates
      (second difference < 0).  The 18 triples are ENUMERATED below, not
      discovered.  HELD iff 18/18.  Violations are split pre-crossing (law
      dead outright) vs post-crossing (the burst is not monotone), both FIRED,
      differently interpreted.

  TALLY: 0-4 predictions HELD.  Outcome RED if the runner's gate is not
  4/4 GREEN (nothing scored).
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
OUTJ = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat87_charter_g1.json"
THRESH = Decimal("-1e-12")   # fires iff lam_min < THRESH (transcribed once)

# ---- the 18 registered P4 triples (k, d1, d2, d3) at uniform spacing; values merged gen-0+gen-1
# (enumeration validated against the actual panel keys by the pre-freeze dry-run:
#  the k=21 chain 0.07->0.09 is broken by the 0.02 gap, so only the gen-1 block
#  triples are measurable there)
TRIPLES = [
    (19, "0.070", "0.075", "0.080"), (19, "0.075", "0.080", "0.085"),
    (20, "0.070", "0.080", "0.090"),
    (21, "0.090", "0.100", "0.110"), (21, "0.100", "0.110", "0.120"),
    (21, "0.110", "0.120", "0.130"),
    (22, "0.130", "0.150", "0.170"), (22, "0.150", "0.170", "0.190"),
    (23, "0.076", "0.080", "0.084"), (23, "0.080", "0.084", "0.088"),
    (23, "0.084", "0.088", "0.092"),
    (24, "0.150", "0.160", "0.170"), (24, "0.160", "0.170", "0.180"),
    (24, "0.170", "0.180", "0.190"),
    (25, "0.150", "0.160", "0.170"), (25, "0.160", "0.170", "0.180"),
    (25, "0.170", "0.180", "0.190"), (25, "0.180", "0.190", "0.200"),
]

# ---- registered bands (transcribed once)
P1_BANDS = {19: (Decimal("0.070"), Decimal("0.085")),
            20: (Decimal("0.070"), Decimal("0.095")),
            21: (Decimal("0.090"), Decimal("0.130"))}
P2_EDGES = [(16, "0.053"), (18, "0.054")]
P2_23 = ("0.076", "0.092")
P3_TOPS = {22: Decimal("0.19"), 24: Decimal("0.19"), 25: Decimal("0.20")}


def merged_panel():
    if hashlib.sha256(open(GEN0, "rb").read()).hexdigest() != GEN0_SHA:
        sys.exit("SEAL FAIL gen-0 results json changed")
    g0 = json.load(open(GEN0))
    g1 = json.load(open(OUTJ))
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
    return g1, panel


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
    g1, panel = merged_panel()
    gate = g1["gate"]
    print("gate: controls=%s G2=%r G3=%r G4-detected=%r  n_mutants=%r"
          % (gate["controls_status"], gate["G2_founders_reproduced"],
             gate["G3_kill_controls_fired"], gate["defect_injection"]["detected"],
             g1.get("n_mutants")))
    ok = (gate["controls_status"] == "GREEN" and gate["G2_founders_reproduced"]
          and gate["G3_kill_controls_fired"] and gate["defect_injection"]["detected"])
    if not ok:
        print("OUTCOME: RED — gate not 4/4 GREEN, nothing scored")
        return 1

    held = []
    labels = {19: "P1a", 20: "P1b", 21: "P1c"}
    print("\n--- P1: held-out firing bands (fires iff lam_min < %s) ---" % THRESH)
    for k, (lo, hi) in sorted(P1_BANDS.items()):
        b = bracket(panel, k)
        if b is None or b[1] > hi:
            g = "SLOW"
        elif b[0] is not None and b[0] < lo:
            g = "FAST"
        else:
            g = "INSIDE"
        print("  %s k=%d band (%s, %s]: bracket %s -> %s"
              % (labels[k], k, lo, hi, ("(%s, %s]" % (b[0], b[1])) if b else "no firing cell", g))
        held.append(g == "INSIDE")
    p1 = all(held)
    print("  P1: %s" % ("HELD" if p1 else "FIRED"))

    print("\n--- P2: responsive brackets ---")
    p2 = True
    for k, edge in P2_EDGES:
        top = lam(panel, k, edge) < THRESH
        anch = not fires(panel, k, "0.05")
        print("  P2: k=%d band (0.050, %s]: lam(%s) = %s < THRESH: %r; gen-0 anchor 0.05 non-firing: %r"
              % (k, edge, edge, lam(panel, k, edge), top, anch))
        p2 = p2 and top and anch
    lo23, hi23 = P2_23
    c1 = not fires(panel, 23, lo23)
    c2 = fires(panel, 23, hi23)
    anch23 = not fires(panel, 23, "0.07")
    print("  P2: k=23 band (0.070, %s]: lam(%s)=%s non-firing %r; lam(%s)=%s fires %r; anchor 0.07 %r"
          % (hi23, lo23, lam(panel, 23, lo23), c1, hi23, lam(panel, 23, hi23), c2, anch23))
    p2 = p2 and c1 and c2 and anch23
    print("  P2: %s" % ("HELD" if p2 else "FIRED"))

    print("\n--- P3: collimation head-to-head ---")
    anyfire = False
    for k, top in sorted(P3_TOPS.items()):
        ds = sorted(d for (kk, d) in panel if kk == k and d <= top)
        f = any(panel[(k, d)][1] for d in ds)
        print("  P3: k=%d fires by %s: %r  (panel top lam = %s)"
              % (k, top, f, lam(panel, k, str(max(ds)))))
        anyfire = anyfire or f
    print("  P3: %s  (%s)" % ("HELD" if anyfire else "FIRED",
                              "collimation reading dead" if anyfire
                              else "geometric extrapolator dead as firing predictor; span law's extension"))

    print("\n--- P4: the law — 18 registered equal-spacing triples accelerate ---")
    n_ok = 0
    for (k, d1, d2, d3) in TRIPLES:
        l1, l2, l3 = lam(panel, k, d1), lam(panel, k, d2), lam(panel, k, d3)
        dd1, dd2 = l2 - l1, l3 - l2
        acc = dd2 - dd1 < 0
        n_ok += acc
        seg = "post-crossing" if l1 < 0 else ("crossing" if l2 < 0 or l3 < 0 else "pre-crossing")
        print("  P4: k=%d (%s,%s,%s): d %+.4e -> %+.4e  accelerating=%r  [%s]"
              % (k, d1, d2, d3, dd1, dd2, acc, seg))
    p4 = n_ok == len(TRIPLES)
    print("  P4: %s  (%d/%d)" % ("HELD" if p4 else "FIRED", n_ok, len(TRIPLES)))

    tally = sum([p1, p2, anyfire, p4])
    print("\nTALLY: %d HELD / %d FIRED of 4 registered predictions"
          % (tally, 4 - tally))
    return 0


if __name__ == "__main__":
    sys.exit(main())
