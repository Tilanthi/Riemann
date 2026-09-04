"""
Independent second instrument for the N2/N5 witness test, using the structural shortcut BEAST
identified (cycle 22, sec 3): the prime/archimedean/endpoint terms are FIXED (same for the true and
synthetic zero configurations) and cancel identically out of the scored quantity. So:

  S_Z(delta) = K_T200 - K(removed pair 1) - K(removed pair 2) + S(inserted off-line quadruple, delta)

using ONLY zero-side computations -- no archimedean integral needed at all. This sidesteps my entire
precision struggle (Letters 141-144) and lets me build a genuinely independent (own code, own
precision management, mpmath dps=45 not scipy/float64) cross-check on BEAST's scored cycle-22 result.

Zero-side formulas (all independently re-derived in Letter 119, confirmed matching BEAST's and Mac's
independent derivations):
  On-line pair {rho, rho_bar}:  K_ij(rho) = 2*Re[u_i(rho) * conj(u_j(rho))]
  Off-line FE-closed quadruple {p, q, p_bar, q_bar} (p=1/2+delta+i*gamma0, q=1/2-delta+i*gamma0):
    S_ij(quadruple) = 2*Re[u_i(p)*conj(u_j(q))] + 2*Re[u_i(q)*conj(u_j(p))]
    (using u_j(1-p)=conj(u_j(q)) since 1-p = 1/2-delta-i*gamma0 = conj(q))
"""
import sys, time
sys.path.insert(0, '/tmp')
from identity_check_m8 import load_genome as load_genome_mp  # mpmath-based TestFn, breakpoints etc
import mpmath as mp
import json

mp.mp.dps = 45  # per Mac's trap #99 lesson: dps=30 is the failure mode, 45 is the validated minimum

def u_of_s_mp(fi, s, pts=None):
    if pts is None:
        pts = fi.breakpoints()
    re = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).real, pts)
    im = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).imag, pts)
    return mp.mpc(re, im)

def K_pair_matrix(fns, rho):
    """K_ij(rho) = 2*Re[u_i(rho)*conj(u_j(rho))] for an on-line zero rho (contributes with its conjugate)."""
    M = len(fns)
    U = [u_of_s_mp(fns[i], rho) for i in range(M)]
    K = mp.zeros(M, M)
    for i in range(M):
        for j in range(M):
            K[i, j] = 2 * (U[i] * mp.conj(U[j])).real
    return K

def S_quadruple_matrix(fns, delta, gamma0):
    """S_ij(quadruple) for the FE-closed off-line quadruple {p,q,pbar,qbar} at (delta, gamma0)."""
    M = len(fns)
    p = mp.mpc(mp.mpf('0.5') + delta, gamma0)
    q = mp.mpc(mp.mpf('0.5') - delta, gamma0)
    Up = [u_of_s_mp(fns[i], p) for i in range(M)]
    Uq = [u_of_s_mp(fns[i], q) for i in range(M)]
    S = mp.zeros(M, M)
    for i in range(M):
        for j in range(M):
            S[i, j] = 2 * (Up[i] * mp.conj(Uq[j])).real + 2 * (Uq[i] * mp.conj(Up[j])).real
    return S

def load_K_T200(seed, M):
    d = json.load(open('/workspace/Riemann/repo/data/machine1_heat72k_identity_target_m8.json'))
    tgt = d['seeds'][f"{seed}/M{M}"]
    K200 = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            K200[i, j] = mp.mpf(tgt['K_T200'][i][j])
    G = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            G[i, j] = mp.mpf(tgt['G_raw'][i][j])
    return K200, G

def lambda_min_gen_eig(K, G):
    L = mp.cholesky(G)
    Linv = L**-1
    B = Linv * K * Linv.T
    n = B.rows
    for i in range(n):
        for j in range(i + 1, n):
            avg = (B[i, j] + B[j, i]) / 2
            B[i, j] = avg
            B[j, i] = avg
    E, _ = mp.eigsy(B)
    return min(E), E

if __name__ == '__main__':
    M = 8
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    K200, G = load_K_T200(seed, M)
    print(f"Loaded K_T200, G for {seed}/M{M}")

    # PAIR-A: gamma = 14.13472514..., 21.02203964... (first two zeta zeros)
    print("\nComputing zeta zeros...")
    z0 = mp.zetazero(1)
    z1 = mp.zetazero(2)
    gamma_a, gamma_b = mp.im(z0), mp.im(z1)
    print(f"gamma_0 (zero 1) = {gamma_a}")
    print(f"gamma_1 (zero 2) = {gamma_b}")
    gamma0 = (gamma_a + gamma_b) / 2
    print(f"gamma0 (midpoint) = {gamma0}")

    rho_a = mp.mpc('0.5', gamma_a)
    rho_b = mp.mpc('0.5', gamma_b)

    print("\nComputing removed-pair K matrices (on-line, PAIR-A)...")
    t0 = time.time()
    K_a = K_pair_matrix(fns, rho_a)
    K_b = K_pair_matrix(fns, rho_b)
    print(f"  done in {time.time()-t0:.1f}s")

    K_base = K200 - K_a - K_b
    lmin_base, _ = lambda_min_gen_eig(K_base, G)
    print(f"\nBaseline (both zeros removed, nothing inserted): lambda_min = {lmin_base}")
    print(f"  (compare to Mac's launch point 3.3758e-7)")

    delta_ladder = [mp.mpf(x) for x in ['0', '0.001', '0.01', '0.05', '0.1', '0.2', '0.3', '0.45']]
    print("\nDelta ladder:")
    results = []
    for delta in delta_ladder:
        t0 = time.time()
        S = S_quadruple_matrix(fns, delta, gamma0)
        S_Z = K_base + S
        lmin, _ = lambda_min_gen_eig(S_Z, G)
        print(f"  delta={float(delta):.3f}: lambda_min = {lmin}  [{time.time()-t0:.1f}s]")
        results.append((float(delta), lmin))

    print("\nCompare to BEAST's scored PAIR-A ladder:")
    print("  delta=0: 4.734e-6, 0.001: 4.733e-6, 0.01: 4.662e-6, 0.05: 2.720e-6,")
    print("  0.1: -6.973e-6, 0.2: -2.321e-4, 0.3: -5.212e-3, 0.45: -4.052e-2")
