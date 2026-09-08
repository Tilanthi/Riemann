#!/usr/bin/env python3
"""m2_c53_spectrum.py -- cycle 53's instrument: the FULL spectrum of the same truncated matrix.

WHY THIS FILE EXISTS
--------------------
c51 closed with one named open item: "the SECOND dislocation's index ... Settling it needs k >= 8
at x=19 -- the cheapest next question. No guess registered."  Getting k >= 8 out of c50/c51's
block inverse iteration costs ~16 LU solves per extra rung and delivers its WORST rung at the top:
in every c51 cell the top rung's relative Ritz residual is 20-50 ORDERS OF MAGNITUDE larger than
the rung below it (x=13 k=7: 1.95e-125 at rung 6, 1.46e-71 at rung 7; x=19 k=5: 2.86e-192 at rung
4, 3.42e-96 at rung 5).  That is inherent to a block method: the top of the block is the least
converged.

This cycle solves the SAME matrix -- built by the SAME unmodified c46_parity.build_matrix_parity --
by direct symmetric eigendecomposition (mpmath eigsy), which returns EVERY rung at once.  Measured
cost at x=13 N=100 dps150: build 167.4 s, full 101-pair eigendecomposition 19.9 s.  The block
method spent 1219.6 s to reach 7 rungs of the same cell.

WHAT IS COPIED AND WHAT IS NEW
------------------------------
NOTHING is copied.  The node detector is IMPORTED from data/c51/m2_c51_nodes.py and used through
that module: sample_and_count, sample_values, refine, count_all_knobs, agree_sf, sturm.  c50's law
("ship a new script, never edit the registered one") is met by importing rather than editing, and
c51's "prove the copy is a copy" gate is replaced by something stronger -- there is no copy.  The
P0 gate below still runs, because the import CHAIN can break even when the source cannot.

NEW HERE:
  * `spec`   -- build + full eigendecomposition + residuals.  Writes eigenvalues and eigenvectors
                and NO NODE COUNT.  This split is the cycle's pre-registration mechanism: the
                eigenvalue ladders (and Model G's prediction derived from them) are pushed BEFORE
                any node count of an unpublished rung exists.
  * `nodes`  -- node counts for rungs 1..R, read from the PUBLISHED 40-s.f. coefficients in the
                spec file, so the artefact is the input.
  * `gpred`  -- Model G's rule evaluated on the pooled eigenvalue ladder alone.
  * `kat`    -- the eigensolver on PLANTED spectra spanning 90 orders of magnitude, which is the
                one thing about this instrument that c50/c51 never had to check.
  * `recount`-- the P0 gate: recount c51's PUBLISHED coefficient arrays through the imported
                detector and reproduce c51's published integers.

THE ADMISSION RULE CHANGES MEANING AND IT IS SAID HERE, NOT DISCOVERED LATER
---------------------------------------------------------------------------
c50's rule (relative Ritz residual < 1e-20) tests the SOLVER, not the BASIS.  For a direct
eigensolver the residual is at the level of the working precision for every rung, so the rule has
an ALMOST EMPTY FIRING WORLD here -- by ALGEBRA, not by measurement.  It is computed and reported
anyway (a rung that fails it is broken), but the cycle's truncation control is the N-CONTROL:
a rung is TRUSTED only if its node count agrees between N=100 and N=180 at the same (x, parity).

usage:
  m2_c53_spectrum.py kat                            planted-spectrum eigensolver KAT
  m2_c53_spectrum.py recount                        P0 gate vs c51's published node cells
  m2_c53_spectrum.py spec PARITY X N DPS GL         one cell -> m2_c53_spec_PARITY_xX_NN_dpsD.json
  m2_c53_spectrum.py nodes PARITY X N DPS R         rungs 1..R -> m2_c53_nodes_PARITY_xX_NN_dpsD.json
  m2_c53_spectrum.py gpred X N DPS                  Model G from the pooled ladder (eigenvalues only)
"""
import json, os, sys, time, random

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_dir(name):
    """resolve relative to THIS file (c50 addendum 2 / m1-L191 finding (c)); no absolute clone path.
    c52's law: PRINT THE PATH THE RESOLVER USED, so a portability pass cannot silently read the
    author's own tree."""
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


C42, CODE, C46, C50, C51 = (_find_dir(d) for d in ("c42", "code", "c46", "c50", "c51"))
for _d in (C42, CODE, C46, C51):
    sys.path.insert(0, _d)

from mpmath import mp, mpf, sqrt, log
import c46_parity as P
import m2_c51_nodes as ND            # the DETECTOR, imported, never copied

ADMIT_REL_RESID = mpf("1e-20")       # c50's rule; see the docstring -- it tests the solver, not the basis
STORE_SF = 40                        # c51's published coefficient width


def resolver_report():
    return dict(HERE=HERE, c42=C42, code=CODE, c46=C46, c50=C50, c51=C51,
                detector_module=os.path.abspath(ND.__file__))


def specname(par, X, N, DPS):
    return os.path.join(HERE, "m2_c53_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))


def nodename(par, X, N, DPS):
    return os.path.join(HERE, "m2_c53_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))


# ---------------------------------------------------------------- KAT: the eigensolver itself
def kat():
    """The NEW component is the eigensolver, so the KAT plants spectra it must recover.

    E1: D = diag(10^-90, 10^-80, ..., 10^0) conjugated by a random orthogonal Q built from
        Householder reflections.  ||A|| ~ 1 while the smallest eigenvalue is 1e-90, which is
        exactly the regime of the x=19 cell (lambda_1 ~ 1e-90).  A symmetric eigensolver has
        absolute error ~ eps*||A||, so at dps300 the RELATIVE error at 1e-90 should still be
        ~1e-210.  If it is not, every deep rung of this cycle is worthless and the cycle stops.
    E2: the same at dps150 (the x=13 cells' precision), where the floor is 1e-150 and the
        smallest planted eigenvalue 1e-90 must still come back to ~60 relative digits.
    E3: eigenVECTOR accuracy: the recovered vector for the smallest planted eigenvalue must have
        relative residual ||Av - lam v||/|lam| below 1e-20 (this cycle's admission rule).
    A dry run on a KNOWN ANSWER is the only thing that tests the test.
    """
    rows, fails = [], 0
    for tag, dps, lo, hi, step in (("E1", 300, -90, 0, 10), ("E2", 150, -90, 0, 10)):
        mp.dps = dps
        planted = [mpf(10) ** e for e in range(lo, hi + 1, step)]
        n = len(planted)
        random.seed(53)
        Q = mp.eye(n)
        for _ in range(3):
            v = mp.matrix([mpf(random.random()) - mpf("0.5") for _ in range(n)])
            nv = sqrt(sum(v[i] ** 2 for i in range(n)))
            for i in range(n):
                v[i] /= nv
            Hh = mp.eye(n) - 2 * (v * v.T)
            Q = Q * Hh
        A = Q * mp.diag(planted) * Q.T
        for i in range(n):
            for j in range(i):
                A[i, j] = A[j, i] = (A[i, j] + A[j, i]) / 2
        E, V = mp.eigsy(A)
        got = sorted([E[i] for i in range(n)])
        want = sorted(planted)
        for w, g in zip(want, got):
            rel = abs(g - w) / abs(w)
            ok = rel < mpf(10) ** (-(dps - 100))
            fails += 0 if ok else 1
            rows.append(dict(kat=tag, planted=mp.nstr(w, 5), got=mp.nstr(g, 25),
                             rel_err=mp.nstr(rel, 5), dps=dps, pass_=bool(ok)))
        # E3: vector residual for the smallest eigenvalue
        j = min(range(n), key=lambda a: E[a])
        v = mp.matrix([V[r, j] for r in range(n)])
        w = A * v - E[j] * v
        rel = sqrt(sum(w[r] ** 2 for r in range(n))) / abs(E[j])
        ok = rel < ADMIT_REL_RESID
        fails += 0 if ok else 1
        rows.append(dict(kat="E3-" + tag, planted=mp.nstr(min(planted), 5),
                         rel_residual=mp.nstr(rel, 5), dps=dps, pass_=bool(ok)))
    out = dict(rows=rows, fails=fails, verdict=("PASS" if fails == 0 else "FAIL"),
               resolver=resolver_report(),
               note="E1/E2 relative-accuracy floor is 10^-(dps-100), a deliberately loose gate: the "
                    "point is orders of magnitude, not the last digit.")
    json.dump(out, open(os.path.join(HERE, "m2_c53_kat.json"), "w"), indent=1)
    for r in rows:
        print("  %-6s dps=%-4s planted=%-10s %s %s"
              % (r["kat"], r["dps"], r["planted"],
                 ("rel_err=" + r["rel_err"]) if "rel_err" in r else ("rel_resid=" + r["rel_residual"]),
                 "PASS" if r["pass_"] else "FAIL"))
    print("KAT fails: %d -> %s" % (fails, out["verdict"]))
    return 0 if fails == 0 else 1


# ---------------------------------------------------------------- P0 gate through the IMPORT
def recount():
    """Recount EVERY published c51 node cell from its published 40-s.f. coefficients, through the
    imported detector, and compare against c51's published integers at all nine knob settings.
    c51's own gate did this for c50's two cells; this one does it for all eight of c51's."""
    mp.dps = 50
    tot = ok = 0
    rows = []
    files = sorted(f for f in os.listdir(C51) if f.startswith("m2_c51_nodes_") and f.endswith(".json"))
    for fn in files:
        d = json.load(open(os.path.join(C51, fn)))
        par, L = d["parity"], mpf(d["L"])
        om, nr, _ = P.make_basis_parity(d["N"], L, par)
        for rung in d["rungs"]:
            coef = [mpf(c) for c in rung["coef"]]
            counts, stable, nu = ND.count_all_knobs(coef, om, nr, L, par)
            for kk, v in sorted(rung["counts"].items()):
                tot += 1
                ok += 1 if counts[kk] == v else 0
            match = all(counts[k2] == v2 for k2, v2 in rung["counts"].items())
            rows.append(dict(file=fn, rung=rung["rung"], published_nu=rung["nu"], recounted_nu=nu,
                             match=bool(match)))
            print("  %-40s rung %-2d published nu=%-3s recounted nu=%-3s %s"
                  % (fn, rung["rung"], rung["nu"], nu, "OK" if match else "MISMATCH"), flush=True)
    verdict = "PASS" if ok == tot else "FAIL"
    json.dump(dict(compared=tot, matched=ok, verdict=verdict, files=files, rows=rows,
                   resolver=resolver_report()),
              open(os.path.join(HERE, "m2_c53_p0_recount.json"), "w"), indent=1)
    print("P0 GATE: %d/%d integers reproduced from %d published cells -> %s"
          % (ok, tot, len(files), verdict))
    return 0 if verdict == "PASS" else 1


# ---------------------------------------------------------------- stage A: the spectrum, NO nodes
def spec(par, X, N, DPS, GL):
    mp.dps = DPS
    t0 = time.time()
    M, L, _ = P.build_matrix_parity(N, X, GL, par)
    tb = time.time() - t0
    A = mp.matrix(M)
    dim = A.rows
    t1 = time.time()
    E, V = mp.eigsy(A)
    te = time.time() - t1
    order = sorted(range(dim), key=lambda i: E[i])
    rungs = []
    for m, i in enumerate(order, start=1):
        v = mp.matrix([V[r, i] for r in range(dim)])
        w = A * v - E[i] * v
        rel = sqrt(sum(w[r] ** 2 for r in range(dim))) / abs(E[i])
        rungs.append(dict(rung=m, lam=mp.nstr(E[i], STORE_SF),
                          log10=mp.nstr(mp.log(E[i], 10), 20) if E[i] > 0 else None,
                          positive=bool(E[i] > 0),
                          rel_residual=mp.nstr(rel, 10),
                          admitted=bool(rel < ADMIT_REL_RESID),
                          coef=[mp.nstr(v[r], STORE_SF) for r in range(dim)]))
    # self-test vs the PUBLISHED block ladder for this window, ceiling-limited by its print width
    ref, refl = ND.find_reference(par, X, N, DPS, GL, 16, 3)
    depths, ceiling = None, None
    if ref is not None:
        ceiling = max(len(s.split("e")[0].replace("-", "").replace(".", "").lstrip("0")) for s in refl)
        depths = [mp.nstr(ND.agree_sf(E[order[i]], mpf(refl[i]), ceiling), 6) for i in range(len(refl))]
    out = dict(parity=par, x=X, N=N, dps=DPS, gl=GL, dim=dim, L=mp.nstr(L, STORE_SF),
               build_seconds=tb, eigsy_seconds=te, seconds=time.time() - t0,
               reference=(os.path.basename(ref) if ref else None),
               selftest_depths_sf=depths, selftest_ceiling_sf=ceiling,
               solver="mpmath eigsy (full symmetric eigendecomposition)",
               admit_rule="rel residual < 1e-20 (c50 rule; tests the SOLVER, not the basis)",
               resolver=resolver_report(), rungs=rungs,
               label="REGISTERED (cycle 53 prereg) -- STAGE A: eigenvalues and vectors, NO node counts")
    fn = specname(par, X, N, DPS)
    json.dump(out, open(fn, "w"), indent=1)
    print("SELF-TEST vs %s: depths %s (CEILING %s s.f.)" % (out["reference"], depths, ceiling))
    print("wrote %s  dim=%d build=%.1fs eigsy=%.1fs total=%.1fs"
          % (os.path.basename(fn), dim, tb, te, out["seconds"]), flush=True)
    return 0


# ---------------------------------------------------------------- stage B: node counts
def nodes(par, X, N, DPS, R):
    mp.dps = 50
    d = json.load(open(specname(par, X, N, DPS)))
    L = mpf(d["L"])
    om, nr, _ = P.make_basis_parity(N, L, par)
    out = []
    t0 = time.time()
    for rung in d["rungs"][:R]:
        coef = [mpf(c) for c in rung["coef"]]
        counts, stable, nu = ND.count_all_knobs(coef, om, nr, L, par)
        nu_ref, lobe = ND.refine(coef, om, nr, L, par)
        st = ND.sturm(par, rung["rung"])
        out.append(dict(rung=rung["rung"], lam=rung["lam"], log10=rung["log10"],
                        rel_residual=rung["rel_residual"], admitted=rung["admitted"],
                        counts=counts, stable=stable, nu=nu, nu_refine_48001=nu_ref,
                        lobe_min_ratio=(None if lobe is None else mp.nstr(lobe, 6)),
                        sturm=st, delta=(None if nu is None else nu - st),
                        parity_T_ok=(None if nu is None else (nu % 2 == (0 if par == "even" else 1)))))
        print("  %-4s rung %-2d log10lam=%-16s rel_resid=%-12s adm=%-5s nu=%-4s refine=%-4s "
              "lobe=%-10s sturm=%-3d delta=%-4s stable=%s"
              % (par, rung["rung"], (rung["log10"] or "")[:16], rung["rel_residual"],
                 rung["admitted"], nu, nu_ref,
                 (None if lobe is None else mp.nstr(lobe, 4)), st,
                 (None if nu is None else nu - st), stable), flush=True)
    res = dict(parity=par, x=X, N=N, dps=DPS, dim=d["dim"], L=d["L"], R=R, rungs=out,
               seconds=time.time() - t0, source=os.path.basename(specname(par, X, N, DPS)),
               detector="IMPORTED from data/c51/m2_c51_nodes.py (not copied)",
               resolver=resolver_report(),
               label="REGISTERED (cycle 53 prereg) -- STAGE B: node counts")
    fn = nodename(par, X, N, DPS)
    json.dump(res, open(fn, "w"), indent=1)
    print("wrote %s  %.1fs" % (os.path.basename(fn), res["seconds"]), flush=True)
    return 0


# ---------------------------------------------------------------- Model G, from eigenvalues alone
def pooled_ladder(X, N, DPS):
    """pool the two sectors by eigenvalue.  Returns (rows, certified_prefix) where a row is
    (pooled_index, parity, sector_rung, log10 lambda).  c50's completeness certificate: with R
    rungs of each sector the pooled ORDER is certified only up to min(lam_even[R], lam_odd[R])."""
    rows = []
    tops = []
    for par in ("even", "odd"):
        d = json.load(open(specname(par, X, N, DPS)))
        rr = [r for r in d["rungs"] if r["positive"]]
        for r in rr:
            rows.append((mpf(r["log10"]), par, r["rung"]))
        tops.append(mpf(rr[-1]["log10"]))
    rows.sort()
    cert = sum(1 for r in rows if r[0] <= min(tops))
    return [(i + 1, p, m, lg) for i, (lg, p, m) in enumerate(rows)], cert


def gpred(X, N, DPS):
    """MODEL G (registered): p2 = 1 + (first strict local MAXIMUM of the pooled log-gap sequence
    that follows its first strict local MINIMUM).  Zero free parameters.  Evaluated on eigenvalues
    ONLY -- no node count is read by this function."""
    mp.dps = 50
    rows, cert = pooled_ladder(X, N, DPS)
    lg = [r[3] for r in rows]
    g = [lg[i + 1] - lg[i] for i in range(len(lg) - 1)]
    m = next((p for p in range(2, len(g)) if g[p - 1] < g[p - 2] and g[p - 1] < g[p]), None)
    M = None
    if m is not None:
        M = next((p for p in range(m + 1, len(g)) if g[p - 1] > g[p - 2] and g[p - 1] > g[p]), None)
    out = dict(x=X, N=N, dps=DPS, pooled_levels=len(rows), certified_prefix=cert,
               gaps=[mp.nstr(v, 12) for v in g],
               first_local_min_index=m, first_local_max_after=M,
               model_G_p2=(None if M is None else M + 1),
               pooled=[dict(p=i, parity=p, sector_rung=mm, log10=mp.nstr(l, 20)) for i, p, mm, l in rows],
               note="Model G is REFUTED IMMEDIATELY if it returns p2 <= 10 at x=19, because c51 "
                    "measured delta=2 at pooled index 10 there.")
    fn = os.path.join(HERE, "m2_c53_gpred_x%d_N%d_dps%d.json" % (X, N, DPS))
    json.dump(out, open(fn, "w"), indent=1)
    print("x=%d N=%d: pooled levels %d (certified prefix %d)" % (X, N, len(rows), cert))
    print("  gaps: %s" % [mp.nstr(v, 6) for v in g])
    print("  first strict local MIN at gap index %s; first strict local MAX after it at %s" % (m, M))
    print("  MODEL G p2 = %s" % out["model_G_p2"])
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    c = sys.argv[1]
    if c == "kat":
        sys.exit(kat())
    elif c == "recount":
        sys.exit(recount())
    elif c == "spec":
        sys.exit(spec(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])))
    elif c == "nodes":
        sys.exit(nodes(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])))
    elif c == "gpred":
        sys.exit(gpred(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])))
    else:
        raise SystemExit(__doc__)
