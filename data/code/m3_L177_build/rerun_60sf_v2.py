import sys, time
sys.path.insert(0, '.')
import mpmath as mp
from weil_form2 import build_matrix_fast

dps = 250
mp.mp.dps = dps          # SET DPS FIRST -- v1's bug was computing L before this line,
                          # baking in a 15-digit-precision L into a dps=250 computation
x, N = 13, 100
L = mp.log(mp.mpf(13))   # now computed at full working precision
t0 = time.time()
M = build_matrix_fast(x, N, L, dps, log=True)
print(f"[{time.time()-t0:.1f}s] matrix built, computing eigenvalues", flush=True)
Mm = mp.matrix(M)
E, _ = mp.eigsy(Mm)
lam_min = min(E)
print(f"[{time.time()-t0:.1f}s] lambda_min (x=13, N=100, dps={dps}) = {mp.nstr(lam_min, 65)}")

# sanity: re-derive L at dps=150 too and confirm it reproduces the earlier committed dps150 value
mp.mp.dps = 150
L150 = mp.log(mp.mpf(13))
M150 = build_matrix_fast(x, N, L150, 150, log=False)
E150, _ = mp.eigsy(mp.matrix(M150))
print(f"sanity dps150 rerun = {mp.nstr(min(E150), 45)}")
print(f"committed dps150    = 3.720899741667123935791434766094540694091e-59")
