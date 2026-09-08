#!/usr/bin/env python3
"""m2_c49_precision.py -- the rule that decides which numbers a machine-2 cell is allowed to hand
to a reader who never reads our prose, plus the upgrade that makes the committed cells obey it.

THE DEFECT THIS FIXES (ledger row, opened 2026-09-08T01:08:38Z)
---------------------------------------------------------------
c48 fixed the storage layer and, in the same push, introduced this:

    "lambda_min_full_sf": 154,          <- a bare integer, at a key that reads "significant figures"
    "lambda_min_width_is_a_knob": true  <- the guard: a bare TRUE, with the caveat in the NAME

154 is the WIDTH the file was written at (the dps knob). The object supports about 95 (measured).
The only thing standing between a reader and a 1.6x overstatement was a field NAME -- and a caveat
in a name reaches only the reader who already knew to look. That is not hypothetical here: an
external machine lifting a precision number out of our cells has happened 1 for 1 (m3's 1.34e-60
was a correct measurement of our print width, read as an agreement depth).

THE RULE (mechanical, and the gate below is the machine form of it)
-------------------------------------------------------------------
For every scalar leaf of a cell whose KEY names precision (see PREC_KEY_RE):

  (M) it may be a LIFTABLE number only if the key itself says what was measured and how -- keys
      matching MEASURE_KEY_RE, e.g. `sf_stable_under_dps_150_to_220`, `sf_vs_assembled_matrix_bound`
      -- and only if its parent dict carries the knob metadata (KNOB_META_REQUIRED);
  (K) otherwise, if it is a liftable number it must be a declared KNOB: the same dict must carry
      `<key>_is_a_knob` whose VALUE is a string containing "NOT an accuracy";
  (S) otherwise it must not be liftable at all -- a string that `float()` refuses, carrying its own
      caveat in the VALUE.

`liftable` = `float(v)` succeeds, on the value as JSON delivers it. A bare `true` fails the rule
outright: a guard whose value carries no information is a guard in name only.

WHAT THIS RULE DOES NOT DEFEND AGAINST, stated because a gate that oversells itself is the defect
one layer up: a scraper that regexes digits out of prose will still pull "154" out of the caveat
string. There is no artefact-side defence against that and this module does not claim one. The
claim is exactly: no standard parse -- `json.load` then `float(cell[k])` -- yields a precision
number the object does not support.

usage: m2_c49_precision.py --self-test
"""
import json
import re

# keys that read as a precision claim. `dps` is included deliberately: it is the knob, in the units
# the run was configured in, and excluding it would be the same name-based exemption this module
# exists to remove.
PREC_KEY_RE = re.compile(r"(?i)(^|_)(sf|sigfig|sigfigs|digits|precision|prec|accuracy|"
                         r"depth|width|dps|bits)(_|$)")

# keys whose NAME states the measurement -- these, and only these, may be liftable numbers.
MEASURE_KEY_RE = re.compile(r"^sf_(stable_under_[a-z0-9_]+|string_agreement_digits_under_[a-z0-9_]+|"
                            r"vs_assembled_matrix_bound)$")

KNOB_META_REQUIRED = ("measure", "knobs_varied", "knobs_held_NOT_covered", "means", "source")

KNOB_TOKEN = "NOT an accuracy"


# --------------------------------------------------------------------------- the rule
def liftable(v):
    """Would a standard parse turn this leaf into a number? bools are not numbers here."""
    if isinstance(v, bool):
        return False
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        try:
            float(v)
            return True
        except ValueError:
            return False
    return False


def walk(obj, path="", parent=None):
    """Yield (path, key, value, parent_dict) for every scalar leaf."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + "/" + k
            if isinstance(v, (dict, list)):
                yield from walk(v, p, v if isinstance(v, dict) else parent)
            else:
                yield p, k, v, obj
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, path + "/%d" % i, parent)


def gate_cell(cell):
    """Return (findings, stats). A finding is (verdict, path, value, why); verdict FAIL/OK."""
    findings, n_ok, n_fail = [], 0, 0
    for p, k, v, parent in walk(cell):
        if not PREC_KEY_RE.search(k):
            continue
        if isinstance(v, bool):
            findings.append(("FAIL", p, v, "guard with a bare boolean value: the caveat is in the "
                                           "NAME only"))
            n_fail += 1
            continue
        if liftable(v):
            if MEASURE_KEY_RE.match(k):
                missing = [m for m in KNOB_META_REQUIRED if m not in parent]
                if missing:
                    findings.append(("FAIL", p, v, "measurement key without knob metadata: missing "
                                                   + ",".join(missing)))
                    n_fail += 1
                else:
                    findings.append(("OK", p, v, "measurement; key names the knob move"))
                    n_ok += 1
                continue
            cav = parent.get(k + "_is_a_knob")
            if isinstance(cav, str) and KNOB_TOKEN in cav:
                findings.append(("OK", p, v, "declared knob; caveat carried in a sibling VALUE"))
                n_ok += 1
            else:
                findings.append(("FAIL", p, v, "LIFTABLE precision number with no declaration: a "
                                               "reader gets a number the object may not support"))
                n_fail += 1
            continue
        # not liftable: a string that float() refuses
        findings.append(("OK", p, v if not isinstance(v, str) else v[:40] + "...",
                         "not liftable by a standard parse"))
        n_ok += 1
    return findings, {"ok": n_ok, "fail": n_fail}


def gate_cell_structure(cell, keys=("L", "lambda_min", "residual", "log10")):
    """Trap #155 in machine form: every stored quantity that carries a WIDTH must carry a DEPTH."""
    out = []
    for key in keys:
        if key + "_exact" not in cell:
            continue
        if key + "_sf" not in cell or not isinstance(cell[key + "_sf"], dict):
            out.append(("FAIL", "/" + key + "_sf", None,
                        "a stored width with no depth slot (trap #155)"))
        else:
            out.append(("OK", "/" + key + "_sf", None, "depth slot present"))
    return out


# --------------------------------------------------------------------------- the upgrade
def knob_caveat(written, key, dps):
    return ("%d significant digits WERE WRITTEN, at the dps=%s working-precision knob. This is a "
            "WIDTH and it is NOT an accuracy: the digits this cell's %s actually supports are a "
            "MEASUREMENT and live in %s_sf. Quoting this number as a precision is trap #155."
            % (written, dps, key, key))


def dps_caveat(dps):
    return ("dps=%s is the working-precision KNOB this run was configured with. It is NOT an "
            "accuracy of any number in this file; the measured accuracies are in the *_sf blocks."
            % dps)


def prec_caveat(prec, key):
    return ("%d bits is the WORKING PRECISION the value was written at (the same knob as dps, in "
            "bits). It is NOT an accuracy; it is retained because the loader needs it to check the "
            "_full decimal at the precision it was printed at. Measured accuracy: %s_sf."
            % (prec, key))


def depth_block(meas, key, note=None):
    """meas: dict with continuous/int depth or None for UNMEASURED."""
    if meas is None:
        return {
            "sf_measured": None,
            "status": "UNMEASURED -- this cell has no partner run with one knob moved, so this "
                      "lane can hand you no supported precision number for it. Absence is "
                      "deliberate: the alternative is a width, and a width is not an accuracy.",
            "measure": None, "knobs_varied": [], "knobs_held_NOT_covered": None,
            "means": None, "source": None,
        }
    b = {
        "sf_stable_under_dps_%d_to_%d" % (meas["lo_dps"], meas["hi_dps"]): meas["continuous"],
        "sf_string_agreement_digits_under_dps_%d_to_%d" % (meas["lo_dps"], meas["hi_dps"]):
            meas["string_digits"],
        "measure": ("agreement of this cell's %s with an INDEPENDENT run of the same cell at "
                    "dps=%d (this cell: dps=%d), one knob moved. Two conventions are given because "
                    "they are different measures and m1-L190 section 4 asked that the measure be "
                    "named: `stable_under` is the continuous -log10(relative difference); "
                    "`string_agreement_digits` is the count of leading significant digits that "
                    "agree, m1's convention. They agree to within one digit."
                    % (key, meas["hi_dps"], meas["lo_dps"])),
        "knobs_varied": ["dps"],
        "knobs_held_NOT_covered": ["gl_degree=9 (the quadrature that DEFINES the matrix)",
                                   "iters=16 (eigensolver iterations)",
                                   "N (the truncation; this is a rung, not the limit)"],
        "means": ("digits of this stored value that survive a change of the arithmetic precision "
                  "knob. It is NOT a distance to the exact operator's eigenvalue: any error shared "
                  "by both runs -- quadrature, truncation, iteration count -- is invisible to it. "
                  "A one-knob agreement is evidence about arithmetic, not about the object."),
        "source": meas.get("source", "data/c49/m2_c49_depth_all_rungs.out"),
    }
    if note:
        b["note"] = note
    return b


def upgrade_cell(cell, depth, keys=("L", "lambda_min", "residual", "log10")):
    """Return (new_cell, moves) where moves is [(field, old, new, why)]. Print fields never move."""
    c = json.loads(json.dumps(cell))          # deep copy, key order preserved
    moves = []
    dps = c.get("dps")
    for key in keys:
        if key + "_exact" not in c:
            continue
        fs = key + "_full_sf"
        if fs in c and not isinstance(c[fs], str):
            old = c[fs]
            c[fs] = knob_caveat(int(old), key, dps)
            moves.append((fs, old, c[fs], "bare int -> self-describing string (rule S)"))
        wk = key + "_width_is_a_knob"
        if wk in c and isinstance(c[wk], bool):
            old = c[wk]
            c[wk] = ("TRUE, and this sentence is the point: %s_full_sf is a width, %s_sf is the "
                     "measurement. The previous value of this field was a bare `true`, which "
                     "carried the caveat in the field NAME and reached only a reader who already "
                     "knew to look." % (key, key))
            moves.append((wk, old, c[wk], "bare true -> the caveat, in the VALUE (rule S)"))
        ex = c.get(key + "_exact")
        if isinstance(ex, dict) and "prec" in ex and "prec_is_a_knob" not in ex:
            ex["prec_is_a_knob"] = prec_caveat(int(ex["prec"]), key)
            moves.append((key + "_exact/prec_is_a_knob", None, "(added)",
                          "knob declaration for the surviving numeric leaf `prec` (rule K)"))
        if key + "_sf" not in c:
            c[key + "_sf"] = depth_block(depth.get(key) if depth else None, key)
            moves.append((key + "_sf", None, "(added)", "the DEPTH slot (trap #155)"))
    if "dps" in c and "dps_is_a_knob" not in c:
        c["dps_is_a_knob"] = dps_caveat(dps)
        moves.append(("dps_is_a_knob", None, "(added)", "knob declaration for `dps` (rule K)"))
    b = c.get("eig_residual_bound_sf")
    if b is not None and not isinstance(b, dict):
        c["eig_residual_bound_sf"] = {
            "sf_vs_assembled_matrix_bound": float(b),
            "measure": ("Weyl/Rayleigh residual bound |lam - lam_exact(M)| <= ||Mv-lam v||/||v||, "
                        "divided by |lam|, for the matrix M THAT WAS BUILT."),
            "knobs_varied": [],
            "knobs_held_NOT_covered": ["gl_degree (the quadrature that defines M)", "N", "iters"],
            "means": ("a LOWER BOUND on the digits of lam certified against the assembled matrix. "
                      "It answers a different question from the *_sf blocks and is systematically "
                      "LARGER ON THE SAME CELL. Measured pairwise over the ten dps=150 rungs "
                      "of the c49 ladder, the excess (bound minus measured agreement) runs "
                      "+0.97 to +2.19 digits (even) and +2.43 to +3.77 (odd); the per-rung "
                      "table is data/c49/m2_c49_depth_all_rungs.out. That excess is the build "
                      "loss the bound cannot see by construction. A bound is not an "
                      "agreement; never quote them as one number."),
            "source": "computed at write time by c48_recell.py; see data/c49/m2_c49_depth_all_rungs.out",
        }
        moves.append(("eig_residual_bound_sf", b, "(dict)",
                      "numeral string -> block whose only liftable leaf names its own question"))
    return c, moves


# --------------------------------------------------------------------------- self-test
def self_test():
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print("  %-64s %s" % (name, "PASS" if cond else "FAIL"))

    print("m2_c49_precision self-test (two arms on KNOWN ANSWERS)")

    # A1 the c48 shape MUST fail, and fail on exactly the fields the ledger row names.
    c48 = {"dps": 150,
           "lambda_min": "3.34e-55", "lambda_min_full": "3.3410774e-55",
           "lambda_min_full_sf": 154,
           "lambda_min_exact": {"sign": 0, "man": "67041478", "exp": -682, "prec": 502,
                                "form": "value = (-1)**sign * man * 2**exp   (exact)"},
           "lambda_min_width_is_a_knob": True,
           "eig_residual_bound_sf": "99.167247"}
    f, s = gate_cell(c48)
    fails = {p for v, p, _, _ in f if v == "FAIL"}
    chk("A1 c48 shape FAILS the gate", s["fail"] > 0)
    chk("A1 the 154 width is caught", "/lambda_min_full_sf" in fails)
    chk("A1 the bare-true guard is caught", "/lambda_min_width_is_a_knob" in fails)
    chk("A1 the numeral-STRING bound is caught (float() lifts it)",
        "/eig_residual_bound_sf" in fails)
    chk("A1 the dps knob is caught", "/dps" in fails)
    chk("A1 the prec knob is caught", "/lambda_min_exact/prec" in fails)
    chk("A1 structure: width without depth slot", any(v == "FAIL" for v, *_ in
                                                      gate_cell_structure(c48)))

    # A2 the upgraded shape MUST pass, with a real measurement present.
    meas = {"lambda_min": {"lo_dps": 150, "hi_dps": 220, "continuous": 95.40,
                           "string_digits": 95, "source": "unit-test"}}
    up, moves = upgrade_cell(c48, meas)
    f2, s2 = gate_cell(up)
    chk("A2 upgraded shape PASSES the gate", s2["fail"] == 0 and s2["ok"] > 0)
    chk("A2 depth slot present", all(v == "OK" for v, *_ in gate_cell_structure(up)))
    chk("A2 the measured depth IS liftable (a reader gets a supported number)",
        liftable(up["lambda_min_sf"]["sf_stable_under_dps_150_to_220"]))
    chk("A2 the width is NOT liftable", not liftable(up["lambda_min_full_sf"]))
    chk("A2 and it still carries the number 154 in prose", "154" in up["lambda_min_full_sf"])
    chk("A2 print fields untouched", up["lambda_min"] == c48["lambda_min"]
        and up["lambda_min_full"] == c48["lambda_min_full"])
    chk("A2 _exact reconstruction fields untouched",
        all(up["lambda_min_exact"][k] == c48["lambda_min_exact"][k]
            for k in ("sign", "man", "exp", "prec", "form")))
    chk("A2 moves are reported, not silent", len(moves) >= 5)

    # A3 UNMEASURED cell: the reader must be unable to lift anything, and told so.
    up3, _ = upgrade_cell(c48, {})
    chk("A3 unmeasured depth slot is null (nothing liftable)",
        up3["lambda_min_sf"]["sf_measured"] is None
        and not liftable(up3["lambda_min_sf"]["sf_measured"]))
    f3, s3 = gate_cell(up3)
    chk("A3 unmeasured cell still PASSES (absence is allowed, overstatement is not)",
        s3["fail"] == 0)

    # A4 NEGATIVE CONTROL on the gate itself: a measurement key WITHOUT the knob metadata must fail,
    #    or the gate would green-light a bare number under a nice name.
    bad = {"lambda_min_sf": {"sf_stable_under_dps_150_to_220": 95.4}}
    f4, s4 = gate_cell(bad)
    chk("A4 a measurement key without knob metadata FAILS", s4["fail"] == 1)

    # A5 NEGATIVE CONTROL: a knob declaration whose caveat does not say what it must.
    bad2 = {"foo_sf": 154, "foo_sf_is_a_knob": "it is a knob"}
    f5, s5 = gate_cell(bad2)
    chk("A5 a knob declaration missing the token FAILS", s5["fail"] == 1)
    good2 = {"foo_sf": 154, "foo_sf_is_a_knob": "154 written; NOT an accuracy, see foo_depth"}
    f6, s6 = gate_cell(good2)
    chk("A5 the same field WITH the token passes", s6["fail"] == 0)

    print("SELF-TEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    raise SystemExit(__doc__)
