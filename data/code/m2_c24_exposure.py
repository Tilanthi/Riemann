"""cycle24 Object A/V3+V5 -- the three measurements the census needs.

(1) SAFETY OF THE PUBLISHED REGIME: deg-8 vs external ground truth at every basis, at the
    largest ordinate any non-tail cycle-22/23 script ever evaluates (zeros210.json max = 209.576...).
(2) THE MIXED-DEGREE DEFECT in m2_tail2.py (cycle 22): bases built at DEG=10 but the Gram taken
    from m2_witness_analysis.gram(), which is hardcoded DEG=8.  Measure |G_8 - G_10|.
(3) RE-VERIFY THE CARRIED CLAIM: the deg-8 tail read |dK|_max = 4.77 over the 123 zeros
    200<gamma<=400.  Never restate a carried claim without re-measuring it.
"""
import sys, json, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from mpmath import mp
import m2_u_instrument as U
from m2_c24_gt_u import u_repo, u_composite

mp.dps = 40
half = mp.mpf(1) / 2
N = 8
gens = U.load_genomes("s1/M8")
tgt = U.load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open("zeros210.json"))]
tail = [mp.mpf(g) for g in json.load(open("tailzeros.json"))]
out = {}

print("=== (1) deg-8 vs ground truth at the published ceiling gamma = %s ===" % mp.nstr(gam[-1], 12), flush=True)
rows = []
for i in range(N):
    phi, bumps = U.make_phi(gens[i])
    ivs = U.intervals(bumps)
    for g in (gam[-1], mp.mpf(250), mp.mpf(400)):
        ut, _ = u_composite(phi, ivs, g, ppw=4, deg=4)
        u8 = u_repo(phi, ivs, g, 8)
        u10 = u_repo(phi, ivs, g, 10)
        r8 = abs(u8 - ut) / abs(ut); r10 = abs(u10 - ut) / abs(ut)
        rows.append({"basis": i, "gamma": mp.nstr(g, 8), "relerr_d8": mp.nstr(r8, 4),
                     "relerr_d10": mp.nstr(r10, 4)})
        print("  basis %d gamma=%-10s relerr_d8=%-12s relerr_d10=%s"
              % (i, mp.nstr(g, 8), mp.nstr(r8, 4), mp.nstr(r10, 4)), flush=True)
out["ceiling"] = rows

print("\n=== (2) Gram at deg 8 vs deg 10 (the m2_tail2.py mixed-degree defect) ===", flush=True)
from m2_u_instrument import breakpoints, gl_nodes, Basis
def build_G(DEG, bs):
    allpts = sorted(set(sum([breakpoints(b.bumps) for b in bs], [])))
    ivs = [(allpts[k], allpts[k+1]) for k in range(len(allpts)-1) if allpts[k+1] > allpts[k]]
    xs, ws = [], []
    for (a, b) in ivs:
        for (x, w) in gl_nodes(a, b, DEG):
            xs.append(x); ws.append(w)
    vv = [[bb.phi(x) for x in xs] for bb in bs]
    G = mp.matrix(N, N)
    for i in range(N):
        for j in range(i, N):
            s = mp.mpf(0)
            for k in range(len(xs)): s += ws[k]*vv[i][k]*vv[j][k]
            G[i, j] = s; G[j, i] = s
    return G
t0 = time.time()
b8 = [Basis(g, degree=8) for g in gens]
G8 = build_G(8, b8)
b10 = [Basis(g, degree=10) for g in gens]
G10 = build_G(10, b10)
dG = max(abs(G8[i, j]-G10[i, j]) for i in range(N) for j in range(N))
rel = dG / max(abs(G10[i, j]) for i in range(N) for j in range(N))
print("  |G_deg8 - G_deg10|_max = %s   relative = %s   (%.0fs)" % (mp.nstr(dG, 6), mp.nstr(rel, 6), time.time()-t0), flush=True)
out["gram_mixed"] = {"absmax": mp.nstr(dG, 8), "rel": mp.nstr(rel, 8)}

print("\n=== (3) re-verify the carried claim: deg-8 tail |dK|_max over 200<gamma<=400 ===", flush=True)
def zpk(bs, r):
    u = [b.u(r) for b in bs]; M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N): M[i, j] = 2*mp.re(u[i]*mp.conj(u[j]))
    return M
def lam(F, G):
    L = mp.cholesky(G); Li = mp.inverse(L); B = Li*F*Li.T; B = (B+B.T)/2
    return sorted(mp.eigsy(B, eigvals_only=True))
def mat(rows):
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N): M[i, j] = mp.mpf(rows[i][j])
    return M
K200 = mat(tgt["K_T200"])
for DEG, bs, G in ((8, b8, G8), (10, b10, G10)):
    t0 = time.time(); acc = mp.matrix(N, N)
    for g in tail:
        acc += zpk(bs, mp.mpc(half, g))
    m = max(abs(acc[i, j]) for i in range(N) for j in range(N))
    dl = lam(K200+acc, G)[0] - lam(K200, G)[0]
    print("  deg=%d  |dK|_max = %-16s  dlam_min(K_T200) = %-16s  (%.0fs)"
          % (DEG, mp.nstr(m, 6), mp.nstr(dl, 6), time.time()-t0), flush=True)
    out["tail_deg%d" % DEG] = {"dKmax": mp.nstr(m, 8), "dlam": mp.nstr(dl, 8)}
json.dump(out, open("exposure.json", "w"), indent=1)
print("done")
