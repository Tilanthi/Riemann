"""Quick-look (NOT a full pre-registered probe) at the k=2 member of Suzuki's family
(arXiv:1204.1823, Theorem 2.3): h^<2>(x) = (1/sqrt(x)) * sum_n c_omega(n) * g^<2>(n/x),
where g^<2>(x) = int_x^1 sqrt(y/x) * g^<1>(y) dy/y, g^<1> = g_omega (already coded).

g^<2> is a UNIVERSAL function of a single variable x in (0,1) (doesn't depend on n),
so it's precomputed ONCE via numerical quadrature on a grid, then interpolated --
avoiding the cost of a fresh integral per lattice point n.
"""
import numpy as np
from scipy import special, integrate, interpolate
import sys, time
sys.path.insert(0, '/tmp')

def g1(x, omega):
    """g_omega^<1>(x) = g_omega(x), the existing formula, scalar version."""
    if x <= 0 or x >= 1:
        return 0.0
    pref = (4*omega/(2*omega-1)) * (np.pi**omega / special.gamma(omega))
    term1 = x**(omega-1) * special.beta((3-2*omega)/2, omega) * special.betaincc((3-2*omega)/2, omega, x**2)
    term2 = ((2*omega+1)/(4*omega)) * x**(-0.5) * special.beta((5-2*omega)/4, omega) * special.betaincc((5-2*omega)/4, omega, x**2)
    return pref * (term1 - term2)

def g2_at(x, omega):
    """g^<2>(x) = int_x^1 sqrt(y/x) g1(y) dy/y, via numerical quadrature."""
    if x <= 0 or x >= 1:
        return 0.0
    def integrand(y):
        return np.sqrt(y/x) * g1(y, omega) / y
    val, err = integrate.quad(integrand, x, 1.0, limit=200)
    return val

if __name__ == '__main__':
    omega = 0.1  # start with a value already well-validated for k=1
    # build a grid of g^<2> on (0,1), precompute once
    print("Building g^<2> grid (quick-look, own implementation)...")
    t0 = time.time()
    xs_grid = np.concatenate([np.linspace(1e-6, 0.01, 200), np.linspace(0.01, 0.999, 500)])
    xs_grid = np.unique(xs_grid)
    g2_vals = np.array([g2_at(x, omega) for x in xs_grid])
    print(f"grid built in {time.time()-t0:.1f}s, {len(xs_grid)} points")
    interp = interpolate.interp1d(xs_grid, g2_vals, kind='cubic', bounds_error=False, fill_value=0.0)

    # sanity check: g2 should be positive? check sign pattern
    print("g^<2> sample values:", [(float(x), float(interp(x))) for x in [0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99]])

    # small-N quick test of h^<2>(x) at a few modest x values (NOT the full N_MAX battery)
    from math import gcd
    def mobius_and_c_omega(N, omega):
        # simple sieve-based c_omega(n) for small N (not optimized, quick-look only)
        c = np.zeros(N+1)
        is_prime = np.ones(N+1, dtype=bool)
        is_prime[0:2] = False
        for p in range(2, int(N**0.5)+1):
            if is_prime[p]:
                is_prime[p*p::p] = False
        primes = np.nonzero(is_prime)[0]
        factor = np.ones(N+1)
        for p in primes:
            factor[p::p] *= (1 - p**(-2.0*omega))
        n_arr = np.arange(0, N+1, dtype=np.float64)
        n_arr[0] = 1.0
        c = (n_arr**omega) * factor
        return c

    N = 2_000_000
    c_arr = mobius_and_c_omega(N, omega)
    for x in [1e4, 1e5, 5e5, 1e6, 2e6]:
        Nx = int(x)
        if Nx > N:
            continue
        n_arr = np.arange(1, Nx+1)
        t_arr = n_arr / x
        g2_arr = interp(t_arr)
        total = np.sum(c_arr[1:Nx+1] * g2_arr)
        h2 = total / np.sqrt(x)
        print(f"x={x:.0e}: h^<2>(x) = {h2:.6e}  sign={'+' if h2>0 else '-'}")
