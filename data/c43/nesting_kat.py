"""KNOWN-ANSWER TEST of my own model-free bound: is M(N=n1) EXACTLY the leading principal
block of M(N=n2)?  If yes, Cauchy interlacing gives lambda_min(N) non-increasing, rigorously."""
import sys; sys.path.insert(0,"/workspace/rh/cycle42")
from mpmath import mp, mpf
mp.dps=30
from c42_connes_x import build_matrix, smallest_eigenpair
M1,_,_,_,_ = build_matrix(12, 13, 9, verbose=False)
M2,_,_,_,_ = build_matrix(20, 13, 9, verbose=False)
worst=mpf(0)
for i in range(13):
    for j in range(13):
        worst=max(worst, abs(M1[i][j]-M2[i][j]))
print("max |M(N=12)[i][j] - M(N=20)[i][j]| over the shared 13x13 block =", mp.nstr(worst,5))
print("=> nesting is EXACT" if worst==0 else "=> NOT exactly nested")
l1,_=smallest_eigenpair(M1,verbose=False); l2,_=smallest_eigenpair(M2,verbose=False)
print("lambda_min(N=12) = %s ;  lambda_min(N=20) = %s ;  non-increasing: %s"
      %(mp.nstr(l1,10),mp.nstr(l2,10), l2<=l1))
