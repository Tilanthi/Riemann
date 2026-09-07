from mpmath import mp, mpmathify as M, mpf, nstr, findroot
mp.dps=40
N=[100,140,180,220]
L=[M("3.720899741667123935791434766094540694091e-59"),
   M("3.191618722904299187775878951533394940265e-59"),
   M("2.959706807240060045108126519806894301792e-59"),
   M("2.833656431009356898926062340578180078197e-59")]
print("=== SENSITIVITY of lam_inf / cumulative factor to the SHAPE parameter p ===")
print("   family lam(N)=lam_inf + C N^-p, lam_inf and C fixed by the LAST TWO points (180,220)")
print("   p        lam_inf(e-59)   cumulative factor L(100)/lam_inf")
for p in ["1.0","1.2","1.4","1.6","1.69","1.79","2.0","2.5","3.0","4.0"]:
    pp=mpf(p); fa,fb=mpf(180)**-pp, mpf(220)**-pp
    C=(L[2]-L[3])/(fa-fb); li=L[2]-C*fa
    print("   %-8s %-15s %s"%(p, nstr(li*mpf('1e59'),8), nstr(L[0]/li,7)))
print()
print("   p is pinned only to ~[1.69,1.79] by the two measured difference-ratios, and those two")
print("   ratios are MUTUALLY INCONSISTENT inside the family (2.31% apart against ~1e-30 data),")
print("   so p is not pinned by a fit at all -- it is a range over an unmodelled residual.")
print()
print("=== registration arithmetic for d4/d3 ===")
def rr(p,a,b,c):
    return (mpf(b)**-p-mpf(c)**-p)/(mpf(a)**-p-mpf(b)**-p)
for p in ["1.5878","1.6900","1.7921"]:
    print("   frozen p=%s -> d4/d3 = %s"%(p, nstr(rr(mpf(p),180,220,260),8)))
