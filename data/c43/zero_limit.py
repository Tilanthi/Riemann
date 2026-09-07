from mpmath import mp, mpmathify as M, mpf, log, exp, findroot, nstr
mp.dps=50
N=[mpf(100),mpf(140),mpf(180),mpf(220)]
L=[M("3.720899741667123935791434766094540694091e-59"),
   M("3.191618722904299187775878951533394940265e-59"),
   M("2.959706807240060045108126519806894301792e-59"),
   M("2.833656431009356898926062340578180078197e-59")]
lr=[log(L[i+1]/L[i]) for i in range(3)]
d=[L[i]-L[i+1] for i in range(3)]; r=[d[1]/d[0],d[2]/d[1]]
print("log-ratios:", [nstr(x,10) for x in lr], " lr2/lr1=",nstr(lr[1]/lr[0],10)," lr3/lr2=",nstr(lr[2]/lr[1],10))
print()
print("=== A. IS lam_inf = 0 ADMISSIBLE?  (decay-to-zero families, fit 2 shape params to lr1,lr2) ===")
tgt=lr[1]/lr[0]
F=lambda q: (N[2]**q-N[1]**q)/(N[1]**q-N[0]**q)-tgt
print("  family lam=C exp(-c N^q), c>0,q>0 is a genuine decay to 0.")
print("  F(q)=0 needed. F on q>0:", [(q, nstr(F(mpf(q)),6)) for q in ["0.001","0.25","0.5","1","2","4"]])
print("  F(q) > 0 for EVERY q>0 tested and increasing => NO ROOT with q>0.")
print("  the only root is at q<0 (F(-2)=%s, F(-1)=%s), and q<0 gives N^q->0 i.e. lam->C>0."%(nstr(F(mpf(-2)),4),nstr(F(mpf(-1)),4)))
print("  family lam=C N^-p (pure power decay to 0): p from each consecutive pair =",
      [nstr(-lr[i]/log(N[i+1]/N[i]),6) for i in range(3)], "-> not constant, REFUTED")
print("  => within the families tested, lam_inf > 0.  The SEQUENCE HAS A POSITIVE LIMIT is the part")
print("     these four points DO determine; the VALUE is the part they do not.")
print()
print("=== B. MODEL-FREE INTERVAL (assumes only lam_min(N) non-increasing: Cauchy interlacing, nested basis) ===")
print("  0 < lam_inf <= lam(220)=%s  =>  cumulative factor >= %s , no upper bound from the data alone"
      %(nstr(L[3],12), nstr(L[0]/L[3],12)))
print("  P2's registered band [1.15,1.6]: its LOWER half [1.15,1.313) is EXCLUDED model-free.")
print()
print("=== C. LOCAL EFFECTIVE EXPONENT p_eff and its DRIFT (what N=260 actually measures) ===")
def rr(p,a,b,c):
    return (mpf(b)**-p-mpf(c)**-p)/(mpf(a)**-p-mpf(b)**-p)
p1=findroot(lambda p: rr(p,100,140,180)-r[0], mpf("1.8"))
p2=findroot(lambda p: rr(p,140,180,220)-r[1], mpf("1.7"))
print("  p_eff(100,140,180) = %s ;  p_eff(140,180,220) = %s ;  drift = %s per 40-step"
      %(nstr(p1,10),nstr(p2,10),nstr(p2-p1,6)))
p3lin=p2+(p2-p1)
print("  linear drift extrapolation -> p_eff(180,220,260) = %s"%nstr(p3lin,10))
print()
print("  PREDICTED d4/d3 = (lam220-lam260)/(lam180-lam220) under each hypothesis:")
for nm,val in [("geometric refit on last triple (r3=r2)", r[1]),
               ("pure 1/N", (mpf(1)/220-mpf(1)/260)/(mpf(1)/180-mpf(1)/220)),
               ("frozen power law p=%s (m1's registered centre)"%nstr(p1,6), rr(p1,180,220,260)),
               ("frozen power law p=%s (from r2)"%nstr(p2,6), rr(p2,180,220,260)),
               ("DRIFTING p_eff, linear, p=%s  <-- BEAST c43 registration"%nstr(p3lin,6), rr(p3lin,180,220,260))]:
    print("     %-58s %s"%(nm, nstr(val,8)))
print()
print("  m1's registered band was [0.57,0.61] centred 0.598 on the FROZEN p=1.792 family.")
