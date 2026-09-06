"""m2 c30 POST-HOC part 3 -- three independence checks on the delta_a finding."""
import json, sys
from mpmath import mp
sys.path.insert(0,"/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2
mp.dps = 60
A=mp.mpf("2.645521411811664489"); B=-mp.mpf("7.4624528767937415788")
DSTAR=mp.mpf("0.141733239663887191395415685084185024")
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
def r_of(e,u,a=A,b=B): return (u**2-a*e+b*e**2)/e**3
def fit(xs,ys,fn):
    n=len(fn); M=mp.matrix(n,n); v=mp.matrix(n,1)
    for i in range(n):
        for j in range(n): M[i,j]=mp.fsum([fn[i](x)*fn[j](x) for x in xs])
        v[i]=mp.fsum([y*fn[i](x) for x,y in zip(xs,ys)])
    c=mp.lu_solve(M,v); return [c[i] for i in range(n)]
def ev(c,fn,x): return mp.fsum([ci*f(x) for ci,f in zip(c,fn)])
def poly(K): return [(lambda x,i=i: x**i) for i in range(K+1)]

En=[mp.mpf(e) for e in NEW]; Un=[mp.mpf(d["rungs"][e]["u"]) for e in NEW]
Rn=[r_of(e,u) for e,u in zip(En,Un)]
Eo=[mp.mpf(e) for e,_ in L165]; Uo=[mp.mpf(u) for _,u in L165]
Ro=[r_of(e,u) for e,u in zip(Eo,Uo)]

print("=== (i) SIX NEW RUNGS ALONE (no published rung used): r = c0/eps^2 + a3 + a4 eps + a5 eps^2 ===")
for K in (2,3):
    fn=[lambda x:1/x**2]+poly(K); c=fit(En,Rn,fn)
    res=max(abs(ev(c,fn,x)-y) for x,y in zip(En,Rn))
    print("  K=%d  c0 = %-18s a3 = %-22s max res %s" % (K,mp.nstr(c[0],10),mp.nstr(c[1],22),mp.nstr(res,8)))
print("  17-rung joint value for comparison: c0 = -1.633394698e-15")

print("\n=== (ii) ELEVEN PUBLISHED RUNGS ALONE: can they see it?  (the blindness receipt) ===")
for K in (5,6,7):
    fn=[lambda x:1/x**2]+poly(K); c=fit(Eo,Ro,fn)
    res=max(abs(ev(c,fn,x)-y) for x,y in zip(Eo,Ro))
    print("  K=%d  c0 = %-18s (true value -1.63e-15)  max res %s" % (K,mp.nstr(c[0],10),mp.nstr(res,8)))

print("\n=== (iii) INSTRUMENT BOUND: delta_u <= |xi(u)|/|xi'(u)| at the smallest rung ===")
eps=mp.mpf("0.0001"); Z=Zeta2(DSTAR+eps,dps=60)
f=lambda t: mp.re(Z.xi(mp.mpf(0.5)+1j*mp.mpf(t)))
u=mp.mpf(d["rungs"]["0.0001"]["u"])
h=u*mp.mpf("1e-8")
fp=(f(u+h)-f(u-h))/(2*h)
print("  eps=1e-4  u=%s" % mp.nstr(u,28))
print("  |xi(u)|  = %s" % mp.nstr(abs(f(u)),8))
print("  |xi'(u)| = %s" % mp.nstr(abs(fp),8))
du=abs(f(u))/abs(fp)
print("  => delta_u <= %s" % mp.nstr(du,8))
print("  the delta_a signature needs delta_u = delta_a*sqrt(eps)/(2*sqrt(a)) = %s"
      % mp.nstr(mp.mpf("1.6334e-15")*mp.sqrt(eps)/(2*mp.sqrt(A)),8))
print("  ratio (needed / bound) = %s" % mp.nstr((mp.mpf("1.6334e-15")*mp.sqrt(eps)/(2*mp.sqrt(A)))/du,8))
