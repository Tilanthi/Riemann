#!/usr/bin/env python3
"""m2_c51_score.py -- the SEALED grader for cycle 51. Sealed with the prereg, BEFORE any cell ran.

It reads only the cells named in the prereg, applies the pre-stated rules, and prints one verdict
per registered prediction. It never chooses a threshold at read time: every threshold below is a
literal in this file, sealed by sha256 in the prereg.

usage: m2_c51_score.py            (no arguments; resolves cells beside itself)
"""
import json, os, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- sealed literals -------------------------------------------------------------------------
CAL = "x13_N100"                       # the calibration window (c50's, the one that produced the claim)
ONSET_N = {"even": 4, "odd": 3}        # Model N: the dislocation's sector index, universal
DELTA_N = {"even": [0, 0, 0, 2, 2], "odd": [0, 0, 2, 2, 6]}   # Model N: the full vector, m=1..5
NZERO = {5: 4, 13: 21, 19: 38}         # c46's measured zero counts n = #{0 < gamma <= 2 pi x}
THRESH_LO = Decimal("-43.9259")        # last EXACT pooled rung at the calibration window
THRESH_HI = Decimal("-40.6436")        # first DEFECTIVE pooled rung there
KAT_FRONTIER = Decimal("5.0e-3")       # measured in m2_c51_kat.json: all 9 knobs true down to here
CELLS = [("even", 5, 100, 5), ("odd", 5, 100, 5),
         ("even", 19, 100, 5), ("odd", 19, 100, 5),
         ("even", 13, 180, 5), ("odd", 13, 180, 5),
         ("even", 13, 100, 7), ("odd", 13, 100, 7)]
NEW_WINDOWS = [(5, 100), (19, 100), (13, 180)]      # windows that did NOT produce the claim


def half_up(x):
    """round-half-up, floor 1 -- the rounding rule Model SCALING is scored under, sealed here."""
    n = int(x + Decimal("0.5"))
    return max(1, n)


def load():
    cells = {}
    for par, X, N, K in CELLS:
        fn = os.path.join(HERE, "m2_c51_nodes_%s_x%d_N%d_k%d.json" % (par, X, N, K))
        cells[(par, X, N)] = json.load(open(fn)) if os.path.exists(fn) else None
    return cells


def rungs_admitted(cell):
    """the rungs this cycle may speak about: admitted by the c50 residual rule AND knob-stable."""
    return [r for r in cell["rungs"] if r["admitted"] and r["stable"]]


def main():
    cells = load()
    missing = [k for k, v in cells.items() if v is None]
    R = {"missing_cells": ["%s x%d N%d" % (p, x, n) for (p, x, n) in missing]}
    if missing:
        print("MISSING CELLS: %s" % R["missing_cells"])
    lines = []

    # ---------- census of what is speakable at all
    census = {}
    for (par, X, N), cell in cells.items():
        if cell is None:
            continue
        adm = rungs_admitted(cell)
        census["%s_x%d_N%d" % (par, X, N)] = dict(
            computed=len(cell["rungs"]), admitted=len(adm),
            dropped_residual=sum(1 for r in cell["rungs"] if not r["admitted"]),
            dropped_unstable=sum(1 for r in cell["rungs"] if r["admitted"] and not r["stable"]),
            delta=[r["delta"] for r in adm], nu=[r["nu"] for r in adm],
            log10=[r["log10"] for r in adm])
    R["census"] = census
    lines.append("CENSUS (counts, never ratios):")
    for k in sorted(census):
        c = census[k]
        lines.append("  %-16s computed %d  admitted %d  dropped(resid) %d  dropped(unstable) %d  delta %s"
                     % (k, c["computed"], c["admitted"], c["dropped_residual"],
                        c["dropped_unstable"], c["delta"]))

    # ---------- P7 instrument gate (runs FIRST: no object claim survives its failure)
    ref_fail, lobe_fail, lobes = 0, 0, []
    for (par, X, N), cell in cells.items():
        if cell is None:
            continue
        for r in rungs_admitted(cell):
            if r["nu_refine_48001"] != r["nu"]:
                ref_fail += 1
            lr = Decimal(r["lobe_min_ratio"])
            lobes.append((("%s_x%d_N%d_r%d" % (par, X, N, r["rung"])), str(lr)))
            if lr <= KAT_FRONTIER:
                lobe_fail += 1
    R["P7"] = dict(refine_mismatches=ref_fail, lobes_at_or_below_frontier=lobe_fail,
                   frontier=str(KAT_FRONTIER), lobe_min_ratios=lobes,
                   verdict=("HELD" if ref_fail == 0 and lobe_fail == 0 else "FAILED"))
    lines.append("P7 (instrument): refine mismatches %d ; admitted rungs at/below the KAT frontier "
                 "%s: %d  -> %s" % (ref_fail, KAT_FRONTIER, lobe_fail, R["P7"]["verdict"]))

    # ---------- P1 Sturm prefix at the three new windows
    p1_tested = p1_fail = 0
    p1_detail = []
    for (X, N) in NEW_WINDOWS:
        for par, pref in (("even", [1, 2, 3]), ("odd", [1, 2])):
            cell = cells.get((par, X, N))
            if cell is None:
                continue
            for r in rungs_admitted(cell):
                if r["rung"] in pref:
                    p1_tested += 1
                    if r["delta"] != 0:
                        p1_fail += 1
                        p1_detail.append("%s x%d N%d rung %d delta=%s" % (par, X, N, r["rung"], r["delta"]))
    R["P1"] = dict(tested=p1_tested, failed=p1_fail, detail=p1_detail,
                   verdict=("HELD" if p1_fail == 0 and p1_tested > 0 else
                            ("REFUTED" if p1_fail else "CENSORED")))
    lines.append("P1 (Sturm prefix, new windows): %d integers tested, %d nonzero -> %s %s"
                 % (p1_tested, p1_fail, R["P1"]["verdict"], p1_detail))

    # ---------- onsets, measured once and used by every model
    onsets = {}
    for (par, X, N), cell in cells.items():
        if cell is None:
            continue
        adm = rungs_admitted(cell)
        on = None
        for r in adm:
            if r["delta"] != 0:
                on = r["rung"]
                break
        onsets["%s_x%d_N%d" % (par, X, N)] = dict(
            onset=on, censored_at=(len(adm) if on is None else None),
            first_delta=(None if on is None else [r["delta"] for r in adm if r["rung"] == on][0]))
    R["onsets"] = onsets
    lines.append("ONSETS (measured): %s" % {k: v["onset"] for k, v in sorted(onsets.items())})

    # ---------- P2 Model N onset universality
    p2 = {}
    for (par, X, N, K) in CELLS:
        key = "%s_x%d_N%d" % (par, X, N)
        if key not in onsets:
            continue
        o = onsets[key]
        if o["onset"] is None:
            p2[key] = "CENSORED(no defect through %d admitted rungs)" % o["censored_at"]
        elif o["onset"] == ONSET_N[par]:
            p2[key] = "HELD(%d)" % o["onset"]
        else:
            p2[key] = "REFUTED(%d, predicted %d)" % (o["onset"], ONSET_N[par])
    held = sum(1 for v in p2.values() if v.startswith("HELD"))
    refu = sum(1 for v in p2.values() if v.startswith("REFUTED"))
    cens = sum(1 for v in p2.values() if v.startswith("CENSORED"))
    R["P2"] = dict(per_cell=p2, held=held, refuted=refu, censored=cens,
                   verdict=("REFUTED" if refu else ("HELD" if cens == 0 else "HELD-WITH-CENSORING")))
    lines.append("P2 (Model N onset (4,3) universal): held %d  refuted %d  censored %d -> %s"
                 % (held, refu, cens, R["P2"]["verdict"]))
    for k in sorted(p2):
        lines.append("     %-16s %s" % (k, p2[k]))

    # ---------- P3 first defect size
    p3 = {k: v["first_delta"] for k, v in onsets.items() if v["first_delta"] is not None}
    bad3 = {k: v for k, v in p3.items() if v != 2}
    R["P3"] = dict(first_deltas=p3, not_two=bad3,
                   verdict=("HELD" if p3 and not bad3 else ("REFUTED" if bad3 else "CENSORED")))
    lines.append("P3 (first defect == +2): %s -> %s" % (p3, R["P3"]["verdict"]))

    # ---------- P4 N-control (declared NOT independent of P2: it is P2's x=13,N=180 conjunct)
    p4 = {k: v for k, v in p2.items() if k.endswith("x13_N180")}
    R["P4"] = dict(per_cell=p4, independent_of_P2=False,
                   verdict=("HELD" if p4 and all(v.startswith("HELD") for v in p4.values())
                            else ("REFUTED" if any(v.startswith("REFUTED") for v in p4.values())
                                  else "CENSORED")))
    lines.append("P4 (N-control, NOT independent of P2): %s -> %s" % (p4, R["P4"]["verdict"]))

    # ---------- P5 monotone delta, deep arm k=7 at the calibration window
    p5_fail, p5_seq = [], {}
    for par in ("even", "odd"):
        cell = cells.get((par, 13, 100))
        if cell is None:
            continue
        d = [r["delta"] for r in rungs_admitted(cell)]
        p5_seq[par] = d
        for i in range(1, len(d)):
            if d[i] < d[i - 1]:
                p5_fail.append("%s rung %d: %d < %d" % (par, i + 1, d[i], d[i - 1]))
    R["P5"] = dict(sequences=p5_seq, decreases=p5_fail,
                   verdict=("HELD" if p5_seq and not p5_fail else ("REFUTED" if p5_fail else "CENSORED")))
    lines.append("P5 (delta non-decreasing, k=7 deep arm): %s -> %s" % (p5_seq, R["P5"]["verdict"]))

    # ---------- P6 THE ABSOLUTE TEST of Model N: the full admitted delta vector, tolerance 0
    p6_tested = p6_fail = 0
    p6_detail = []
    for (X, N) in NEW_WINDOWS:
        for par in ("even", "odd"):
            cell = cells.get((par, X, N))
            if cell is None:
                continue
            for r in rungs_admitted(cell):
                if r["rung"] <= 5:
                    p6_tested += 1
                    exp = DELTA_N[par][r["rung"] - 1]
                    if r["delta"] != exp:
                        p6_fail += 1
                        p6_detail.append("%s x%d N%d rung %d: delta %s, Model N says %d"
                                         % (par, X, N, r["rung"], r["delta"], exp))
    R["P6"] = dict(tested=p6_tested, mismatches=p6_fail, detail=p6_detail,
                   verdict=("HELD" if p6_tested and p6_fail == 0 else
                            ("REFUTED" if p6_fail else "CENSORED")),
                   note="ABSOLUTE: decided with no reference to any competing model (c50's law).")
    lines.append("P6 (ABSOLUTE full-vector test of Model N): %d integers tested, %d mismatches -> %s"
                 % (p6_tested, p6_fail, R["P6"]["verdict"]))
    for d in p6_detail:
        lines.append("     %s" % d)

    # ---------- P8 the comparison (explicitly NOT validation)
    comp = {}
    for (X, N) in NEW_WINDOWS + [(13, 100)]:
        for par in ("even", "odd"):
            key = "%s_x%d_N%d" % (par, X, N)
            if key not in onsets:
                continue
            meas = onsets[key]["onset"]
            adm = rungs_admitted(cells[(par, X, N)])
            pred_N = ONSET_N[par]
            scal = Decimal(ONSET_N[par]) * Decimal(NZERO[X]) / Decimal(NZERO[13])
            pred_S = half_up(scal)
            # THRESHOLD: first admitted rung whose log10 lambda exceeds the calibrated band
            pred_T, ambig = None, False
            for r in adm:
                lg = Decimal(r["log10"])
                if lg > THRESH_HI:
                    pred_T = r["rung"]
                    break
                if THRESH_LO < lg <= THRESH_HI:
                    ambig = True
            def score(pred):
                if pred is None:
                    return "no-defect-through-%d" % len(adm), (meas is None)
                if pred > len(adm):
                    return "onset>%d (beyond computed)" % len(adm), (meas is None)
                return str(pred), (meas == pred)
            sN, okN = score(pred_N)
            sS, okS = score(pred_S)
            sT, okT = score(pred_T)
            comp[key] = dict(measured=meas, admitted=len(adm),
                             N=dict(pred=sN, correct=okN),
                             SCALING=dict(pred=sS, correct=okS, raw=str(scal)),
                             THRESHOLD=dict(pred=sT, correct=okT, ambiguous_rung_present=ambig))
    tally = {m: sum(1 for v in comp.values() if v[m]["correct"]) for m in ("N", "SCALING", "THRESHOLD")}
    R["P8"] = dict(per_cell=comp, tally=tally, denominator=len(comp),
                   note="A COMPARISON IS NOT A VALIDATION (c50). Read this line beside P6's verdict.")
    lines.append("P8 (comparison, NOT validation): out of %d cells, correct onsets -- "
                 "Model N %d / SCALING %d / THRESHOLD %d"
                 % (len(comp), tally["N"], tally["SCALING"], tally["THRESHOLD"]))
    for k in sorted(comp):
        v = comp[k]
        lines.append("     %-16s measured %-5s  N %-6s %-5s  SCALING %-6s %-5s  THRESHOLD %-24s %s"
                     % (k, v["measured"], v["N"]["pred"], v["N"]["correct"],
                        v["SCALING"]["pred"], v["SCALING"]["correct"],
                        v["THRESHOLD"]["pred"], v["THRESHOLD"]["correct"]))

    # ---------- Theorem T as an instrument check over every cell (never as a prediction)
    tfail = 0
    for (par, X, N), cell in cells.items():
        if cell is None:
            continue
        for r in cell["rungs"]:
            if r["parity_T_ok"] is False:
                tfail += 1
    R["theoremT_violations"] = tfail
    lines.append("Theorem T (node-count parity == sector parity; an INSTRUMENT check, not a "
                 "prediction): %d violations over every computed rung" % tfail)

    out = "\n".join(lines)
    print(out)
    json.dump(R, open(os.path.join(HERE, "m2_c51_scores.json"), "w"), indent=1)
    open(os.path.join(HERE, "m2_c51_scores.out"), "w").write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
