"""machine2 CYCLE 29 PART B -- THE GRADER for the sealed S3=D4 scored run.

WRITTEN AND HASHED BEFORE THE SEALED RUNNER WAS EXECUTED.  Its sha256 is recorded in
/shared/progress/rh-cycle29.md ahead of the first scored value, so that "graded against the
hypotheses AS FROZEN" is a checkable statement and not a claim about my intentions.

It reads exactly two files:
  1. the sealed prereg JSON  (sha256 238187e2a9c193c8f8c480ff033b7c952e3b661f67c3236848ac7b701087db0f)
     -- for the bands, the ty4 point predictions and the machine-readable `hypotheses` array;
  2. the scored runner's own output JSON  (c27_s3_scored.json), untouched.

Cycle-28 self-catch (i) said: a prereg in prose graded by a parser is two documents that can
disagree.  So the thresholds below are transcribed ONCE, here, from the frozen `fires_against_me_if`
strings, and the transcription is printed beside every verdict for a reader to check by eye.

THREE DECLARED GRADING CONVENTIONS, fixed before any value existed:
  (A) H3's frozen claim has TWO parts (lands in [0.547,2.189]  AND  therefore outside the PT band)
      but its frozen falsifier names only ONE interval ([0.100,0.401]).  A value outside BOTH would
      leave the claim unheld and the falsifier unfired.  That third outcome is graded
      NEITHER-HELD-NOR-FIRED and is reported as such; it is not silently rounded to either side.
  (B) H6 is graded on  R_c(R2)/R_c(R3)  -- the ratio the frozen claim names, whose ty4 value is
      0.1645733612/0.2434402706 = 0.67603.  The runner ALSO prints a quantity it labels
      "PRIMARY ratio", which is (defect fraction pct R2)/(pct R3) -- a DIFFERENT number.  Grading
      H6 on the runner's printed headline would be grading the wrong statistic.
  (C) every threshold is applied at the frozen digits, inclusive at the endpoints (the frozen text
      says "lands in"/"outside"), and any value within 1 part in 1e6 of an endpoint is additionally
      flagged BOUNDARY so no verdict rests on an undeclared tie-break.
"""
import json, os, sys
from decimal import Decimal, getcontext

getcontext().prec = 60
REPO = "/shared/rh-exchange-repo/Riemann"
PRE = json.load(open(os.path.join(REPO, "data/machine2_cycle27_s3_prereg.json")))
SC = json.load(open(sys.argv[1]))

D = lambda x: Decimal(str(x))
COMPOSED = ("R2", "R3", "R3b", "R4")
ALLRUNGS = ("R0", "R1", "R2", "R1b", "R3", "R1e", "R3b", "R0s", "R1d", "R4")
EPS = Decimal("1e-6")


def boundary(v, lo, hi):
    for e in (lo, hi):
        if e != 0 and abs((v - e) / e) < EPS:
            return True
    return False


verdicts = []


def emit(hid, name, held, detail, threshold, extra=""):
    verdicts.append({"id": hid, "name": name, "verdict": held, "threshold_as_frozen": threshold,
                     "detail": detail, "extra": extra})
    print("\n%-4s %-52s  ==> %s" % (hid, name, held))
    print("     threshold as frozen : %s" % threshold)
    for line in detail:
        print("     %s" % line)
    if extra:
        print("     NOTE: %s" % extra)


# ---------------- H1 ----------------
det, outside = [], []
for r in COMPOSED:
    lo, hi = [D(x) for x in PRE["H1_PT_band"][r]["band"]]
    v = D(SC["defects"][r]["D_over_cross"])
    inb = lo <= v <= hi
    if not inb:
        outside.append(r)
    det.append("%-4s PT %-10s D/X_2nd = %-14s band [%s, %s]  %s%s" % (
        r, PRE["PT_by_rung"][r], v, lo, hi, "IN" if inb else "OUTSIDE",
        "  (extrapolation)" if not PRE["H1_PT_band"][r]["in_fitted_PT_range"] else ""))
    if boundary(v, lo, hi):
        det.append("     ^ BOUNDARY: within 1e-6 relative of a band endpoint")
emit("H1", "IS D/X_2nd A FAMILY PROPERTY OR A SITE PROPERTY?",
     "FALSIFIED (fires against me)" if len(outside) >= 2 else "HELD",
     det + ["outside-band count = %d of 4 (fires at >= 2); rungs outside: %s" % (
         len(outside), ",".join(outside) or "none")],
     "2 or more of the 4 rungs land outside their band")

# ---------------- H2 ----------------
det, bad = [], []
for r in COMPOSED:
    v = D(SC["defects"][r]["D_over_cross"])
    if v <= 0:
        bad.append("%s sign" % r)
    det.append("%-4s sign(D/X_2nd) = %s   (%s)" % (r, "+" if v > 0 else "-", v))
ovmin = None
for r in ALLRUNGS:
    o = D(SC["rungs"][r]["ovl_launch_v0"])
    ovmin = o if ovmin is None or o < ovmin else ovmin
    if o < Decimal("0.99"):
        bad.append("%s ovl %s" % (r, o))
det.append("min ovl_launch_v0 over all ten rungs = %s  (threshold 0.99)" % ovmin)
emit("H2", "EIGENVALUE HALF ALIVE", "FALSIFIED (fires against me)" if bad else "HELD",
     det + (["violations: " + "; ".join(bad)] if bad else []),
     "any composed rung has D/X_2nd < 0, or any overlap < 0.99")

# ---------------- H3 ----------------
v = D(SC["defects"]["R4"]["D_over_cross"])
ty4lo, ty4hi = Decimal("0.547"), Decimal("2.189")
bandlo, bandhi = [D(x) for x in PRE["H1_PT_band"]["R4"]["band"]]
if ty4lo <= v <= ty4hi:
    h3 = "HELD"
elif bandlo <= v <= bandhi:
    h3 = "FALSIFIED (fires against me)"
else:
    h3 = "NEITHER HELD NOR FIRED (convention A)"
emit("H3", "TWO PREDICTORS DISAGREE AT R4; ty4 BACKED IN ADVANCE", h3,
     ["R4 exact D/X_2nd = %s" % v,
      "ty4 predictor 1.0943675, backed interval [%s, %s]" % (ty4lo, ty4hi),
      "PT band [%s, %s]" % (bandlo, bandhi),
      "in ty4 interval: %s   in PT band: %s" % (ty4lo <= v <= ty4hi, bandlo <= v <= bandhi)],
     "the exact D/X_2nd at R4 lands in [0.100, 0.401]",
     "H1 and H3 are ANTI-CORRELATED BY CONSTRUCTION at R4 (frozen text). Do not count twice.")

# ---------------- H4 ----------------
det, fired = [], []
for r in ALLRUNGS:
    lam = D(SC["rungs"][r]["lam"])
    if lam < 0:
        fired.append(r)
    det.append("%-4s lam_min = %-26s %s" % (r, lam, "FIRES" if lam < 0 else "ok"))
emit("H4", "NO RUNG FIRES", "FALSIFIED (fires against me)" if fired else "HELD",
     det + ["rungs with lam_min < 0: %s" % (",".join(fired) or "none")],
     "any rung has lam_min < 0")

# ---------------- H5 ----------------
det, bad = [], []
rmax = None
for r in ALLRUNGS:
    b = SC["band"][r]
    t = D(b["t"])
    rr = D(b["r"])
    rmax = rr if rmax is None or rr > rmax else rmax
    ok = b["same_sign"] and abs(t) <= 3
    if not ok:
        bad.append("%s tripwire" % r)
    det.append("%-4s same_sign=%-5s |t|=%-14s r=%-14s %s" % (r, b["same_sign"], abs(t), rr,
                                                             "OK" if ok else "**"))
if rmax > Decimal("0.30"):
    bad.append("max r = %s > 0.30" % rmax)
det.append("max r over the ten rungs = %s  (threshold 0.30)" % rmax)
emit("H5", "THE TRIPWIRE TRANSFERS TO A THIRD SITE",
     "FALSIFIED (fires against me)" if bad else "HELD",
     det + (["violations: " + "; ".join(bad)] if bad else []),
     "any rung has opposite sign or |t| > 3, or max r > 0.30",
     "declared in the prereg: ratio = 0.5|1+t| is an IDENTITY, so a HELD H5 is NOT evidence "
     "for the band rule.")

# ---------------- H6 ----------------
rc2 = D(SC["defects"]["R2"]["R_c"])
rc3 = D(SC["defects"]["R3"]["R_c"])
ratio = rc2 / rc3
lo, hi = Decimal("0.30"), Decimal("1.50")
det = ["R_c(R2) = %s   R_c(R3) = %s" % (rc2, rc3),
       "R_c(R2)/R_c(R3) = %s   band [0.30, 1.50]" % ratio,
       "ty4 predicted 0.67603 (0.1645733612/0.2434402706); S2 measured 0.610",
       "runner's separately-printed 'PRIMARY ratio' (defect-fraction pct) = %s -- NOT the graded "
       "statistic (convention B)" % SC["ratio_R2_over_R3"]]
if boundary(ratio, lo, hi):
    det.append("BOUNDARY: within 1e-6 relative of an endpoint")
emit("H6", "THE CANCELLING POINT STILL BUYS NOTHING",
     "HELD" if lo <= ratio <= hi else "FALSIFIED (fires against me)", det,
     "outside [0.30, 1.50]",
     "declared dependent on the same ty4 column as H3 -- a hit is NOT independent corroboration.")

held = sum(1 for v in verdicts if v["verdict"] == "HELD")
fals = sum(1 for v in verdicts if v["verdict"].startswith("FALSIFIED"))
other = len(verdicts) - held - fals
print("\n=== TALLY: %d HELD / %d FALSIFIED / %d other, of 6 ===" % (held, fals, other))
print("=== independence: H1 and H3 anti-correlated at R4; H6 dependent on the H3 ty4 column. "
      "6 verdicts, NOT 6 independent tests. ===")
json.dump({"verdicts": verdicts, "tally": {"held": held, "falsified": fals, "other": other}},
          open(sys.argv[2], "w"), indent=1)
