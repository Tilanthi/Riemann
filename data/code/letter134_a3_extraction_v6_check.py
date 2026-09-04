"""
v5: higher precision (dps=70) and wider stencils (7 t-points fitting up to t^12; 9 D-points for a
higher-order 3rd-D-derivative stencil) specifically to get F6,G4,H2,K0 (the a3-feeding layer) to
convergence, following the same refine-and-check-convergence discipline that closed a/U2.
"""
import sys, time
sys.path.insert(0, '/tmp')
from zeta2_impl import zeta2
import mpmath as mp

mp.mp.dps = 70
Dstar = mp.mpf('0.141733239663887191395415685084185024')

def g(t, D):
    s = mp.mpf('0.5') + mp.mpc(0, 1) * t
    return zeta2(s, D)

H_T = mp.mpf('0.012')
DELTA_D = mp.mpf('0.0012')

if __name__ == '__main__':
    t_ks = [0, 1, 2, 3, 4, 5, 6]     # fit up to t^12 (7 unknowns)
    j_s = [-4, -3, -2, -1, 0, 1, 2, 3, 4]  # 9-point D stencil

    print(f"Evaluating g(t,D) on a {len(t_ks)}x{len(j_s)} grid (h_t={H_T}, delta_D={DELTA_D}, dps={mp.mp.dps})...")
    grid = {}
    t0 = time.time()
    for j in j_s:
        D = Dstar + j * DELTA_D
        for k in t_ks:
            t = k * H_T
            v = g(t, D)
            grid[(k, j)] = v.real
    print(f"  {len(grid)} evals done in {time.time()-t0:.1f}s", flush=True)

    NUNK = len(t_ks)
    M = mp.matrix(NUNK, NUNK)
    facs = [mp.factorial(2*m) for m in range(NUNK)]
    for i, k in enumerate(t_ks):
        x = k * H_T
        for m in range(NUNK):
            M[i, m] = x**(2*m) / facs[m]

    F_of_D = {m: {} for m in range(NUNK)}
    for j in j_s:
        rhs = mp.matrix([grid[(k, j)] for k in t_ks])
        sol = mp.lu_solve(M, rhs)
        for m in range(NUNK):
            F_of_D[m][j] = sol[m]

    F0_of_D, F2_of_D, F4_of_D, F6_of_D = F_of_D[0], F_of_D[1], F_of_D[2], F_of_D[3]
    F2 = F2_of_D[0]; F4 = F4_of_D[0]; F6 = F6_of_D[0]
    print(f"\nF0(0)={F0_of_D[0]}")
    print(f"F2 = {F2}")
    print(f"F4 = {F4}")
    print(f"F6 = {F6}")

    # 9-point central-difference coefficients (standard, O(h^8) accurate)
    def fd1_9(vals, h):
        # coeffs: [1, -8, 56, -448, 0, 448, -56, 8, -1] / (840 h)  for f' using j=-4..4 (excluding 0)
        c = {1: 3/4, 2: -3/20, 3: 1/60, 4: 0}  # not used directly; use explicit formula below
        return (3*vals[-4] - 32*vals[-3] + 168*vals[-2] - 672*vals[-1]
                + 672*vals[1] - 168*vals[2] + 32*vals[3] - 3*vals[4]) / (840*h)
    def fd2_9(vals, h):
        return (-9*vals[-4] + 128*vals[-3] - 1008*vals[-2] + 8064*vals[-1] - 14350*vals[0]
                + 8064*vals[1] - 1008*vals[2] + 128*vals[3] - 9*vals[4]) / (5040*h*h)
    def fd3_9(vals, h):
        # 3rd derivative, 9-point central, O(h^6): standard coefficients
        return (-7*vals[-4] + 72*vals[-3] - 338*vals[-2] + 488*vals[-1]
                - 488*vals[1] + 338*vals[2] - 72*vals[3] + 7*vals[4]) / (240*h**3)

    G0 = fd1_9(F0_of_D, DELTA_D)
    H0 = mp.mpf('0.5') * fd2_9(F0_of_D, DELTA_D)
    K0 = fd3_9(F0_of_D, DELTA_D) / 6
    G2 = fd1_9(F2_of_D, DELTA_D)
    H2 = mp.mpf('0.5') * fd2_9(F2_of_D, DELTA_D)
    G4 = fd1_9(F4_of_D, DELTA_D)

    print(f"\nG0={G0}\nG2={G2}\nG4={G4}\nH0={H0}\nH2={H2}\nK0={K0}")

    a_computed = -2 * G0 / F2
    tgt_a = mp.mpf('2.645521411811663')
    print(f"\n-2*G0/F2 = {a_computed}  target={tgt_a}  rel diff={abs(a_computed-tgt_a)/tgt_a}")

    U2 = -2 * ((F4/24)*a_computed**2 + (G2/2)*a_computed + H0) / F2
    tgt_U2 = mp.mpf('7.46245287679')
    print(f"U2 = {U2}  target={tgt_U2}  rel diff={abs(U2-tgt_U2)/tgt_U2}")

    U3 = -2 * ((F4/12)*a_computed*U2 + (F6/720)*a_computed**3 + (G2/2)*U2
                + (G4/24)*a_computed**2 + (H2/2)*a_computed + K0) / F2
    print(f"\na3 (U3) = {U3}")
    print("target band [11,13], mean 11.7975")
