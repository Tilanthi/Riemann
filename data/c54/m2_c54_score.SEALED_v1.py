#!/usr/bin/env python3
"""m2_c54_score.py -- cycle 54's grader: the REMEDY, and the scorer for the x=17 window.

THE DEFECT THIS FILE EXISTS TO END
----------------------------------
`data/c53/m2_c53_score.py:62` built the pooled table with `delta=r[4]`, where `r[4]` is the
PER-SECTOR defect `nu - sturm(parity, m)` read back out of the node file.  Under alternation that
equals the pooled defect; off alternation it does not.  The pooled defect is
    Delta(p) = nu_p - (p - 1)
and it must be computed FROM THE SORT INDEX, because the sort index is the only thing that knows
what pooling did.  Remedy item 1.

And `certified_prefix` in that grader is c50's COMPLETENESS certificate, while the depth the letter
actually reasons from is the N-CONTROL trusted depth.  Two notions of "how deep may I be believed",
one JSON, one name that answers to both.  Remedy item 2: BOTH are printed, under distinct names,
with a legend, everywhere either appears.

Remedy item 3 is `kat_na`: a PLANTED NON-ALTERNATING pool on which the two formulas MUST differ --
a remedy whose test cannot fail is not a test.
Remedy item 4 (m1's, accepted) is `fixture_d`: a cell where the two depths DIFFER BY CONSTRUCTION,
so the printing rule has its own test that can fail.

SORTING.  The pooled order is taken on `decimal.Decimal(log10)`, never on `float(...)` and never on
the STRING.  m1's near-miss in L197's preparation was a lexicographic sort of 39-digit decimals:
a lexicographic sort of decimal strings is a numeric sort only if the strings share sign, width and
exponent convention, and these share none of the three.  The float order is computed too, as a
MEASUREMENT, and reported beside the Decimal order rather than assumed equal.

usage:
  m2_c54_score.py kat_na       remedy item 3
  m2_c54_score.py fixture_d    remedy item 4
  m2_c54_score.py regression   R3 + R4 (needs a scratch copy; see --scratch)
  m2_c54_score.py score        the x=17 scorecard -> m2_c54_scores.json
"""
import json, os, sys, subprocess, shutil, glob
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_dir(name):
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


C51, C53 = _find_dir("c51"), _find_dir("c53")

DEPTH_LEGEND = {
    "completeness_certified_prefix":
        "c50's COMPLETENESS certificate: with R rungs of each sector the pooled ORDER is certified "
        "only at or below T = min(top_even, top_odd). It licenses the ORDER, not the values.",
    "n_control_trusted_depth":
        "the N-CONTROL trusted depth (c53 P6): 2*min(sector rungs whose node count agrees between "
        "N=100 and N=180) - 1. It licenses the NODE COUNTS, and it is the depth a claim is scored "
        "over. Conservative by >= 1 level by construction.",
    "why_both": "c53 printed only the first, under a name the second answers to (m1-L197 defect, "
                "reproduced and merged in ERRATUM 28). Neither number is 'the' depth."}


# ------------------------------------------------------------------ pooling, done right
def pool_rows(nodefiles):
    """nodefiles: {'even': path, 'odd': path}.  Returns (rows, tops) with rows sorted by Decimal."""
    rows, tops = [], []
    for par in ("even", "odd"):
        d = json.load(open(nodefiles[par]))
        rr = [r for r in d["rungs"] if r.get("log10") is not None]
        for r in rr:
            rows.append(dict(log10=Decimal(r["log10"]), parity=par, sector_rung=r["rung"],
                             nu=r["nu"], sector_delta=r["delta"], lam=r["lam"],
                             lobe=r.get("lobe_min_ratio"), admitted=r.get("admitted"),
                             refine=r.get("nu_refine_48001")))
        tops.append(Decimal(rr[-1]["log10"]))
    rows.sort(key=lambda r: r["log10"])
    return rows, tops


def pooled_table(nodefiles):
    rows, tops = pool_rows(nodefiles)
    T = min(tops)
    out = []
    for i, r in enumerate(rows):
        p = i + 1
        out.append(dict(p=p, parity=r["parity"], sector_rung=r["sector_rung"], nu=r["nu"],
                        log10=str(r["log10"]),
                        pooled_delta=(None if r["nu"] is None else r["nu"] - (p - 1)),   # <- REMEDY 1
                        sector_delta_FROM_FILE=r["sector_delta"],
                        lobe=r["lobe"], admitted=r["admitted"], refine=r["refine"]))
    cert = sum(1 for r in rows if r["log10"] <= T)
    # the float order, MEASURED not assumed (m1's trap-#149 worry, re-asked at the new window)
    frows = sorted(range(len(rows)), key=lambda i: float(rows[i]["log10"]))
    float_order_same = (frows == list(range(len(rows))))
    return out, cert, float_order_same


def n_control_depth(nodes100, nodes180):
    """2*min(agreed sector rungs)-1, per c53 P6.  Returns (depth, per-sector detail)."""
    detail = {}
    agreed = []
    for par in ("even", "odd"):
        a = json.load(open(nodes100[par]))["rungs"]
        b = json.load(open(nodes180[par]))["rungs"]
        k = 0
        for ra, rb in zip(a, b):
            if ra["nu"] is not None and ra["nu"] == rb["nu"]:
                k += 1
            else:
                break
        detail[par] = dict(agreed_sector_rungs=k, compared=min(len(a), len(b)),
                           first_disagreement=(None if k >= min(len(a), len(b))
                                               else dict(rung=a[k]["rung"], N100=a[k]["nu"],
                                                         N180=b[k]["nu"])))
        agreed.append(k)
    return (2 * min(agreed) - 1 if min(agreed) > 0 else 0), detail


# ------------------------------------------------------------------ REMEDY 3: planted KAT
def kat_na():
    """A PLANTED NON-ALTERNATING pooled ladder on which the c53 formula and the c54 formula MUST
    differ.  Firing world non-empty BY CONSTRUCTION, and the expected divergence is written down
    here, in the source, before the run.

    Construction: three even rungs and one odd rung, pooled in the order e,e,o,e -- i.e. the
    alternation that c53's shortcut silently assumes is broken at pooled index 2.
    Sturm baselines (c51): even rung m -> 2(m-1); odd rung m -> 2m-1.
      pooled 1: even m=1, nu=0   sector_delta = 0-0 = 0    pooled Delta = 0-0 = 0    SAME
      pooled 2: even m=2, nu=2   sector_delta = 2-2 = 0    pooled Delta = 2-1 = 1    DIFFER by 1
      pooled 3: odd  m=1, nu=3   sector_delta = 3-1 = 2    pooled Delta = 3-2 = 1    DIFFER by 1
      pooled 4: even m=3, nu=6   sector_delta = 6-4 = 2    pooled Delta = 6-3 = 3    DIFFER by 1
    Expected: 4 rows, 3 disagreements, at pooled indices 2, 3, 4.
    A KAT that only exercised an ALTERNATING pool would pass under the defect and is the reason the
    c53 defect survived its own cycle.
    """
    plant = [dict(par="even", m=1, nu=0, log10="-40.0"),
             dict(par="even", m=2, nu=2, log10="-30.0"),
             dict(par="odd",  m=1, nu=3, log10="-20.0"),
             dict(par="even", m=3, nu=6, log10="-10.0")]
    def sturm(par, m):
        return 2 * (m - 1) if par == "even" else 2 * m - 1
    rows, expected = [], dict(rows=4, disagreements=3, at=[2, 3, 4])
    for i, r in enumerate(plant):
        p = i + 1
        c53_formula = r["nu"] - sturm(r["par"], r["m"])
        c54_formula = r["nu"] - (p - 1)
        rows.append(dict(p=p, parity=r["par"], sector_rung=r["m"], nu=r["nu"],
                         c53_sector_delta=c53_formula, c54_pooled_delta=c54_formula,
                         differ=bool(c53_formula != c54_formula)))
    got = dict(rows=len(rows), disagreements=sum(1 for r in rows if r["differ"]),
               at=[r["p"] for r in rows if r["differ"]])
    # control: the SAME test on an ALTERNATING pool must show ZERO disagreement
    alt = [dict(par="even", m=1, nu=0), dict(par="odd", m=1, nu=1),
           dict(par="even", m=2, nu=2), dict(par="odd", m=2, nu=3)]
    ctrl = []
    for i, r in enumerate(alt):
        p = i + 1
        ctrl.append(dict(p=p, differ=bool(r["nu"] - sturm(r["par"], r["m"]) != r["nu"] - (p - 1))))
    ctrl_fires = sum(1 for c in ctrl if c["differ"])
    ok = (got == expected) and ctrl_fires == 0
    out = dict(verdict=("PASS" if ok else "FAIL"), expected=expected, measured=got,
               rows=rows, alternating_control=dict(disagreements=ctrl_fires, rows=ctrl),
               note="POSITIVE arm: a non-alternating pool, where the c53 shortcut is wrong at 3 of 4 "
                    "rows. NEGATIVE arm (the control): an alternating pool, where it is wrong at 0 "
                    "of 4 -- which is exactly why four cycles of alternating data never showed it.")
    json.dump(out, open(os.path.join(HERE, "m2_c54_kat_na.json"), "w"), indent=1)
    print("KAT-NA: expected %s measured %s ; alternating control fires %d -> %s"
          % (expected, got, ctrl_fires, out["verdict"]))
    return 0 if ok else 1


# ------------------------------------------------------------------ REMEDY 4: differing-depths fixture
def fixture_d():
    """m1's optional fourth item: a fixture in which the two depths DIFFER BY CONSTRUCTION, so the
    printing rule has a test that can fail.

    Built from the two real x=13 c53 cells by TRUNCATING the N=180 partner's node list: the
    completeness certificate is a property of the N=100 eigenvalue tops (unchanged), while the
    N-control depth is a property of the AGREEMENT between N=100 and N=180 (shortened).  If a future
    grader ever prints one number where the other belongs, this fixture separates them.
    """
    n100 = {p: os.path.join(C53, "m2_c53_nodes_%s_x13_N100_dps150.json" % p) for p in ("even", "odd")}
    n180 = {p: os.path.join(C53, "m2_c53_nodes_%s_x13_N180_dps150.json" % p) for p in ("even", "odd")}
    for f in list(n100.values()) + list(n180.values()):
        if not os.path.exists(f):
            print("FIXTURE-D UNMEASURED: %s absent" % os.path.basename(f))
            json.dump(dict(verdict="UNMEASURED", missing=os.path.basename(f)),
                      open(os.path.join(HERE, "m2_c54_fixture_d.json"), "w"), indent=1)
            return 1
    tmp = os.path.join(HERE, "_fixture_d_tmp")
    os.makedirs(tmp, exist_ok=True)
    trunc = {}
    for par in ("even", "odd"):
        d = json.load(open(n180[par]))
        d["rungs"] = d["rungs"][:4]                  # <- the construction: agreement can reach 4 at most
        fn = os.path.join(tmp, os.path.basename(n180[par]))
        json.dump(d, open(fn, "w"))
        trunc[par] = fn
    _, cert, _ = pooled_table(n100)
    depth_full, det_full = n_control_depth(n100, n180)
    depth_trunc, det_trunc = n_control_depth(n100, trunc)
    ok = (cert != depth_trunc) and (depth_trunc == 7) and (depth_full != depth_trunc)
    out = dict(verdict=("PASS" if ok else "FAIL"),
               completeness_certified_prefix=cert,
               n_control_trusted_depth_full=depth_full,
               n_control_trusted_depth_truncated=depth_trunc,
               expected_truncated_depth=7,
               depth_legend=DEPTH_LEGEND, detail_full=det_full, detail_truncated=det_trunc,
               note="the two depths are DIFFERENT QUANTITIES and this fixture makes them numerically "
                    "different on purpose: the certificate is unchanged at %d while the N-control "
                    "depth falls from %d to %d. Any grader that prints one for the other fails here."
                    % (cert, depth_full, depth_trunc))
    json.dump(out, open(os.path.join(HERE, "m2_c54_fixture_d.json"), "w"), indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    print("FIXTURE-D: certificate %s ; N-control full %s -> truncated %s (expected 7) -> %s"
          % (cert, depth_full, depth_trunc, out["verdict"]))
    return 0 if ok else 1



# ------------------------------------------------------------------ R3 + R4: the regression
def _flatten(o, path="", out=None):
    if out is None:
        out = {}
    if isinstance(o, dict):
        for k in o:
            _flatten(o[k], path + "/" + str(k), out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            _flatten(v, path + "[%d]" % i, out)
    else:
        out[path] = o
    return out


def _viol_key(r):
    """the identity of a P4 violation ROW, independent of where the list happens to put it."""
    return (r.get("x"), r.get("N"), r.get("p"), r.get("why"))


def _leafdiff_positional(a, b):
    """CONVENTION A (m1's): leaves aligned by POSITION, so a list that grows shifts everything
    after the insertion point."""
    fa, fb = _flatten(a), _flatten(b)
    keys = set(fa) | set(fb)
    return sorted(k for k in keys if fa.get(k, "<<absent>>") != fb.get(k, "<<absent>>"))


def _leafdiff_keyaligned(a, b):
    """CONVENTION B (machine 2's): identical to A except that P4's `violations` rows are matched by
    their identifying key (x, N, p, why) instead of by list index, so an inserted row is counted as
    an ADDITION and the rows after it are not counted as changes."""
    a2, b2 = json.loads(json.dumps(a)), json.loads(json.dumps(b))
    for d in (a2, b2):
        v = d.get("P4", {}).get("violations")
        if isinstance(v, list):
            d["P4"]["violations"] = {json.dumps(_viol_key(r)): r for r in v}
    return _leafdiff_positional(a2, b2)


def regression(scratch):
    """R3: KAT first -- the UNPATCHED sealed c53 grader must reproduce the banked scores exactly.
    Only then is the patched run evidence about the DEFECT rather than about the harness.
    R4: the 45-vs-48 leaf count, under BOTH conventions, each printed with its definition."""
    banked = json.load(open(os.path.join(C53, "m2_c53_scores.json")))
    sc53 = os.path.join(scratch, "c53")
    grader = os.path.join(sc53, "m2_c53_score.py")
    if not os.path.exists(grader):
        raise SystemExit("scratch copy missing: %s" % grader)
    # --- KAT: unpatched
    subprocess.run([sys.executable, grader], cwd=sc53, check=True, stdout=subprocess.DEVNULL)
    unpatched = json.load(open(os.path.join(sc53, "m2_c53_scores.json")))
    kat_ok = (json.dumps(unpatched, sort_keys=True) == json.dumps(banked, sort_keys=True))
    # --- the one-line patch, applied to the SCRATCH copy only
    src = open(grader).read()
    assert src.count("delta=r[4]") == 1, "the defect line is not where c53 left it"
    open(grader, "w").write(src.replace("delta=r[4]", "delta=r[3] - i"))
    subprocess.run([sys.executable, grader], cwd=sc53, check=True, stdout=subprocess.DEVNULL)
    patched = json.load(open(os.path.join(sc53, "m2_c53_scores.json")))
    # --- verdicts
    def verdicts(d):
        return {k: v.get("verdict") for k, v in d.items() if isinstance(v, dict) and "verdict" in v}
    vb, vp = verdicts(banked), verdicts(patched)
    same_verdicts = (vb == vp)
    posit = _leafdiff_positional(banked, patched)
    keyal = _leafdiff_keyaligned(banked, patched)
    def bucket(keys):
        b = {}
        for k in keys:
            top = k.split("/")[1] if k.startswith("/") else k
            b[top] = b.get(top, 0) + 1
        return b
    out = dict(
        R3_kat_unpatched_reproduces_banked=bool(kat_ok),
        verdict_count=len(vb), verdicts_identical=bool(same_verdicts),
        verdicts_banked=vb, verdicts_patched=vp,
        R4_leaf_counts=dict(
            convention_A_positional=dict(
                count=len(posit), by_top_key=bucket(posit),
                definition="leaves aligned by POSITION; a list that grows shifts every leaf after "
                           "the insertion point, so re-valued and displaced leaves are both counted "
                           "(m1's convention)"),
            convention_B_key_aligned=dict(
                count=len(keyal), by_top_key=bucket(keyal),
                definition="identical, except P4.violations rows are matched by their identity "
                           "(x, N, p, why); an inserted row is an ADDITION and the rows after it are "
                           "not counted as changes (machine 2's convention)")),
        differing_leaf_paths_positional=posit,
        differing_leaf_paths_key_aligned=keyal,
        headline_values=dict(
            p2=patched.get("P1", {}).get("p2"), occupied_bin=patched.get("P1", {}).get("occupied_bin"),
            survivors=patched.get("P1", {}).get("survivors"),
            p3=patched.get("P3", {}).get("p3"),
            violations_banked=len(banked.get("P4", {}).get("violations", [])),
            violations_patched=len(patched.get("P4", {}).get("violations", []))),
        depth_legend=DEPTH_LEGEND,
        note="the scratch copy is disposable; data/c53 is never written by this gate. A count "
             "travels with its convention (trap #154): neither number is 'the' answer alone.")
    json.dump(out, open(os.path.join(HERE, "m2_c54_regression.json"), "w"), indent=1)
    print("R3 KAT (unpatched reproduces banked): %s" % ("PASS" if kat_ok else "FAIL"))
    print("R3 verdicts identical: %s (%d verdicts)" % (same_verdicts, len(vb)))
    print("R4 leaf counts: convention A (positional) = %d ; convention B (key-aligned) = %d"
          % (len(posit), len(keyal)))
    print("   A by key: %s" % bucket(posit))
    print("   B by key: %s" % bucket(keyal))
    print("   violations rows %s -> %s" % (out["headline_values"]["violations_banked"],
                                           out["headline_values"]["violations_patched"]))
    return 0 if (kat_ok and same_verdicts) else 1


# ------------------------------------------------------------------ the x=17 scorecard
DPS, GL, X = 300, 9, 17

# the registered models, verbatim from m2_c54_prereg.md section 3. LIVE vs CONTROL is part of the
# registration: Z and G were already refuted at x=19 and are not scored as live models.
MODELS = {"L": dict(p2=10, live=True,  rule="length = round(4*log x / log 13) = round(4.41835) = 4"),
          "I": dict(p2=11, live=True,  rule="p2 = 10 + (n-21)/(38-21) = 10.647"),
          "X": dict(p2=11, live=True,  rule="p2 = 10 + (log x - log 13)/(log 19 - log 13) = 10.707"),
          "Z": dict(p2=12, live=False, rule="length = round(4n/21) = round(6.0952) = 6 -- REFUTED at x=19"),
          "G": dict(p2=None, live=False, rule="gap turnaround, computed at STAGE A -- REFUTED at x=19")}


def _nodefiles(N):
    return {p: os.path.join(HERE, "m2_c54_nodes_%s_x%d_N%d_dps%d.json" % (p, X, N, DPS))
            for p in ("even", "odd")}


def _first_leave(seq, value, start=1):
    for i in range(start, len(seq)):
        if seq[i - 1] == value and seq[i] != value:
            return i + 1
    return None


def score():
    S = dict(window=dict(x=X, dps=DPS, gl=GL, N=[100, 180]), depth_legend=DEPTH_LEGEND)
    n100, n180 = _nodefiles(100), _nodefiles(180)
    have100 = all(os.path.exists(f) for f in n100.values())
    have180 = all(os.path.exists(f) for f in n180.values())
    S["inputs"] = dict(N100_present=have100, N180_present=have180,
                       files={k: os.path.basename(v) for k, v in list(n100.items()) + list(n180.items())})
    if not have100:
        S["VERDICT"] = "UNMEASURED -- the N=100 node cells do not exist"
        json.dump(S, open(os.path.join(HERE, "m2_c54_scores.json"), "w"), indent=1)
        print("UNMEASURED: no N=100 node cells")
        return 2

    tab, cert, float_same = pooled_table(n100)
    S["completeness_certified_prefix"] = cert
    S["float_order_equals_decimal_order"] = bool(float_same)
    S["pooled_table_N100"] = tab
    seq = [r["pooled_delta"] for r in tab]
    S["pooled_delta_N100"] = seq
    S["pooled_parity_order_N100"] = "".join(r["parity"][0] for r in tab)
    S["sector_delta_field_would_have_given"] = [r["sector_delta_FROM_FILE"] for r in tab]
    S["sort_index_vs_sector_field_agree"] = bool(seq == S["sector_delta_field_would_have_given"])

    if have180:
        depth, det = n_control_depth(n100, n180)
    else:
        depth, det = 0, dict(reason="N=180 cells absent")
    S["n_control_trusted_depth"] = depth
    S["n_control_detail"] = det

    def scored_over(p):
        """a prediction about pooled index p is scored only if p is inside the trusted depth."""
        return p is not None and depth >= p

    # ---- P1: the onset
    p1 = _first_leave(seq, 0)
    S["P1"] = dict(measured_p1=p1, registered=6,
                   verdict=("UNMEASURED (outside trust)" if not scored_over(p1)
                            else ("HELD" if p1 == 6 else "REFUTED")),
                   confirmation_note="declared WEAK in advance: c51's onset held 8/8 across a 9.5x "
                                     "range of n, so a pass here is UNINFORMATIVE-if-passed.")

    # ---- P2: the target
    p2 = _first_leave(seq, 2)
    bins = {}
    for k, m in MODELS.items():
        if m["p2"] is not None:
            bins.setdefault(m["p2"], []).append(k)
    occupants = bins.get(p2, [])
    live_occ = [k for k in occupants if MODELS[k]["live"]]
    S["P2"] = dict(measured_p2=p2, models=MODELS, bins={str(k): v for k, v in sorted(bins.items())},
                   occupied_bin=p2, occupants=occupants, live_occupants=live_occ,
                   survivor_count=len(live_occ),
                   refuted_live_models=[k for k, m in MODELS.items()
                                        if m["live"] and m["p2"] is not None and m["p2"] != p2],
                   discrimination=("NONE -- more than one registered model names this bin"
                                   if len(occupants) > 1 else
                                   ("SINGLE OCCUPANT" if len(occupants) == 1 else
                                    "EMPTY BIN -- every registered model is refuted")),
                   verdict=("UNMEASURED (outside trust)" if not scored_over(p2) else "MEASURED"))

    # ---- P3: the size
    inc = None if p2 is None or p2 > len(seq) else seq[p2 - 1] - 2
    S["P3"] = dict(registered=4, measured_increment=inc,
                   verdict=("UNMEASURED (outside trust)" if not scored_over(p2)
                            else ("HELD" if inc == 4 else "REFUTED")))

    # ---- P4: p3 as an INVARIANCE
    p3 = _first_leave(seq, 6)
    S["P4"] = dict(registered=15, measured_p3=p3,
                   verdict=("UNMEASURED (outside trust)" if not scored_over(p3)
                            else ("HELD" if p3 == 15 else "REFUTED")),
                   note="registered as an INVARIANCE: p3 was 15 at BOTH x=13 and x=19 while p2 moved.")

    # ---- P5: the decrease
    got = {p: (seq[p - 1] if p <= len(seq) else None) for p in (15, 16, 17)}
    ok5 = (got[15] == 10 and got[16] == 10 and got[17] == 8)
    S["P5"] = dict(registered=dict(p15=10, p16=10, p17=8), measured=got,
                   verdict=("UNMEASURED (outside trust)" if depth < 17
                            else ("HELD" if ok5 else "REFUTED")))

    # ---- P6: the N-control itself
    S["P6"] = dict(registered_floor=21, measured_depth=depth, detail=det,
                   verdict=("UNMEASURED (N=180 absent)" if not have180
                            else ("HELD" if depth >= 21 else "REFUTED")))

    # ---- P7: alternation through trust
    order = S["pooled_parity_order_N100"][:max(depth, 0)]
    alt = all(order[i] != order[i + 1] for i in range(len(order) - 1)) if len(order) > 1 else None
    S["P7"] = dict(order_through_trust=order, depth=depth,
                   verdict=("UNMEASURED" if not order else ("HELD" if alt else "REFUTED")))

    # ---- model G, from the stage-A file if it exists
    g = os.path.join(HERE, "m2_c54_gpred_x%d_N%d_dps%d.json" % (X, 100, DPS))
    if os.path.exists(g):
        gd = json.load(open(g))
        S["P2"]["models"]["G"]["p2"] = gd.get("model_G_p2")
        S["model_G_stageA"] = dict(p2=gd.get("model_G_p2"),
                                   first_local_min_index=gd.get("first_local_min_index"),
                                   first_local_max_after=gd.get("first_local_max_after"))
    json.dump(S, open(os.path.join(HERE, "m2_c54_scores.json"), "w"), indent=1)
    print("x=%d  certificate=%s  N-control trusted depth=%s" % (X, cert, depth))
    print("  pooled Delta (N=100): %s" % seq)
    print("  parity order        : %s" % S["pooled_parity_order_N100"])
    print("  p1=%s  p2=%s  size=%s  p3=%s" % (p1, p2, inc, p3))
    print("  occupants of bin %s: %s   live survivors: %s" % (p2, occupants, live_occ))
    for k in ("P1", "P3", "P4", "P5", "P6", "P7"):
        print("  %s: %s" % (k, S[k]["verdict"]))
    print("  sort-index vs sector-field agree: %s (float order == Decimal order: %s)"
          % (S["sort_index_vs_sector_field_agree"], float_same))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "kat_na":
        sys.exit(kat_na())
    if cmd == "fixture_d":
        sys.exit(fixture_d())
    if cmd == "regression":
        sys.exit(regression(sys.argv[2]))
    if cmd == "score":
        sys.exit(score())
    print(__doc__)
    sys.exit(2)
