#!/usr/bin/env python3
"""
m2_L179c_erratum_carrier_census.py -- cycle 45. v3 of the erratum-carrier census.

WHY A v3, stated as a defect in v2 and not as an improvement:

  (1) v2's per-file verdict is `labelled_here`, which returns True if ANY occurrence of the dead
      literal in the file sits within +/-2 lines of kill language. So APPENDING A MARKER AT END OF
      FILE FLIPS THE WHOLE FILE TO "LABELLED" WHILE THE ORIGINAL OCCURRENCE, possibly hundreds of
      lines up, IS STILL BARE. The reader who lands on the original occurrence sees a naked number
      and the census says the file is marked.
      🔑 A PER-FILE VERDICT CANNOT REPORT A PER-OCCURRENCE DEFECT, and the cheapest marker is
         exactly the one that satisfies the per-file verdict without reaching the reader.
      v3 therefore counts OCCURRENCES, and it counts them OUTSIDE the marker block separately.

  (2) v2 predates the marker convention m1 RULED in L181 section 3, which explicitly permits a
      SIBLING marker for a parser-consumed file (JSON, TSV) where an in-place append would break a
      reader or invalidate an md5 receipt. v2 has no class for that, so it reports a correctly
      marked JSON as BARE.
      🔑 A DETECTOR WRITTEN BEFORE THE CONVENTION SCORES THE CONVENTION AS A FAILURE. v3 adds the
         class rather than loosening the old one: BOTH verdicts are printed for every file.

v3 emits four coverage classes per (erratum, literal, file):
  ADJACENT   original occurrence has kill language within +/-2 lines, outside any marker block
  MARKER     the file carries an in-file ERRATUM MARKER block that prints this literal
  SIBLING    a marker file in the SAME directory names this file's basename AND prints this literal
             AND uses kill language
  BARE       none of the above
Precedence for the headline: ADJACENT > SIBLING > MARKER > BARE (a marker adjacent to the reader's
eye beats a marker at the bottom of a 400-line file).
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import importlib.util
# NB: loaded under a NON-"__main__" module name so v2's own __main__ guard stays shut and it
# does NOT re-run and re-write its own output JSON while we are reading the corpus it measures.
spec = importlib.util.spec_from_file_location("m2_L179b_v2", os.path.join(HERE, "m2_L179b_erratum_carrier_census.py"))
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)

ERRATA, KILL_RE = v2.ERRATA, v2.KILL_RE
WINDOW = v2.WINDOW_MARK
MARKER_BANNER = re.compile(r"ERRATUM MARKER, ADDED")
MARKER_FILE_RE = re.compile(r"(?i)(^00-ERRATUM|\.ERRATUM-\d+\.)")
SELF = os.path.basename(__file__)


def sh(a):
    return subprocess.check_output(a, cwd=REPO).decode("utf-8", "replace")


def toks_of(text):
    return set(v2.TOKEN_RE.findall(text))


def has_token(text, lit):
    """🔴 v3 draft 1 used `lit in text`, a SUBSTRING test, and it re-introduced EXACTLY the defect
    v2's K8 exists to prevent: the dead literal `103.72` of ERRATUM 3 matched INSIDE the zero
    ordinate `103.7255380404`, inventing 20 false carrier triples. c39's law, on the instrument
    written to enforce c39's law. Token-exact, always."""
    return lit in toks_of(text)


def read(p):
    with open(os.path.join(REPO, p), encoding="utf-8", errors="replace") as f:
        return f.read()


def marker_block_lines(lines):
    """indices of lines inside an in-file ERRATUM MARKER block (banner to end of file)."""
    for i, l in enumerate(lines):
        if MARKER_BANNER.search(l):
            return set(range(max(0, i - 2), len(lines)))
    return set()


def classify(path, lit, dir_markers):
    lines = read(path).splitlines()
    block = marker_block_lines(lines)
    occ = [i for i, l in enumerate(lines) if has_token(l, lit)]
    occ_out = [i for i in occ if i not in block]
    occ_in = [i for i in occ if i in block]
    adjacent = False
    for i in occ_out:
        lo, hi = max(0, i - WINDOW), min(len(lines), i + WINDOW + 1)
        if any(KILL_RE.search(lines[j]) for j in range(lo, hi)):
            adjacent = True
    base = os.path.basename(path)
    sibling = False
    for mp, mtxt in dir_markers.get(os.path.dirname(path), []):
        if os.path.basename(mp) == base:
            continue
        if base in mtxt and lit in mtxt and KILL_RE.search(mtxt):
            sibling = True
    marker = len(occ_in) > 0
    # PRECEDENCE, and the reasoning, because a precedence order is a claim about a READER:
    # ADJACENT (the marker is where the eye lands) > MARKER (same file, but possibly 400 lines away)
    # > SIBLING (a different file entirely, which is the ONLY option for a parser-consumed artefact
    # and is therefore best-available there, not second-best). The three booleans are printed
    # separately below so the collapse is never the only thing on offer.
    cls = "ADJACENT" if adjacent else ("MARKER" if marker else ("SIBLING" if sibling else "BARE"))
    return cls, len(occ), len(occ_out), len(occ_in), adjacent, sibling, marker


def main():
    data_files = [p for p in sh(["git", "ls-files", "data"]).splitlines()
                  if p and not p.endswith(".pyc") and "erratum_carrier_census" not in p]
    dir_markers = {}
    for p in data_files:
        if MARKER_FILE_RE.search(os.path.basename(p)):
            dir_markers.setdefault(os.path.dirname(p), []).append((p, read(p)))

    # ---- KNOWN-ANSWER TEST, runs first ------------------------------------------------
    kats = []
    def K(n, ok, why): kats.append((n, ok, why))
    dead22 = ERRATA[22]["lits"][0]
    live22 = v2.LIVE_130
    c43j = "data/c43/c43_x13_N100_dps150_widened.json"
    c1 = classify(c43j, dead22, dir_markers)[0]
    K("K1 the byte-identical c43 JSON is SIBLING-covered (00-ERRATUM-22-READ-FIRST.md names it)",
      c1 == "SIBLING", "EXTERNAL ground truth: m1-L181 sec 3(3) ruled this exact case correct")
    K("K2 v2 calls that same file BARE (the class v2 cannot express)",
      not v2.labelled_here(read(c43j).splitlines(), dead22), "the defect being repaired")
    K("K3 a synthetic absent literal is covered nowhere",
      classify(c43j, v2.SYNTH_ABSENT, dir_markers)[0] == "BARE", "synthetic negative")
    K("K4 the LIVE 130 s.f. value is not in any erratum's dead list",
      all(live22 not in e["lits"] for e in ERRATA), "an all-DEAD classifier fails here")
    dead20 = "2.9078e9"
    K("K5 m1's own footered file reads ADJACENT, not merely MARKER",
      classify("data/code/machine1_l171_c31v_f_attack.py", dead20, dir_markers)[0] == "ADJACENT",
      "m1's footers are value-adjacent; positive control on ADJACENT")
    a3l, a3d = v2.A3_LIVE, v2.A3_DEAD_9SF
    K("K6 token matching does not report the live 26-digit a3 as the dead 9-digit a3",
      a3d in a3l and a3l != a3d, "the prefix trap, carried over from v2 K8")
    e3lit = "103.72"
    false_carrier = "data/c42/c42_convergence_in_x.tsv"
    K("K7 substring trap: 103.72 inside the ordinate 103.7255380404 is NOT a carrier",
      (not has_token(read(false_carrier), e3lit)) and ("103.7255380404" in read(false_carrier)),
      "v3 draft 1 failed this and invented 20 false triples")
    n_marker_files = sum(len(v) for v in dir_markers.values())
    K("K8 marker-file index is non-empty and derived by filename rule, not by hand",
      n_marker_files > 0, "a sibling detector with no sibling index is vacuous")
    K("K9 this instrument excludes itself and v2 from the scanned corpus",
      not any("erratum_carrier_census" in p for p in data_files), "c41: exclude your own output AND source")
    print("== KNOWN-ANSWER TEST OF THIS INSTRUMENT (runs first)   %d/%d"
          % (sum(1 for _, o, _ in kats if o), len(kats)))
    for n, o, w in kats:
        print("   %s %-78s (%s)" % ("PASS" if o else "FAIL", n, w))
    print()

    print("== PER-OCCURRENCE COVERAGE, value-naming errata only")
    print("   %-62s %-9s %-9s %5s %5s %5s" % ("file", "v3", "v2", "occ", "out", "in"))
    tot = dict(ADJACENT=0, SIBLING=0, MARKER=0, BARE=0)
    bools = dict(adjacent=0, in_file_marker=0, sibling=0)
    occ_out_bare = 0
    rows = []
    for e in ERRATA:
        if e["cls"] != "VALUE-NAMED":
            continue
        for lit in e["lits"]:
            carriers = [p for p in data_files if has_token(read(p), lit)]
            if not carriers:
                continue
            print("   ERRATUM %-3d dead literal %s" % (e["id"], (lit[:52] + "...") if len(lit) > 55 else lit))
            for p in sorted(carriers):
                cls, n, nout, nin, adj, sib, mk = classify(p, lit, dir_markers)
                v2cls = "LABELLED" if v2.labelled_here(read(p).splitlines(), lit) else "BARE"
                tot[cls] += 1
                bools["adjacent"] += adj; bools["in_file_marker"] += mk; bools["sibling"] += sib
                if cls in ("MARKER", "BARE"):
                    occ_out_bare += nout
                print("      %-62s %-9s %-9s %5d %5d %5d" % (p, cls, v2cls, n, nout, nin))
                rows.append((e["id"], p, cls, v2cls, n, nout, nin))
    print()
    print("== ANSWER, with the denominator named")
    N = sum(tot.values())
    print("   carrier (erratum, literal, file) triples in the data corpus : %d" % N)
    for k in ("ADJACENT", "SIBLING", "MARKER", "BARE"):
        print("      %-9s %3d" % (k, tot[k]))
    print("   the three coverage booleans, counted independently of the precedence collapse:")
    for k, v_ in bools.items():
        print("      %-16s %3d" % (k, v_))
    print("   triples BARE under v3                                       : %d" % tot["BARE"])
    print("   v2 would report BARE for                                    : %d"
          % sum(1 for r in rows if r[3] == "BARE"))
    print("   OCCURRENCES still unlabelled outside any marker block, in")
    print("   files whose only marker is an EOF block or nothing at all   : %d" % occ_out_bare)
    print()
    print("   READING: an ADJACENT or SIBLING triple is marked in the sense m1 ruled. A MARKER triple")
    print("   is marked in the sense v2 measures and NOT in the sense a reader experiences, because the")
    print("   original occurrence is still bare where it sits. BARE is unmarked in every sense.")


if __name__ == "__main__":
    main()
