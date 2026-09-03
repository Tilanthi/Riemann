import numpy as np
from scipy import special
import time

def prime_sieve(N):
    """Sieve of Eratosthenes, returns boolean array is_prime[0..N]."""
    is_prime = np.ones(N+1, dtype=bool)
    is_prime[0:2] = False
    for p in range(2, int(N**0.5)+1):
        if is_prime[p]:
            is_prime[p*p::p] = False
    return is_prime

def c_omega_array(N, omega, is_prime=None):
    """c_omega(n) for n=1..N, via c_omega(n) = n^omega * prod_{p|n}(1-p^{-2omega})."""
    if is_prime is None:
        is_prime = prime_sieve(N)
    factor = np.ones(N+1, dtype=np.float64)
    primes = np.nonzero(is_prime)[0]
    for p in primes:
        factor[p::p] *= (1.0 - p**(-2.0*omega))
    n_arr = np.arange(0, N+1, dtype=np.float64)
    n_arr[0] = 1.0  # avoid 0**omega issues, index 0 unused anyway
    c = (n_arr**omega) * factor
    return c

def g_general_vec(t, omega):
    """g_omega^<1>(t) vectorized for 0<t<1 array, omega != 1/2."""
    pref = (4*omega/(2*omega-1)) * (np.pi**omega / special.gamma(omega))
    term1 = t**(omega-1) * special.beta((3-2*omega)/2, omega) * special.betaincc((3-2*omega)/2, omega, t**2)
    term2 = ((2*omega+1)/(4*omega)) * t**(-0.5) * special.beta((5-2*omega)/4, omega) * special.betaincc((5-2*omega)/4, omega, t**2)
    return pref * (term1 - term2)

def h_omega_1_batch(x_list, c_omega_cache, omega):
    Nmax = len(c_omega_cache)-1
    results = []
    for x in x_list:
        N = int(np.floor(x))
        assert N <= Nmax, f"N={N} exceeds cache {Nmax}"
        n_arr = np.arange(1, N+1, dtype=np.float64)
        t = n_arr / x
        g = g_general_vec(t, omega)
        total = np.sum(c_omega_cache[1:N+1] * g)
        results.append(total/x)
    return results

if __name__ == '__main__':
    # small-N brute-force cross-check via trial division
    def euler_style_c(n, omega):
        nn = n; primes_of_n = []
        p = 2
        while p*p <= nn:
            if nn % p == 0:
                primes_of_n.append(p)
                while nn % p == 0:
                    nn //= p
            p += 1
        if nn > 1:
            primes_of_n.append(nn)
        val = n**omega
        for p in primes_of_n:
            val *= (1 - p**(-2.0*omega))
        return val

    N = 1000
    omega = 0.3
    is_p = prime_sieve(N)
    c_arr = c_omega_array(N, omega, is_p)
    ok = True
    for n in [1,2,3,4,6,12,30,60,97,100,997,1000]:
        expect = euler_style_c(n, omega)
        got = c_arr[n]
        if abs(got-expect) > 1e-9*abs(expect):
            print(f"MISMATCH n={n}: got {got} expect {expect}")
            ok = False
    print("c_omega sieve sanity:", "PASS" if ok else "FAIL")
