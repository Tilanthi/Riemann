"""
v2: FIXES a real bug found via debugging -- raw g(t,D)=zeta2(1/2+it,D) is NOT even in complex t
(it's g(-t.bar,D)=conj(g(t,D)) in general, which for REAL t only reduces to g(-t,D)=conj(g(t,D)),
i.e. Re[g] even / Im[g] odd along the real t-axis -- but g ITSELF is not literally even).

The physically-correct, genuinely-even-in-complex-t, holomorphic object is:
   F_real(t,D) := (g(t,D) + g(-t,D)) / 2
which matches Re[g(t,D)] for real t (verified: this is what the earlier finite-difference approach
was implicitly computing via .real, and that approach DID converge to the target band -- confirms
F_real, not raw g, is the right object) and is holomorphic + genuinely even in complex t by
construction (sum of two holomorphic functions, symmetric under t -> -t by construction).
"""
import sys, time
sys.path.insert(0, '/tmp')
from zeta2_impl_complexD import zeta2
import mpmath as mp

mp.mp.dps = 60
Dstar = mp.mpf('0.141733239663887191395415685084185024')

def g(t, D):
    s = mp.mpf('0.5') + mp.mpc(0, 1) * t
    return zeta2(s, D)

R_T = mp.mpf('0.3')
R_D = mp.mpf('0.06')
N_T = 32
N_D = 24

if __name__ == '__main__':
    print(f"Grid: N_t={N_T}, N_D={N_D}, r_t={R_T}, r_D={R_D}, dps={mp.mp.dps}")
    t0 = time.time()

    # need g at ALL N_T points around the full circle (to form F_real = (g(t)+g(-t))/2)
    t_nodes_full = [R_T * mp.e**(mp.mpc(0, 1) * 2 * mp.pi * k / N_T) for k in range(N_T)]
    D_nodes = [Dstar + R_D * mp.e**(mp.mpc(0, 1) * 2 * mp.pi * l / N_D) for l in range(N_D)]

    g_grid = [[None] * N_D for _ in range(N_T)]
    n_evals = 0
    for k in range(N_T):
        for l in range(N_D):
            g_grid[k][l] = g(t_nodes_full[k], D_nodes[l])
            n_evals += 1
            if n_evals % 50 == 0:
                print(f"  ... {n_evals}/{N_T*N_D} evals, {time.time()-t0:.1f}s elapsed", flush=True)
    t1 = time.time()
    print(f"  {n_evals} evaluations done in {t1-t0:.1f}s", flush=True)

    # F_real(t_k, D_l) = (g(t_k,D_l) + g(t_{k+N_T/2}, D_l)) / 2   [t_{k+N_T/2} = -t_k]
    half = N_T // 2
    F_half = [[None] * N_D for _ in range(half)]
    for k in range(half):
        for l in range(N_D):
            F_half[k][l] = (g_grid[k][l] + g_grid[k + half][l]) / 2

    t_nodes_half = t_nodes_full[:half]

    def c(m, n):
        total = mp.mpc(0)
        for k in range(half):
            tk = t_nodes_half[k]
            factor = tk**(-n) * (1 + (-1)**n)
            for l in range(N_D):
                dl = D_nodes[l] - Dstar
                total += F_half[k][l] * factor * dl**(-m)
        return total / (N_T * N_D)

    F0 = c(0, 0)
    F2 = mp.factorial(2) * c(0, 2)
    F4 = mp.factorial(4) * c(0, 4)
    F6 = mp.factorial(6) * c(0, 6)
    G0 = c(1, 0)
    G2 = 2 * c(1, 2)
    G4 = 24 * c(1, 4)
    H0 = c(2, 0)
    H2 = 2 * c(2, 2)
    K0 = c(3, 0)

    print(f"\nF0 = {F0}  (should be ~0)")
    print(f"F2 = {F2}")
    print(f"F4 = {F4}")
    print(f"F6 = {F6}")
    print(f"G0 = {G0}")
    print(f"G2 = {G2}")
    print(f"G4 = {G4}")
    print(f"H0 = {H0}")
    print(f"H2 = {H2}")
    print(f"K0 = {K0}")

    a_computed = -2 * G0 / F2
    tgt_a = mp.mpf('2.645521411811663')
    print(f"\n-2*G0/F2 = {a_computed}")
    print(f"target a = {tgt_a}  rel diff = {abs(a_computed-tgt_a)/tgt_a}")

    U2 = -2 * ((F4/24)*a_computed**2 + (G2/2)*a_computed + H0) / F2
    tgt_U2 = mp.mpf('7.46245287679')
    print(f"\nU2 = {U2}")
    print(f"target U2 = {tgt_U2}  rel diff = {abs(U2-tgt_U2)/tgt_U2}")

    U3 = -2 * ((F4/12)*a_computed*U2 + (F6/720)*a_computed**3 + (G2/2)*U2
                + (G4/24)*a_computed**2 + (H2/2)*a_computed + K0) / F2
    print(f"\na3 (U3, contour method) = {U3}")
    print(f"prior finite-difference results: 11.700719 / 11.700760")
    print(f"target band [11,13], mean 11.7975")

    print(f"\nTotal wall time: {time.time()-t0:.1f}s")
