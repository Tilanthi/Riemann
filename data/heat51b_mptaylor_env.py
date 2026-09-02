"""heat51b — environment-dependence of the mp.taylor failure + fixed contour
  control on the synthetic.

  heat51 P2 found: mp.taylor of log[Xi/(z^2-d^2)] at Lehmer gives, on THIS
  machine, a5 = -3812.924724849 (dps 50/80/120 identical) vs identity truth
  +18.406508 -- 208x wrong, and NOT the +17.2788 machine 3 published from
  the same method and same site. Their dps=90 rerun was stable on THEIR
  machine. So the instrument is precision-stable WITHIN an environment and
  non-reproducible ACROSS environments. This script pins that down:
    P1 exact-input reproduction: run their T2g function verbatim with
        THEIR 22-digit m0/d (mp.mpf string constants), not our float64
        table values, at dps 50 and 90. If still -3812.92, the input is
        exonerated and the divergence is environmental (mpmath version /
        Richardson-table defaults).
    P2 mpmath version + taylor implementation path printed (the docstring
        says coefficients come from ctx.diffs -- high-order numerical
        differentiation).
    P3 mp.taylor at two more sites (k922, W) vs identity truth -- their
        Letter-8 values at these sites PASS the identity at 1e-6..1e-9,
        so we register the expectation that mp.taylor also passes here
        (i.e. failure is site/input-dependent, not universal); either
        outcome is reportable.
    P4 the FIXED contour control on heat51's synthetic (the P1 control in
        heat51 was mis-wired: F_syn_quot already returns a log and was
        passed through log_unwrap again -- double log; disclosed in the
        letter). Correct wiring: raw quotient into log_unwrap.
  Pre-registered (trap #32). Traps: #36 (quote this .out), #49, #51.
"""
import numpy as np
import mpmath as mp
import datetime

print("TIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
I1 = mp.mpc(0, 1)
print("P2 mpmath version:", mp.__version__, flush=True)

ZEROS = np.sort(np.loadtxt("/tmp/zeros1.dat", dtype=np.float64))

def find_pair(target_d, center, lo, hi):
    best = None
    for j in range(lo, hi):
        mid = 0.5*(ZEROS[j]+ZEROS[j+1]); d = 0.5*(ZEROS[j+1]-ZEROS[j])
        if abs(mid-center) > 30: continue
        err = abs(d-target_d)
        if best is None or err < best[0]: best = (err, j)
    return best[1]

def table_truth(j):
    m0 = 0.5*(ZEROS[j]+ZEROS[j+1])
    others = np.concatenate([ZEROS[:j], ZEROS[j+2:]])
    disp = others - m0
    S = {k: float(np.sum(1.0/disp**k)) for k in (3, 5, 6)}
    return -2*S[3], -24*S[5], -120*S[6]

# ---------- P1: their exact inputs, their exact function ----------
print("\nP1 their T2g function verbatim, THEIR 22-digit m0/d:", flush=True)
m0_t2g = mp.mpf('7005.0817154237838622066')
d_t2g  = mp.mpf('0.0188492488630700935625')
def make_f(m0, d):
    def f(z, m0=m0, d=d):
        s = mp.mpf('0.5') + 1j*(m0+z)
        Xi_val = mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
        return mp.log(Xi_val / (z**2 - d**2))
    return f
f_leh = make_f(m0_t2g, d_t2g)
a3t, a5t, a6t = table_truth(6708)
print(f"  identity truth (our j=6708 table): a3={a3t:+.6f} a5={a5t:+.6f} a6={a6t:+.6f}",
      flush=True)
for dps in (50, 90):
    mp.mp.dps = dps
    ct = mp.taylor(f_leh, 0, 6)
    a3 = float(mp.re(ct[3]))*6.0; a5 = float(mp.re(ct[5]))*120.0
    a6 = float(mp.re(ct[6]))*720.0
    print(f"  dps={dps}: a3={a3:+.6f} (rel {abs(a3-a3t)/abs(a3t):.1e})  "
          f"a5={a5:+.6f} (rel {abs(a5-a5t)/abs(a5t):.1e})  "
          f"a6={a6:+.4f} (rel {abs(a6-a6t)/abs(a6t):.1e})", flush=True)
print("  (their published: a3=+1.53700, a5=+17.2788, a6=-103.015)", flush=True)

# ---------- P3: two more sites ----------
print("\nP3 mp.taylor at k922 and W (their values PASS identity there):", flush=True)
for name, td, ctr, lo, hi in (("k922", 0.0807504, 1329.12, 850, 1000),
                              ("W",    0.2998529, 9023.265, 8900, 9100)):
    j = find_pair(td, ctr, lo, hi)
    m0 = 0.5*(ZEROS[j]+ZEROS[j+1]); d = 0.5*(ZEROS[j+1]-ZEROS[j])
    f = make_f(mp.mpf(float(m0)), mp.mpf(float(d)))
    a3t, a5t, a6t = table_truth(j)
    mp.mp.dps = 50
    ct = mp.taylor(f, 0, 6)
    a3 = float(mp.re(ct[3]))*6.0; a5 = float(mp.re(ct[5]))*120.0
    a6 = float(mp.re(ct[6]))*720.0
    print(f"  {name:5s} j={j}: a3 {a3:+.6f} vs {a3t:+.6f} (rel {abs(a3-a3t)/abs(a3t):.1e})  "
          f"a5 {a5:+.6f} vs {a5t:+.6f} (rel {abs(a5-a5t)/abs(a5t):.1e})", flush=True)
mp.mp.dps = 50

# ---------- P4: fixed contour control on heat51's synthetic ----------
print("\nP4 fixed contour control (raw quotient into log_unwrap):", flush=True)
nwin, jpair = 120, 60
gam = np.array([k + 0.1*np.sin(7.0*k) for k in range(nwin)], dtype=np.float64)
gam[jpair] = 60.0 - 0.01; gam[jpair+1] = 60.0 + 0.01
m0s = 0.5*(gam[jpair]+gam[jpair+1])
others = np.concatenate([gam[:jpair], gam[jpair+2:]])
u = others - m0s
S = {k: float(np.sum(1.0/u**k)) for k in range(2, 7)}
truth_jet = {k: float(mp.factorial(k))*((-1)**(k+1))*S[k]/k for k in range(2, 7)}
um = [mp.mpf(float(v)) for v in u]; dm = mp.mpf("0.01")
def G_raw(z):
    # RAW quotient (NOT pre-logged) -- the correct contour wiring
    Xi = (1+z/dm)*(1-z/dm)
    for uk in um:
        Xi *= (1 + z/uk)
    return Xi/(z*z - dm*dm)
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
r_min = float(np.min(np.abs(u))); r_cap = min(0.75*r_min, 0.45)
for frac in ("0.35", "0.55", "0.75"):
    r = mp.mpf(frac)*mp.mpf(float(r_cap))
    th = [2*mp.pi*k/96 for k in range(96)]
    vals = [G_raw(r*mp.e**(I1*t)) for t in th]
    logs = log_unwrap(vals)
    rels = []
    for j in range(2, 7):
        s = sum(L*mp.e**(-I1*j*t) for L, t in zip(logs, th))
        aj = float(mp.re(mp.factorial(j)/(96*r**j)*s))
        rels.append(abs(aj - truth_jet[j])/abs(truth_jet[j]))
    print(f"  r={float(r):.4f}: worst rel over a2..a6 = {max(rels):.2e}", flush=True)

print("\nTIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
print("done", flush=True)
