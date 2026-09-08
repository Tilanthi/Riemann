#!/usr/bin/env python3
"""m2_c49_depth_all_rungs.py -- the depth of the c48 ladder AT EVERY RUNG, in both conventions.

WHY THIS EXISTS
---------------
c48 published "our depth is ~95 s.f., not 154".  That sentence was true of the two rungs it
measured (N=60, N=100) and was published over a five-rung ladder.  The other three rungs had no
partner run at all: their cells store 154 significant digits and nothing in the tree said how many
of them the object supports.  A width extrapolated across an axis it was never measured on is the
same defect as a width quoted as an accuracy -- trap #155 with an index instead of a knob.

THE INSTRUMENT is c48's D2, unchanged and imported in spirit: agreement, in significant figures,
between a cell's stored value at dps=150 and an INDEPENDENT run of the same cell at dps=220, one
knob moved.  Two conventions are reported side by side because m1-L190 s4 asked that a quoted
depth name its measure:

    continuous          -log10(|a-b|/|b|)                     (ours)
    string-agreement    leading significant decimal digits    (m1's; integer, floor-like)

They are different measures of the same disagreement and are expected to agree to within a digit.

WHAT IT DOES NOT MEASURE, by construction: gl_degree=9, iters=16 and N are HELD in both runs of
every pair, so any error they share is invisible here.  This is evidence about arithmetic, not
about the operator.

usage: m2_c49_depth_all_rungs.py [--json OUT]
"""
import os
import sys
import json
import glob
from mpmath import mp, mpf

mp.dps = 400

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/shared/rh-exchange-repo/Riemann"
C48DIR = os.path.join(REPO, "data", "c48")
C46DIR = os.path.join(REPO, "data", "c46")
NEWDIR = os.path.join(HERE, "cells220")

sys.path.insert(0, os.path.join(HERE, "flat"))
import m2_c48_cell_storage as S  # noqa: E402


def cont_sf(a, b):
    """continuous depth: -log10(relative difference), measured against b."""
    a, b = mpf(a), mpf(b)
    if a == b:
        return None          # exact agreement -- reported as such, never as a number
    return float(-mp.log(abs(a - b) / abs(b), 10))


def digits_of(x, n):
    """(exponent, digit-string) of |x| normalised to d.ddd, n digits, no rounding surprises."""
    x = abs(mpf(x))
    if x == 0:
        return None, "0" * n
    e = int(mp.floor(mp.log(x, 10)))
    m = x / mpf(10) ** e
    if m >= 10:                      # log10 rounding at a decade edge
        m /= 10
        e += 1
    elif m < 1:
        m *= 10
        e -= 1
    s = mp.nstr(m, n + 5, strip_zeros=False).replace(".", "").replace("-", "")
    return e, s


def agree_digits(a, b, cap=300):
    """m1's convention: how many LEADING significant decimal digits are identical."""
    ea, sa = digits_of(a, cap)
    eb, sb = digits_of(b, cap)
    if ea != eb:
        return 0
    n = 0
    for ca, cb in zip(sa[:cap], sb[:cap]):
        if ca != cb:
            break
        n += 1
    return n            # capped: `digits_of` renders cap+5 guard digits, and returning them
                        # would report more agreement than was asked for (KAT arm-1 caught this)


def load_pairs():
    """(parity, N) -> {'lo': cell@dps150, 'hi': cell@dps220, 'frozen': c46 cell, 'hi_src': path}"""
    out = {}
    for f in sorted(glob.glob(os.path.join(C48DIR, "c48_*_dps150_*.json"))):
        c = json.load(open(f))
        out[(c["parity"], c["N"])] = {"lo": c, "lo_src": f, "hi": None, "hi_src": None,
                                      "frozen": None}
    for d in (C48DIR, NEWDIR):
        for f in sorted(glob.glob(os.path.join(d, "c48_*_dps220_*.json"))):
            c = json.load(open(f))
            k = (c["parity"], c["N"])
            if k in out and out[k]["hi"] is None:
                out[k]["hi"] = c
                out[k]["hi_src"] = f
    for k, v in out.items():
        fz = os.path.join(C46DIR, os.path.basename(v["lo_src"]).replace("c48_", "c46_", 1))
        if os.path.exists(fz):
            v["frozen"] = json.load(open(fz))
            v["frozen_src"] = fz
    return out


REGISTERED = {60: "c48 (published)", 100: "c48 (published)",
              140: "UNREGISTERED (killed run, 02:14-02:19Z)",
              180: "UNREGISTERED (killed run, 02:14-02:19Z)",
              220: "REGISTERED (c49 prereg P1b)"}


def main():
    pairs = load_pairs()
    rows = []
    print("m2_c49_depth_all_rungs   x=13, gl_degree=9, iters=16, dps 150 vs an independent 220\n")
    print("  %-6s %-4s %10s %10s %12s %10s  %s"
          % ("parity", "N", "cont s.f.", "digits", "via frozen", "gain", "arm"))
    for (p, N) in sorted(pairs, key=lambda t: (t[0], t[1])):
        v = pairs[(p, N)]
        if v["hi"] is None:
            print("  %-6s %-4d %10s %10s %12s %10s  %s"
                  % (p, N, "-", "-", "-", "-", "NO PARTNER RUN"))
            rows.append({"parity": p, "N": N, "status": "NO PARTNER RUN"})
            continue
        hi = S.load_number(v["hi"], "lambda_min")
        lo_new = S.load_number(v["lo"], "lambda_min")
        d_new = cont_sf(lo_new, hi)
        g_new = agree_digits(lo_new, hi)
        d_old = g_old = None
        if v["frozen"] is not None:
            lo_old = mpf(v["frozen"]["lambda_min"])
            d_old = cont_sf(lo_old, hi)
            g_old = agree_digits(lo_old, hi)
        print("  %-6s %-4d %10.2f %10d %12s %10s  %s"
              % (p, N, d_new, g_new,
                 ("%.2f" % d_old) if d_old else "-",
                 ("%.2f" % (d_new - d_old)) if d_old else "-",
                 REGISTERED[N]))
        rows.append({"parity": p, "N": N, "continuous": d_new, "string_digits": g_new,
                     "via_frozen_continuous": d_old, "via_frozen_digits": g_old,
                     "lo_src": os.path.relpath(v["lo_src"], REPO),
                     "hi_src": (os.path.relpath(v["hi_src"], REPO)
                                if v["hi_src"].startswith(REPO) else "c49 run: "
                                + os.path.basename(v["hi_src"])),
                     "arm": REGISTERED[N]})

    print("\nSCORING the preregistered predictions (prereg/m2_c49_prereg.md s2)")
    done = [r for r in rows if r.get("continuous") is not None]

    # P1a monotone non-increasing in N, tolerance 0.30
    viol = []
    for p in ("even", "odd"):
        seq = sorted([r for r in done if r["parity"] == p], key=lambda r: r["N"])
        for i in range(len(seq)):
            for j in range(i + 1, len(seq)):
                if seq[j]["continuous"] - seq[i]["continuous"] > 0.30:
                    viol.append((p, seq[i]["N"], seq[j]["N"],
                                 seq[j]["continuous"] - seq[i]["continuous"]))
    print("  P1a monotone non-increasing in N (tol 0.30): %s%s"
          % ("HELD" if not viol else "FAILED", "" if not viol else "  " + str(viol)))

    # P1b band at the registered rung
    band = {"even": (89.7, 92.7), "odd": (93.0, 96.0)}
    p1b = []
    for p in ("even", "odd"):
        r = [x for x in done if x["parity"] == p and x["N"] == 220]
        if not r:
            p1b.append("%s N=220 NOT MEASURED" % p)
            continue
        d = r[0]["continuous"]
        lo, hi = band[p]
        p1b.append("%s %.2f in [%.1f,%.1f] -> %s"
                   % (p, d, lo, hi, "INSIDE" if lo <= d <= hi else
                      ("BELOW" if d < lo else "ABOVE")))
    print("  P1b band at N=220: " + " | ".join(p1b))

    # P1c parity ordering
    bad = []
    for N in sorted(set(r["N"] for r in done)):
        e = [r for r in done if r["N"] == N and r["parity"] == "even"]
        o = [r for r in done if r["N"] == N and r["parity"] == "odd"]
        if e and o and not (o[0]["continuous"] > e[0]["continuous"]):
            bad.append(N)
    print("  P1c odd depth > even depth at every rung: %s%s"
          % ("HELD" if not bad else "FAILED", "" if not bad else "  rungs " + str(bad)))

    # P1d the gap
    bad2 = [(r["parity"], r["N"], r["via_frozen_continuous"]) for r in done
            if r["via_frozen_continuous"] is not None and r["via_frozen_continuous"] > 61]
    bad3 = [(r["parity"], r["N"], r["continuous"]) for r in done if r["continuous"] <= 85]
    print("  P1d frozen-cell reading < 61 s.f. everywhere: %s%s"
          % ("HELD" if not bad2 else "FAILED", "" if not bad2 else "  " + str(bad2)))
    print("      c48-cell reading > 85 s.f. everywhere:   %s%s"
          % ("HELD" if not bad3 else "FAILED", "" if not bad3 else "  " + str(bad3)))

    print("\nCONVENTION CHECK (m1-L190 s4): |continuous - string_digits| <= 1 everywhere?")
    off = [(r["parity"], r["N"], r["continuous"], r["string_digits"]) for r in done
           if abs(r["continuous"] - r["string_digits"]) > 1.0]
    print("  %s%s" % ("YES" if not off else "NO", "" if not off else "  " + str(off)))

    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump({"rows": rows, "band": band}, open(out, "w"), indent=1)
        print("\nwrote %s" % out)
    return 0




# --------------------------------------------------------------------------- KAT
def self_test():
    """A dry run on KNOWN ANSWERS is the only thing that tests the test.

    Arm 1: `agree_digits` against pairs whose answer is countable by hand.
    Arm 2: `cont_sf` against the SEALED c48 instrument's PUBLISHED output -- the four D2 numbers
           m1-L190 s1 verified at primary. If this reimplementation did not reproduce them, every
           number in this cycle would be measuring a new instrument and saying nothing about c48.
    """
    ok = True

    def chk(name, got, want):
        nonlocal ok
        good = (got == want)
        ok = ok and good
        print("  %-58s %-14s %s" % (name, str(got), "PASS" if good else "FAIL want %s" % (want,)))

    print("m2_c49_depth_all_rungs self-test\n arm 1: agree_digits on hand-countable pairs")
    chk("identical values -> cap", agree_digits(mpf("1.5"), mpf("1.5"), cap=20), 20)
    chk("1.0 vs 2.0 -> 0 leading digits agree", agree_digits(mpf(1), mpf(2)), 0)
    chk("1.234567 vs 1.234568 -> 6", agree_digits(mpf("1.234567"), mpf("1.234568")), 6)
    chk("1.0 vs 1.1 -> 1", agree_digits(mpf("1.0"), mpf("1.1")), 1)
    chk("different decade -> 0", agree_digits(mpf("9.9"), mpf("10.1")), 0)
    chk("sign is ignored (magnitudes compared)", agree_digits(mpf("-1.2345"), mpf("1.2346")), 4)
    chk("1e-55 scale, 30 digits then a break",
        agree_digits(mpf("2.84751569133936367715637039399e-55"),
                     mpf("2.84751569133936367715637039398e-55")), 29)
    print(" arm 2: cont_sf against the SEALED c48 instrument's published D2 output")
    pairs = load_pairs()
    for (p, N, want) in (("even", 60, 92.66), ("even", 100, 92.22),
                         ("odd", 60, 95.81), ("odd", 100, 95.40)):
        v = pairs.get((p, N))
        got = None
        if v and v["hi"] is not None:
            got = round(cont_sf(S.load_number(v["lo"], "lambda_min"),
                                S.load_number(v["hi"], "lambda_min")), 2)
        chk("c48 published D2 %s N=%d" % (p, N), got, want)
    print("SELF-TEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(main())
