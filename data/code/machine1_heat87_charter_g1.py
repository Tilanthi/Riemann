#!/usr/bin/env python3
"""heat87 — CHARTER MECHANISM-1, GENERATION ONE (gen-1 breeding).

Prereg = m1-PREREG-heat87 (frozen BEFORE any gen-1 cell is computed; this file's
sha256 and the grader's sha256 are printed in that letter). Direct child of the
heat85 g0 runner (launch-4 seal 13d34a17..., gates 4/4 GREEN, scored 0 HELD /
4 FIRED-AGAINST-m1 in m1-L176): same census instrument, same seals, same gate
structure G1-G4 (G4 threshold 0.1 as amended pre-data at re-freeze-3, #144 --
no new guesses, the measured defect size rel 0.4872 is on the record).  The
ONLY substantive change is the panel: MUTANTS below.  Breeder: m1 (Mac,
Claude Code).  GEN-1-BOUNDARY token: this run sits at the gen-0 -> gen-1
boundary; every m1 commit in the boundary window carries the token
GEN-1-BOUNDARY + breeder authorship + a data/ artefact (m2 AMENDMENT 1 /
my 99804c note, superseding my L175 section-6 wording; third bearer of the
token at prereg time -- counted per #145: two prior commit-message instances).

What gen-1 tests (full statement in the prereg letter; bands derived by
machine1_heat87_g1_band_derivation.py from the PUBLIC gen-0 panel only):

  L1 (the registered extrapolator): on the pre-crossing segment, adjacent
  differences accelerate geometrically, rho(k) estimated from the last two
  equal-spacing differences, band rho/1.3 .. rho*1.3.  18/18 gen-0 triples
  accelerate -- the law is consistent with everything measured so far.

  P1 (held-out, k=19/20/21 -- never span-marked): delta*(19) in (0.070,0.085],
  delta*(20) in (0.070,0.095], delta*(21) in (0.090,0.130].  Conjunctive.
  P2 (responsive brackets): delta*(16) in (0.050,0.053], delta*(18) in
  (0.050,0.054], delta*(23) in (0.070,0.092].  Conjunctive.
  P3 (collimation head-to-head): at least one of k=22 (by 0.19), k=24 (by
  0.19), k=25 (by 0.20) fires.  m2's span-collapse reading says none ever
  fires; L1 says all three do (centers 0.14/0.17/0.17).
  P4 (the law): every NEW equal-spacing triple in the merged panel
  accelerates (second difference < 0).  18 new triples, enumerated in the
  grader.

Population (frozen; per-k delta-windows per m2's c35 section-7 span table as
adopted in m1-L176 section 7 -- per-k, NOT global):
  k=16: 0.0505 0.0515 0.053        (bracket: linear point 0.050145)
  k=18: 0.0510 0.0525 0.0540       (bracket: linear point 0.051200)
  k=19: 0.075 0.080 0.085          (held-out)
  k=20: 0.080 0.090 0.095          (held-out)
  k=21: 0.09 0.10 0.11 0.12 0.13   (held-out; the discriminator vs collimation)
  k=22: 0.13 0.15 0.17 0.19        (collimation head-to-head)
  k=23: 0.076 0.080 0.084 0.088 0.092 (bracket: linear point 0.082644)
  k=24: 0.15 0.16 0.17 0.18 0.19   (collimation head-to-head)
  k=25: 0.15 0.16 0.17 0.18 0.19 0.20 (WEAKEST anchor: 2-point, rho assumed)
                                                        = 37 mutant cells

Gate (identical to g0 launch-4; failure = abort, outcome RED, nothing scored):
  G1 controls k=0..7 @ delta=0 at M64: none fires;
  G2 the 12 founders reproduce the census lam_min to rel <= 1e-9 AND fires-bit;
  G3 the three kill-controls FIRE;
  G4 defect injection at (16,0.05) with gram(z_{k+1}) dropped: rel > 0.1.

Output JSON keys the grader reads (#123; same schema as g0):
  gate.controls_status / gate.founders / gate.G2_founders_reproduced /
  gate.G3_kill_controls_fired / gate.defect_injection.detected /
  cells["{k}/{d}"].lam_min, .fires / n_mutants / wall_seconds
The grader (machine1_heat87_grade.py) transcribes the frozen thresholds ONCE
and prints them beside every verdict.  No verdict is computed inside this
runner.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import machine1_heat78c_survivor_census as census  # noqa: E402  (sealed, verified below)
from mpmath import mp, mpf, zetazero  # noqa: E402

mp.dps = 45
THRESH = mpf("-1e-12")
T0 = time.time()

CENSUS_RUNNER_SHA = "88ab08f82fc8d14453dc064ba292dd35dc57541a5acc45f0d0bf10cd2721cd53"
CENSUS_JSON = os.path.join(HERE, "..", "heat78c_census_result.json")
CENSUS_JSON_SHA = "3d2f1d7a771a689d460f8e6994b98a8458c5ca8825f06f6f805c7a14393cc920"
OUTJ = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat87_charter_g1.json"

FOUNDERS_S = [(16, "0.05"), (18, "0.05"), (19, "0.05"), (20, "0.05"), (21, "0.05"),
              (22, "0.05"), (23, "0.05"), (24, "0.05"), (24, "0.1")]
FOUNDERS_F = [(15, "0.05"), (17, "0.05"), (0, "0.1")]
MUTANTS = ([(16, d) for d in ("0.0505", "0.0515", "0.053")]
           + [(18, d) for d in ("0.0510", "0.0525", "0.0540")]
           + [(19, d) for d in ("0.075", "0.080", "0.085")]
           + [(20, d) for d in ("0.080", "0.090", "0.095")]
           + [(21, d) for d in ("0.09", "0.10", "0.11", "0.12", "0.13")]
           + [(22, d) for d in ("0.13", "0.15", "0.17", "0.19")]
           + [(23, d) for d in ("0.076", "0.080", "0.084", "0.088", "0.092")]
           + [(24, d) for d in ("0.15", "0.16", "0.17", "0.18", "0.19")]
           + [(25, d) for d in ("0.15", "0.16", "0.17", "0.18", "0.19", "0.20")])


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

    zeros = [mpf(str(zetazero(n).imag)) for n in range(1, 28)]  # 27: k=25 needs zeros[26]

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

    # ---------------- G4: defect injection (threshold 0.1, inherited from
    # g0 re-freeze-3 -- the MEASURED defect size is rel 0.4872, #144) --------
    lam_bad = solve(16, "0.05", drop_second_gram=True)
    ref = mpf(cj["64/16/4/0.05"]["lam_min"])
    rel_bad = abs(lam_bad - ref) / abs(ref)
    detected = rel_bad > mpf("0.1")
    gate["defect_injection"] = {"lam_bad": mp.nstr(lam_bad, 25), "rel_vs_census": mp.nstr(rel_bad, 4),
                                "threshold_as_run": "0.1 (inherited from g0 re-freeze-3, #144)",
                                "detected": bool(detected)}
    print("G4 defect injection rel %s (thresh 0.1, inherited) detected=%s"
          % (mp.nstr(rel_bad, 4), detected), flush=True)

    if not (g2ok and g3ok and detected):
        json.dump({"gate": gate, "aborted": "gate failure (G2/G3/G4)", "wall_seconds": time.time() - T0},
                  open(OUTJ, "w"), indent=1)
        sys.exit("GATE FAIL — no mutant scored")

    # ---------------- the gen-1 mutant panel ----------------
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
