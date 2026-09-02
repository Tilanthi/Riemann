"""heat51 — CONVICTION TEST: is mpmath.mp.taylor precision-stable but
  input-dependently WRONG at higher Taylor orders, with no error signal?

  Context: machine 3's Letter-8/9 kappa5 (Lehmer jet +17.2788) violates
  the table identity a5 = -24 S5 (truth +18.406508, full 100k table,
  G5 = 2.5e-18) by 6.1e-2 relative, while their six other sites agree
  with our certified contour at 1e-6..1e-9. Their dps=90 rerun of the
  Lehmer value was stable -- they correctly concluded it is not a
  working-precision artifact, but that leaves the [OPEN-QUESTION] of
  what it IS. Candidate root cause: mp.taylor computes coefficients
  via ctx.diffs -- high-order numerical differentiation (Richardson-
  extrapolated finite differences), the same instrument family our own
  FD ladder was convicted of in heat32a (trap #49). An FD/Richardson
  scheme can converge to a STABLE WRONG value when its extrapolation
  table degenerates -- stability across dps is exactly what that
  failure mode predicts. mp.taylor's own docstring: "The coefficients
  are computed using high-order numerical differentiation."

  THIS SCRIPT (pre-registered, trap #32), all parts written before the
  single execution below. Both outcomes are reportable -- if mp.taylor
  passes P1/P2, the conviction collapses and their 17.2788 has some
  other cause, and we will say so:
    P0 sanity: mp.taylor on log(1+z) -- must reproduce
        [0, 1, -1/2, +1/3, -1/4, +1/5, -1/6] (true series
        z - z^2/2 + z^3/3 - ...). Baseline: instrument sane on a plain
        function.
    P1 KNOWN-TRUTH SYNTHETIC. Build 120 synthetic gammas (deterministic
        jitter, no RNG), pair in the middle with half-gap d, and
        Xi_syn(z) = (1+z/d)(1-z/d) * prod over the 118 non-pair window
        members of (1+z/u_k), u_k = m0 - gamma_k. For a FINITE product
        the Taylor coefficients of F(z) = log[Xi_syn(z)/(z^2-d^2)] are
        EXACTLY  c_j = (-1)^(j+1) S_j^(w) / j,  a_j = j! c_j,  with
        S_j^(w) summed over the 118 window members EXCLUDING the pair
        by INDEX (trap #38). Truth by construction, independent of any
        derivative scheme. Extract the same F with (i) mp.taylor and
        (ii) our certified Cauchy contour (control). Registered
        expectation (from an ad-hoc pre-letter session run with the
        corrected own-pair window -- see disclosure): mp.taylor exact
        at odd orders, catastrophically wrong at a4/a6.
    P2 reproduce THEIR Lehmer computation exactly: mp.taylor of
        ln[Xi/(z^2-d^2)] at their m0/d (T2g values, matching ours to
        the digit). Registered expectation: a5 = +17.278849... (their
        Letter-8 jet value), i.e. the wrong value, reproduced.
    P3 dps sweep 50/80/120 of that value. Registered expectation:
        stable -- the precision-stable-but-wrong signature.

  DISCLOSURES (error doctrine, machine 3's Letter-6 / machine 2's
  ERRATUM 1), both self-caught before any number below was quoted:
  (a) an ad-hoc FIRST version of P1 had the own-pair exclusion wrong
      (dropped Z[j] only, kept Z[j+1], the pair's upper member -- trap
      #38 sibling), briefly suggesting a sign-flip pattern; corrected
      within the same session, no number from it entered any letter.
  (b) the FIRST draft of this very file had P0's truth array mis-signed
      (coefficients of -log(1+z)); the sanity check then reported
      "error 1.0" against the CORRECT mp.taylor output. Caught by
      probing mp.taylor's actual log(1+z) output before anything was
      quoted; the instrument was right, our truth array was wrong.
      Kept here as a permanent trap-#49 reminder: the reference in a
      sanity check is itself code, and can itself be the bug.
  Traps: #36 (quote this .out), #38, #49, #51.
"""
import numpy as np
import mpmath as mp
import datetime

print("TIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
I1 = mp.mpc(0, 1)

# ---------- P0: sanity ----------
mp.mp.dps = 50
f0 = lambda z: mp.log(1+z)
c0 = mp.taylor(f0, 0, 6)
truth0 = [mp.mpf(0), mp.mpf(1), mp.mpf(-1)/2, mp.mpf(1)/3, mp.mpf(-1)/4,
          mp.mpf(1)/5, mp.mpf(-1)/6]
err0 = max(abs(c0[k]-truth0[k]) for k in range(7))
print("P0 sanity log(1+z): max |taylor - truth| over orders 0..6 =",
      mp.nstr(err0, 3), "  (truth array = series of log(1+z) itself)",
      flush=True)

# ---------- P1: known-truth synthetic ----------
print("\nP1 synthetic: 120 windowed gammas, pair in middle, d=0.01", flush=True)
nwin, jpair = 120, 60
gam = np.array([k + 0.1*np.sin(7.0*k) for k in range(nwin)], dtype=np.float64)
gam[jpair] = 60.0 - 0.01          # pair lower
gam[jpair+1] = 60.0 + 0.01        # pair upper  (half-gap d = 0.01)
m0 = 0.5*(gam[jpair]+gam[jpair+1]); d = 0.01
others = np.concatenate([gam[:jpair], gam[jpair+2:]])   # index-based exclusion
u = others - m0
S = {j: float(np.sum(1.0/u**j)) for j in range(2, 7)}
truth_plain = {j: ((-1)**(j+1))*S[j]/j for j in range(2, 7)}
truth_jet = {j: float(mp.factorial(j))*truth_plain[j] for j in range(2, 7)}
print(f"  m0={m0:.6f} d={d}  nearest non-pair |u|={np.min(np.abs(u)):.4f}",
      flush=True)
um = [mp.mpf(float(v)) for v in u]
dm = mp.mpf("0.01")
def F_syn_quot(z):
    # literally the quotient form used for zeta: log[Xi_syn/(z^2-d^2)]
    Xi = (1+z/dm)*(1-z/dm)
    for uk in um:
        Xi *= (1 + z/uk)
    return mp.log(Xi/(z*z - dm*dm))

mp.mp.dps = 120                    # function VALUES exact; instrument under test
ct = mp.taylor(F_syn_quot, 0, 6)
mp.mp.dps = 50
print("  order | mp.taylor (jet)   | truth (jet)      | rel err", flush=True)
worst_odd = worst_even = 0.0
for j in range(2, 7):
    aj = float(mp.re(ct[j]))*float(mp.factorial(j))
    rel = abs(aj - truth_jet[j])/abs(truth_jet[j])
    tag = "odd " if j % 2 else "even"
    print(f"     {j} | {aj:+17.8e} | {truth_jet[j]:+17.8e} | {rel:9.2e} {tag}",
          flush=True)
    if j % 2: worst_odd = max(worst_odd, rel)
    else: worst_even = max(worst_even, rel)
print(f"  worst odd-order rel err  = {worst_odd:.2e}", flush=True)
print(f"  worst even-order rel err = {worst_even:.2e}", flush=True)

# control: our contour on the SAME synthetic (N=96, 3 radii)
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
def cauchy_a(r, nmax, N=96):
    th = [2*mp.pi*k/N for k in range(N)]
    vals = [F_syn_quot(r*mp.e**(I1*t)) for t in th]
    logs = log_unwrap(vals)
    out = []
    for j in range(1, nmax+1):
        s = sum(L*mp.e**(-I1*j*t) for L, t in zip(logs, th))
        out.append(mp.factorial(j)/(N*r**j)*s)
    return out
r_min = float(np.min(np.abs(u))); r_cap = min(0.75*r_min, 0.45)
print("  contour control (same F):", flush=True)
for frac in ("0.35", "0.55", "0.75"):
    r = mp.mpf(frac)*mp.mpf(float(r_cap))
    a = cauchy_a(r, 6)
    rels = [abs(float(mp.re(a[j-1])) - truth_jet[j])/abs(truth_jet[j])
            for j in range(2, 7)]
    print(f"    r={float(r):.4f}: worst rel over a2..a6 = {max(rels):.2e}",
          flush=True)

# ---------- P2/P3: reproduce their Lehmer computation, dps sweep ----------
print("\nP2 reproduce machine 3's Lehmer kappa5 (T2g method, their m0/d):",
      flush=True)
ZEROS = np.sort(np.loadtxt("/tmp/zeros1.dat", dtype=np.float64))
best = None
for j in range(6000, 6800):                       # value-anchored (trap #51)
    mid = 0.5*(ZEROS[j]+ZEROS[j+1])
    if abs(mid - 7005.08171542) > 1.0: continue
    dd = 0.5*(ZEROS[j+1]-ZEROS[j])
    if best is None or dd < best[0]: best = (dd, j)
jl = best[1]
m0l = 0.5*(ZEROS[jl]+ZEROS[jl+1]); dl = 0.5*(ZEROS[jl+1]-ZEROS[jl])
m0m = mp.mpf(float(m0l)); dmm = mp.mpf(float(dl))
def xi_z(z):
    s = mp.mpf("0.5") + I1*z
    return mp.pi**(-s/2) * mp.gamma(s/2) * mp.zeta(s) * s * (s-1) / 2
def F_leh(z):
    return mp.log(xi_z(m0m + z)/(z*z - dmm*dmm))
others_l = np.concatenate([ZEROS[:jl], ZEROS[jl+2:]])
disp = others_l - m0l
S5l = float(np.sum(1.0/disp**5))
print(f"  Lehmer j={jl} m0={m0l:.13f} d={dl:.13f} (T2g: 7005.0817154237838622066"
      f" / 0.0188492488630700935625)", flush=True)
print(f"  identity truth a5 = -24*S5 (full 100k table) = {-24*S5l:+.6f}   "
      f"(heat47 contour: +18.406508, 3 radii; heat48 P3: 2 more radii, N=192, dps=60)",
      flush=True)
for dps in (50, 80, 120):
    mp.mp.dps = dps
    ct = mp.taylor(F_leh, 0, 6)
    a5 = float(mp.re(ct[5]))*120.0
    a3 = float(mp.re(ct[3]))*6.0
    a6 = float(mp.re(ct[6]))*720.0
    print(f"  P3 dps={dps:3d}: mp.taylor a5 = {a5:+.9f} "
          f"(rel vs truth {abs(a5 - (-24*S5l))/abs(24*S5l):.2e})   "
          f"a3={a3:+.6f}  a6={a6:+.6f}", flush=True)
mp.mp.dps = 50
print("\nTIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
print("done", flush=True)
