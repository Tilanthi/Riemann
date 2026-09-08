#!/usr/bin/env python3
"""m2_c50_ladder.py -- cycle 50's ANALYSIS instrument: pooled parity ladder, gaps, q, and the
A/B model residuals.  Measuring instrument is data/c46/c46_parity.py, used unmodified.

usage:
  m2_c50_ladder.py --self-test [--c46dir DIR]     arms 1,2 (and 3 if the k=5 cells exist)
  m2_c50_ladder.py --score --cells DIR --c46dir DIR [--json OUT.json]

Conventions are fixed in m2_c50_prereg.md sec 1 and are NOT re-derived here:
    gap_j = log10 lam_pooled[j+1] - log10 lam_pooled[j]
    d_1   = log10 lam_odd[1] - log10 lam_even[1]
    s_1   = log10 lam_even[2] - log10 lam_even[1]
    r_1   = d_1/s_1,   q_j = gap_{j+1}/gap_j,   and under alternation r_1 = 1/(1+q_1) exactly.
Rung admission rule (prereg P1): a rung is reported only if its RELATIVE Ritz residual < 1e-20;
dropped rungs are counted and printed even when the count is 0 (c41: print the excluded count
beside the declared count, or "correctly zero" and "broken exclusion" are the same transcript).
"""
import argparse, glob, json, os, sys
from mpmath import mp, mpf, log, pi

mp.dps = 60
RESID_RULE = mpf(10) ** (-20)
GAP_FLOOR = mpf("1.0")            # dex; below this, alternation is a near-tie (prereg P1)
Q_CAL = mpf("0.9206571015")       # model A constant, registered in the prereg
NZERO = {"4.953032424395115": 4, "5": 4, "13": 21, "19": 38}


# ------------------------------------------------------------------ models
def F(n):
    n = mpf(n)
    return 2 * pi ** 2 * n / log(n)


def modelB_gaps(n, jmax=4):
    return [(F(n + 2 * j) - F(n + 2 * j - 2)) / log(10) for j in range(1, jmax + 1)]


def modelA_q():
    return Q_CAL


# ------------------------------------------------------------------ cells
def load_block(path):
    d = json.load(open(path))
    rungs = []
    for i, r in enumerate(d["ritz"]):
        lam = mpf(r["lam"])
        res = mpf(r["residual"])
        rel = abs(res / lam) if lam != 0 else mpf("inf")
        rungs.append(dict(i=i, log10=mpf(r["log10"]), lam=lam, rel=rel, ok=(rel < RESID_RULE)))
    return dict(parity=d["parity"], x=str(d["x"]), N=d["N"], dps=d["dps"], k=d["k"],
                rungs=rungs, path=path)


def pool(even, odd):
    """merge the two admitted ladders; returns dict with order string, gaps, q, d1, s1, r1."""
    ev = [r for r in even["rungs"] if r["ok"]]
    od = [r for r in odd["rungs"] if r["ok"]]
    dropped = (len(even["rungs"]) - len(ev)) + (len(odd["rungs"]) - len(od))
    merged = sorted([(r["log10"], "e") for r in ev] + [(r["log10"], "o") for r in od],
                    key=lambda t: t[0])
    order = "".join(p for _, p in merged)
    gaps = [merged[i + 1][0] - merged[i][0] for i in range(len(merged) - 1)]
    # a zero gap makes q undefined; report None rather than raising (found by self-test arm 1d,
    # which is the whole reason the degenerate case is in the KAT)
    q = [(gaps[i + 1] / gaps[i] if gaps[i] != 0 else None) for i in range(len(gaps) - 1)]
    out = dict(order=order, gaps=gaps, q=q, dropped=dropped,
               n_even=len(ev), n_odd=len(od),
               alternates=(order == ("eo" * len(order))[:len(order)]),
               min_gap=(min(gaps) if gaps else None))
    out["near_tie"] = (out["min_gap"] is not None and out["min_gap"] < GAP_FLOOR)
    out["gaps_decreasing"] = all(gaps[i + 1] < gaps[i] for i in range(len(gaps) - 1))
    if len(ev) >= 1 and len(od) >= 1:
        out["d1"] = od[0]["log10"] - ev[0]["log10"]
    if len(ev) >= 2:
        out["s1"] = ev[1]["log10"] - ev[0]["log10"]
    if "d1" in out and "s1" in out and out["s1"] != 0:
        out["r1"] = out["d1"] / out["s1"]
    return out


# ------------------------------------------------------------------ self-tests
def self_test(c46dir, cellsdir=None):
    ns = mp.nstr
    fails = []

    # ---- arm 1: hand-computable synthetic ladders, KNOWN answers
    def synth(evlog, odlog, k=None):
        mk = lambda vals, par: dict(parity=par, x="0", N=0, dps=0, k=len(vals),
                                    rungs=[dict(i=i, log10=mpf(v), lam=mpf(10) ** mpf(v),
                                                rel=mpf("1e-30"), ok=True)
                                           for i, v in enumerate(vals)], path="<synth>")
        return mk(evlog, "even"), mk(odlog, "odd")

    e, o = synth(["-10", "-6", "-3"], ["-8", "-4.5", "-2"])
    p = pool(e, o)
    # pooled: -10 e, -8 o, -6 e, -4.5 o, -3 e, -2 o ; gaps 2,2,1.5,1.5,1 ; q = 1,0.75,1,0.6667
    ok = (p["order"] == "eoeoeo" and p["alternates"] and
          [ns(g, 6) for g in p["gaps"]] == ["2.0", "2.0", "1.5", "1.5", "1.0"] and
          ns(p["d1"], 6) == "2.0" and ns(p["s1"], 6) == "4.0" and ns(p["r1"], 6) == "0.5" and
          not p["gaps_decreasing"] and not p["near_tie"])
    print("arm1a synthetic alternating ladder, known answer      : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm1a")
        print("      got", p["order"], [ns(g, 6) for g in p["gaps"]], ns(p.get("r1", 0), 6))
    # identity r1 == 1/(1+q1)
    # the EXACT identity is gap_1 + gap_2 == s_1 (a subtraction identity); r_1 == 1/(1+q_1)
    # follows but is computed through two divisions and is exact only to the working precision --
    # self-test arm 2b caught me asserting == 0 on it against real cells (7.8e-62 at dps=60)
    ok = ((p["gaps"][0] + p["gaps"][1] - p["s1"]) == 0 and
          abs(p["r1"] - 1 / (1 + p["q"][0])) < mpf(10) ** (-55))
    print("arm1b identity gap1+gap2==s1 exact, r_1==1/(1+q_1)    : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm1b")
    # deliberately NON-alternating input must be reported as non-alternating
    e, o = synth(["-10", "-9"], ["-3", "-2"])
    p = pool(e, o)
    ok = (p["order"] == "eeoo" and not p["alternates"])
    print("arm1c non-alternating input reported as such          : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm1c")
    # near-tie / degenerate: equal values must not be silently ordered into a pass
    e, o = synth(["-10", "-5"], ["-10", "-4"])
    p = pool(e, o)
    ok = (p["min_gap"] == 0 and p["near_tie"] and not p["gaps_decreasing"])
    print("arm1d degenerate equal rungs flagged as near-tie      : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm1d")
    # residual rule must DROP a bad rung and count it
    e, o = synth(["-10", "-6"], ["-8", "-4"])
    e["rungs"][1]["rel"] = mpf("1e-3"); e["rungs"][1]["ok"] = False
    p = pool(e, o)
    ok = (p["dropped"] == 1 and p["order"] == "eoo")
    print("arm1e rung failing the residual rule dropped+counted  : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm1e")

    # ---- arm 2: PUBLISHED number from the SEALED c46 instrument's frozen cells
    ev = load_block(os.path.join(c46dir, "c46_block_even_x13_N100_dps150_g9_it16_k3.json"))
    od = load_block(os.path.join(c46dir, "c46_block_odd_x13_N100_dps150_g9_it16_k3.json"))
    p = pool(ev, od)
    ratio = mpf(10) ** p["s1"]
    ok = (mp.nstr(ratio, 6) == "3.91576e+7")
    print("arm2a c46 PUBLISHED lambda2/lambda1 = 3.91576e7       : got %s -> %s"
          % (mp.nstr(ratio, 6), "PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm2a")
    ok = (p["order"] == "eoeoeo") and ((p["gaps"][0] + p["gaps"][1] - p["s1"]) == 0) and \
         (abs(p["r1"] - 1 / (1 + p["q"][0])) < mpf(10) ** (-55))
    print("arm2b c46 cells: order eoeoeo, gap1+gap2==s1 exactly  : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm2b")
    # c46's own published parity gap at x=13 N=100: 3.9532
    ok = (mp.nstr(p["d1"], 5) == "3.9532")
    print("arm2c c46 PUBLISHED parity gap 3.9532 dex             : got %s -> %s"
          % (mp.nstr(p["d1"], 5), "PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm2c")
    # model A's constant must equal the calibration q_1 to the digits registered
    ok = (mp.nstr(p["q"][0], 10) == mp.nstr(Q_CAL, 10))
    print("arm2d registered model-A constant == calibration q_1  : %s" % ("PASS" if ok else "FAIL"))
    if not ok:
        fails.append("arm2d")

    # ---- arm 3 (only once the k=5 calibration cells exist): P0's first two rows
    f5e = os.path.join(cellsdir or "", "c46_block_even_x13_N100_dps150_g9_it16_k5.json")
    f5o = os.path.join(cellsdir or "", "c46_block_odd_x13_N100_dps150_g9_it16_k5.json")
    if os.path.exists(f5e) and os.path.exists(f5o):
        worst = mpf(0)
        for path5, path3 in ((f5e, "even"), (f5o, "odd")):
            new = load_block(path5)
            old = load_block(os.path.join(c46dir, "c46_block_%s_x13_N100_dps150_g9_it16_k3.json" % path3))
            for i in range(3):
                rel = abs(new["rungs"][i]["lam"] / old["rungs"][i]["lam"] - 1)
                worst = max(worst, rel)
        ok = worst < mpf(10) ** (-30)
        print("arm3  k=5 run reproduces published k=3 ladder (6 val): worst rel = %s -> %s"
              % (mp.nstr(worst, 5), "PASS" if ok else "FAIL"))
        if not ok:
            fails.append("arm3")
    else:
        print("arm3  k=5 calibration cells absent                    : NOT RUN (pre-launch)")

    print("SELF-TEST: %d fail(s)%s" % (len(fails), (" " + ",".join(fails)) if fails else ""))
    return 1 if fails else 0


# ------------------------------------------------------------------ scoring
def score(cellsdir, c46dir, jsonout=None):
    ns = mp.nstr
    rows = []
    pats = sorted(glob.glob(os.path.join(cellsdir, "c46_block_even_*.json")))
    for fe in pats:
        fo = fe.replace("_even_", "_odd_")
        if not os.path.exists(fo):
            print("!! no odd partner for %s" % os.path.basename(fe))
            continue
        ev, od = load_block(fe), load_block(fo)
        p = pool(ev, od)
        x = ev["x"]
        n = NZERO.get(x)
        row = dict(x=x, N=ev["N"], dps=ev["dps"], k=ev["k"], n=n,
                   order=p["order"], alternates=p["alternates"], near_tie=p["near_tie"],
                   dropped=p["dropped"], min_gap=ns(p["min_gap"], 10),
                   gaps=[ns(g, 12) for g in p["gaps"]], q=[ns(v, 12) for v in p["q"]],
                   gaps_decreasing=p["gaps_decreasing"],
                   d1=ns(p["d1"], 12), s1=ns(p.get("s1", mpf(0)), 12),
                   r1=ns(p.get("r1", mpf(0)), 12),
                   lam2_over_lam1=ns(mpf(10) ** p["s1"], 8) if "s1" in p else None,
                   rel_resid_max=ns(max([r["rel"] for r in ev["rungs"] + od["rungs"]]), 5))
        if "s1" in p and n:
            qa = modelA_q()
            gB = modelB_gaps(n)
            qb = gB[1] / gB[0]
            row["A_q1"] = ns(qa, 8); row["B_q1"] = ns(qb, 8)
            row["res_q1_A"] = ns(p["q"][0] - qa, 8); row["res_q1_B"] = ns(p["q"][0] - qb, 8)
            row["A_s1hat"] = ns(p["d1"] * (1 + qa), 10); row["B_s1hat"] = ns(p["d1"] * (1 + qb), 10)
            row["res_s1_A"] = ns(p["s1"] - p["d1"] * (1 + qa), 8)
            row["res_s1_B"] = ns(p["s1"] - p["d1"] * (1 + qb), 8)
            row["B_gap1hat"] = ns(gB[0], 8)
            row["res_gap1_B"] = ns(p["gaps"][0] - gB[0], 8)
            row["winner_q1"] = "A" if abs(p["q"][0] - qa) < abs(p["q"][0] - qb) else "B"
        rows.append(row)
    if jsonout:
        json.dump(rows, open(jsonout, "w"), indent=1)
    hdr = ["x", "N", "dps", "k", "n", "order", "alt", "drop", "d1", "s1", "q1",
           "res_q1_A", "res_q1_B", "win", "lam2/lam1"]
    print("\t".join(hdr))
    for r in rows:
        print("\t".join(str(v) for v in [r["x"], r["N"], r["dps"], r["k"], r["n"], r["order"],
                                         r["alternates"], r["dropped"], r["d1"], r["s1"],
                                         r["q"][0] if r["q"] else "-",
                                         r.get("res_q1_A", "-"), r.get("res_q1_B", "-"),
                                         r.get("winner_q1", "-"), r["lam2_over_lam1"]]))
    print("\nper-cell detail")
    for r in rows:
        print("  x=%s N=%s dps=%s k=%s  order=%s  min_gap=%s  dropped=%s  max_rel_resid=%s"
              % (r["x"], r["N"], r["dps"], r["k"], r["order"], r["min_gap"], r["dropped"],
                 r["rel_resid_max"]))
        print("     gaps: %s" % ", ".join(r["gaps"]))
        print("     q   : %s   decreasing=%s" % (", ".join(r["q"]), r["gaps_decreasing"]))
        if "res_s1_A" in r:
            print("     s1=%s  A_hat=%s (res %s)  B_hat=%s (res %s)  B_gap1_hat=%s (res %s)"
                  % (r["s1"], r["A_s1hat"], r["res_s1_A"], r["B_s1hat"], r["res_s1_B"],
                     r["B_gap1hat"], r["res_gap1_B"]))
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--cells", default=None)
    ap.add_argument("--c46dir", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    c46dir = a.c46dir or os.path.join(here, "data", "c46")
    if a.self_test:
        sys.exit(self_test(c46dir, a.cells))
    if a.score:
        score(a.cells or c46dir, c46dir, a.json)
    else:
        print(__doc__)
