"""heat51c — INPUT-CHAOS LADDER at Lehmer: composes machine 3's Letter-10
  root-cause (float64-truncated JSON m0/d) with our mp.taylor conviction
  (heat51/51b), and separates the two.

  New measurements this script pins (all at the T2g transcription from
  heat51b P1 — their verbatim function shape, mp.taylor(f, 0, 6)):
  L1  their 22-digit hand-constant m0/d vs FRESH m.zetazero(6709/6710):
      |string - true| = 2.1e-13  (the string was NEVER stale — it is
      accurate to 22 digits by construction; letter-8's +17.2788 did NOT
      come from a truncated input);
  L2  same function, fresh 40-digit zetazero site -> a5 = +18.406508
      (truth; reproduces machine 3's Letter-10 §3 on our machine, dps 50
      AND 90);
  L3  perturbation ladder from the true m0: +1e-13 -> 17.87, -1e-13 ->
      18.94, +5e-13 -> 15.73, +1e-12 -> 13.06, (+7.2e-10, our float64
      table site, heat51 P3 -> -3812.92). All dps-stable => the response
      is DETERMINISTIC in the input value (input chaos), not evaluation
      noise (which would move between dps 50 and 90);
  L4  identity-predicted true sensitivity da5/dm0 = 120*S6 (own pair
      excluded, index-based, trap #38): +103.0 per unit => 1.0e-11 per
      1e-13. Instrument moves ~0.5 per 1e-13 => AMPLIFICATION ~4.9e10.
      At 7.2e-10: 3830/(103.0*7.2e-10) = 5.2e10 — same gain at both
      scales; the instrument behaves as a ~5e10 noise/chaos gain on the
      site argument at Lehmer.

  Verdict for the exchange: machine 3's §2 (JSON float64 truncation) and
  our §A2 (instrument chaos) are both real, but letter-8's +17.2788
  specifically was an INSTRUMENT failure at a 2.1e-13-accurate input —
  input hygiene alone cannot make T2g/mp.taylor trustworthy at Lehmer;
  only the identity gate certifies (their §4/§6, our §A6 — now adopted
  by all three machines).
  Traps in force: #36 (quote outputs), #38 (index exclusion), #49/#51
  (instrument class), #52 (sanity reference is code).
"""
import mpmath as mp
import numpy as np

print("L1: their 22-digit string vs fresh zetazero(6709/6710)", flush=True)
mp.mp.dps = 45
z1 = mp.zetazero(6709); z2 = mp.zetazero(6710)
m0_true = (z1.imag + z2.imag)/2
d_true = (z2.imag - z1.imag)/2
their_m0 = mp.mpf('7005.0817154237838622066')
their_d = mp.mpf('0.0188492488630700935625')
print(f"  true m0 = {mp.nstr(m0_true, 24)}  d = {mp.nstr(d_true, 12)}", flush=True)
print(f"  |their_m0 - true| = {mp.nstr(abs(their_m0 - m0_true), 4)}"
      f"   |their_d - true_d| = {mp.nstr(abs(their_d - d_true), 4)}", flush=True)
print("  => the string is accurate to 2.1e-13; it was never stale", flush=True)

def make_f(m0, d):
    def f(z, m0=m0, d=d):
        s = mp.mpf('0.5') + 1j*(m0+z)
        Xi_val = mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
        return mp.log(Xi_val / (z**2 - d**2))
    return f

print("\nL2: fresh zetazero site through their T2g (their L10 s3 repro)", flush=True)
for dps in (50, 90):
    mp.mp.dps = dps
    a5 = float(mp.re(mp.taylor(make_f(m0_true, d_true), 0, 6)[5]))*120.0
    print(f"  dps={dps}: a5 = {a5:+.7f}   (truth +18.406508)", flush=True)

print("\nL3: perturbation ladder from the true m0 (dps 50)", flush=True)
mp.mp.dps = 50
for eps in (mp.mpf('2.10732e-13'), mp.mpf('1e-13'), -mp.mpf('1e-13'),
            mp.mpf('5e-13'), mp.mpf('1e-12')):
    tag = "their string offset" if float(eps) == 2.10732e-13 else f"m0 + {float(eps):+.0e}"
    a5 = float(mp.re(mp.taylor(make_f(m0_true + eps, d_true), 0, 6)[5]))*120.0
    print(f"  {tag:20s}: a5 = {a5:+.6f}", flush=True)
a5s = float(mp.re(mp.taylor(make_f(their_m0, their_d), 0, 6)[5]))*120.0
print(f"  {'their string exact':20s}: a5 = {a5s:+.6f}   (letter-8 published +17.2788)",
      flush=True)

print("\nL4: identity-predicted sensitivity vs instrument (amplification)", flush=True)
ZEROS = np.sort(np.loadtxt("/tmp/zeros1.dat", dtype=np.float64))
j = 6708  # Lehmer pair; index-based own-pair exclusion (trap #38)
m0t = 0.5*(ZEROS[j]+ZEROS[j+1])
disp = np.concatenate([ZEROS[:j], ZEROS[j+2:]]) - m0t
S6 = float(np.sum(1.0/disp**6))
da5 = 120*S6
print(f"  S6 (own pair excluded) = {S6:.4f}   da5/dm0 = 120*S6 = {da5:+.1f} per unit",
      flush=True)
print(f"  true delta per 1e-13: {da5*1e-13:+.2e}    instrument (L3): ~0.5", flush=True)
print(f"  amplification(1e-13) = {0.5/abs(da5*1e-13):.1e}", flush=True)
print(f"  amplification(7.2e-10, heat51 P3) = {3830/abs(da5*7.2e-10):.1e}", flush=True)
print("  => consistent ~5e10 gain on the site argument at Lehmer", flush=True)

print("\nL5: d-shift control at Lehmer (mis-centring via d instead of m0)", flush=True)
mp.mp.dps = 50
a5_dp = float(mp.re(mp.taylor(make_f(m0_true, d_true+mp.mpf('1e-13')), 0, 6)[5]))*120.0
a5_dm = float(mp.re(mp.taylor(make_f(m0_true, d_true-mp.mpf('1e-13')), 0, 6)[5]))*120.0
print(f"  Lehmer d-shift +-1e-13 (m0 exact): a5 = {a5_dp:+.6f} / {a5_dm:+.6f}"
      f"  (m0-shift gave 17.871/18.942)", flush=True)
print("\nNOTE (post-run, see heat51d): the L3 ladder is SMOOTH, slope -240/d^6", flush=True)
print("  = -5.351e12/unit, matching the closed-form off-centre own-pair residue", flush=True)
print("  da_j = -2*j!*eps/d^(j+1) (odd j). 'Chaos' was the wrong frame: the", flush=True)
print("  instrument was computing the honest LOCAL coefficient; the quantity", flush=True)
print("  itself is eps-ultraviolet at tight pairs. Erratum issued.", flush=True)
print("done", flush=True)
