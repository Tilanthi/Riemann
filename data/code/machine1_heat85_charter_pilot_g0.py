#!/usr/bin/env python3
"""heat85 — CHARTER MECHANISM-1, GENERATION ZERO: the survivor-ridge mutant cloud.

Prereg = m1-L168 (frozen BEFORE any mutant cell was computed). This is the pilot the
disruption charter (m1-L166 §4) commits to: one generation of mutations over the
census's surviving configuration space — the 9 M64 survivors and the k=16/k=17
inversion-knife neighbourhood — with falsifiable predictions that can lose, named
JSON keys per #123, and the adversarial control as launch gate (the 94d9e4f
condition: known-firing population members the engine must kill, plus a
defect-injected solve the evaluator must catch, before any mutant is scored).

Instrument: EXACTLY the census instrument — this file imports the sealed heat78c
runner byte-identical (sha256 verified at startup), reuses its Instrument class and
input seals, and changes nothing about the kernel path:
    K_S = K_T200 - gram(z_k) - gram(z_{k+1}) + quad_ex(g, delta),
    g = z_k + phi*(z_{k+1} - z_k),  verdict FIRES iff lam_min < -1e-12.  M = 64 only.

Population (frozen):
  founders_survive (9): (16,0.05) (18,0.05) (19,0.05) (20,0.05) (21,0.05) (22,0.05)
                        (23,0.05) (24,0.05) (24,0.1)
  founders_fire    (3): (15,0.05) (17,0.05) (0,0.1)     <- the kill-controls
  mutants (31): k in {16,18..24} x delta in {0.04, 0.06, 0.07}        (24 cells)
                (17, 0.04)                                            (1)
                (25, 0.05)                                            (1)
                (24, 0.09) (24, 0.11) (24, 0.12) (23, 0.1) (25, 0.1)  (5)

Gate (all must pass BEFORE any mutant is scored; failure = abort, outcome RED):
  G1  controls k=0..7 @ delta=0 at M64: none fires (census discipline);
  G2  every founder reproduces the census lam_min to rel <= 1e-9 AND the same
      fires-bit (reads data/heat78c_census_result.json, sha256 verified);
  G3  the three kill-controls FIRE (the engine kills the known-defective members);
  G4  defect injection: (16,0.05) re-solved with gram(z_{k+1}) DROPPED must
      disagree with the census value by rel > 1e3 — an evaluator that cannot fail
      is blind (#118).

Output JSON keys the grader reads (named here and in the prereg; #123):
  gate.controls_status          "GREEN" | "RED"
  gate.founders["{k}/{d}"]      {lam, census_lam, rel, fires, match}
  gate.defect_injection         {lam_bad, rel_vs_census, detected}
  cells["{k}/{d}"]              {lam_min, fires}          mutants + founders
  wall_seconds
The grader (machine1_heat85_grade.py, sha256 frozen in the prereg) transcribes the
frozen thresholds ONCE and prints them beside every verdict. No verdict is computed
inside this runner.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import machine1_heat78c_survivor_census as census  # noqa: E402  (sealed, verified below)
from mpmath import mp, mpf, mpim, zetazero  # noqa: E402

mp.dps = 45
THRESH = mpf("-1e-12")
T0 = time.time()

CENSUS_RUNNER_SHA = "88ab08f82fc8d14453dc064ba292dd35dc57541a5acc45f0d0bf10cd2721cd53"
CENSUS_JSON = os.path.join(HERE, "..", "heat78c_census_result.json")
CENSUS_JSON_SHA = "3d2f1d7a771a689d460f8e6994b98a8458c5ca8825f06f6f805c7a14393cc920"
OUTJ = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat85_charter_pilot_g0.json"

FOUNDERS_S = [(16, "0.05"), (18, "0.05"), (19, "0.05"), (20, "0.05"), (21, "0.05"),
              (22, "0.05"), (23, "0.05"), (24, "0.05"), (24, "0.1")]
FOUNDERS_F = [(15, "0.05"), (17, "0.05"), (0, "0.1")]
MUTANTS = ([(k, d) for k in (16, 18, 19, 20, 21, 22, 23, 24) for d in ("0.04", "0.06", "0.07")]
           + [(17, "0.04"), (25, "0.05")]
           + [(24, "0.09"), (24, "0.11"), (24, "0.12"), (23, "0.1"), (25, "0.1")])


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    # --- seal layer: census runner byte-identity + census result JSON + 3 frozen inputs
    got = sha(os.path.join(HERE, "machine1_heat78c_survivor_census.py"))
    if got != CENSUS_RUNNER_SHA:
        sys.exit("SEAL FAIL census runner %s" % got)
    got = sha(os.path.normpath(CENSUS_JSON))
    if got != CENSUS_JSON_SHA:
        sys.exit("SEAL FAIL census result json %s" % got)
    census.check_seals()  # the 3 frozen inputs (GEN/IDT/K64), aborts on mismatch
    cj = json.load(open(os.path.normpath(CENSUS_JSON)))["results"]

    # --- instrument: exactly the census M64 instrument
    gdata = json.load(open(census.GEN))["genomes"]
    k64 = json.load(open(census.K64))
    M = 64
    genomes = gdata["s1/M64"]
    phis, edges = zip(*[census.make_phi(g) for g in genomes])
    K = mp.matrix(M, M)
    G = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            K[i, j] = mpf(k64["K_T200"][i][j])
            G[i, j] = mpf(k64["G_raw"][i][j])
    inst = census.Instrument(M, K, G, phis, edges)
    print("instrument built %.1fs" % (time.time() - T0), flush=True)

    zeros = [mpf(str(mpim(zetazero(n)))) for n in range(1, 28)]  # 27: k=25 needs zeros[26]

    def g_of(k, phi8=4):
        return zeros[k] + (zeros[k + 1] - zeros[k]) * mpf(phi8) / 8

    def solve(k, dstr, drop_second_gram=False):
        if drop_second_gram:  # G4 defect injection only
            KS = inst.K - inst.gram(zeros[k]) + inst.quad_ex(g_of(k), mpf(dstr))
        else:
            KS = inst.K - inst.gram(zeros[k]) - inst.gram(zeros[k + 1]) + inst.quad_ex(g_of(k), mpf(dstr))
        vals, _ = inst.eig(KS)
        return vals[0]

    # ---------------- G1: controls ----------------
    red = False
    ctl = {}
    for k in range(8):
        lam = solve(k, "0")
        fires = lam < THRESH
        ctl[str(k)] = {"lam_min": mp.nstr(lam, 25), "fires": bool(fires)}
        if fires:
            red = True
        print("G1 control k=%d lam %s %s" % (k, mp.nstr(lam, 12), "FIRES-RED" if fires else "ok"), flush=True)
    gate = {"controls_status": "RED" if red else "GREEN"}
    if red:
        json.dump({"gate": gate, "aborted": "G1 controls RED", "wall_seconds": time.time() - T0},
                  open(OUTJ, "w"), indent=1)
        sys.exit("G1 FAIL — nothing scored")

    # ---------------- G2/G3: founders vs census ----------------
    found = {}
    g2ok, g3ok = True, True
    for (k, d) in FOUNDERS_S + FOUNDERS_F:
        lam = solve(k, d)
        ref = mpf(cj["64/%d/4/%s" % (k, d)]["lam_min"])
        rel = abs(lam - ref) / abs(ref)
        fires = lam < THRESH
        match = (rel <= mpf("1e-9")) and (fires == cj["64/%d/4/%s" % (k, d)]["fires"])
        if not match:
            g2ok = False
        if (k, d) in FOUNDERS_F and not fires:
            g3ok = False
        found["%d/%s" % (k, d)] = {"lam": mp.nstr(lam, 25), "census_lam": mp.nstr(ref, 25),
                                   "rel": mp.nstr(rel, 4), "fires": bool(fires), "match": bool(match)}
        print("G2/3 founder %d/%s lam %s rel %s fires=%s match=%s"
              % (k, d, mp.nstr(lam, 10), mp.nstr(rel, 3), fires, match), flush=True)
    gate["founders"] = found
    gate["G2_founders_reproduced"] = g2ok
    gate["G3_kill_controls_fired"] = g3ok

    # ---------------- G4: defect injection ----------------
    lam_bad = solve(16, "0.05", drop_second_gram=True)
    ref = mpf(cj["64/16/4/0.05"]["lam_min"])
    rel_bad = abs(lam_bad - ref) / fabs(ref)
    detected = rel_bad > mpf("1e3")
    gate["defect_injection"] = {"lam_bad": mp.nstr(lam_bad, 25), "rel_vs_census": mp.nstr(rel_bad, 4),
                                "detected": bool(detected)}
    print("G4 defect injection rel %s detected=%s" % (mp.nstr(rel_bad, 4), detected), flush=True)

    if not (g2ok and g3ok and detected):
        json.dump({"gate": gate, "aborted": "gate failure (G2/G3/G4)", "wall_seconds": time.time() - T0},
                  open(OUTJ, "w"), indent=1)
        sys.exit("GATE FAIL — no mutant scored")

    # ---------------- the mutant cloud ----------------
    cells = {}
    todo = list(dict.fromkeys(MUTANTS))  # dedupe, keep order
    for n, (k, d) in enumerate(todo, 1):
        lam = solve(k, d)
        cells["%d/%s" % (k, d)] = {"lam_min": mp.nstr(lam, 25), "fires": bool(lam < THRESH)}
        print("mutant %2d/%d  %2d/%s  lam %s  %s" % (n, len(todo), k, d, mp.nstr(lam, 12),
                                                     "FIRES" if lam < THRESH else "survives"), flush=True)
    # founders also carried in cells for grader convenience (fresh values, gate-matched)
    for (k, d) in FOUNDERS_S:
        cells["%d/%s" % (k, d)] = {"lam_min": found["%d/%s" % (k, d)]["lam"], "fires": found["%d/%s" % (k, d)]["fires"]}

    json.dump({"gate": gate, "cells": cells, "n_mutants": len(todo), "wall_seconds": time.time() - T0},
              open(OUTJ, "w"), indent=1)
    print("WROTE %s  (%d mutants, %.1fs)" % (OUTJ, len(todo), time.time() - T0), flush=True)


if __name__ == "__main__":
    main()
