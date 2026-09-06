# NOTE (committed deliberately): SECTIONS 2 AND 4 OF THIS FILE CARRY A SIGN ERROR (a_true = a_used - c0).
# Superseded by m2_c30_posthoc2.py, which writes the identity out and gets the sign right.
# Kept in the record because the wrong sign was caught by its own decisive test making things worse.
"""m2 c30 POST-HOC (labelled; NOT graded, NOT pre-registered).

The five falsifications share one signature.  This file measures it.
Model probe:   r(eps) = -da/eps^2 + (-db)/eps + a3 + a4 eps + ...
(dr/da = -1/eps^2, dr/db = +1/eps, exactly as the frozen input budget states)
"""
import json
from mpmath import mp
mp.dps = 60

A = mp.mpf("2.645521411811664489")
B = -mp.mpf("7.4624528767937415788")
A_OLD16 = mp.mpf("2.645521411811663")
A_M1LADDER = mp.mpf("2.645521411811663079")

L165 = [("0.001","0.05150723818940063653522997138655916611777128352831"),
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

d = json.load(open("m2_c30_scored.json"))
NEW = ["0.0001","0.00015","0.00022","0.00033","0.0005","0.00075"]

def r_of(e,u,a=A,b=B): return (u**2 - a*e + b*e**2)/e**3

E = [mp.mpf(e) for e,_ in L165] + [mp.mpf(e) for e in NEW]
U = [mp.mpf(u) for _,u in L165] + [mp.mpf(d["rungs"][e]["u"]) for e in NEW]
R = [r_of(e,u) for e,u in zip(E,U)]

def fit(xs, ys, funcs):
    n=len(funcs); M=mp.matrix(n,n); v=mp.matrix(n,1)
    for i in range(n):
        for j in range(n): M[i,j]=mp.fsum([funcs[i](x)*funcs[j](x) for x in xs])
        v[i]=mp.fsum([y*funcs[i](x) for x,y in zip(xs,ys)])
    c=mp.lu_solve(M,v); return [c[i] for i in range(n)]
def ev(c,funcs,x): return mp.fsum([ci*f(x) for ci,f in zip(c,funcs)])

print("=== 1. SIGNED per-rung deviation from the 11-rung K=6 extrapolation, x eps^2 ===")
poly6=[(lambda x,i=i: x**i) for i in range(7)]
c6=fit(E[:11],R[:11],poly6)
print(" %-10s %-18s %-18s" % ("eps","r_obs - r_pred","(r_obs-r_pred)*eps^2"))
for e_s in NEW:
    e=mp.mpf(e_s); ro=r_of(e, mp.mpf(d["rungs"][e_s]["u"])); rp=ev(c6,poly6,e)
    print(" %-10s %-18s %-18s" % (e_s, mp.nstr(ro-rp,8), mp.nstr((ro-rp)*e**2,8)))

print("\n=== 2. JOINT 17-rung fit with eps^-2 in the basis (da free), K=3..6 ===")
print(" %-4s %-16s %-22s %-20s" % ("K","max residual","a3","da = -c[eps^-2]"))
best=None
for K in range(3,7):
    funcs=[lambda x: 1/x**2]+[(lambda x,i=i: x**i) for i in range(K+1)]
    c=fit(E,R,funcs)
    mr=max(abs(ev(c,funcs,x)-y) for x,y in zip(E,R))
    da=-c[0]
    print(" %-4d %-16s %-22s %-20s" % (K, mp.nstr(mr,8), mp.nstr(c[1],22), mp.nstr(da,10)))
    if best is None or mr<best[0]: best=(mr,K,c,funcs,da)

mr,K,c,funcs,da=best
print("\nbest K=%d  max residual %s  a3=%s  da=%s" % (K,mp.nstr(mr,8),mp.nstr(c[1],22),mp.nstr(da,10)))
a_new = A + da
print("  a_operative      = %s" % mp.nstr(A,22))
print("  a_operative + da  = %s" % mp.nstr(a_new,22))
print("  retired 16 s.f. a = %s   (a_new - it = %s)" % (mp.nstr(A_OLD16,22), mp.nstr(a_new-A_OLD16,8)))
print("  m1 eps->0 ladder  = %s   (a_new - it = %s)" % (mp.nstr(A_M1LADDER,22), mp.nstr(a_new-A_M1LADDER,8)))
print("  a_operative - retired16 = %s" % mp.nstr(A-A_OLD16,8))

print("\n=== 3. does an eps^-1 (db) term add anything? ===")
for K in range(3,7):
    funcs2=[lambda x: 1/x**2, lambda x: 1/x]+[(lambda x,i=i: x**i) for i in range(K+1)]
    c2=fit(E,R,funcs2)
    mr2=max(abs(ev(c2,funcs2,x)-y) for x,y in zip(E,R))
    print("  K=%d  with eps^-1: max res %-14s  da=%-14s  db=%s"
          % (K, mp.nstr(mr2,8), mp.nstr(-c2[0],8), mp.nstr(c2[1],8)))

print("\n=== 4. re-run the WHOLE unit with a := a_operative + da (no other change) ===")
R2=[r_of(e,u,a=a_new) for e,u in zip(E,U)]
def loo(xs,ys,funcs):
    order=sorted(range(len(xs)),key=lambda i:xs[i]); errs=[]
    for i in order[1:-1]:
        xr=[xs[j] for j in range(len(xs)) if j!=i]; yr=[ys[j] for j in range(len(ys)) if j!=i]
        cc=fit(xr,yr,funcs); errs.append(ev(cc,funcs,xs[i])-ys[i])
    return mp.sqrt(mp.fsum([e**2 for e in errs])/len(errs))
print(" %-4s %-16s %-16s %-22s" % ("K","max res","interior LOO","a3"))
bl=None
for K in range(3,9):
    fn=[(lambda x,i=i: x**i) for i in range(K+1)]
    cc=fit(E,R2,fn); mr3=max(abs(ev(cc,fn,x)-y) for x,y in zip(E,R2)); lo=loo(E,R2,fn)
    print(" %-4d %-16s %-16s %-22s" % (K,mp.nstr(mr3,8),mp.nstr(lo,8),mp.nstr(cc[0],22)))
    if bl is None or lo<bl[0]: bl=(lo,K,cc[0])
print(" LOO-optimal K=%d  a3=%s  (11-rung published a3 = 11.700717319895873971)" % (bl[1],mp.nstr(bl[2],22)))
sp=[]
for K in (6,7,8):
    fn=[(lambda x,i=i: x**i) for i in range(K+1)]; sp.append(fit(E,R2,fn)[0])
print(" a3 spread K6..8 with corrected a = %s   (11-rung reference 3.4931094e-9)" % mp.nstr(max(sp)-min(sp),8))
