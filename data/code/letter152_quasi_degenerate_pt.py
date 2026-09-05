"""
Letter 152 -- a genuinely new test motivated directly by Mac's L151/L152 finding: the eigenvalue
half of the local theory failed at R2/R3/R4 because of a LEVEL CROSSING (post-perturbation ground
state = 99%/99%/95% the OLD FIRST EXCITED state) -- ordinary Rayleigh-Schrodinger PT expands around a
single fixed eigenvector (v0) and cannot see a state it has left. Mac's own closing line: "the
replacement must track level crossings, not perturbative branches."

This tests the natural fix: QUASI-DEGENERATE PERTURBATION THEORY. Instead of expanding lam_min in
powers of delta around v0 alone, project the FULL (non-perturbatively exact) delta-dependent matrix
onto the span of the launch matrix's lowest k eigenvectors (G-orthonormal), and diagonalize that small
k x k matrix EXACTLY at each delta -- no Taylor truncation in delta at all, just a truncation in HOW
MANY states of the launch spectrum are kept. This can track a level crossing between any of the k
states by construction (it's an exact diagonalization within a k-dim subspace), while still being
vastly cheaper than the full M=8 dimensional exact answer if k is small.

Question: does k=2 (the two states known to cross) already recover the exact answer to good accuracy,
or does the perturbation reach deeper into the spectrum than the two states everyone has been
discussing?

Reuses the exact Family C configuration and K_base from Letters 149/150 (same removed set, same
gamma_a/gamma_b_R03) so the comparison is against ALREADY-VALIDATED exact numbers.
"""
import sys, time, json
sys.path.insert(0, '/tmp')
from identity_check_m8 import load_genome as load_genome_mp
import mpmath as mp

mp.mp.dps = 45


def u_of_s_mp(fi, s):
    pts = fi.breakpoints()
    re = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).real, pts)
    im = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).imag, pts)
    return mp.mpc(re, im)


def Uc(fns, i, s, cache):
    key = (i, str(s))
    if key not in cache:
        cache[key] = u_of_s_mp(fns[i], s)
    return cache[key]


def K_pair_matrix(fns, rho, cache):
    M = len(fns)
    U = [Uc(fns, i, rho, cache) for i in range(M)]
    K = mp.zeros(M, M)
    for i in range(M):
        for j in range(M):
            K[i, j] = 2 * (U[i] * mp.conj(U[j])).real
    return K


def S_quadruple_matrix(fns, delta, gamma0, cache):
    M = len(fns)
    p = mp.mpc(mp.mpf('0.5') + delta, gamma0)
    q = mp.mpc(mp.mpf('0.5') - delta, gamma0)
    Up = [Uc(fns, i, p, cache) for i in range(M)]
    Uq = [Uc(fns, i, q, cache) for i in range(M)]
    S = mp.zeros(M, M)
    for i in range(M):
        for j in range(M):
            S[i, j] = 2 * (Up[i] * mp.conj(Uq[j])).real + 2 * (Uq[i] * mp.conj(Up[j])).real
    return S


def load_K_T200(seed, M):
    d = json.load(open('/workspace/Riemann/repo/data/machine1_heat72k_identity_target_m8.json'))
    tgt = d['seeds'][f"{seed}/M{M}"]
    K200 = mp.matrix(M, M)
    G = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            K200[i, j] = mp.mpf(tgt['K_T200'][i][j])
            G[i, j] = mp.mpf(tgt['G_raw'][i][j])
    return K200, G


def g_orthonormal_eigensystem(K, G):
    """Returns (eigenvalues sorted ascending, G-orthonormal eigenvectors as columns of a matrix V)."""
    L = mp.cholesky(G)
    Linv = L**-1
    B = Linv * K * Linv.T
    n = B.rows
    for i in range(n):
        for j in range(i + 1, n):
            avg = (B[i, j] + B[j, i]) / 2
            B[i, j] = avg
            B[j, i] = avg
    E, W = mp.eigsy(B)  # B = W diag(E) W^T, W orthonormal (Euclidean)
    order = sorted(range(len(E)), key=lambda i: E[i])
    Esort = [E[i] for i in order]
    LinvT = Linv.T
    Vcols = []
    for i in order:
        w = mp.matrix([W[r, i] for r in range(n)])
        v = LinvT * w  # G-orthonormal eigenvector of the generalized problem
        Vcols.append(v)
    return Esort, Vcols


def project(S, Vcols, k):
    """H_eff[i,j] = v_i^T S v_j for i,j < k (v's already G-orthonormal, so this is the correct
    reduced Hamiltonian with no further metric correction needed)."""
    Heff = mp.zeros(k, k)
    for i in range(k):
        for j in range(k):
            Heff[i, j] = (Vcols[i].T * S * Vcols[j])[0, 0]
    return Heff


def lam_min_reduced(S, Vcols, k):
    Heff = project(S, Vcols, k)
    n = Heff.rows
    for i in range(n):
        for j in range(i + 1, n):
            avg = (Heff[i, j] + Heff[j, i]) / 2
            Heff[i, j] = avg
            Heff[j, i] = avg
    E, _ = mp.eigsy(Heff)
    return min(E)


def main():
    t0 = time.time()
    M = 8
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    K200, G = load_K_T200(seed, M)
    cache = {}

    g1, g2, g3, g4 = (mp.im(mp.zetazero(n)) for n in (1, 2, 3, 4))
    rho_list = [mp.mpc('0.5', g) for g in (g1, g2, g3, g4)]
    K_removed = mp.zeros(M, M)
    for rho in rho_list:
        K_removed += K_pair_matrix(fns, rho, cache)
    K_base = K200 - K_removed
    print(f"[{time.time()-t0:.1f}s] K_base ready", flush=True)

    gamma_a = mp.mpf('18.43929670238273204181427')
    gamma_b_R03 = mp.mpf('26.36436221657414487498832')

    S_a0 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_a, cache)
    S_b0 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_b_R03, cache)
    launch = K_base + S_a0 + S_b0
    Espec, Vcols = g_orthonormal_eigensystem(launch, G)
    print(f"[{time.time()-t0:.1f}s] launch spectrum: {[str(x) for x in Espec]}", flush=True)

    rungs = {
        "R0": (mp.mpf('0.1'), gamma_a, mp.mpf('0'), gamma_b_R03),
        "R1": (mp.mpf('0'), gamma_a, mp.mpf('0.07208635197257083638787626'), gamma_b_R03),
        "R2": (mp.mpf('0.1'), gamma_a, mp.mpf('0.07208635197257083638787626'), gamma_b_R03),
        "R3": (mp.mpf('0.1'), gamma_a, mp.mpf('0.2'), gamma_b_R03),
    }
    # exact values from Letter 149 (R0-R3 share this launch; R4 uses a different gamma_b, skip here)
    exact = {
        "R0": mp.mpf('-0.0000069928795174021922995151458298058223985347513'),
        "R1": mp.mpf('0.00000417118007711471600213197818562418021022299912'),
        "R2": mp.mpf('-0.00000824238483760173481147989811112382514536079736'),
        "R3": mp.mpf('-0.0000233441768363132274114566640970037934116635397'),
    }

    results = {}
    for name, (da, ga, db, gb) in rungs.items():
        t_r = time.time()
        Sa = S_quadruple_matrix(fns, da, ga, cache)
        Sb = S_quadruple_matrix(fns, db, gb, cache)
        S_Z = K_base + Sa + Sb
        row = {}
        for k in (1, 2, 3, 4, 6, 8):
            lam_k = lam_min_reduced(S_Z, Vcols, k)
            rel_err = abs(lam_k / exact[name] - 1)
            row[k] = {"lam": str(lam_k), "rel_err_vs_exact": str(rel_err)}
            print(f"  {name} k={k}: lam_min(reduced)={lam_k}  rel_err={float(rel_err)*100:.4f}%",
                  flush=True)
        results[name] = row
        print(f"[{time.time()-t_r:.1f}s] {name} done", flush=True)

    out = {"launch_spectrum": [str(x) for x in Espec], "results": results,
           "note": "quasi-degenerate PT: exact diagonalization of the k-dim projection of S_Z onto "
                   "the launch matrix's lowest k G-orthonormal eigenvectors, vs the true exact lam_min",
           "wall_seconds": time.time() - t0}
    path = '/workspace/Riemann/repo/data/code/letter152_qdpt_result.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")


if __name__ == '__main__':
    main()
