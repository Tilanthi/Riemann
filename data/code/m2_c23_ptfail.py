"""machine2 cycle23 -- WHY second-order PT missed by 17x: the validity check I used
(|f|/gap, diagonal element at v0) is the wrong one; the operator norm of the perturbation
in the G-metric is what has to be small against the spectral gap.  Also a degree-10
refinement certificate on the scored rungs."""
import json, os, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N
mp.dps=40
half=mp.mpf(1)/2
HERE=os.path.dirname(os.path.abspath(__file__))
gens=load_genomes("s1/M8"); tgt=load_target("s1/M8")
gam=[mp.mpf(g) for g in json.load(open(os.path.join(HERE,"zeros210.json")))]
up200=[g for g in gam if g<=200]
def build(DEG):
    bs=[Basis(g,degree=DEG) for g in gens]
    from m2_u_instrument import breakpoints, gl_nodes
    allpts=sorted(set(sum([breakpoints(b.bumps) for b in bs],[])))
    ivs=[(allpts[k],allpts[k+1]) for k in range(len(allpts)-1) if allpts[k+1]>allpts[k]]
    xs,ws=[],[]
    for (a,b) in ivs:
        for (x,w) in gl_nodes(a,b,DEG): xs.append(x); ws.append(w)
    vv=[[bb.phi(x) for x in xs] for bb in bs]
    Gm=mp.matrix(N,N)
    for i in range(N):
        for j in range(i,N):
            s=mp.mpf(0)
            for k in range(len(xs)): s+=ws[k]*vv[i][k]*vv[j][k]
            Gm[i,j]=s; Gm[j,i]=s
    return bs,Gm
for DEG in (8,10):
    bases,G=build(DEG)
    K200=mat(tgt["K_T200"])
    def zpk(r):
        u=[b.u(r) for b in bases]; M=mp.matrix(N,N)
        for i in range(N):
            for j in range(N): M[i,j]=2*mp.re(u[i]*mp.conj(u[j]))
        return M
    def quad(d,g0):
        p=mp.mpc(half+d,g0); q=mp.mpc(half-d,g0)
        up=[b.u(p) for b in bases]; uq=[b.u(q) for b in bases]; M=mp.matrix(N,N)
        for i in range(N):
            for j in range(N): M[i,j]=2*mp.re(up[i]*mp.conj(uq[j])+up[j]*mp.conj(uq[i]))
        return M
    GA1,GA2,GB1,GB2=up200[0],up200[1],up200[2],up200[3]
    REM=zpk(mp.mpc(half,GA1))+zpk(mp.mpc(half,GA2))+zpk(mp.mpc(half,GB1))+zpk(mp.mpc(half,GB2))
    g_a=GA1+(GA2-GA1)*5/mp.mpf(8); g_b=GB1+(GB2-GB1)*2/mp.mpf(8)
    qA0=quad(mp.mpf(0),g_a); qB0=quad(mp.mpf(0),g_b)
    L=K200-REM+qA0+qB0
    ev=lam(L,G)
    DA=mp.mpf("0.1"); DB=mp.mpf("0.07208635197257083638787626")
    Pa=quad(DA,g_a)-qA0; Pb=quad(DB,g_b)-qB0
    pa=lam(Pa,G); pb=lam(Pb,G)
    r0=lam(L+Pa,G)[0]; r2=lam(L+Pa+Pb,G)[0]
    print("DEG=%d  launch=%s gap=%s"%(DEG,mp.nstr(ev[0],16),mp.nstr(ev[1]-ev[0],10)))
    print("   ||P_a|| G-metric spectrum extremes: %s .. %s"%(mp.nstr(pa[0],8),mp.nstr(pa[-1],8)))
    print("   ||P_b|| G-metric spectrum extremes: %s .. %s"%(mp.nstr(pb[0],8),mp.nstr(pb[-1],8)))
    print("   norm(P_a)/gap = %s   norm(P_b)/gap = %s"%(
        mp.nstr(max(abs(pa[0]),abs(pa[-1]))/(ev[1]-ev[0]),6),
        mp.nstr(max(abs(pb[0]),abs(pb[-1]))/(ev[1]-ev[0]),6)))
    print("   R0 exact = %s   R2 exact = %s"%(mp.nstr(r0,16),mp.nstr(r2,16)))
