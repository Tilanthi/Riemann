"""heat48 — TABLE-IDENTITY ARBITRATION of the kappa5 Lehmer discrepancy.
  Machine 3 Letter 8 (git 19:55:19Z) vs our heat47 (19:42:56-19:44:48Z,
  committed in our letter 19:47:36Z — both pre-registered, disjoint
  instruments). kappa5 agrees 6/7 sites at 6 s.f.; LEHMER disagrees:
  ours +0.153388 plain, theirs +0.143990 plain (6.5% relative).
  THEOREM (identity family, validated in heat47 at j=3,4,5 to 6 digits,
  all 7 sites, radius-stable x3): with S_j = sum over all table zeros
  except own pair (index-based) of (m0-gamma)^(-j), and G_j the arch
  Taylor parts (|G_j| <= 1e-18 for j>=4 at our sites),
        a_j - G_j = -(j-1)! * S_j      for all j >= 2.
  LHS = contour on mpmath zeta/gamma (TABLE-FREE). RHS = pure table
  arithmetic. Disjoint computations agreeing = both right.
  THIS SCRIPT (pre-registered, trap #32):
  P1  Recompute S_5, S_6 at all 7 sites from the table; predict
      a5 = -24 S5 (6 s.f., G5 negligible) and a6 = -120 S6.
      DECISION RULE (registered): any instrument's a_j that violates
      -(j-1)! S_j by > 1e-4 RELATIVE at that site is [FALSIFIED] at
      that site, regardless of provenance.
  P2  Apply to: our heat47 a5 column (expect all-pass — belt and
      braces re-derivation); machine 3's Letter-8 kappa5 plain column
      (expect 6 pass, Lehmer FAIL); machine 3's Letter-8 kappa6 plain
      column (first kappa6 on the board — no prior of ours; theorem
      decides; G6 ~ 1e-22 << a6).
  P3  Re-verify OUR Lehmer a5 independently of heat47's radii: fresh
      Cauchy contour, r = 0.20 and 0.28 of r_cap (different from
      heat47's 0.35/0.55/0.75), N=192 (vs 96), dps=60 (vs 50).
      Expect a5 = +18.4065 jet at 6 s.f. if ours is right.
  P4  Cross-check their kappa3 column against the same theorem
      (zp3 = -2 S3) — expect all 7 pass incl. Lehmer (known 1.2e-5).
  Traps: #36 (quote this .out), #51 (value-anchored sites only).
"""
import numpy as np
import mpmath as mp
import datetime
mp.mp.dps = 50

print("TIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
ZEROS = np.sort(np.loadtxt("/tmp/zeros1.dat", dtype=np.float64))
I1 = mp.mpc(0, 1)

def find_pair(target_d, center, lo, hi):
    best = None
    for j in range(lo, hi):
        mid = 0.5*(ZEROS[j]+ZEROS[j+1]); d = 0.5*(ZEROS[j+1]-ZEROS[j])
        if abs(mid-center) > 30: continue
        err = abs(d-target_d)
        if best is None or err < best[0]:
            best = (err, j)
    return best[1]

SITES = [
    ("W",         find_pair(0.2998529, 9023.265, 8900, 9100)),
    ("k922",      find_pair(0.0807504, 1329.12, 850, 1000)),
    ("Lehmer",    find_pair(0.0188492, 7005.08, 6000, 6800)),
    ("k693",      find_pair(0.1105535, 1054.89, 550, 800)),
    ("k453",      find_pair(0.1552154, 750.81, 300, 550)),
    ("k1166",     find_pair(0.1252795, 1610.13, 1000, 1250)),
    ("telescope", find_pair(0.0073507, 71732.91, 94000, 97000)),
]

# machine 3 Letter 8 tables (plain normalization; jet = n! * plain)
M3_K5 = {"k453": -0.00302117, "k693": +0.00248883, "k922": -0.02595928,
         "k1166": +0.00446110, "Lehmer": +0.14399041, "telescope": +0.30948635,
         "W": +5.25841023}
M3_K6 = {"k453": -0.00297433, "k693": -0.01495228, "k922": -0.04962456,
         "k1166": -0.06991331, "Lehmer": -0.14307592, "telescope": -0.46067820,
         "W": -8.51432869}
M3_K3 = {"k453": -0.0125013, "k693": -0.00693421, "k922": -0.0520458,
         "k1166": +0.0161912, "Lehmer": +0.256167, "telescope": +0.327860,
         "W": +2.28820}
OURS_A5 = {"W": 631.009283, "k922": -3.115109, "Lehmer": 18.406508,
           "k693": 0.298651, "k453": -0.362541, "k1166": 0.535331,
           "telescope": 37.138362}

print("\n== P1/P2: theorem table a_j = -(j-1)! S_j, j=3,5,6 ==", flush=True)
print(f"{'site':10s} {'a3 pred':>10s} {'M3 k3':>10s} {'rel':>8s} | "
      f"{'a5 pred':>11s} {'M3 k5':>10s} {'rel':>8s} | {'ours a5':>10s} "
      f"{'rel':>8s} | {'a6 pred':>10s} {'M3 k6':>10s} {'rel':>8s}", flush=True)
verdicts = {"k3": [], "k5_m3": [], "k5_ours": [], "k6_m3": []}
for name, j in SITES:
    m0 = 0.5*(ZEROS[j]+ZEROS[j+1])
    others = np.concatenate([ZEROS[:j], ZEROS[j+2:]])
    disp = others - m0
    S3 = float(np.sum(1.0/disp**3)); S5 = float(np.sum(1.0/disp**5))
    S6 = float(np.sum(1.0/disp**6))
    a3 = -2*S3; a5 = -24*S5; a6 = -120*S6       # jet scale, G_j negligible
    r3 = abs(M3_K3[name] - a3/6)/abs(a3/6)
    r5m = abs(M3_K5[name] - a5/120)/abs(a5/120)
    r5o = abs(OURS_A5[name] - a5)/abs(a5)
    r6m = abs(M3_K6[name] - a6/720)/abs(a6/720)
    verdicts["k3"].append(r3); verdicts["k5_m3"].append(r5m)
    verdicts["k5_ours"].append(r5o); verdicts["k6_m3"].append(r6m)
    print(f"{name:10s} {a3/6:+10.6f} {M3_K3[name]:+10.6f} {r3:8.1e} | "
          f"{a5:+11.6f} {M3_K5[name]*120:+10.6f} {r5m:8.1e} | "
          f"{OURS_A5[name]:+10.6f} {r5o:8.1e} | {a6/720:+10.6f} "
          f"{M3_K6[name]:+10.6f} {r6m:8.1e}", flush=True)

print("\n== registered decision rule: rel > 1e-4 = [FALSIFIED] at that site ==",
      flush=True)
names = [n for n, _ in SITES]
for key, label in [("k3", "M3 kappa3"), ("k5_m3", "M3 kappa5"),
                   ("k5_ours", "OURS kappa5"), ("k6_m3", "M3 kappa6")]:
    bad = [names[i] for i, r in enumerate(verdicts[key]) if r > 1e-4]
    worst = max(verdicts[key])
    print(f"  {label:12s}: fails at {bad if bad else 'NONE'} "
          f"(worst rel {worst:.1e})", flush=True)

print("\n== P3: independent re-verification of OUR Lehmer a5 ==", flush=True)
mp.mp.dps = 60
def xi_z(z):
    s = mp.mpf("0.5") + I1*z
    return mp.pi**(-s/2) * mp.gamma(s/2) * mp.zeta(s) * s * (s-1) / 2
def log_unwrap(vals):
    out = []; arg = mp.arg(vals[0]); base = mp.log(abs(vals[0])); prev = arg
    for k, w in enumerate(vals):
        a = mp.arg(w); dd = a - prev
        if dd > mp.pi: dd -= 2*mp.pi
        if dd < -mp.pi: dd += 2*mp.pi
        if k == 0: out.append(base + I1*arg)
        else:
            arg += dd; out.append(mp.log(abs(w)) + I1*arg)
        prev = a
    return out
jl = SITES[[n for n, _ in SITES].index("Lehmer")][1]
m0 = 0.5*(ZEROS[jl]+ZEROS[jl+1]); d = 0.5*(ZEROS[jl+1]-ZEROS[jl])
m0m = mp.mpf(float(m0)); dm = mp.mpf(float(d))
others = np.concatenate([ZEROS[:jl], ZEROS[jl+2:]])
r_min = float(np.min(np.abs(others - m0))); r_cap = min(0.75*r_min, 0.45)
print(f"Lehmer j={jl} m0={m0:.7f} d={d:.9f} r_cap={r_cap:.4f} "
      f"(heat47 radii were 0.165/0.259/0.354)", flush=True)
def F(z):
    return xi_z(m0m + z)/(z*z - dm*dm)
for frac, N in (("0.20", 192), ("0.28", 192)):
    r = mp.mpf(frac)*mp.mpf(float(r_cap))
    th = [2*mp.pi*k/N for k in range(N)]
    vals = [F(r*mp.e**(I1*t)) for t in th]
    logs = log_unwrap(vals)
    s5 = sum(L*mp.e**(-I1*5*t) for L, t in zip(logs, th))
    a5 = mp.factorial(5)/(N*r**5)*s5
    a5r = float(mp.re(a5)) if isinstance(a5, mp.mpc) else float(a5)
    print(f"  r={float(r):.4f} N={N} dps=60: a5={a5r:+.6f} jet "
          f"({a5r/120:+.6f} plain) | heat47 a5=+18.406508 | "
          f"M3 Letter8 a5=+17.2788", flush=True)

print("\nTIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
print("done", flush=True)
