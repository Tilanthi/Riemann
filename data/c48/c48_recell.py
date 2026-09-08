#!/usr/bin/env python3
"""c48_recell.py -- regenerate a c46 parity cell with the c48 storage layer.

The science is c46's, unchanged and IMPORTED, not copied: `build_matrix_parity` and c42's
`smallest_eigenpair` are called exactly as `c46_parity.run_cell` calls them, with the same
(parity, x, N, dps, gl_degree, iters).  The ONLY difference is what reaches the file:

    c46:  lambda_min = mp.nstr(lam, 60)                      <- 90 digits discarded at write time
    c48:  lambda_min = mp.nstr(lam, 60)   (RETAINED, byte-identical)
        + lambda_min_full   / lambda_min_exact               <- the full working-precision value

Because the retained field is produced by the identical call on the identical run, byte-equality of
`lambda_min` between the c48 cell and the frozen c46 cell is simultaneously
  (a) the reproduction check on the computation, and
  (b) the non-movement proof for the fix.
It is checked here at write time and again, independently, by m2_c48_nonmovement_check.py.

usage: c48_recell.py PARITY X N DPS GLDEG ITERS OUTDIR [C46DIR]
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mpmath import mp, mpf, sqrt
import m2_c48_cell_storage as S

# repo layout: this file lives in data/c48/, the science in data/c46/ and data/c42/, the storage
# layer in data/code/. Overridable for out-of-tree runs (the c48 ladder itself was produced with the
# code copied OUT of the clone, because c46_parity.run_cell writes next to itself).
DATA = os.path.dirname(HERE)
C46DIR = os.environ.get("M2_C46DIR", os.path.join(DATA, "c46"))
sys.path.insert(0, C46DIR)
sys.path.insert(0, os.environ.get("M2_C42DIR", os.path.join(DATA, "c42")))
sys.path.insert(0, os.path.join(DATA, "code"))
import c46_parity as c46
import c42_connes_x as c42

RET_LAM = (("", 60), ("_30", 30))
RET_L = (("", 40),)
RET_RES = (("", 10),)
RET_LOG = (("", 20),)


def main(parity, X, N, DPS, GLDEG, ITERS, outdir):
    mp.dps = DPS                       # dps FIRST, before any mpmath value is created
    t0 = time.time()
    M, L, pps = c46.build_matrix_parity(N, X, GLDEG, parity)
    t_build = time.time() - t0
    lam, v = c42.smallest_eigenpair(M, iters=ITERS, verbose=False)
    A = mp.matrix(M)
    Av = A * v
    res = sqrt(sum((Av[i] - lam * v[i]) ** 2 for i in range(len(M))))
    vnorm = sqrt(sum(v[i] ** 2 for i in range(len(M))))

    out = dict(parity=parity, x=X, N=N, dim=len(M), dps=DPS, gl_degree=GLDEG, iters=ITERS,
               prime_powers=pps)
    out.update(S.store_number(L, "L", RET_L))
    out.update(S.store_number(lam, "lambda_min", RET_LAM))
    out.update(S.store_number(res, "residual", RET_RES))
    out.update(S.store_number(mp.log(lam, 10), "log10", RET_LOG))
    # the accuracy witness that belongs BESIDE the width (c37's standing remedy):
    # for a symmetric M, |lam - lam_exact(M)| <= ||Av - lam v|| / ||v||  (Weyl / Rayleigh residual).
    out["eig_residual_bound_sf"] = mp.nstr(-mp.log(res / vnorm / abs(lam), 10), 8)
    out["accuracy_note"] = ("_full is the WORKING PRECISION of the run (a knob). The digits of "
                            "lambda_min supported by the eigensolve on the assembled matrix are "
                            "bounded below by eig_residual_bound_sf; the digits supported against "
                            "the exact matrix are a separate MEASUREMENT (vary dps, see "
                            "m2_c48_recover_depth.py). A width is not a certificate.")
    out["seconds_build"] = t_build
    out["seconds_total"] = time.time() - t0
    out["storage"] = "m2_c48_cell_storage.py; retained fields byte-identical to c46_parity.run_cell"

    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    fn = os.path.join(outdir, "c48_%s_x%s_N%d_dps%d_g%d_it%d.json"
                      % (parity, str(X).replace(".", "p"), N, DPS, GLDEG, ITERS))
    json.dump(out, open(fn, "w"), indent=1)

    # write-time reproduction + non-movement check against the frozen c46 cell, if present
    old = os.path.join(C46DIR, "c46_%s_x%s_N%d_dps%d_g%d_it%d.json"
                       % (parity, str(X).replace(".", "p"), N, DPS, GLDEG, ITERS))
    verdict = "NO FROZEN CELL"
    if os.path.exists(old):
        o = json.load(open(old))
        same = [(k, out[k] == o[k]) for k in ("L", "lambda_min", "lambda_min_30", "residual", "log10")
                if k in o]
        verdict = " ".join("%s=%s" % (k, "SAME" if s else "MOVED") for k, s in same)
    print("%s x=%s N=%d dps=%d dim=%d  lam=%s  full_sf=%d  resid_sf=%s  %.1fs  [%s]"
          % (parity, X, N, DPS, len(M), out["lambda_min_30"], out["lambda_min_full_sf"],
             out["eig_residual_bound_sf"], out["seconds_total"], verdict), flush=True)
    return 0


if __name__ == "__main__":
    a = sys.argv
    X = float(a[2]) if "." in a[2] else int(a[2])
    sys.exit(main(a[1], X, int(a[3]), int(a[4]), int(a[5]), int(a[6]), a[7]))
