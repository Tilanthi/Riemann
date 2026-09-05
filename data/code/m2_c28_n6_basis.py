"""machine2 CYCLE 28, leg 3b -- IS THE ~4e-8 RESIDUAL FLOOR NOISE, OR A MISSING BASIS TERM?
The polynomial ladder K=5..8 on m2's full-precision cycle-21 r stalls at ~4e-8 while the
instrument's own floor is ~1e-18 and one published half-ulp of b moves the residual by 1%.
A stall that four extra free parameters cannot reduce is either a non-polynomial term in the
basis or an error in a published constant.  Both are testable, and m1-L137 already named the
first: "the grid's eps^{5/2} slope test measures [the even-carrier premise] on the locus side"
-- a test the locus side never ran.
Augment the K=5 polynomial with ONE extra basis function at a time and look for an ORDER
collapse of the residual, not a marginal improvement.
"""
from mpmath import mp
mp.dps = 50
A = mp.mpf("2.645521411811663"); B = mp.mpf("-7.46245287679")
DAT = [("0.001","0.05150723818940063653522997"),
 ("0.001123903193255665747441","0.05461458474016286082927124"),
 ("0.002","0.07294509283746563691152741"),("0.0035","0.09670183421043065840984313"),
 ("0.006","0.1270603431867589315365682"),
 ("0.008266760336112808604584","0.149621445957808028913411"),
 ("0.012","0.1812222345972055203851323"),("0.02","0.236627035028954718936398"),
 ("0.035","0.3197940308419042261822956"),("0.06","0.434057465263706265691976"),
 ("0.1","0.5942792183051371124814878")]
E=[mp.mpf(a) for a,_ in DAT]; U=[mp.mpf(b) for _,b in DAT]
R=[(u**2-A*e+B*e**2)/e**3 for e,u in zip(E,U)]

def lstsq(basis, ys):
    n=len(basis); M=mp.matrix(n,n); rhs=mp.matrix(n,1)
    cols=[[f(x) for x in E] for f in basis]
    for i in range(n):
        for j in range(n): M[i,j]=sum(cols[i][k]*cols[j][k] for k in range(len(E)))
        rhs[i]=sum(ys[k]*cols[i][k] for k in range(len(E)))
    c=mp.lu_solve(M,rhs)
    resid=[ys[k]-sum(c[i]*cols[i][k] for i in range(n)) for k in range(len(E))]
    return [c[i] for i in range(n)], max(abs(r) for r in resid), resid

poly=lambda K:[(lambda x,k=k: x**k) for k in range(K+1)]
extras={"none":None,"eps^0.5":lambda x:mp.sqrt(x),"eps^1.5":lambda x:x*mp.sqrt(x),
        "eps^2.5":lambda x:x**2*mp.sqrt(x),"eps^-1":lambda x:1/x,"eps^-2":lambda x:1/x**2,
        "log(eps)":lambda x:mp.log(x),"eps*log(eps)":lambda x:x*mp.log(x)}
print("K=5 polynomial (6 params) + ONE extra basis function (7 params), 11 points")
print("%-14s %-14s %-20s %s"%("extra","max resid","a3 = c_0","extra coeff"))
for name,f in extras.items():
    basis=poly(5)+([f] if f else [])
    c,res,_=lstsq(basis,R)
    print("%-14s %-14s %-20s %s"%(name,mp.nstr(res,3),mp.nstr(c[0],14),
          mp.nstr(c[-1],6) if f else "-"))
print("\nper-point residual, plain K=5 (sign pattern says structured vs random):")
c,res,rr=lstsq(poly(5),R)
for e,r in zip(E,rr): print("  eps=%-26s resid %s"%(mp.nstr(e,8),mp.nstr(r,4)))
