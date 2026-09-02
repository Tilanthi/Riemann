"""heat52 — R-CHANNEL vs q_far-CHANNEL of the b_c calibration error.
  PRE-REGISTERED as "heat48" in our Letter-4 reply §6 (trap #32); renamed
  heat52 because heat48-51b were consumed by the 2026-09-02 arbitration
  night. Analysis plan unchanged from the registration.

  Registration (verbatim intent): across the existing heat38/heat40
  calibration pool (errors already computed on disk; NO new census, no
  new zeta calls), test whether model calibration error correlates with
  R = S4/S2^2 (equivalently u1/S2) AT LEAST AS STRONGLY as with q_far.
  Method: partial correlation controlling for q_far.
  FALSIFIER: |partial r(err, R | q_far)| < 0.15 -> the R-channel adds
  nothing beyond q_far; report either way.

  Pool bookkeeping (honesty note): the registration said "61-site pool";
  on disk the pools contain 30 (heat38 q-strata) + 30 (heat40 B'-strata)
  = 60 in-pool sites with computed errors, plus the out-of-pool W anchor
  (heat33h/heat35: err -0.15%, heat38b header: q_far(W)=0.0813, q(W)
  0.248; heat47: R(W)=0.4562). PRIMARY analysis = the 60 in-pool sites;
  the registration's "61" is run as the W-inclusive SENSITIVITY.

  Site reconstruction: verbatim pool codes (heat38b's picks for heat38;
  heat40's picks for heat40) from the same imported machinery, joined to
  the parsed .out errors by (h, d/q) matching as in heat38b (trap #36:
  errors from the files, never recomputed). R, q, q_far computed fresh
  from the zero table with INDEX-BASED own-pair exclusion (trap #38);
  q join-checked against the printed heat38 q column (convention check).

  P1  Pearson r(err, X) for X in {R, q_far, q} on the union and each pool.
  P2  partial r(err, R | q_far) and r(err, q_far | R), standard formula.
  P3  REGISTERED DECISION: R-channel survives iff |partial r(err,R|q_far)|
      >= 0.15 AND |r(err,R)| >= |r(err,q_far)|.
  P4  multiple regression err% ~ [1, R, q_far] with SEs; within-q-tercile
      robustness; W-inclusive 61-site sensitivity.
"""
import re
import numpy as np
from heat38_population import ZEROS, site_setup

def sums(i):
    # R: FULL-TABLE S4/S2^2, index-based own-pair exclusion (registered
    # definition, matches the GUE-exchange R).
    # q, q_far: the MODEL's windowed convention (site_setup B, WIN=50;
    # disp1 = eps1) -- the convention the pool errors were calibrated
    # under (heat38b/heat40). Join-checked against the printed columns.
    m0 = 0.5*(ZEROS[i]+ZEROS[i+1]); d = 0.5*(ZEROS[i+1]-ZEROS[i])
    others = np.concatenate([ZEROS[:i], ZEROS[i+2:]])
    disp = others - m0
    S2 = float(np.sum(1.0/disp**2)); S4 = float(np.sum(1.0/disp**4))
    st = site_setup(i)
    B = st["B"]; e1 = st["disp1"]
    Bp = B - 1.0/(e1*e1)
    return dict(m0=m0, d=d, R=S4/S2**2, q=B*d*d/2, q_far=Bp*d*d/2)

# ---- heat38 pool picks (verbatim from heat38b) ----
cand = []
for i in range(1, len(ZEROS)-2):
    m0 = 0.5*(ZEROS[i]+ZEROS[i+1])
    if m0 > 6000: break
    d = 0.5*(ZEROS[i+1]-ZEROS[i])
    if not (0.05 <= d <= 0.35): continue
    L = min(m0 - ZEROS[i-1], ZEROS[i+2] - m0)
    if not (d < 0.25*L): continue
    cand.append(i)
met = sorted((site_setup(i)["B"]*site_setup(i)["d"]**2/2, i) for i in cand)
qs = [q for q, _ in met]; n = len(met)
t1, t2 = qs[n//3], qs[2*n//3]
picks38 = []
for nm, lst in (("LOW", [i for q, i in met if q <= t1]),
                ("MID", [i for q, i in met if t1 < q <= t2]),
                ("HIGH", [i for q, i in met if q > t2])):
    lst_h = sorted(lst, key=lambda i: 0.5*(ZEROS[i]+ZEROS[i+1]))
    picks38 += [(nm, i) for i in
                [lst_h[int(round(k*(len(lst_h)-1)/9))] for k in range(10)]]

# ---- heat40 pool picks (verbatim from heat40) ----
cand = []
for i in range(1, len(ZEROS)-2):
    m0 = 0.5*(ZEROS[i]+ZEROS[i+1])
    if m0 > 6000: break
    d = 0.5*(ZEROS[i+1]-ZEROS[i])
    if not (0.20 <= d <= 0.24): continue
    L = min(m0 - ZEROS[i-1], ZEROS[i+2] - m0)
    if not (d < 0.25*L): continue
    cand.append(i)
Bp = {i: site_setup(i)["B"] - 1.0/(site_setup(i)["disp1"]**2) for i in cand}
met = sorted((Bp[i], i) for i in cand)
bs = [b for b, _ in met]; n = len(met)
t1b, t2b = bs[n//3], bs[2*n//3]
picks40 = []
for nm, lst in (("LOWB", [i for b, i in met if b <= t1b]),
                ("MIDB", [i for b, i in met if t1b < b <= t2b]),
                ("HIGHB", [i for b, i in met if b > t2b])):
    lst_h = sorted(lst, key=lambda i: 0.5*(ZEROS[i]+ZEROS[i+1]))
    picks40 += [(nm, i) for i in
                [lst_h[int(round(k*(len(lst_h)-1)/9))] for k in range(10)]]

# ---- parse the two .out files (trap #36) ----
pat38 = re.compile(r"(LOW|MID|HIGH) h=([\d.]+) d=([\d.]+) q=([\d.]+) .*bc_m=([\d.]+) "
                   r"bc_c=([\d.]+) \(([+-][\d.]+)%\)")
filed38 = [dict(h=float(m.group(2)), d=float(m.group(3)), q=float(m.group(4)),
                err=float(m.group(7)))
           for ln in open("heat38_population.out") if (m := pat38.search(ln))]
pat40 = re.compile(r"(LOWB|MIDB|HIGHB) h=([\d.]+) d=([\d.]+) Bp=[\d.]+ "
                   r"q_far=([\d.]+) bc_m=[\d.]+ bc_c=[\d.]+ \(([+-][\d.]+)%\)")
filed40 = [dict(h=float(m.group(2)), d=float(m.group(3)), qf=float(m.group(4)),
                err=float(m.group(5)))
           for ln in open("heat40_matched.out") if (m := pat40.search(ln))]
print(f"parsed {len(filed38)} heat38 rows, {len(filed40)} heat40 rows", flush=True)

rows = []
for nm, i in picks38:
    s = sums(i)
    hit = [f for f in filed38 if abs(f["h"]-s["m0"]) < 0.05 and abs(f["q"]-s["q"]) < 0.002]
    assert hit, f"no heat38 row for i={i} h={s['m0']:.1f}"
    rows.append(dict(pool="38", strat=nm, i=i, **s, err=hit[0]["err"]))
for nm, i in picks40:
    s = sums(i)
    hit = [f for f in filed40 if abs(f["h"]-s["m0"]) < 0.05 and abs(f["d"]-s["d"]) < 0.002]
    assert hit, f"no heat40 row for i={i} h={s['m0']:.1f}"
    assert abs(hit[0]["qf"]-s["q_far"]) < 0.002, f"q_far mismatch i={i}"
    rows.append(dict(pool="40", strat=nm, i=i, **s, err=hit[0]["err"]))
print(f"joined {len(rows)} sites ({sum(1 for r in rows if r['pool']=='38')} heat38 + "
      f"{sum(1 for r in rows if r['pool']=='40')} heat40)", flush=True)
# convention check: our fresh q vs heat38's printed q (they used site_setup B)
mx = max(abs(r["q"]-f["q"]) for r in rows if r["pool"] == "38"
         for f in filed38 if abs(f["h"]-r["m0"]) < 0.05)
print(f"convention check: max |our q - printed q| over heat38 sites = {mx:.5f}", flush=True)

err = np.array([r["err"] for r in rows])
R = np.array([r["R"] for r in rows])
QF = np.array([r["q_far"] for r in rows])
Q = np.array([r["q"] for r in rows])

def pearson(x, y):
    return float(np.corrcoef(x, y)[0, 1])
def partial(x, y, z):
    rxy, rxz, ryz = pearson(x, y), pearson(x, z), pearson(y, z)
    return (rxy - rxz*ryz)/np.sqrt((1-rxz**2)*(1-ryz**2))

print("\n=== P1: Pearson r(err, X) ===", flush=True)
for lbl, x in (("R", R), ("q_far", QF), ("q", Q)):
    r_all = pearson(x, err)
    r_38 = pearson(x[ [k for k,r in enumerate(rows) if r["pool"]=="38"] ],
                   err[ [k for k,r in enumerate(rows) if r["pool"]=="38"] ])
    r_40 = pearson(x[ [k for k,r in enumerate(rows) if r["pool"]=="40"] ],
                   err[ [k for k,r in enumerate(rows) if r["pool"]=="40"] ])
    print(f"  err vs {lbl:5s}: union {r_all:+.3f}   heat38 {r_38:+.3f}   heat40 {r_40:+.3f}",
          flush=True)
print(f"  collinearity r(R, q_far) = {pearson(R, QF):+.3f}   r(R, q) = {pearson(R, Q):+.3f}",
      flush=True)

print("\n=== P2: partial correlations ===", flush=True)
pR = partial(R, err, QF); pQ = partial(QF, err, R)
print(f"  partial r(err, R    | q_far) = {pR:+.3f}", flush=True)
print(f"  partial r(err, q_far| R    ) = {pQ:+.3f}", flush=True)

print("\n=== P3: registered decision ===", flush=True)
ok1 = abs(pR) >= 0.15
ok2 = abs(pearson(R, err)) >= abs(pearson(QF, err))
print(f"  |partial r(err,R|q_far)| = {abs(pR):.3f} >= 0.15 ? {'YES' if ok1 else 'NO'}", flush=True)
print(f"  |r(err,R)| = {abs(pearson(R,err)):.3f} >= |r(err,q_far)| = {abs(pearson(QF,err)):.3f} ? "
      f"{'YES' if ok2 else 'NO'}", flush=True)
print(f"  VERDICT: R-channel {'SURVIVES' if (ok1 and ok2) else 'FALSIFIED'}"
      f" (falsifier |partial| < 0.15: {'not fired' if ok1 else 'FIRED'})", flush=True)

print("\n=== P4a: multiple regression err% ~ [1, R, q_far] ===", flush=True)
X = np.column_stack([np.ones_like(R), R, QF])
beta, *_ = np.linalg.lstsq(X, err, rcond=None)
resid = err - X @ beta
dof = len(err) - 3
s2 = float(resid @ resid)/dof
cov = s2*np.linalg.inv(X.T @ X)
se = np.sqrt(np.diag(cov))
names = ["const", "R", "q_far"]
for nm, b, s in zip(names, beta, se):
    print(f"  {nm:6s} {b:+8.3f} +- {s:.3f}   (t = {b/s:+.2f})", flush=True)
print(f"  residual sd {resid.std(ddof=3):.3f} pp   R2 = "
      f"{1 - resid@resid/((err-err.mean())@(err-err.mean())):.4f}", flush=True)

print("\n=== P4b: within-q-tercile robustness (union, terciles of q) ===", flush=True)
o = np.argsort(Q)
for lbl, idx in (("q-low", o[:20]), ("q-mid", o[20:40]), ("q-high", o[40:])):
    print(f"  {lbl:7s} n={len(idx)}: r(err,R) = {pearson(R[idx], err[idx]):+.3f}   "
          f"r(err,q_far) = {pearson(QF[idx], err[idx]):+.3f}", flush=True)

print("\n=== P4c: W-inclusive 61-site sensitivity ===", flush=True)
R61 = np.append(R, 0.4562); QF61 = np.append(QF, 0.0813); E61 = np.append(err, -0.15)
print(f"  r(err,R) = {pearson(R61,E61):+.3f}   r(err,q_far) = {pearson(QF61,E61):+.3f}   "
      f"partial r(err,R|q_far) = {partial(R61,E61,QF61):+.3f}", flush=True)

print("\n=== per-site table ===", flush=True)
for r in rows:
    print(f"  {r['pool']} {r['strat']:5s} i={r['i']:5d} h={r['m0']:7.1f} d={r['d']:.3f} "
          f"R={r['R']:.4f} q={r['q']:.4f} q_far={r['q_far']:.4f} err={r['err']:+.2f}%",
          flush=True)
print("done", flush=True)
