"""
m3-L165 -- build K_T200/G_raw at M=16 or M=32 using the first M entries of the already-published
s1/M64 genome draw (verified: s1/M8 == s1/M64[:8] byte-for-byte), then compute the k=16 cell's
lam_min at delta in {0.05, 0.1}, for the pre-registered M-ladder test (m3-L165 letter).

Usage: python3 m3_L165_M_ladder_build.py <M>   (M = 16 or 32)
"""
import sys, time, json
sys.path.insert(0, '/tmp')
import mpmath as mp

mp.mp.dps = 45


class TestFn:
    def __init__(self, bumps):
        self.bumps = [(mp.mpf(c), mp.mpf(mu), mp.mpf(s)) for c, mu, s in bumps]

    def theta(self, s):
        if s <= 0:
            return mp.mpf(0)
        if s >= 1:
            return mp.mpf(1)
        return mp.e**(-1 / s) / (mp.e**(-1 / s) + mp.e**(-1 / (1 - s)))

    def window(self, x):
        ax = abs(x)
        if ax >= 8:
            return mp.mpf(0)
        return self.theta((8 - ax) / 2)

    def bump(self, t):
        if abs(t) >= 1:
            return mp.mpf(0)
        return mp.e**(-1 / (1 - t * t))

    def phi(self, x):
        tot = mp.mpf(0)
        for c, mu, s in self.bumps:
            tot += c * self.bump((x - mu) / s)
        return self.window(x) * tot

    def breakpoints(self):
        edges = set([mp.mpf(-8), mp.mpf(-6), mp.mpf(6), mp.mpf(8)])
        for c, mu, s in self.bumps:
            edges.add(mu - s)
            edges.add(mu + s)
        return sorted(edges)


def load_genome_slice(M):
    d = json.load(open('/workspace/Riemann/repo/data/code/machine1_heat70_genomes_m8_m64.json'))
    g64 = d['genomes']['s1/M64']
    assert len(g64) == 64
    genomes = g64[:M]
    return [TestFn(bumps) for bumps in genomes]


def u_of_s_mp(fi, s):
    pts = fi.breakpoints()
    re = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).real, pts)
    im = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).imag, pts)
    return mp.mpc(re, im)


def gram(fns, M, rho, cache):
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
    M = int(sys.argv[1])
    fns = load_genome_slice(M)
    print(f"[{time.time()-t0:.1f}s] {M} genomes loaded (sliced from s1/M64)", flush=True)

    edges_list = [fi.breakpoints() for fi in fns]
    G = mp.zeros(M, M)
    for i in range(M):
        for j in range(i, M):
            pe = sorted(set(edges_list[i]) | set(edges_list[j]))
            val = mp.quad(lambda x: fns[i].phi(x) * fns[j].phi(x), pe)
            G[i, j] = val
            G[j, i] = val
    print(f"[{time.time()-t0:.1f}s] G_raw done", flush=True)

    zs = []
    n = 1
    while True:
        z = mp.zetazero(n)
        if float(z.imag) > 200:
            break
        zs.append(z)
        n += 1
    print(f"[{time.time()-t0:.1f}s] {len(zs)} zeros to T=200", flush=True)

    K200 = mp.zeros(M, M)
    for zi, z in enumerate(zs):
        Uz = [u_of_s_mp(fns[i], z) for i in range(M)]
        for i in range(M):
            for j in range(i, M):
                val = 2 * (Uz[i] * mp.conj(Uz[j])).real
                K200[i, j] += val
                if i != j:
                    K200[j, i] += val
        if (zi + 1) % 20 == 0:
            print(f"[{time.time()-t0:.1f}s] {zi+1}/{len(zs)} zeros folded into K", flush=True)
    print(f"[{time.time()-t0:.1f}s] K_T200 done", flush=True)

    lmin_launch = lambda_min_gen_eig(K200, G)
    print(f"[{time.time()-t0:.1f}s] untouched launch lambda_min(K_T200,G) = {lmin_launch}", flush=True)

    # k=16 cell: zeros[16], zeros[17] (0-indexed, zeros[k]=zetazero(k+1)), zetazero(17),(18)
    cache = {}
    g16, g17 = mp.im(mp.zetazero(17)), mp.im(mp.zetazero(18))
    g0 = g16 + (g17 - g16) * mp.mpf(4) / 8  # phi=4/8 midpoint
    K_base = K200 - gram(fns, M, mp.mpc('0.5', g16), cache) - gram(fns, M, mp.mpc('0.5', g17), cache)

    results = {}
    for dstr in ('0.05', '0.1'):
        delta = mp.mpf(dstr)
        S = quad_ex(fns, M, g0, delta, cache)
        lmin = lambda_min_gen_eig(K_base + S, G)
        results[dstr] = str(lmin)
        print(f"[{time.time()-t0:.1f}s] k=16 delta={dstr}: lam_min = {lmin}", flush=True)

    out = {"M": M, "launch_lam_min": str(lmin_launch), "k16_results": results,
           "wall_seconds": time.time() - t0}
    path = f'/workspace/Riemann/repo/data/code/m3_L165_M{M}_result.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")


if __name__ == '__main__':
    main()
