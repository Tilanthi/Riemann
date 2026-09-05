"""cycle24 Object B -- is the 15.05 ratio between m1's ||dQ_a||=4.45e-4 and ours 6.6952522e-3
a METRIC CONVENTION?  Compute P_a in every plausible convention and read off which one m1 is in.

Ours (published, 9350043): spectral norm in the G-metric = max |generalised eigenvalue of (P_a,G)|.
Candidates for m1's: raw spectral, raw Frobenius, G-metric Frobenius, correlation-scaled
(D^{-1/2} P D^{-1/2}, D=diag G), and the same five for P_b.  Also every "known conversion
constant" of G at this site, so the coincidence question is answered by a number, not by a story.
"""
import sys, json, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target, breakpoints, gl_nodes
from m2_witness_analysis import lam, mat, N

mp.dps = 40
half = mp.mpf(1) / 2
DEG = 8
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open("zeros210.json"))]
up200 = [g for g in gam if g <= 200]

t0 = time.time()
bases = [Basis(g, degree=DEG) for g in gens]
allpts = sorted(set(sum([breakpoints(b.bumps) for b in bases], [])))
ivs = [(allpts[k], allpts[k+1]) for k in range(len(allpts)-1) if allpts[k+1] > allpts[k]]
xs, ws = [], []
for (a, b) in ivs:
    for (x, w) in gl_nodes(a, b, DEG):
        xs.append(x); ws.append(w)
vv = [[bb.phi(x) for x in xs] for bb in bases]
G = mp.matrix(N, N)
for i in range(N):
    for j in range(i, N):
        s = mp.mpf(0)
        for k in range(len(xs)): s += ws[k]*vv[i][k]*vv[j][k]
        G[i, j] = s; G[j, i] = s
print("# build %.0fs" % (time.time()-t0), flush=True)

def zpk(r):
    u = [b.u(r) for b in bases]; M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N): M[i, j] = 2*mp.re(u[i]*mp.conj(u[j]))
    return M
def quad(d, g0):
    p = mp.mpc(half+d, g0); q = mp.mpc(half-d, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]; M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N): M[i, j] = 2*mp.re(up[i]*mp.conj(uq[j])+up[j]*mp.conj(uq[i]))
    return M

GA1, GA2, GB1, GB2 = up200[0], up200[1], up200[2], up200[3]
g_a = GA1+(GA2-GA1)*5/mp.mpf(8); g_b = GB1+(GB2-GB1)*2/mp.mpf(8)
K200 = mat(tgt["K_T200"])
REM = zpk(mp.mpc(half, GA1))+zpk(mp.mpc(half, GA2))+zpk(mp.mpc(half, GB1))+zpk(mp.mpc(half, GB2))
qA0 = quad(mp.mpf(0), g_a); qB0 = quad(mp.mpf(0), g_b)
L = K200-REM+qA0+qB0
ev = lam(L, G); gap = ev[1]-ev[0]
DA = mp.mpf("0.1"); DB = mp.mpf("0.07208635197257083638787626")
Pa = quad(DA, g_a)-qA0; Pb = quad(DB, g_b)-qB0

def spec2(M):
    return max(abs(e) for e in sorted(mp.eigsy(mp.matrix([[ (M[i,j]+M[j,i])/2 for j in range(N)] for i in range(N)]), eigvals_only=True)))
def frob(M):
    return mp.sqrt(sum(M[i,j]**2 for i in range(N) for j in range(N)))
Lc = mp.cholesky(G); Li = mp.inverse(Lc)
def toG(M):
    B = Li*M*Li.T
    return mp.matrix([[ (B[i,j]+B[j,i])/2 for j in range(N)] for i in range(N)])
D = [mp.sqrt(G[i,i]) for i in range(N)]
def corr(M):
    return mp.matrix([[ M[i,j]/(D[i]*D[j]) for j in range(N)] for i in range(N)])

evG = sorted(mp.eigsy(mp.matrix([[ (G[i,j]+G[j,i])/2 for j in range(N)] for i in range(N)]), eigvals_only=True))
print("gap = %s" % mp.nstr(gap, 12))
print("G spectrum: lmin=%s lmax=%s cond=%s sqrt(cond)=%s 1/lmin=%s 1/sqrt(lmin)=%s"
      % (mp.nstr(evG[0], 8), mp.nstr(evG[-1], 8), mp.nstr(evG[-1]/evG[0], 8),
         mp.nstr(mp.sqrt(evG[-1]/evG[0]), 8), mp.nstr(1/evG[0], 8), mp.nstr(1/mp.sqrt(evG[0]), 8)))
print("diag(G): %s" % [mp.nstr(G[i,i], 6) for i in range(N)])

TARGET = mp.mpf("4.45e-4")
for nm, P in (("P_a", Pa), ("P_b", Pb)):
    cands = {
        "G-metric spectral (OURS)": spec2(toG(P)),
        "G-metric Frobenius": frob(toG(P)),
        "raw spectral": spec2(P),
        "raw Frobenius": frob(P),
        "raw max|entry|": max(abs(P[i,j]) for i in range(N) for j in range(N)),
        "corr spectral": spec2(corr(P)),
        "corr Frobenius": frob(corr(P)),
        "G^-1 P spectral": spec2(mp.inverse(G)*P),
    }
    print("\n== %s ==" % nm)
    for k, v in sorted(cands.items(), key=lambda kv: -kv[1]):
        print("  %-26s %14s   /gap = %-12s  ours/this = %s"
              % (k, mp.nstr(v, 8), mp.nstr(v/gap, 8), mp.nstr(cands["G-metric spectral (OURS)"]/v, 6)))
    best = min(cands.items(), key=lambda kv: abs(mp.log(kv[1]/TARGET)))
    print("  closest to m1's 4.45e-4: %s = %s (factor %s)" % (best[0], mp.nstr(best[1], 8), mp.nstr(best[1]/TARGET, 6)))
json.dump({"gap": mp.nstr(gap, 14), "G_lmin": mp.nstr(evG[0], 12), "G_lmax": mp.nstr(evG[-1], 12)},
          open("normconv.json", "w"), indent=1)
