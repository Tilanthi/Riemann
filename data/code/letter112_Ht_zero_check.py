"""Investigating a genuinely tractable question inspired by SAPIENS's push + Mac/BEAST's
confinement-argument technique: z=0 is the UNIQUE point manifestly self-dual under H_t's
own z -> -z symmetry (the exact analogue of BEAST's Epstein-fold self-duality). Does H_t(0)
ever vanish for real t? If so, the SAME confinement argument (real coefficients + z->-z
duality force a self-dual pair's local structure to stay on {Im z=0} U {Re z=0}) would apply
there directly. z=0 requires NO large-x quadrature, so this is fully within reach of already-
working tools (no cancellation issue).
"""
from mpmath import mp, mpf, exp, cos, quad, pi as mp_pi

mp.dps = 40

def Phi(u, nmax=10):
    u = mpf(u)
    total = mpf(0)
    for n in range(1, nmax+1):
        n = mpf(n)
        term = (2*mp_pi**2*n**4*exp(9*u) - 3*mp_pi*n**2*exp(5*u)) * exp(-mp_pi*n**2*exp(4*u))
        total += term
    return total

def H_t_at_0(t):
    t = mpf(t)
    breaks = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.8, 1.2]
    def integrand(u):
        return exp(t*u**2) * Phi(u)
    return quad(integrand, breaks)

if __name__ == '__main__':
    print("H_t(0) across a range of t:")
    for t in [1.0, 0.5, 0.22, 0.1, 0.0, -0.1, -0.22, -0.5, -1.0, -2.0, -5.0, -10.0, -20.0]:
        val = H_t_at_0(t)
        print(f"  t={t:7.2f}: H_t(0) = {float(val):.10e}")

print()
print("Extended range + asymptotic check (H_t(0) ~ Phi(0)/2 * sqrt(pi/|t|) as t -> -infty):")
phi0 = Phi(0)
print(f"Phi(0) = {float(phi0):.6e}")
from mpmath import sqrt
for t in [-50, -100, -200]:
    val = H_t_at_0(t)
    asym = phi0/2 * sqrt(mp_pi/abs(mpf(t)))
    print(f"  t={t:7.1f}: H_t(0) = {float(val):.6e}   asymptotic ~ {float(asym):.6e}   ratio = {float(val/asym):.4f}")
