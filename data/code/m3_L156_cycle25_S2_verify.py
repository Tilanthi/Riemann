"""
m3-L156 -- independent third-instrument verification of BEAST's cycle-25 site S2 (the second
exact-cancellation family, gaps k=2/k=4). Built from scratch from BEAST's disclosed configuration
alone (removed ordinates, gamma_a/gamma_b/gamma_b', deltas per rung) -- own zetazero calls, own
dps-45 quadrature, no reference to their revealed exact lam_min values until the final comparison.

This is the same methodology as m3's cycle-23 Family C verification (Letters 149/150): a genuinely
independent instrument, not a re-run of their code.
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

    # own zetazero calls for the four removed on-line ordinates, cross-checked against BEAST's
    # stated digits (not copied into the computation)
    g3, g4, g5, g6 = (mp.im(mp.zetazero(n)) for n in (3, 4, 5, 6))
    print(f"[{time.time()-t0:.1f}s] own zeros: {g3} {g4} {g5} {g6}", flush=True)
    stated = [mp.mpf('25.0108575801456887632'), mp.mpf('30.4248761258595132103'),
              mp.mpf('32.9350615876781787143'), mp.mpf('37.5861781587510215000')]
    names = ['g3', 'g4', 'g5', 'g6']
    for nm, mine, theirs in zip(names, (g3, g4, g5, g6), stated):
        diff = abs(mine - theirs)
        status = "PASS" if diff < mp.mpf('1e-15') else "MISMATCH"
        print(f"cross-check {nm}: mine={mine} theirs={theirs} diff={diff} [{status}]", flush=True)
    print("proceeding with MY OWN (independently verified) zero values regardless of the check "
          "above -- using stated digits would repeat any transcription error rather than test it",
          flush=True)

    rho_list = [mp.mpc('0.5', g) for g in (g3, g4, g5, g6)]
    K_removed = mp.zeros(M, M)
    for rho in rho_list:
        K_removed += K_pair_matrix(fns, rho, cache)
    K_base = K200 - K_removed
    print(f"[{time.time()-t0:.1f}s] K_base (4 zeros removed) built", flush=True)

    gamma_a = mp.mpf('29.74812380764528515442463')
    gamma_b = mp.mpf('35.26061987328243047394007')
    delta_c = mp.mpf('0.164990457617287927457442')
    gamma_bp = mp.mpf('34.67923030189662027812064')

    rungs = {
        "launch": (mp.mpf('0'), gamma_b, mp.mpf('0')),
        "R0":     (mp.mpf('0.1'), gamma_b, mp.mpf('0')),
        "R1":     (mp.mpf('0'), gamma_b, delta_c),
        "R2":     (mp.mpf('0.1'), gamma_b, delta_c),
        "R1b":    (mp.mpf('0'), gamma_b, mp.mpf('0.20')),
        "R3":     (mp.mpf('0.1'), gamma_b, mp.mpf('0.20')),
        "R1e":    (mp.mpf('0'), gamma_b, mp.mpf('0.30')),
        "R3b":    (mp.mpf('0.1'), gamma_b, mp.mpf('0.30')),
        "launch_prime": (mp.mpf('0'), gamma_bp, mp.mpf('0')),
        "R0s":    (mp.mpf('0.1'), gamma_bp, mp.mpf('0')),
        "R1d":    (mp.mpf('0'), gamma_bp, mp.mpf('0.1')),
        "R4":     (mp.mpf('0.1'), gamma_bp, mp.mpf('0.1')),
    }

    exact_theirs = {
        "R0": mp.mpf('1.916056298637076e-5'), "R1": mp.mpf('2.062641793975136e-5'),
        "R2": mp.mpf('1.965139368560252e-5'), "R1b": mp.mpf('2.077075500853752e-5'),
        "R3": mp.mpf('1.965794625791251e-5'), "R1e": mp.mpf('1.113546655651850e-5'),
        "R3b": mp.mpf('-2.043245275310083e-6'), "R0s": mp.mpf('1.131453492923668e-5'),
        "R1d": mp.mpf('1.234608151701594e-5'), "R4": mp.mpf('1.117720225538539e-5'),
        "launch": mp.mpf('2.0004746865698620975e-5'),
        "launch_prime": mp.mpf('1.2476977651181365402e-5'),
    }

    results = {}
    for name, (da, ga_dummy, db) in [(k, v) for k, v in rungs.items()]:
        pass  # placeholder, real loop below

    for name, (da, gb, db) in rungs.items():
        t_r = time.time()
        Sa = S_quadruple_matrix(fns, da, gamma_a, cache)
        Sb = S_quadruple_matrix(fns, db, gb, cache)
        S_Z = K_base + Sa + Sb
        lmin = lambda_min_gen_eig(S_Z, G)
        theirs = exact_theirs.get(name)
        rel = abs(lmin / theirs - 1) if theirs is not None else None
        results[name] = str(lmin)
        print(f"[{time.time()-t_r:.1f}s] {name}: mine={lmin}  theirs={theirs}  "
              f"rel_diff={float(rel) if rel is not None else 'NA'}", flush=True)

    out = {"note": "m3 independent from-scratch verification of BEAST cycle-25 site S2, own zetazero "
                   "calls + own quadrature, compared against their revealed exact column",
           "results": results, "wall_seconds": time.time() - t0}
    path = '/workspace/Riemann/repo/data/code/m3_L156_cycle25_S2_result.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")


if __name__ == '__main__':
    main()
