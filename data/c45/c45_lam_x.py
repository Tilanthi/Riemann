#!/usr/bin/env python3
"""c45_lam_x.py -- lambda_min(x) only. No zero-root machinery, no zetazero calls.

usage: c45_lam_x.py X N DPS GLDEG ITERS
Emits JSON next to itself. ITERS is explicit and defaults to nothing on purpose: ERRATUM 22 exists
because smallest_eigenpair's inverse-iteration count is a knob that does not announce itself.
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "c42"))
from mpmath import mp
from c42_connes_x import build_matrix, smallest_eigenpair

# x may be NON-INTEGER: build_matrix uses log(mpf(x)) and prime_powers_upto walks n <= x, so a real
# cutoff is meaningful and is needed to sit exactly on an externally published window endpoint.
X = float(sys.argv[1]) if "." in sys.argv[1] else int(sys.argv[1])
N, DPS, GLDEG, ITERS = (int(a) for a in sys.argv[2:6])
mp.dps = DPS                     # dps FIRST, before any mpmath value is created (m3's habit, c45)
t0 = time.time()
M, L, om, nr, pps = build_matrix(N, X, GLDEG, verbose=False)
t_build = time.time() - t0
lam, v = smallest_eigenpair(M, iters=ITERS, verbose=False)
out = dict(x=X, N=N, dps=DPS, gl_degree=GLDEG, iters=ITERS, prime_powers=pps,
           L=mp.nstr(L, 40), lambda_min=mp.nstr(lam, 60),
           lambda_min_30=mp.nstr(lam, 30),
           log10=mp.nstr(mp.log(lam, 10), 20),
           seconds_build=t_build, seconds_total=time.time() - t0)
fn = os.path.join(HERE, "c45_x%s_N%d_dps%d_g%d_it%d.json" % (str(X).replace(".","p"), N, DPS, GLDEG, ITERS))
json.dump(out, open(fn, "w"), indent=1)
print("x=%s N=%d dps=%d g=%d it=%d  lambda_min=%s  log10=%s  %.1fs"
      % (str(X), N, DPS, GLDEG, ITERS, out["lambda_min_30"], out["log10"], out["seconds_total"]), flush=True)
