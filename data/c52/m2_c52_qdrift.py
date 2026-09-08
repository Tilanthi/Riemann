#!/usr/bin/env python3
"""m2_c52_qdrift.py -- cycle 52's ANALYSIS instrument for the x-drift of q_1.

MEASURING instrument  : data/c46/c46_parity.py `block`, UNMODIFIED (sha256 in the prereg seal).
POOLING instrument    : data/c50/m2_c50_ladder.py `load_block` + `pool`, IMPORTED UNMODIFIED.
                        Cycle 50 published and sealed those conventions; re-typing them here would
                        create a second definition of gap_j/q_j that could silently diverge from
                        the one the published numbers were made with.  So they are imported, and
                        arm P0 proves the import reproduces c50's PUBLISHED numbers.

Everything NEW in this file is: the exact zero counter n(x), the per-x table, the N-covariate
S_N(x), the two fit-free axis discriminators, the isoresolution comparison, the three registered
rate families, and the two permutation nulls.

usage:
  m2_c52_qdrift.py --kat                              KATs + external ground truth (no target output)
  m2_c52_qdrift.py --score --cells DIR [--json OUT]   the registered scoring run
"""
import argparse, glob, json, os, random, sys
from mpmath import mp, mpf, log, exp

HERE = os.path.dirname(os.path.abspath(__file__))
mp.dps = 60


def _repo():
    for cand in (os.path.join(HERE, "repo", "Riemann"), "/shared/rh-exchange-repo/Riemann"):
        if os.path.isdir(os.path.join(cand, "data", "c50")):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate the Riemann checkout (tried ./repo/Riemann and the shared clone)")


REPO = _repo()
sys.path.insert(0, os.path.join(REPO, "data", "c50"))
import m2_c50_ladder as C50           # noqa: E402  -- imported UNMODIFIED, see docstring

# ---------------------------------------------------------------- the exact zero counter
# n(x) := #{gamma > 0 : gamma <= 2 pi x}, the convention NAMED in data/c46/c46_analyse.py.
# EXTERNAL GROUND TRUTH (V5): m1's exact counts are 21 / 32 / 38 / 56 at x = 13 / 17 / 19 / 25,
# and c46_analyse.py's comment lists the first five ordinates as
# 14.1347, 21.0220, 25.0109, 30.4249, 32.9351.  --kat checks this counter against BOTH.
_ZC = None


def _zeros(m=70):
    global _ZC
    if _ZC is None or len(_ZC) < m:
        with mp.workdps(30):
            _ZC = [mp.im(mp.zetazero(k)) for k in range(1, m + 1)]
    return _ZC


def nzero(xs):
    T = 2 * mp.pi * mpf(str(xs))
    zs = _zeros()
    c = sum(1 for z in zs if z <= T)
    if c == len(zs):
        raise SystemExit("zero cache too small for x=%s" % xs)
    return c


# ---------------------------------------------------------------- cell loading
def load_pair(cellsdir, par_pattern, xs, N, dps, k=3):
    fe = os.path.join(cellsdir, "c46_block_even_x%s_N%d_dps%d_g9_it16_k%d.json"
                      % (xs.replace(".", "p"), N, dps, k))
    fo = fe.replace("_even_", "_odd_")
    if not (os.path.exists(fe) and os.path.exists(fo)):
        return None
    return C50.pool(C50.load_block(fe), C50.load_block(fo))


def q1_of(p):
    """q_1 = gap_2/gap_1, reported ONLY if the pooled prefix carrying it is certified and admitted."""
    if p is None or len(p["q"]) < 1 or p["q"][0] is None:
        return None
    if p["certified"] < 3:
        return None
    return p["q"][0]


# ---------------------------------------------------------------- registered families
def fit_power(us, ys):
    """least squares of ln y on ln u : y = A u^(-beta).  Returns (lnA, beta)."""
    lu = [log(u) for u in us]
    ly = [log(y) for y in ys]
    m = len(us)
    mu = sum(lu) / m
    my = sum(ly) / m
    num = sum((lu[i] - mu) * (ly[i] - my) for i in range(m))
    den = sum((lu[i] - mu) ** 2 for i in range(m))
    slope = num / den
    return my - slope * mu, -slope          # y = exp(lnA) * u^slope ; beta = -slope


def predict_power(par, u):
    lnA, beta = par
    return exp(lnA) * u ** (-beta)


# ---------------------------------------------------------------- KAT
def kat():
    fails = []
    print("=" * 100)
    print("c52 KAT -- the pooling import, the zero counter against EXTERNAL ground truth, and the fitter")
    print("=" * 100)

    # K0: c50's own self-test, run through THIS file's import, on the published c46 cells.
    rc = C50.self_test(os.path.join(REPO, "data", "c46"))
    print("K0 c50 ladder self-test through this import           : %s" % ("PASS" if rc == 0 else "FAIL"))
    if rc:
        fails.append("K0")

    # K1: EXTERNAL ground truth for the NEW instrument (the zero counter).  m1's exact counts.
    ext = {"13": 21, "17": 32, "19": 38, "25": 56}
    got = {x: nzero(x) for x in ext}
    ok = (got == ext)
    print("K1 n(x) vs m1's EXACT counts 21/32/38/56 at 13/17/19/25: got %s -> %s"
          % ([got[x] for x in ("13", "17", "19", "25")], "PASS" if ok else "FAIL"))
    if not ok:
        fails.append("K1")

    # K1b: the first five ordinates as printed in c46_analyse.py's comment
    pub = ["14.1347", "21.0220", "25.0109", "30.4249", "32.9351"]
    gotz = [mp.nstr(z, 6) for z in _zeros()[:5]]
    ok = all(g.startswith(p[:7].rstrip("0")) or abs(mpf(g) - mpf(p)) < mpf("1e-4")
             for g, p in zip(gotz, pub))
    print("K1b first five ordinates vs c46_analyse's comment      : %s -> %s"
          % (gotz, "PASS" if ok else "FAIL"))
    if not ok:
        fails.append("K1b")

    # K1c: the counter must be a STEP function -- x=4 and x=4.82 must share n, x=4.82 and x=4.86 must not.
    ok = (nzero("4") == nzero("4.82") == 3) and (nzero("4.86") == nzero("5") == nzero("5.23") == 4)
    print("K1c same-n blocks: n(4)=n(4.82)=3, n(4.86)=n(5)=n(5.23)=4 : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("K1c")

    # K2: the fitter on a KNOWN answer -- exact power law must be recovered to working precision.
    us = [mpf(2), mpf(5), mpf(11)]
    ys = [mpf(3) * u ** (-mpf("0.7")) for u in us]
    lnA, beta = fit_power(us, ys)
    ok = abs(exp(lnA) - 3) < mpf("1e-40") and abs(beta - mpf("0.7")) < mpf("1e-40")
    print("K2 fitter recovers y = 3 u^-0.7 exactly               : A=%s beta=%s -> %s"
          % (mp.nstr(exp(lnA), 10), mp.nstr(beta, 10), "PASS" if ok else "FAIL"))
    if not ok:
        fails.append("K2")

    # K2b: a fit is not a test.  Planted NON-power data must produce residuals the scorer sees.
    ys2 = [mpf("0.5"), mpf("0.4"), mpf("0.39")]
    par = fit_power(us, ys2)
    res = [abs(predict_power(par, u) - y) for u, y in zip(us, ys2)]
    ok = max(res) > mpf("1e-3")
    print("K2b planted non-power data leaves visible residuals   : max %s -> %s"
          % (mp.nstr(max(res), 5), "PASS" if ok else "FAIL"))
    if not ok:
        fails.append("K2b")

    # K3: the permutation null on a KNOWN answer.  A perfectly monotone sequence of m distinct
    # values has exactly one increasing label assignment, so p = 1/m!.
    ok = (perm_p_monotone(5) == mpf(1) / 120)
    print("K3 permutation null of a monotone m=5 sequence = 1/120 : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("K3")

    print("KAT RESULT: %d fail(s)%s" % (len(fails), (" " + ",".join(fails)) if fails else ""))
    return 1 if fails else 0


def perm_p_monotone(m):
    """exact p-value that a random assignment of m distinct values to m ordered labels is
    strictly increasing: 1/m!."""
    f = mpf(1)
    for i in range(2, m + 1):
        f *= i
    return 1 / f


# ---------------------------------------------------------------- scoring
def score(cellsdir, jsonout=None):
    ns = mp.nstr
    sys.path.insert(0, HERE)
    import m2_c52_grid as G
    out = dict(cells_dir=cellsdir, xgrid=G.XGRID, planned=len(G.cells()), rows=[], verdicts={})

    # ---- the measured table ------------------------------------------------------------------
    table = {}                      # (xs, N) -> dict
    for xs in G.XGRID:
        for N in sorted({60, 100, G.n_iso(xs)}):
            p = load_pair(cellsdir, None, xs, N, G.DPS)
            if p is None:
                continue
            q = q1_of(p)
            table[(xs, N)] = dict(x=xs, N=N, n=nzero(xs), L=log(mpf(xs)),
                                  q1=q, order=p["order"], certified=p["certified"],
                                  dropped=p["dropped"], alternates=p["alternates"],
                                  min_gap=p["min_gap"], iso=(N == G.n_iso(xs)))
    completed = len(table)
    out["completed_pairs"] = completed
    out["planned_pairs"] = sum(len(sorted({60, 100, G.n_iso(x)})) for x in G.XGRID)

    print("=" * 118)
    print("c52 -- q_1 = gap_2/gap_1 of the pooled parity ladder, per (x, N).  dps=300, gl=9, it=16, k=3 everywhere.")
    print("=" * 118)
    print("%-6s %5s %4s %8s  %-18s %-9s %4s %4s  %s"
          % ("x", "N", "n", "L", "q_1", "order", "cert", "drop", "note"))
    for key in sorted(table, key=lambda t: (float(t[0]), t[1])):
        r = table[key]
        note = "ISO" if r["iso"] else ""
        if r["q1"] is None:
            note += " q_1 WITHHELD (certified prefix < 3)"
        print("%-6s %5d %4d %8s  %-18s %-9s %4d %4d  %s"
              % (r["x"], r["N"], r["n"], ns(r["L"], 6),
                 ns(r["q1"], 12) if r["q1"] is not None else "-",
                 r["order"], r["certified"], r["dropped"], note))
        out["rows"].append(dict(x=r["x"], N=r["N"], n=r["n"], L=ns(r["L"], 20),
                                q1=(ns(r["q1"], 20) if r["q1"] is not None else None),
                                order=r["order"], certified=r["certified"],
                                dropped=r["dropped"], iso=r["iso"]))

    def q(xs, N):
        t = table.get((xs, N))
        return t["q1"] if t else None

    # ---- P0: the pooling import reproduces c50's PUBLISHED numbers -----------------------------
    print("\n--- P0  the pooling import vs c50's PUBLISHED q_1 (external ground truth for the analysis) ---")
    PUB = {"5": "0.889256615305", "13": "0.9206571015", "19": "0.931062954"}
    c50dir = os.path.join(REPO, "data", "c50")
    p0 = {}
    p0fail = 0
    for xs, pub in PUB.items():
        dps = 300 if xs == "19" else 150
        k = 5 if xs in ("5", "13") else 3
        pp = load_pair(c50dir, None, xs, 100, dps, k=k)
        gotq = q1_of(pp)
        agree = gotq is not None and ns(gotq, len(pub.replace("0.", ""))) == pub
        p0[xs] = dict(published=pub, got=(ns(gotq, 20) if gotq is not None else None), agree=bool(agree))
        print("  x=%-3s published q_1 = %-15s recomputed = %-22s %s"
              % (xs, pub, ns(gotq, 15) if gotq is not None else "-", "AGREE" if agree else "DISAGREE"))
        if not agree:
            p0fail += 1
    out["verdicts"]["P0"] = dict(fails=p0fail, detail=p0, held=(p0fail == 0))

    # ---- P1: alternation + certification at every completed (x,N) ------------------------------
    bad = [k for k, r in table.items() if not (r["certified"] >= 3 and
                                               r["order"][:3] == "eoe")]
    out["verdicts"]["P1"] = dict(checked=len(table), failed=len(bad),
                                 failing=[[k[0], k[1]] for k in sorted(bad)],
                                 held=(len(bad) == 0))
    print("\n--- P1  certified prefix >= 3 and pooled order starts 'eoe' : %d of %d cells fail"
          % (len(bad), len(table)))

    # ---- S_N: the N covariate (correction C1) --------------------------------------------------
    print("\n--- S_N(x) = q_1(x,100) - q_1(x,60): the N-control AT EACH x, used as a COVARIATE ---")
    SN = {}
    for xs in G.XGRID:
        a, b = q(xs, 100), q(xs, 60)
        if a is not None and b is not None:
            SN[xs] = a - b
            print("  x=%-6s S_N = %-16s  (|S_N| = %s)" % (xs, ns(SN[xs], 8), ns(abs(SN[xs]), 8)))
        else:
            print("  x=%-6s S_N = UNMEASURED (missing N=60 or N=100 cell)" % xs)
    out["S_N"] = {k: ns(v, 20) for k, v in SN.items()}

    q100 = {xs: q(xs, 100) for xs in G.XGRID if q(xs, 100) is not None}
    R = (max(q100.values()) - min(q100.values())) if len(q100) >= 2 else None
    out["range_q1_N100"] = ns(R, 20) if R is not None else None
    print("  range R of q_1 over the completed N=100 grid          : %s" % (ns(R, 10) if R else "-"))

    # ---- P5: is the drift bigger than the truncation sensitivity, PER x? -----------------------
    print("\n--- P5  per-x confound verdict: CONFOUNDED if |S_N(x)| > R/3 ---")
    p5 = {}
    for xs in G.XGRID:
        if xs not in SN or R is None:
            p5[xs] = "UNMEASURED"
        else:
            p5[xs] = "CONFOUNDED" if abs(SN[xs]) > R / 3 else "CLEAN"
        print("  x=%-6s %s" % (xs, p5[xs]))
    out["verdicts"]["P5"] = p5

    # ---- P2: monotone x-drift at fixed N=100, + permutation null -------------------------------
    print("\n--- P2  strict monotone increase of q_1 in x at fixed N=100 ---")
    for tag, xs_list in (("P2a all-12", G.XGRID),
                         ("P2b coarse-9", ["4", "5", "7", "9", "11", "13", "16", "19", "23"])):
        vals = [(xs, q(xs, 100)) for xs in xs_list if q(xs, 100) is not None]
        mono = all(vals[i + 1][1] > vals[i][1] for i in range(len(vals) - 1))
        pval = perm_p_monotone(len(vals)) if len(vals) >= 2 else None
        print("  %-12s m=%2d  strictly increasing: %-5s   permutation null p = 1/%d! = %s"
              % (tag, len(vals), mono, len(vals), ns(pval, 4) if pval else "-"))
        viol = [(vals[i][0], vals[i + 1][0]) for i in range(len(vals) - 1)
                if not vals[i + 1][1] > vals[i][1]]
        if viol:
            print("      violating consecutive pairs: %s" % viol)
        out["verdicts"][tag.split()[0]] = dict(m=len(vals), monotone=bool(mono),
                                               perm_p=(ns(pval, 6) if pval else None),
                                               violations=viol)

    # ---- P3: the FIT-FREE axis discriminators --------------------------------------------------
    print("\n--- P3  the axis, with ZERO fitted parameters ---")
    print("  a pure-n law says q_1 is a function of n alone; a pure-x/L law says it is smooth in x.")
    p3 = {}
    for tag, pairs, kind in (
            ("P3a-n3", [("4", "4.82")], "same n=3, x moves 20.5%"),
            ("P3a-n4", [("4.86", "5"), ("5", "5.23"), ("4.86", "5.23")], "same n=4, x moves up to 7.6%"),
            ("P3b", [("4.82", "4.86")], "n moves +1, x moves 0.83%")):
        for (xa, xb) in pairs:
            qa, qb = q(xa, 100), q(xb, 100)
            if qa is None or qb is None:
                print("  %-8s %s vs %s : UNMEASURED" % (tag, xa, xb))
                p3["%s:%s-%s" % (tag, xa, xb)] = "UNMEASURED"
                continue
            d = qb - qa
            band_c = 3 * max(abs(SN.get(xa, mpf(0))), abs(SN.get(xb, mpf(0))))
            band_p = 3 * abs(SN.get(xa, mpf(0)) - SN.get(xb, mpf(0)))
            print("  %-8s x=%-5s -> %-5s (%s)\n           dq_1 = %-16s conservative band %s [%s]   paired band %s [%s]"
                  % (tag, xa, xb, kind, ns(d, 8), ns(band_c, 6),
                     "EXCEEDS" if abs(d) > band_c else "inside", ns(band_p, 6),
                     "EXCEEDS" if abs(d) > band_p else "inside"))
            p3["%s:%s-%s" % (tag, xa, xb)] = dict(dq1=ns(d, 20), band_cons=ns(band_c, 12),
                                                  band_paired=ns(band_p, 12),
                                                  exceeds_cons=bool(abs(d) > band_c),
                                                  exceeds_paired=bool(abs(d) > band_p))
    out["verdicts"]["P3"] = p3

    # ---- P4: does the drift survive isoresolution? ---------------------------------------------
    print("\n--- P4  isoresolution series (N/L constant) vs fixed-N series: consecutive signs ---")
    isoq = []
    for xs in G.XGRID:
        Ni = G.n_iso(xs)
        v = q(xs, Ni)
        if v is not None:
            isoq.append((xs, v))
    fixq = [(xs, q(xs, 100)) for xs in G.XGRID if q(xs, 100) is not None]
    common = [xs for xs, _ in isoq if q(xs, 100) is not None]
    agree, dis = 0, []
    for i in range(len(common) - 1):
        xa, xb = common[i], common[i + 1]
        si = mp.sign(q(xb, G.n_iso(xb)) - q(xa, G.n_iso(xa)))
        sf = mp.sign(q(xb, 100) - q(xa, 100))
        if si == sf:
            agree += 1
        else:
            dis.append((xa, xb, str(si), str(sf)))
    print("  x with BOTH series: %d   consecutive sign agreements: %d of %d   disagreements: %s"
          % (len(common), agree, max(len(common) - 1, 0), dis if dis else "none"))
    if len(isoq) >= 2:
        print("  isoresolution q_1 range: %s -> %s (span %s)"
              % (ns(isoq[0][1], 12), ns(isoq[-1][1], 12), ns(isoq[-1][1] - isoq[0][1], 8)))
    if len(fixq) >= 2:
        print("  fixed-N=100    q_1 range: %s -> %s (span %s)"
              % (ns(fixq[0][1], 12), ns(fixq[-1][1], 12), ns(fixq[-1][1] - fixq[0][1], 8)))
    out["verdicts"]["P4"] = dict(common=len(common), agreements=agree,
                                 pairs=max(len(common) - 1, 0), disagreements=dis,
                                 iso_series=[[a, ns(b, 20)] for a, b in isoq],
                                 fixed_series=[[a, ns(b, 20)] for a, b in fixq])

    # ---- P6: the three registered rate families, calibrated on the PUBLISHED 3, applied blind ---
    print("\n--- P6  three registered families, calibrated on the 3 PUBLISHED points ONLY, applied blind ---")
    cal_x = ["5", "13", "19"]
    calq = {}
    for xs in cal_x:
        dps = 300 if xs == "19" else 150
        k = 5 if xs in ("5", "13") else 3
        pp = load_pair(c50dir, None, xs, 100, dps, k=k)
        calq[xs] = q1_of(pp)
    p6 = {}
    if all(v is not None for v in calq.values()):
        ys = [1 - calq[xs] for xs in cal_x]
        axes = dict(x=[mpf(xs) for xs in cal_x],
                    L=[log(mpf(xs)) for xs in cal_x],
                    n=[mpf(nzero(xs)) for xs in cal_x])
        for name, us in axes.items():
            par = fit_power(us, ys)
            print("  family F_%s : 1 - q_1 = %s * %s^(-%s)"
                  % (name, ns(exp(par[0]), 8), name, ns(par[1], 8)))
            rows = []
            for xs in G.XGRID:
                m = q(xs, 100)
                if m is None:
                    continue
                u = {"x": mpf(xs), "L": log(mpf(xs)), "n": mpf(nzero(xs))}[name]
                pred = 1 - predict_power(par, u)
                resid = m - pred
                band = 3 * abs(SN.get(xs, mpf(0))) if xs in SN else None
                rows.append((xs, pred, resid, band, xs in cal_x))
            print("    %-6s %-16s %-16s %-14s %-8s %s"
                  % ("x", "predicted q_1", "measured q_1", "residual", "3|S_N|", "in band?"))
            for (xs, pred, resid, band, iscal) in rows:
                print("    %-6s %-16s %-16s %-14s %-8s %s%s"
                      % (xs, ns(pred, 10), ns(q(xs, 100), 10), ns(resid, 6),
                         ns(band, 4) if band else "-",
                         ("YES" if band is not None and abs(resid) <= band else "NO"),
                         "   [calibration]" if iscal else ""))
            blind = [r for r in rows if not r[4]]
            nb = sum(1 for r in blind if r[3] is not None and abs(r[2]) <= r[3])
            signs = [int(mp.sign(r[2])) for r in blind]
            sign_changes = sum(1 for i in range(len(signs) - 1) if signs[i] * signs[i + 1] < 0)
            mono = all(blind[i + 1][2] >= blind[i][2] for i in range(len(blind) - 1)) or \
                   all(blind[i + 1][2] <= blind[i][2] for i in range(len(blind) - 1))
            ssr = sum(abs(r[2]) for r in blind)
            print("    BLIND: %d of %d inside 3|S_N| ; residual signs %s ; monotone-in-x: %s ; "
                  "sum|resid| = %s" % (nb, len(blind), "".join("+" if s > 0 else "-" for s in signs),
                                       mono, ns(ssr, 6)))
            p6[name] = dict(A=ns(exp(par[0]), 12), beta=ns(par[1], 12),
                            blind_in_band=nb, blind_total=len(blind),
                            residual_signs="".join("+" if s > 0 else "-" for s in signs),
                            sign_changes=sign_changes, monotone_residuals=bool(mono),
                            sum_abs_resid=ns(ssr, 12),
                            rows=[[r[0], ns(r[1], 20), ns(r[2], 20)] for r in rows])
    else:
        print("  calibration points unavailable -- P6 UNMEASURED")
    out["verdicts"]["P6"] = p6

    # ---- P7: permutation null for the winning family -------------------------------------------
    print("\n--- P7  label-permutation null for the best family (V5: a new feature ships with a null) ---")
    if p6:
        best = min(p6, key=lambda k: mpf(p6[k]["sum_abs_resid"]))
        rows = p6[best]["rows"]
        blind = [(xs, mpf(pred), mpf(res)) for (xs, pred, res) in rows if xs not in cal_x]
        meas = [mpf(pred) + mpf(res) for (_, pred, res) in blind]
        preds = [mpf(pred) for (_, pred, _) in blind]
        obs = sum(abs(m - p) for m, p in zip(meas, preds))
        rnd = random.Random(20260908)
        B, hits = 20000, 0
        for _ in range(B):
            sh = meas[:]
            rnd.shuffle(sh)
            if sum(abs(m - p) for m, p in zip(sh, preds)) <= obs:
                hits += 1
        pv = mpf(hits) / B
        print("  best family by sum|resid| = F_%s ; observed %s ; %d/%d random label assignments do "
              "as well or better -> p = %s" % (best, ns(obs, 8), hits, B, ns(pv, 5)))
        out["verdicts"]["P7"] = dict(best=best, observed=ns(obs, 20), draws=B, hits=hits,
                                     p=ns(pv, 8), seed=20260908)
    else:
        print("  UNMEASURED")

    print("\nDENOMINATOR: %d of %d planned (x,N) PAIRS completed; %d of %d planned CELLS present."
          % (completed, out["planned_pairs"],
             len([f for f in glob.glob(os.path.join(cellsdir, "c46_block_*_dps300_*_k3.json"))]),
             out["planned"]))
    if jsonout:
        json.dump(out, open(jsonout, "w"), indent=1)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kat", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--cells")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.kat:
        sys.exit(kat())
    if a.score:
        sys.exit(score(a.cells, a.json))
    raise SystemExit(__doc__)
