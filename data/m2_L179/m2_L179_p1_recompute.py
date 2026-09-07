#!/usr/bin/env python3
"""
m2_L179_p1_recompute.py — machine 2's INDEPENDENT recompute of P1 = lambda_min(x=13, N=100)
to >= 68 significant figures, answering m3-L179 (astra-pa) and BEAST-AGI's cross-check brief.

WHAT THIS IS AND IS NOT INDEPENDENT OF
  independent of : m3's rerun_60sf.py / rerun_60sf_v2.py, m3's committed intermediates, m3's
                   printed literals (none of them are read, imported or used as a starting
                   point anywhere in this file or in c42_connes_x.py).
  shared with m3 : (a) the DEFINITION of the quantity — the c42 README section 1 convention
                   (basis, form, prime-power support, minimisation, quadrature family);
                   (b) Python 3 + mpmath as the arithmetic library. Named, not claimed away.
  our own code   : c42_connes_x.py (machine 2, cycle 42), used unmodified.

BUG THIS RUN MUST NOT HAVE (m3-L179 section 1, and our own c34 grader defect (i)):
  an mpf/constant created BEFORE mp.dps is raised is silently born at 15 digits and caps
  everything downstream. Countermeasures here, in order:
    1. mp.dps is set on the first executable line that touches mpmath, BEFORE the pipeline
       module is imported and before any mpf exists.
    2. --bug reproduces that exact shape ON PURPOSE inside OUR pipeline (L = log(13) built at
       the default dps, then dps raised), so that a 15-s.f.-deep agreement is DISTINGUISHABLE
       from a genuine deep one instead of being a mystery.
    3. the dps=150/GL9 cell is a KNOWN-ANSWER TEST against our own committed c43 literals.

CHANNELS (a certified width must be measured per channel, not asserted — c34/c44):
  dps channel : 150 vs 250 vs 300 at fixed GL degree 9
  quadrature  : GL degree 9 vs 10 at fixed dps 250
The published width is min(agreement across both channels), printed one digit wider (c39).
"""
import sys, time, json, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--dps", type=int, required=True)
ap.add_argument("--gl", type=int, default=9)
ap.add_argument("--x", type=int, default=13)
ap.add_argument("--N", type=int, default=100)
ap.add_argument("--width", type=int, default=120, help="s.f. printed (>= any width claimed)")
ap.add_argument("--iters", type=int, default=4,
                help="inverse-iteration count; THE THIRD CHANNEL — c34: the knob you did not vary is the one that binds")
ap.add_argument("--startvec", default="uniform", choices=("uniform", "alt", "random"),
                help="FOURTH channel: the inverse iteration's start vector. 'uniform' uses the "
                     "c42 pipeline's own smallest_eigenpair(); the others run a SECOND, locally "
                     "written implementation of the same iteration, so this switch varies the "
                     "start vector AND the implementation at once (declared, not conflated).")
ap.add_argument("--bug", action="store_true",
                help="POSITIVE CONTROL: build L=log(x) at the DEFAULT dps before raising dps")
ap.add_argument("--out", required=True)
ap.add_argument("--srcdir", default="/workspace/rh/cycle42")
a = ap.parse_args()

from mpmath import mp

# --- positive control: the contaminated constant must be born BEFORE dps is raised ---------
L_CONTAMINATED = None
if a.bug:
    assert mp.dps == 15, "control requires the mpmath default"
    L_CONTAMINATED = mp.log(mp.mpf(a.x))          # <-- 15 digits, on purpose

# --- THE HABIT: dps first, before the pipeline module is imported and before any mpf ------
mp.dps = a.dps

sys.path.insert(0, a.srcdir)
import c42_connes_x as P                            # our own cycle-42 pipeline, unmodified

if a.bug:                                           # one-shot patch: only the L = log(x) call
    _orig_log, _fired = P.log, [False]
    def _log(v):
        if not _fired[0] and v == mp.mpf(a.x):
            _fired[0] = True
            return L_CONTAMINATED
        return _orig_log(v)
    P.log = _log

t0 = time.time()
M, L, om, nr, pps = P.build_matrix(a.N, a.x, a.gl, verbose=False)
t_mat = time.time() - t0
if a.startvec == "uniform":
    lam, v = P.smallest_eigenpair(M, iters=a.iters, verbose=False)
else:
    # second implementation of the same inverse iteration, different start vector
    import random
    n = len(M)
    A = mp.matrix(M)
    if a.startvec == "alt":
        v = mp.matrix([mp.mpf((-1) ** i) / mp.sqrt(n) for i in range(n)])
    else:
        random.seed(20260907)
        v = mp.matrix([mp.mpf(random.uniform(-1, 1)) for _ in range(n)])
        v = v / mp.sqrt(sum(x ** 2 for x in v))
    for _ in range(a.iters):
        w = mp.lu_solve(A, v)
        v = w / mp.sqrt(sum(x ** 2 for x in w))
    Av0 = A * v
    lam = sum(v[i] * Av0[i] for i in range(n))
t_all = time.time() - t0

# residual of the eigenpair, so the eigen-solve is not taken on trust
Av = mp.matrix(M) * v
res = mp.sqrt(sum((Av[i] - lam * v[i]) ** 2 for i in range(len(v))))

rec = dict(who="machine2 (beast-atlas)", script="m2_L179_p1_recompute.py",
           x=a.x, N=a.N, dps=a.dps, gl_degree=a.gl, iters=a.iters, startvec=a.startvec, mode=("BUG-CONTROL" if a.bug else "CLEAN"),
           n_gl_nodes=3 * 2 ** a.gl, prime_power_support=[str(p) for p in pps],
           lambda_min=mp.nstr(lam, a.width, strip_zeros=False),
           lambda_min_w45=mp.nstr(lam, 45, strip_zeros=False),
           lambda_min_w60=mp.nstr(lam, 60, strip_zeros=False),
           lambda_min_w100=mp.nstr(lam, 100, strip_zeros=False),
           eig_residual=mp.nstr(res, 8), rel_eig_residual=mp.nstr(res / abs(lam), 8),
           secs_matrix=round(t_mat, 1), secs_total=round(t_all, 1))
json.dump(rec, open(a.out, "w"), indent=1)
for k in ("mode", "dps", "gl_degree", "iters", "startvec", "n_gl_nodes", "lambda_min", "rel_eig_residual", "secs_total"):
    print("%-18s %s" % (k, rec[k]), flush=True)
