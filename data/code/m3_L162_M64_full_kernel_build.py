"""
m3-L162 -- build and CACHE the full K_T200_M64/G_raw_M64 matrices from scratch (own zetazero calls,
own dps-45 quadrature, no reference to Mac's heat78a kernel file), so they can be reused for
independent spot-checks of specific census cells without repeating the ~2.4h base computation each
time. This is the same public-reference-data computation as m3_L159_M64_launch_verify.py, extended to
save the full matrices (that script only saved the launch eigenvalues).

After this completes, m3_L162_census_cell_verify.py will use these matrices to independently verify
specific cells from Mac's now-fully-revealed heat78c census (m1-L165), post-reveal, third-instrument
style -- exactly the CYCLE-23 pattern.
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


def main():
    t0 = time.time()
    M = 64
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    print(f"[{time.time()-t0:.1f}s] {M} genomes loaded", flush=True)

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

    zs = []
    n = 1
    while True:
        z = mp.zetazero(n)
        if float(z.imag) > 200:
            break
        zs.append(z)
        n += 1
    print(f"[{time.time()-t0:.1f}s] {len(zs)} zeros to T=200", flush=True)

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

    out = {
        "M": M, "seed": seed, "dps": mp.mp.dps, "n_zeros": len(zs),
        "K_T200": [[str(K[i, j]) for j in range(M)] for i in range(M)],
        "G_raw": [[str(G[i, j]) for j in range(M)] for i in range(M)],
        "wall_seconds": time.time() - t0,
    }
    path = '/workspace/Riemann/repo/data/code/m3_L162_M64_kernel_full.json'
    with open(path, 'w') as fh:
        json.dump(out, fh)
    print(f"[{time.time()-t0:.1f}s] WROTE {path}")


if __name__ == '__main__':
    main()
