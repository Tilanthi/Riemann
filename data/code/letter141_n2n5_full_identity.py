"""
N2/N5 witness-test build, step 1: bilinear Endpoint/Prime/Arch terms with the CORRECTED kernel
(Mac's L132 fix: sum form minus log(pi), independently re-derived and confirmed by BEAST's cycle 21),
validated against Mac's exported on-line K_FE (data/machine1_heat72k_identity_target_m8.json).

Identity: K_FE[i,j] = Endpoint[i,j] - Prime[i,j] + Arch[i,j]
  Endpoint[i,j] = u_i(1)*u_j(0)
  Prime[i,j]    = sum_p sum_k (log p) * { p^-k * INT1(i,j,k,p) + INT2(i,j,k,p) }
                  INT1 = int phi_i(tau) phi_j(tau - k log p) e^tau dtau
                  INT2 = int phi_i(tau) phi_j(tau + k log p) e^tau dtau
  Arch[i,j]     = (1/2pi) int Re[ K(t) * u_i(-1/2+it) * u_j(3/2-it) ] dt
                  K(t) = 0.5*digamma(s/2) + 0.5*digamma((1-s)/2) - log(pi), s=-1/2+it   [CORRECTED]
"""
import sys, time
sys.path.insert(0, '/tmp')
from identity_check_fast import load_genome, u_of_s_scipy as u_of_s
import numpy as np
from scipy import special, integrate
import json

def digamma_half(s):
    return special.digamma(s / 2)

def kernel_correct(s):
    return 0.5 * digamma_half(s) + 0.5 * digamma_half(1 - s) - np.log(np.pi)

def endpoint_entry(fi, fj, U1, U0, i, j):
    return U1[i] * U0[j]

def prime_side_fast(fi, fj, max_shift, grid_n=400):
    shifts = np.linspace(0, max_shift, grid_n)

    def cross_corr(mode):
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

    from scipy import interpolate
    Cvals = cross_corr('sub')
    Dvals = cross_corr('add')
    Cinterp = interpolate.interp1d(shifts, Cvals, kind='cubic', bounds_error=False, fill_value=0.0)
    Dinterp = interpolate.interp1d(shifts, Dvals, kind='cubic', bounds_error=False, fill_value=0.0)

    Nmax = int(np.exp(max_shift)) + 10
    Nmax = min(Nmax, 3_000_000)
    is_prime = np.ones(Nmax + 1, dtype=bool)
    is_prime[0:2] = False
    for p in range(2, int(Nmax ** 0.5) + 1):
        if is_prime[p]:
            is_prime[p * p::p] = False
    primes = np.nonzero(is_prime)[0]

    total = 0.0
    for p in primes:
        logp = np.log(p)
        k = 1
        while k * logp <= max_shift:
            shift = k * logp
            c = float(Cinterp(shift))
            d = float(Dinterp(shift))
            if c != 0.0 or d != 0.0:
                total += logp * (np.exp(-k * logp) * c + d)
            k += 1
    return total

def arch_entry_corrected(fi, fj, t_max=150):
    def integrand(t):
        s = complex(-0.5, t)
        kernel = kernel_correct(s)
        ui = u_of_s(fi, s)
        uj = u_of_s(fj, 1 - s)
        return kernel * ui * uj
    re, _ = integrate.quad(lambda t: integrand(t).real, -t_max, t_max,
                            points=[-20, -5, 0, 5, 20], limit=400, epsabs=1e-13, epsrel=1e-11)
    im, _ = integrate.quad(lambda t: integrand(t).imag, -t_max, t_max,
                            points=[-20, -5, 0, 5, 20], limit=400, epsabs=1e-13, epsrel=1e-11)
    return complex(re, im) / (2 * np.pi)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', default='s1')
    ap.add_argument('--ij', default='0,0')
    ap.add_argument('--tmax', type=float, default=150)
    args = ap.parse_args()

    fns = load_genome(f"{args.seed}/M8", 8)
    d = json.load(open('/workspace/Riemann/repo/data/machine1_heat72k_identity_target_m8.json'))
    tgt = d['seeds'][f"{args.seed}/M8"]

    i, j = [int(x) for x in args.ij.split(',')]
    fi, fj = fns[i], fns[j]
    print(f"seed={args.seed} (i,j)=({i},{j})")

    U0 = [float(x) for x in tgt['U0']]
    U1 = [float(x) for x in tgt['U1']]
    endpoint = endpoint_entry(fi, fj, U1, U0, i, j)
    print(f"Endpoint = {endpoint}")

    max_shift = max(fi.supp_hi - fj.supp_lo, fj.supp_hi - fi.supp_lo)
    t0 = time.time()
    prime = prime_side_fast(fi, fj, max_shift)
    t1 = time.time()
    print(f"Prime = {prime}  [{t1-t0:.1f}s]")

    t0 = time.time()
    arch = arch_entry_corrected(fi, fj, t_max=args.tmax)
    t1 = time.time()
    print(f"Arch (corrected kernel) = {arch}  [{t1-t0:.1f}s]")

    rhs = endpoint - prime + arch
    K200 = float(tgt['K_T200'][i][j])
    K150 = float(tgt['K_T150'][i][j])
    print(f"\nRHS (Endpoint - Prime + Arch) = {rhs}")
    print(f"Mac's K_T200[{i}][{j}] = {K200}")
    print(f"Mac's K_T150[{i}][{j}] = {K150}")
    rel = abs(rhs.real - K200) / abs(K200) if K200 != 0 else abs(rhs.real - K200)
    print(f"rel diff vs K_T200: {rel:.3e}")
    print(f"K200-K150 bracket: {abs(K200-K150):.3e}")
