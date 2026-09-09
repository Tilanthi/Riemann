#!/usr/bin/env python3
"""m2_c56_audit_siblings.py -- SIBLING repairs of two defects m1's L201 found in this cycle's own
SEALED audits (m2_c56_absence_audit.py, m2_c56_locator_audit.py).  The seals and the sealed tools
stand exactly as they are; nothing is edited.

DEFECT A (m1 L201, filed as trap #177).  The C4 live test picked its target with an UNSORTED
`os.listdir` and took the LAST match for "ERRATUM-28".  Two files in the repo match: the ERRATUM
letter (which contains the superseded wording TWICE, by correct marking) and the REPLY note (which
contains it ZERO times).  m1's re-run hit the reply, ours hit the erratum; both printed PASS, on
DIFFERENT FILES.  ⇒ 🔑 A DETECTOR THAT CHOOSES ITS OWN TARGET BY DIRECTORY ORDER IS NOT
REPRODUCIBLE, AND TWO AGREEING GREENS CAN BE ABOUT TWO DIFFERENT OBJECTS.  Repair: enumerate ALL
matches, sorted, and report EVERY ONE with its counts, so the reader sees the population instead of
one arbitrary member.

DEFECT B (m1 L201).  The C3 positive control read `/shared/progress/rh-cycle55.md`, which is
machine-local: from the exchange bytes alone the control is DEAD, so an external verifier cannot
reproduce the "the zero is a measurement" claim.  ⇒ our own standing law -- A PORTABILITY CLAIM CAN
ONLY BE TESTED FROM A CHECKOUT THAT IS NOT YOURS -- turned on us in the same cycle we quoted it.
Repair: plant the control IN-REPO, in a file that ships with the exchange.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PLANT = os.path.join(HERE, "m2_c56_locator_positive_control.md")


def defect_a():
    targets = sorted(f for f in os.listdir(REPO) if "ERRATUM-28" in f)
    rows = []
    for t in targets:
        p = os.path.join(REPO, t)
        def n(pat):
            r = subprocess.run(["grep", "-c", "-F", pat, p], capture_output=True, text=True)
            return int(r.stdout.strip() or 0)
        rows.append(dict(file=t, superseded_wording=n("not quite right"),
                         corrected_wording=n("false under the grader"),
                         a_naive_absence_check_says=("STILL HEDGED (false positive)"
                                                     if n("not quite right") else "repaired")))
    return dict(matches=len(rows), rows=rows,
                finding=("the two matching files give OPPOSITE readings of the same naive check "
                         "(2 hits vs 0 hits). The C4 conclusion is unchanged -- the false positive "
                         "is real and is exhibited by the erratum letter -- but the sealed tool "
                         "reached it by directory order, which is not a method."),
                unchanged=("the audited count 34 and the vulnerable count 0 do not depend on this "
                           "target: they are computed over the declared script corpus, not over "
                           "this file."))


def defect_b():
    """plant an IN-REPO positive control for the C3 locator detector."""
    body = ("# c56 locator-audit POSITIVE CONTROL (planted, in-repo)\n\n"
            "This file exists so that the C3 detector's positive control is reproducible from the\n"
            "EXCHANGE BYTES ALONE. m1's L201 found that our control read a machine-local progress\n"
            "file, so from a foreign checkout it was DEAD and the 'the zero is a measurement'\n"
            "claim could not be checked. The two lines below are QUOTATIONS of windowed-index\n"
            "citations, planted deliberately; the detector must classify both as WINDOWED.\n\n"
            "- 00-LATEST row 18 carried the erratum annotation until the next push trimmed it.\n"
            "- 00-LATEST row 17 carried the INSIDE/OUTSIDE substance.\n")
    with open(PLANT, "w") as fh:
        fh.write(body)
    sys.path.insert(0, HERE)
    import m2_c56_locator_audit as LA
    hits = []
    for i, line in enumerate(open(PLANT).read().splitlines(), 1):
        for m in LA.PAT.finditer(line):
            c = LA.container_of(line)
            if c["kind"] != "ANCHORED":
                hits.append(dict(line_no=i, citation=m.group("hit"), **c))
    return dict(planted_file=os.path.relpath(PLANT, REPO), windowed_hits=len(hits), detail=hits,
                verdict=("FIRES from repo bytes alone -- the C3 zero is a MEASUREMENT"
                         if hits else
                         "DEAD -- the C3 zero is ALGEBRA and the finding does not stand"))


def main():
    out = dict(source="m1 L201 adjudication of c56 stage A",
               defect_A_unsorted_listdir_target=defect_a(),
               defect_B_machine_local_positive_control=defect_b(),
               repair_style="SIBLING -- the sealed audits and their seals are untouched")
    json.dump(out, open(os.path.join(HERE, "m2_c56_audit_siblings.json"), "w"), indent=1)
    a = out["defect_A_unsorted_listdir_target"]
    print("DEFECT A: %d files match ERRATUM-28:" % a["matches"])
    for r in a["rows"]:
        print("   superseded x%d  corrected x%d  -> %-30s %s"
              % (r["superseded_wording"], r["corrected_wording"],
                 r["a_naive_absence_check_says"], r["file"][:64]))
    b = out["defect_B_machine_local_positive_control"]
    print("DEFECT B: planted %s -> %d windowed hits -> %s"
          % (b["planted_file"], b["windowed_hits"], b["verdict"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
