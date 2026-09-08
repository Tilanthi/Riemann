#!/usr/bin/env python3
"""m2_c49_gate_census.py -- does the c49 precision gate have a firing world outside the cells it
was written against?  (prereg s3, P2a / P2b)

A gate is only a measurement if it can come out either way on data it did not see.  This runs
`m2_c49_precision.gate_cell` over EVERY machine-2 cell artefact in the c48 storage census (95 of
them, the same denominator m1-L190 s1 recounted exactly) and reports two numbers, because the raw
one overstates:

  P2a  artefacts with >=1 FAIL of any kind.   Includes `/dps` and `/*_exact/prec`, which are
       CONFIGURATION KNOBS that were never claimed as accuracies.  A gate that fails on those is
       describing the corpus, not discriminating within it, and I registered that in advance.
  P2b  artefacts with a FAIL after excluding those two knob paths -- the count of artefacts that
       could actually hand a reader a number the object may not support.

usage: m2_c49_gate_census.py [--tsv OUT]
"""
import os
import re
import sys
import json
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/shared/rh-exchange-repo/Riemann"
CENSUS = os.path.join(REPO, "data", "c48", "m2_c48_storage_census.tsv")

sys.path.insert(0, HERE)
import m2_c49_precision as P  # noqa: E402

# the two pure-configuration paths, excluded for P2b and named here so the exclusion is auditable
KNOB_PATHS = re.compile(r"(^/dps$|/prec$|^/iters$|^/gl_degree$)")


def main():
    files = []
    with open(CENSUS) as fh:
        next(fh)
        for line in fh:
            f = line.split("\t")[0]
            if f not in files:
                files.append(f)

    rows, raw_fail, disc_fail = [], 0, 0
    path_counts = collections.Counter()
    disc_paths = collections.Counter()
    missing = []
    for rel in files:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            missing.append(rel)
            continue
        cell = json.load(open(p))
        findings, stats = P.gate_cell(cell)
        fails = [f for f in findings if f[0] == "FAIL"]
        d = [f for f in fails if not KNOB_PATHS.search(f[1])]
        for f in fails:
            path_counts[f[1]] += 1
        for f in d:
            disc_paths[f[1]] += 1
        if fails:
            raw_fail += 1
        if d:
            disc_fail += 1
        rows.append((rel, len(fails), len(d), ";".join(sorted(set(f[1] for f in d)))))

    n = len(rows)
    print("m2_c49_gate_census -- the c49 precision gate over the c48 census denominator\n")
    print("  artefacts in census file      : %d" % len(files))
    print("  artefacts read (exist on disk): %d%s"
          % (n, "" if not missing else "   MISSING: %s" % missing))
    print("  P2a  >=1 FAIL of any kind     : %d of %d" % (raw_fail, n))
    print("  P2b  >=1 FAIL excluding knobs : %d of %d" % (disc_fail, n))
    print("\n  most common failing paths (raw):")
    for pth, c in path_counts.most_common(8):
        print("      %-38s %4d" % (pth, c))
    print("\n  most common failing paths (discriminating):")
    if not disc_paths:
        print("      (none)")
    for pth, c in disc_paths.most_common(8):
        print("      %-38s %4d" % (pth, c))

    print("\nSCORING (prereg s3)")
    print("  P2a >= 90 of 95 fail, top path is /dps : %s"
          % ("HELD" if raw_fail >= 90 and path_counts.most_common(1)[0][0] == "/dps"
             else "FAILED (raw_fail=%d top=%s)"
                  % (raw_fail, path_counts.most_common(1)[0][0] if path_counts else None)))
    if disc_fail == 0:
        verdict = ("EMPTY FIRING WORLD -- and by the standing law I must say which kind: this is "
                   "ALGEBRA (the gate restates the c48 cell shape), not MEASUREMENT. Any claim "
                   "that it generalises is WITHDRAWN.")
    elif disc_fail <= 20:
        verdict = "HELD (<=20): the defect is c48-local, and the gate does fire outside its author."
    else:
        verdict = ("FAILED UP (>20): the misreadable-number defect is CORPUS-WIDE, not c48-local. "
                   "This enlarges the row rather than closing it.")
    print("  P2b <= 20 discriminating fails         : %d -> %s" % (disc_fail, verdict))

    if "--tsv" in sys.argv:
        out = sys.argv[sys.argv.index("--tsv") + 1]
        with open(out, "w") as fh:
            fh.write("file\tfails_raw\tfails_discriminating\tdiscriminating_paths\n")
            for r in sorted(rows, key=lambda r: (-r[2], r[0])):
                fh.write("%s\t%d\t%d\t%s\n" % r)
        print("\nwrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
