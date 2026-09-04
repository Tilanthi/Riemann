"""machine2 cycle22 — measured zero-side tail beyond T=200, at a node budget certified to gamma=400."""
import json
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, N
mp.dps = 40
DEG = 10
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
bases = [Basis(g, degree=DEG) for g in gens]
half = mp.mpf(1)/2
G = gram(); K200 = mat(tgt["K_T200"])
zs = [mp.mpf(g) for g in json.load(open("tailzeros.json"))]
print(f"# deg={DEG} nodes/basis={[len(b.xs) for b in bases]}  tail zeros: {len(zs)}")
lam0 = lam(K200, G)[0]
acc = mp.matrix(N, N)
bands = [250, 300, 350, 400]; bi = 0
def zpk(rho):
    u = [b.u(rho) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2*mp.re(u[i]*mp.conj(u[j]))
    return M
for g in zs:
    acc += zpk(mp.mpc(half, g))
    while bi < len(bands) and g > bands[bi]:
        m = max(abs(acc[i,j]) for i in range(N) for j in range(N))
        print(f"  200<gamma<={bands[bi]:<4} |dK|_max={mp.nstr(m,5):>12}  d lam_min={mp.nstr(lam(K200+acc,G)[0]-lam0,5)}", flush=True)
        bi += 1
m = max(abs(acc[i,j]) for i in range(N) for j in range(N))
print(f"  200<gamma<=400  |dK|_max={mp.nstr(m,5):>12}  d lam_min={mp.nstr(lam(K200+acc,G)[0]-lam0,5)}")
