"""
CORRECTED scalar Kowalski identity check (v2), fixing the bug Mac found (L132, dd50654):
kernel must be the SUM of the two half-digammas minus log(pi), not their difference:

  kernel(s) = (1/2)psi(s/2) + (1/2)psi((1-s)/2) - log(pi)

(derived from Lambda(s)=pi^{-s/2}Gamma(s/2)zeta(s), Lambda'/Lambda(s)=Lambda'/Lambda(1-s):
 -zeta'/zeta(s) = zeta'/zeta(1-s) + kernel(s))

My original v1 (letter129_scalar_identity_check.py) had the DIFFERENCE form (no -log pi), which
decays like 1/t^2 in real part instead of growing like log(t/2pi) -- "an integrand with no
archimedean content", per Mac's diagnosis. My complex-product contraction (Re[K(t)*u(t)], not
Re[K(t)]*Re[u(t)]) was already correct and needed no fix.
"""
import sys
sys.path.insert(0, '/tmp')
from scalar_identity_check import load_genome, u_of_s, prime_side_scalar, zero_side_scalar
import numpy as np
from scipy import special, integrate
import time

def digamma_half(s):
    return special.digamma(s / 2)

def kernel_correct(s):
    return 0.5 * digamma_half(s) + 0.5 * digamma_half(1 - s) - np.log(np.pi)

def arch_side_v2(fi, t_max=150):
    def integrand(t):
        s = complex(-0.5, t)
        kernel = kernel_correct(s)
        u = u_of_s(fi, s)
        return kernel * u  # complex product; contraction is Re of this
    re, ere = integrate.quad(lambda t: integrand(t).real, -t_max, t_max,
                              points=[-20, -5, 0, 5, 20], limit=400, epsabs=1e-13, epsrel=1e-11)
    im, eim = integrate.quad(lambda t: integrand(t).imag, -t_max, t_max,
                              points=[-20, -5, 0, 5, 20], limit=400, epsabs=1e-13, epsrel=1e-11)
    return complex(re, im) / (2 * np.pi)

if __name__ == '__main__':
    fns = load_genome('s1/M8', 8)
    targets = {0: 0.102851814149, 1: -0.559823222, 2: -0.028490956, 3: 0.321824777}
    for idx in [0, 1, 2, 3]:
        f = fns[idx]
        t0 = time.time()
        u1 = u_of_s(f, 1.0 + 0j)
        endpoint = u1.real
        prime, nterms = prime_side_scalar(f)
        zero, nz = zero_side_scalar(f, T=150)
        arch = arch_side_v2(f, t_max=150)
        rhs = endpoint - prime + arch
        gap = rhs - zero
        target = targets[idx]
        print(f"basis {idx}: Arch(v2)={arch}  target={target}  arch_closure={arch.real-target:.2e}")
        print(f"  Endpoint={endpoint:.6f} Prime={prime:.6f} Zero(T150)={zero:.6f} RHS={rhs}  gap(RHS-Zero)={gap}  [{time.time()-t0:.1f}s]")
