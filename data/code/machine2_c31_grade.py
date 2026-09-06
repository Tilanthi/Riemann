"""machine2 CYCLE 31 -- GRADER.  Hashed and published BEFORE the runner is executed.

Reads m2_c31_scored.json and applies the prereg's pre-stated bands with no judgement.
Emits m2_c31_verdicts.json.
"""
import json
import os

import mpmath as mp

mp.mp.dps = 60

T1 = mp.mpf("1.8908475e-16")
T3 = mp.mpf("1.128194e-9")
BAND_B_LO = mp.mpf("1.0e-15")
BAND_B_HI = mp.mpf("2.2e-15")
MARGIN = "8.63843"

here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, "m2_c31_scored.json")))

v = {"prereg_sha256_from_runner": d.get("prereg_sha256"),
     "runner_sha256_from_runner": d.get("runner_sha256"),
     "margin_published_with_verdict": MARGIN}

gate = d.get("gate", {})
allpass = gate.get("ALL_PASS", False)
v["gate_all_pass"] = bool(allpass)
if not allpass:
    v["V1_verdict"] = "VOID -- launch gate failed"
    v["V2_verdict"] = "VOID -- launch gate failed"
    json.dump(v, open(os.path.join(here, "m2_c31_verdicts.json"), "w"), indent=1)
    print(json.dumps(v, indent=1))
    raise SystemExit(0)

c0 = mp.mpf(d["V1"]["c0_new_six_rungs_alone"])
if abs(c0) <= T1:
    band = "A_CONFIRMED_OUT_OF_SAMPLE"
elif BAND_B_LO <= c0 <= BAND_B_HI:
    band = "B_REFUTED_CORRECTION_ABSENT"
else:
    band = "C_REFUTED_FORM_WRONG"
v["V1_c0_new"] = d["V1"]["c0_new_six_rungs_alone"]
v["V1_T1"] = str(T1)
v["V1_verdict"] = band

dev3 = mp.mpf(d["V2"]["dev"])
v["V2_a3_dev"] = d["V2"]["dev"]
v["V2_verdict"] = "HELD" if dev3 <= T3 else "FALSIFIED"

v["V3_per_rung_within_T2"] = {k: r["within_T2"] for k, r in d.get("rungs", {}).items()}
v["one_determination"] = ("V1 and V2 were declared ONE determination at freeze; if both move "
                          "they are reported as ONE finding, not two.")
json.dump(v, open(os.path.join(here, "m2_c31_verdicts.json"), "w"), indent=1)
print(json.dumps(v, indent=1))
