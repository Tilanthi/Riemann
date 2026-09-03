from mpmath import mp, mpf, exp, cos, quad, pi as mp_pi

mp.dps = 30

def Phi(u, nmax=10):
    u = mpf(u)
    total = mpf(0)
    for n in range(1, nmax+1):
        n = mpf(n)
        term = (2*mp_pi**2*n**4*exp(9*u) - 3*mp_pi*n**2*exp(5*u)) * exp(-mp_pi*n**2*exp(4*u))
        total += term
    return total

def H_t(t, x, nmax=10):
    t = mpf(t); x = mpf(x)
    breaks = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.8, 1.2]
    def integrand(u):
        return exp(t*u**2) * Phi(u, nmax=nmax) * cos(x*u)
    return quad(integrand, breaks)

if __name__ == '__main__':
    # second zeta zero check: x = 2*21.022040
    x2 = 2*mpf('21.022039639')
    print(f"H_0({float(x2)}) [should be ~0, second zeta zero x2]:", float(H_t(0, x2)))
    x3 = 2*mpf('25.010857580')
    print(f"H_0({float(x3)}) [should be ~0, third zeta zero]:", float(H_t(0, x3)))
    # nearby off points for scale comparison
    print(f"H_0({float(x2)-0.5}):", float(H_t(0, x2-mpf('0.5'))))
    print(f"H_0({float(x2)+0.5}):", float(H_t(0, x2+mpf('0.5'))))
