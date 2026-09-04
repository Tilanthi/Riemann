"""E1 cross-check at the precision E1's OWN cancellation demands.
E1 forms pi^{-s}Gamma(s)*2*zeta2 from terms of size O(1/|s|) while |Gamma(s)| ~ e^{-pi t/2}:
predicted digits lost = pi*t/(2 ln 10) = 0.6822 t.  So dps must EXCEED 0.6822 t + working digits.
This is a prediction made before the run and checked against it."""
import json, math
from mpmath import mp, mpf, mpc, fabs, nstr
import eval2, epstein_fold as e1

zs = json.load(open("zeros_verified.json"))
print("%-28s %-8s %-7s %-13s %-13s" % ("zero s0 (Im)", "pred dps", "used", "|F| on E1", "verdict"))
rows = []
for z in zs:
    t = float(z['im'])
    pred = 0.6822 * t
    dps = int(pred) + 45
    mp.dps = dps + 10
    s0 = mpc(mpf(z['re']), mpf(z['im']))
    e1.set_cut(dps + 10)
    v = e1.zeta2(s0, mpf(1) / 7) * mpf(49) ** (-s0)
    r = float(fabs(v))
    ok = "PASS" if r < 1e-25 else "FAIL"
    print("%-28s %-8.1f %-7d %-13.3e %-13s" % (nstr(mp.im(s0), 12), pred, dps, r, ok))
    rows.append(dict(im=z['im'], pred_digits_lost=pred, dps_used=dps, residual_E1=r, verdict=ok))
json.dump(rows, open("e1_recheck.json", "w"), indent=1)
print("\n  %d/%d zeros confirmed on E1 at adequate precision (implementation-independent," % (sum(1 for r in rows if r['verdict']=='PASS'), len(rows)))
print("   ANCESTRY-SHARED: E1 and E2 both descend from the Jacobi theta transformation).")
