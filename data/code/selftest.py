from mpmath import mp, mpf, log, nsum, inf, nstr
mp.dps=40
import bd_dn as B
from math import gcd
# ARM 1: closed form vs analytic value for (2,2)
v = B.inner_f(2,2); exact = mpf(1)/4*log(2)
print("ARM1 (2,2):", nstr(v,20), "vs 0.25*ln2 =", nstr(exact,20), "ok" if abs(v-exact)<mpf(10)**-30 else "FAIL")
# ARM 2: closed form vs BRUTE-FORCE truncated series with tail bound
def brute(j,k,R=4000000):
    s=mpf(0)
    for r in range(1,R):
        wj=r%j
        if wj==0: continue
        wk=r%k
        if wk==0: continue
        s+= mpf(wj*wk)/(j*k*r*(r+1))
    return s, mpf(1)/R   # tail < sum_{r>=R} 1/(r(r+1)) = 1/R
for (j,k) in [(2,3),(3,3),(4,6),(5,7),(6,10)]:
    cf=B.inner_f(j,k); bf,tail=brute(j,k,200000)
    print(f"ARM2 ({j},{k}): closed={nstr(cf,14)} brute={nstr(bf,14)} diff={nstr(abs(cf-bf),4)} tailbound={nstr(tail,4)}",
          "ok" if abs(cf-bf)<tail else "FAIL")
# ARM 3: Vasyunin closed form (14) as an INDEPENDENT check, j!=k coprime-and-not
from mpmath import cot, pi, euler
def vas_diag_part(j,k):
    # eq (14) partial: only the terms printed in the fetched text (2 cot sums + logs).
    return None
# ARM 4: b_k
print("ARM4 b_2 =", nstr(B.b_f(2),12), "expect ln2/2 =", nstr(log(2)/2,12))
