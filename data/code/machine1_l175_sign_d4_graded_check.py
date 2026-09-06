"""m1 L175 verification battery (runs ~10 min at DPS 55+12).

A. Independent sign calibration for MY fold convention (m2-ERRATUM-17 'live for m1'):
   my L174 fixed the sign of a by comparison with the anchor under audit.  Here the
   side that bears the REAL zero pair is fixed by root find on MY lineage (heat72
   zeta2_C, imported -- never transcribed): D = D*-1e-3 -> real root; D = D*+1e-3 ->
   no real root + on-line ordinate.  Echoed m2 calibration values compared, not consumed.
B. Post-reveal reproduction of ONE graded point: u2_true(eps=0.02) from m2's graded
   run, by my own root find (independent code path, shared D* literal only).
C. The D4 erratum: closing-control residuals of my v3 parsed from the committed
   .stdout; u^2-space fit resid = p*eps^4 + q*eps^5 -> corrected a4 = p + a4_used,
   a5 = q; wrong-coefficient fingerprint receipts (resid/eps^4 constancy, du ~ eps^3.5).
D. Arithmetic verification of m2's graded output (parsed from machine2_c33_oos_graded.out):
   P1 slopes, P3 ratio, and consistency of graded err_3/err_5(0.02) with their
   disclosed 7-coefficient list.

No file writes inside (stdout only; bash redirects).  Nothing scored.
"""
import importlib.util
import os
import re
import sys
import time

from mpmath import mp, mpf, mpc, sqrt, fabs

HERE = os.path.dirname(os.path.abspath(__file__))
DPS = int(os.environ.get("L175_DPS", "55"))
GUARD = int(os.environ.get("L175_GUARD", "12"))
T0 = time.time()
mp.dps = DPS + GUARD

_spec = importlib.util.spec_from_file_location(
    "v3mod", os.path.join(HERE, "machine1_der_route_a_b_a3_v3.py"))
v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v3)
DSTAR = v3.DSTAR
HALF = mpf("0.5")
A17 = mpf("2.6455214118116629")

# ---- echoed counterparty values: compared, never consumed (trap #S12: parse, don't retype;
#      these few are themselves the quote under comparison, printed as such below)
M2_CAL = {"u": mpf("0.0513621518162436"), "u2": mpf("0.00263807064"),
          "u2_line": mpf("-0.00265299559")}
M2_A4 = mpf("-20.4755387553904125007058067226")
M2_A5 = mpf("18.2711625011499510374264312727")
M2_A6 = mpf("-64.5504639041088266572855354966")
M2_A7 = mpf("-94.4010332681698208452798269282")
M2_U2_002 = mpf("0.0500158309334201322927895535832")
A4_USED = mpf("-14725.652175546936039")   # = -D4 as used by v3's closing control (from v3.out)


def f_real(t, D):
    return v3.zeta2_C_deep(HALF + t, D)


def f_line_re(v, D):
    s = mpc(HALF, v)
    val = v3.zeta2_C_deep(s, D)
    return val.real, val.imag


print(f"# m1 L175 battery  dps={DPS}+{GUARD}  D* = {mp.nstr(DSTAR, 30)}  t={T0:.0f}")

# ============================== A. sign calibration ==============================
print("\n## A. sign calibration on MY lineage (heat72 zeta2_C)")
print("# A.1  D = D* - 1e-3 : expect a REAL root (m2 calibration: u = 0.0513621518162436,"
      " u^2 = +0.00263807064, ECHOED)")
Dm = DSTAR - mpf("1e-3")
u = mp.findroot(lambda t: f_real(t, Dm), sqrt(A17 * mpf("1e-3")))
u2 = u ** 2
print(f"   u    = {mp.nstr(u, 17)}   |f(u)| = {mp.nstr(fabs(f_real(u, Dm)), 4)}")
print(f"   u^2  = {mp.nstr(u2, 12)}")
print(f"   u    - m2 calib u  = {mp.nstr(u - M2_CAL['u'], 4)}   (rel {mp.nstr((u - M2_CAL['u']) / M2_CAL['u'], 4)})")
print(f"   u^2  - m2 calib u2 = {mp.nstr(u2 - M2_CAL['u2'], 4)}   (rel {mp.nstr((u2 - M2_CAL['u2']) / M2_CAL['u2'], 4)})")

print("# A.2  D = D* + 1e-3 : expect NO real root (scan) + on-line ordinate"
      " (m2: u^2 = -0.00265299559 on the line, ECHOED)")
Dp = DSTAR + mpf("1e-3")
# NB: t=0 itself is the zeta(1) pole of the t1 term -- the completed function is finite
# there by cancellation, but the raw formula is not; the scan starts at 5e-3 (the
# root-find intervals never include 0).
vals = [(t, f_real(t, Dp)) for t in [mpf(x) / 1000 for x in (5, 10, 20, 30, 40, 50, 60)]]
sgn_changes = sum(1 for i in range(len(vals) - 1) if vals[i][1] * vals[i + 1][1] < 0)
for t, fv in vals:
    print(f"   f({mp.nstr(t,3)}) = {mp.nstr(fv, 8)}")
print(f"   sign changes on [0, 0.06]: {sgn_changes}  (0 expected)")
vre, vim = f_line_re(mpf("0.05"), Dp)
print(f"   on-lineness probe at v=0.05: |Im|/|Re| = {mp.nstr(fabs(vim / vre), 4)}")
v = mp.findroot(lambda vv: f_line_re(vv, Dp)[0], sqrt(fabs(M2_CAL["u2_line"])))
vre, vim = f_line_re(v, Dp)
print(f"   line ordinate v   = {mp.nstr(v, 17)}   |Re f| = {mp.nstr(fabs(vre), 4)}   |Im f| = {mp.nstr(fabs(vim), 4)}")
print(f"   -v^2 = {mp.nstr(-(v ** 2), 12)}   vs m2 calib {M2_CAL['u2_line']}   diff {mp.nstr(-(v ** 2) - M2_CAL['u2_line'], 4)}")
print("# => on MY evaluator: real pair at D < D*, on-line pair at D > D*;"
      " with u^2 = -x my printed a is +2.6455... on the D > D* side. Sign anchored"
      " by measurement, not by the header anchor under audit.")

# ============================== B. graded-point reproduction ==============================
print("\n## B. post-reveal reproduction of ONE graded point: u2_true(eps = 0.02)"
      " (m2 graded value ECHOED)")
D02 = DSTAR - mpf("0.02")
u2b = mp.findroot(lambda t: f_real(t, D02), sqrt(A17 * mpf("0.02")))
val_b = u2b ** 2
print(f"   my u^2  = {mp.nstr(val_b, 30)}")
print(f"   |f(u)|  = {mp.nstr(fabs(f_real(u2b, D02)), 4)}")
d = val_b - M2_U2_002
print(f"   m2 u^2  = {mp.nstr(M2_U2_002, 30)}   diff = {mp.nstr(d, 6)}   rel = {mp.nstr(d / M2_U2_002, 4)}")

# ============================== C. D4 erratum fit ==============================
print("\n## C. D4 erratum: v3 closing-control residuals parsed from committed .stdout")
rows = []
pat = re.compile(
    r"closing e=([0-9.e-]+): u_pred=\(([0-9.e+-]+)\s*\+\s*([0-9.e+-]+)j\)\s+"
    r"u_pub=([0-9.]+)\s+du=\(([-0-9.e+]+)")
with open(os.path.join(HERE, "..", "machine1_der_route_a_b_a3_v3.stdout")) as fh:
    for line in fh:
        m = pat.match(line.strip())
        if m:
            rows.append((mpf(m.group(1)), mpf(m.group(2)), mpf(m.group(4)), mpf(m.group(5))))
print(f"# parsed {len(rows)} closing rows (eps, u_pred, u_pub, du_re)")
print("# C.1 u^2-space residuals: resid = u_pub^2 - u_pred^2  (u_pred used a4 = -D4 = "
      f"{mp.nstr(A4_USED, 18)})")
data = []
for eps, upr, upb, du in rows:
    resid = upb ** 2 - upr ** 2
    data.append((eps, resid, du))
    print(f"   eps={mp.nstr(eps,7)}  resid={mp.nstr(resid,12)}  resid/eps^4={mp.nstr(resid / eps**4, 10)}")
print("#   a WRONG 4th coefficient -> resid ~ eps^4 (resid/eps^4 constant);"
      " a mere truncation (a5 missing) -> resid ~ eps^5 (resid/eps^4 ~ eps)")

# least squares resid = p*eps^4 + q*eps^5  (exact 2x2 normal equations) + leave-one-out
def fit2(pts):
    S = [[mpf(0)] * 3 for _ in range(2)]
    for eps, resid, _ in pts:
        b1, b2 = eps ** 4, eps ** 5
        S[0][0] += b1 * b1; S[0][1] += b1 * b2; S[0][2] += b1 * resid
        S[1][0] += b1 * b2; S[1][1] += b2 * b2; S[1][2] += b2 * resid
    det = S[0][0] * S[1][1] - S[0][1] * S[1][0]
    p = (S[0][2] * S[1][1] - S[1][2] * S[0][1]) / det
    q = (S[0][0] * S[1][2] - S[1][0] * S[0][2]) / det
    return p, q

p, q = fit2(data)
loo_p, loo_q = [], []
for i in range(len(data)):
    pp, qq = fit2([r for j, r in enumerate(data) if j != i])
    loo_p.append(pp); loo_q.append(qq)
sp = max(fabs(x - p) for x in loo_p)
sq = max(fabs(x - q) for x in loo_q)
print(f"# C.2 two-term LS fit: p = {mp.nstr(p, 10)}  q = {mp.nstr(q, 9)}   (LOO spread p {mp.nstr(sp,3)}, q {mp.nstr(sq,3)})")
a4_corr = p + A4_USED          # u_pred^2 used a4_used*eps^4 ; true a4 = a4_used + p
a5_mine = q                     # v3 series carried no eps^5 term
print(f"   corrected a4 (mine, eps = D - D* ladder convention) = {mp.nstr(a4_corr, 9)}  +- {mp.nstr(sp, 3)}")
print(f"   implied  a5 (mine, same convention)                 = {mp.nstr(a5_mine, 9)}  +- {mp.nstr(sq, 3)}")
print(f"   vs m2 ladder-print convention |a4| = 20.4755387...: diff = {mp.nstr(a4_corr + M2_A4, 4)}"
      f"  ({mp.nstr(fabs(a4_corr + M2_A4) / sp, 3)} LOO-sigmas)")
print(f"   vs m2 a5 = 18.2711625...: diff = {mp.nstr(a5_mine - M2_A5, 4)}  ({mp.nstr(fabs(a5_mine - M2_A5) / sq, 3)} LOO-sigmas)")
print("# C.3 du ~ eps^3.5 receipts (through the sqrt: du ~ resid/(2u) ~ eps^{7/2})")
for i in range(1, len(data)):
    r_obs = data[i][2] / data[i - 1][2]
    r_pred = (data[i][0] / data[i - 1][0]) ** mpf(3.5)
    print(f"   eps {mp.nstr(data[i-1][0],6)}->{mp.nstr(data[i][0],6)}: du ratio {mp.nstr(r_obs, 5)}"
          f"   eps^3.5 prediction {mp.nstr(r_pred, 5)}")

# ============================== D. graded-output arithmetic ==============================
print("\n## D. m2 graded output arithmetic (parsed from machine2_c33_oos_graded.out)")
eps_l, errs = [], []
slope_printed = {}
epsk_printed = {}
with open(os.path.join(HERE, "..", "machine2_c33_oos_graded.out")) as fh:
    txt = fh.read()
sec = txt.split("=== v2")[0]
for line in sec.splitlines():
    m = re.match(r"eps = ([0-9.]+)", line.strip())
    if m:
        eps_l.append(mpf(m.group(1)))
    m = re.match(r"err_(\d) = ([0-9.e-]+)", line.strip())
    if m:
        errs.append((int(m.group(1)) - 1, mpf(m.group(2))))
    m = re.match(r"k=(\d): slope = ([0-9.]+)", line.strip())
    if m:
        slope_printed[int(m.group(1)) - 1] = mpf(m.group(2))
    m = re.match(r"order (\d+): eps_\(1e-12\) = ([0-9.e-]+)", line.strip())
    if m:
        epsk_printed[int(m.group(1)) - 1] = mpf(m.group(2))
by_k = {}
for k, e in errs:
    by_k.setdefault(k, []).append(e)

def lsq_slope(pts):
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    return (sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts),
            my)

print("# D.1 P1 slopes recomputed (v1 block, graded of record)")
for k in range(5):
    pts = [(mp.log10(e), mp.log10(v)) for e, v in zip(eps_l, by_k[k]) if v > mpf("1e-25")]
    sl, ic = lsq_slope(pts)
    print(f"   k={k+1}: my slope {mp.nstr(sl, 6)}  printed {mp.nstr(slope_printed[k], 6)}"
          f"  diff {mp.nstr(sl - slope_printed[k], 2)}   in band of {k+1}+-0.10: "
          f"{abs(sl - (k + 1)) <= mpf('0.10')} (v1 code target {k}: "
          f"{abs(sl - k) <= mpf('0.10')})")
g3 = epsk_printed[2] / epsk_printed[4]
print(f"# D.2 P3: eps3 = {mp.nstr(epsk_printed[2], 8)}  eps5 = {mp.nstr(epsk_printed[4], 8)}"
      f"  gain recomputed {mp.nstr(g3, 7)} (printed 10.695674)")
e = mpf("0.02")
pred3 = e ** 4 * fabs(M2_A4 + M2_A5 * e + M2_A6 * e ** 2 + M2_A7 * e ** 3)
pred5 = e ** 6 * fabs(M2_A6 + M2_A7 * e)
print(f"# D.3 graded-vs-extension consistency at eps=0.02:")
print(f"   err_3: graded {mp.nstr(by_k[2][2], 8)}   7-coef prediction {mp.nstr(pred3, 8)}"
      f"   ratio {mp.nstr(by_k[2][2] / pred3, 5)}")
print(f"   err_5: graded {mp.nstr(by_k[4][2], 8)}   |a6+a7 e| e^6  {mp.nstr(pred5, 8)}"
      f"   ratio {mp.nstr(by_k[4][2] / pred5, 5)}")

print(f"\n# wall {time.time() - T0:.0f}s; no proof claim; verification battery, nothing scored")
