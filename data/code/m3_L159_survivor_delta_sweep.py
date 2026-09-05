"""
m3-L159 -- follow-up to the Letter 158 survivor-set pilot. That scan fixed delta=0.1 and found only
k=0 fires; among the 24 survivors, k=1 and k=2 (the two lowest-height, immediately-following pairs)
had the SMALLEST lam_min (closest to firing), before rising to a plateau by k~9. This tests two
things at once with a small, cheap extension:
  (a) does the "cliff" soften as delta grows -- do k=1/k=2 fire at larger delta?
  (b) does the height-ordering among survivors (k=1 closer to firing than k=9+) persist as delta
      grows, i.e. is closeness-to-firing systematically height-correlated, not just a delta=0.1
      artifact?
Also includes k=9 (a plateau representative) as a comparison point at the same deltas, to see whether
the plateau pairs stay far from firing even as delta grows, or whether they too start moving.
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

    zeros = [mp.im(mp.zetazero(n)) for n in range(1, 12)]  # up to zero #11, covers k=0..9's pairs
    print(f"[{time.time()-t0:.1f}s] zeros ready", flush=True)

    K_pair_cache = {}

    def K_at(idx):
        if idx not in K_pair_cache:
            rho = mp.mpc('0.5', zeros[idx])
            K_pair_cache[idx] = K_pair_matrix(fns, rho, cache)
        return K_pair_cache[idx]

    deltas = [mp.mpf(x) for x in ['0.1', '0.15', '0.2', '0.3', '0.45']]
    test_pairs = [1, 2, 9]  # k=1 (closest to firing at delta=0.1), k=2 (2nd closest), k=9 (plateau rep)

    results = {}
    for k in test_pairs:
        gamma_i, gamma_j = zeros[k], zeros[k + 1]
        gamma0 = (gamma_i + gamma_j) / 2
        K_base = K200 - K_at(k) - K_at(k + 1)
        row = {}
        for delta in deltas:
            t_d = time.time()
            S = S_quadruple_matrix(fns, delta, gamma0, cache)
            lmin = lambda_min_gen_eig(K_base + S, G)
            fires = lmin < 0
            row[str(delta)] = {"lam_min": str(lmin), "fires": fires}
            print(f"[{time.time()-t_d:.1f}s] k={k} (gamma0={float(gamma0):.3f}) delta={float(delta):.2f}: "
                  f"lam_min={lmin}  {'FIRES' if fires else 'survives'}", flush=True)
        results[f"k{k}"] = {"gamma0": str(gamma0), "deltas": row}

    out = {"note": "delta-sweep on the two closest-to-firing survivors (k=1,k=2) and one plateau "
                   "representative (k=9) from the Letter 158 pilot",
           "results": results, "wall_seconds": time.time() - t0}
    path = '/workspace/Riemann/repo/data/code/m3_L159_delta_sweep_result.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")


if __name__ == '__main__':
    main()
