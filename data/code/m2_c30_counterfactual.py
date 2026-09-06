"""m2 c30 POST-HOC part 4 -- COUNTERFACTUAL regrade with a := a_ladder. LABELLED POST-HOC,
NOT a verdict; the graded tally stays 0 HELD / 5 FALSIFIED."""
import json
from mpmath import mp
mp.dps=60
A=mp.mpf("2.645521411811664489"); B=-mp.mpf("7.4624528767937415788")
DA=-mp.mpf("1.633394698e-15"); AT=A+DA
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
def r_of(e,u,a): return (u**2-a*e+B*e**2)/e**3
def fit(xs,ys,fn):
    n=len(fn);M=mp.matrix(n,n);v=mp.matrix(n,1)
    for i in range(n):
        for j in range(n): M[i,j]=mp.fsum([fn[i](x)*fn[j](x) for x in xs])
        v[i]=mp.fsum([y*fn[i](x) for x,y in zip(xs,ys)])
    c=mp.lu_solve(M,v);return [c[i] for i in range(n)]
def ev(c,fn,x): return mp.fsum([ci*f(x) for ci,f in zip(c,fn)])
def poly(K): return [(lambda x,i=i: x**i) for i in range(K+1)]
def loo(xs,ys,fn):
    o=sorted(range(len(xs)),key=lambda i:xs[i]);e=[]
    for i in o[1:-1]:
        xr=[xs[j] for j in range(len(xs)) if j!=i];yr=[ys[j] for j in range(len(ys)) if j!=i]
        e.append(ev(fit(xr,yr,fn),fn,xs[i])-ys[i])
    return mp.sqrt(mp.fsum([x**2 for x in e])/len(e))
Eo=[mp.mpf(x) for x,_ in L165];Uo=[mp.mpf(u) for _,u in L165]
En=[mp.mpf(x) for x in NEW];Un=[mp.mpf(d["rungs"][x]["u"]) for x in NEW]
for lab,a in [("GRADED (a operative)",A),("COUNTERFACTUAL (a ladder)",AT)]:
    Ro=[r_of(e,u,a) for e,u in zip(Eo,Uo)];Rn=[r_of(e,u,a) for e,u in zip(En,Un)]
    c6=fit(Eo,Ro,poly(6))
    q1=max(abs(ev(c6,poly(6),e)-r) for e,r in zip(En,Rn))
    E=Eo+En;R=Ro+Rn
    best=None
    for K in range(3,9):
        l=loo(E,R,poly(K))
        if best is None or l<best[0]: best=(l,K)
    a3=fit(E,R,poly(best[1]))[0]
    sp=[fit(E,R,poly(K))[0] for K in (6,7,8)]
    lb=loo(E,R,poly(best[1])); lh=loo(E,R,poly(best[1])+[lambda x:mp.sqrt(x)])
    a3ref=mp.mpf("11.700717319895873971") if a==A else fit(Eo,Ro,poly(6))[0]
    print("--- %s   (a3 11-rung K6 reference = %s)" % (lab, mp.nstr(a3ref,22)))
    print("   Q1 max dev      %-16s  thr <=2e-8        %s" % (mp.nstr(q1,8), "HELD" if q1<=mp.mpf("2e-8") else "FALSIFIED"))
    print("   Q2 LOO-opt K    %-16s  thr ==6           %s" % (best[1], "HELD" if best[1]==6 else "FALSIFIED"))
    sh=abs(a3-a3ref)
    print("   Q3 a3 shift     %-16s  thr <=1e-8        %s" % (mp.nstr(sh,8), "HELD" if sh<=mp.mpf("1e-8") else "FALSIFIED"))
    spread=max(sp)-min(sp)
    print("   Q4 a3 spread    %-16s  thr <3.4931094e-9 %s" % (mp.nstr(spread,8), "HELD" if spread<mp.mpf("3.4931094e-9") else "FALSIFIED"))
    print("   Q5 loo half/base %-15s  thr >=1           %s" % (mp.nstr(lh/lb,8), "HELD" if lh>=lb else "FALSIFIED"))
    print("   a3(union) = %s" % mp.nstr(a3,22))
