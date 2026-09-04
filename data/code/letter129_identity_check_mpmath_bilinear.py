"""
Term-by-term identity check against Mac's exported data/machine1_heat72k_identity_target_m8.json.

Kowalski Prop 1.2.1 (scalar):
  sum_p sum_{k>=1} (log p)(phi(p^k)+psi(p^k)) = int_0^inf phi(x)dx - sum_rho phihat(rho) + Arch[phihat]
  where psi(x) = (1/x) phi(1/x), Arch[phihat] = (1/2pi i) int_(-1/2) [(1/2)G'/G(s/2) - (1/2)G'/G((1-s)/2)] phihat(s) ds

Bilinear form (Phi_ij = phi_i * h_j convolution, per L119/L120): Phihat_ij(s) = u_i(s)*u_j(1-s).
Rearranged identity, per term:
  K_FE[i,j] = Endpoint[i,j] - Prime[i,j] + Arch[i,j]
  Endpoint[i,j] = u_i(1)*u_j(0)                              (= U1[i]*U0[j], Mac's export)
  Prime[i,j]    = sum_p sum_k (log p) * { p^-k * INT1(i,j,k,p) + INT2(i,j,k,p) }
                  INT1 = int phi_i(tau) phi_j(tau - k log p) e^tau dtau
                  INT2 = int phi_i(tau) phi_j(tau + k log p) e^tau dtau
  Arch[i,j]     = (1/2pi) int_{-inf}^{inf} [(1/2)psi_dg(-1/4+it/2) - (1/2)psi_dg(3/4-it/2)] *
                         u_i(-1/2+it) u_j(3/2-it) dt
                  (s=-1/2+it, digamma psi_dg = Gamma'/Gamma)

This script computes Prime and Arch directly (Endpoint from Mac's export), and checks
K_FE[i,j] =?= Endpoint[i,j] - Prime[i,j] + Arch[i,j] against Mac's exported K_FE (T=200/150 bracket).
"""
import json, sys, time
import mpmath as mp

def theta(s):
    if s <= 0: return mp.mpf(0)
    if s >= 1: return mp.mpf(1)
    return mp.e**(-1/s) / (mp.e**(-1/s) + mp.e**(-1/(1-s)))

def w(x):
    ax = abs(x)
    if ax >= 8: return mp.mpf(0)
    return theta((8 - ax) / 2)

def bump(t):
    if abs(t) >= 1: return mp.mpf(0)
    return mp.e**(-1/(1 - t*t))

class TestFn:
    def __init__(self, bumps):
        self.bumps = [(mp.mpf(c), mp.mpf(mu), mp.mpf(s)) for c, mu, s in bumps]
        # actual compact support extent (union of bump intervals, clipped to [-8,8])
        los = [max(mp.mpf(-8), mu - s) for c, mu, s in self.bumps]
        his = [min(mp.mpf(8), mu + s) for c, mu, s in self.bumps]
        self.supp_lo = min(los)
        self.supp_hi = max(his)

    def f(self, x):
        tot = mp.mpf(0)
        for c, mu, s in self.bumps:
            t = (x - mu) / s
            if abs(t) < 1:
                tot += c * bump(t)
        return tot

    def phi(self, x):
        wx = w(x)
        if wx == 0: return mp.mpf(0)
        return wx * self.f(x)

    def breakpoints(self):
        pts = {mp.mpf(-8), mp.mpf(-6), mp.mpf(6), mp.mpf(8)}
        for c, mu, s in self.bumps:
            lo, hi = mu - s, mu + s
            if -8 < lo < 8: pts.add(lo)
            if -8 < hi < 8: pts.add(hi)
        return sorted(pts)

def load_genome(seed_key, n):
    d = json.load(open('/workspace/Riemann/repo/data/code/machine1_heat70_genomes_m8_m64.json'))
    g = d['genomes'][seed_key]
    assert len(g) == n
    return [TestFn(bumps) for bumps in g]

def u_of_s(fi, s, pts=None):
    """u_i(s) = int phi_i(x) e^{s x} dx, s complex or real."""
    if pts is None: pts = fi.breakpoints()
    re = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).real, pts)
    im = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).imag, pts)
    return mp.mpc(re, im)

# ---------- Prime side ----------
def prime_side_entry(fi, fj, log_primes_k, verbose=False):
    """log_primes_k: list of (log p, k, weight=log p) tuples to sum over (precomputed candidates)."""
    total = mp.mpf(0)
    pts_i = fi.breakpoints()
    for logp, k in log_primes_k:
        shift = k * logp
        # INT1: phi_i(tau) phi_j(tau - shift) e^tau dtau, tau in overlap of [fi.supp] and [fj.supp + shift]
        lo1 = max(fi.supp_lo, fj.supp_lo + shift)
        hi1 = min(fi.supp_hi, fj.supp_hi + shift)
        if lo1 < hi1:
            bpts = sorted(set([lo1, hi1]) | {p for p in pts_i if lo1 < p < hi1} |
                           {p + shift for p in fj.breakpoints() if lo1 < p + shift < hi1})
            int1 = mp.quad(lambda tau: fi.phi(tau) * fj.phi(tau - shift) * mp.e**tau, bpts)
        else:
            int1 = mp.mpf(0)
        # INT2: phi_i(tau) phi_j(tau + shift) e^tau dtau
        lo2 = max(fi.supp_lo, fj.supp_lo - shift)
        hi2 = min(fi.supp_hi, fj.supp_hi - shift)
        if lo2 < hi2:
            bpts2 = sorted(set([lo2, hi2]) | {p for p in pts_i if lo2 < p < hi2} |
                            {p - shift for p in fj.breakpoints() if lo2 < p - shift < hi2})
            int2 = mp.quad(lambda tau: fi.phi(tau) * fj.phi(tau + shift) * mp.e**tau, bpts2)
        else:
            int2 = mp.mpf(0)
        contrib = logp * (mp.e**(-k*logp) * int1 + int2)
        total += contrib
    return total

def build_prime_candidates(max_shift):
    """All (log p, k) with k*log(p) <= max_shift, via sieve."""
    import numpy as np
    # need primes up to exp(max_shift)
    Nmax = int(mp.e**max_shift) + 10
    Nmax = min(Nmax, 2_000_000)  # safety cap
    is_prime = [True]*(Nmax+1)
    is_prime[0:2] = [False, False]
    for p in range(2, int(Nmax**0.5)+1):
        if is_prime[p]:
            for m in range(p*p, Nmax+1, p):
                is_prime[m] = False
    primes = [p for p in range(2, Nmax+1) if is_prime[p]]
    cands = []
    for p in primes:
        logp = mp.log(p)
        k = 1
        while k*logp <= max_shift:
            cands.append((logp, k))
            k += 1
    return cands

# ---------- Archimedean side ----------
def digamma_half(s):
    return mp.digamma(s/2)

def arch_side_entry(fi, fj, t_max=60):
    """Arch[i,j] = (1/2pi) int_{-inf}^{inf} [(1/2)psi(( -1/2+it)/2) - (1/2)psi((3/2-it)/2)] u_i(-1/2+it) u_j(3/2-it) dt"""
    def integrand(t):
        s = mp.mpc(mp.mpf('-0.5'), t)
        kernel = mp.mpf('0.5')*digamma_half(s) - mp.mpf('0.5')*digamma_half(1-s)
        ui = u_of_s(fi, s)
        uj = u_of_s(fj, 1-s)
        return (kernel * ui * uj)
    # integrate real part (imaginary part should cancel by symmetry, check both)
    re = mp.quad(lambda t: integrand(t).real, [-t_max, -20, -5, 0, 5, 20, t_max])
    im = mp.quad(lambda t: integrand(t).imag, [-t_max, -20, -5, 0, 5, 20, t_max])
    return mp.mpc(re, im) / (2*mp.pi)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', default='s1')
    ap.add_argument('--dps', type=int, default=30)
    ap.add_argument('--ij', default='0,0')
    ap.add_argument('--tmax', type=float, default=60)
    args = ap.parse_args()
    mp.mp.dps = args.dps

    fns = load_genome(f"{args.seed}/M8", 8)
    d = json.load(open('/workspace/Riemann/repo/data/machine1_heat72k_identity_target_m8.json'))
    tgt = d['seeds'][f"{args.seed}/M8"]

    i, j = [int(x) for x in args.ij.split(',')]
    fi, fj = fns[i], fns[j]

    print(f"seed={args.seed} (i,j)=({i},{j}) dps={args.dps}")

    # Endpoint from Mac's export directly
    U0 = [mp.mpf(x) for x in tgt['U0']]
    U1 = [mp.mpf(x) for x in tgt['U1']]
    endpoint = U1[i] * U0[j]
    print(f"Endpoint (from Mac's export) = {endpoint}")

    # Prime side, computed by me
    t0 = time.time()
    max_shift = fi.supp_hi - fi.supp_lo + fj.supp_hi - fj.supp_lo  # generous bound
    max_shift = float(max_shift) + 1
    cands = build_prime_candidates(max_shift)
    print(f"  prime candidates (k*log p <= {max_shift:.2f}): {len(cands)}")
    prime = prime_side_entry(fi, fj, cands)
    t1 = time.time()
    print(f"Prime side = {prime}  [{t1-t0:.1f}s]")

    # Archimedean side, computed by me
    t0 = time.time()
    arch = arch_side_entry(fi, fj, t_max=args.tmax)
    t1 = time.time()
    print(f"Arch side = {arch}  [{t1-t0:.1f}s]")

    identity_rhs = endpoint - prime + arch
    print(f"\nIdentity RHS (Endpoint - Prime + Arch) = {identity_rhs}")

    K200 = mp.mpf(tgt['K_T200'][i][j])
    K150 = mp.mpf(tgt['K_T150'][i][j])
    print(f"Mac's K_T200[{i}][{j}] = {K200}")
    print(f"Mac's K_T150[{i}][{j}] = {K150}")
    diff200 = abs(identity_rhs.real - K200) / abs(K200) if K200 != 0 else abs(identity_rhs.real - K200)
    print(f"rel diff vs K_T200: {diff200}")
    print(f"K_T200 - K_T150 bracket: {abs(K200-K150)}")
