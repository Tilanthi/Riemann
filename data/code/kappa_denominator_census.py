#!/usr/bin/env python3
"""
kappa_denominator_census.py -- machine 2 (BEAST-AGI / beast-atlas lane).

WHY THIS EXISTS
---------------
`machine1-kappa-set-10items.md` asks each machine to code 10 items A/B/C/D/X/U. A code is a
claim about how an item sits relative to a reference class, and the reference class has a SIZE.
A hand-written size tests the author's imagination; a grepped size tests the corpus. So before
coding, machine 2 derives two denominators per item, mechanically, from the exchange repository
at a stated commit:

  D_sup  CORROBORATION denominator. How many distinct files on origin/main reference the item,
         and how many distinct authoring machines wrote them. Pure census: a regex over every
         tracked file. Nothing here is a judgement except the choice of token.

  D_ev   EVIDENCE denominator. The scored-unit count that the item's OWN claim rests on,
         extracted verbatim by regex from the item's own source artefact, with file:line
         printed so the extraction can be disputed line by line.

DISCLOSED LIMIT, up front: the regexes are mine. What is derived is the NUMBER; what is
declared is WHICH UNIT COUNTS. Printing the matched line is the whole remedy -- a reader who
thinks the unit is wrong can see exactly the sentence I read it out of and say so.

This script is committed BEFORE it is run and before machine 2's codes are written. Its
SHA-256 is stated in `machine2-kappa-prereg-and-denominator-method.md`.

Usage:  python3 data/code/kappa_denominator_census.py          (run from repo root)
Output: plain text on stdout; redirect to data/machine2_kappa_denominator_census.out
"""

import hashlib
import os
import re
import subprocess
import sys

REPO_HINT = "machine1-kappa-set-10items.md"


# ----------------------------------------------------------------------------------
# machine attribution: derived from the filename convention PROTOCOL.md fixes, not from
# reading authorship out of the body (a body can quote another machine at length).
# ----------------------------------------------------------------------------------
def machine_of(path: str) -> str:
    b = os.path.basename(path)
    if b.startswith("machine1"):
        return "m1"
    if b.startswith("machine2") or b.startswith("machine2_"):
        return "m2"
    if b.startswith("machine3") or b.startswith("letter") or "astra-pa" in b:
        return "m3"
    if b.startswith("sapiens"):
        return "SAPIENS"
    if b.startswith("m1_"):
        return "m1"
    return "shared"  # LEDGER.md, PROTOCOL.md, PROVENANCE.md, data/*


# ----------------------------------------------------------------------------------
# The 10 items. `tokens` drive the corroboration census; `evidence` drives extraction.
# `evidence` entries are (source_file, regex, what_the_unit_is).
# ----------------------------------------------------------------------------------
ITEMS = [
    dict(
        n=1,
        short="Gram-matrix generalized eigenproblem replaces the stochastic W(f) search",
        tokens=[r"Rayleigh.{0,3}Ritz", r"generalized eigenproblem", r"heat61e", r"heat61f"],
        evidence=[
            ("machine1-heat61f-m-ladder-verdict.md", r"^\| (8|16|32) \|", "M-ladder rungs scored"),
            ("machine1-heat61e-complete-erratum.md", r"^\| (LA|LB|LC)", "spans scored at M=8"),
            ("machine1-heat61e-complete-erratum.md", r"(\d+)/64", "gate evaluations, denominator 64"),
        ],
    ),
    dict(
        n=2,
        short="random orthonormal spans reach the GA's lifetime best; wide generic near-null cluster",
        tokens=[r"heat62", r"RIDGE-GENERIC", r"near-null"],
        evidence=[
            ("machine1-heat62-reveal-ridge-generic.md", r"(\d+) trials = .*", "trials designed"),
            ("machine1-heat62-reveal-ridge-generic.md", r"(\d+)/(\d+) scored", "trials scored / designed"),
            ("machine1-heat62-reveal-ridge-generic.md", r"(\d+) DQ", "trials disqualified"),
        ],
    ),
    dict(
        n=3,
        short="the numerical-differentiation wrapper measures the epsilon-ultraviolet coefficient",
        tokens=[r"epsilon-law", r"mp\.taylor", r"240.{0,3}(?:\\cdot|\*|)\s*(?:varepsilon|ε)?/d", r"ε-law"],
        evidence=[
            ("machine1-erratum-epsilon-law.md", r"Eight independent checks", "independent checks"),
            ("machine1-erratum-epsilon-law.md", r"(\d+)/(\d+) sites ratio", "sites agreeing / sites tested"),
            ("machine1-erratum-epsilon-law.md", r"[Ff]ifteen orders of magnitude", "decades of epsilon spanned"),
        ],
    ),
    dict(
        n=4,
        short="instrument error is a function of the object class; per-class floor before selection",
        tokens=[r"#65", r"class[- ]floor", r"per-class floor"],
        evidence=[
            ("machine1-trap-register.md", r"machine [123] —", "founding instances named in the #65 entry"),
            ("machine1-note-glenn-disruptive-directive-2026-09-03.md",
             r"fired three times in one week", "independent firings claimed"),
        ],
    ),
    dict(
        n=5,
        short="route-6 kill structurally unavailable; routes 1+6 merged at instrument level",
        tokens=[r"route-6", r"Connes", r"Weil positivity"],
        evidence=[
            ("machine1-heat61f-m-ladder-verdict.md", r"arXiv:2006\.13771", "cited theorem anchoring the merge"),
            ("machine1-heat61f-m-ladder-verdict.md", r"theorem-grade", "deductive, not sampled"),
        ],
    ),
    dict(
        n=6,
        short="machine 2 cycle-10: one_half_origin does not isolate G2-32 under any uniform reading",
        tokens=[r"one_half_origin", r"G2-32", r"cycle 10", r"cycle-10"],
        evidence=[
            ("machine2-cycle10-negative-result-the-survivor-is-not-distinguished-2026-09-03.md",
             r"(\d+) rows, (\d+) distinct, (\d+) uncodable", "corpus rows coded"),
            ("machine2-cycle10-negative-result-the-survivor-is-not-distinguished-2026-09-03.md",
             r"(\d+) of (\d+)\)", "falsifier F2 trigger count before/after our own ruling"),
            ("machine2-cycle10-negative-result-the-survivor-is-not-distinguished-2026-09-03.md",
             r"^\| U[12] ", "uniform boundary readings enumerated"),
        ],
    ),
    dict(
        n=7,
        short="machine 2's 8-axis descriptor: kappa 0.000, permutation null P=1.0000, construct validity survives",
        tokens=[r"permutation null", r"P = 1\.0000", r"primes_enc", r"8-axis"],
        evidence=[
            ("machine2-protocol-debate-opening-position-2026-09-03.md",
             r"Agreement (\d+)/(\d+) cells", "inter-coder cells: the kappa denominator"),
            ("machine2-protocol-debate-opening-position-2026-09-03.md",
             r"`\w+` \+\d\.\d{3}", "per-axis kappa values published"),
            ("machine2-cycle10-negative-result-the-survivor-is-not-distinguished-2026-09-03.md",
             r"P\(random label performs as well\) = ([\d.]+)", "permutation null result"),
            ("machine2-cycle10-negative-result-the-survivor-is-not-distinguished-2026-09-03.md",
             r"\*\*9 of 11\*\*|9 of 11", "external construct-validity denominator"),
        ],
    ),
    dict(
        n=8,
        short="machine 3 three-window completeness certification vs independent Turing/Rosser counts",
        tokens=[r"turing_certify", r"nzeros", r"Turing.{0,3}Rosser|Turing's method"],
        evidence=[
            ("letter48-astra-pa-turing-certify-results-2026-09-03.md",
             r"^\| (letter40-site-1e12|neffpop-site-[AB]) \|", "windows certified"),
            ("letter48-astra-pa-turing-certify-results-2026-09-03.md",
             r"\| (\d+) \| (\d+) \| \*\*✓\*\*", "n_scan / n_rigorous per window"),
        ],
    ),
    dict(
        n=9,
        short="machine 3 N_eff campaign null, self-reclassified to the lowest register class",
        tokens=[r"N_eff", r"Bohigas", r"Novelty Register|novelty register"],
        evidence=[
            ("letter34-astra-pa-neff-campaign-wrap-2026-09-03.md",
             r"(\d+) heights with n=1, (\d+) with n=5, (\d+) with n=20", "measured heights by replication depth"),
            ("letter34-astra-pa-neff-campaign-wrap-2026-09-03.md",
             r"letters (\d+).{1,3}(\d+)", "letters spanned by the campaign"),
            ("letter41-astra-pa-response-to-glenn-disruptive-framework-2026-09-03.md",
             r"^\| .* \| \*\*[AB]/?[B]?\*\* \||^\| .* \| \*\*mostly", "threads audited in the zero-D table"),
        ],
    ),
    dict(
        n=10,
        short="Suzuki A.1(3) single-sign lane: eventual sign at one omega > 0 implies zero-freeness",
        tokens=[r"A\.1\(3\)", r"1204\.1827", r"h_.?omega|h_ω"],
        evidence=[
            ("machine1-heat61f-m-ladder-verdict.md", r"Theorem A\.1\(3\)", "statement of the lane"),
            ("machine1-addendum-suzuki-2026-09-03.md", r"Proposition 1\.2", "the proposition carrying the RH link"),
        ],
    ),
]

# A scored-run detector for item 10: a proposal has no scored run. Grep the whole tree for a
# result-bearing A.1(3) sign scan. If this finds nothing, D_ev(item 10) = 0 BY CENSUS.
ITEM10_RESULT_PATTERNS = [
    r"A\.1\(3\).{0,120}(result|RESULT|scan complete|sign at x)",
    r"omega[- ]scan results",
    r"ω-scan results",
]


def tracked_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True)
    return [p for p in out.stdout.split("\n") if p]


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except (IsADirectoryError, FileNotFoundError):
        return ""


def head_sha():
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


def main():
    if not os.path.exists(REPO_HINT):
        print(f"REFUSED: run from the repository root (cannot see {REPO_HINT})", file=sys.stderr)
        return 2

    files = tracked_files()
    bodies = {p: read(p) for p in files}
    dq = []

    print("=" * 100)
    print("MACHINE 2 -- DENOMINATOR CENSUS FOR THE 10-ITEM CROSS-MACHINE KAPPA SET")
    print("=" * 100)
    print(f"repo HEAD               : {head_sha()}")
    print(f"tracked files censused  : {len(files)}")
    print(f"script SHA-256          : {hashlib.sha256(read(__file__).encode()).hexdigest()}")
    print()
    print("D_sup = corroboration denominator (distinct FILES referencing the item, and distinct")
    print("        authoring machines among them). Derived by regex over every tracked file.")
    print("D_ev  = evidence denominator (scored units the item's own claim rests on), extracted")
    print("        verbatim from the item's own source artefact, with file:line printed.")
    print()

    summary = []
    for it in ITEMS:
        print("-" * 100)
        print(f"ITEM {it['n']}: {it['short']}")
        print("-" * 100)

        # ---- D_sup ----------------------------------------------------------------
        hits, machines = [], set()
        for p in files:
            body = bodies[p]
            if any(re.search(tok, body) for tok in it["tokens"]):
                hits.append(p)
                machines.add(machine_of(p))
        # the kappa-set letter itself mentions every item by construction; exclude it so the
        # census cannot corroborate an item with the letter that proposed it.
        hits = [h for h in hits if os.path.basename(h) != REPO_HINT]
        machines = {machine_of(h) for h in hits}
        print(f"  D_sup FILES   : {len(hits)}   (kappa-set letter itself excluded by construction)")
        print(f"  D_sup MACHINES: {len(machines)} -> {sorted(machines)}")
        for h in sorted(hits)[:12]:
            print(f"      {machine_of(h):8s} {h}")
        if len(hits) > 12:
            print(f"      ... and {len(hits) - 12} more")

        # ---- D_ev -----------------------------------------------------------------
        print("  D_ev EXTRACTIONS:")
        ev_total = 0
        ev_found = False
        for (src, rgx, unit) in it["evidence"]:
            if src not in bodies:
                print(f"      MISSING SOURCE  {src}  [{unit}]")
                dq.append(f"item {it['n']}: source file {src} not tracked at HEAD")
                continue
            matched = []
            for i, line in enumerate(bodies[src].split("\n"), 1):
                if re.search(rgx, line):
                    matched.append((i, line.strip()))
            if not matched:
                print(f"      NO MATCH        {src}  /{rgx}/  [{unit}]")
                dq.append(f"item {it['n']}: regex /{rgx}/ matched 0 lines in {src} ({unit})")
                continue
            ev_found = True
            ev_total += len(matched)
            print(f"      {len(matched):3d} x  {unit}   <- {src} /{rgx}/")
            for (i, line) in matched[:6]:
                print(f"            L{i}: {line[:150]}")
            if len(matched) > 6:
                print(f"            ... and {len(matched) - 6} more matching lines")

        summary.append(dict(n=it["n"], files=len(hits), machines=len(machines),
                            ev_lines=ev_total, ev_found=ev_found))
        print()

    # ---- item 10 special census: does a scored run exist anywhere at HEAD? ------------
    print("-" * 100)
    print("ITEM 10 SPECIAL CENSUS -- does any tracked file report a SCORED A.1(3) sign run?")
    print("-" * 100)
    found10 = []
    for p in files:
        for rgx in ITEM10_RESULT_PATTERNS:
            if re.search(rgx, bodies[p]):
                found10.append((p, rgx))
    if found10:
        for p, rgx in found10:
            print(f"  RESULT-BEARING: {p}  /{rgx}/")
    else:
        print("  NONE. D_ev(item 10) = 0 scored runs at this HEAD, BY CENSUS, not by assertion.")
    print()

    # ---- mechanical verdicts on the pre-registered hypotheses ------------------------
    print("=" * 100)
    print("MECHANICAL VERDICTS ON THE PRE-REGISTERED HYPOTHESES (prereg letter, previous commit)")
    print("=" * 100)
    no_ev = [s["n"] for s in summary if not s["ev_found"]]
    print(f"  H-A  every item has an extractable evidence denominator : "
          f"{'HOLDS' if not no_ev else 'FALSIFIED, items ' + str(no_ev)}")
    lt2 = [s["n"] for s in summary if s["machines"] < 2]
    print(f"  H-B  every item is referenced by >= 2 machines          : "
          f"{'HOLDS' if not lt2 else 'FALSIFIED, items ' + str(lt2)}")
    print( "  H-C  code correlates with denominator                   : scored in the codes letter")
    print( "  H-D  no item needs U                                    : scored in the codes letter")
    print( "  H-E  modal code is C                                    : scored in the codes letter")
    print()
    print("  per-item table (item, D_sup files, D_sup machines, D_ev matched lines):")
    for s in summary:
        print(f"    {s['n']:3d}   {s['files']:4d}   {s['machines']:3d}   {s['ev_lines']:4d}")
    print()

    # ---- DQ-SECTION, mandatory under R3 ----------------------------------------------
    print("=" * 100)
    print("DQ-SECTION (R3: a missing section is a red run, not a silent pass)")
    print("=" * 100)
    if not dq:
        print("  no disqualifications recorded")
    else:
        for d in dq:
            print(f"  DQ: {d}")
    print()
    print("  STANDING DQs that apply to this instrument whatever it prints:")
    print("  1. The regexes are authored by machine 2. The NUMBER is derived; the CHOICE OF UNIT")
    print("     is declared. Matched lines are printed so the choice is disputable.")
    print("  2. D_sup counts FILES, not independent judgements. Three files by one machine on one")
    print("     evening are one judgement wearing three filenames. That is why the machine count")
    print("     is printed beside the file count and is the number to read.")
    print("  3. Token regexes are lexical. An item discussed without its token is invisible here,")
    print("     so D_sup is a LOWER BOUND on corroboration, never an upper bound.")
    print("  4. This census measures the RECORD, not the mathematics. An item with a large D_sup")
    print("     is well-discussed, not correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
