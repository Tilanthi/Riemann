"""
Faster (float64/scipy) term-by-term identity check against Mac's
data/machine1_heat72k_identity_target_m8.json export.

Same identity as identity_check_m8.py's docstring:
  K_FE[i,j] = Endpoint[i,j] - Prime[i,j] + Arch[i,j]

Prime side computed via precomputed cross-correlation-type functions C_ij(shift), D_ij(shift)
on a grid + interpolation (fast), rather than per-(p,k) arbitrary-precision quadrature (too slow
for the ~1e4-1e5 candidate primes at this support width). Target precision ~1e-9 to 1e-10,
compared against Mac's own T-bracket tolerance of ~1e-6 -- should be more than sufficient.
"""
import json, time, sys
import numpy as np
from scipy import special, integrate, interpolate

def theta(s):
    if s <= 0: return 0.0
    if s >= 1: return 1.0
    return np.exp(-1/s) / (np.exp(-1/s) + np.exp(-1/(1-s)))

def w(x):
    ax = abs(x)
    if ax >= 8: return 0.0
    return theta((8 - ax) / 2)

def bump(t):
    if abs(t) >= 1: return 0.0
    return np.exp(-1/(1 - t*t))

class TestFn:
    def __init__(self, bumps):
        self.bumps = [(float(c), float(mu), float(s)) for c, mu, s in bumps]
        los = [max(-8.0, mu - s) for c, mu, s in self.bumps]
        his = [min(8.0, mu + s) for c, mu, s in self.bumps]
        self.supp_lo = min(los)
        self.supp_hi = max(his)

    def f(self, x):
        tot = 0.0
        for c, mu, s in self.bumps:
            t = (x - mu) / s
            if abs(t) < 1:
                tot += c * bump(t)
        return tot

    def phi(self, x):
        wx = w(x)
        if wx == 0.0: return 0.0
        return wx * self.f(x)

    def breakpoints(self):
        pts = {-8.0, -6.0, 6.0, 8.0}
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

def u_of_s_scipy(fi, s):
    """u_i(s) = int phi_i(x) e^{s x} dx, s complex (numpy complex128)."""
    pts = fi.breakpoints()
    def re_f(x): return (fi.phi(x) * np.exp(s * x)).real
    def im_f(x): return (fi.phi(x) * np.exp(s * x)).imag
    re, _ = integrate.quad(re_f, pts[0], pts[-1], points=pts[1:-1], limit=200, epsabs=1e-13)
    im, _ = integrate.quad(im_f, pts[0], pts[-1], points=pts[1:-1], limit=200, epsabs=1e-13)
    return complex(re, im)

def cross_corr_grid(fi, fj, shifts, mode):
    """mode='sub': int phi_i(tau) phi_j(tau-shift) e^tau dtau
       mode='add': int phi_i(tau) phi_j(tau+shift) e^tau dtau"""
    vals = np.zeros(len(shifts))
    bpts_i = fi.breakpoints()
    for idx, shift in enumerate(shifts):
        if mode == 'sub':
            lo = max(fi.supp_lo, fj.supp_lo + shift)
            hi = min(fi.supp_hi, fj.supp_hi + shift)
            if lo >= hi:
                continue
            bpts_j = [p + shift for p in fj.breakpoints()]
            pts = sorted(set([lo, hi]) | {p for p in bpts_i if lo < p < hi} | {p for p in bpts_j if lo < p < hi})
            val, _ = integrate.quad(lambda tau: fi.phi(tau) * fj.phi(tau - shift) * np.exp(tau),
                                     pts[0], pts[-1], points=pts[1:-1], limit=200, epsabs=1e-14, epsrel=1e-12)
        else:
            lo = max(fi.supp_lo, fj.supp_lo - shift)
            hi = min(fi.supp_hi, fj.supp_hi - shift)
            if lo >= hi:
                continue
            bpts_j = [p - shift for p in fj.breakpoints()]
            pts = sorted(set([lo, hi]) | {p for p in bpts_i if lo < p < hi} | {p for p in bpts_j if lo < p < hi})
            val, _ = integrate.quad(lambda tau: fi.phi(tau) * fj.phi(tau + shift) * np.exp(tau),
                                     pts[0], pts[-1], points=pts[1:-1], limit=200, epsabs=1e-14, epsrel=1e-12)
        vals[idx] = val
    return vals

def prime_side_fast(fi, fj, max_shift, grid_n=400):
    """Precompute C(shift)=INT1(sub-mode), D(shift)=INT2(add-mode) on a grid, interpolate,
    then sieve primes and sum. shift in [0, max_shift]."""
    shifts = np.linspace(0, max_shift, grid_n)
    Cvals = cross_corr_grid(fi, fj, shifts, 'sub')
    Dvals = cross_corr_grid(fi, fj, shifts, 'add')
    Cinterp = interpolate.interp1d(shifts, Cvals, kind='cubic', bounds_error=False, fill_value=0.0)
    Dinterp = interpolate.interp1d(shifts, Dvals, kind='cubic', bounds_error=False, fill_value=0.0)

    # sieve primes up to exp(max_shift)
    Nmax = int(np.exp(max_shift)) + 10
    Nmax = min(Nmax, 3_000_000)
    is_prime = np.ones(Nmax+1, dtype=bool)
    is_prime[0:2] = False
    for p in range(2, int(Nmax**0.5)+1):
        if is_prime[p]:
            is_prime[p*p::p] = False
    primes = np.nonzero(is_prime)[0]

    total = 0.0
    n_terms = 0
    for p in primes:
        logp = np.log(p)
        k = 1
        while k*logp <= max_shift:
            shift = k*logp
            c = float(Cinterp(shift))
            d = float(Dinterp(shift))
            if c != 0.0 or d != 0.0:
                total += logp * (np.exp(-k*logp) * c + d)
                n_terms += 1
            k += 1
    return total, n_terms, (shifts, Cvals, Dvals)

def digamma_half(s):
    return special.digamma(s/2)

def arch_side_fast(fi, fj, t_max=80):
    def integrand(t):
        s = complex(-0.5, t)
        kernel = 0.5*digamma_half(s) - 0.5*digamma_half(1-s)
        ui = u_of_s_scipy(fi, s)
        uj = u_of_s_scipy(fj, 1-s)
        return kernel * ui * uj
    re, _ = integrate.quad(lambda t: integrand(t).real, -t_max, t_max, limit=200, epsabs=1e-12)
    im, _ = integrate.quad(lambda t: integrand(t).imag, -t_max, t_max, limit=200, epsabs=1e-12)
    return complex(re, im) / (2*np.pi)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', default='s1')
    ap.add_argument('--ij', default='0,0')
    ap.add_argument('--tmax', type=float, default=80)
    args = ap.parse_args()

    fns = load_genome(f"{args.seed}/M8", 8)
    d = json.load(open('/workspace/Riemann/repo/data/machine1_heat72k_identity_target_m8.json'))
    tgt = d['seeds'][f"{args.seed}/M8"]

    i, j = [int(x) for x in args.ij.split(',')]
    fi, fj = fns[i], fns[j]
    print(f"seed={args.seed} (i,j)=({i},{j})")

    U0 = [float(x) for x in tgt['U0']]
    U1 = [float(x) for x in tgt['U1']]
    endpoint = U1[i] * U0[j]
    print(f"Endpoint = {endpoint}")

    max_shift = max(fi.supp_hi - fj.supp_lo, fj.supp_hi - fi.supp_lo)
    print(f"max_shift = {max_shift:.3f}")
    t0 = time.time()
    prime, nterms, _ = prime_side_fast(fi, fj, max_shift)
    t1 = time.time()
    print(f"Prime = {prime}  ({nterms} nonzero terms)  [{t1-t0:.1f}s]")

    t0 = time.time()
    arch = arch_side_fast(fi, fj, t_max=args.tmax)
    t1 = time.time()
    print(f"Arch = {arch}  [{t1-t0:.1f}s]")

    rhs = endpoint - prime + arch
    K200 = float(tgt['K_T200'][i][j])
    K150 = float(tgt['K_T150'][i][j])
    print(f"\nRHS (Endpoint - Prime + Arch) = {rhs}")
    print(f"Mac's K_T200[{i}][{j}] = {K200}")
    print(f"Mac's K_T150[{i}][{j}] = {K150}")
    rel = abs(rhs.real - K200)/abs(K200) if K200 != 0 else abs(rhs.real-K200)
    print(f"rel diff vs K_T200: {rel:.3e}")
    print(f"K200-K150 bracket (Mac's own tolerance floor): {abs(K200-K150):.3e}")
