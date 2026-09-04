"""machine 2 (beast-atlas) -- cycle 20 -- the PARAMETER-FREE ZERO-SUM PREDICTOR.

Located at primary AFTER the measurements (so: post-hoc as a test, but the FORM is not ours):
Burnol, Adv. Math. 170 (2002) 56-70 = arXiv:math/0103058, Theorem 1.4 and Note 2.2, and
Baez-Duarte, Balazard, Landreau, Saias, Adv. Math. 149 (2000) 130-144, Theorem 1.2.

Burnol's Note 2.2, verbatim, in the unit-disc model: "In case Q(z) has a root in the open unit disc
then E(N) is bounded below by a positive constant.  In case Q(z) has all its roots outside the open
unit disc, then the result above holds but only the roots ON the unit circle contribute.  Finally if
all its roots are outside the closed unit disc then the decrease is exponential."
And his Theorem 1.4: lim N E(N,P) = sum_alpha m_alpha^2 |P(alpha)|^2 -- the approximation error is
the WEIGHT EVALUATED AT THE ZEROS.

Half-plane analogue used here as a predictor, with NO fitted parameter:

    Pred  =  sum_{rho on the critical line}  m_rho^2 |W(rho)|^2  /  ||1||^2 ,   capped at 1.

The cap is not a fudge: d^2 <= ||1||^2 always (take g = 0), while the asymptotic form carries a
1/log N that we cannot reach at N <= 56, so any predicted value above 1 only says "saturated".
"""
import json, sys
from mpmath import mp, mpf, mpc, findroot, nstr

sys.path.insert(0, '.')
from machine2_cycle20_carriers import CARRIERS, carrier_eval

mp.dps = 25
TMAX = 30
STEP = mpf('0.02')


def zeros_on_line(key, tmax=TMAX):
    """Locate zeros of F on Re s = 1/2 with 0 < t <= tmax, by scanning |F| for local minima and
    refining with a complex Newton solve; a candidate is accepted only if the refined root has
    |Re s - 1/2| < 1e-12 (so an off-line zero is NOT silently counted as an on-line one)."""
    ts, vals = [], []
    t = mpf('0.01')
    while t <= tmax:
        ts.append(t)
        vals.append(abs(carrier_eval(key, mpc(mpf(1) / 2, t))))
        t += STEP
    out, offline = [], []
    for i in range(1, len(ts) - 1):
        if vals[i] < vals[i - 1] and vals[i] < vals[i + 1] and vals[i] < 1:
            try:
                r = findroot(lambda z: carrier_eval(key, z), mpc(mpf(1) / 2, ts[i]),
                             tol=mpf('1e-30'))
            except Exception:
                continue
            if abs(mp.im(r)) < mpf('0.001') or mp.im(r) < 0:
                continue
            if any(abs(mp.im(r) - mp.im(z)) < mpf('1e-6') for z in out + offline):
                continue
            if abs(mp.re(r) - mpf(1) / 2) < mpf('1e-12'):
                out.append(r)
            else:
                offline.append(r)
    return sorted(out, key=lambda z: mp.im(z)), sorted(offline, key=lambda z: mp.im(z))


def W2(s):
    return 1 / (s * (s + 1))


def main():
    meas = json.load(open("machine2_cycle20_mainW2.json"))
    m48 = {r["carrier"]: r["rel_con"] for r in meas["runs"] if r["N"] == 48}
    out = {"TMAX": TMAX, "rows": []}
    for key in list(CARRIERS)[:10]:
        zs, off = zeros_on_line(key)
        pred = sum(abs(W2(z)) ** 2 for z in zs) / (mpf(1) / 3)
        row = {"carrier": key, "label": CARRIERS[key][0],
               "n_online_zeros_below_%d" % TMAX: len(zs),
               "first_online_zero_t": nstr(mp.im(zs[0]), 12) if zs else None,
               "offline_or_unrefined_found": [nstr(z, 10) for z in off],
               "pred_zero_sum": float(pred), "pred_capped": float(min(pred, mpf(1))),
               "measured_rel_con_N48": m48[key]}
        row["ratio_pred_over_meas"] = row["pred_capped"] / m48[key]
        out["rows"].append(row)
        print(f"{key:22s} first zero t={row['first_online_zero_t']} "
              f"n={len(zs)} pred={row['pred_capped']:.4g} meas={m48[key]:.4g} "
              f"ratio={row['ratio_pred_over_meas']:.3g}", flush=True)
    json.dump(out, open("machine2_cycle20_zerosum.json", "w"), indent=1)


if __name__ == "__main__":
    main()
