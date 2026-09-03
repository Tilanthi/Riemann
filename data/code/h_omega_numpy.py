import numpy as np
import time

def phi_sieve(N):
    """Euler's totient sieve for n=1..N (index 0 unused)."""
    phi = np.arange(N+1, dtype=np.int64)
    for p in range(2, N+1):
        if phi[p] == p:  # p is prime
            phi[p::p] -= phi[p::p] // p
    return phi

def g_half_vec(t):
    """g_{1/2}^<1>(t) vectorized, for 0<t<1 array; t>=1 handled by caller (should not be passed here)."""
    return (2.0/np.sqrt(t)) * (2.0*np.sqrt(1.0-t**2) + np.log(t) - np.log(1.0+np.sqrt(1.0-t**2)))

def h_half_1_batch(x_list, phi, c_half_cache=None):
    """Evaluate h_{1/2}^<1>(x) for each x in x_list, reusing the phi sieve. x must be <= len(phi)-1."""
    Nmax = len(phi)-1
    if c_half_cache is None:
        n_arr = np.arange(1, Nmax+1, dtype=np.float64)
        c_half_cache = phi[1:Nmax+1].astype(np.float64) / np.sqrt(n_arr)
    results = []
    for x in x_list:
        N = int(np.floor(x))
        assert N <= Nmax
        n_arr = np.arange(1, N+1, dtype=np.float64)
        t = n_arr / x
        g = g_half_vec(t)
        total = np.sum(c_half_cache[:N] * g)
        results.append(total / x)
    return results, c_half_cache

if __name__ == '__main__':
    N = 100000
    t0 = time.time()
    phi = phi_sieve(N)
    print(f"sieve N={N} done in {time.time()-t0:.2f}s")
    # cross-check phi against known small values
    known = {1:1,2:1,3:2,4:2,5:4,6:2,7:6,8:4,9:6,10:4,12:4,100:40}
    for n,v in known.items():
        assert phi[n]==v, f"phi({n})={phi[n]} expected {v}"
    print("phi sieve sanity: PASS on", list(known.keys()))

    xs = [2,3,5,8,13,21,34,55,89, 1000, 10000, 100000]
    t0=time.time()
    res, cache = h_half_1_batch(xs, phi)
    print(f"batch eval done in {time.time()-t0:.2f}s")
    for x,h in zip(xs,res):
        print(f"x={x:8d}  h={h: .10f}  sqrt(x)*h={ (x**0.5)*h :.6f}")
