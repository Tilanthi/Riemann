import mpmath as mp
import time

mp.mp.dps = 30

g1 = mp.mpf('1000000000000.387021605953')
g2 = mp.mpf('1000000000000.45400991512')

# Quick verification: refine both to higher precision via local bisection around the
# already-located approximate roots, and confirm siegelz truly changes sign right there.
def my_bisect(f, a, b, tol, max_iter=60):
    fa = f(a)
    for _ in range(max_iter):
        mid = (a+b)/2
        fm = f(mid)
        if abs(b-a) < tol:
            return mid
        if (fa > 0) == (fm > 0):
            a, fa = mid, fm
        else:
            b = mid
    return (a+b)/2

print('verify z(g1-1e-6), z(g1+1e-6):', mp.siegelz(g1-mp.mpf('1e-6')), mp.siegelz(g1+mp.mpf('1e-6')))
print('verify z(g2-1e-6), z(g2+1e-6):', mp.siegelz(g2-mp.mpf('1e-6')), mp.siegelz(g2+mp.mpf('1e-6')))

t0=time.time()
g1r = my_bisect(mp.siegelz, g1-mp.mpf('1e-6'), g1+mp.mpf('1e-6'), mp.mpf('1e-15'))
g2r = my_bisect(mp.siegelz, g2-mp.mpf('1e-6'), g2+mp.mpf('1e-6'), mp.mpf('1e-15'))
print('refined gamma1=', g1r)
print('refined gamma2=', g2r)
print('refine time:', time.time()-t0)

m0 = (g1r+g2r)/2
d = (g2r-g1r)/2
print('m0=', m0, ' d=', d)

def Xi(z):
    s = mp.mpf('0.5') + 1j*(m0+z)
    return mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)

t0=time.time()
def f(z):
    return mp.log(Xi(z) / (z**2 - d**2))
c = mp.taylor(f, 0, 4)
print('taylor extraction time:', time.time()-t0)
k1,k2,k3,k4 = c[1],c[2],c[3],c[4]
B = -2*k2
R = -4*k4/B**2
q = B*d**2/2
N_eff = mp.log(m0/(2*mp.pi))/mp.sqrt(12*mp.mpf('1.5731433'))
print(f'kappa1={k1}  B={B}  kappa3={k3}  kappa4={k4}')
print(f'R={R}  q={q}  N_eff={N_eff}')
