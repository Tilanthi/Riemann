"""machine2 cycle23 -- T-truncation budget for the COMPOSED launch, at a node budget
certified to gamma=400 (deg 10).  Re-run because the deg-8 budget is known (cycle-22 own
failure #2) to be eight orders wrong at gamma~350: the deg-8 read gave |dK|_max=4.77.
Also doubles as a refinement check on the launch itself (deg 8 vs deg 10)."""
import json, os, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, N
mp.dps = 40
half = mp.mpf(1)/2
DEG = 10
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open("zeros210.json"))]
up200 = [g for g in gam if g <= 200]
tail = [mp.mpf(g) for g in json.load(open("tailzeros.json"))]
t0=time.time()
bases = [Basis(g, degree=DEG) for g in gens]
print("# deg=%d nodes/basis=%s build %.1fs" % (DEG, [len(b.xs) for b in bases], time.time()-t0), flush=True)
def gram10():
    from m2_u_instrument import breakpoints, gl_nodes
    allpts = sorted(set(sum([breakpoints(b.bumps) for b in bases], [])))
    ivs = [(allpts[k], allpts[k+1]) for k in range(len(allpts)-1) if allpts[k+1] > allpts[k]]
    xs, ws = [], []
    for (a,b) in ivs:
        for (x,w) in gl_nodes(a,b,DEG):
            xs.append(x); ws.append(w)
    vals = [[bb.phi(x) for x in xs] for bb in bases]
    Gm = mp.matrix(N,N)
    for i in range(N):
        for j in range(i,N):
            s = mp.mpf(0)
            for k in range(len(xs)): s += ws[k]*vals[i][k]*vals[j][k]
            Gm[i,j]=s; Gm[j,i]=s
    return Gm
G = gram10(); K200 = mat(tgt["K_T200"])
def zpk(rho):
    u=[b.u(rho) for b in bases]; M=mp.matrix(N,N)
    for i in range(N):
        for j in range(N): M[i,j]=2*mp.re(u[i]*mp.conj(u[j]))
    return M
def quad(delta,g0):
    p=mp.mpc(half+delta,g0); q=mp.mpc(half-delta,g0)
    up=[b.u(p) for b in bases]; uq=[b.u(q) for b in bases]; M=mp.matrix(N,N)
    for i in range(N):
        for j in range(N): M[i,j]=2*mp.re(up[i]*mp.conj(uq[j])+up[j]*mp.conj(uq[i]))
    return M
def eig_full(F,Gm):
    L=mp.cholesky(Gm); Li=mp.inverse(L); B=Li*F*Li.T; B=(B+B.T)/2
    E,V=mp.eigsy(B); idx=sorted(range(N), key=lambda i:E[i])
    return [E[i] for i in idx],[Li.T*mp.matrix([V[r,i] for r in range(N)]) for i in idx]
def bil(M,v,w):
    s=mp.mpf(0)
    for i in range(N):
        for j in range(N): s+=v[i]*M[i,j]*w[j]
    return s
GA1,GA2,GB1,GB2 = up200[0],up200[1],up200[2],up200[3]
g_a = GA1+(GA2-GA1)*5/mp.mpf(8); g_b = GB1+(GB2-GB1)*2/mp.mpf(8)
L = K200 - zpk(mp.mpc(half,GA1)) - zpk(mp.mpc(half,GA2)) - zpk(mp.mpc(half,GB1)) - zpk(mp.mpc(half,GB2)) \
    + quad(mp.mpf(0),g_a) + quad(mp.mpf(0),g_b)
vals,vecs = eig_full(L,G); v0=vecs[0]
print("# deg10 composed launch lam_min = %s  (deg8: 4.2496273813877281464e-6)" % mp.nstr(vals[0],20), flush=True)
print("# deg10 spectral gap = %s  (deg8: 5.84529811238e-6)" % mp.nstr(vals[1]-vals[0],12), flush=True)
acc = mp.matrix(N,N)
bands=[250,300,350,400]; bi=0
for g in tail:
    acc += zpk(mp.mpc(half,g))
    while bi < len(bands) and g > bands[bi]:
        m=max(abs(acc[i,j]) for i in range(N) for j in range(N))
        print("  200<g<=%d |dK|max=%s  dlam_launch=%s" % (bands[bi], mp.nstr(m,5),
              mp.nstr(eig_full(L+acc,G)[0][0]-vals[0],5)), flush=True)
        bi+=1
m=max(abs(acc[i,j]) for i in range(N) for j in range(N))
dl=eig_full(L+acc,G)[0][0]-vals[0]
print("  200<g<=400 |dK|max=%s  dlam_launch=%s  v0^T dK v0=%s" % (mp.nstr(m,5), mp.nstr(dl,5), mp.nstr(bil(acc,v0,v0),5)))
json.dump({"deg":DEG,"launch_lam":mp.nstr(vals[0],20),"gap":mp.nstr(vals[1]-vals[0],14),
           "dKmax":mp.nstr(m,8),"dlam":mp.nstr(dl,8),"v0dKv0":mp.nstr(bil(acc,v0,v0),8)},
          open("tail_budget.json","w"), indent=1)
print("done %.1fs" % (time.time()-t0))
