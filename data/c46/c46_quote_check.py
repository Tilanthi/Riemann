#!/usr/bin/env python3
"""c46_quote_check.py -- machine-check every VERBATIM quote c46 makes from Connes arXiv:2602.04022.

A self-read never catches an omission, and an omission falsifies a verbatim claim. So each quote is
checked as a SUBSTRING of a whitespace-normalised pdftotext extraction of the PDF committed in this
repo. The extraction step is part of the claim: pdftotext inserts line breaks (normalised away here)
and occasionally splices a glyph from an adjacent line, so any quote is cut short of such a splice
rather than repaired.

usage: c46_quote_check.py [path/to/2602.04022v1.pdf]
exit 0 = every quote found; exit 1 = at least one quote NOT found (the claim is falsified).
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), "..", "2602.04022v1.pdf")
PDF = os.path.abspath(PDF)

# (label, quote). Each is quoted in data/c46/ artefacts exactly as written here.
QUOTES = [
    ("connes-6.6-remaining-step",
     "In order to apply Theorem 6.1 one needs to show that the smallest eigenvalue of the Weil "
     "quadratic form QWλ is simple with even eigenvector."),
    ("connes-fn12-assumption",
     "one needs to assume that the lowest eigenvalue of the quadratic form is simple and even"),
    ("connes-support-13",
     "the function ψ vanishes outside the interval [1/13, 13] and one does not need to use any "
     "other prime power than 2, 3, 4, 5, 7, 8, 9, 11, 13 to compute Q(φ)"),
]

# NEGATIVE CONTROL: a sentence deliberately altered from a real one. It must NOT be found, or the
# checker is matching loosely and every PASS above is worthless.
NEGATIVE = ("negative-control-altered",
            "In order to apply Theorem 6.1 one needs to show that the smallest eigenvalue of the Weil "
            "quadratic form QWλ is simple with odd eigenvector.")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def main():
    if not os.path.exists(PDF):
        print("MISSING PDF: %s" % PDF)
        return 1
    txt = subprocess.run(["pdftotext", PDF, "-"], capture_output=True, text=True, check=True).stdout
    hay = norm(txt)
    print("source   : %s (%d bytes of PDF)" % (PDF, os.path.getsize(PDF)))
    print("extracted: %d chars, normalised to %d" % (len(txt), len(hay)))
    bad = 0
    for label, q in QUOTES:
        ok = norm(q) in hay
        print("  %-28s %s  (%d chars)" % (label, "FOUND   " if ok else "NOT FOUND", len(q)))
        if not ok:
            bad += 1
    label, q = NEGATIVE
    ok = norm(q) in hay
    print("  %-28s %s  <- must be NOT FOUND" % (label, "FOUND   " if ok else "NOT FOUND"))
    if ok:
        bad += 1
    print("RESULT: %s (%d defect(s))" % ("PASS" if bad == 0 else "FAIL", bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
