"""Pre-registration power analysis for the gen-1 role comparison (frozen with the prereg).

Cluster unit = FILE (lines within one letter are not independent).  Cluster bootstrap on the
gen-0 baseline gives the sampling SD of each metric for an arm of n_files letters; the MDE is
the two-sided alpha=0.05, 80%-power detectable difference for gen-0 (as observed) vs a gen-1
arm of n1 letters.
"""
import random, math, sys, statistics as st
sys.path.insert(0, "/workspace/rh/cycle33")
from m2_c33_role_census import census, metrics
from collections import Counter

REPO = "/shared/rh-exchange-repo/Riemann"
random.seed(20260906)

files, excl, per_file, tot = census(REPO, "53a3b46", None)
pf = [(p, o, c) for p, o, c in per_file]
print(f"baseline files={len(pf)}")

def pooled(sel):
    c = Counter()
    for _, _, fc in sel:
        c.update(fc)
    return c

def boot_sd(n_files, key, B=4000):
    vals = []
    for _ in range(B):
        sel = [random.choice(pf) for _ in range(n_files)]
        m = metrics(pooled(sel), "U-DROP")
        v = m[key]
        if v == v:
            vals.append(v)
    return st.pstdev(vals), st.mean(vals)

obs = metrics(pooled(pf), "U-DROP")
print("observed pooled (U-DROP):", {k: round(v, 4) for k, v in obs.items() if isinstance(v, float)})
sw = metrics(pooled(pf), "U-DROP")["M2_cross_share"], metrics(pooled(pf), "U-SELF")["M2_cross_share"], metrics(pooled(pf), "U-SPLIT")["M2_cross_share"]
print(f"M2 convention swing (U-DROP/U-SELF/U-SPLIT) = {sw}  swing={max(sw)-min(sw):.4f}")

n0 = len(pf)
for n1 in [9, 12, 15, 20]:
    print(f"\n-- gen-1 arm of n1={n1} letters (gen-0 arm n0={n0}) --")
    for key in ["M1_explicit_rate", "M2_cross_share", "M3_density_per_kline", "NC_conf_explicit_rate"]:
        sd0, _ = boot_sd(n0, key)
        sd1, _ = boot_sd(n1, key)
        se = math.sqrt(sd0**2 + sd1**2)
        print(f"   {key:24s} obs={obs[key]:8.4f}  SE(diff)={se:7.4f}  MDE(80%,a=.05)={2.802*se:7.4f}")
