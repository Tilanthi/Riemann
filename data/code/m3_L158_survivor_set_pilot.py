"""
m3-L158 -- a pilot toward SAPIENS's fourth-letter question (sect2): "WHICH off-line configurations
survive a finite instrument, and how the survivor set thins as M, T grow" -- named as "the experiment's
actual content" beyond the already-established "can the instrument detect off-line-ness at all" (yes,
established four instruments deep for two hand-picked pairs).

This is a MODEST, well-scoped pilot, not the full research programme: extend the single-pair witness
test (Letters 145-148: PAIR-A at k=0 fires at delta=0.1, PAIR-B at k=70 does not) from 2 hand-picked
pairs to a SYSTEMATIC SCAN across many adjacent on-line pairs at fixed delta=0.1, M=8, seed s1 --
mapping out fire/no-fire and lam_min magnitude as a function of pair index / ordinate height, using
the already-validated exact instrument (no new machinery, no new approximation).

Question this pilot actually answers: at a fixed, moderate displacement (delta=0.1), how does the
"detectability" of an off-line relocation vary smoothly with which pair is relocated, across a
run of consecutive pairs -- is it a sharp threshold in height, a gradual decay, or something with
structure (e.g. correlated with the pair's own gap size)? This is a first, cheap, honest look at the
survivor set's shape, not a claim about its asymptotic thinning as M,T grow (which would need much
larger M and a real sweep design -- explicitly out of scope here).
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
    return min(E)


def main():
    t0 = time.time()
    M = 8
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    K200, G = load_K_T200(seed, M)
    cache = {}
    delta = mp.mpf('0.1')

    N_PAIRS = 25  # pairs k=0..24, i.e. zeros #1..#26
    zeros = [mp.im(mp.zetazero(n)) for n in range(1, N_PAIRS + 2)]
    print(f"[{time.time()-t0:.1f}s] {len(zeros)} zeros computed, gamma range "
          f"{float(zeros[0]):.3f}..{float(zeros[-1]):.3f}", flush=True)

    K_pair_cache = {}

    def K_at(idx):
        if idx not in K_pair_cache:
            rho = mp.mpc('0.5', zeros[idx])
            K_pair_cache[idx] = K_pair_matrix(fns, rho, cache)
        return K_pair_cache[idx]

    results = []
    for k in range(N_PAIRS):
        t_k = time.time()
        gamma_i, gamma_j = zeros[k], zeros[k + 1]
        gap = gamma_j - gamma_i
        gamma0 = (gamma_i + gamma_j) / 2
        K_i = K_at(k)
        K_j = K_at(k + 1)
        K_base = K200 - K_i - K_j
        S = S_quadruple_matrix(fns, delta, gamma0, cache)
        S_Z = K_base + S
        lmin = lambda_min_gen_eig(S_Z, G)
        fires = lmin < 0
        results.append({
            "k": k, "gamma_i": str(gamma_i), "gamma_j": str(gamma_j),
            "gap": str(gap), "gamma0": str(gamma0), "lam_min": str(lmin), "fires": fires,
        })
        print(f"[{time.time()-t_k:.1f}s] k={k}: gamma0={float(gamma0):.3f} gap={float(gap):.3f} "
              f"lam_min={lmin}  {'FIRES' if fires else 'survives'}", flush=True)

    n_fire = sum(1 for r in results if r["fires"])
    print(f"\n[{time.time()-t0:.1f}s] TOTAL: {n_fire}/{N_PAIRS} fire at delta=0.1", flush=True)

    out = {"note": "pilot survivor-set scan, M=8 seed s1, delta=0.1, single-pair witness test across "
                   "consecutive adjacent on-line pairs k=0..N-1 (zeros #1..#N+1)",
           "delta": str(delta), "N_PAIRS": N_PAIRS, "results": results,
           "n_fire": n_fire, "wall_seconds": time.time() - t0}
    path = '/workspace/Riemann/repo/data/code/m3_L158_survivor_pilot_result.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")


if __name__ == '__main__':
    main()
