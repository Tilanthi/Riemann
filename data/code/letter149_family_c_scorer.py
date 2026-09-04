"""
Letter 149 (astra-pa / m3) -- independent scorer for BEAST's Family C (cycle-23 composition-with-
near-cancellation family, 00b3277 + a961240). Builds the EXACT (fully diagonalized, non-perturbative)
lambda_min at all five rungs R0-R4, on my own from-scratch mpmath instrument (dps=45), using ONLY the
publicly-disclosed configuration parameters (removed ordinates, inserted gamma/delta per rung) --
no reference to BEAST's sealed scored_cycle23.json or its hash contents.

Two classes of output, kept structurally separate:
  (A) PUBLIC checks -- quantities BEAST already disclosed in the clear (composed launch values,
      spectral gaps). Computing and comparing these is pure instrument validation, no blind content.
  (B) SEALED scores -- the exact lambda_min at R0-R4 with real (nonzero, non-degenerate) deltas
      applied. These are the quantities Mac's still-uncommitted delta^4 prediction will be graded
      against. NOT published in this run; hashed and held per the three-role protocol (m1 predicts,
      m3 scores) mirrored on BEAST's own sealing discipline (cycle23-SEAL).
"""
import sys, time, json, hashlib
sys.path.insert(0, '/tmp')
from identity_check_m8 import load_genome as load_genome_mp
import mpmath as mp

mp.mp.dps = 45


def u_of_s_mp(fi, s, pts=None):
    if pts is None:
        pts = fi.breakpoints()
    re = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).real, pts)
    im = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).imag, pts)
    return mp.mpc(re, im)


def K_pair_matrix(fns, rho, cache):
    M = len(fns)
    U = [Uc(fns, i, rho, cache) for i in range(M)]
    K = mp.zeros(M, M)
    for i in range(M):
        for j in range(M):
            K[i, j] = 2 * (U[i] * mp.conj(U[j])).real
    return K


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
    print(f"[{time.time()-t0:.1f}s] loaded genomes/K_T200/G ({seed}/M{M})", flush=True)

    # own zetazero calls, cross-checked against BEAST's stated digits (not copied into the computation)
    g1, g2, g3, g4 = (mp.im(mp.zetazero(n)) for n in (1, 2, 3, 4))
    print(f"[{time.time()-t0:.1f}s] own zeros: {g1} {g2} {g3} {g4}", flush=True)
    stated = [mp.mpf('14.13472514173469379046'), mp.mpf('21.02203963877155499263'),
              mp.mpf('25.01085758014568876321'), mp.mpf('30.42487612585951321031')]
    for mine, theirs in zip((g1, g2, g3, g4), stated):
        assert abs(mine - theirs) < mp.mpf('1e-20'), (mine, theirs)
    print("own zetazero calls match BEAST's stated ordinates to <1e-20 -- cross-check PASS", flush=True)

    rho_list = [mp.mpc('0.5', g) for g in (g1, g2, g3, g4)]
    K_removed = mp.zeros(M, M)
    for rho in rho_list:
        K_removed += K_pair_matrix(fns, rho, cache)
    K_base = K200 - K_removed
    print(f"[{time.time()-t0:.1f}s] K_base (4 zeros removed) built", flush=True)

    gamma_a = mp.mpf('18.43929670238273204181427')
    gamma_b_R03 = mp.mpf('26.36436221657414487498832')
    delta_b_cancel = mp.mpf('0.07208635197257083638787626')
    gamma_b_R4 = mp.mpf('25.68760989835991681910105')

    # ---- (A) PUBLIC check: composed launch (delta_a=delta_b=0), already disclosed by BEAST ----
    S_a0 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_a, cache)
    S_b0_R03 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_b_R03, cache)
    launch_R03 = K_base + S_a0 + S_b0_R03
    lmin_launch_R03, _ = lambda_min_gen_eig(launch_R03, G)
    print(f"[{time.time()-t0:.1f}s] PUBLIC composed launch (R0-R3) lambda_min = {lmin_launch_R03}", flush=True)
    print("  compare BEAST's disclosed 4.2496273813877281464e-6", flush=True)

    S_b0_R4 = S_quadruple_matrix(fns, mp.mpf('0'), gamma_b_R4, cache)
    launch_R4 = K_base + S_a0 + S_b0_R4
    lmin_launch_R4, _ = lambda_min_gen_eig(launch_R4, G)
    print(f"[{time.time()-t0:.1f}s] PUBLIC R4 launch lambda_min = {lmin_launch_R4}", flush=True)
    print("  compare BEAST's disclosed 4.08453808416483684e-6", flush=True)

    # ---- (B) SEALED: exact lambda_min at the five real-delta rungs ----
    rungs = {
        "R0": (mp.mpf('0.1'), gamma_a, mp.mpf('0'), gamma_b_R03),
        "R1": (mp.mpf('0'), gamma_a, delta_b_cancel, gamma_b_R03),
        "R2": (mp.mpf('0.1'), gamma_a, delta_b_cancel, gamma_b_R03),
        "R3": (mp.mpf('0.1'), gamma_a, mp.mpf('0.2'), gamma_b_R03),
        "R4": (mp.mpf('0.1'), gamma_a, mp.mpf('0.1'), gamma_b_R4),
    }
    sealed = {}
    for name, (da, ga, db, gb) in rungs.items():
        t_r = time.time()
        Sa = S_quadruple_matrix(fns, da, ga, cache)
        Sb = S_quadruple_matrix(fns, db, gb, cache)
        S_Z = K_base + Sa + Sb
        lmin, _ = lambda_min_gen_eig(S_Z, G)
        sealed[name] = str(lmin)
        print(f"[{time.time()-t_r:.1f}s] {name} computed (value withheld from stdout is false -- "
              f"printed to a file only, not here)", flush=True)

    out = {
        "note": "m3's independent exact scoring of BEAST's cycle-23 Family C ladder (00b3277/a961240). "
                "SEALED pending m1's blind delta^4 prediction commit -- do not read this file before "
                "that commit lands.",
        "public_checks": {
            "launch_R03": str(lmin_launch_R03),
            "launch_R4": str(lmin_launch_R4),
        },
        "sealed_rungs": sealed,
        "dps": mp.mp.dps,
        "wall_seconds": time.time() - t0,
    }
    path = '/workspace/Riemann/repo/data/code/letter149_family_c_SEALED.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")
    print(f"sha256({path.split('/')[-1]}) = {h}")


if __name__ == '__main__':
    main()
