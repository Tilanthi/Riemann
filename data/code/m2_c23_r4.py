"""machine2 cycle23 -- R4, the GENUINE same-sign control rung.
Cell (a=5,b=1) of the self-consistent scan is the '++' cell: both first-order functionals
positive.  Same removed set as R0-R3 (gap A k=0, gap B k=2); leg B moves to grid point 1.
Design data only."""
import json, os
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N
mp.dps=40
half=mp.mpf(1)/2
gens=load_genomes("s1/M8"); tgt=load_target("s1/M8")
gam=[mp.mpf(g) for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeros210.json")))]
up200=[g for g in gam if g<=200]
bases=[Basis(g,degree=8) for g in gens]
G=gram(); K200=mat(tgt["K_T200"])
def quad(d,g0):
    p=mp.mpc(half+d,g0); q=mp.mpc(half-d,g0)
    up=[b.u(p) for b in bases]; uq=[b.u(q) for b in bases]; M=mp.matrix(N,N)
    for i in range(N):
        for j in range(N): M[i,j]=2*mp.re(up[i]*mp.conj(uq[j])+up[j]*mp.conj(uq[i]))
    return M
def eig_full(F,Gm):
    L=mp.cholesky(Gm); Li=mp.inverse(L); B=Li*F*Li.T; B=(B+B.T)/2
    E,V=mp.eigsy(B); idx=sorted(range(N),key=lambda i:E[i])
    return [E[i] for i in idx],[Li.T*mp.matrix([V[r,i] for r in range(N)]) for i in idx]
def bil(M,v,w):
    s=mp.mpf(0)
    for i in range(N):
        for j in range(N): s+=v[i]*M[i,j]*w[j]
    return s
GA1,GA2,GB1,GB2=up200[0],up200[1],up200[2],up200[3]
g_a=GA1+(GA2-GA1)*5/mp.mpf(8); g_b4=GB1+(GB2-GB1)*1/mp.mpf(8)
qA0,qB0=quad(mp.mpf(0),g_a),quad(mp.mpf(0),g_b4)
L=K200-zero_pair_K(mp.mpc(half,GA1))-zero_pair_K(mp.mpc(half,GA2))\
   -zero_pair_K(mp.mpc(half,GB1))-zero_pair_K(mp.mpc(half,GB2))+qA0+qB0
vals,vecs=eig_full(L,G); v0=vecs[0]; l0=vals[0]
print("R4 launch gamma_a=%s gamma_b=%s"%(mp.nstr(g_a,25),mp.nstr(g_b4,25)))
print("R4 launch lam0=%s  gap=%s"%(mp.nstr(l0,18),mp.nstr(vals[1]-vals[0],10)))
D=mp.mpf("0.1")
Pa=quad(D,g_a)-qA0; Pb=quad(D,g_b4)-qB0
fa=bil(Pa,v0,v0); fb=bil(Pb,v0,v0)
sa=sb=X=mp.mpf(0)
for k in range(1,N):
    A=bil(Pa,v0,vecs[k]); B_=bil(Pb,v0,vecs[k]); den=vals[0]-vals[k]
    sa+=A*A/den; sb+=B_*B_/den; X+=2*A*B_/den
print("f_a=%s  f_b=%s   (same sign: %s)"%(mp.nstr(fa,14),mp.nstr(fb,14), "YES" if fa*fb>0 else "NO"))
print("self_a=%s self_b=%s CROSS=%s"%(mp.nstr(sa,12),mp.nstr(sb,12),mp.nstr(X,14)))
shift=fa+fb+sa+sb+X
print("lam_pred=%s   total shift=%s   |X|/|shift|=%s"%(mp.nstr(l0+shift,14),mp.nstr(shift,10),
      mp.nstr(abs(X/shift)*100,6)+"%"))
# also |X|/|shift| for R3 and R2 from ptable
pt=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ptable.json")))
for r in ("R2","R3"):
    s=mp.mpf(pt[r]["lam_pred"])-mp.mpf(pt["launch"])
    print("  %s: |X|/|shift| = %s%%"%(r,mp.nstr(abs(mp.mpf(pt[r]['cross'])/s)*100,6)))
json.dump({"g_a":mp.nstr(g_a,25),"g_b":mp.nstr(g_b4,25),"launch":mp.nstr(l0,20),
           "f_a":mp.nstr(fa,16),"f_b":mp.nstr(fb,16),"self_a":mp.nstr(sa,14),"self_b":mp.nstr(sb,14),
           "cross":mp.nstr(X,16),"lam_pred":mp.nstr(l0+shift,16),"shift":mp.nstr(shift,14)},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "r4.json"), "w"),indent=1)
