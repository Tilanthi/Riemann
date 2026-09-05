"""machine2 cycle25 -- band propagation for the committed prediction.

Reads c25_prereg.json (predictions only, no exact value exists yet) and emits the COMMITTED bands.
Rule adopted from m1-L150 sect3: the halfwidth of a predicted lam value is 2*|ty6 - ty4|, measured
in-house from the next order and from no exact value.  A defect D = shift - s_A - s_B is a signed sum
of THREE predicted lam values (the launch enters exactly, delta = 0, so it carries no band), so its
halfwidth is the SUM of the three halfwidths -- deliberately conservative (no independence assumed
between truncation errors that share an instrument).
"""
import json, os
from mpmath import mp

mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "c25_prereg.json")))
pred = P["prediction"]
lam_launch = {"b": mp.mpf(P["launch"]["lam"]), "bs": mp.mpf(P["launch"]["lam_s"])}
F = P["functionals"]
fmap = {"R2": ("f_a", "f_b"), "R3": ("f_a", "f_b3"), "R3b": ("f_a", "f_b4"), "R4": ("f_as", "f_bs")}
arms = {"R2": ("R0", "R1"), "R3": ("R0", "R1b"), "R3b": ("R0", "R1e"), "R4": ("R0s", "R1d")}
out = {}
print("%-4s %14s %14s %14s %10s %12s %12s" % ("rung", "D_pred", "D_lo", "D_hi", "R_c", "frac%", "frac% band"))
for r in ("R2", "R3", "R3b", "R4"):
    a, b = arms[r]
    site = pred[r]["site"]
    l0 = lam_launch[site]
    sA = mp.mpf(pred[a]["ty4"]) - lam_launch[pred[a]["site"]]
    sB = mp.mpf(pred[b]["ty4"]) - lam_launch[pred[b]["site"]]
    sh = mp.mpf(pred[r]["ty4"]) - l0
    D = sh - sA - sB
    hw = sum(mp.mpf(pred[x]["band_halfwidth"]) for x in (r, a, b))
    fa = abs(mp.mpf(F[fmap[r][0]])); fb = abs(mp.mpf(F[fmap[r][1]]))
    Rc = abs(D) / (fa + fb)
    # relative defect fraction, propagated conservatively (shift band = its own rung halfwidth)
    shw = mp.mpf(pred[r]["band_halfwidth"])
    lo = min(abs((D - hw) / (sh + shw)), abs((D + hw) / (sh - shw)), abs((D - hw) / (sh - shw)),
             abs((D + hw) / (sh + shw)))
    hi = max(abs((D - hw) / (sh + shw)), abs((D + hw) / (sh - shw)), abs((D - hw) / (sh - shw)),
             abs((D + hw) / (sh + shw)))
    out[r] = {"s_A": mp.nstr(sA, 12), "s_B": mp.nstr(sB, 12), "shift": mp.nstr(sh, 12),
              "D": mp.nstr(D, 12), "D_lo": mp.nstr(D - hw, 12), "D_hi": mp.nstr(D + hw, 12),
              "halfwidth": mp.nstr(hw, 8), "R_c": mp.nstr(Rc, 10),
              "R_c_lo": mp.nstr(abs(D - hw) / (fa + fb) if (D - hw) * D > 0 else mp.mpf(0), 10),
              "R_c_hi": mp.nstr(abs(D + hw) / (fa + fb), 10),
              "frac_pct": mp.nstr(100 * abs(D / sh), 8),
              "frac_pct_lo": mp.nstr(100 * lo, 8), "frac_pct_hi": mp.nstr(100 * hi, 8),
              "cross_2nd": P["second_order"][r][2],
              "D_over_cross": mp.nstr(D / mp.mpf(P["second_order"][r][2]), 8)}
    print("%-4s %14s %14s %14s %10s %12s %12s"
          % (r, mp.nstr(D, 6), mp.nstr(D - hw, 6), mp.nstr(D + hw, 6), mp.nstr(Rc, 5),
             mp.nstr(100 * abs(D / sh), 5), "[%s, %s]" % (mp.nstr(100 * lo, 3), mp.nstr(100 * hi, 3))))
ratio = mp.mpf(out["R2"]["frac_pct"]) / mp.mpf(out["R3"]["frac_pct"])
rlo = mp.mpf(out["R2"]["frac_pct_lo"]) / mp.mpf(out["R3"]["frac_pct_hi"])
rhi = mp.mpf(out["R2"]["frac_pct_hi"]) / mp.mpf(out["R3"]["frac_pct_lo"])
out["ratio_R2_over_R3"] = {"pred": mp.nstr(ratio, 8), "lo": mp.nstr(rlo, 8), "hi": mp.nstr(rhi, 8)}
print("\nPRIMARY: (defect fraction at the CANCELLATION rung)/(at the ORDINARY OPPOSING rung)")
print("   ty4 prediction %s   propagated band [%s, %s]" % (mp.nstr(ratio, 6), mp.nstr(rlo, 4), mp.nstr(rhi, 4)))
print("   cycle-23 measured value of the same ratio at site S1: 9.37/7.13 = 1.314")
json.dump(out, open(os.path.join(HERE, "c25_bands.json"), "w"), indent=1)
