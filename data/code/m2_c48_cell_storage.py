#!/usr/bin/env python3
"""m2_c48_cell_storage.py -- the storage layer for machine-2 numeric cells.

WHY THIS FILE EXISTS
--------------------
Every cell this lane has committed stores its headline number as `mp.nstr(value, 60)` taken from a
run whose working precision was dps=150.  Ninety digits were therefore discarded AT WRITE TIME, and
the discard is invisible from inside: the run knew the value to ~150 digits and the file kept 60.
c47 named the consequence in the published letter (`c6f6315`):

    "relative difference 1.34e-60 at full dps=150 precision" is OUR print granularity, not an
    agreement depth ... anyone comparing against our published cells inherits our print width as
    their instrument floor; the remedy is at the storage layer.

This module is that remedy.  It is deliberately small, has no dependency on any cycle's science, and
is meant to be imported by every future cell writer in this lane.

THE INVARIANT (the whole point)
-------------------------------
The retained narrow print fields are produced by *exactly* the call they were produced by before --
`mp.nstr(value, 60)` and `mp.nstr(value, 30)` -- so no string this lane has already published can
move.  The new fields are strictly ADDITIVE.  `check_additivity()` below is the machine test of that
sentence, and `m2_c48_nonmovement_check.py` runs it against the committed artefacts.

THE THREE LAYERS WRITTEN
------------------------
    <key>          mp.nstr(v, 60)   RETAINED, byte-identical to what this lane has always written
    <key>_30       mp.nstr(v, 30)   RETAINED
    <key>_full     mp.nstr(v, D)    D = full working precision, D = floor(prec*log10 2) + 3
    <key>_exact    {"sign","man","exp","prec"}  with  v = (-1)^sign * man * 2**exp  EXACTLY

`_exact` is the authoritative field and it is not mpmath-specific: `man` and `exp` are integers and
the identity `v = (-1)^sign * man * 2**exp` is exact in any system with big integers.  `_full` is the
human-readable form and is checked against `_exact` on every read.

WHAT THIS MODULE DOES NOT CLAIM
-------------------------------
Storing 151 digits is a statement about the WORKING PRECISION of the run (a knob), not about the
ACCURACY of the value (a measurement).  c38's ERRATUM 19 was exactly the mistake of letting a width
be read as a certificate.  Accuracy has to be measured separately -- by moving the dps knob and
seeing how many digits survive -- and this module therefore also writes `<key>_width_is_a_knob: true`
so the distinction travels with the artefact instead of living in a letter.

usage:  m2_c48_cell_storage.py --self-test
"""
import os, sys
from mpmath import mp, mpf

RETAINED = ((("", 60), ("_30", 30)))   # the print fields this lane has always written; DO NOT CHANGE


def full_digits(prec=None):
    """Decimal digits that round-trip a binary float of `prec` bits (+2 guard)."""
    prec = mp.prec if prec is None else prec
    return int(prec * 0.30102999566398119521) + 3


def store_number(value, key="value", retained=RETAINED):
    """Return the dict of storage fields for one mpf.  Additive over the historical fields."""
    v = mpf(value)
    sign, man, exp, bc = v._mpf_
    if man == 0:                                   # zero / inf / nan carry no man-exp form
        raise ValueError("store_number: non-finite or zero value; handle at the call site")
    out = {}
    for suffix, sf in retained:
        out[key + suffix] = mp.nstr(v, sf)         # <-- the byte-preserving calls, unchanged
    D = full_digits()
    # min_fixed/max_fixed force exponential notation: a fixed-point 223-digit string prefixed by
    # fifty-four zeros invites a reader to miscount significant figures, which is the very confusion
    # this module exists to end. Verified round-trip-exact at the write precision, same as before.
    out[key + "_full"] = mp.nstr(v, D, min_fixed=0, max_fixed=0)
    out[key + "_full_sf"] = D
    out[key + "_exact"] = {"sign": sign, "man": str(man), "exp": exp, "prec": mp.prec,
                           "form": "value = (-1)**sign * man * 2**exp   (exact)"}
    out[key + "_width_is_a_knob"] = True
    # write-time KAT: both new fields must reconstruct the live value
    if load_number(out, key)._mpf_ != v._mpf_:
        raise AssertionError("store_number: exact field does not reconstruct the live value")
    if mpf(out[key + "_full"])._mpf_ != v._mpf_:
        raise AssertionError("store_number: _full decimal does not round-trip at write precision")
    return out


def load_number(cell, key="value", strict=True):
    """Reconstruct the mpf EXACTLY from a stored cell.  Never reads the 60-s.f. field."""
    e = cell[key + "_exact"]
    man, exp, sign = int(e["man"]), int(e["exp"]), int(e["sign"])
    need = e["prec"]
    if mp.prec < need:                             # a narrow reader would silently re-truncate
        if strict:
            raise ValueError("load_number: reader prec %d < stored prec %d -- widen mp.dps first"
                             % (mp.prec, need))
    with mp.workprec(max(mp.prec, need) + 64):      # man*2**exp is exact once prec >= bitcount(man)
        v = mpf(man) * mpf(2) ** exp
    if sign:
        v = -v
    if strict and (key + "_full") in cell:
        # NB. The decimal field round-trips ONLY at the precision it was written at. Parsed at a
        # WIDER precision it recovers the decimal string, not the binary number it was printed from,
        # and the two differ below the last stored digit. That is the same print-width defect this
        # module exists to remove, one layer down -- which is why `_exact` is the authoritative field
        # and `_full` is checked against it here at the STORED precision, never at the reader's.
        with mp.workprec(need):
            if mpf(cell[key + "_full"])._mpf_ != v._mpf_:
                raise AssertionError("load_number: _full and _exact disagree in %s" % key)
    return v


def check_additivity(cell, key="value", retained=RETAINED):
    """Regenerate every retained narrow field FROM THE FULL-PRECISION STORAGE and byte-compare.

    Returns list of (field, regenerated, stored, bool_equal).  This is the non-movement proof:
    it never trusts the narrow field, it re-derives it.
    """
    v = load_number(cell, key)
    rows = []
    for suffix, sf in retained:
        f = key + suffix
        regen = mp.nstr(v, sf)
        rows.append((f, regen, cell.get(f), regen == cell.get(f)))
    return rows


def agreement_sf(a, b):
    """Significant figures to which two mpf values agree.  inf if bit-identical."""
    a, b = mpf(a), mpf(b)
    if a == b:
        return mp.inf
    return -mp.log(abs(a - b) / abs(a), 10)


# ------------------------------------------------------------------ self-test (known answers)
def self_test():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print("  %-58s %s" % (name, "PASS" if cond else "FAIL"))

    print("m2_c48_cell_storage self-test")

    # T1 known answer: a value whose 60-s.f. and 151-s.f. prints are both known by construction.
    mp.dps = 150
    v = mp.sqrt(mpf(2)) / mpf(10) ** 55
    c = store_number(v, "lam")
    chk("T1 exact field reconstructs bit-identically", load_number(c, "lam")._mpf_ == v._mpf_)
    chk("T1 retained 60-s.f. field == mp.nstr(v,60)", c["lam"] == mp.nstr(v, 60))
    chk("T1 retained 30-s.f. field == mp.nstr(v,30)", c["lam_30"] == mp.nstr(v, 30))
    chk("T1 full field carries > 60 s.f.", c["lam_full_sf"] > 60 and len(
        c["lam_full"].split("e")[0].replace(".", "").replace("-", "").lstrip("0")) > 60)
    chk("T1 additivity regenerates both narrow fields",
        all(r[3] for r in check_additivity(c, "lam")))

    # T2 NEGATIVE CONTROL, the defect itself: the OLD storage (60 s.f. only) must FAIL to recover.
    old = mp.nstr(v, 60)
    back = mpf(old)
    lost = agreement_sf(v, back)
    chk("T2 old 60-s.f. storage recovers only ~60 s.f. (59 < d < 62)", 59 < lost < 62)
    chk("T2 new storage recovers > 60 s.f. (bit-exact)", load_number(c, "lam") == v)

    # T3 the reader-precision trap: a narrow reader must REFUSE, not silently truncate.
    mp.dps = 30
    try:
        load_number(c, "lam")
        chk("T3 narrow reader refuses (strict)", False)
    except ValueError:
        chk("T3 narrow reader refuses (strict)", True)
    mp.dps = 150

    # T3b THE TRAP THE GATE CAUGHT: a reader WIDER than the writer must still reconstruct bit-exactly,
    #     and the decimal field must not be checked at the reader's precision (it round-trips only at
    #     the writer's). Known answer: the same bits, from a reader 70 dps wider.
    mp.dps = 220
    chk("T3b wide reader reconstructs bit-exactly", load_number(c, "lam")._mpf_ == v._mpf_)
    chk("T3b wide reader regenerates the 60-s.f. field byte-identically",
        all(r[3] for r in check_additivity(c, "lam")))
    wide = mpf(c["lam_full"])
    chk("T3b and the decimal alone would NOT have (differs below the last stored digit)",
        wide._mpf_ != v._mpf_ and agreement_sf(wide, v) > 150)
    mp.dps = 150

    # T4 a value needing a sign and a value with a short mantissa
    for t in (-mp.pi / mpf(10) ** 200, mpf(1) / 1024):
        c2 = store_number(t, "z")
        chk("T4 roundtrip %s" % mp.nstr(t, 6), load_number(c2, "z")._mpf_ == mpf(t)._mpf_)

    # T5 a DIFFERENT working precision must widen the full field, not the retained ones
    mp.dps = 220
    v2 = mp.sqrt(mpf(2)) / mpf(10) ** 55
    c3 = store_number(v2, "lam")
    chk("T5 dps=220 widens _full", c3["lam_full_sf"] > c["lam_full_sf"])
    chk("T5 dps=220 leaves the 60-s.f. field byte-identical", c3["lam"] == c["lam"])
    mp.dps = 150

    print("SELF-TEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def refresh_full(path, keys=("L", "lambda_min", "residual", "log10")):
    """Rewrite the `_full` decimal of an existing cell FROM `_exact`, at the stored precision.

    Touches no other field and re-runs no science: `_exact` is the authoritative storage, `_full` is
    its human-readable shadow. Refuses if the regenerated narrow fields would move.
    """
    import json
    c = json.load(open(path))
    changed = []
    for key in keys:
        if key + "_exact" not in c:
            continue
        need = c[key + "_exact"]["prec"]
        with mp.workprec(need):
            v = load_number(c, key, strict=False)
            before = c.get(key + "_full")
            c[key + "_full"] = mp.nstr(v, full_digits(need), min_fixed=0, max_fixed=0)
            assert mpf(c[key + "_full"])._mpf_ == v._mpf_, "refresh_full: lost the round-trip"
        if before != c[key + "_full"]:
            changed.append(key)
    # NON-MOVEMENT GUARD: every narrow field present must still regenerate byte-identically.
    # Widths are read off the cell itself (count of significant digits in the stored string), so this
    # guard cannot be desynchronised from the fields it protects by a change of convention elsewhere.
    with mp.workprec(1400):
        for key in keys:
            if key + "_exact" not in c:
                continue
            v = load_number(c, key)
            for f in [k for k in c if k == key or k.startswith(key + "_")]:
                if not isinstance(c[f], str) or f.endswith("_full") or f.endswith("_exact"):
                    continue
                sf = len(c[f].split("e")[0].replace(".", "").replace("-", "").lstrip("0"))
                assert mp.nstr(v, sf) == c[f], "refresh_full would move %s" % f
    json.dump(c, open(path, "w"), indent=1)
    return changed


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) > 2 and sys.argv[1] == "--refresh-full":
        for p in sys.argv[2:]:
            print("refreshed %-56s %s" % (os.path.basename(p), refresh_full(p)))
        sys.exit(0)
    raise SystemExit(__doc__)
