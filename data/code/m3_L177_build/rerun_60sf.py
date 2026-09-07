import sys, time
sys.path.insert(0, '.')
import mpmath as mp
from weil_form2 import build_matrix_fast

x, N, L_x = 13, 100, None
L = mp.log(mp.mpf(13))
dps = 250
t0 = time.time()
M = build_matrix_fast(x, N, L, dps, log=True)
print(f"[{time.time()-t0:.1f}s] matrix built, computing eigenvalues", flush=True)
Mm = mp.matrix(M)
E, _ = mp.eigsy(Mm)
lam_min = min(E)
print(f"[{time.time()-t0:.1f}s] lambda_min (x=13, N=100, dps={dps}) = {mp.nstr(lam_min, 65)}")
