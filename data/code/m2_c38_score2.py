import json, re, mpmath as mp
mp.mp.dps=200
R="/shared/rh-exchange-repo/Riemann/"
c36=open(R+"machine2-c36-the-two-unanchored-checks-are-real-and-neither-touches-the-evaluator.md").read()
D175=max(re.findall(r"0\.14173323966388719139541568508418502362314456[0-9]*",c36),key=len)
FP=mp.mpf(re.search(r"f'\(D\*\) = (-37\.4819713608[0-9]*)",open("/workspace/rh/cycle37/c37_fprime.out").read()).group(1))
G={e['label']:e for e in json.load(open('c38_runs.json'))}
eps={k:mp.mpf(G[k]['eps']) for k in G}
print("### P5 (band log10|eps(R6)| in [-156,-149])")
l=mp.log10(abs(eps['R6'])); print("   eps(R6) = %s   log10 = %s -> %s"%(mp.nstr(eps['R6'],12),mp.nstr(l,8),
      "CONFIRMED" if -156<=l<=-149 else "FALSIFIED"))
print("   => the dps-125 residual was the EVALUATOR FLOOR, not the centre: raising dps alone moved it")
print("      from %s to %s, a factor %s"%(mp.nstr(eps['R4'],6),mp.nstr(eps['R6'],6),mp.nstr(eps['R4']/eps['R6'],6)))
b=abs(eps['R6']/FP)
print("\n### ERRATUM-19 NUMBER: certified accuracy of our PUBLISHED 175-digit D*")
print("   |delta_175| <= |eps(R6)/f'(D*)| = %s   => D* is supported to %d significant figures"%(mp.nstr(b,8),int(-mp.log10(b))))
print("   published width: %d s.f.  =>  %d UNSUPPORTED digits"%(len(D175)-2,(len(D175)-2)-int(-mp.log10(b))))
print("   c36's stated error bar 7.18811e-133 is a REFINEMENT DELTA (dps 130 vs 150), not a floor.")
print("\n### P6 (band [+2.62e-90, +3.20e-90], POSITIVE)")
e7=eps['R7']; lo,hi=mp.mpf("2.62e-90"),mp.mpf("3.20e-90")
print("   eps(R7) = %s  -> sign %s (predicted POSITIVE: %s); magnitude %s"%
      (mp.nstr(e7,12),"+" if e7>0 else "-","CONFIRMED" if e7>0 else "FALSIFIED",
       "in band CONFIRMED" if lo<=e7<=hi else "OUT of band by %s %% -> FALSIFIED as filed"%mp.nstr(100*(e7-hi)/hi,4)))
x=mp.mpf("5.059151051e-32"); y=mp.mpf("-4.000026001"); r=mp.mpf("0.035")
print("   model split: x-term %s, y-term %s ; measured minus y-term = %s => x extrapolates %s x low"
      %(mp.nstr(x*r**40,6),mp.nstr(y*(2*r)**80,6),mp.nstr(e7-y*(2*r)**80,6),mp.nstr((e7-y*(2*r)**80)/(x*r**40),6)))
print("\n### the three dps-90 points at N_w=40, x-term isolated (y = -4 exactly)")
for rw,lab in [("0.035","R7"),("0.04","R2"),("0.045","R3")]:
    rr=mp.mpf(rw); xt=eps[lab]+4*(2*rr)**80
    print("   r_w=%-6s eps=%-16s  x-term = eps + 4(2r)^80 = %-14s  x-term/r^40 = %s"%(rw,mp.nstr(eps[lab],8),mp.nstr(xt,8),mp.nstr(xt/rr**40,8)))
print("   => x is NOT constant across r_w (5.06e-32 vs 6.03e-32): a THIRD term exists at N_w=40 and")
print("      three points cannot resolve three terms. UNMEASURED, client: a 4th r_w at fixed N_w.")
