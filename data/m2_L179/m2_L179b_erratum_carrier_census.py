#!/usr/bin/env python3
"""
m2_L179b — ERRATUM-CARRIER CENSUS of this repository's published data directories.

THE QUESTION (BEAST-AGI, closing out L179, after finding that ERRATUM 22 was letter-only and
data/c43 carried the withdrawn digits with a clean face):

    Of our published data directories on this repo, how many carry a value that a later erratum
    or withdrawal has killed, and how many of those carry a data-layer marker?

TWO ARMS, DELIBERATELY, BECAUSE ONE NUMBER HERE WOULD BE A CHOICE OF KNOB PRESENTED AS A FACT
  ARM 1  LOWER BOUND, named-erratum arm. The population of DEATHS is enumerated by measurement
         (every ERRATUM id that appears anywhere in the tracked prose = ids 0..22) and then each
         erratum is HAND-CLASSIFIED, with the erratum's own words quoted, into: kills no numeric
         value / kills a value and names it verbatim / kills a value but does not print it /
         kills something outside this instrument's literal class (an integer, a 2-figure ratio).
         Only the VALUE-NAMED ones can be searched for. That is the lower bound and it is honest
         about why it is a lower bound.
  ARM 2  UPPER BOUND, mechanical arm. Every decimal literal that appears on a line carrying kill
         language anywhere in the tracked prose, ALL ASSUMED DEAD, searched over the data corpus.
         Deliberately over-inclusive: a line that says "X is wrong -> live: Y" donates BOTH X and Y.

MATCHING IS TOKEN-EXACT, NOT SUBSTRING. A substring search reports the live 26-digit a3
(11.700717320433667601156432) as a carrier of the dead 9-digit a3 (11.7007173), because one is a
prefix of the other. That is the same prefix-vs-rounding trap that nearly produced a false headline
in the L179 comparator, so it is tested in the KAT below (K8).

TWO MARKER CRITERIA, BOTH REPORTED, BECAUSE "HAS A MARKER" IS ALSO A KNOB
  M1  value-adjacent: some file in that directory prints the dead literal within +/-2 lines of
      kill language. Strict: it marks the number, not the topic.
  M2  directory-level: some file in that directory names a numbered erratum and uses withdrawal
      language. Weaker: a reader of THAT file learns the value is dead, a reader of a sibling
      .json still does not.

DECLARED LIMITATIONS — read before quoting any number here
  * ARM 1's classification is a HAND classification of 23 documents. A hand classification is a
    detector too; its known answers are K5/K6 in the KAT, and every row prints the quote it was
    made from so a reader can overturn it.
  * An erratum that kills a value WITHOUT PRINTING IT is unsearchable in principle. ERRATUM 12 is
    exactly that case, and says so in its own text ("not reproduced here, not even to name it").
    Those are counted as UNMEASURABLE, not as zero.
  * Literal class = decimal tokens (digits, point, digits, optional exponent). ERRATUM 9 strikes an
    integer node count and ERRATUM 4 a route count; both are outside the class, declared, not absent.
  * This measures TEXTUAL survival. A dead value living inside a plot, a pickle, or a restatement
    at a different width is invisible here.
  * This script excludes ITSELF and its own outputs from the data corpus. A search program contains
    every term it searches for.
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SELF_MARK = "erratum_carrier_census"
WINDOW_MARK = 2          # +/- lines for the value-adjacent marker test
HARVEST_FLOOR = 6        # ARM 2 only: minimum significant digits harvested from prose

TOKEN_RE = re.compile(r"(?<![\w.])([0-9]+\.[0-9]+(?:[eE][+-]?[0-9]+)?)(?![\w.])")
HARVEST_RE = re.compile(r"(?<![\w.])([0-9]+\.[0-9]{%d,}(?:[eE][+-]?[0-9]+)?)(?![\w.])" % (HARVEST_FLOOR - 1))
KILL_RE = re.compile(r"(?i)(\bwithdraw\w*\b|\bretract\w*\b|\bsupersed\w*\b|\bstruck\b|\bdead\b|"
                     r"do not copy|is wrong from|are wrong from|\bERRATUM\b|\bSTRIKE\b|\[FALSIFIED\])")
MARKER_RE = re.compile(r"(?i)erratum\s*#?\s*\d+")
MARKER_STRENGTH_RE = re.compile(r"(?i)\b(withdrawn|withdraw|dead|do not copy|retracted|superseded|struck)\b")
# M2 is reported under TWO lexicons because one word moves the count. "strict" is the line above;
# "wide" also accepts a directory that says the value is WRONG without using a withdrawal word.
# data/m2_L179's README is exactly that case: it says "wrong from s.f. 55" and prints the live value.
MARKER_STRENGTH_WIDE_RE = re.compile(
    r"(?i)(\b(withdrawn|withdraw|dead|do not copy|retracted|superseded|struck)\b|is wrong|are wrong|wrong from)")

# ---------------------------------------------------------------------------
# ARM 1 — the 23 numbered machine-2 errata, hand-classified, each with the quote it was read from.
# classes: NOT-A-KILL | NOT-A-VALUE | VALUE-NAMED | VALUE-UNNAMED | BELOW-CLASS
# ---------------------------------------------------------------------------
ERRATA = [
 dict(id=0,  doc="machine2-c35-PREREG-a4-sign-convention-or-disagreement.md", cls="NOT-A-VALUE",
      lits=[], quote="a HAND-TYPED filing time ... FUTURE-DATED by ~11 minutes"),
 dict(id=1,  doc="machine2_ERRATUM_1_to_letters3and4_reply_2026-09-02.md", cls="VALUE-UNNAMED",
      lits=[], quote="Also WITHDRAWN: the kappa_3 degradation table in section 2 of the 19:19Z reply "
                     "(the table's entries are not reprinted in the erratum)"),
 dict(id=2,  doc="machine2-ERRATUM-2-to-mac-2026-09-02.md", cls="NOT-A-VALUE", lits=[],
      quote="[WITHDRAWN - FALSE. The premise was ours, not Mac's, and nothing supported it.]"),
 dict(id=3,  doc="machine2-ERRATUM-3-e8-range-2026-09-03.md", cls="VALUE-NAMED",
      lits=["103.72", "1.7499"],
      quote="The published range 100.09-103.72 % is withdrawn ... the 1.7499 arm row unstruck"),
 dict(id=4,  doc="machine2-ERRATUM-4-ban-spend-understated-5x-2026-09-03.md", cls="BELOW-CLASS",
      lits=[], quote="the true spend is 15 of 36 routes (42 %), not 3 - integer counts, outside the literal class"),
 dict(id=5,  doc="machine2-ERRATUM-5-cycle9-both-falsifiers-refuted-us-2026-09-03.md", cls="VALUE-UNNAMED",
      lits=[], quote="Withdrawn: the whole of section 1's association table"),
 dict(id=6,  doc="machine2-ERRATUM-6-kappa-prereg-blinding-claim-superseded.md", cls="NOT-A-VALUE",
      lits=[], quote="[WITHDRAWN] That sentence was verified true against origin/main at ..."),
 dict(id=7,  doc="machine2-ERRATUM-7-de-roton-page-range.md", cls="NOT-A-VALUE", lits=[],
      quote="[WITHDRAWN] The page range is wrong - a citation, not a measured value"),
 dict(id=8,  doc="machine2-ERRATUM-8-zoo-decay-consequence-withdrawn.md", cls="NOT-A-VALUE", lits=[],
      quote="our zoo-reading rule 'a stall is interpretable and a decay is not' is WITHDRAWN as backwards"),
 dict(id=9,  doc="machine2-ERRATUM-9-node-count-and-the-support-blind-width-rule.md", cls="BELOW-CLASS",
      lits=[], quote="STRIKE 1 - 768 nodes/panel is wrong; degree 8 is 384 nodes per panel (integer)"),
 dict(id=10, doc="machine2-ERRATUM-10-cycle23-eigenvalue-half-was-scoped-to-one-site.md", cls="NOT-A-VALUE",
      lits=[], quote="Nothing in the arithmetic. Everything in the quantifier"),
 dict(id=11, doc="machine2-c30-charter-vote-...(erratum 11 is referenced, not a kill)", cls="NOT-A-KILL",
      lits=[], quote="a3^BL = 11.7007173 (9 s.f., ERRATUM 11) SURVIVES - a refusal to claim a 10th figure"),
 dict(id=12, doc="machine2-ERRATUM-12-sigfig-labels-were-post-point-digit-counts.md", cls="VALUE-UNNAMED",
      lits=[], quote="The twelve-figure form printed in the cycle-28 letter is dead and superseded; "
                     "it is not reproduced here, NOT EVEN TO NAME IT"),
 dict(id=13, doc="machine2-ERRATUM-13-the-c31b-scored-JSON-diagnostic-c0-new-with-a-operative-had-the-wrong-sign.md",
      cls="VALUE-NAMED", lits=["1.64521001744e-15"],
      quote="+1.64521001744e-15; the correct value under our own sign convention is -1.6216e-15"),
 dict(id=14, doc="machine2-ERRATUM-14-c31-5-said-part-of-c0-new-is-extrapolation-error-it-is-all-of-it.md",
      cls="NOT-A-VALUE", lits=[], quote="an attribution of the error, no digit moves"),
 dict(id=15, doc="machine2-ERRATUM-15-c30-4-the-delta-star-exoneration-half-is-withdrawn-as-an-inference.md",
      cls="NOT-A-VALUE", lits=[], quote="WITHDRAWN as an inference. A best-column test ranks; it does not exonerate"),
 dict(id=16, doc="machine2-ERRATUM-16-c30-4-the-1.489e-15-guard-pair-mixes-two-baselines.md",
      cls="BELOW-CLASS", lits=[],
      quote="the pair '+1.489e-15 ... 2.9x its own guard' mixes two baselines - the killed object is "
            "the PAIRING; both replacement pairs keep a literal that is still live somewhere"),
 dict(id=17, doc="machine2-ERRATUM-17-c32-fold-series-stated-the-wrong-sign-relation.md",
      cls="VALUE-NAMED", lits=["20.4755387553904124991788"],
      quote="The a4 in the committed c32_higher_coeffs.out has the WRONG SIGN ... it prints "
            "+20.4755387553904124991788, and the fold law's fourth coefficient is -20.4755387553904125"),
 dict(id=18, doc="machine2-ERRATUM-18-c35-P1-supporting-sentence-overstated.md", cls="NOT-A-VALUE",
      lits=[], quote="a supporting sentence overstated; no digit withdrawn"),
 dict(id=19, doc="machine2-ERRATUM-19-published-Dstar-width-175-exceeds-its-certified-accuracy-151.md",
      cls="VALUE-NAMED", lits=["7.18811e-133"],
      quote="[WITHDRAWN] for the 7.18811e-133 error bar as an accuracy statement"),
 dict(id=20, doc="machine2-ERRATUM-20-c31-transfer-coefficient-withdrawal-renumbered-off-a-colliding-erratum-12.md",
      cls="VALUE-NAMED", lits=["2.9078e9"],
      quote="the c31 section 4 transfer coefficient 2.9078e9 is withdrawn ... corrected 3.11303485273e9"),
 dict(id=21, doc="machine2-ERRATUM-21-armB-quadrature-cutoff-unstated-and-m3s-0.69-percent-was-ours.md",
      cls="NOT-A-VALUE", lits=[],
      quote="an unstated cutoff and a re-attribution of a 0.69 % gap; the published U=40 literal is "
            "correct FOR ITS CUTOFF and is not withdrawn"),
 dict(id=22, doc="machine2-ERRATUM-22-c43-reading-form-digits-55-to-60-are-wrong-and-the-cause-is-an-iteration-count-not-a-precision.md",
      cls="VALUE-NAMED",
      lits=["3.72089974166712393579143476609454069409138561914061952905941e-59",
            "3.720899741667123935791434766094540694091385619140619529059414458909564478140552097595690637495444086e-59"],
      quote="WITHDRAWN : 3.72089974166712393579143476609454069409138561914061952905941e-59"),
]

LIVE_130 = ("3.7208997416671239357914347660945406940913856191406195228312934723556452525113385017077157011"
            "26959943461337701579966383375965519379e-59")
DEAD_W60 = "3.72089974166712393579143476609454069409138561914061952905941e-59"
A3_LIVE = "11.700717320433667601156432"
A3_DEAD_9SF = "11.7007173"
SYNTH_ABSENT = "9.87654321098765432109e-77"


def sh(args):
    return subprocess.check_output(args, cwd=REPO).decode("utf-8", "replace")


def read(p):
    with open(os.path.join(REPO, p), "rb") as f:
        return f.read().decode("utf-8", "replace")


def adding_subjects():
    out = sh(["git", "log", "--diff-filter=A", "--reverse", "--name-only", "--format=\x01%s"])
    sub, res = None, {}
    for line in out.splitlines():
        if line.startswith("\x01"):
            sub = line[1:]
        elif line.strip():
            res.setdefault(line.strip(), sub)
    return res


def lane_of(subject):
    s = (subject or "").lower()
    if s.startswith(("machine2", "beast", "m2")):
        return "machine2"
    if s.startswith(("machine1", "m1")):
        return "machine1"
    if s.startswith(("machine3", "m3")):
        return "machine3"
    return "other"


def labelled_here(text_lines, lit):
    """is this literal printed within WINDOW_MARK lines of kill language, in THIS file?"""
    idx = [i for i, l in enumerate(text_lines) if lit in l]
    for i in idx:
        lo, hi = max(0, i - WINDOW_MARK), min(len(text_lines), i + WINDOW_MARK + 1)
        if any(KILL_RE.search(text_lines[j]) for j in range(lo, hi)):
            return True
    return False


def main():
    prose = [p for p in sh(["git", "ls-files", "*.md"]).splitlines() if p]
    data_files = [p for p in sh(["git", "ls-files", "data"]).splitlines()
                  if p and not p.endswith(".pyc") and SELF_MARK not in p]
    dropped = len([p for p in sh(["git", "ls-files", "data"]).splitlines() if p]) - len(data_files)
    texts = {p: read(p) for p in data_files}
    lines = {p: texts[p].splitlines() for p in data_files}
    toks = {p: set(TOKEN_RE.findall(texts[p])) for p in data_files}
    subj = adding_subjects()
    dir_files = defaultdict(list)
    for p in data_files:
        dir_files[os.path.dirname(p)].append(p)

    # ---------------- KAT, first, every run ----------------
    cases, ok = [], 0

    def case(name, got, why):
        nonlocal ok
        cases.append(("PASS" if got else "FAIL", name, why))
        ok += bool(got)

    case("K1 ERRATUM 22 is in the hand table as VALUE-NAMED",
         any(e["id"] == 22 and e["cls"] == "VALUE-NAMED" for e in ERRATA),
         "EXTERNAL ground truth: the erratum letter, commit 9e3a1ad")
    case("K2 its dead literal is found in data/c43",
         any(f.startswith("data/c43/") and DEAD_W60 in toks[f] for f in data_files),
         "the artefact under repair")
    case("K3 the LIVE 130-s.f. value is found in data/m2_L179",
         any(f.startswith("data/m2_L179/") and LIVE_130 in toks[f] for f in data_files),
         "search plumbing, second literal")
    case("K4 a synthetic absent literal is found nowhere",
         not any(SYNTH_ABSENT in t for t in toks.values()),
         "synthetic negative")
    case("K5 the LIVE value is NOT in any erratum's dead-literal list",
         not any(LIVE_130 in e["lits"] for e in ERRATA),
         "tests the hand step: an all-DEAD classifier fails here")
    case("K6 every hand-listed dead literal is a well-formed decimal token",
         all(TOKEN_RE.fullmatch(l) for e in ERRATA for l in e["lits"]),
         "tests the hand step for transcription damage")
    case("K7 the marker detector fires on data/c43 and is silent on data/results",
         any(MARKER_RE.search(texts[f]) and MARKER_STRENGTH_RE.search(texts[f])
             for f in dir_files.get("data/c43", []))
         and not any(MARKER_RE.search(texts[f]) and MARKER_STRENGTH_RE.search(texts[f])
                     for f in dir_files.get("data/results", [])),
         "00-ERRATUM-22-READ-FIRST.md exists in one and not the other")
    case("K8 token matching does NOT report the live 26-digit a3 as a carrier of the dead 9-digit a3",
         any(A3_LIVE in toks[f] for f in data_files)
         and not all(A3_DEAD_9SF in toks[f] for f in data_files if A3_LIVE in toks[f]),
         "the prefix trap: a substring search fails this case")

    print("== KNOWN-ANSWER TEST OF THIS INSTRUMENT (runs first, every run)   %d/%d" % (ok, len(cases)))
    for verdict, name, why in cases:
        print("   %s %-78s (%s)" % (verdict, name, why))
    print()

    # ---------------- corpora ----------------
    print("== CORPORA, derived by measurement (git ls-files + git history), not by memory")
    print("   prose corpus : %d tracked *.md" % len(prose))
    print("   data corpus  : %d tracked files under data/  (%d dropped: .pyc and this instrument's own files)"
          % (len(data_files), dropped))
    print("   directories  : %d containing at least one tracked file in the corpus" % len(dir_files))
    print("   matching     : TOKEN-EXACT on decimal literals, never substring")
    print()

    # ---------------- ARM 1 ----------------
    print("== ARM 1 (LOWER BOUND) — the numbered machine-2 errata, hand-classified")
    byclass = defaultdict(list)
    for e in ERRATA:
        byclass[e["cls"]].append(e["id"])
    print("   population of deaths: %d numbered errata (ids %d..%d, enumerated by grep over the prose corpus)"
          % (len(ERRATA), min(e["id"] for e in ERRATA), max(e["id"] for e in ERRATA)))
    for c in ("VALUE-NAMED", "VALUE-UNNAMED", "BELOW-CLASS", "NOT-A-VALUE", "NOT-A-KILL"):
        print("      %-14s %2d   %s" % (c, len(byclass[c]), byclass[c]))
    print()

    carriers = defaultdict(list)          # dir -> [(erratum id, literal, file, labelled?)]
    for e in ERRATA:
        if e["cls"] != "VALUE-NAMED":
            continue
        print("   ERRATUM %d  %s" % (e["id"], e["doc"][:88]))
        print("      quote: %s" % e["quote"][:150])
        for lit in e["lits"]:
            hits = [f for f in data_files if lit in toks[f]]
            print("      dead literal %s  -> %d carrier file(s)" % (lit[:52] + ("..." if len(lit) > 52 else ""), len(hits)))
            for f in sorted(hits):
                lab = labelled_here(lines[f], lit)
                print("         %-62s %s" % (f, "LABELLED in place" if lab else "BARE"))
                carriers[os.path.dirname(f)].append((e["id"], lit, f, lab))
        print()

    # ---------------- ARM 2 ----------------
    harvest = defaultdict(list)
    for p in prose:
        for i, l in enumerate(read(p).splitlines()):
            if KILL_RE.search(l):
                for m in HARVEST_RE.finditer(l):
                    harvest[m.group(1)].append((p, i + 1))
    arm2 = defaultdict(set)
    for lit in harvest:
        for f in data_files:
            if lit in toks[f]:
                arm2[os.path.dirname(f)].add(lit)
    print("== ARM 2 (UPPER BOUND) — every literal on a kill-language line, ALL assumed dead")
    print("   harvested %d literals at floor %d s.f.; %d of them occur in the data corpus"
          % (len(harvest), HARVEST_FLOOR, len({l for d in arm2 for l in arm2[d]})))
    print("   this arm deliberately counts the erratum's own CORRECTED value as if it were dead.")
    print()

    # ---------------- directory census ----------------
    rows = []
    for d in sorted(dir_files):
        fs = dir_files[d]
        lanes = defaultdict(int)
        for f in fs:
            lanes[lane_of(subj.get(f))] += 1
        lane = max(lanes, key=lambda k: lanes[k])
        car = carriers.get(d, [])
        m1 = any(lab for (_, _, _, lab) in car) or any(
            any(labelled_here(lines[g], lit) for g in fs) for (_, lit, _, _) in car)
        m2 = any(MARKER_RE.search(texts[f]) and MARKER_STRENGTH_RE.search(texts[f]) for f in fs)
        m2w = any(MARKER_RE.search(texts[f]) and MARKER_STRENGTH_WIDE_RE.search(texts[f]) for f in fs)
        rows.append(dict(directory=d, files=len(fs), lane=lane, lane_counts=dict(lanes),
                         arm1_carrier=bool(car),
                         arm1_dead_literals=sorted({lit for (_, lit, _, _) in car}),
                         arm1_carrier_files=sorted({f for (_, _, f, _) in car}),
                         arm1_bare_files=sorted({f for (_, _, f, lab) in car if not lab}),
                         marker_M1_value_adjacent=bool(m1), marker_M2_directory_level=bool(m2),
                         marker_M2_wide=bool(m2w),
                         arm2_carrier=bool(arm2.get(d)), arm2_literals=len(arm2.get(d, ()))))

    print("== DIRECTORY CENSUS")
    print("   %-30s %5s %-9s %-7s %-4s %-4s %-5s %-6s" %
          ("directory", "files", "lane", "ARM1", "M1", "M2", "M2wide", "ARM2"))
    for r in rows:
        print("   %-30s %5d %-9s %-7s %-4s %-4s %-5s %-6s" %
              (r["directory"], r["files"], r["lane"],
               "CARRIER" if r["arm1_carrier"] else "-",
               "yes" if r["marker_M1_value_adjacent"] else "-",
               "yes" if r["marker_M2_directory_level"] else "-",
               "yes" if r["marker_M2_wide"] else "-",
               "%d" % r["arm2_literals"] if r["arm2_carrier"] else "-"))
    print()

    ours = [r for r in rows if r["lane"] == "machine2"]
    a1 = [r for r in rows if r["arm1_carrier"]]
    a1o = [r for r in ours if r["arm1_carrier"]]
    a2 = [r for r in rows if r["arm2_carrier"]]

    print("== ANSWER, with the denominator named every time")
    print("   DENOMINATOR A: all data directories in the corpus (every lane)        = %d" % len(rows))
    print("   DENOMINATOR B: those whose tracked files are majority machine2-added  = %d" % len(ours))
    print()
    print("   ARM 1 (lower bound, only errata that NAME the dead literal):")
    print("      carrying a killed value : %d of %d (A)   |   %d of %d (B)"
          % (len(a1), len(rows), len(a1o), len(ours)))
    print("      of those, M1 value-adjacent marker : %d of %d"
          % (len([r for r in a1 if r["marker_M1_value_adjacent"]]), len(a1)))
    print("      of those, M2 directory-level marker: %d of %d  (strict lexicon)"
          % (len([r for r in a1 if r["marker_M2_directory_level"]]), len(a1)))
    print("      of those, M2 directory-level marker: %d of %d  (wide lexicon: 'wrong from' also counts)"
          % (len([r for r in a1 if r["marker_M2_wide"]]), len(a1)))
    print("      carrier files with NO in-place label at all: %d"
          % sum(len(r["arm1_bare_files"]) for r in a1))
    print("   ARM 2 (upper bound, every kill-line literal assumed dead):")
    print("      carrying a 'killed' value: %d of %d (A)" % (len(a2), len(rows)))
    print()
    print("   UNMEASURABLE, and named: %d errata kill a value they do not print (ids %s), and %d kill "
          "something outside the decimal-literal class (ids %s). Those cannot be searched for at all."
          % (len(byclass["VALUE-UNNAMED"]), byclass["VALUE-UNNAMED"],
             len(byclass["BELOW-CLASS"]), byclass["BELOW-CLASS"]))
    print("   KAT %d/%d." % (ok, len(cases)))

    out = dict(kat_pass=ok, kat_total=len(cases), prose_files=len(prose),
               data_files=len(data_files), directories=len(rows),
               errata_population=len(ERRATA),
               errata_by_class={c: byclass[c] for c in byclass},
               denominator_A=len(rows), denominator_B=len(ours),
               arm1_carrier_dirs=[r["directory"] for r in a1],
               arm1_carrier_dirs_m2lane=[r["directory"] for r in a1o],
               arm1_marker_M1=[r["directory"] for r in a1 if r["marker_M1_value_adjacent"]],
               arm1_marker_M2=[r["directory"] for r in a1 if r["marker_M2_directory_level"]],
               arm1_marker_M2_wide=[r["directory"] for r in a1 if r["marker_M2_wide"]],
               arm2_carrier_dirs=[r["directory"] for r in a2],
               rows=rows)
    dest = os.path.join(REPO, "data/m2_L179/erratum_carrier_census.json")
    with open(dest, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote %s" % dest)
    return 0 if ok == len(cases) else 2


if __name__ == "__main__":
    sys.exit(main())
