"""
m3-L162 part 2 -- independent third-instrument spot-check of specific M64 census cells (m1-L165),
using the from-scratch M64 kernel built in m3_L162_M64_full_kernel_build.py (own zetazero calls, own
dps-45 quadrature, no reference to Mac's heat78a kernel file).

Cells checked (arm A, phi=4/8 midpoint, M=64):
  k=16 delta=0.05 -- the "inversion" cell, should SURVIVE (the one exception to the height-ordering rule)
  k=16 delta=0.1  -- should FIRE (confirms the inversion needs delta=0.1, not 0.05, unlike its neighbors)
  k=20 delta=0.05 -- one of the 9 true M64 survivors
  k=15 delta=0.05 -- one of the 3 "reorganization" flips (marginal, barely negative)
  k=22 delta=0.1  -- another reorganization flip
  k=23 delta=0.1  -- another reorganization flip
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


def gram(fns, M, rho, cache):
    U = [Uc(fns, i, rho, cache) for i in range(M)]
    K = mp.zeros(M, M)
    for i in range(M):
        for j in range(M):
            K[i, j] = 2 * (U[i] * mp.conj(U[j])).real
    return K


def quad_ex(fns, M, g0, delta, cache):
    p, q = mp.mpc(mp.mpf('0.5') + delta, g0), mp.mpc(mp.mpf('0.5') - delta, g0)
    up = [Uc(fns, i, p, cache) for i in range(M)]
    uq = [Uc(fns, i, q, cache) for i in range(M)]
    S = mp.zeros(M, M)
    for i in range(M):
        for j in range(M):
            S[i, j] = 2 * (up[i] * mp.conj(uq[j])).real + 2 * (up[j] * mp.conj(uq[i])).real
    return S


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
    M = 64
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    d = json.load(open('/workspace/Riemann/repo/data/code/m3_L162_M64_kernel_full.json'))
    assert d['M'] == M
    K200 = mp.matrix(M, M)
    G = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            K200[i, j] = mp.mpf(d['K_T200'][i][j])
            G[i, j] = mp.mpf(d['G_raw'][i][j])
    print(f"[{time.time()-t0:.1f}s] kernel loaded", flush=True)

    cache = {}
    # own zetazero calls for indices 16..25 (covers k up to 24: zeros[k]=zetazero(k+1))
    zdict = {n: mp.im(mp.zetazero(n)) for n in range(16, 26)}
    print(f"[{time.time()-t0:.1f}s] zeros ready", flush=True)

    def zeros_k(k):
        return zdict[k + 1], zdict[k + 2]

    def g_of(k, phi8):
        zi, zj = zeros_k(k)
        return zi + (zj - zi) * mp.mpf(phi8) / 8

    census_ref = {
        (16, '0.05'): mp.mpf('5.053612052269358070563243e-11'),
        (16, '0.1'): mp.mpf('-0.0000007980718943933414519252095'),
        (20, '0.05'): mp.mpf('9.928773791557768914406345e-11'),
        (15, '0.05'): mp.mpf('-6.329602530638020047891359e-10'),
        (22, '0.1'): mp.mpf('-2.135176833101324708185699e-10'),
        (23, '0.1'): mp.mpf('-1.214758777067231931212808e-10'),
    }

    cells = [(16, '0.05'), (16, '0.1'), (20, '0.05'), (15, '0.05'), (22, '0.1'), (23, '0.1')]
    for (k, dstr) in cells:
        t_c = time.time()
        zi, zj = zeros_k(k)
        g0 = g_of(k, 4)
        delta = mp.mpf(dstr)
        K_S = K200 - gram(fns, M, mp.mpc('0.5', zi), cache) - gram(fns, M, mp.mpc('0.5', zj), cache) \
              + quad_ex(fns, M, g0, delta, cache)
        lmin = lambda_min_gen_eig(K_S, G)
        ref = census_ref[(k, dstr)]
        rel = abs(lmin / ref - 1) if ref != 0 else None
        fires = lmin < mp.mpf('-1e-12')
        print(f"[{time.time()-t_c:.1f}s] k={k} delta={dstr}: mine={lmin}  census={ref}  "
              f"rel_diff={rel}  fires={fires}", flush=True)

    print(f"[{time.time()-t0:.1f}s] all cells done")


if __name__ == '__main__':
    main()
