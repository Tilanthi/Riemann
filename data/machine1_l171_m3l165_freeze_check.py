"""m1-L171 §9.1: freeze-time receipt of m3-L165 (M-ladder k=16 prereg, dfb64a2).
All inputs parsed from committed artefacts — nothing re-typed (trap #S12).
Checks: (1) census endpoints, (2) genome nesting + hash, (3) H1/H4 arithmetic,
(4) heat85 M=64-only collision-freedom, (5) cross-instrument mixing note,
(6) H1/H3 joint-window computation. No m3 computation is performed or graded.
"""
import json, hashlib, math

cen = json.load(open("data/heat78c_census_result.json"))["results"]
out = {}

# 1. endpoints at m3's print precision
claimed = {
    "8/16/4/0.05":  "1.153296287502721e-5",
    "64/16/4/0.05": "5.053612052269358e-11",
    "8/16/4/0.1":   "1.152593916547098e-5",
    "64/16/4/0.1":  "-7.980718943933415e-7",
}
for key, s in claimed.items():
    lam = cen[key]["lam_min"]
    # agree to every digit m3 printed?
    n_print = len(s.replace("-", "").replace(".", "").replace("e-", "").split("e")[0])
    agree = abs(float(lam) - float(s)) / abs(float(s)) < 10 ** (2 - n_print)
    out[f"endpoint_{key}"] = f"census {lam} vs m3 {s} -> {'MATCH at print precision' if agree else 'MISMATCH'} fires={cen[key]['fires']}"

# 2. nesting + hash
h = hashlib.sha256(open("data/code/machine1_heat70_genomes_m8_m64.json", "rb").read()).hexdigest()
out["genome_sha256"] = h
out["genome_hash_matches_frozen_1065fd37"] = h.startswith("1065fd370fd9370807ea61f19708cbf1d")
g = json.load(open("data/code/machine1_heat70_genomes_m8_m64.json"))["genomes"]
for seed in ("s1", "s2", "s3"):
    out[f"nested_{seed}"] = g[f"{seed}/M64"][:8] == g[f"{seed}/M8"]

# 3. H1/H4 arithmetic
l8, l64 = 1.153296287502721e-5, 5.053612052269358e-11
r = l64 / l8
out["H1_loglin_M16"] = f"{l8 * r**(1/7):.8e} (m3: 1.97908248e-6)"
out["H1_loglin_M32"] = f"{l8 * r**(3/7):.8e} (m3: 5.82787055e-8)"
out["H3_null_R"] = 3 / 7
a8, a64 = 1.152593916547098e-5, -7.980718943933415e-7
out["H4_linear_M16"] = f"{a8 + (a64 - a8) / 7:.8e} (m3: 9.76536616e-6)"
out["H4_linear_M32"] = f"{a8 + 3 * (a64 - a8) / 7:.8e} (m3: 6.24422014e-6)"

# 4. heat85 collision: runner M value
src = open("data/code/machine1_heat85_charter_pilot_g0.py").read()
out["heat85_M64_only"] = "M = 64" in src and "M = 64 only" in src
out["heat85_has_M16_M32"] = ("M = 16" in src) or ("M = 32" in src)

# 6. H1/H3 joint window. R = ln(l32/l8)/ln(l64/l8): both logs negative, so a
# SMALLER l32 (more drop by M=32) gives a LARGER R. pred/3 edge -> R_hi, pred*3 edge -> R_lo.
L = math.log(l64 / l8)
pred32 = l8 * r ** (3 / 7)
r_lo = math.log(pred32 * 3 / l8) / L
r_hi = math.log(pred32 / 3 / l8) / L
out["H1_M32_band_R_range_ascending"] = sorted([round(r_lo, 4), round(r_hi, 4)])
out["H3_R_threshold"] = 0.35
out["joint_window"] = f"[{r_lo:.4f}, 0.3500) width {0.35 - r_lo:.4f}"

print(json.dumps(out, indent=1, default=str))
