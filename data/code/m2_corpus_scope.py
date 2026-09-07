#!/usr/bin/env python3
"""machine2 -- CORPUS SCOPE DECLARATION.  Shared by every corpus scan we own.

THE RULE IT IMPLEMENTS (BEAST-AGI, c41 ruling + sequencing addendum)
  A measuring artefact left inside the corpus it measures is a CIRCULAR CARRIER: the instrument
  reads its own output back as evidence, and the number it invents can be a FORMAT WIDTH rather than
  a measurement (c40's `print(f"dps={dps:4d}")` read as a precision of 4).
  =>  Every corpus scan must DECLARE what it is entitled to read, EXCLUDE its own output paths, and
      PRINT the excluded count on every run.  A silent exclusion is a second way to look at nothing
      and feel fine.
  The addendum's ordering is the reason this module exists at all and is imported FIRST: the
  circular carrier and the synthetic literal are the same defect -- AN UNDECLARED CORPUS SCOPE --
  and a marker convention applied inside an unbounded corpus is marking literals in a set nobody has
  drawn.  Declare the corpus, THEN mark what survives.

WHY A PRINTED ZERO IS NOT THE SAME AS SILENCE
  On a scan's first run its own output is not yet committed, so the honest excluded count is 0.
  0 is ALSO what a broken exclusion prints.  This module therefore always prints the declaration
  (how many paths were declared) beside the count (how many were actually present and removed), so
  the two failure modes are distinguishable from the transcript alone.

WHAT IT DELIBERATELY DOES NOT DO
  It does not infer a scan's outputs from file extension, from a name-stem resemblance, or from
  anything else.  Outputs are DECLARED by the scan, by hand, in one place.  An inferred exclusion is
  a second detector, and an undeclared detector is the thing this whole cycle exists to remove.
"""
import os, sys

__all__ = ["Scope", "declare"]


class Scope:
    """A declared corpus scope.

    entitled  -- one-line prose: what this scan is entitled to read.  Printed, not enforced; it is
                 the human-readable half and its job is to be falsifiable by reading the code.
    outputs   -- tuple of repo-relative paths this scan WRITES.  Enforced: removed from every file
                 list passed through .apply().
    sources   -- tuple of repo-relative paths that are this scan's OWN SOURCE CODE.
                 🔴 A SECOND SPECIES OF CIRCULAR CARRIER, found in c41 and not in the ruling:
                 a pattern-matching census's own source contains EVERY PATTERN IT SEARCHES FOR, by
                 construction.  Left in the corpus it inflates every "how often is this mentioned"
                 statistic by exactly one per key, always, and it does so silently because the file
                 looks like an ordinary artefact.  Measured instance: machine2_cycle20_disjointness
                 re-run today lists data/code/machine2_cycle20_disjointness.py as a carrier mention
                 for 6 of its 10 keys.  Declared and excluded separately from outputs, because the
                 two have different fixes: an output can be moved out of the tree, a source cannot.
    also_excl -- tuple of repo-relative paths excluded for a stated reason other than self-output
                 (e.g. a sibling instrument's output).  Printed separately so the two reasons never
                 merge into one number.
    """

    def __init__(self, scan, entitled, outputs=(), also_excl=(), reason="", sources=()):
        self.scan = scan
        self.entitled = entitled
        self.sources = tuple(sources)
        self.outputs = tuple(outputs)
        self.also_excl = tuple(also_excl)
        self.reason = reason
        self.n_removed_self = None
        self.n_removed_other = None

    def apply(self, files):
        """Remove declared paths from `files`.  Returns the filtered list and records the counts."""
        so, ao, sc = set(self.outputs), set(self.also_excl), set(self.sources)
        keep, rs, ro, rc = [], [], [], []
        for f in files:
            if f in so:
                rs.append(f)
            elif f in sc:
                rc.append(f)
            elif f in ao:
                ro.append(f)
            else:
                keep.append(f)
        self.n_removed_self, self.n_removed_other = len(rs), len(ro)
        self.n_removed_source = len(rc)
        self._removed_self, self._removed_other, self._removed_source = rs, ro, rc
        return keep

    def report(self, stream=sys.stdout):
        if self.n_removed_self is None:
            raise RuntimeError("Scope.report() called before Scope.apply(): the count would be a "
                               "claim rather than a measurement.")
        p = stream.write
        p("=== DECLARED CORPUS SCOPE (%s) ===\n" % self.scan)
        p("  entitled to read : %s\n" % self.entitled)
        p("  self-outputs DECLARED %d | PRESENT AND EXCLUDED %d\n"
          % (len(self.outputs), self.n_removed_self))
        for f in self._removed_self:
            p("      excluded (own output): %s\n" % f)
        if len(self.outputs) and self.n_removed_self == 0:
            p("      note: 0 excluded. Correct before this scan's output is committed, and also what\n"
              "            a broken exclusion prints. Both possibilities are live; the declaration\n"
              "            count above is what distinguishes them.\n")
        if self.sources:
            p("  own SOURCE declared %d | PRESENT AND EXCLUDED %d  (a search program contains "
              "every term it searches for)\n" % (len(self.sources), self.n_removed_source))
            for f in self._removed_source:
                p("      excluded (own source): %s\n" % f)
        if self.also_excl:
            p("  other exclusions DECLARED %d | PRESENT AND EXCLUDED %d  reason: %s\n"
              % (len(self.also_excl), self.n_removed_other, self.reason or "(none given)"))
            for f in self._removed_other:
                p("      excluded (declared): %s\n" % f)
        p("\n")


def declare(scan, entitled, outputs=(), also_excl=(), reason="", sources=()):
    return Scope(scan, entitled, outputs, also_excl, reason, sources)


# --- known-answer test -------------------------------------------------------------
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

    s = declare("t", "everything", outputs=("data/o.json",))
    keep = s.apply(["a.md", "data/o.json", "data/b.out"])
    chk("POS-1 a declared output present in the list is removed", keep == ["a.md", "data/b.out"])
    chk("POS-2 the removal is COUNTED, not assumed", s.n_removed_self == 1)

    s2 = declare("t2", "everything", outputs=("data/not_here.json",))
    keep2 = s2.apply(["a.md"])
    chk("NEG-1 a declared output that is absent removes nothing", keep2 == ["a.md"])
    chk("NEG-2 an absent declaration counts 0, and 0 is reported as 0", s2.n_removed_self == 0)

    s3 = declare("t3", "everything")
    try:
        s3.report()
        chk("POS-3 report() before apply() must raise", False)
    except RuntimeError:
        chk("POS-3 report() before apply() raises rather than printing an uncounted number", True)

    s4 = declare("t4", "e", outputs=("data/x.out",), also_excl=("data/y.out",), reason="sibling")
    k4 = s4.apply(["data/x.out", "data/y.out", "data/z.out"])
    chk("POS-4 self-output and other-exclusion are counted SEPARATELY",
        k4 == ["data/z.out"] and s4.n_removed_self == 1 and s4.n_removed_other == 1)

    s5 = declare("t5", "e", outputs=("data/x.out",))
    k5 = s5.apply(["data/x.out.bak", "data/xx.out"])
    chk("NEG-3 exclusion is EXACT-PATH, never a prefix or a stem resemblance",
        k5 == ["data/x.out.bak", "data/xx.out"] and s5.n_removed_self == 0)

    s6 = declare("t6", "e", sources=("data/code/t6.py",))
    k6 = s6.apply(["data/code/t6.py", "data/a.out"])
    chk("POS-5 a declared OWN SOURCE is removed and counted separately from outputs",
        k6 == ["data/a.out"] and s6.n_removed_source == 1 and s6.n_removed_self == 0)

    s7 = declare("t7", "e", outputs=("data/code/t7.py",), sources=("data/code/t7.py",))
    k7 = s7.apply(["data/code/t7.py"])
    chk("NEG-4 a path declared as BOTH output and source is removed ONCE, counted as output",
        k7 == [] and s7.n_removed_self == 1 and s7.n_removed_source == 0)

    globals()["_N_CONTROLS"] = n
    return ok


if __name__ == "__main__":
    print("=== m2_corpus_scope known-answer test ===")
    okk = selftest()
    print("%d/%d controls %s" % (_N_CONTROLS, _N_CONTROLS, "PASS" if okk else "FAIL"))
    sys.exit(0 if okk else 2)
