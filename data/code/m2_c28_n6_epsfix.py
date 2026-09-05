"""machine2 CYCLE 28, leg 3c -- THE ~4e-8 FLOOR IS MY OWN eps-TRUNCATION ARTEFACT, and my
cycle-21 .out documents it in its own header.  Lines 37-38 of machine2_cycle21_birth_locus.out:
  printed 0.0011239031932557  exact 0.001123903193255665747441  delta_eps=3.425e-17 => delta_u ~ 8.309e-16
  printed 0.0082667603361     exact 0.008266760336112808604584  delta_eps=-1.281e-14 => delta_u ~ 1.146e-13
The grid ROWS were computed at the PRINTED eps.  Leg 3b paired those u with the EXACT eps.
Redo with the eps actually used, and with the two affected rows dropped.
"""
from mpmath import mp
mp.dps = 50
A = mp.mpf("2.645521411811663"); B = mp.mpf("-7.46245287679")
RUN = [("0.001","0.05150723818940063653522997"),
 ("0.0011239031932557","0.05461458474016286082927124"),
 ("0.002","0.07294509283746563691152741"),("0.0035","0.09670183421043065840984313"),
 ("0.006","0.1270603431867589315365682"),
 ("0.0082667603361","0.149621445957808028913411"),
 ("0.012","0.1812222345972055203851323"),("0.02","0.236627035028954718936398"),
 ("0.035","0.3197940308419042261822956"),("0.06","0.434057465263706265691976"),
 ("0.1","0.5942792183051371124814878")]
def fit(E,R,K):
    n=K+1;M=mp.matrix(n,n);rhs=mp.matrix(n,1)
    for i in range(n):
        for j in range(n): M[i,j]=sum(x**(i+j) for x in E)
        rhs[i]=sum(y*x**i for x,y in zip(E,R))
    c=mp.lu_solve(M,rhs)
    rr=[y-sum(c[k]*x**k for k in range(n)) for x,y in zip(E,R)]
    return [c[k] for k in range(n)],max(abs(t) for t in rr),rr
for tag,rows in (("eps AS RUN (printed), 11 pts",RUN),
                 ("two anchor rows DROPPED, 9 pts",[r for i,r in enumerate(RUN) if i not in (1,5)])):
    E=[mp.mpf(a) for a,_ in rows];U=[mp.mpf(b) for _,b in rows]
    R=[(u**2-A*e+B*e**2)/e**3 for e,u in zip(E,U)]
    print("\n=== %s ==="%tag)
    print("%-4s %-20s %-12s %-12s %-11s"%("K","a3","a4","a5","max resid"))
    for K in range(3,min(8,len(rows)-2)+1):
        c,res,_=fit(E,R,K)
        print("%-4d %-20s %-12s %-12s %-11s"%(K,mp.nstr(c[0],16),mp.nstr(c[1],8),
              mp.nstr(c[2],8),mp.nstr(res,3)))
    c,res,rr=fit(E,R,5)
    print("K=5 per-point residual:",", ".join(mp.nstr(t,3) for t in rr))
