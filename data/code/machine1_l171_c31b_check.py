"""m1-L171: independent QR check of m2's c31b scored arithmetic from their published
u literals only (their instrument outputs are NOT recomputed -- this tests the fit
chain on their data, exactly the arithmetic/measurement distinction both sides have
adopted). Conventions identical to machine1_l171_c30_refit.py.
"""
import json
from mpmath import mp, mpf, sqrt

mp.dps = 60

A_CORR = mpf("2.645521411811662855605")   # a_used + delta_a (m2's c30 print)
A_USED = mpf("2.645521411811664489")      # m1 operative (L164 sect5 as corrected)
B_OP = mpf("-7.4624528767937415788")
REF_A3 = mpf("11.70071732105115376305")   # m2's V2 reference literal
DELTA_A = mpf("-1.633394698e-15")

# m2 c31b scored JSON, six new rungs (u at 39-40 s.f.)
RUNGS = [
    ("0.000025", "0.008132816210340134959336068070940762320306"),
    ("0.000035", "0.009623013635025217754974852059278739816048"),
    ("0.00005",  "0.01150194453931563567155676941668683643768"),
    ("0.00007",  "0.01360966821269902887760245528186822810223"),
    ("0.00012",  "0.01782049519407109981636298012442234783656"),
    ("0.00027",  "0.02673639886779683540681680986901007426482"),
]


def r_of(eps, u, a):
    return (u * u - a * eps + B_OP * eps ** 2) / eps ** 3


def lsq(basis, xs, ys):
    Am = mp.matrix(len(xs), len(basis))
    bv = mp.matrix(len(xs), 1)
    for i, (x, y) in enumerate(zip(xs, ys)):
        for j, f in enumerate(basis):
            Am[i, j] = f(x)
        bv[i] = y
    c, _ = mp.qr_solve(Am, bv)
    return [c[j] for j in range(len(basis))]


def poly_basis(k):
    return [lambda e, j=j: e ** j for j in range(k + 1)]


eps = [mpf(e) for e, _ in RUNGS]
u = [mpf(s) for _, s in RUNGS]

r_corr = [r_of(e, ui, A_CORR) for e, ui in zip(eps, u)]
r_used = [r_of(e, ui, A_USED) for e, ui in zip(eps, u)]

out = {}

# cross-check r against their printed r_corrected_a (expect agreement to their print precision)
their_r = ["11.7012292379679054259573", "11.701433995226010888216",
           "11.7017411469155159129492", "11.7021506994400400297881",
           "11.7031746487015136776143", "11.7062470491008034225262"]
for e, mine, theirs in zip(eps, r_corr, their_r):
    rel = abs(mine - mpf(theirs)) / abs(mpf(theirs))
    out[f"r_check_eps{e}"] = f"mine {mp.nstr(mine, 12)} theirs {theirs} rel {mp.nstr(rel, 3)}"

# V1: basis [eps^-2, 1, eps, eps^2, eps^3] on r_corr
b1 = [lambda e: 1 / e ** 2] + poly_basis(3)[0:]
c1 = lsq(b1, eps, r_corr)
out["V1_c0_new"] = mp.nstr(c1[0], 12)
res = max(abs(mp.fsum(f(e) * cj for f, cj in zip(b1, c1)) - rr) for e, rr in zip(eps, r_corr))
out["V1_max_res"] = mp.nstr(res, 9)

# V2: plain K=3 on r_corr -> a3 (constant term)
c2 = lsq(poly_basis(3), eps, r_corr)
a3_new = c2[0]
out["V2_a3_new"] = mp.nstr(a3_new, 22)
out["V2_dev_vs_ref"] = mp.nstr(abs(a3_new - REF_A3), 9)

# transfer coefficient: a3 shift per unit c0 = (a3_plain - a3_with)/c0_new
transfer = (c2[0] - c1[1]) / c1[0]
out["transfer_a3_per_c0"] = mp.nstr(transfer, 12)

# ratios
out["ratio_delta_a_over_c0new"] = mp.nstr(abs(DELTA_A) / abs(c1[0]), 6)
T1 = mpf("1.8908475e-16")
T3 = mpf("1.128194e-9")
out["c0_admitted_by_T3"] = mp.nstr(T3 / abs(transfer), 6)
out["T1_over_T3admits"] = mp.nstr(T1 / (T3 / abs(transfer)), 6)

# diagnostic: same fit on r_used (my operative a) -> their c0_new_with_a_operative
c3 = lsq(b1, eps, r_used)
out["c0_new_with_a_used"] = mp.nstr(c3[0], 13)

# eps^2*dev non-flatness check (their upper-bound argument): signed dev = r_corr - r_pred_frozen_curve
# r_pred from THEIR printed predictions; verify dev_signed prints
pred = ["11.7012292209069374831573", "11.7014339872456960672521",
        "11.7017411436083767352848", "11.7021506982224613571416",
        "11.7031746487627328296939", "11.7062470494235936728743"]
devs = []
for e, mine, p in zip(eps, r_corr, pred):
    devs.append((mine - mpf(p)) * e ** 2)
out["eps2_dev_spread"] = [mp.nstr(d, 4) for d in devs]

print(json.dumps(out, indent=1))
