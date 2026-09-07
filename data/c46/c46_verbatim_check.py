#!/usr/bin/env python3
"""c46_verbatim_check.py -- machine-check every REPO-INTERNAL verbatim quote c46 makes.

c46_quote_check.py does the same job for the external source (Connes' PDF). This one covers the
quotations c46 takes from artefacts inside this repository -- our own c45 prereg and the c42 README.
An omission or a silently normalised quotation mark falsifies a verbatim claim, and a self-read never
catches either; only a substring check against the file does.

Whitespace is normalised (the quotes are line-wrapped differently in the quoting artefact than in the
source), NOTHING ELSE is: quotation marks, capitalisation and punctuation must match exactly.

exit 0 = every quote found and every negative control absent.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

QUOTES = [
    ("c45-S1-equivalence-sentence", "data/c45/c45_attackC_prereg.md",
     'The limit of lambda_min(x) as x grows is the infimum of the Weil form on the whole space, so '
     '**"lambda_min(x) > 0 for every x" is equivalent to Weil positivity, i.e. to RH itself.**'),
    ("c42-convention-basis-line", "data/c42/c42_connes_x.py",
     "basis      : phi_0 = 1/sqrt(L); phi_k = sqrt(2/L) cos(w_k t), w_k = 2 pi k / L, k=1..N"),
    ("c42-README-parity-restriction", "data/c42/README.md",
     "it does not fix the inner product, the parity restriction, or the recentring"),
    ("c42-convention-minimise-line", "data/c42/c42_connes_x.py",
     "minimise   : min over ||f||_{L2(dt)} = 1  ->  smallest eigenpair of the (N+1)x(N+1) matrix M"),
]

# must NOT be found: the same S1 sentence with the quantifier already repaired. If this matched, the
# source would have been edited and the erratum would be describing a file that no longer says it.
NEGATIVE = [
    ("negative-S1-already-repaired", "data/c45/c45_attackC_prereg.md",
     'is equivalent to Weil positivity on both blocks'),
]


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    bad = 0
    for label, rel, q in QUOTES:
        path = os.path.join(REPO, rel)
        hay = norm(open(path, encoding="utf-8", errors="replace").read())
        ok = norm(q) in hay
        print("  %-32s %-38s %s  (%d chars)" % (label, rel, "FOUND    " if ok else "NOT FOUND", len(q)))
        bad += 0 if ok else 1
    for label, rel, q in NEGATIVE:
        path = os.path.join(REPO, rel)
        hay = norm(open(path, encoding="utf-8", errors="replace").read())
        ok = norm(q) in hay
        print("  %-32s %-38s %s  <- must be NOT FOUND" % (label, rel, "FOUND    " if ok else "NOT FOUND"))
        bad += 1 if ok else 0
    print("RESULT: %s (%d defect(s))" % ("PASS" if bad == 0 else "FAIL", bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
