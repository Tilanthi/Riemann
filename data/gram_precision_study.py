import mpmath as mp
import time

def ghat(s, dps):
    return mp.sqrt(2*mp.pi) * mp.e**(s**2/2)

def phihat(a, s):
    return a**s * ghat(s, None)

# GROUND TRUTH via zero-side sum (fast, reliable -- Gaussian decay in t regardless of dilation)
def K_zeroside(a_j, a_k, n_zeros, dps):
    old = mp.mp.dps
    mp.mp.dps = dps
    total = mp.mpf(0)
    for n in range(1, n_zeros+1):
        rho = mp.mpf('0.5') + 1j*mp.zetazero(n).imag
        total += 2*mp.re(phihat(a_j,rho)*phihat(a_k,1-rho))
    mp.mp.dps = old
    return total

if __name__ == '__main__':
    a_j, a_k = mp.mpf('1.0'), mp.mpf('2.0')
    for dps in [30, 50]:
        for nz in [20, 40]:
            t0=time.time()
            v = K_zeroside(a_j, a_k, nz, dps)
            print(f"dps={dps} n_zeros={nz}: K[0][1] (zero-side, ground truth) = {v}  [{time.time()-t0:.1f}s]")
