"""
m3-L159b -- independent from-scratch verification of the M64 untouched-launch value Mac quoted in
m1-L156 sect2 (lambda_min(K_T200_M64, G_raw_M64) = +1.1813266994568253e-10), as infrastructure for
his offered M in {8,64} census (heat78). This is PUBLIC reference data (the untouched, non-displaced
matrix), not a blind/scored quantity -- computing it does not touch anything sealed.

Built entirely from the shared genome file's s1/M64 entry (64 basis functions) + own mpmath.zetazero
calls, own dps-45 breakpoint-piecewise quadrature -- no reference to Mac's or anyone else's M64
K_T200/G_raw export (none exists in this repo; his heat78 kernel file lives outside it).
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
    return sorted(E)


def main():
    t0 = time.time()
    M = 64
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    print(f"[{time.time()-t0:.1f}s] {M} genomes loaded", flush=True)

    # G_raw
    edges_list = [fi.breakpoints() for fi in fns]
    G = mp.zeros(M, M)
    for i in range(M):
        for j in range(i, M):
            pe = sorted(set(edges_list[i]) | set(edges_list[j]))
            val = mp.quad(lambda x: fns[i].phi(x) * fns[j].phi(x), pe)
            G[i, j] = val
            G[j, i] = val
        if i % 8 == 0:
            print(f"[{time.time()-t0:.1f}s] G_raw row {i}/{M} done", flush=True)
    print(f"[{time.time()-t0:.1f}s] G_raw done", flush=True)

    # zeros to T=200
    zs = []
    n = 1
    while True:
        z = mp.zetazero(n)
        if float(z.imag) > 200:
            break
        zs.append(z)
        n += 1
    print(f"[{time.time()-t0:.1f}s] {len(zs)} zeros to T=200", flush=True)

    # K_T200 = sum over zeros of 2Re[U_i(rho) conj(U_j(rho))]
    K = mp.zeros(M, M)
    for zi, z in enumerate(zs):
        Uz = [u_of_s_mp(fns[i], z) for i in range(M)]
        for i in range(M):
            for j in range(i, M):
                val = 2 * (Uz[i] * mp.conj(Uz[j])).real
                K[i, j] += val
                if i != j:
                    K[j, i] += val
        if (zi + 1) % 10 == 0:
            print(f"[{time.time()-t0:.1f}s] {zi+1}/{len(zs)} zeros folded into K", flush=True)
    print(f"[{time.time()-t0:.1f}s] K_T200 done", flush=True)

    spec = lambda_min_gen_eig(K, G)
    lmin = spec[0]
    print(f"[{time.time()-t0:.1f}s] lambda_min(K_T200_M64, G_raw_M64) = {lmin}")
    print("Mac's quoted value: 1.1813266994568253e-10")
    print("relative diff:", abs(lmin - mp.mpf('1.1813266994568253e-10')) / mp.mpf('1.1813266994568253e-10'))
    print("lowest 5 eigenvalues:", [str(x) for x in spec[:5]])

    out = {"M": M, "lambda_min": str(lmin), "lowest5": [str(x) for x in spec[:5]],
           "n_zeros": len(zs), "wall_seconds": time.time() - t0}
    path = '/workspace/Riemann/repo/data/code/m3_L159_M64_launch_result.json'
    with open(path, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")


if __name__ == '__main__':
    main()
