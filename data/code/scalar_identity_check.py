"""
SCALAR (non-bilinear) Kowalski Prop 1.2.1 identity check, to isolate whether the archimedean-term
numerical method is correct, decoupled from the bilinear-convolution complexity.

sum_p sum_k (log p)(phi(p^k) + psi(p^k)) = int_0^inf phi(y) dy - sum_rho phihat(rho) + Arch[phihat]
  psi(y) = (1/y) phi(1/y)

In my x=log y convention (TestFn.phi(x) == Kowalski's phi(e^x)):
  phi(p^k)   -> TestFn.phi(k*log p)
  psi(p^k) = (1/p^k) phi(1/p^k) -> p^-k * TestFn.phi(-k*log p)
  int_0^inf phi(y)dy = phihat(1) = u(1)
  sum_rho phihat(rho) = sum over ALL nontrivial zeros (upper+lower half) = sum_n 2*Re[u(rho_n)]
     (using u(conj(s))=conj(u(s)) for real test function, rho_n=1/2+i*gamma_n)
  Arch[phihat] = (1/2pi) int_{-inf}^{inf} [(1/2)digamma((-1/2+it)/2) - (1/2)digamma((3/2-it)/2)] u(-1/2+it) dt
"""
import numpy as np
from scipy import special, integrate
import mpmath as mp
import sys, time
sys.path.insert(0, '/tmp')
from identity_check_fast import load_genome, TestFn

def u_of_s(fi, s):
    pts = fi.breakpoints()
    def re_f(x): return (fi.phi(x) * np.exp(s * x)).real
    def im_f(x): return (fi.phi(x) * np.exp(s * x)).imag
    re, _ = integrate.quad(re_f, pts[0], pts[-1], points=pts[1:-1], limit=200, epsabs=1e-13)
    im, _ = integrate.quad(im_f, pts[0], pts[-1], points=pts[1:-1], limit=200, epsabs=1e-13)
    return complex(re, im)

def prime_side_scalar(fi, max_shift=None):
    if max_shift is None:
        max_shift = fi.supp_hi - fi.supp_lo  # phi(k log p) needs k log p in [supp_lo,supp_hi]; psi needs -k log p in [supp_lo,supp_hi]
    Nmax = int(np.exp(max_shift)) + 10
    Nmax = min(Nmax, 3_000_000)
    is_prime = np.ones(Nmax+1, dtype=bool); is_prime[0:2]=False
    for p in range(2, int(Nmax**0.5)+1):
        if is_prime[p]: is_prime[p*p::p]=False
    primes = np.nonzero(is_prime)[0]
    total = 0.0
    nterms = 0
    for p in primes:
        logp = np.log(p)
        k = 1
        while k*logp <= max_shift + 1e-9:
            shift = k*logp
            v1 = fi.phi(shift) if fi.supp_lo <= shift <= fi.supp_hi else 0.0
            v2 = (np.exp(-k*logp) * fi.phi(-shift)) if fi.supp_lo <= -shift <= fi.supp_hi else 0.0
            if v1 != 0.0 or v2 != 0.0:
                total += logp * (v1 + v2)
                nterms += 1
            k += 1
    return total, nterms

def zero_side_scalar(fi, T=100):
    mp.mp.dps = 30
    total = 0.0
    n = 1
    while True:
        z = mp.zetazero(n)
        gamma = float(mp.im(z))
        if gamma > T:
            break
        s = complex(0.5, gamma)
        u = u_of_s(fi, s)
        total += 2*u.real
        n += 1
    return total, n-1

def digamma_half(s):
    return special.digamma(s/2)

def arch_side_scalar(fi, t_max=80, npts_report=False):
    def integrand(t):
        s = complex(-0.5, t)
        kernel = 0.5*digamma_half(s) - 0.5*digamma_half(1-s)
        u = u_of_s(fi, s)
        return kernel * u
    re, err = integrate.quad(lambda t: integrand(t).real, -t_max, t_max, limit=400, epsabs=1e-13, epsrel=1e-11)
    im, errim = integrate.quad(lambda t: integrand(t).imag, -t_max, t_max, limit=400, epsabs=1e-13, epsrel=1e-11)
    if npts_report:
        print(f"  arch quad errest: re={err:.2e} im={errim:.2e}")
    return complex(re, im) / (2*np.pi)

if __name__ == '__main__':
    fns = load_genome('s1/M8', 8)
    f0 = fns[0]
    print("supp:", f0.supp_lo, f0.supp_hi)

    u1 = u_of_s(f0, 1.0+0j)
    endpoint = u1.real
    print(f"Endpoint u(1) = {u1}")

    t0=time.time()
    prime, nterms = prime_side_scalar(f0)
    print(f"Prime = {prime}  ({nterms} terms) [{time.time()-t0:.1f}s]")

    t0=time.time()
    zero, nzeros = zero_side_scalar(f0, T=100)
    print(f"Zero side (T=100, {nzeros} zeros) = {zero} [{time.time()-t0:.1f}s]")

    t0=time.time()
    arch = arch_side_scalar(f0, t_max=80, npts_report=True)
    print(f"Arch = {arch} [{time.time()-t0:.1f}s]")

    rhs = endpoint - prime + arch
    print(f"\nRHS (Endpoint - Prime + Arch) = {rhs}")
    print(f"Zero side (LHS, T=100 truncated) = {zero}")
    print(f"diff = {rhs - zero}")
