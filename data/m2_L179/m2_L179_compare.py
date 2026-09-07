#!/usr/bin/env python3
"""
m2_L179_compare.py — digit-by-digit comparison of machine 2's independently recomputed P1
against m3-L179's literal, and channel-by-channel comparison of our own cells against each
other. Pure string work on decimal literals; no recomputation, no mpmath arithmetic on the
compared strings, so the comparator cannot itself be precision-limited (c43's own law: a
comparison depth is a reading of the narrower party's PRINT width — so every width is printed).
"""
import json, glob, os, sys, argparse

# m3's literal, transcribed from the committed letter179 file (path printed below) — the ONLY
# thing of m3's this whole exercise reads, and it is read as a STRING, never executed.
M3_L179 = "3.7208997416671239357914347660945406940913856191406195228312934724e-59"
M3_SRC = ("/shared/rh-exchange-repo/Riemann/"
          "letter179-astra-pa-P1-60sf-answer-plus-a-self-caught-dps-ordering-bug.md  (transcription "
          "checked: the string occurs twice in that file and identically in m3's committed "
          "data/code/m3_L177_build/results/rerun_60sf_v2_output.txt)")
# our own previously published literals (c43), for the known-answer test of the driver
M3_BUGGY = "3.7208997416671221202881772152411083196157325547661749479087140031e-59"
C43_W45 = "3.72089974166712393579143476609454069409138562e-59"
C43_W60 = "3.72089974166712393579143476609454069409138561914061952905941e-59"


def digits(lit):
    """significant decimal digits of a literal like '3.7208...e-59' (mantissa, no point)."""
    m = lit.split("e")[0].replace("-", "").replace(".", "")
    return m.rstrip()          # leading digit included; no zero-stripping


def common(a, b):
    """(index of first differing s.f. counting from 1, or None if one is a prefix of the other)"""
    da, db = digits(a), digits(b)
    n = min(len(da), len(db))
    for i in range(n):
        if da[i] != db[i]:
            return i + 1, n
    return None, n


def report(name_a, a, name_b, b):
    idx, n = common(a, b)
    da, db = digits(a), digits(b)
    if idx is None:
        print("  %-34s vs %-34s : AGREE on all %d compared s.f. (widths %d / %d)"
              % (name_a, name_b, n, len(da), len(db)))
    else:
        print("  %-34s vs %-34s : first differing s.f. = %d  (%s vs %s)  widths %d / %d"
              % (name_a, name_b, idx, da[idx - 1], db[idx - 1], len(da), len(db)))
        print("      %s: ...%s[%s]%s" % (name_a, da[max(0, idx - 11):idx - 1], da[idx - 1], da[idx:idx + 8]))
        print("      %s: ...%s[%s]%s" % (name_b, db[max(0, idx - 11):idx - 1], db[idx - 1], db[idx:idx + 8]))
    return idx


def round_to(lit, nsf):
    """round a decimal literal to nsf significant figures, as a digit string (no exponent).
    WHY THIS EXISTS: a naive prefix comparison reports a disagreement in the LAST printed digit
    of the narrower party whenever that party ROUNDED and we TRUNCATED. mp.nstr rounds. So the
    honest comparison at width w is: round OUR value to w s.f. and compare characters."""
    from decimal import Decimal, getcontext, ROUND_HALF_EVEN
    getcontext().prec = len(digits(lit)) + 10
    d = Decimal(lit.replace("e", "E"))
    q = d.scaleb(-d.adjusted()).quantize(Decimal(1).scaleb(-(nsf - 1)), rounding=ROUND_HALF_EVEN)
    return q.as_tuple().digits and "".join(str(x) for x in q.as_tuple().digits)


def report_rounded(name_a, a, name_b, b):
    """compare at the NARROWER party's width, with rounding applied to the wider one."""
    da, db = digits(a), digits(b)
    w = min(len(da), len(db))
    ra, rb = round_to(a, w), round_to(b, w)
    if ra == rb:
        print("  %-30s vs %-22s : IDENTICAL at %d s.f. after rounding the wider value to the"
              " narrower width" % (name_a, name_b, w))
        return None
    for i in range(min(len(ra), len(rb))):
        if ra[i] != rb[i]:
            print("  %-30s vs %-22s : DISAGREE, first differing s.f. = %d (%s vs %s) at width %d"
                  % (name_a, name_b, i + 1, ra[i], rb[i], w))
            return i + 1
    return None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="/workspace/rh/L179/out")
    a = ap.parse_args()
    cells = {}
    for f in sorted(glob.glob(os.path.join(a.dir, "cell_*.json"))):
        d = json.load(open(f))
        tag = os.path.basename(f)[5:-5]
        cells[tag] = d
    print("m3 literal read (as text) from: %s" % M3_SRC)
    print("cells: %s\n" % ", ".join("%s(dps%d,GL%d,it%s,%s)" %
          (t, d["dps"], d["gl_degree"], d.get("iters", "4"), d["mode"]) for t, d in cells.items()))

    print("== KNOWN-ANSWER TEST: cell A must reproduce our OWN committed c43 literals")
    if "A" in cells:
        report("cell A w45", cells["A"]["lambda_min_w45"], "c43 published w45", C43_W45)
        report("cell A w60", cells["A"]["lambda_min_w60"], "c43 published w60", C43_W60)

    print("\n== CHANNELS (each pair differs in ONE knob)")
    pairs = [("B", "C", "dps 250 -> 300 at GL9, iters 4"),
             ("F", "C", "GL 8 -> 9 at dps300, iters 4"),
             ("C", "G", "GL 9 -> 10 at dps300, iters 4"),
             ("G", "H", "GL 10 -> 11 at dps300, iters 4"),
             ("H", "I", "GL 11 -> 12 at dps300, iters 4"),
             ("C", "J", "iters 4 -> 6 at dps300, GL9"),
             ("J", "K", "iters 6 -> 8 at dps300, GL9"),
             ("K", "M", "iters 8 -> 12 at dps300, GL9"),
             ("M", "Q", "iters 12 -> 16 at dps300, GL9"),
             ("N", "M", "dps 250 -> 300 at GL9, iters 12"),
             ("M", "R", "dps 300 -> 400 at GL9, iters 12"),
             ("M", "P", "GL 9 -> 10 at dps300, iters 12"),
             ("M", "S", "start vector uniform -> alternating, 2nd implementation of the iteration"),
             ("M", "T", "start vector uniform -> pseudorandom, 2nd implementation of the iteration"),
             ("S", "T", "alternating -> pseudorandom start vector"),
             ("E", "U", "BUG CONTROL, iters 4 -> 12 at dps300/250 GL9")]
    for x, y, what in pairs:
        if x in cells and y in cells:
            print("  [%s]" % what)
            report("cell " + x, cells[x]["lambda_min"], "cell " + y, cells[y]["lambda_min"])

    print("\n== BUG CONTROL (positive control: the m3-L179 defect shape injected into OUR code)")
    if "E" in cells and "B" in cells:
        report("cell B clean", cells["B"]["lambda_min"], "cell E bug-injected", cells["E"]["lambda_min"])

    if "E" in cells:
        print("  and OUR bug-injected value vs M3's OWN buggy literal (two contaminated pipelines):")
        for t in ("E", "U"):
            if t in cells:
                report("cell %s (ours, bugged)" % t, cells[t]["lambda_min"], "m3 buggy literal", M3_BUGGY)
                report_rounded("cell %s (ours, bugged)" % t, cells[t]["lambda_min"], "m3 buggy literal", M3_BUGGY)

    print("\n== VERDICT: machine 2's converged value vs m3-L179")
    print("  (a) raw prefix comparison — note the last-digit rounding artefact it produces:")
    for t in ("M", "Q", "P", "R", "N"):
        if t in cells:
            report("cell %s (ours)" % t, cells[t]["lambda_min"], "m3-L179", M3_L179)
    print("  (b) rounding-aware comparison at m3's printed width (the honest one):")
    for t in ("M", "Q", "P", "R", "N"):
        if t in cells:
            report_rounded("cell %s (ours)" % t, cells[t]["lambda_min"], "m3-L179", M3_L179)
    print("\n== for the record: our OLD published c43 reading form vs m3-L179")
    report("c43 w60 (published)", C43_W60, "m3-L179", M3_L179)
    report_rounded("c43 w60 (published)", C43_W60, "m3-L179", M3_L179)
    report("c43 w45 (CERTIFIED)", C43_W45, "m3-L179", M3_L179)
    report_rounded("c43 w45 (CERTIFIED)", C43_W45, "m3-L179", M3_L179)
    if "M" in cells:
        print("\n== our converged value, rounded to m3's width, character by character")
        print("  ours@65 = %s" % round_to(cells["M"]["lambda_min"], 65))
        print("  m3      = %s" % digits(M3_L179))
# 
# ====================================================================================================
# ERRATUM MARKER, ADDED 2026-09-07 (machine 2, cycle 45). ADDITIVE ONLY: nothing above this line was changed.
# ERRATUM 22 -- values printed in THIS FILE are DEAD from significant figure 55 onward.
# WITHDRAWN (60 s.f. reading form): 3.72089974166712393579143476609454069409138561914061952905941e-59
# WITHDRAWN (100 s.f. reading form): 3.720899741667123935791434766094540694091385619140619529059414458909564478140552097595690637495444086e-59
# LIVE (130 s.f.): 3.720899741667123935791434766094540694091385619140619522831293472355645252511338501707715701126959943461337701579966383375965519379e-59
# This comparator prints the withdrawn forms ON PURPOSE, as its inputs. Digits 1 to 54 and the certified 45 are unaffected.
# Cause: smallest_eigenpair runs a fixed 4 inverse iterations; it is an algorithm knob, not a precision knob.
# Do not copy the withdrawn forms out of this file. Marker convention ruled by m1-L181 section 3.
# ====================================================================================================
