"""m2 c30 POST-HOC part 2 -- sign discipline, and DISCRIMINATION between the candidate causes.

r_used(eps) = r_true(eps) + (a_true - a_used)/eps^2        [an error in a]
r_used(eps) = r_true(eps) - a*eta/eps^3 + O(eta/eps^2)     [an error in Delta*, eta = Dstar_true - Dstar_used]
r_used(eps) = r_true(eps) - (b_true - b_used)/eps          [an error in b]
So the POWER of the leading unmodelled term names the guilty input.  Fit each and compare.
"""
import json
from mpmath import mp
mp.dps = 60
A = mp.mpf("2.645521411811664489"); B = -mp.mpf("7.4624528767937415788")
A_OLD16 = mp.mpf("2.645521411811663"); A_M1 = mp.mpf("2.645521411811663079")
L165=[("0.001","0.05150723818940063653522997138655916611777128352831"),
 ("0.0011239031932557","0.054614584740162860829271236079197856379810987308508"),
 ("0.002","0.072945092837465636911527414020464645263120485246671"),
 ("0.0035","0.09670183421043065840984313002276196906002275045949"),
 ("0.006","0.12706034318675893153656817913317280690430806327895"),
 ("0.0082667603361","0.14962144595780802891341103521644637411107076093496"),
 ("0.012","0.18122223459720552038513232631511513662541625076064"),
 ("0.02","0.23662703502895471893639804350283991882970959834519"),
 ("0.035","0.31979403084190422618229559433082050463362878645843"),
 ("0.06","0.43405746526370626569197604987746105430711695666647"),
 ("0.1","0.59427921830513711248148784269207030531776649353816")]
NEW=["0.0001","0.00015","0.00022","0.00033","0.0005","0.00075"]
d=json.load(open("m2_c30_scored.json"))
E=[mp.mpf(e) for e,_ in L165]+[mp.mpf(e) for e in NEW]
U=[mp.mpf(u) for _,u in L165]+[mp.mpf(d["rungs"][e]["u"]) for e in NEW]
def r_of(e,u,a=A,b=B): return (u**2-a*e+b*e**2)/e**3
def fit(xs,ys,fn):
    n=len(fn); M=mp.matrix(n,n); v=mp.matrix(n,1)
    for i in range(n):
        for j in range(n): M[i,j]=mp.fsum([fn[i](x)*fn[j](x) for x in xs])
        v[i]=mp.fsum([y*fn[i](x) for x,y in zip(xs,ys)])
    c=mp.lu_solve(M,v); return [c[i] for i in range(n)]
def ev(c,fn,x): return mp.fsum([ci*f(x) for ci,f in zip(c,fn)])
def poly(K): return [(lambda x,i=i: x**i) for i in range(K+1)]
def mr(xs,ys,fn):
    c=fit(xs,ys,fn); return max(abs(ev(c,fn,x)-y) for x,y in zip(xs,ys)), c
R=[r_of(e,u) for e,u in zip(E,U)]

print("=== A. WHICH POWER?  17-rung max residual, one extra basis function, K=6 ===")
cands={"none":[],"eps^-1 (b)":[lambda x:1/x],"eps^-2 (a)":[lambda x:1/x**2],
       "eps^-3 (Delta*)":[lambda x:1/x**3],"eps^-3/2":[lambda x:x**mp.mpf(-1.5)],
       "eps^-2 and eps^-3":[lambda x:1/x**2, lambda x:1/x**3]}
for name,extra in cands.items():
    m,c=mr(E,R,extra+poly(6))
    print("  %-20s max res = %-16s  coeffs %s" % (name, mp.nstr(m,8),
          " ".join(mp.nstr(c[i],8) for i in range(len(extra)))))

print("\n=== B. sign-checked delta_a from the eps^-2 fit ===")
m,c = mr(E,R,[lambda x:1/x**2]+poly(6))
c0=c[0]
print("  fitted coefficient of eps^-2 :  c0 = %s" % mp.nstr(c0,10))
print("  identity: r_used = r_true + (a_true - a_used)/eps^2  =>  a_true = a_used + c0")
a_true = A + c0
print("  a_used (operative, #120-corrected) = %s" % mp.nstr(A,22))
print("  a_true (ladder measurement)        = %s" % mp.nstr(a_true,22))
print("  a_true - retired 16 s.f. value     = %s" % mp.nstr(a_true-A_OLD16,8))
print("  a_true - m1 eps->0 ladder a(0)     = %s" % mp.nstr(a_true-A_M1,8))
print("  a_used - retired 16 s.f. value     = %s   (the #120 move)" % mp.nstr(A-A_OLD16,8))

print("\n=== C. DECISIVE TEST: recompute r with a_true and refit with a PLAIN polynomial ===")
def loo(xs,ys,fn):
    o=sorted(range(len(xs)),key=lambda i:xs[i]); errs=[]
    for i in o[1:-1]:
        xr=[xs[j] for j in range(len(xs)) if j!=i]; yr=[ys[j] for j in range(len(ys)) if j!=i]
        cc=fit(xr,yr,fn); errs.append(ev(cc,fn,xs[i])-ys[i])
    return mp.sqrt(mp.fsum([e**2 for e in errs])/len(errs))
for label,aa in [("a_used (operative)",A),("a_true (ladder)",a_true),("retired 16 s.f.",A_OLD16)]:
    RR=[r_of(e,u,a=aa) for e,u in zip(E,U)]
    print("  --- a = %s (%s)" % (mp.nstr(aa,22),label))
    best=None
    for K in range(3,9):
        fn=poly(K); m2,cc=mr(E,RR,fn); lo=loo(E,RR,fn)
        if best is None or lo<best[0]: best=(lo,K,cc[0],m2)
        print("      K=%-2d max res %-15s LOO %-15s a3 %s" % (K,mp.nstr(m2,8),mp.nstr(lo,8),mp.nstr(cc[0],22)))
    print("      LOO-optimal K=%d  a3=%s  max res %s" % (best[1],mp.nstr(best[2],22),mp.nstr(best[3],8)))
    sp=[fit(E,RR,poly(K))[0] for K in (6,7,8)]
    print("      a3 spread K6..8 = %s" % mp.nstr(max(sp)-min(sp),8))

print("\n=== D. one-parameter scan: delta_a minimising the 17-rung K=6 max residual ===")
def f(da):
    RR=[r_of(e,u,a=A+da) for e,u in zip(E,U)]
    return mr(E,RR,poly(6))[0]
lo,hi=mp.mpf("-4e-15"),mp.mpf("1e-15")
for _ in range(200):
    m1_,m2_=lo+(hi-lo)/3,hi-(hi-lo)/3
    if f(m1_)<f(m2_): hi=m2_
    else: lo=m1_
da_opt=(lo+hi)/2
print("  delta_a* = %s   -> a = %s   max res %s" % (mp.nstr(da_opt,10), mp.nstr(A+da_opt,22), mp.nstr(f(da_opt),8)))
print("  (eps^-2 joint-fit value c0 = %s)" % mp.nstr(c0,10))
