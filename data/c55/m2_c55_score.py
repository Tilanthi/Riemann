#!/usr/bin/env python3
"""m2_c55_score.py -- cycle 55's grader: the scorer for TWO windows, x = 22 and x = 25.

x = 25 is the extrapolation SEALED UNRUN in c54's prereg (ef19ac5) and is OPENED here.  x = 22 is
added because x = 25 cannot discriminate models I and X and x = 22 can, at identical cost.  The
JOINT criterion on the pair (p2(22), p2(25)) is the cycle's discriminating instrument; see
m2_c55_prereg.md sections 3-5.  Derived from data/c54/m2_c54_score.py; the diff is shipped as
m2_c55_score_from_c54.diff and the c54 regression arm is deliberately not carried.

THE REMEDY THIS FILE INHERITS

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
  m2_c55_score.py kat_na       remedy item 3
  m2_c55_score.py fixture_d    remedy item 4
  m2_c55_score.py score        both scorecards + the JOINT criterion -> m2_c55_scores.json
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
    """A PLANTED NON-ALTERNATING pooled ladder on which the c53 formula and the c55 formula MUST
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
        c55_formula = r["nu"] - (p - 1)
        rows.append(dict(p=p, parity=r["par"], sector_rung=r["m"], nu=r["nu"],
                         c53_sector_delta=c53_formula, c55_pooled_delta=c55_formula,
                         differ=bool(c53_formula != c55_formula)))
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
    json.dump(out, open(os.path.join(HERE, "m2_c55_kat_na.json"), "w"), indent=1)
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
                      open(os.path.join(HERE, "m2_c55_fixture_d.json"), "w"), indent=1)
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
    json.dump(out, open(os.path.join(HERE, "m2_c55_fixture_d.json"), "w"), indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    print("FIXTURE-D: certificate %s ; N-control full %s -> truncated %s (expected 7) -> %s"
          % (cert, depth_full, depth_trunc, out["verdict"]))
    return 0 if ok else 1



# NOTE: cycle 54's R3+R4 regression arm (the ERRATUM-28 re-score of c53's banked scores and
# the 45-vs-48-vs-49 leaf-count settlement) is DELIBERATELY NOT CARRIED HERE.  It was a gate
# about c53's artefacts and it discharged in c54; shipping it under a c55 name would be an
# unrun instrument wearing this cycle's label.  See m2_c55_score_from_c54.diff.

# ------------------------------------------------------------------ the x=22 and x=25 scorecards
DPS, GL = 300, 9
WINDOWS = (22, 25)                # x=25 = c54's SEALED extrapolation; x=22 = the discriminator

# ---------------------------------------------------------------------------------------------
# AMENDMENT 1 (m1's witness observation (b), adopted BEFORE any x=17 node count existed; see
# m2_c55_prereg_addendum_1.md and m2_c55_score.SEALED_v1.py + its diff).
# 🔴 THE POINT: the prereg REGISTERED RULES that are functions of the zero count n and of log x,
# and then PRINTED their n=32 instances.  A scorer that hardcodes the printed bins is scoring the
# instances, not the rules -- so a re-measurement that moved a bin would look like a broken
# registration instead of the rule firing.  The models are therefore evaluated HERE from the
# MEASURED n (m2_c55_zerocount.json, bracketing ordinates published) and from log x, and the
# printed bins are carried alongside as a CHECK that must agree.
# Direction check (m1's discipline): this amendment cannot move a bin at the measured n -- proved
# by the n-sweep printed in the output -- and it can only ADD a way for the cycle to report a
# discrepancy.  It removes no failure mode.
# `round` here is HALF-UP, matching the prereg's arithmetic; Python's built-in round() is
# banker's rounding and would send 4.5 to 4 and 10.5 to 10.  No registered value is a tie, and
# the sweep prints the margins.
# ---------------------------------------------------------------------------------------------
from math import log as _log, floor as _floor, sqrt as _sqrt

P1_ONSET = 6                      # the registered universal onset; p2 = onset + plateau length


def _round_half_up(v):
    return int(_floor(float(v) + 0.5))


def model_values(x, n):
    """The REGISTERED RULES, evaluated at the MEASURED n and at log x. Zero free parameters.

    live=True means NOT YET REFUTED at any published window.  L died at x=17 (said 10, measured 11)
    and Z died at x=17 and x=19; they are carried as CONTROLS, because a refuted model that suddenly
    hits would say the refutation was window-specific.  S and A are registered at c55 (weaker than
    L/I/X/Z's cross-cycle c54 seal, and labelled `sealed_at`).
    """
    L13, L19 = _log(13.0), _log(19.0)
    lx = _log(float(x))
    def m(p2, raw, live, rule, sealed_at):
        return dict(p2=p2, raw=raw, live=live, rule=rule, sealed_at=sealed_at,
                    rounding_margin=abs(raw - (_floor(raw) + 0.5)) if raw is not None else None)
    return {
        "L": m(P1_ONSET + _round_half_up(4 * lx / L13), 4 * lx / L13, False,
               "p2 = 6 + round(4*log x / log 13)  -- REFUTED at x=17", "c54"),
        "I": m(_round_half_up(10 + (n - 21) / (38 - 21)), 10 + (n - 21) / (38 - 21), True,
               "p2 = round(10 + (n-21)/(38-21)), n MEASURED", "c54"),
        "X": m(_round_half_up(10 + (lx - L13) / (L19 - L13)), 10 + (lx - L13) / (L19 - L13), True,
               "p2 = round(10 + (log x - log 13)/(log 19 - log 13))", "c54"),
        "Z": m(P1_ONSET + _round_half_up(4.0 * n / 21), 4.0 * n / 21, False,
               "p2 = 6 + round(4n/21), n MEASURED -- REFUTED at x=17 and x=19", "c54"),
        "S": m(P1_ONSET + _round_half_up(4.0 * _sqrt(n / 21.0)), 4.0 * _sqrt(n / 21.0), True,
               "p2 = 6 + round(4*sqrt(n/21)), n MEASURED -- NEW at c55", "c55"),
        "A": m(P1_ONSET + _round_half_up(4.0 * _log(n) / _log(21.0)), 4.0 * _log(n) / _log(21.0), True,
               "p2 = 6 + round(4*log n / log 21), n MEASURED -- NEW at c55", "c55"),
        "G": dict(p2=None, live=False, raw=None, rounding_margin=None, sealed_at="c54",
                  rule="gap turnaround, computed at STAGE A -- REFUTED at x=17 and x=19")}


# The prereg's PRINTED instances, per window.  x=25's row is c54's SEALED column, opened here.
PRINTED_BINS = {22: {"L": 11, "I": 12, "X": 11, "Z": 15, "S": 12, "A": 11},
                25: {"L": 11, "I": 12, "X": 12, "Z": 17, "S": 13, "A": 11}}
SEALED_AT_C54 = {"L": 11, "I": 12, "X": 12, "Z": 17}      # the x=25 column, verbatim from ef19ac5
# The JOINT signatures declared in the prereg, on the pair (p2(22), p2(25)).
JOINT_SIGNATURES = {"A": (11, 11), "X": (11, 12), "I": (12, 12), "S": (12, 13),
                    "L": (11, 11), "Z": (15, 17)}
REGISTERED_TAIL = [4, 2, 2, 3, 1]        # P8: plateau lengths l3..l7
REGISTERED_VALUES = [0, 2, 6, 10, 8, 16, 12]   # P9: the first seven plateau VALUES


def measured_n(x):
    """n from m2_c55_zerocount.json -- MEASURED, with its bracketing ordinates published."""
    fn = os.path.join(HERE, "m2_c55_zerocount.json")
    if not os.path.exists(fn):
        return None
    return json.load(open(fn))["counts"][str(x)]["n"]


def _nodefiles(x, N):
    return {p: os.path.join(HERE, "m2_c55_nodes_%s_x%d_N%d_dps%d.json" % (p, x, N, DPS))
            for p in ("even", "odd")}


def _first_leave(seq, value, start=1):
    for i in range(start, len(seq)):
        if seq[i - 1] == value and seq[i] != value:
            return i + 1
    return None


def plateaus(seq):
    """[(value, length), ...] in pooled order."""
    out = []
    for v in seq:
        if out and out[-1][0] == v:
            out[-1][1] += 1
        else:
            out.append([v, 1])
    return [(v, n) for v, n in out]


def score_window(x):
    """Everything that is a property of ONE window.  Returns the record; writes nothing."""
    S = dict(window=dict(x=x, dps=DPS, gl=GL, N=[100, 180]), depth_legend=DEPTH_LEGEND)
    n100, n180 = _nodefiles(x, 100), _nodefiles(x, 180)
    have100 = all(os.path.exists(f) for f in n100.values())
    have180 = all(os.path.exists(f) for f in n180.values())
    S["inputs"] = dict(N100_present=have100, N180_present=have180,
                       files={k: os.path.basename(v)
                              for k, v in list(n100.items()) + list(n180.items())})
    if not have100:
        S["VERDICT"] = "UNMEASURED -- the N=100 node cells do not exist"
        return S

    tab, cert, float_same = pooled_table(n100)
    S["completeness_certified_prefix"] = cert
    S["float_order_equals_decimal_order"] = bool(float_same)
    S["pooled_table_N100"] = tab
    seq = [r["pooled_delta"] for r in tab]
    S["pooled_delta_N100"] = seq
    S["pooled_parity_order_N100"] = "".join(r["parity"][0] for r in tab)
    S["sector_delta_field_would_have_given"] = [r["sector_delta_FROM_FILE"] for r in tab]
    S["sort_index_vs_sector_field_agree"] = bool(seq == S["sector_delta_field_would_have_given"])

    depth, det = n_control_depth(n100, n180) if have180 else (0, dict(reason="N=180 cells absent"))
    S["n_control_trusted_depth"] = depth
    S["n_control_detail"] = det

    def scored_over(p):
        return p is not None and depth >= p

    # ---- P1 onset (control, declared WEAK)
    p1 = _first_leave(seq, 0)
    S["P1"] = dict(measured_p1=p1, registered=6,
                   verdict=("UNMEASURED (outside trust)" if not scored_over(p1)
                            else ("HELD" if p1 == 6 else "REFUTED")),
                   confirmation_note="declared WEAK in advance: UNINFORMATIVE-if-passed.")

    # ---- P2 the target
    p2 = _first_leave(seq, 2)
    n_meas = measured_n(x)
    MODELS = model_values(x, n_meas)
    bin_check = {k: dict(rule_value=MODELS[k]["p2"], printed_in_prereg=PRINTED_BINS[x][k],
                         agree=bool(MODELS[k]["p2"] == PRINTED_BINS[x][k]),
                         raw=MODELS[k]["raw"], rounding_margin=MODELS[k]["rounding_margin"])
                 for k in PRINTED_BINS[x]}
    S["measured_zero_count_n"] = n_meas
    S["rule_vs_printed_bin"] = bin_check
    S["rule_vs_printed_bin_all_agree"] = all(v["agree"] for v in bin_check.values())
    if x == 25:
        S["sealed_column_c54"] = dict(
            sealed=SEALED_AT_C54,
            rule_values_now={k: MODELS[k]["p2"] for k in SEALED_AT_C54},
            agree=all(MODELS[k]["p2"] == SEALED_AT_C54[k] for k in SEALED_AT_C54),
            note="c54's P8, sealed at ef19ac5 2026-09-09T00:17:40Z before x=17 was computed; "
                 "OPENED and scored here, never re-derived.")
    sweep = {str(nn): {k: v["p2"] for k, v in model_values(x, nn).items() if v["p2"] is not None}
             for nn in range(max(n_meas - 4, 1), n_meas + 5)}
    S["n_sweep_of_the_rules"] = sweep
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
                   knife_edge_occupants=[k for k in occupants
                                         if (MODELS[k]["rounding_margin"] or 1) < 0.05],
                   discrimination=("NONE -- more than one registered model names this bin"
                                   if len(occupants) > 1 else
                                   ("SINGLE OCCUPANT" if len(occupants) == 1 else
                                    "EMPTY BIN -- every registered model is refuted at this window")),
                   verdict=("UNMEASURED (outside trust)" if not scored_over(p2) else "MEASURED"))

    # ---- P3 the size
    inc = None if p2 is None or p2 > len(seq) else seq[p2 - 1] - 2
    S["P3"] = dict(registered=4, measured_increment=inc,
                   verdict=("UNMEASURED (outside trust)" if not scored_over(p2)
                            else ("HELD" if inc == 4 else "REFUTED")))

    # ---- P4 the invariance
    p3 = _first_leave(seq, 6)
    S["P4"] = dict(registered=15, measured_p3=p3,
                   verdict=("UNMEASURED (outside trust)" if not scored_over(p3)
                            else ("HELD" if p3 == 15 else "REFUTED")),
                   note="registered as an INVARIANCE: p3 = 15 at x = 13, 17 and 19 while p2 moved.")

    # ---- P5 the decrease
    got = {p: (seq[p - 1] if p <= len(seq) else None) for p in (15, 16, 17)}
    ok5 = (got[15] == 10 and got[16] == 10 and got[17] == 8)
    S["P5"] = dict(registered=dict(p15=10, p16=10, p17=8), measured=got,
                   verdict=("UNMEASURED (outside trust)" if depth < 17
                            else ("HELD" if ok5 else "REFUTED")))

    # ---- P6 the N-control
    S["P6"] = dict(registered_floor=23, measured_depth=depth, detail=det,
                   verdict=("UNMEASURED (N=180 absent)" if not have180
                            else ("HELD" if depth >= 23 else "REFUTED")))

    # ---- P7 alternation through trust
    order = S["pooled_parity_order_N100"][:max(depth, 0)]
    alt = all(order[i] != order[i + 1] for i in range(len(order) - 1)) if len(order) > 1 else None
    S["P7"] = dict(order_through_trust=order, depth=depth,
                   verdict=("UNMEASURED" if not order else ("HELD" if alt else "REFUTED")))

    # ---- P8 plateau lengths (tail l3..l7 only: l1 is P1 and l2 is P2 restated)
    pl = plateaus(seq)
    lens = [n for _v, n in pl]
    vals = [v for v, _n in pl]
    inside = sum(lens[:7]) <= depth
    tail = lens[2:7]
    S["P8"] = dict(registered_tail_l3_to_l7=REGISTERED_TAIL, measured_tail=tail,
                   all_lengths=lens[:8], reference_x17_x19=[5, 5, 4, 2, 2, 3, 1],
                   reference_x13=[5, 4, 5, 2, 1, 3, 1],
                   verdict=("UNMEASURED (the first seven plateaux reach past the trusted depth)"
                            if not inside else ("HELD" if tail == REGISTERED_TAIL else "REFUTED")))

    # ---- P9 plateau values
    S["P9"] = dict(registered=REGISTERED_VALUES, measured=vals[:7],
                   verdict=("UNMEASURED (outside trust)" if not inside
                            else ("HELD" if vals[:7] == REGISTERED_VALUES else "REFUTED")))

    # ---- P10 the eighth value, DIRECTION only, declared WEAK (outcome space 3)
    eighth = vals[7] if len(vals) > 7 else None
    eighth_inside = (sum(lens[:8]) <= depth) if len(lens) > 7 else False
    S["P10"] = dict(registered="< 16 (direction only; 24/20/16 at x=13/17/19)",
                    measured_eighth_value=eighth, reference=[24, 20, 16],
                    verdict=("UNMEASURED (outside trust)" if not eighth_inside
                             else ("HELD" if eighth < 16 else "REFUTED")),
                    strength="WEAK by declaration: outcome space 3, worth one bit at most.")

    # ---- P11 model G, from the stage-A file
    g = os.path.join(HERE, "m2_c55_gpred_x%d_N%d_dps%d.json" % (x, 100, DPS))
    if os.path.exists(g):
        gd = json.load(open(g))
        S["P2"]["models"]["G"]["p2"] = gd.get("model_G_p2")
        S["P11"] = dict(registered=10, measured=gd.get("model_G_p2"),
                        first_local_min_index=gd.get("first_local_min_index"),
                        first_local_max_after=gd.get("first_local_max_after"),
                        verdict=("HELD" if gd.get("model_G_p2") == 10 else "REFUTED"),
                        note="a prediction about the EIGENVALUE ladder alone, settled at stage A "
                             "before any node count of this window existed.")
        if gd.get("model_G_p2") is not None:
            S["P2"]["bins"].setdefault(str(gd["model_G_p2"]), [])
            if "G" not in S["P2"]["bins"][str(gd["model_G_p2"])]:
                S["P2"]["bins"][str(gd["model_G_p2"])].append("G")
            if gd["model_G_p2"] == p2 and "G" not in S["P2"]["occupants"]:
                S["P2"]["occupants"].append("G")
                S["P2"]["discrimination"] = ("NONE -- more than one registered model names this bin"
                                             if len(S["P2"]["occupants"]) > 1
                                             else S["P2"]["discrimination"])
    else:
        S["P11"] = dict(verdict="UNMEASURED -- no stage-A gpred artefact for this window")

    # ---- the FORK, evaluated rather than narrated
    l2 = (p2 - p1) if (p2 and p1) else None
    l3 = (p3 - p2) if (p3 and p2) else None
    S["FORK"] = dict(identity="p3 = 6 + l2 + l3 ; the p3=15 invariance IS l2 + l3 = 9",
                     l2=l2, l3=l3, sum_l2_l3=(None if l2 is None or l3 is None else l2 + l3),
                     invariance_holds=(None if l2 is None or l3 is None else (l2 + l3 == 9)),
                     reading=("p2 moved and p3 stayed: the invariance absorbed the move"
                              if (l2 is not None and l3 is not None and l2 + l3 == 9)
                              else "the invariance did NOT absorb the move"))
    return S


def score():
    """Both windows, then the JOINT criterion registered in the prereg."""
    OUT = dict(cycle=55, windows={}, generated_by=os.path.basename(__file__))
    for x in WINDOWS:
        OUT["windows"][str(x)] = score_window(x)

    pair = tuple(OUT["windows"][str(x)].get("P2", {}).get("measured_p2") for x in WINDOWS)
    depths = {str(x): OUT["windows"][str(x)].get("n_control_trusted_depth") for x in WINDOWS}
    both = all(v is not None for v in pair)
    named = sorted(k for k, sig in JOINT_SIGNATURES.items() if both and tuple(sig) == pair)
    live_named = [k for k in named if k in ("I", "X", "S", "A")]
    if not both:
        verdict = "UNMEASURED -- one or both windows did not produce p2 inside trust"
    elif not named:
        verdict = ("EVERY REGISTERED RULE REFUTED -- the measured pair %s matches no registered "
                   "signature" % (pair,))
    elif len(named) == 1:
        verdict = "CONFIRMED: %s is the sole registered namer of the pair %s" % (named[0], pair)
    else:
        verdict = ("NO BANK -- the pair %s is named by more than one registered rule (%s); the "
                   "strict criterion blocks a bank even when only one of them is live"
                   % (pair, ", ".join(named)))
    OUT["JOINT"] = dict(windows=list(WINDOWS), measured_pair=list(pair),
                        signatures={k: list(v) for k, v in JOINT_SIGNATURES.items()},
                        namers=named, live_namers=live_named, verdict=verdict,
                        criterion="a model is CONFIRMED only if it names BOTH measured values and no "
                                  "other REGISTERED model (live or refuted control) names both.",
                        trusted_depths=depths)
    json.dump(OUT, open(os.path.join(HERE, "m2_c55_scores.json"), "w"), indent=1)

    for x in WINDOWS:
        S = OUT["windows"][str(x)]
        if "pooled_delta_N100" not in S:
            print("x=%d: %s" % (x, S.get("VERDICT")))
            continue
        print("x=%d  certificate=%s  N-control trusted depth=%s"
              % (x, S["completeness_certified_prefix"], S["n_control_trusted_depth"]))
        print("  pooled Delta (N=100): %s" % S["pooled_delta_N100"])
        print("  parity order        : %s" % S["pooled_parity_order_N100"])
        print("  p1=%s p2=%s size=%s p3=%s   plateau lengths %s"
              % (S["P1"]["measured_p1"], S["P2"]["measured_p2"], S["P3"]["measured_increment"],
                 S["P4"]["measured_p3"], S["P8"]["all_lengths"]))
        print("  occupants of bin %s: %s   live: %s   knife-edge: %s"
              % (S["P2"]["occupied_bin"], S["P2"]["occupants"], S["P2"]["live_occupants"],
                 S["P2"]["knife_edge_occupants"]))
        print("  FORK: l2=%s l3=%s sum=%s invariance_holds=%s"
              % (S["FORK"]["l2"], S["FORK"]["l3"], S["FORK"]["sum_l2_l3"],
                 S["FORK"]["invariance_holds"]))
        for k in ("P1", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11"):
            print("    %s: %s" % (k, S.get(k, {}).get("verdict")))
        if x == 25 and "sealed_column_c54" in S:
            print("  SEALED c54 column agrees with the rules re-evaluated at measured n: %s"
                  % S["sealed_column_c54"]["agree"])
    print("JOINT: pair=%s -> %s" % (OUT["JOINT"]["measured_pair"], OUT["JOINT"]["verdict"]))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "kat_na":
        sys.exit(kat_na())
    if cmd == "fixture_d":
        sys.exit(fixture_d())
    if cmd == "score":
        sys.exit(score())
    print(__doc__)
    sys.exit(2)
