"""machine2 cycle23 -- COMPLETE second-order perturbation-theory prediction table for the
four rungs of the named family.  Design data: uses only the composed LAUNCH (both legs at
delta=0, PSD, on-line) and the single-leg perturbations.  No exact composed lam_min at
nonzero delta is evaluated here."""
import json, os
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N
mp.dps = 40
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
g_a=GA1+(GA2-GA1)*5/mp.mpf(8); g_b=GB1+(GB2-GB1)*2/mp.mpf(8)
qA0,qB0=quad(mp.mpf(0),g_a),quad(mp.mpf(0),g_b)
L=K200-zero_pair_K(mp.mpc(half,GA1))-zero_pair_K(mp.mpc(half,GA2))\
    -zero_pair_K(mp.mpc(half,GB1))-zero_pair_K(mp.mpc(half,GB2))+qA0+qB0
vals,vecs=eig_full(L,G); v0=vecs[0]; l0=vals[0]
DA=mp.mpf("0.1"); DB=mp.mpf("0.07208635197257083638787626")
RUNGS={"R0":(DA,mp.mpf(0)),"R1":(mp.mpf(0),DB),"R2":(DA,DB),"R3":(DA,mp.mpf("0.2"))}
print("composed launch lam0 = %s"%mp.nstr(l0,18))
print("%4s %10s %10s %14s %14s %14s %14s"%("rung","d_a","d_b","first order","2nd self","2nd CROSS","lam_pred"))
out={}
for r,(da,db) in RUNGS.items():
    Pa=quad(da,g_a)-qA0 if da!=0 else mp.matrix(N,N)
    Pb=quad(db,g_b)-qB0 if db!=0 else mp.matrix(N,N)
    fa=bil(Pa,v0,v0); fb=bil(Pb,v0,v0)
    sa=sb=X=mp.mpf(0)
    for k in range(1,N):
        A=bil(Pa,v0,vecs[k]); B_=bil(Pb,v0,vecs[k]); den=vals[0]-vals[k]
        sa+=A*A/den; sb+=B_*B_/den; X+=2*A*B_/den
    pred=l0+fa+fb+sa+sb+X
    out[r]={"d_a":mp.nstr(da,20),"d_b":mp.nstr(db,26),"f_a":mp.nstr(fa,16),"f_b":mp.nstr(fb,16),
            "self_a":mp.nstr(sa,14),"self_b":mp.nstr(sb,14),"cross":mp.nstr(X,16),
            "lam_pred":mp.nstr(pred,16)}
    print("%4s %10s %10s %14s %14s %14s %14s"%(r,mp.nstr(da,4),mp.nstr(db,4),mp.nstr(fa+fb,8),
          mp.nstr(sa+sb,8),mp.nstr(X,8),mp.nstr(pred,10)))
# naive-additivity prediction of R2 and R3 from the PT R0/R1 values
for r,base in (("R2","R1"),("R3",None)):
    pass
sA=mp.mpf(out["R0"]["lam_pred"])-l0
sB=mp.mpf(out["R1"]["lam_pred"])-l0
print("\nPT single-leg shifts: s_A=%s  s_B=%s"%(mp.nstr(sA,10),mp.nstr(sB,10)))
print("naive additivity for R2: %s ; PT with cross: %s ; D_pred = %s"%
      (mp.nstr(l0+sA+sB,12), out["R2"]["lam_pred"], out["R2"]["cross"]))
print("R2 total shift (pred) = %s"%mp.nstr(mp.mpf(out["R2"]["lam_pred"])-l0,10))
out["launch"]=mp.nstr(l0,20); out["sA_pt"]=mp.nstr(sA,14); out["sB_pt"]=mp.nstr(sB,14)
json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ptable.json"), "w"),indent=1)
