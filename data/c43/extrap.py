from mpmath import mp, mpmathify as M, mpf, log, findroot
mp.dps=60
N=[100,140,180,220]
L=[M("3.720899741667123935791434766094540694091e-59"),
   M("3.191618722904299187775878951533394940265e-59"),
   M("2.959706807240060045108126519806894301792e-59"),
   M("2.833656431009356898926062340578180078197e-59")]
d=[L[i]-L[i+1] for i in range(3)]
r=[d[1]/d[0], d[2]/d[1]]
print("successive lambda ratios:", [mp.nstr(L[i+1]/L[i],10) for i in range(3)])
print("successive DIFFERENCE ratios r1,r2:", mp.nstr(r[0],10), mp.nstr(r[1],10))
print("  (m3 quoted 0.438, 0.544; m1 quoted 0.4382, 0.5435)")
print()
print("=== the data are EXACT: quote the noise level ===")
# m3 states dps150 vs dps220 ratio = 1.0 to displayed precision -> numerical noise <<1e-30
print("m3's own dps control: ratio 1.0 at dps150 vs 220 => noise on each lambda < ~1e-30 relative")
print("=> a model miss of 1e-3 relative is ~1e27 times the noise. Nothing here is a 'fit within error'.")
print()
def report(name, pred_r2_from_r1, lam_inf):
    pass
print("=== FAMILY TESTS: 3-parameter families, shape param fixed by r1, r2 PREDICTED (1 dof) ===")
# A) geometric lam_inf + C rho^N : r2 = r1 exactly
print("A geometric (lam_inf + C*rho^N):   predicts r2 = r1 = %s ; measured %s ; miss %+.2f%%"
      % (mp.nstr(r[0],6), mp.nstr(r[1],6), float((r[0]-r[1])/r[1]*100)))
# B) pure 1/N  (2-param: predicts BOTH ratios, 0 dof used)
b1=(mpf(1)/140-mpf(1)/180)/(mpf(1)/100-mpf(1)/140); b2=(mpf(1)/180-mpf(1)/220)/(mpf(1)/140-mpf(1)/180)
print("B algebraic 1/N (lam_inf + C/N):   predicts r1=%s r2=%s ; measured %s %s ; miss %+.2f%% %+.2f%%"
      % (mp.nstr(b1,6),mp.nstr(b2,6),mp.nstr(r[0],6),mp.nstr(r[1],6),
         float((b1-r[0])/r[0]*100), float((b2-r[1])/r[1]*100)))
# C) power law lam_inf + C N^-p : p from r1, predict r2
def rr(p,a,b,c,e):
    return ((mp.mpf(b)**-p - mp.mpf(c)**-p)/(mp.mpf(a)**-p - mp.mpf(b)**-p))
p=findroot(lambda p: rr(p,100,140,180,0)-r[0], mpf("1.8"))
r2p=rr(p,140,180,220,0)
print("C power law (lam_inf + C*N^-p):    p fit to r1 = %s ; predicts r2=%s ; measured %s ; miss %+.2f%%"
      % (mp.nstr(p,10), mp.nstr(r2p,6), mp.nstr(r[1],6), float((r2p-r[1])/r[1]*100)))
print("   (m1 quoted p=1.792, 'reproduces the second to 2.3%')")
# D) stretched exponential lam_inf + C exp(-c N^q): shape params c,q -> 2 shape params, 0 dof from 2 ratios
#    ratio r = (exp(-c b^q)-exp(-c c^q))/(exp(-c a^q)-exp(-c b^q)); solve c,q from r1,r2 -> then NO prediction left
def rE(c,q,a,b,cc):
    f=lambda n: mp.e**(-c*mp.mpf(n)**q)
    return (f(b)-f(cc))/(f(a)-f(b))
try:
    sol=findroot(lambda c,q: (rE(c,q,100,140,180)-r[0], rE(c,q,140,180,220)-r[1]), (mpf("0.05"), mpf("0.9")))
    print("D stretched exp (lam_inf+C e^{-c N^q}): EXACT fit c=%s q=%s -> ZERO dof, no prediction made"%(mp.nstr(sol[0],8),mp.nstr(sol[1],8)))
    cE,qE=sol[0],sol[1]
except Exception as ex:
    cE=qE=None; print("D stretched exp: no root found:", ex)
print()
print("=== IMPLIED lam_inf AND CUMULATIVE SHRINK FACTOR under each family ===")
def linf_from(fun, idx):
    # lam(N) = linf + C*f(N); solve linf from two points given shape
    a,b=idx
    fa,fb=fun(N[a]),fun(N[b])
    C=(L[a]-L[b])/(fa-fb); return L[a]-C*fa
rows=[]
# geometric via Aitken on each triple
for (i,j,k) in [(0,1,2),(1,2,3)]:
    rho40=(L[j]-L[k])/(L[i]-L[j]); linf=L[i]-(L[i]-L[j])**2/((L[i]-L[j])-(L[j]-L[k]))
    rows.append(("A geometric Aitken (%d,%d,%d)"%(N[i],N[j],N[k]), linf))
# 1/N Richardson pairs
for (a,b) in [(0,1),(1,2),(2,3),(0,3)]:
    rows.append(("B 1/N Richardson (%d,%d)"%(N[a],N[b]), linf_from(lambda n: mpf(1)/n,(a,b))))
# power law p from r1 and p from r2 and p from all-4 lsq-ish
p_r1=p
p_r2=findroot(lambda pp: rr(pp,140,180,220,0)-r[1], mpf("1.8"))
for nm,pp in [("p=%s (from r1)"%mp.nstr(p_r1,6),p_r1), ("p=%s (from r2)"%mp.nstr(p_r2,6),p_r2)]:
    rows.append(("C power law %s"%nm, linf_from(lambda n: mp.mpf(n)**-pp,(2,3))))
if cE is not None:
    rows.append(("D stretched exp exact-fit (0 dof)", linf_from(lambda n: mp.e**(-cE*mp.mpf(n)**qE),(2,3))))
for nm,li in rows:
    print("  %-38s lam_inf=%s   cumulative factor L100/lam_inf = %s"
          % (nm, mp.nstr(li,8), mp.nstr(L[0]/li,6)))
print()
print("=== Is lam_inf = 0 (pure decay) refuted? ===")
pd=[log(L[i+1]/L[i])/log(mpf(N[i+1])/N[i]) for i in range(3)]
print("  pure power decay exponents from consecutive pairs:", [mp.nstr(x,6) for x in pd])
print("  not constant (%.3f -> %.3f -> %.3f) => lam ~ C N^-p with lam_inf=0 is REFUTED"%(float(pd[0]),float(pd[1]),float(pd[2])))
