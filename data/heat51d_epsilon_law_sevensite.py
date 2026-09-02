"""heat51d — THE epsILON LAW, closed form + seven-site verification.
  SUPERSEDES the 'chaotic input sensitivity' attribution of heat51/51b
  and our arbitration letter §A2 (erratum pushed separately).

  LAW. For a pair-midpoint site (true midpoint m0, half-gap d) evaluated
  at a centre m0' = m0 + eps, the odd-order log-xi Taylor coefficients
  carry the un-cancelled own-pair residue

      a_j(m0') = a_j(m0) - 2*j!*eps/d^(j+1)      (odd j; S_j = sum (m0-gamma)^-j
                                                   convention of the identity)

  while even orders are clean at O(eps) (the pair and the removal factor
  z^2-d^2 are both even about the exact midpoint). Derivation: relative
  to m0', the pair sits at -(eps)+-d_true; its odd-j contribution to S_j
  is +2*j*eps*d^-(j+1) + O(eps^2), and a_j = G_j - (j-1)!*S_j. For j=5:
  delta a_5 = -240*eps/d^6.

  WHAT THIS EXPLAINS (all previously-measured, on-disk):
   * machine 3 letter-8 Lehmer a5 = +17.2788 vs certified +18.406508:
     their JSON/hand m0 was the CORRECTLY-ROUNDED float64 double of the
     true midpoint (verified: double expansion 7005.0817154237838622066
     192328929901123046875 = their JSON value digit-for-digit), eps =
     +2.107e-13 -> delta a5 = -240*2.107e-13/0.018849^6 = -1.1277.
     Observed -1.1277. The instrument was RIGHT about the local
     coefficient; the site was 2e-13 off-centre and nobody labelled it.
   * their letter-8 a3 = +1.537001 vs +1.537022: law j=3,
     delta a3 = -12*eps/d^4 = -2.0e-5. Observed -2.1e-5.
   * our heat51 P3 float64-table site (eps = +7.158e-10): law gives
     -3831.2 -> a5 = 18.4065 - 3831.2 = -3812.8. Observed -3812.92.
   * heat51c L3 ladder: exact -> +18.406508; +1e-13 -> -0.535 (obs
     17.871); -1e-13 -> +0.535 (obs 18.942); +5e-13 -> -2.68 (obs
     15.731); +1e-12 -> -5.35 (obs 13.055). All dps-stable: the
     response is DETERMINISTIC-linear, not noise.
   * d-shift +-1e-13 at exact m0: law says delta a5 = 0. Observed 0.
   * their letter-8 kappa6 at Lehmer was CORRECT (even order, O(eps^2)).
  OPEN detail: our heat51 P3 a6 at the eps=7e-10 site was off by ~1e6 —
  beyond the O(eps) law (even order); not needed for any published value.

  TWO-INSTRUMENT DISTINCTION (why our contour agreed with the certified
  exact-site values at OUR OWN eps=7e-10 table site): the contour extracts
  POSITIVE Fourier modes of the branch-unwrapped boundary log. The
  near-cancelled interior zero-pole cluster (separation ~1.4e-9) expands
  on |z|=r as eps/(z-d) = eps*sum d^k z^-(k+1) — NEGATIVE modes only.
  So contour+unwrap measures the pair-extracted (site-invariant)
  coefficient; FD/mp.taylor measures the honest local coefficient. They
  coincide iff eps = 0. Both are correct answers to different questions.

  SEVEN-SITE TEST (this script's run): machine 3's T2g (old, letter-8
  era) vs T2h (certified, fresh high-precision sites) kappa5_jet per
  site; eps = m0_old - m0_new(T2h); prediction -240*eps/d_new^6.
"""
import json
import mpmath as mp

mp.mp.dps = 50
old = json.load(open("/Users/gjw255/astrodata/SWARM/Riemann_exchange/data/"
                     "T2g_kappa5_coefficients.json"))["sites"]
new = json.load(open("/Users/gjw255/astrodata/SWARM/Riemann_exchange/data/"
                     "T2h_certified_identity_gated.json"))
print("seven-site law test: obs (a5_old - a5_new) vs pred -240*eps/d^6")
print(f"{'site':10s} {'eps':>12s} {'d':>10s} {'pred dA5':>12s} {'obs dA5':>12s} {'ratio':>8s}")
tot = 0
for site in ("k453", "k693", "k922", "k1166", "Lehmer", "telescope", "W_site"):
    m0_old = mp.mpf(old[site]["m0"]); a5_old = mp.mpf(old[site]["jet"]["a5"])
    m0_new = mp.mpf(new[site]["m0"]); a5_new = mp.mpf(new[site]["kappa5_jet"])
    d_new = mp.mpf(new[site]["d"])
    eps = m0_old - m0_new
    pred = -240*eps/mp.power(d_new, 6)
    obs = a5_old - a5_new
    ratio = obs/pred if pred != 0 else mp.inf
    ok = abs(ratio - 1) < 0.05
    tot += ok
    print(f"{site:10s} {mp.nstr(eps, 4):>12s} {mp.nstr(d_new, 4):>10s} "
          f"{mp.nstr(pred, 5):>12s} {mp.nstr(obs, 5):>12s} {mp.nstr(ratio, 4):>8s} "
          f"{'OK' if ok else '--'}", flush=True)
print(f"\n{tot}/7 sites: old-minus-new kappa5 == -240*eps/d^6 within 5%")

# double-identity check for Lehmer: is their old JSON m0 exactly the
# correctly-rounded float64 of the true midpoint?
m0_true = mp.mpf(new["Lehmer"]["m0"])
dbl = mp.mpf(float(m0_true))
print("\nLehmer provenance: float64(true m0) =", mp.nstr(dbl, 45))
print("                     their old JSON  =", old["Lehmer"]["m0"])
print("  equal:", dbl == mp.mpf(old["Lehmer"]["m0"]),
      " eps(double) =", mp.nstr(dbl - m0_true, 4))
print("done", flush=True)
