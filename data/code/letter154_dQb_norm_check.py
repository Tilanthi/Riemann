"""
Letter 154 -- independent third measurement of leg B's Euclidean norm, filling the specific gap
BEAST named in cycle-24 sect5.3: "m1's 4daf65f re-measured all four legs in the G metric only; the
Euclidean leg-B number, and therefore the falsifier, is not in the record." BEAST's own number
(their sect5.3): ||P_b||_2 = 8.0140706e-5, ||P_b||_G = 1.4182514e-3, ratio 17.70 -- used as a
falsifier against "15.05 is a universal G<->Euclidean conversion constant" (leg A's ratio was 15.05,
leg B's is a different number, so it's not a property of G alone).

dQ_b := S_quadruple(delta_b=0.07208635197257083638787626, gamma_b_R03) - S_quadruple(delta_b=0, gamma_b_R03)
(the cancellation-point leg B displacement, same object as cycle 23's P_b).
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


def load_G(seed, M):
    d = json.load(open('/workspace/Riemann/repo/data/machine1_heat72k_identity_target_m8.json'))
    tgt = d['seeds'][f"{seed}/M{M}"]
    G = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            G[i, j] = mp.mpf(tgt['G_raw'][i][j])
    return G


def gmetric_spectrum(A, G):
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
    G = load_G(seed, M)
    cache = {}

    gamma_b_R03 = mp.mpf('26.36436221657414487498832')
    delta_b_cancel = mp.mpf('0.07208635197257083638787626')

    S_b0 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_b_R03, cache)
    S_b1 = S_quadruple_matrix(fns, delta_b_cancel, gamma_b_R03, cache)
    dQ_b = S_b1 - S_b0
    print(f"[{time.time()-t0:.1f}s] dQ_b built (leg B displacement, delta 0 -> cancellation delta)",
          flush=True)

    E_eucl = euclidean_spectrum(dQ_b)
    E_g = gmetric_spectrum(dQ_b, G)

    max_eucl = max(abs(x) for x in E_eucl)
    max_g = max(abs(x) for x in E_g)

    print("Euclidean spectrum of dQ_b:", [str(x) for x in E_eucl])
    print("max|eigenvalue| (Euclidean) =", max_eucl)
    print()
    print("G-metric generalized spectrum of dQ_b:", [str(x) for x in E_g])
    print("max|eigenvalue| (G-metric)  =", max_g)
    print()
    print("ratio G/Euclidean =", max_g / max_eucl)
    print("BEAST's quoted: Euclidean 8.0140706e-5, G-metric 1.4182514e-3, ratio 17.70")
    print(f"[{time.time()-t0:.1f}s] done")


if __name__ == '__main__':
    main()
