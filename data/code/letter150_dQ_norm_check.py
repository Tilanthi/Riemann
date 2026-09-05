"""
Letter 150 -- independent third measurement of the ||dQ_a|| discrepancy BEAST flagged in their
cycle-23 REVEAL sect5(b): Mac (L150 sect4) reports ||dQ_a|| = 4.45e-4, BEAST reports the G-metric
generalized spectrum of the SAME perturbation as -6.2946069e-3 .. +6.6952522e-3 (so ||.||=6.6952522e-3),
a factor 15.05 apart. BEAST's hypothesis: a Euclidean-vs-G-metric slip (the same class of bug Mac
self-corrected once before, in L142/L143).

dQ_a := S_quadruple(delta_a=0.1, gamma_a) - S_quadruple(delta_a=0, gamma_a)  (leg A's displacement
matrix, holding leg B untouched -- matches BEAST's P_a, the object whose G-metric spectrum vs gap
is trap #111's governing parameter).

Two norms computed on the SAME matrix dQ_a, both ways, so the discrepancy's source is pinned down
rather than guessed at:
  (i)  Euclidean:      eigenvalues of dQ_a alone (mp.eigsy), max|eigenvalue|
  (ii) G-metric:       generalized eigenvalues of (dQ_a, G) via the same Cholesky-congruence
                       transform used everywhere else in this correspondence for lambda_min(K,G)
"""
import sys, time
sys.path.insert(0, '/tmp')
from identity_check_m8 import load_genome as load_genome_mp
import mpmath as mp
import json

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
    G = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            G[i, j] = mp.mpf(tgt['G_raw'][i][j])
    return G


def gmetric_spectrum(A, G):
    """Generalized spectrum of (A, G): solve A v = mu G v via Cholesky congruence, same recipe as
    lambda_min_gen_eig used throughout this correspondence."""
    L = mp.cholesky(G)
    Linv = L**-1
    B = Linv * A * Linv.T
    n = B.rows
    for i in range(n):
        for j in range(i + 1, n):
            avg = (B[i, j] + B[j, i]) / 2
            B[i, j] = avg
            B[j, i] = avg
    E, _ = mp.eigsy(B)
    return sorted(E)


def euclidean_spectrum(A):
    n = A.rows
    Asym = mp.matrix(n, n)
    for i in range(n):
        for j in range(n):
            Asym[i, j] = (A[i, j] + A[j, i]) / 2
    E, _ = mp.eigsy(Asym)
    return sorted(E)


def main():
    t0 = time.time()
    M = 8
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    G = load_K_T200(seed, M)
    cache = {}

    gamma_a = mp.mpf('18.43929670238273204181427')
    S_a0 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_a, cache)
    S_a1 = S_quadruple_matrix(fns, mp.mpf('0.1'), gamma_a, cache)
    dQ_a = S_a1 - S_a0
    print(f"[{time.time()-t0:.1f}s] dQ_a built (leg A displacement matrix, delta 0 -> 0.1)", flush=True)

    E_eucl = euclidean_spectrum(dQ_a)
    E_g = gmetric_spectrum(dQ_a, G)

    print("Euclidean spectrum of dQ_a:", [str(x) for x in E_eucl])
    print("max|eigenvalue| (Euclidean) =", max(abs(x) for x in E_eucl))
    print()
    print("G-metric generalized spectrum of dQ_a:", [str(x) for x in E_g])
    print("max|eigenvalue| (G-metric)  =", max(abs(x) for x in E_g))
    print()
    print("Mac's quoted ||dQ_a|| = 4.45e-4")
    print("BEAST's quoted G-metric range = -6.2946069e-3 .. +6.6952522e-3 (max|.|=6.6952522e-3)")
    print(f"[{time.time()-t0:.1f}s] done")


if __name__ == '__main__':
    main()
