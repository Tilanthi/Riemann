#!/usr/bin/env python3
"""m2_c55_storage_test_h1fix.py -- SIBLING repair of the H1 GATE, which failed on a PRINT WIDTH.

WHAT HAPPENED.  m2_c55_storage_test.py (sealed in seal 3, unedited) registered H1 as "all 101
eigenvalue strings come back BIT-IDENTICAL to the sealed run, or the test is void".  H1 came back
**0/101**.  The reason is not that the computation changed: `STORE_SF` governs the print width of
`lam`, `L` and every coefficient, so raising it 40 -> 120 necessarily changes every string in the
file.  The sealed 40-s.f. strings are the correctly rounded PREFIXES of the 120-s.f. ones.

🔴 THIS IS c37's LAW, AGAIN, AND AGAINST MYSELF: **A PRINT FORMAT IS AN INSTRUMENT.**  I wrote a
gate meant to test "the computation is unchanged" and implemented it as "the printed string is
unchanged", while the very knob under test was a print width.  The registered gate is left in the
record REFUTED-as-written; this file adds the measurement the gate was reaching for.

H1' (the repaired form, and the only claim made here): every sealed 40-s.f. value equals the
120-s.f. value rounded to 40 significant figures.  That is what "the computation is unchanged"
means when the knob is a print width.

MUTATION CONTROL: the same comparison is run against a copy of the hp file with ONE digit of ONE
eigenvalue altered, and it must report exactly one mismatch.  Without a planted failure a 101/101
green is indistinguishable from a comparison that cannot fail.

usage: m2_c55_storage_test_h1fix.py  ->  m2_c55_storage_test_h1fix.json
"""
import copy, json, os, sys
from mpmath import mp, mpf, nstr

HERE = os.path.dirname(os.path.abspath(__file__))
SEALED = os.path.join(HERE, "m2_c55_spec_even_x22_N100_dps300.json")
HP = os.path.join(HERE, "m2_c55_hp_spec_even_x22_N100_dps300_sf120.json")
OUT = os.path.join(HERE, "m2_c55_storage_test_h1fix.json")
SF = 40

mp.dps = 200


def round_to(s, sf):
    return nstr(mpf(s), sf, strip_zeros=False)


def compare(a, b):
    """returns (compared, mismatches[list of dicts]) over lam and every coefficient."""
    mism, compared = [], 0
    for ra, rb in zip(a["rungs"], b["rungs"]):
        compared += 1
        if mpf(ra["lam"]) != mpf(round_to(rb["lam"], SF)):
            mism.append(dict(rung=ra["rung"], field="lam", sealed=ra["lam"],
                             hp_rounded=round_to(rb["lam"], SF)))
        for i, (ca, cb) in enumerate(zip(ra["coef"], rb["coef"])):
            compared += 1
            if mpf(ca) != mpf(round_to(cb, SF)):
                mism.append(dict(rung=ra["rung"], field="coef[%d]" % i, sealed=ca,
                                 hp_rounded=round_to(cb, SF)))
    return compared, mism


def main():
    a, b = json.load(open(SEALED)), json.load(open(HP))
    compared, mism = compare(a, b)
    # ---- mutation control
    bm = copy.deepcopy(b)
    lam = bm["rungs"][0]["lam"]
    bm["rungs"][0]["lam"] = lam[:8] + ("7" if lam[8] != "7" else "3") + lam[9:]
    _c2, mism2 = compare(a, bm)
    fires = len(mism2) == len(mism) + 1
    out = dict(
        gate="H1' -- sealed 40-s.f. values equal the 120-s.f. values rounded to 40 s.f.",
        sealed_file=os.path.basename(SEALED), hp_file=os.path.basename(HP),
        registered_H1_as_written=dict(
            form="bit-identical strings", result="0/101 -> REFUTED",
            why="STORE_SF is the PRINT WIDTH of lam, L and every coefficient, so raising it changes "
                "every string by construction; the gate tested the print, not the computation",
            law="c37: a print format is an instrument -- and this time it was my own gate"),
        compared_values=compared, mismatches=len(mism), mismatch_detail=mism[:10],
        verdict=("HELD" if not mism else "REFUTED"),
        mutation_control=dict(planted="one digit of rungs[0].lam in the hp file",
                              mismatches_without=len(mism), mismatches_with=len(mism2),
                              fires=bool(fires)),
        reading=("the two runs are the SAME computation stored at two widths: %d values compared "
                 "(101 eigenvalues + 101x101 coefficients), %d mismatches."
                 % (compared, len(mism))))
    if not fires:
        out["verdict"] = "VOID -- the mutation control did not fire"
    json.dump(out, open(OUT, "w"), indent=1)
    print("H1' : %d values compared, %d mismatches -> %s" % (compared, len(mism), out["verdict"]))
    print("mutation control: %d -> %d mismatches, fires=%s"
          % (len(mism), len(mism2), fires))
    return 0 if out["verdict"] == "HELD" else 1


if __name__ == "__main__":
    sys.exit(main())
