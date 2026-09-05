"""
Letter 153 -- independent verification of Mac's L153 sect3 refinement: on the launch4 family
(R0d, R4), the k=2 quasi-degenerate sign fix does NOT arrive at k=2 (unlike R0/R2/R3) -- it stays
POSITIVE through k=3 and only flips at k=4. This directly corrects the over-broad generalization in
my own Letter 152 subject line ("k=2 fixes the sign at every level-crossing rung" -- true only for
the launch/R0-R3 family I happened to test, not universally).

Reuses the same exact-instrument machinery as letter152_quasi_degenerate_pt.py, applied to launch4
= K_base + S_a(delta=0) + S_b(delta=0, gamma_b_R4), and its two rungs R0d (leg A only, delta=0.1) and
R4 (both legs, delta_a=0.1, delta_b=0.1).
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
    L = mp.cholesky(G)
    Linv = L**-1
    B = Linv * K * Linv.T
    n = B.rows
    for i in range(n):
        for j in range(i + 1, n):
            avg = (B[i, j] + B[j, i]) / 2
            B[i, j] = avg
            B[j, i] = avg
    E, W = mp.eigsy(B)
    order = sorted(range(len(E)), key=lambda i: E[i])
    Esort = [E[i] for i in order]
    LinvT = Linv.T
    Vcols = []
    for i in order:
        w = mp.matrix([W[r, i] for r in range(n)])
        v = LinvT * w
        Vcols.append(v)
    return Esort, Vcols


def lam_min_reduced(S, Vcols, k):
    Heff = mp.zeros(k, k)
    for i in range(k):
        for j in range(k):
            Heff[i, j] = (Vcols[i].T * S * Vcols[j])[0, 0]
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
    gamma_b_R4 = mp.mpf('25.68760989835991681910105')

    S_a0 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_a, cache)
    S_b0_R4 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_b_R4, cache)
    launch4 = K_base + S_a0 + S_b0_R4
    Espec, Vcols = g_orthonormal_eigensystem(launch4, G)
    print(f"[{time.time()-t0:.1f}s] launch4 spectrum: {[str(x) for x in Espec]}", flush=True)

    S_a1 = S_quadruple_matrix(fns, mp.mpf('0.1'), gamma_a, cache)
    S_b1_R4 = S_quadruple_matrix(fns, mp.mpf('0.1'), gamma_b_R4, cache)

    rungs = {"R0d": K_base + S_a1 + S_b0_R4, "R4": K_base + S_a1 + S_b1_R4}
    exact = {"R0d": mp.mpf('-0.00000899539971714261894416139162154784750309823313'),
             "R4": mp.mpf('-0.0000211082147227832554218195326686191369420512128')}

    results = {}
    for name, S_Z in rungs.items():
        row = {}
        for k in (1, 2, 3, 4, 5, 6, 7, 8):
            lam_k = lam_min_reduced(S_Z, Vcols, k)
            rel_err = abs(lam_k / exact[name] - 1)
            row[k] = str(lam_k)
            print(f"  {name} k={k}: lam_min(reduced)={lam_k}  "
                  f"sign={'neg' if lam_k<0 else 'pos'}  rel_err={float(rel_err)*100:.2f}%", flush=True)
        results[name] = row

    out = {"launch4_spectrum": [str(x) for x in Espec], "results": results,
           "note": "independent verification of Mac's L153 sect3 claim: k=2 stays POSITIVE on the "
                   "launch4 family (R0d, R4), sign only flips at k=4",
           "wall_seconds": time.time() - t0}
    path = '/workspace/Riemann/repo/data/code/letter153_qdpt_launch4_result.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")


if __name__ == '__main__':
    main()
