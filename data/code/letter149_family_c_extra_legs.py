"""
Extra single-leg reference rungs needed to compute D(R3) and D(R4) properly (BEAST's a961240 D
formula needs single-leg shifts measured at the SAME launch baseline the composed rung uses):
  s_Bb  = leg B alone, delta_b=0.2, gamma_b_R03  -- needed for D(R3) (R3 uses gamma_b_R03)
  R0d   = leg A alone, delta_a=0.1, WITH leg B degenerate at gamma_b_R4 (delta_b=0) -- Mac's R0d
  R1c   = leg B alone, delta_b=0.1, gamma_b_R4, WITH leg A degenerate (delta_a=0) -- Mac's R1c
These are NOT part of BEAST's sealed 5-rung ladder (R0-R4) -- they're single-leg calibration points,
already openly computable from the disclosed configuration, needed only for the D-formula bookkeeping.
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
    return min(E), E


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
    gamma_b_R4 = mp.mpf('25.68760989835991681910105')

    # s_Bb: leg B alone at delta=0.2, gamma_b_R03; leg A degenerate at delta=0
    Sa0 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_a, cache)
    Sbb = S_quadruple_matrix(fns, mp.mpf('0.2'), gamma_b_R03, cache)
    lmin_Bb, _ = lambda_min_gen_eig(K_base + Sa0 + Sbb, G)
    print(f"[{time.time()-t0:.1f}s] leg-B-alone delta=0.2 (gamma_b_R03) computed", flush=True)

    # R0d: leg A alone at delta=0.1, leg B degenerate at gamma_b_R4
    Sa1 = S_quadruple_matrix(fns, mp.mpf('0.1'), gamma_a, cache)
    Sb0_R4 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_b_R4, cache)
    lmin_R0d, _ = lambda_min_gen_eig(K_base + Sa1 + Sb0_R4, G)
    print(f"[{time.time()-t0:.1f}s] R0d computed", flush=True)

    # R1c: leg B alone at delta=0.1, gamma_b_R4; leg A degenerate at delta=0
    Sb1_R4 = S_quadruple_matrix(fns, mp.mpf('0.1'), gamma_b_R4, cache)
    lmin_R1c, _ = lambda_min_gen_eig(K_base + Sa0 + Sb1_R4, G)
    print(f"[{time.time()-t0:.1f}s] R1c computed", flush=True)

    out = {"leg_B_alone_delta0.2_gammaR03": str(lmin_Bb),
           "R0d": str(lmin_R0d), "R1c": str(lmin_R1c),
           "wall_seconds": time.time() - t0}
    path = '/workspace/riemann_sealed/letter149_family_c_extra_legs.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t0:.1f}s] WROTE {path} (private, not committed to the public repo)")


if __name__ == '__main__':
    main()
