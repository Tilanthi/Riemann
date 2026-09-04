"""machine2 cycle23 -- SCORED RUN of the named composition family (five rungs).

Pre-registration: machine2-cycle23-FAMILY-CHOICE-... (00b3277) sect 6 (C1,C3,C4)
                  machine2-cycle23-PREREG-2-... (a961240) sect 5 (C2', C5, C6, C2-original)
both pushed before this script ran and before any exact composed lam_min existed.

Scored object per rung:
  S_Z = K_T200 - rem(gA1) - rem(gA2) - rem(gB1) - rem(gB2) + quad(delta_a, g_a) + quad(delta_b, g_b)
  value = lam_min(S_Z, G)  in the G-metric (generalized eigenproblem, Cholesky)

Graded quantities:
  s_A = lam(R0) - lam(launch) ;  s_B = lam(R1) - lam(launch)
  D   = lam(R2) - [ lam(launch) + s_A + s_B ]          (additivity defect; predicted = X)
  R_c = |D| / (|f_a| + |f_b|)                          (cancellation-robust, PREREG-2 sect 4)
R3 and R4 use their own single-leg references (R0 for leg A at delta_a=0.1 is shared by
R2/R3/R4; leg B references at delta_b = 0.2 and 0.1 are computed here as R1b, R1c).
"""
import json, os, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N
mp.dps = 40
half = mp.mpf(1)/2
HERE = os.path.dirname(os.path.abspath(__file__))
gens=load_genomes("s1/M8"); tgt=load_target("s1/M8")
gam=[mp.mpf(g) for g in json.load(open(os.path.join(HERE,"zeros210.json")))]
up200=[g for g in gam if g<=200]
t0=time.time()
bases=[Basis(g,degree=8) for g in gens]
G=gram(); K200=mat(tgt["K_T200"])
def quad(d,g0):
    p=mp.mpc(half+d,g0); q=mp.mpc(half-d,g0)
    up=[b.u(p) for b in bases]; uq=[b.u(q) for b in bases]; M=mp.matrix(N,N)
    for i in range(N):
        for j in range(N): M[i,j]=2*mp.re(up[i]*mp.conj(uq[j])+up[j]*mp.conj(uq[i]))
    return M
GA1,GA2,GB1,GB2=up200[0],up200[1],up200[2],up200[3]
REM = zero_pair_K(mp.mpc(half,GA1))+zero_pair_K(mp.mpc(half,GA2))\
     +zero_pair_K(mp.mpc(half,GB1))+zero_pair_K(mp.mpc(half,GB2))
g_a  = GA1+(GA2-GA1)*5/mp.mpf(8)
g_b  = GB1+(GB2-GB1)*2/mp.mpf(8)
g_b4 = GB1+(GB2-GB1)*1/mp.mpf(8)
DA=mp.mpf("0.1"); DB=mp.mpf("0.07208635197257083638787626")
def L(da,gb,db):
    return K200 - REM + quad(da,g_a) + quad(db,gb)
CFG = {
 "launch": (mp.mpf(0), g_b,  mp.mpf(0)),
 "R0":     (DA,        g_b,  mp.mpf(0)),
 "R1":     (mp.mpf(0), g_b,  DB),
 "R2":     (DA,        g_b,  DB),
 "R1b":    (mp.mpf(0), g_b,  mp.mpf("0.2")),
 "R3":     (DA,        g_b,  mp.mpf("0.2")),
 "launch4":(mp.mpf(0), g_b4, mp.mpf(0)),
 "R0d":    (DA,        g_b4, mp.mpf(0)),
 "R1c":    (mp.mpf(0), g_b4, mp.mpf("0.1")),
 "R4":     (DA,        g_b4, mp.mpf("0.1")),
}
res={}
for k,(da,gb,db) in CFG.items():
    v=lam(L(da,gb,db),G)[0]
    res[k]=mp.nstr(v,20)
    print("%8s  delta_a=%-8s gamma_b=%s delta_b=%-28s lam_min=%s"%(
        k,mp.nstr(da,4),mp.nstr(gb,12),mp.nstr(db,20),mp.nstr(v,16)),flush=True)
def f(x): return mp.mpf(res[x])
l0=f("launch"); l04=f("launch4")
sA = f("R0")-l0; sB = f("R1")-l0; sBb = f("R1b")-l0
sA4 = f("R0d")-l04; sB4 = f("R1c")-l04
D2 = f("R2")-(l0+sA+sB); D3 = f("R3")-(l0+sA+sBb); D4 = f("R4")-(l04+sA4+sB4)
fa=mp.mpf("6.539269783062942e-8")   # from prereg (00b3277 sect4 / PREREG-2 sect3)
fb2=mp.mpf("-6.539269783062942e-8")
fb3=mp.mpf("-2.3892388783e-7")      # f_a+f_b at R3 = -1.7353119e-7 => f_b
fa4=mp.mpf("4.1025724034132e-7"); fb4=mp.mpf("9.437482143326e-8")
print("\nexact single-leg shifts: s_A=%s  s_B=%s  s_B(0.2)=%s  s_A4=%s s_B4=%s"%
      (mp.nstr(sA,12),mp.nstr(sB,12),mp.nstr(sBb,12),mp.nstr(sA4,12),mp.nstr(sB4,12)))
print("D(R2)=%s   D(R3)=%s   D(R4)=%s"%(mp.nstr(D2,12),mp.nstr(D3,12),mp.nstr(D4,12)))
Rc2=abs(D2)/(abs(fa)+abs(fb2)); Rc3=abs(D3)/(abs(fa)+abs(fb3)); Rc4=abs(D4)/(abs(fa4)+abs(fb4))
print("R_c: R2=%s%%  R3=%s%%  R4=%s%%"%(mp.nstr(Rc2*100,6),mp.nstr(Rc3*100,6),mp.nstr(Rc4*100,6)))
sh2=f("R2")-l0; sh3=f("R3")-l0; sh4=f("R4")-l04
print("|D|/|shift| (NOT graded): R2=%s%% R3=%s%% R4=%s%%"%
      (mp.nstr(abs(D2/sh2)*100,5),mp.nstr(abs(D3/sh3)*100,5),mp.nstr(abs(D4/sh4)*100,5)))
res.update({"s_A":mp.nstr(sA,16),"s_B":mp.nstr(sB,16),"s_Bb":mp.nstr(sBb,16),
            "s_A4":mp.nstr(sA4,16),"s_B4":mp.nstr(sB4,16),
            "D_R2":mp.nstr(D2,16),"D_R3":mp.nstr(D3,16),"D_R4":mp.nstr(D4,16),
            "Rc_R2":mp.nstr(Rc2,10),"Rc_R3":mp.nstr(Rc3,10),"Rc_R4":mp.nstr(Rc4,10),
            "shift_R2":mp.nstr(sh2,14),"shift_R3":mp.nstr(sh3,14),"shift_R4":mp.nstr(sh4,14)})
json.dump(res,open(os.path.join(HERE,"scored_cycle23.json"),"w"),indent=1)
print("\ndone %.1fs"%(time.time()-t0))
