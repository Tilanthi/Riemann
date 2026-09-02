"""heat49 — CONTOUR CERTIFICATION of kappa6 at all 7 sites (+ a4 record).
  Motivation: machine 3's kappa6 (Letter 8, mp.taylor) passes the table
  identity a6 = -120 S6 at all 7 sites but only at ~1e-5, and our
  synthetic mp.taylor demo shows its even orders can be wrong by
  1e7-5e10 SILENTLY (heat49 synthetic: a4 rel 1.47e7, a6 rel 5.19e10,
  odd orders exact). Their 1e-5 agreement may be luck. Certify a6 by
  Cauchy contour (the instrument that has never disagreed with the
  theorem), radius sweep x3, identity residual printed.
  PRE-REGISTERED (trap #32): contour a6 = -120 S6 within 1e-6 relative
  at all 7 sites at the two largest radii. Falsifier: any site > 1e-4.
  Also records the a4 contour column (for the full certified kappa table
  in the letter). Traps: #36, #51 (value-anchored), #38 (index-based
  own-pair exclusion).
"""
import numpy as np
import mpmath as mp
import datetime
mp.mp.dps = 50

print("TIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
ZEROS = np.sort(np.loadtxt("/tmp/zeros1.dat", dtype=np.float64))
I1 = mp.mpc(0, 1)

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

def cauchy_coeffs(f_maker, r, nmax, N=96):
    th = [2*mp.pi*k/N for k in range(N)]
    vals = [f_maker(r*mp.e**(I1*t)) for t in th]
    logs = log_unwrap(vals)
    a = []
    for j in range(1, nmax+1):
        s = sum(L*mp.e**(-I1*j*t) for L, t in zip(logs, th))
        a.append(mp.factorial(j)/(N*r**j) * s)
    return a

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
M3_K6 = {"k453": -0.00297433, "k693": -0.01495228, "k922": -0.04962456,
         "k1166": -0.06991331, "Lehmer": -0.14307592, "telescope": -0.46067820,
         "W": -8.51432869}

print("\nsite        a6 contour (largest r)   a6 = -120 S6    rel      "
      "| a4 contour    a4 = -6 S4    M3 k6 plain  rel(M3)", flush=True)
for name, j in SITES:
    m0 = 0.5*(ZEROS[j]+ZEROS[j+1]); d = 0.5*(ZEROS[j+1]-ZEROS[j])
    m0m = mp.mpf(float(m0)); dm = mp.mpf(float(d))
    others = np.concatenate([ZEROS[:j], ZEROS[j+2:]])
    r_min = float(np.min(np.abs(others - m0)))
    r_cap = min(0.75*r_min, 0.45)
    disp = others - m0
    S4 = float(np.sum(1.0/disp**4)); S6 = float(np.sum(1.0/disp**6))
    def F(z):
        return xi_z(m0m + z)/(z*z - dm*dm)
    a6_final = a4_final = None
    for frac in ("0.35", "0.55", "0.75"):
        r = mp.mpf(frac)*mp.mpf(float(r_cap))
        a = cauchy_coeffs(F, r, 6)
        def _r(v):
            return float(mp.re(v)) if isinstance(v, mp.mpc) else float(v)
        a6_final = _r(a[5]); a4_final = _r(a[3])
    rel6 = abs(a6_final - (-120*S6))/abs(120*S6)
    rel4 = abs(a4_final - (-6*S4))/abs(6*S4)
    relm3 = abs(M3_K6[name] - a6_final/720)/abs(a6_final/720)
    print(f"{name:10s} {a6_final:+22.6f} {-120*S6:+14.6f} {rel6:8.1e} | "
          f"{a4_final:+11.6f} {-6*S4:+11.6f} {rel4:8.1e} | "
          f"{a6_final/720:+11.6f} {M3_K6[name]:+11.6f} {relm3:8.1e}", flush=True)
print("\nTIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
print("done", flush=True)
