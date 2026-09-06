"""machine2 CYCLE 30 -- GRADER.  Written and hashed BEFORE the scored run (#123 / m1 ask 5).

Grades ONLY the JSON keys named in m2_c30_prereg.json
(sha256 a0d6b65b85e490b5854e6b0e87c47a706bb4de1ab6316222d64c5d68d64818f0).
Conventions A-E of the prereg are transcribed here once and printed beside each verdict.
Anything the runner prints that is not a named key is NOT the graded statistic.
"""
import json
import sys

from mpmath import mp

mp.dps = 60
PREREG_SHA = "a0d6b65b85e490b5854e6b0e87c47a706bb4de1ab6316222d64c5d68d64818f0"
NEW_EPS = ["0.0001", "0.00015", "0.00022", "0.00033", "0.0005", "0.00075"]


def boundary(val, thr):
    """Convention B: within rel 1e-3 of the threshold -> BOUNDARY flag (not verdict-changing)."""
    thr = mp.mpf(thr)
    if thr == 0:
        return False
    return abs(mp.mpf(val) - thr) / abs(thr) < mp.mpf("1e-3")


def main():
    d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "m2_c30_scored.json"))
    print("=== m2 CYCLE 30 GRADER === prereg sha256 %s" % PREREG_SHA)

    if not d.get("gate", {}).get("ALL_PASS"):
        print("GATE FAILED -> all five hypotheses UNGRADED (convention D). Outcome RED.")
        return

    print("GATE: G1 %s  G2 %s  G3 %s  G4 %s" % tuple(
        "PASS" if d["gate"][k]["pass"] else "FAIL" for k in ("G1", "G2", "G3", "G4")))
    verdicts = {}

    # ---- Q1: max over the six named dev_K6_extrap keys <= 2e-8
    devs = {e: mp.mpf(d["rungs"][e]["dev_K6_extrap"]) for e in NEW_EPS}
    q1v = max(devs.values())
    verdicts["Q1"] = {"stat": "max dev_K6_extrap", "value": mp.nstr(q1v, 10),
                      "threshold": "<= 2e-8", "held": bool(q1v <= mp.mpf("2e-8")),
                      "boundary": boundary(q1v, "2e-8"),
                      "per_rung": {e: mp.nstr(v, 8) for e, v in devs.items()}}

    # ---- Q2: fit17/loo_optimal_K == 6
    k17 = d["fit17"]["loo_optimal_K"]
    verdicts["Q2"] = {"stat": "fit17/loo_optimal_K", "value": k17, "threshold": "== 6",
                      "held": bool(k17 == 6), "boundary": False}

    # ---- Q3: |a3 shift| <= 1e-8
    q3v = mp.mpf(d["fit17"]["a3_shift_abs"])
    verdicts["Q3"] = {"stat": "fit17/a3_shift_abs", "value": mp.nstr(q3v, 10),
                      "threshold": "<= 1e-8", "held": bool(q3v <= mp.mpf("1e-8")),
                      "boundary": boundary(q3v, "1e-8")}

    # ---- Q4: 17-rung a3 spread over K=6,7,8 strictly < 3.4931094e-9
    q4v = mp.mpf(d["fit17"]["a3_spread_K6to8"])
    verdicts["Q4"] = {"stat": "fit17/a3_spread_K6to8", "value": mp.nstr(q4v, 10),
                      "threshold": "< 3.4931094e-9", "held": bool(q4v < mp.mpf("3.4931094e-9")),
                      "boundary": boundary(q4v, "3.4931094e-9")}

    # ---- Q5: loo_rms_half >= loo_rms_base  (no improvement from a half power)
    base = mp.mpf(d["fit17"]["loo_rms_base"])
    half = mp.mpf(d["fit17"]["loo_rms_half"])
    verdicts["Q5"] = {"stat": "fit17/loo_rms_half vs loo_rms_base",
                      "value": "half=%s base=%s ratio=%s" % (mp.nstr(half, 8), mp.nstr(base, 8),
                                                             mp.nstr(half / base, 8)),
                      "threshold": "half >= base", "held": bool(half >= base),
                      "boundary": boundary(half, base)}

    for k in ("Q1", "Q2", "Q3", "Q4", "Q5"):
        v = verdicts[k]
        print("%-3s %-10s  %-46s  thr %-22s %s%s" % (
            k, "HELD" if v["held"] else "FALSIFIED", str(v["value"])[:46], v["threshold"],
            "", "  [BOUNDARY]" if v.get("boundary") else ""))

    held = [k for k in verdicts if verdicts[k]["held"]]
    fals = [k for k in verdicts if not verdicts[k]["held"]]
    print("\nTALLY %d HELD / %d FALSIFIED : held=%s falsified=%s"
          % (len(held), len(fals), sorted(held), sorted(fals)))
    # #122 deflation, transcribed from the prereg's own reason clustering
    if "Q1" in fals and "Q5" in fals:
        print("#122 DEFLATION: Q1 and Q5 share the ANALYTICITY reason (declared at freeze). "
              "Both failing is ONE determination, not two -> effective determinations = %d"
              % (len(verdicts) - 1))
    else:
        print("#122: Q1/Q5 share the analyticity reason; they did not fail together, "
              "so no deflation applies to this tally.")

    c1 = mp.mpf(d["control"]["C1_min_shift_over_small_rungs"])
    print("CONTROL C1 (declared EMPTY-BY-ALGEBRA firing world, NOT in the tally): "
          "min shift %s vs >= 1e-8 -> %s" % (mp.nstr(c1, 8), "as designed" if c1 >= mp.mpf("1e-8")
                                             else "FIRED (implementation defect)"))

    json.dump({"verdicts": verdicts, "tally": {"held": sorted(held), "falsified": sorted(fals)}},
              open("m2_c30_verdicts.json", "w"), indent=1)
    print("wrote m2_c30_verdicts.json")


if __name__ == "__main__":
    main()
