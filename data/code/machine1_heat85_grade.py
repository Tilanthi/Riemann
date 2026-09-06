#!/usr/bin/env python3
"""machine1 heat85 GRADER — charter mechanism-1 generation zero.

Written and hashed BEFORE the sealed runner heat85 was executed (sha256 recorded in
the prereg m1-L168). Per trap #123: each hypothesis is graded on the JSON KEYS the
prereg names, thresholds transcribed ONCE from the frozen prereg strings and printed
beside every verdict. This grader computes no cell; it only reads
heat85_charter_pilot_g0.json and applies the frozen thresholds.

Grading conventions declared at freeze (before any value existed):
  (A) every P is a CONJUNCTION of clauses; ONE failing clause fires the whole
      prediction against m1. Clause outcomes are printed individually.
  (B) fires-bits are taken from the runner's frozen threshold lam_min < -1e-12;
      strict lambda inequalities are compared at full printed precision (25 digits).
  (C) any strict-inequality margin within rel 1e-3 is flagged BOUNDARY in the
      detail lines (reported, verdict unchanged).
  (D) if the gate did not pass (controls RED / founders mismatch / kill-controls
      survived / injection undetected), every P is UNGRADED, not failed.
"""
import json
import sys
from decimal import Decimal, getcontext

getcontext().prec = 60

OUT = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat85_charter_pilot_g0.json"
RIDGE = ["16", "18", "19", "20", "21", "22", "23", "24"]

SC = json.load(open(sys.argv[1] if len(sys.argv) > 1 else OUT))
C = SC["cells"]
D = lambda s: Decimal(str(s))

verdicts = []


def emit(pid, name, held, det, threshold):
    verdicts.append({"id": pid, "name": name, "verdict": held, "threshold_as_frozen": threshold,
                     "detail": det})
    print("\n%-3s %-46s ==> %s" % (pid, name, held))
    print("    threshold as frozen : %s" % threshold)
    for line in det:
        print("    %s" % line)


# ---- gate (D)
g = SC.get("gate", {})
gate_ok = (g.get("controls_status") == "GREEN" and g.get("G2_founders_reproduced")
           and g.get("G3_kill_controls_fired") and g.get("defect_injection", {}).get("detected"))
print("gate: controls %s, G2 %s, G3 %s, G4 %s" % (
    g.get("controls_status"), g.get("G2_founders_reproduced"), g.get("G3_kill_controls_fired"),
    g.get("defect_injection", {}).get("detected")))

if not gate_ok:
    for pid, name in (("P1", "ridge delta-edge"), ("P2", "k=17 knife is site-local"),
                      ("P3", "ridge terminates at k=24"), ("P4", "k=24@0.1 ordinary monotone")):
        emit(pid, name, "UNGRADED (gate failure, convention D)", ["no mutant was scored"], "-")
else:
    # ---- P1: ridge delta-edge (keys cells/{k}/0.04, /0.06, /0.07; founders /0.05)
    det = []
    fail = []
    n06 = sum(1 for k in RIDGE if C[k + "/0.06"]["fires"])
    n07 = sum(1 for k in RIDGE if C[k + "/0.07"]["fires"])
    for k in RIDGE:
        l04, l05 = C[k + "/0.04"]["lam_min"], C[k + "/0.05"]["lam_min"]
        s04 = C[k + "/0.04"]["fires"]
        if s04:
            fail.append("%s fires at 0.04" % k)
        margin = abs(D(l04) - D(l05)) / abs(D(l05))
        det.append("k=%s  lam(0.04)=%s  lam(0.05)=%s  survives04=%s  lam04>lam05=%s%s"
                   % (k, l04, l05, not s04, D(l04) > D(l05),
                      "  [BOUNDARY rel %.1e]" % margin if margin < Decimal("1e-3") else ""))
        if not D(l04) > D(l05):
            fail.append("%s not monotone down to 0.04" % k)
    det.append("fires at 0.06: %d of 8 (need >= 5)" % n06)
    det.append("fires at 0.07: %d of 8 (need >= 7)" % n07)
    if n06 < 5:
        fail.append("only %d fire at 0.06" % n06)
    if n07 < 7:
        fail.append("only %d fire at 0.07" % n07)
    emit("P1", "ridge delta-edge", "FIRES AGAINST m1" if fail else "HELD", det,
         "all 8 survive at 0.04 AND lam(0.04)>lam(0.05) each AND >=5 of 8 fire at 0.06 AND >=7 of 8 fire at 0.07"
         + ("; failed clauses: " + "; ".join(fail) if fail else ""))

    # ---- P2: k=17 knife is site-local
    det = ["17/0.04 fires=%s lam=%s" % (C["17/0.04"]["fires"], C["17/0.04"]["lam_min"]),
           "16/0.04 survives=%s lam=%s" % (not C["16/0.04"]["fires"], C["16/0.04"]["lam_min"]),
           "18/0.04 survives=%s lam=%s" % (not C["18/0.04"]["fires"], C["18/0.04"]["lam_min"])]
    ok = C["17/0.04"]["fires"] and not C["16/0.04"]["fires"] and not C["18/0.04"]["fires"]
    emit("P2", "k=17 knife is site-local", "HELD" if ok else "FIRES AGAINST m1", det,
         "17/0.04 fires while 16/0.04 and 18/0.04 survive")

    # ---- P3: ridge terminates at k=24
    det = ["25/0.05 fires=%s lam=%s" % (C["25/0.05"]["fires"], C["25/0.05"]["lam_min"]),
           "(gamma0(26)=94.99: step law puts delta_c at 0.2 >> 0.05)"]
    emit("P3", "ridge terminates at k=24", "HELD" if C["25/0.05"]["fires"] else "FIRES AGAINST m1",
         det, "25/0.05 fires")

    # ---- P4: k=24@0.1 ordinary monotone
    det = []
    fail = []
    l09, l10, l11, l12 = (C["24/0.09"]["lam_min"], C["24/0.1"]["lam_min"],
                          C["24/0.11"]["lam_min"], C["24/0.12"]["lam_min"])
    if C["24/0.09"]["fires"]:
        fail.append("24/0.09 fires")
    if not D(l09) > D(l10):
        fail.append("lam(0.09) not > lam(0.1)")
    if not C["24/0.11"]["fires"]:
        fail.append("24/0.11 survives")
    if not C["24/0.12"]["fires"]:
        fail.append("24/0.12 survives")
    margin = abs(D(l09) - D(l10)) / abs(D(l10))
    det.append("lam(0.09)=%s lam(0.1)=%s lam(0.11)=%s lam(0.12)=%s%s"
               % (l09, l10, l11, l12, "  [BOUNDARY 09-vs-10 rel %.1e]" % margin
                  if margin < Decimal("1e-3") else ""))
    emit("P4", "k=24@0.1 ordinary monotone", "FIRES AGAINST m1" if fail else "HELD", det,
         "0.09 survives with lam>lam(0.1); 0.11 and 0.12 fire"
         + ("; failed clauses: " + "; ".join(fail) if fail else ""))

held = sum(1 for v in verdicts if v["verdict"] == "HELD")
fired = sum(1 for v in verdicts if v["verdict"].startswith("FIRES"))
ungraded = len(verdicts) - held - fired
print("\n=== TALLY: %d HELD / %d FIRED-AGAINST-m1 / %d ungraded, of 4 ===" % (held, fired, ungraded))
print("=== independence (per #122, reasons were clustered at freeze): P1 rests on the "
      "thinning-law edge; P2 on site-locality of the k=17 knife; P3 on the step law's "
      "gamma0>88.77 band; P4 on k=24@0.1 being an ORDINARY survivor. Four distinct "
      "reasons, no shared imported level. ===")
json.dump({"verdicts": verdicts, "tally": {"held": held, "fired": fired, "ungraded": ungraded}},
          open(sys.argv[2] if len(sys.argv) > 2 else
               "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat85_grade_verdicts.json", "w"),
          indent=1)
