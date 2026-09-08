#!/usr/bin/env python3
"""m2_c53_score.py -- the SEALED GRADER for cycle 53.

Written and pushed BEFORE any node count of an unpublished rung exists (stage-A push).  It scores
G0, G1, G2 and P1..P7 exactly as §4 of the prereg words them, including the CONFIRMATION CRITERIA:
an agreement that could not have failed is scored UNINFORMATIVE, never PASS.

Degradation: with a missing or half-finished grid every verdict degrades to UNMEASURED with a
printed denominator.  It must never crash and must never silently score a subset.

usage: m2_c53_score.py           (reads data/c53 and data/c51; writes m2_c53_scores.json)
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_dir(name):
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


C51 = _find_dir("c51")
CELLS = [("even", 13, 100, 150), ("odd", 13, 100, 150),
         ("even", 19, 100, 300), ("odd", 19, 100, 300),
         ("even", 13, 180, 150), ("odd", 13, 180, 150),
         ("even", 19, 180, 300), ("odd", 19, 180, 300)]
FRONTIER = 5.0e-3            # c51's MEASURED blind-spot frontier of this detector


def load(par, X, N, D):
    fn = os.path.join(HERE, "m2_c53_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, D))
    return json.load(open(fn)) if os.path.exists(fn) else None


def load_spec(par, X, N, D):
    fn = os.path.join(HERE, "m2_c53_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, D))
    return json.load(open(fn)) if os.path.exists(fn) else None


def load_block(par, X, N, k=12):
    fn = os.path.join(HERE, "m2_c51_nodes_%s_x%d_N%d_k%d.json" % (par, X, N, k))
    return json.load(open(fn)) if os.path.exists(fn) else None


def pooled(X, N, D):
    """pool the two sectors by eigenvalue; returns rows (p, parity, sector rung, log10, nu, delta)
    and the c50 completeness certificate (how many pooled levels are certified)."""
    rows, tops = [], []
    for par in ("even", "odd"):
        d = load(par, X, N, D)
        if d is None:
            return None, None
        rr = [r for r in d["rungs"] if r["log10"] is not None]
        for r in rr:
            rows.append((float(r["log10"]), par, r["rung"], r["nu"], r["delta"],
                         r["lobe_min_ratio"], r["stable"], r["nu_refine_48001"]))
        tops.append(float(rr[-1]["log10"]))
    rows.sort()
    cert = sum(1 for r in rows if r[0] <= min(tops))
    out = [dict(p=i + 1, parity=r[1], rung=r[2], log10=r[0], nu=r[3], delta=r[4],
                lobe=r[5], stable=r[6], refine=r[7]) for i, r in enumerate(rows)]
    return out, cert


def first_leave(seq, value, start=1):
    """smallest p (1-based) with seq[p-1] != value, given seq[p-2] == value.  None if it never leaves."""
    for i in range(start, len(seq)):
        if seq[i - 1] == value and seq[i] != value:
            return i + 1
    return None


def main():
    S = {}

    # ---------------- G0: the P0 gate
    fn = os.path.join(HERE, "m2_c53_p0_recount.json")
    if os.path.exists(fn):
        d = json.load(open(fn))
        S["G0"] = dict(verdict=d["verdict"], compared=d["compared"], matched=d["matched"],
                       cells=len(d["files"]))
    else:
        S["G0"] = dict(verdict="UNMEASURED", reason="m2_c53_p0_recount.json absent")

    # ---------------- G1: eigenvalue agreement vs the published block ladders
    g1 = []
    for par, X, N, D in CELLS:
        sp = load_spec(par, X, N, D)
        if sp is None:
            g1.append(dict(cell="%s x%d N%d" % (par, X, N), verdict="UNMEASURED"))
            continue
        dep = sp.get("selftest_depths_sf")
        if not dep:
            g1.append(dict(cell="%s x%d N%d" % (par, X, N), verdict="NO REFERENCE PUBLISHED",
                           ceiling=sp.get("selftest_ceiling_sf")))
            continue
        vals = [float(v) for v in dep]
        g1.append(dict(cell="%s x%d N%d" % (par, X, N), depths_sf=dep,
                       ceiling_sf=sp.get("selftest_ceiling_sf"),
                       verdict=("PASS" if min(vals) >= 30 else "FAIL"), min_sf=min(vals)))
    if any(r.get("verdict") == "UNMEASURED" for r in g1):
        g1v = "UNMEASURED"                      # found by the empty-grid dry run, before the seal
    elif all(r.get("verdict") in ("PASS", "NO REFERENCE PUBLISHED") for r in g1):
        g1v = "PASS"
    else:
        g1v = "FAIL"
    S["G1"] = dict(rows=g1, verdict=g1v,
                   note="depth is CEILING-LIMITED by the published print width (c37/c43)")

    # ---------------- G2: delta cross-determination against c51's published integers
    pubs = [("even", 13, 100, 150, "m2_c51_nodes_even_x13_N100_k7.json", 7),
            ("odd", 13, 100, 150, "m2_c51_nodes_odd_x13_N100_k7.json", 7),
            ("even", 13, 180, 150, "m2_c51_nodes_even_x13_N180_k5.json", 5),
            ("odd", 13, 180, 150, "m2_c51_nodes_odd_x13_N180_k5.json", 5),
            ("even", 19, 100, 300, "m2_c51_nodes_even_x19_N100_k5.json", 5),
            ("odd", 19, 100, 300, "m2_c51_nodes_odd_x19_N100_k5.json", 5)]
    rows, comp, agree, topcomp, topagree = [], 0, 0, 0, 0
    for par, X, N, D, fn, ktop in pubs:
        mine = load(par, X, N, D)
        pub = json.load(open(os.path.join(C51, fn)))
        if mine is None:
            rows.append(dict(cell=fn, verdict="UNMEASURED"))
            continue
        md = {r["rung"]: r["delta"] for r in mine["rungs"]}
        for r in pub["rungs"]:
            if r["rung"] not in md:
                continue
            comp += 1
            ok = md[r["rung"]] == r["delta"]
            agree += 1 if ok else 0
            istop = (r["rung"] == ktop)
            if istop:
                topcomp += 1
                topagree += 1 if ok else 0
            rows.append(dict(cell=fn, rung=r["rung"], published_delta=r["delta"],
                             c53_delta=md[r["rung"]], top_of_block=istop, agree=bool(ok),
                             block_rel_residual=r["rel_residual"]))
    if comp == 0:
        S["G2"] = dict(verdict="UNMEASURED", rows=rows)
    elif agree < comp:
        S["G2"] = dict(verdict="DISAGREEMENT -- HEADLINE", compared=comp, agreed=agree, rows=rows)
    elif topcomp == 0:
        S["G2"] = dict(verdict="UNINFORMATIVE", compared=comp, agreed=agree,
                       reason="no top-of-block rung was compared; agreement at low rungs is not "
                              "evidence about the solvers (prereg G2 confirmation criterion)",
                       rows=rows)
    else:
        S["G2"] = dict(verdict="PASS (informative)", compared=comp, agreed=agree,
                       top_of_block_compared=topcomp, top_of_block_agreed=topagree, rows=rows)

    # ---------------- P1: the target
    pl19, cert19 = pooled(19, 100, 300)
    models = dict(C=10, L=11, Z=13)
    gf = os.path.join(HERE, "m2_c53_gpred_x19_N100_dps300.json")
    models["G"] = json.load(open(gf))["model_G_p2"] if os.path.exists(gf) else None
    if pl19 is None:
        S["P1"] = dict(verdict="UNMEASURED", models=models)
    else:
        seq = [r["delta"] for r in pl19]
        p2 = first_leave(seq, 2)
        bin_ = ("none in range" if p2 is None else (">20" if p2 > 20 else str(p2)))
        named = [m for m, v in models.items() if v is not None and str(v) == bin_]
        S["P1"] = dict(verdict=("MEASURED" if p2 else "NO DISLOCATION IN RANGE"),
                       p2=p2, occupied_bin=bin_, certified_prefix=cert19,
                       models=models, survivors=named, survivor_count=len(named),
                       discrimination=("none -- two models in the winning bin" if len(named) > 1
                                       else ("one named survivor" if len(named) == 1
                                             else "every registered model refuted")),
                       pooled_delta=seq)

    # ---------------- P2: the SIZE of the second dislocation at x=19
    if pl19 is None or S["P1"].get("p2") is None:
        S["P2"] = dict(verdict="UNMEASURED",
                       reason="no second dislocation inside the computed range")
    else:
        seq = [r["delta"] for r in pl19]
        inc = seq[S["P1"]["p2"] - 1] - 2
        S["P2"] = dict(verdict=("HELD" if inc == 4 else "REFUTED"), predicted=4, measured=inc)

    # ---------------- P3: the third dislocation at x=13
    pl13, cert13 = pooled(13, 100, 150)
    if pl13 is None:
        S["P3"] = dict(verdict="UNMEASURED")
    else:
        seq = [r["delta"] for r in pl13]
        p3 = first_leave(seq, 6)
        if p3 is None:
            S["P3"] = dict(verdict="UNMEASURED -- no third jump inside the computed range",
                           models=dict(A=6, D=8), pooled_delta=seq, certified_prefix=cert13)
        else:
            inc = seq[p3 - 1] - 6
            surv = [m for m, v in dict(A=6, D=8).items() if v == inc]
            S["P3"] = dict(verdict="MEASURED", p3=p3, increment=inc, new_delta=seq[p3 - 1],
                           models=dict(A=6, D=8), survivors=surv, survivor_count=len(surv),
                           pooled_delta=seq, certified_prefix=cert13)

    # ---------------- P4: no recovery
    bad = []
    for X, N, D in ((13, 100, 150), (19, 100, 300), (13, 180, 150), (19, 180, 300)):
        pl, _ = pooled(X, N, D)
        if pl is None:
            continue
        seq = [r["delta"] for r in pl]
        for i in range(1, len(seq)):
            if seq[i] < seq[i - 1]:
                bad.append(dict(x=X, N=N, p=i + 1, prev=seq[i - 1], now=seq[i]))
        for r in pl:
            if r["nu"] in (5, 6):
                bad.append(dict(x=X, N=N, p=r["p"], nu=r["nu"], why="hidden node count returned"))
            if X == 13 and r["nu"] in (11, 12, 13, 14):
                bad.append(dict(x=X, N=N, p=r["p"], nu=r["nu"], why="second band count returned"))
    anydata = any(pooled(X, N, D)[0] is not None
                  for X, N, D in ((13, 100, 150), (19, 100, 300), (13, 180, 150), (19, 180, 300)))
    deep = (pl13 is not None and max((r["rung"] for r in pl13 if r["parity"] == "even"), default=0) >= 8)
    S["P4"] = dict(verdict=("UNMEASURED" if not anydata else
                            ("REFUTED -- HEADLINE" if bad else ("HELD" if deep else "INHERITED, NOT TESTED"))),
                   violations=bad,
                   note="informative only over rungs deeper than c51 reached (prereg P4 criterion)")

    # ---------------- P5: the control with a known answer
    ctrl = []
    for X, N, D in ((13, 100, 150), (19, 100, 300), (13, 180, 150), (19, 180, 300)):
        pl, _ = pooled(X, N, D)
        if pl is None:
            ctrl.append(dict(x=X, N=N, verdict="UNMEASURED"))
            continue
        seq = [r["delta"] for r in pl]
        ok = all(v == 0 for v in seq[:5]) and len(seq) > 5 and seq[5] == 2
        ctrl.append(dict(x=X, N=N, first_six=seq[:6], verdict=("PASS" if ok else "FAIL")))
    S["P5"] = dict(rows=ctrl,
                   verdict=("PASS" if all(r["verdict"] == "PASS" for r in ctrl) else
                            ("UNMEASURED" if any(r["verdict"] == "UNMEASURED" for r in ctrl) else "FAIL")))

    # ---------------- P6: the N-control = the real admission rule
    trust = []
    for X, D in ((13, 150), (19, 300)):
        for par in ("even", "odd"):
            a, b = load(par, X, 100, D), load(par, X, 180, D)
            if a is None or b is None:
                trust.append(dict(x=X, parity=par, verdict="UNMEASURED"))
                continue
            bm = {r["rung"]: r["nu"] for r in b["rungs"]}
            first_bad = None
            depth = 0
            for r in a["rungs"]:
                if r["rung"] not in bm:
                    break
                if bm[r["rung"]] != r["nu"]:
                    first_bad = r["rung"]
                    break
                depth = r["rung"]
            trust.append(dict(x=X, parity=par, agreed_sector_rungs=depth,
                              first_disagreeing_rung=first_bad,
                              N100_nu=[r["nu"] for r in a["rungs"]],
                              N180_nu=[bm.get(r["rung"]) for r in a["rungs"]]))
    ok = [t for t in trust if "agreed_sector_rungs" in t]
    pooled_trusted = (min(t["agreed_sector_rungs"] for t in ok) * 2 - 1) if ok else None
    S["P6"] = dict(rows=trust, pooled_trusted_depth=pooled_trusted,
                   predicted_at_least=12,
                   verdict=("UNMEASURED" if pooled_trusted is None else
                            ("HELD" if pooled_trusted >= 12 else "REFUTED")),
                   note="pooled trusted depth = 2*min(sector agreement)-1, the pooled prefix all of "
                        "whose members are N-controlled; a depth equal to the computed depth R is a "
                        "FLOOR, not a measurement of the truncation (prereg P6 criterion)")

    # ---------------- P7: does the detector run out before the basis does?
    below, checked = [], 0
    for par, X, N, D in CELLS:
        d = load(par, X, N, D)
        if d is None:
            continue
        for r in d["rungs"]:
            if r["rung"] >= 8 and r["lobe_min_ratio"] is not None:
                checked += 1
                if float(r["lobe_min_ratio"]) < FRONTIER:
                    below.append(dict(cell="%s x%d N%d" % (par, X, N), rung=r["rung"],
                                      lobe=r["lobe_min_ratio"], nu=r["nu"], delta=r["delta"]))
    S["P7"] = dict(frontier=FRONTIER, deep_rungs_checked=checked, below_frontier=below,
                   verdict=("UNMEASURED" if checked == 0 else
                            ("HELD -- the detector runs out first" if below else
                             "REFUTED -- my own expectation was wrong, the frontier is not binding at this depth")))

    # ---------------- tier 2: independent solver on the deep rungs
    t2 = []
    for par, X, N, D in (("even", 13, 100, 150), ("odd", 13, 100, 150),
                         ("even", 19, 100, 300), ("odd", 19, 100, 300)):
        blk, mine = load_block(par, X, N), load(par, X, N, D)
        if blk is None or mine is None:
            t2.append(dict(cell="%s x%d" % (par, X), verdict="UNMEASURED"))
            continue
        md = {r["rung"]: r["delta"] for r in mine["rungs"]}
        cmp_ = [(r["rung"], r["delta"], md.get(r["rung"])) for r in blk["rungs"] if r["rung"] in md]
        bad = [c for c in cmp_ if c[1] != c[2]]
        t2.append(dict(cell="%s x%d" % (par, X), compared=len(cmp_), disagreements=bad,
                       deepest_rung=max([c[0] for c in cmp_], default=0),
                       verdict=("PASS" if not bad else "DISAGREEMENT -- HEADLINE")))
    S["TIER2_double_determination"] = dict(rows=t2,
                                           verdict=("UNMEASURED" if all(r["verdict"] == "UNMEASURED" for r in t2)
                                                    else ("PASS" if all(r["verdict"] in ("PASS", "UNMEASURED") for r in t2)
                                                          else "DISAGREEMENT -- HEADLINE")))

    json.dump(S, open(os.path.join(HERE, "m2_c53_scores.json"), "w"), indent=1)
    for k in ("G0", "G1", "G2", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "TIER2_double_determination"):
        print("%-28s %s" % (k, S[k].get("verdict")))
    print()
    if S["P1"].get("p2"):
        print("P1  p2(x=19) = %s   models %s   survivors %s (%d)"
              % (S["P1"]["p2"], S["P1"]["models"], S["P1"]["survivors"], S["P1"]["survivor_count"]))
        print("    pooled Delta x=19 N=100: %s" % S["P1"]["pooled_delta"])
    if S["P3"].get("p3"):
        print("P3  third jump at x=13 at pooled p=%s, increment +%s, survivors %s"
              % (S["P3"]["p3"], S["P3"]["increment"], S["P3"]["survivors"]))
    if "pooled_delta" in S["P3"]:
        print("    pooled Delta x=13 N=100: %s" % S["P3"]["pooled_delta"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
