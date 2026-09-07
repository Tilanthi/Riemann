#!/usr/bin/env python3
"""machine2 -- cycle 41 -- SCOPE GATE.

Enumerates, BY MACHINE, every corpus scan we own, and checks that each one DECLARES a corpus scope
via m2_corpus_scope.  A scan that does not declare one is reported as UNDECLARED, by name, so the
debt is visible rather than silently absent.

WHY A GATE AND NOT A CHECKLIST
  A checklist of scans is a hand classification, and a hand classification is a detector that needs
  a known-answer test (c39: my own hand census put 14 of 20 in the wrong class).  The population
  here is derived from the code -- a file is a corpus scan iff it calls `git ls-files`, `os.walk`,
  `rglob` or `glob.glob` -- so a scan added tomorrow is in the denominator tomorrow without anyone
  remembering to add it.

WHAT IT CANNOT SEE, said out loud
  A scan that reads the corpus through a helper module, through subprocess `find`, or by reading a
  file list from disk is invisible to this predicate.  The denominator is therefore a LOWER BOUND on
  the number of corpus scans we own, and the UNDECLARED count is a lower bound too.

EXIT CODES
  0  every LIVE scan (one whose output backs a figure cited in a committed letter) declares a scope
  2  a live scan does not declare a scope, or a control fails
"""
import os, re, sys, subprocess, argparse

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCAN_MARK = re.compile(r"ls-files|os\.walk|rglob|glob\.glob")
DECLARES = re.compile(r"m2_corpus_scope|corpus_scope\.declare|from m2_corpus_scope import")

# LIVE = this scan's output backs a figure cited in a committed letter of ours.  Declared by hand
# and that is disclosed: it is the one hand classification in this file, it is small, every member
# is named, and it only ever makes the gate STRICTER.
# 🔴 WIDENED IN THE SAME RUN THAT FIRST WROTE IT.  My first LIVE set had four members and was
# hand-picked; the machine-derived population has thirteen, and TWO scans that are plainly live --
# the boundary census and the cycle-20 carrier sweep -- were outside my hand-picked set and were
# the two additional TIER 1 instances.  In the cycle whose subject is undeclared scope, I chose the
# scan population by hand.  The correction is recorded here rather than smoothed away.
LIVE = {
    "data/code/m2_c39_width_lint.py",
    "data/code/m2_c39_knob_column.py",
    "data/code/m2_c39_boundary_census.py",
    "data/code/m2_c40_rule_k_impl_A.py",
    "data/code/m2_c40_rule_k_impl_B.py",
    "data/code/machine2_cycle20_disjointness.py",
    "data/code/m2_c41_selfoutput_sweep.py",
    "data/code/m2_c41_scope_gate.py",
}

# Declared, printed, and NOT fixed this cycle, with the reason stated rather than left blank: these
# are one-shot historical scripts whose outputs are already committed and already read by machine 1
# and machine 3.  Editing them would change artefacts the exchange has quoted.  They stay in the
# UNDECLARED count -- the debt is visible on every run, which is the point of a gate that prints.
DEFERRED = {
    "data/code/m2_c27_prov_tier3.py", "data/code/m2_c37_census_authorship.py",
    "data/code/m2_c37_census_constants.py", "data/code/m2_c37_p2.py",
    "data/code/m2_c38_testimony_harvest.py", "data/code/m2_c39_lint_widths.py",
    "data/code/machine2_cycle16_disjointness.py",
}


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m2_corpus_scope

SCOPE = m2_corpus_scope.declare(
    "m2_c41_scope_gate (scan population)",
    entitled="every tracked our-side data/code/*.py file",
    outputs=(),
    sources=())


def tracked():
    out = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True).stdout
    files = [f for f in out.split("\n") if f]
    files = SCOPE.apply(files)
    SCOPE.report()
    return files


def ours_code(files):
    return [f for f in files
            if f.startswith("data/code/") and f.endswith(".py")
            and os.path.basename(f).startswith(("m2_", "machine2"))]


def read(p):
    try:
        return open(os.path.join(REPO, p), encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def selftest(verbose=True):
    ok, n = True, 0

    def chk(name, cond):
        nonlocal ok, n
        n += 1
        if not cond:
            ok = False
            print("  CONTROL FAIL: %s" % name)
        elif verbose:
            print("  ok: %s" % name)

    chk("POS-1 the scan predicate fires on a git ls-files call",
        bool(SCAN_MARK.search('subprocess.run(["git","ls-files"])')))
    chk("POS-2 the scan predicate fires on os.walk", bool(SCAN_MARK.search("for dp,_,fn in os.walk(R):")))
    chk("NEG-1 the scan predicate does not fire on an ordinary open()",
        not SCAN_MARK.search('t = open(path).read()'))
    chk("POS-3 the declaration predicate fires on a real import",
        bool(DECLARES.search("import m2_corpus_scope")))
    chk("NEG-2 the declaration predicate does not fire on the words 'corpus' or 'scope' alone",
        not DECLARES.search("this scan reads the whole corpus within scope"))
    chk("POS-4 this gate is itself in LIVE, so it cannot exempt itself",
        "data/code/m2_c41_scope_gate.py" in LIVE)
    globals()["_N_CONTROLS"] = n
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet-selftest", action="store_true")
    a = ap.parse_args()

    print("=== KNOWN-ANSWER TEST (runs first; fail-closed) ===")
    if not selftest(verbose=not a.quiet_selftest):
        print("REFUSING TO REPORT: a control failed.")
        sys.exit(2)
    print("known-answer test: %d/%d controls PASS\n" % (_N_CONTROLS, _N_CONTROLS))

    files = tracked()
    scans, declared, undeclared = [], [], []
    for f in ours_code(files):
        t = read(f)
        if not SCAN_MARK.search(t):
            continue
        scans.append(f)
        (declared if DECLARES.search(t) else undeclared).append(f)

    print("CORPUS SCANS WE OWN (machine-derived; LOWER BOUND): %d" % len(scans))
    print("  declaring a corpus scope : %d" % len(declared))
    print("  UNDECLARED               : %d" % len(undeclared))
    for f in sorted(declared):
        print("    DECLARED   %s%s" % (f, "   [LIVE]" if f in LIVE else ""))
    for f in sorted(undeclared):
        tag = "   [LIVE]" if f in LIVE else ("   [DEFERRED, reason stated in source]" if f in DEFERRED else "")
        print("    UNDECLARED %s%s" % (f, tag))
    unexplained = [f for f in undeclared if f not in LIVE and f not in DEFERRED]
    if unexplained:
        print("  ⚠ UNDECLARED and NOT deferred -- neither fixed nor explained:")
        for f in sorted(unexplained):
            print("      %s" % f)

    live_undeclared = [f for f in undeclared if f in LIVE]
    missing_live = [f for f in LIVE if f not in scans]
    print("\nLIVE scans (output backs a cited figure): %d; LIVE and UNDECLARED: %d"
          % (len(LIVE), len(live_undeclared)))
    if missing_live:
        print("  ⚠ named LIVE but not detected as a corpus scan (check the name, not the verdict):")
        for f in sorted(missing_live):
            print("    %s" % f)
    if live_undeclared:
        print("GATE RED: a live corpus scan does not declare its scope.")
        sys.exit(2)
    print("GATE GREEN for LIVE scans. %d non-live scans remain undeclared and are listed above as "
          "an open debt, not as a pass." % len([f for f in undeclared if f not in LIVE]))


if __name__ == "__main__":
    main()
