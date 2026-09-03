import mpmath as mp
import time

mp.mp.dps = 25
g1 = mp.mpf('14142135623731.13763022274')
g2 = mp.mpf('14142135623731.23545079008')
d = (g2-g1)/2   # small magnitude, unaffected by ambient dps either way

mp.mp.dps = 15
m0_bug = (g1+g2)/2   # exact reproduction of e13_site.py's actual bug

def measure(m0, d, dps=30):
    old = mp.mp.dps
    mp.mp.dps = dps
    def Xi(z):
        s = mp.mpf('0.5') + 1j*(m0+z)
        return mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
    def f(z):
        return mp.log(Xi(z) / (z**2 - d**2))
    c = mp.taylor(f, 0, 4)
    k4 = c[4]; B = -2*c[2]
    R = -4*k4/B**2
    q = B*d**2/2
    mp.mp.dps = old
    return R, B, k4, q

t0=time.time()
R_bug, B_bug, k4_bug, q_bug = measure(m0_bug, d)
print(f"Using the EXACT dps=15-corrupted m0: R={mp.nstr(R_bug,10)}  B={mp.nstr(B_bug,10)}  kappa4={mp.nstr(k4_bug,10)}  q={mp.nstr(q_bug,10)}  [{time.time()-t0:.1f}s]")
print("Original e13_site.py reported:        R=1.07924  B=37.6134  kappa4=-381.719  q=0.04499")
