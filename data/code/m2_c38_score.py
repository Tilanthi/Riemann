"""c38 SCORING of the pre-registered bands (a101489), and the two-channel decomposition."""
import json, re, mpmath as mp
mp.mp.dps = 200
R="/shared/rh-exchange-repo/Riemann/"
c36=open(R+"machine2-c36-the-two-unanchored-checks-are-real-and-neither-touches-the-evaluator.md").read()
D175=mp.mpf(max(re.findall(r"0\.14173323966388719139541568508418502362314456[0-9]*",c36),key=len))
FP=mp.mpf(re.search(r"f'\(D\*\) = (-37\.4819713608[0-9]*)",open("/workspace/rh/cycle37/c37_fprime.out").read()).group(1))
c34=json.load(open('/workspace/rh/cycle34/c34_refit.json')); c38=json.load(open('c38_runs.json'))
G={e['label']:e for e in c38}; H={e['label']:e for e in c34}
C80=mp.mpf(c34[0]['cfg']['centre']); delta=C80-D175
eps={k:mp.mpf(G[k]['eps']) for k in G}
print("delta = C80 - D175 =", mp.nstr(delta,12), "   f'*delta =", mp.nstr(FP*delta,14))
for k in ["R1","R2","R3","R4"]:
    c=G[k]['cfg']; print("  %-3s r_w=%-6s N_w=%-3d dps=%-4d centre=%-3d-digit  eps=%s"
        %(k,c['r_w'],c['N_w'],c['dps'],len(c['centre'])-2,mp.nstr(eps[k],20)))

print("\n### P1 (PRIMARY, prefactor-free ratio; band [12241, 12489])")
ratio=eps["R3"]/eps["R2"]
print("   eps(R3)/eps(R2) =", mp.nstr(ratio,12), " -> ", "CONFIRMED" if 12241<=ratio<=12489 else "FALSIFIED")

print("\n### P2 (eps at N_w=40, r_w=0.045, 80-digit centre = 3.28229455657e-80, rel <= 1e-6)")
pred2=FP*delta-4*(2*mp.mpf("0.045"))**80
rel=abs(eps["R1"]-pred2)/abs(pred2)
print("   predicted %s   measured %s   rel dev %s -> %s"%(mp.nstr(pred2,12),mp.nstr(eps["R1"],12),
      mp.nstr(rel,6),"CONFIRMED" if rel<=mp.mpf("1e-6") else "FALSIFIED"))

print("\n### THE ONE-KNOB DIFFERENCE R1-R3 (identical knobs, centre the ONLY change)")
d13=eps["R1"]-eps["R3"]
print("   eps(R1)-eps(R3) =", mp.nstr(d13,20))
print("   f'(D*)*delta    =", mp.nstr(FP*delta,20))
print("   ratio           =", mp.nstr(d13/(FP*delta),12), "  [c37 predicted 3.2831684545749610703e-80]")

print("\n### TWO-CHANNEL DECOMPOSITION at N_w=40 from the R2/R3 pair (exactly determined, 0 dof)")
r2=(2*mp.mpf("0.04"))**80; r3=(2*mp.mpf("0.045"))**80
A=(eps["R3"]-eps["R2"])/(r3-r2); T90=eps["R2"]-A*r2
print("   eps = T(dps) + A*(2 r_w)^80")
print("   A            =", mp.nstr(A,12), "   [pure pole-pair model predicts exactly -4; dev %s %%]"%mp.nstr(100*(A+4)/-4,4))
print("   T(dps=90)    =", mp.nstr(T90,12))
print("   T(dps=125)   =", mp.nstr(eps['R4'],12), "  [= eps(R4); its own alias term is 4(0.09)^144 = %s]"%mp.nstr(4*(2*mp.mpf('0.045'))**144,4))
print("   => the r-independent part is NOT dps-independent: it moves by %s between dps 90 and 125"%mp.nstr(T90/eps['R4'],6))
print("   => at dps 125 it BOUNDS the centre error: |delta_175| <= |eps(R4)/f'| =", mp.nstr(abs(eps['R4']/FP),6))
print("      i.e. our published 175-digit D* is certified to ~%d digits, not 175."%(int(-mp.log10(abs(eps['R4']/FP)))))

print("\n### P3(a) (band |eps(R4)| < 1e-129)")
print("   |eps(R4)| =", mp.nstr(abs(eps["R4"]),12), "->",
      "CONFIRMED" if abs(eps["R4"])<mp.mpf("1e-129") else "FALSIFIED (still a %.1f-order removal of the 3.28e-80 print floor)"%float(mp.log10(mp.mpf('3.2831684546e-80')/abs(eps['R4']))))

print("\n### P3(b) NO PUBLISHED CONSTANT MOVES  (c34 published cfg DP19 RECENTRED at 45 s.f.)")
pub={"a":"2.64552141181166286801612612120342539738354204",
     "b":"-7.46245287679368626753358035162874151331895732",
     "a3":"11.700717320433667601156432487039813849333726",
     "a4":"-20.4755387553904125007058067225760662898269858",
     "a5":"18.2711625011499510374264312726700306984558616"}
allok=True
for nm in ["a","b","a3","a4","a5"]:
    new=mp.mpf(G["R4"]['rec'][nm]); old=mp.mpf(H["DP19"]['rec'][nm])
    sf=len(pub[nm].replace('-','').replace('.',''))
    re_new=mp.nstr(new,sf,strip_zeros=False)
    ok=(mp.mpf(re_new)==mp.mpf(pub[nm]))
    allok&=ok
    print("   %-3s published %-47s  re-run@%d-digit-centre -> %-47s %s   |new-old(c34 rec)| = %s"
          %(nm,pub[nm],175,re_new,"MATCH" if ok else "MOVED",mp.nstr(abs(new-old),6)))
print("   P3(b):", "CONFIRMED - no published digit moves, no erratum owed on this arm" if allok else "FALSIFIED - ERRATUM OWED")

print("\n### P3(c) RAW shifts = S_k*(C175-C80), predicted vs measured, band 1%")
for nm in ["a","b","a3","a4","a5"]:
    S=mp.mpf(H["DP19"]['sens'][nm]); pred=S*(-delta)
    meas=mp.mpf(G["R4"]['raw'][nm])-mp.mpf(H["DP19"]['raw'][nm])
    print("   %-3s predicted %-16s measured %-16s ratio %s -> %s"%(nm,mp.nstr(pred,8),mp.nstr(meas,8),
          mp.nstr(meas/pred,8),"in band" if abs(meas/pred-1)<mp.mpf("0.01") else "OUT of band"))
