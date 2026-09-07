"""
m3-L177 build, gate KAT-1-equivalent: the classical Weil explicit formula (poles + archimedean +
primes) applied to a GAUSSIAN test function (general, not tied to the compact-support basis used for
the matrix), checked against a DIRECT SUM over the zeta zeros themselves via mpmath.zetazero -- an
instrument with no shared code/data/convention with anything else built in this exercise. This is the
gate that must pass before the matrix code (which reuses the SAME archimedean-rewrite formula) is
trusted. Independent implementation of the same KIND of check BEAST's own KAT-1 describes; built from
the classical explicit-formula convention in section 1 of c42/README.md, not from BEAST's code.
"""
import mpmath as mp
import time


def explicit_formula_gaussian(s, dps, prime_n_max, t_quad_range):
    """
    g(t) = exp(-t^2/(2 s^2)),  h(r) = s sqrt(2 pi) exp(-s^2 r^2/2)  [standard Gaussian FT pair]
    W(g) = h(i/2)+h(-i/2) - g(0) log(pi)
           - gammaE g(0) + 2 INT_0^inf [e^{-2t} g(0) - e^{-t/2} g(t)]/(1-e^{-2t}) dt
           - 2 SUM_{n>=2} Lambda(n) n^{-1/2} g(log n)
    Returns (total, pole, arch, prime) all as mpf.
    """
    mp.mp.dps = dps
    s = mp.mpf(s)

    def g(t):
        return mp.e ** (-(t ** 2) / (2 * s ** 2))

    def h(r):
        return s * mp.sqrt(2 * mp.pi) * mp.e ** (-(s ** 2) * (r ** 2) / 2)

    g0 = g(mp.mpf(0))
    half_i = mp.mpc(0, mp.mpf('0.5'))
    pole = (h(half_i) + h(-half_i)).real - g0 * mp.log(mp.pi)

    def arch_integrand(t):
        if t == 0:
            # removable; use a tiny offset consistently with the rest of the build
            t = mp.mpf('1e-30')
        num = mp.e ** (-2 * t) * g0 - mp.e ** (-t / 2) * g(t)
        den = 1 - mp.e ** (-2 * t)
        return num / den

    # BUG FOUND+FIXED (self-caught: arm B's residual came out dps-INDEPENDENT at ~8.7565e-27, which
    # is exactly e^-60 -- confirmed by direct comparison -- meaning it was the truncation error of
    # cutting this integral at t_quad_range=30 (e^{-2*30}), not a precision floor at all. Fixed by
    # integrating out to a range where e^{-2T} is far below any working precision used here.)
    T = max(t_quad_range, dps)  # e^{-2*dps} is comfortably below 10^-dps
    arch = -mp.euler * g0 + 2 * mp.quad(arch_integrand, [0, T])

    def mangoldt(n):
        if n < 2:
            return mp.mpf(0)
        m, p, d = n, None, 2
        while d * d <= m:
            if m % d == 0:
                p = d
                while m % d == 0:
                    m //= d
                break
            d += 1
        if p is None:
            p, m = m, 1
        return mp.log(p) if m == 1 else mp.mpf(0)

    prime = mp.mpf(0)
    for n in range(2, prime_n_max + 1):
        lam = mangoldt(n)
        if lam != 0:
            prime += lam / mp.sqrt(mp.mpf(n)) * g(mp.log(mp.mpf(n)))
    prime = -2 * prime

    total = pole + arch + prime
    return total, pole, arch, prime


def zero_side_gaussian(s, dps, n_zeros):
    mp.mp.dps = dps
    s = mp.mpf(s)

    def h(r):
        return s * mp.sqrt(2 * mp.pi) * mp.e ** (-(s ** 2) * (r ** 2) / 2)

    total = mp.mpf(0)
    for n in range(1, n_zeros + 1):
        gamma_n = mp.zetazero(n).imag
        total += h(gamma_n)
    return 2 * total


if __name__ == '__main__':
    t0 = time.time()
    print("=== KAT-1-equivalent gate: arm A (narrow Gaussian, s=0.2) ===", flush=True)
    W, pole, arch, prime = explicit_formula_gaussian(s='0.2', dps=50, prime_n_max=4000,
                                                       t_quad_range=30)
    print(f"pole={pole}  arch={arch}  prime={prime}", flush=True)
    print(f"W (formula side) = {W}", flush=True)
    Z = zero_side_gaussian(s='0.2', dps=50, n_zeros=40)
    print(f"Z (zero side, 40 zeros) = {Z}", flush=True)
    reldiff = abs(W - Z) / abs(Z)
    print(f"relative difference = {reldiff}  [{time.time()-t0:.1f}s]", flush=True)

    print("\n=== KAT-1-equivalent gate: arm B (wide Gaussian, s=1, sharp cancellation test) ===",
          flush=True)
    t1 = time.time()
    W2, pole2, arch2, prime2 = explicit_formula_gaussian(s='1', dps=50, prime_n_max=300000,
                                                          t_quad_range=30)
    print(f"pole={pole2}  arch={arch2}  prime={prime2}", flush=True)
    print(f"W (formula side) = {W2}", flush=True)
    Z2 = zero_side_gaussian(s='1', dps=50, n_zeros=40)
    print(f"Z (zero side, 40 zeros) = {Z2}", flush=True)
    print(f"abs(W) after cancellation of O(size) terms = {abs(W2)}  [{time.time()-t1:.1f}s]",
          flush=True)

    print(f"\n[{time.time()-t0:.1f}s] done", flush=True)
