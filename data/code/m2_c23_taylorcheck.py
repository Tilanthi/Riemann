"""machine2 cycle23 -- third implementation of the delta^2 / delta^4 truncated local theory,
checked at the ONE point where m1's gamma0-sweep and m3's delta-ladder cross
(gamma_0 = 17.5784 gap-A midpoint, delta = 0.1).  Receipt only; no new configuration."""
import json, os
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N
mp.dps = 40
half = mp.mpf(1)/2
gens=load_genomes("s1/M8"); tgt=load_target("s1/M8")
gam=[mp.mpf(g) for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeros210.json")))]
bases=[Basis(g,degree=8) for g in gens]
G=gram(); K200=mat(tgt["K_T200"])
g1,g2=gam[0],gam[1]; g0=(g1+g2)/2
base=K200-zero_pair_K(mp.mpc(half,g1))-zero_pair_K(mp.mpc(half,g2))
s0=mp.mpc(half,g0)
def deriv(b,k):
    tot=mp.mpc(0)
    for x,w in zip(b.xs,b.ws): tot += w*(x**k)*mp.exp(s0*x)
    return tot
DER=[[deriv(b,k) for k in range(5)] for b in bases]
def utaylor(i,d,K):
    return sum(DER[i][k]*(d**k)/mp.factorial(k) for k in range(K+1))
def Smat(up,uq):
    M=mp.matrix(N,N)
    for i in range(N):
        for j in range(N): M[i,j]=2*mp.re(up[i]*mp.conj(uq[j])+up[j]*mp.conj(uq[i]))
    return M
d=mp.mpf("0.1")
p=mp.mpc(half+d,g0); q=mp.mpc(half-d,g0)
ex = lam(base+Smat([b.u(p) for b in bases],[b.u(q) for b in bases]),G)[0]
t2 = lam(base+Smat([utaylor(i,d,2) for i in range(N)],[utaylor(i,-d,2) for i in range(N)]),G)[0]
t4 = lam(base+Smat([utaylor(i,d,4) for i in range(N)],[utaylor(i,-d,4) for i in range(N)]),G)[0]
print("gamma_0 = %s  delta = %s" % (mp.nstr(g0,12), d))
print("exact     %s   (m3 -6.97325e-6, m1 -6.973e-6, m2 cycle22 -6.97324649e-6)" % mp.nstr(ex,14))
print("taylor2   %s   (m3 -3.44976e-6, m1 -3.450e-6)" % mp.nstr(t2,14))
print("taylor4   %s   (m3 -6.86629e-6)" % mp.nstr(t4,14))
print("ty2/ex-1  %s%%   (m1 table: -50.5%%)" % mp.nstr((t2/ex-1)*100,6))
print("ty4/ex-1  %s%%   (m1 table: -1.53%%; m3 residual 1.534%%)" % mp.nstr((t4/ex-1)*100,6))
print("gap closed by order 4 = %s%%   (m3: 97.0%%)" % mp.nstr((t4-t2)/(ex-t2)*100,6))
json.dump({"g0":mp.nstr(g0,20),"delta":str(d),"exact":mp.nstr(ex,18),"ty2":mp.nstr(t2,18),
           "ty4":mp.nstr(t4,18),"ty2_rel":mp.nstr((t2/ex-1)*100,8),"ty4_rel":mp.nstr((t4/ex-1)*100,8),
           "closure":mp.nstr((t4-t2)/(ex-t2)*100,8)}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "taylorcheck.json"), "w"), indent=1)
