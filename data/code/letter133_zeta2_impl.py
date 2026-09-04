"""
Independent implementation of the 2D Epstein zeta function zeta2(s,D) = (1/2) Sum'_{(j,k)} (j^2+D^2 k^2)^{-s},
via the standard theta-function/Poisson-summation analytic continuation (Epstein/Riemann method),
built from scratch (NOT reusing Mac's heat6X code) -- per the "own code, own precision" commitment
in Letter 128/132.

Derivation (see letter for the algebra): with theta(t) = sum_n e^{-pi n^2 t}, Theta_D(t) = theta(t)*theta(D*?)
-- careful, let Theta_D(t) := sum_{(j,k) in Z^2} e^{-pi t (j^2 + D^2 k^2)} = theta_1(t) * theta_D(t)
where theta_1(t) = sum_n e^{-pi n^2 t}, theta_D(t) = sum_k e^{-pi D^2 k^2 t} = theta_1(D^2 t).

2D Poisson (Gram matrix diag(1,D^2), det=D^2): Theta_D(t) = (1/(t*D)) * Theta_{1/D}(1/t)

Continuation:
2*zeta2(s,D)*pi^{-s}*Gamma(s) = -1/s + 1/(D*(s-1)) + (1/D)*I1(s) + I2(s)
  I1(s) = int_1^inf (Theta_{1/D}(u)-1) u^{-s} du
  I2(s) = int_1^inf (Theta_D(t)-1)  t^{s-1} dt

=> zeta2(s,D) = (pi^s / (2*Gamma(s))) * [ -1/s + 1/(D*(s-1)) + (1/D)*I1(s) + I2(s) ]

Both I1, I2 converge extremely fast (Theta-1 ~ 2e^{-pi*t} as t->inf for the dominant term), valid for
ALL complex s (no convergence restriction) -- this is what lets us evaluate at Re(s)=1/2 directly,
unlike the raw divergent-at-that-point Dirichlet series.
"""
import mpmath as mp

mp.mp.dps = 40

def theta1(t):
    """theta_1(t) = sum_{n=-inf}^{inf} e^{-pi n^2 t} = 1 + 2 sum_{n=1}^{inf} e^{-pi n^2 t}."""
    t = mp.mpf(t) if not isinstance(t, mp.mpc) else t
    total = mp.mpf(1)
    n = 1
    while True:
        term = 2 * mp.e**(-mp.pi * n * n * t)
        total += term
        if abs(term) < mp.mpf(10) ** (-mp.mp.dps - 5):
            break
        n += 1
        if n > 100000:
            break
    return total

def Theta_D(t, D):
    """Theta_D(t) = theta_1(t) * theta_1(D^2 * t)."""
    return theta1(t) * theta1(D * D * t)

def I1_I2(s, D, dps=None):
    """I1(s) = int_1^inf (Theta_{1/D}(u)-1) u^{-s} du
       I2(s) = int_1^inf (Theta_D(t)-1)  t^{s-1} dt"""
    Dinv = 1 / D
    def f1(u):
        return (Theta_D(u, Dinv) - 1) * u**(-s)
    def f2(t):
        return (Theta_D(t, D) - 1) * t**(s - 1)
    I1 = mp.quad(f1, [1, 2, 5, 10, mp.inf])
    I2 = mp.quad(f2, [1, 2, 5, 10, mp.inf])
    return I1, I2

def zeta2(s, D):
    s = mp.mpc(s)
    D = mp.mpf(D)
    I1, I2 = I1_I2(s, D)
    bracket = -1/s + 1/(D*(s-1)) + I1/D + I2
    return (mp.pi**s / (2*mp.gamma(s))) * bracket

def dirichlet_beta(s):
    """Dirichlet beta function: beta(s) = sum_{n=0}^inf (-1)^n/(2n+1)^s = 4^-s[zeta(s,1/4)-zeta(s,3/4)]."""
    return 4**(-s) * (mp.zeta(s, mp.mpf(1)/4) - mp.zeta(s, mp.mpf(3)/4))

def zeta2_direct_series(s, D, N=2000):
    """Direct Dirichlet series (only converges for Re(s)>1) -- independent cross-check in that regime."""
    total = mp.mpf(0)
    D = mp.mpf(D)
    for j in range(-N, N+1):
        for k in range(-N, N+1):
            if j == 0 and k == 0:
                continue
            q = j*j + D*D*k*k
            if q > N*N:  # crude cutoff to keep it bounded, only used for a sanity check at Re(s) large
                continue
            total += q**(-s)
    return total / 2

if __name__ == '__main__':
    print("=== Validation 0: direct series (Re(s) large) vs theta-continuation ===")
    for s_val in [mp.mpc('3', '0'), mp.mpc('2.5', '0')]:
        direct = zeta2_direct_series(s_val, mp.mpf('1.3'), N=300)
        cont = zeta2(s_val, mp.mpf('1.3'))
        print(f"s={s_val} D=1.3: direct(N=300)={direct}  continuation={cont}  diff={abs(direct-cont)}")

    # Validation 1: zeta2(s,1) = 2*zeta(s)*beta(s)  (D=1 factorization, a known identity per memory notes)
    print("=== Validation: zeta2(s,1) = 2*zeta(s)*beta(s) ===")
    for s_val in [mp.mpc('2', '0'), mp.mpc('0.5', '0'), mp.mpc('0.5', '2'), mp.mpc('-1', '0')]:
        z2 = zeta2(s_val, 1)
        rhs = 2 * mp.zeta(s_val) * dirichlet_beta(s_val)
        rel = abs(z2 - rhs) / abs(rhs) if rhs != 0 else abs(z2 - rhs)
        print(f"s={s_val}: zeta2(s,1)={z2}\n         2*zeta*beta={rhs}\n         rel_diff={rel}")
