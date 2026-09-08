#!/usr/bin/env python3
"""m2_c51_nodes.py -- cycle 51's REGISTERED nodal instrument.

WHY THIS FILE EXISTS
--------------------
c50 shipped, as an UNREGISTERED EXPLORATORY arm, the most quotable sentence in its letter: "the
nodal ladder is EXACT for five rungs, then dislocates by exactly +2". It was measured at ONE window
(x=13, N=100, dps=150) and scored nothing. Cycle 51 registers it and tests it at windows that did
not produce it, with an ABSOLUTE refutation test (integer equality, tolerance 0) that is decided
independently of any model comparison (c50's law: model selection by relative fit is not model
validation -- A beat B by 3-6x and was still wrong).

WHAT IS COPIED AND WHAT IS NEW
------------------------------
`block_with_vectors` and `sample_and_count` are VERBATIM copies of c50's v2 routines (commit
3ea026b, data/c50/m2_c50_nodes.py). They are copied rather than imported so that this cycle's
instrument is a single sealed file, and rather than EDITED so that c50's registered artefact is
untouched (c49's rule: ship a new script, never edit the registered one). The copy is PROVED to be
a copy by the P0 gate below, which re-counts c50's published coefficient arrays and must return
c50's published integers exactly.

NEW HERE:
  * reference-cell lookup across data/c46 and data/c50 at ANY k (c50's version demanded an
    identical-k cell and refused otherwise, which is why it could only ever run at one window);
  * the residual computed HERE from my own Ritz vectors, so the admission rule (c50: relative Ritz
    residual < 1e-20) is applied by measurement inside this instrument;
  * `kat` -- the node detector KAT'd against SEALED INTEGERS (see below);
  * `recount` -- the P0 reproduction gate;
  * the Sturm baseline and the defect delta, computed and stored per SECTOR rung.

THEOREM T (proved in the prereg, KAT'd here, NOT registered as a prediction)
---------------------------------------------------------------------------
On a symmetric window, an even eigenfunction has an EVEN number of interior sign changes and an odd
one an ODD number -- for the object (pairing t <-> -t) and for this detector (the grid is symmetric
and, for odd npts, contains t=0, where an odd function is exactly 0 and is filtered out by the
significance cut). Therefore node-count parity is FORCED by the sector and carries no information
about the operator. Registering "every dislocation is even" as a prediction would be a corollary
used as a test (the c33/c49/c50 defect). It is an instrument KAT here instead: if it ever fails,
the detector is broken.

THE DETECTOR'S BLIND SPOT IS MEASURED, NOT ASSERTED
---------------------------------------------------
c50 reported node counts "stable across nine knob settings". A stability sweep measures
reproducibility, NOT resolving power: a lobe that every setting misses is stably missed. K2 plants
lobes of known, shrinking amplitude (phi = cos(w_9 t) + c, true interior node count 18 for every
c < 1, analytically, sealed) and measures the c at which each knob setting loses them. That is the
frontier the sweep cannot see.

usage:
  m2_c51_nodes.py kat                                 detector KAT vs sealed integers -> m2_c51_kat.json
  m2_c51_nodes.py recount                             P0 gate: re-count c50's published coefficients
  m2_c51_nodes.py run PARITY X N DPS GLDEG ITERS K    one cell -> m2_c51_nodes_PARITY_xX_NN_kK.json
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))


def _find_dir(name):
    """resolve relative to THIS file: working-tree layout first, committed data/<cycle> layout
    second (m1-L191 finding (c); c50's addendum 2). No absolute clone path anywhere."""
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


for _d in ("c42", "code", "c46"):
    sys.path.insert(0, _find_dir(_d))
from mpmath import mp, mpf, sqrt, cos, sin, pi, log
import c46_parity as P

C46 = _find_dir("c46")
C50 = _find_dir("c50")

# ---------------------------------------------------------------- sealed constants of the cycle
ADMIT_REL_RESID = mpf("1e-20")          # c50's admission rule, applied here by measurement
GRIDS = (1201, 4001, 12001)
TOLS = (mpf(0), mpf("1e-8"), mpf("1e-4"))
SELFTEST_MIN_SF = 30                    # c50's gate; the CEILING is the published print width (40 s.f.)


def sturm(parity, m):
    """the Sturm-Liouville baseline node count for sector rung m (1-based)."""
    return 2 * (m - 1) if parity == "even" else 2 * m - 1


# ---------------------------------------------------------------- VERBATIM from c50 (3ea026b)
def block_with_vectors(M, k, iters):
    """same block inverse iteration + Rayleigh-Ritz as c46_parity.smallest_block, but the Ritz
    VECTORS are kept.  Deliberately the same starting block and the same loop so that the
    eigenvalues are comparable to the sealed instrument's digit for digit."""
    n = len(M)
    A = mp.matrix(M)
    V = mp.matrix(n, k)
    for i in range(n):
        for j in range(k):
            V[i, j] = mpf(1) / (1 + ((i * (j + 3) + j) % 7)) + mpf(j + 1) / (n + i + 1)

    def orth(V):
        for j in range(k):
            for i in range(j):
                c = sum(V[r, i] * V[r, j] for r in range(n))
                for r in range(n):
                    V[r, j] -= c * V[r, i]
            nr_ = sqrt(sum(V[r, j] ** 2 for r in range(n)))
            for r in range(n):
                V[r, j] /= nr_
        return V

    V = orth(V)
    lams = None
    for _ in range(iters):
        W = mp.matrix(n, k)
        for j in range(k):
            col = mp.lu_solve(A, mp.matrix([V[r, j] for r in range(n)]))
            for r in range(n):
                W[r, j] = col[r]
        V = orth(W)
        B = mp.matrix(k, k)
        AV = A * V
        for i in range(k):
            for j in range(k):
                B[i, j] = sum(V[r, i] * AV[r, j] for r in range(n))
        for i in range(k):
            for j in range(i):
                B[i, j] = B[j, i] = (B[i, j] + B[j, i]) / 2
        E, Q = mp.eigsy(B)
        V = V * Q
        lams = [E[i] for i in range(k)]
    return lams, V


def sample_and_count(coef, om, nr, L, parity, npts, tol):
    """phi(t) = sum_a coef[a]*nr[a]*{cos,sin}(om[a] t) on (-L/2, L/2), sampled on a uniform interior
    grid; count sign changes among the samples whose magnitude exceeds tol*max|phi| on the grid.
    VERBATIM c50 v2 (the version that filters on significance instead of skipping exact zeros --
    a detector that skips its own zeros is blind exactly at the thing it counts)."""
    half = L / 2
    vals = []
    for i in range(npts):
        t = -half + (2 * half) * mpf(i + 1) / (npts + 1)
        s = mpf(0)
        for a in range(len(om)):
            s += coef[a] * nr[a] * (cos(om[a] * t) if parity == "even" else sin(om[a] * t))
        vals.append(s)
    mx = max(abs(v) for v in vals)
    cut = tol * mx
    cur, ch = 0, 0
    for v in vals:
        if abs(v) <= cut:
            continue
        sg = 1 if v > 0 else -1
        if cur != 0 and sg != cur:
            ch += 1
        cur = sg
    return ch


def sample_values(coef, om, nr, L, parity, npts):
    """NEW in c51 (not part of the verbatim copy): the same sampling, but the VALUES are returned so
    the lobe amplitudes can be measured. Used only by the REFINE pass."""
    half = L / 2
    vals = []
    for i in range(npts):
        t = -half + (2 * half) * mpf(i + 1) / (npts + 1)
        s = mpf(0)
        for a in range(len(om)):
            s += coef[a] * nr[a] * (cos(om[a] * t) if parity == "even" else sin(om[a] * t))
        vals.append(s)
    return vals


def refine(coef, om, nr, L, parity, npts=48001):
    """REFINE pass: one grid 4x finer than the finest published knob, at tol=0, plus the MINIMUM
    LOBE AMPLITUDE actually detected (as a ratio to max|phi|).

    WHY: c50 reported node counts 'stable across nine knob settings'. A stability sweep measures
    reproducibility, not resolving power -- K2 in this file's KAT shows all three tol settings at
    grid 1201 returning a stably WRONG 0 for a function whose true count is 18. The refine count is
    a falsifiable instrument prediction (it must equal the 9-knob count) and the lobe ratio says how
    far the detected lobes sit above the KAT's measured blind-spot frontier. It bounds the lobes we
    DID see; it cannot bound a lobe nobody saw, and is reported as such."""
    vals = sample_values(coef, om, nr, L, parity, npts)
    mx = max(abs(v) for v in vals)
    cur, ch, run_max, mins = 0, 0, mpf(0), []
    for v in vals:
        sg = 1 if v > 0 else (-1 if v < 0 else 0)
        if sg == 0:
            continue
        if cur != 0 and sg != cur:
            ch += 1
            mins.append(run_max)
            run_max = mpf(0)
        cur = sg
        if abs(v) > run_max:
            run_max = abs(v)
    mins.append(run_max)
    return ch, (min(mins) / mx if mins else None)


# ---------------------------------------------------------------- new: reference-cell lookup
def find_reference(parity, X, N, DPS, GL, IT, K):
    """the published block cell for this window at the LARGEST available k (any k, not only K).
    Returns (path, [lam strings]) or (None, None)."""
    best = None
    for d in (C46, C50):
        for kk in range(1, 13):
            fn = os.path.join(d, "c46_block_%s_x%d_N%d_dps%d_g%d_it%d_k%d.json"
                              % (parity, X, N, DPS, GL, IT, kk))
            if os.path.exists(fn) and (best is None or kk > best[0]):
                best = (kk, fn)
    if best is None:
        return None, None
    return best[1], [r["lam"] for r in json.load(open(best[1]))["ritz"]]


def agree_sf(a, b, ceiling):
    """agreeing significant figures, CEILING-LIMITED by the narrower party's print width (c37/c47:
    an agreement depth reads the narrower party's print, and must be stated as a ceiling)."""
    if a == b:
        return mpf(ceiling)
    return min(mpf(ceiling), -mp.log(abs(a - b) / abs(a), 10))


def count_all_knobs(coef, om, nr, L, parity):
    counts = {}
    for g in GRIDS:
        for t in TOLS:
            counts["%d_%s" % (g, mp.nstr(t, 2))] = sample_and_count(coef, om, nr, L, parity, g, t)
    vals = list(counts.values())
    return counts, (len(set(vals)) == 1), (vals[0] if len(set(vals)) == 1 else None)


# ---------------------------------------------------------------- KAT
def kat():
    """the detector against SEALED INTEGERS.

    K1 even basis  : phi = cos(w_j t), interior zeros t = L(2m+1)/(4j) -> exactly 2j sign changes.
    K1 odd  basis  : phi = sin(w_j t), interior zeros t = mL/(2j), |m| < j -> exactly 2j-1.
    K2 planted lobe: phi = cos(w_9 t) + c, 0 < c < 1 -> the 9 negative lobes survive, exactly 18
                     interior sign changes for EVERY such c; the lobe DEPTH is (1-c) against a
                     maximum of (1+c), so c sweeps the detector's amplitude resolution.
    K3 parity      : Theorem T -- even count even, odd count odd, at every knob. A failure here is
                     an instrument failure, never a finding about the operator.
    """
    mp.dps = 50
    L = log(13)                       # any symmetric window; this is the x=13 window's L = ln x
    N = 12                            # the detector does not see N; 12 keeps the KAT ~2 min
    ome, nre, _ = P.make_basis_parity(N, L, "even")
    omo, nro, _ = P.make_basis_parity(N, L, "odd")
    rows, fails = [], 0

    for j in range(1, 7):
        ce = [mpf(1) if a == j else mpf(0) for a in range(len(ome))]
        counts, stable, nu = count_all_knobs(ce, ome, nre, L, "even")
        exp = 2 * j
        ok = stable and nu == exp
        fails += 0 if ok else 1
        rows.append(dict(kat="K1-even-j%d" % j, expected=exp, got=nu, stable=stable,
                         counts=counts, pass_=ok,
                         parity_ok=all(v % 2 == 0 for v in counts.values())))
        co = [mpf(1) if a == j - 1 else mpf(0) for a in range(len(omo))]   # odd basis starts at j=1
        counts, stable, nu = count_all_knobs(co, omo, nro, L, "odd")
        exp = 2 * j - 1
        ok = stable and nu == exp
        fails += 0 if ok else 1
        rows.append(dict(kat="K1-odd-j%d" % j, expected=exp, got=nu, stable=stable,
                         counts=counts, pass_=ok,
                         parity_ok=all(v % 2 == 1 for v in counts.values())))

    for cs in ("0.9", "0.99", "0.999", "0.9999", "0.99999"):
        c = mpf(cs)
        ce = [mpf(0)] * len(ome)
        ce[9] = mpf(1) / nre[9]                # cos(w_9 t)
        ce[0] = c / nre[0]                     # + c
        counts, stable, nu = count_all_knobs(ce, ome, nre, L, "even")
        rows.append(dict(kat="K2-planted-c%s" % cs, expected=18, got=nu, stable=stable,
                         counts=counts, pass_=(stable and nu == 18),
                         parity_ok=all(v % 2 == 0 for v in counts.values()),
                         lobe_depth_ratio=mp.nstr((1 - c) / (1 + c), 6)))
        # K2 is a MEASUREMENT of the frontier, not a gate: it is expected to fail at small enough
        # (1-c). Its failures are counted separately and reported as the blind spot.

    parity_fails = sum(0 if r["parity_ok"] else 1 for r in rows)
    k2 = [r for r in rows if r["kat"].startswith("K2")]
    out = dict(rows=rows, k1_fails=fails, parity_fails_T=parity_fails,
               k2_frontier={r["kat"]: {"got": r["got"], "counts": r["counts"]} for r in k2},
               verdict=("PASS" if (fails == 0 and parity_fails == 0) else "FAIL"))
    json.dump(out, open(os.path.join(HERE, "m2_c51_kat.json"), "w"), indent=1)
    for r in rows:
        print("  %-20s expected=%-3s got=%-5s stable=%-5s parityT=%-5s %s"
              % (r["kat"], r["expected"], r["got"], r["stable"], r["parity_ok"],
                 "PASS" if r["pass_"] else "MISS"))
    print("K1 fails (gate): %d   Theorem-T parity fails (gate): %d   verdict %s"
          % (fails, parity_fails, out["verdict"]))
    return 0 if out["verdict"] == "PASS" else 1


# ---------------------------------------------------------------- P0 reproduction gate
def recount():
    """P0: re-count node numbers from c50's PUBLISHED coefficient arrays (data/c50/m2_c50_nodes_*.json)
    with this file's detector. Must return c50's published integers at all 9 knob settings, both
    parities, 5 rungs -> 90 comparisons. Any mismatch = GATE FAIL."""
    mp.dps = 50
    N, X = 100, 13
    L = log(X)
    tot = ok = 0
    rows = []
    for par in ("even", "odd"):
        src = os.path.join(C50, "m2_c50_nodes_%s_x13_N100.json" % par)
        d = json.load(open(src))
        om, nr, _ = P.make_basis_parity(N, mpf(d["L"]), par)
        for rung in d["rungs"]:
            coef = [mpf(c) for c in rung["coef"]]
            counts, stable, nu = count_all_knobs(coef, om, nr, mpf(d["L"]), par)
            for kk, v in sorted(rung["counts"].items()):
                tot += 1
                ok += 1 if counts[kk] == v else 0
            rows.append(dict(parity=par, rung=rung["rung"], published=rung["counts"],
                             recounted=counts, stable=stable, nu=nu))
            print("  %-4s rung %d  published nu=%s  recounted nu=%s  %s"
                  % (par, rung["rung"], sorted(set(rung["counts"].values())), nu,
                     "OK" if all(counts[k2] == v2 for k2, v2 in rung["counts"].items()) else "MISMATCH"))
    verdict = "PASS" if ok == tot else "FAIL"
    json.dump(dict(compared=tot, matched=ok, verdict=verdict, rows=rows,
                   note="P0 reproduction gate: c50's published coefficients, c51's detector"),
              open(os.path.join(HERE, "m2_c51_p0_recount.json"), "w"), indent=1)
    print("P0 GATE: %d/%d integers reproduced -> %s" % (ok, tot, verdict))
    return 0 if verdict == "PASS" else 1


# ---------------------------------------------------------------- one cell
def run(par, X, N, DPS, GL, IT, K):
    mp.dps = DPS
    t0 = time.time()
    M, L, _ = P.build_matrix_parity(N, X, GL, par)
    lams, V = block_with_vectors(M, K, IT)
    om, nr, idx = P.make_basis_parity(N, L, par)
    dim = len(om)

    # ---- self-test against the published cell (any k), CEILING-LIMITED by its print width
    ref, refl = find_reference(par, X, N, DPS, GL, IT, K)
    if ref is None:
        print("SELF-TEST: no reference cell for this window -> nothing reported.")
        return 1
    ceiling = max(len(s.split("e")[0].replace("-", "").replace(".", "").lstrip("0")) for s in refl)
    depths = []
    for i in range(min(K, len(refl))):
        depths.append(agree_sf(lams[i], mpf(refl[i]), ceiling))
    st_ok = all(d >= SELFTEST_MIN_SF for d in depths)
    print("SELF-TEST vs %s: depths %s (CEILING %d s.f. = the published print width) -> %s"
          % (os.path.basename(ref), [mp.nstr(d, 4) for d in depths], ceiling,
             "PASS" if st_ok else "FAIL"), flush=True)
    if not st_ok:
        print("SELF-TEST FAILED -- nothing reported.")
        return 1

    # ---- residuals from MY OWN vectors, so the admission rule is applied by measurement here
    A = mp.matrix(M)
    resid = []
    for j in range(K):
        v = mp.matrix([V[r, j] for r in range(dim)])
        w = A * v - lams[j] * v
        resid.append(sqrt(sum(w[r] ** 2 for r in range(dim))))

    mp.dps = 50
    out = []
    for j in range(K):
        coef = [V[r, j] for r in range(dim)]
        counts, stable, nu = count_all_knobs(coef, om, nr, L, par)
        nu_ref, lobe = refine(coef, om, nr, L, par)
        rel = resid[j] / abs(lams[j])
        adm = rel < ADMIT_REL_RESID
        st = sturm(par, j + 1)
        out.append(dict(rung=j + 1, lam=mp.nstr(lams[j], 40), log10=mp.nstr(mp.log(lams[j], 10), 20),
                        residual=mp.nstr(resid[j], 10), rel_residual=mp.nstr(rel, 10),
                        admitted=bool(adm), counts=counts, stable=stable, nu=nu,
                        nu_refine_48001=nu_ref,
                        lobe_min_ratio=(None if lobe is None else mp.nstr(lobe, 6)),
                        sturm=st, delta=(None if nu is None else nu - st),
                        parity_T_ok=(None if nu is None else (nu % 2 == (0 if par == "even" else 1))),
                        coef=[mp.nstr(c, 40) for c in coef]))
        print("  %-4s rung %d  log10lam=%s  rel_resid=%s  admitted=%s  nu=%s  refine48001=%s  "
              "lobe_min=%s  sturm=%d  delta=%s  stable=%s"
              % (par, j + 1, mp.nstr(mp.log(lams[j], 10), 12), mp.nstr(rel, 4), adm, nu, nu_ref,
                 (None if lobe is None else mp.nstr(lobe, 4)), st,
                 (None if nu is None else nu - st), stable), flush=True)

    res = dict(parity=par, x=X, N=N, dps=DPS, k=K, gl=GL, iters=IT, L=mp.nstr(L, 40),
               reference=os.path.basename(ref), selftest_depths=[mp.nstr(d, 6) for d in depths],
               selftest_ceiling_sf=ceiling, admit_rule="rel Ritz residual < 1e-20 (c50)",
               rungs=out, seconds=time.time() - t0,
               label="REGISTERED (cycle 51 prereg P1-P6)")
    fn = os.path.join(HERE, "m2_c51_nodes_%s_x%d_N%d_k%d.json" % (par, X, N, K))
    json.dump(res, open(fn, "w"), indent=1)
    print("wrote %s  %.1fs" % (os.path.basename(fn), res["seconds"]), flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]
    if cmd == "kat":
        sys.exit(kat())
    elif cmd == "recount":
        sys.exit(recount())
    elif cmd == "run":
        sys.exit(run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
                     int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8])))
    else:
        raise SystemExit(__doc__)
