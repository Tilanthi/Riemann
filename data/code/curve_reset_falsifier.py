import mpmath as mp
mp.mp.dps = 40

# angles from the genus-4 curve run (y^2 = pi-digit poly, g=4, p=11), sorted
angles = [-2.738696141872615, -2.270582213271576, -1.278853467546496, -0.6025331358098163,
           0.6025331358098163, 1.278853467546496, 2.270582213271576, 2.738696141872615]

theta = [mp.mpf(str(a)) for a in angles]

# tightest pair: -2.738696... and -2.270582... (gap 0.4681), by symmetry also 2.270582/2.738696
g1, g2 = theta[0], theta[1]
d = (g2-g1)/2
m0 = (g1+g2)/2
print(f"tight pair: theta0={float(g1):.6f}, theta1={float(g2):.6f}, m0={mp.nstr(m0,15)}, d={mp.nstr(d,15)}")

def g_poly(t):
    # exact polynomial with roots at all 8 angles
    val = mp.mpf(1)
    for th in theta:
        val *= (t - th)
    return val

def f(z):
    return mp.log(g_poly(m0+z) / (z**2 - d**2))

c = mp.taylor(f, 0, 4)
k1,k2,k3,k4 = c[1],c[2],c[3],c[4]
B = -2*k2
R = -4*k4/B**2
q = B*d**2/2
print(f"kappa1={mp.nstr(k1,10)}  B={mp.nstr(B,10)}  kappa3={mp.nstr(k3,10)}  kappa4={mp.nstr(k4,10)}")
print(f"R={mp.nstr(R,10)}   q={mp.nstr(q,10)}")

print()
print("Comparison: zeta-side empirical R range this correspondence has measured: ~0.03 to ~1.08")
print("(GUE reference median ~0.19; widest outlier this session R=1.079 at E~1.4e13, later shown")
print(" to reproduce at R=0.1334 -- so the honest outer envelope is closer to [0.03, 0.46] with the")
print(" E~1.4e13 anomaly's true value now resolved to 0.1334, well inside range)")
