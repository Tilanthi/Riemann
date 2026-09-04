"""machine2 cycle23 -- does m1's heat72n ordinate TRUNCATION move lam_min?

His SWEEPS list is ["14.134725","14.9956","15.8566","16.7175","17.5784","18.4393",
"19.3002","20.1611","21.0220"]; the exact grid points are gamma1 + (gamma2-gamma1)*m/8
with gamma1,gamma2 the first two zeta zeros.  Offsets are up to 4.6e-5.  The ty4/ex ratio
is invariant to this (both legs share the ordinate), but the comparison against m2's
scored row is not.  Measured here at delta=0.1, single pair, gap A.
"""
import json, os, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N
mp.dps = 40
half = mp.mpf(1)/2
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam=[mp.mpf(g) for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeros210.json")))]
bases=[Basis(g,degree=8) for g in gens]
G=gram(); K200=mat(tgt["K_T200"])
g1,g2=gam[0],gam[1]
rem=zero_pair_K(mp.mpc(half,g1))+zero_pair_K(mp.mpc(half,g2))
base=K200-rem
def quad(d,g0):
    p=mp.mpc(half+d,g0); q=mp.mpc(half-d,g0)
    up=[b.u(p) for b in bases]; uq=[b.u(q) for b in bases]; M=mp.matrix(N,N)
    for i in range(N):
        for j in range(N): M[i,j]=2*mp.re(up[i]*mp.conj(uq[j])+up[j]*mp.conj(uq[i]))
    return M
M1=["14.134725","14.9956","15.8566","16.7175","17.5784","18.4393","19.3002","20.1611","21.0220"]
D=mp.mpf("0.1")
print("%14s %14s %10s %16s %16s %10s"%("exact grid g0","m1 string","offset","lam(exact g0)","lam(m1 g0)","rel diff"))
rows=[]
for m in range(9):
    ge=g1+(g2-g1)*m/mp.mpf(8); gm1=mp.mpf(M1[m])
    le=lam(base+quad(D,ge),G)[0]; lm=lam(base+quad(D,gm1),G)[0]
    rel=abs(lm-le)/abs(le)
    rows.append({"g_exact":mp.nstr(ge,20),"g_m1":M1[m],"offset":mp.nstr(gm1-ge,6),
                 "lam_exact":mp.nstr(le,14),"lam_m1":mp.nstr(lm,14),"rel":mp.nstr(rel,8)})
    print("%14s %14s %10s %16s %16s %10s"%(mp.nstr(ge,10),M1[m],mp.nstr(gm1-ge,3),
          mp.nstr(le,9),mp.nstr(lm,9),mp.nstr(rel*100,5)+"%"),flush=True)
json.dump(rows,open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ordcheck.json"), "w"),indent=1)
