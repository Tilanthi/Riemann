"""
v4: same delta_D=0.001, h_t=0.01, but 6 t-points (0..5h) fitting up to t^10 (6 unknowns) instead of
4 points fitting up to t^6 -- reduces contamination of F4,F6 from higher-order terms without needing
smaller h_t (which would need more D-grid re-evaluation too). 7 D-points unchanged (42 evals total).
"""
import sys, time
sys.path.insert(0, '/tmp')
from zeta2_impl import zeta2
import mpmath as mp

mp.mp.dps = 50
Dstar = mp.mpf('0.141733239663887191395415685084185024')

def g(t, D):
    s = mp.mpf('0.5') + mp.mpc(0, 1) * t
    return zeta2(s, D)

H_T = mp.mpf('0.01')
DELTA_D = mp.mpf('0.001')

if __name__ == '__main__':
    t_ks = [0, 1, 2, 3, 4, 5]
    j_s = [-3, -2, -1, 0, 1, 2, 3]

    print(f"Evaluating g(t,D) on a {len(t_ks)}x{len(j_s)} grid (h_t={H_T}, delta_D={DELTA_D})...")
    grid = {}
    t0 = time.time()
    for j in j_s:
        D = Dstar + j * DELTA_D
        for k in t_ks:
            t = k * H_T
            v = g(t, D)
            grid[(k, j)] = v.real
    print(f"  {len(grid)} evals done in {time.time()-t0:.1f}s")

    NUNK = 6  # const, t^2, t^4, t^6, t^8, t^10
    M = mp.matrix(NUNK, NUNK)
    facs = [mp.factorial(2*m) for m in range(NUNK)]
    for i, k in enumerate(t_ks):
        x = k * H_T
        for m in range(NUNK):
            M[i, m] = x**(2*m) / facs[m]

    F_of_D = {m: {} for m in range(NUNK)}  # F_of_D[m][j] = F_{2m}(D_j)
    for j in j_s:
        rhs = mp.matrix([grid[(k, j)] for k in t_ks])
        sol = mp.lu_solve(M, rhs)
        for m in range(NUNK):
            F_of_D[m][j] = sol[m]

    F0_of_D, F2_of_D, F4_of_D, F6_of_D = F_of_D[0], F_of_D[1], F_of_D[2], F_of_D[3]
    F2 = F2_of_D[0]; F4 = F4_of_D[0]; F6 = F6_of_D[0]
    print(f"\nF0(0)={F0_of_D[0]}  (should be ~0)")
    print(f"F2 = {F2}")
    print(f"F4 = {F4}")
    print(f"F6 = {F6}")

    def fd1(vals, h):
        return (-vals[-3] + 9*vals[-2] - 45*vals[-1] + 45*vals[1] - 9*vals[2] + vals[3]) / (60*h)
    def fd2(vals, h):
        return (2*vals[-3] - 27*vals[-2] + 270*vals[-1] - 490*vals[0] + 270*vals[1] - 27*vals[2] + 2*vals[3]) / (180*h*h)
    def fd3(vals, h):
        return (-vals[-3] + 8*vals[-2] - 13*vals[-1] + 13*vals[1] - 8*vals[2] + vals[3]) / (8*h**3)

    G0 = fd1(F0_of_D, DELTA_D)
    H0 = mp.mpf('0.5') * fd2(F0_of_D, DELTA_D)
    K0 = fd3(F0_of_D, DELTA_D) / 6
    G2 = fd1(F2_of_D, DELTA_D)
    H2 = mp.mpf('0.5') * fd2(F2_of_D, DELTA_D)
    G4 = fd1(F4_of_D, DELTA_D)

    print(f"\nG0={G0}\nG2={G2}\nG4={G4}\nH0={H0}\nH2={H2}\nK0={K0}")

    a_computed = -2 * G0 / F2
    print(f"\n=== BLIND VALIDATION 1 ===")
    print(f"-2*G0/F2 = {a_computed}")
    tgt_a = mp.mpf('2.645521411811663')
    print(f"target a = {tgt_a}  rel diff = {abs(a_computed-tgt_a)/tgt_a}")

    U2 = -2 * ((F4/24)*a_computed**2 + (G2/2)*a_computed + H0) / F2
    print(f"\n=== BLIND VALIDATION 2 ===")
    print(f"U2 (=-b) = {U2}")
    tgt_U2 = mp.mpf('7.46245287679')
    print(f"target U2 = {tgt_U2}  rel diff = {abs(U2-tgt_U2)/tgt_U2}")

    # If both validations are tight, go ahead and compute a3 too (U3)
    U3 = -2 * ((F4/12)*a_computed*U2 + (F6/720)*a_computed**3 + (G2/2)*U2
                + (G4/24)*a_computed**2 + (H2/2)*a_computed + K0) / F2
    print(f"\n=== a3 (U3) ===")
    print(f"a3 = {U3}")
    print(f"Mac's anchor mean 11.7975, band [11,13]")
