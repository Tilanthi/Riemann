#!/usr/bin/env python3
"""c43_widen.py -- rerun the c42 x=13 N=100 dps=150 PRIMARY cell and print lambda_min
at a width WIDER than the certified width, discharging the c39 print-width remedy at
the level of the INSTRUMENT'S STORAGE rather than the letter's prose.
Strict subset of c42_run.py: identical build_matrix + smallest_eigenpair path, zero
diagnostics skipped (they do not touch lambda_min)."""
import sys, time, json
sys.path.insert(0, "/workspace/rh/cycle42")
from mpmath import mp
X, N, DPS, GLDEG = 13, 100, 150, 9
mp.dps = DPS
from c42_connes_x import build_matrix, smallest_eigenpair
t0=time.time()
M, L, om, nr, pps = build_matrix(N, X, GLDEG, verbose=False)
print("matrix %.1fs"%(time.time()-t0), flush=True)
lam, v = smallest_eigenpair(M, verbose=False)
print("eig    %.1fs"%(time.time()-t0), flush=True)
out = dict(x=X, N=N, dps=DPS, gldeg=GLDEG,
           lambda_min_w30_AS_PUBLISHED=mp.nstr(lam, 30),
           lambda_min_w45=mp.nstr(lam, 45),
           lambda_min_w60=mp.nstr(lam, 60),
           lambda_min_w100=mp.nstr(lam, 100),
           prime_power_support=[str(p) for p in pps])
json.dump(out, open("/workspace/c43/c43_x13_N100_dps150_widened.json","w"), indent=1)
for k in ("lambda_min_w30_AS_PUBLISHED","lambda_min_w45","lambda_min_w60"):
    print(k, "=", out[k])
print("wall %.1fs"%(time.time()-t0))
