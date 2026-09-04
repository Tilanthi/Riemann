"""machine2 cycle23 -- ON-LINE CONTROLS for the composed family.  Every fully on-line
count-matched configuration must give lam_min >= 0 (Weil positivity holds for on-line
zero sets by construction of K).  These carry no witness content and no scored value:
they are the arm that is supposed to PASS, and an instrument bug shows up here first."""
import json, os
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N
mp.dps=40
half=mp.mpf(1)/2
HERE=os.path.dirname(os.path.abspath(__file__))
gens=load_genomes("s1/M8"); tgt=load_target("s1/M8")
gam=[mp.mpf(g) for g in json.load(open(os.path.join(HERE,"zeros210.json")))]
up200=[g for g in gam if g<=200]
bases=[Basis(g,degree=8) for g in gens]
G=gram(); K200=mat(tgt["K_T200"])
GA1,GA2,GB1,GB2=up200[0],up200[1],up200[2],up200[3]
REM=zero_pair_K(mp.mpc(half,GA1))+zero_pair_K(mp.mpc(half,GA2))\
   +zero_pair_K(mp.mpc(half,GB1))+zero_pair_K(mp.mpc(half,GB2))
g_a=GA1+(GA2-GA1)*5/mp.mpf(8); g_b=GB1+(GB2-GB1)*2/mp.mpf(8)
BUDGET=mp.mpf("7.241e-11")
print("on-line control: replace each quadruple by an on-line PAIR-of-pairs at gamma +- eta")
print("%8s %22s %22s %8s"%("eta","lam_min","(budget 7.241e-11)","verdict"))
rows={}
for e in ["0","0.25","0.5","1","2","3.4438","5"]:
    et=mp.mpf(e)
    A=zero_pair_K(mp.mpc(half,g_a+et))+zero_pair_K(mp.mpc(half,g_a-et))
    B=zero_pair_K(mp.mpc(half,g_b+et))+zero_pair_K(mp.mpc(half,g_b-et))
    v=lam(K200-REM+A+B,G)[0]
    rows[e]=mp.nstr(v,16)
    print("%8s %22s %22s %8s"%(e,mp.nstr(v,14),"",("PASS" if v>=-BUDGET else "FAIL")))
# eta* restoration: eta chosen so the inserted on-line pairs sit exactly on the removed zeros
eA=(GA2-GA1)/2; eB=(GB2-GB1)/2
A=zero_pair_K(mp.mpc(half,g_a+eA))+zero_pair_K(mp.mpc(half,g_a-eA))
B=zero_pair_K(mp.mpc(half,g_b+eB))+zero_pair_K(mp.mpc(half,g_b-eB))
S=K200-REM+A+B
dk=max(abs(S[i,j]-K200[i,j]) for i in range(N) for j in range(N))
print("eta* restoration (eta_A=%s, eta_B=%s): |S - K_T200|_max = %s  %s"%
      (mp.nstr(eA,10),mp.nstr(eB,10),mp.nstr(dk,4),"PASS" if dk<mp.mpf("1e-30") else "FAIL"))
print("lam_min at eta* = %s  vs lam_min(K_T200,G) = %s"%
      (mp.nstr(lam(S,G)[0],16),mp.nstr(lam(K200,G)[0],16)))
rows["eta_star_dK"]=mp.nstr(dk,6)
json.dump(rows,open(os.path.join(HERE,"controls.json"),"w"),indent=1)
