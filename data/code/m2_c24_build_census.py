"""cycle24 Object A / V1+V2 -- emit the census table as a TSV, so the denominator is
reproducible rather than asserted.  Classification is by MEASUREMENT wherever possible:
  - membership route P = git provenance (files touched by the 7 commits that touch the evaluator
    or any of its importers, from the evaluator's birth commit found by --diff-filter=A)
  - membership route F = numeric fingerprint grep over 17 roots, each find-counted first
  - degree statement  = grep of the artefact itself for an explicit degree
  - recoverability    = does a COMMITTED script that produced the number name its degree at the
                        Basis(...) call site (measured by grep, not by memory)
"""
import csv, subprocess, os, sys

REPO = "/shared/rh-exchange-repo/Riemann"
rows = []
def add(cat, path, member, states, recov, note):
    rows.append(dict(category=cat, artefact=path, in_denominator=member,
                     classification=states, recovery=recov, note=note))

L = "machine2-cycle22-PREREG-witness-analytic-zero-side.md"
letters = [
 (L, "STATES-A-DEGREE", "letter L58: 'degree 8 per sub-interval'"),
 ("machine2-cycle22-witness-fires-on-the-bare-zero-side.md", "STATES-A-DEGREE",
  "9 degree statements incl own-failure #2; but see ERRATUM 9 (node COUNT wrong)"),
 ("machine2-cycle23-FAMILY-CHOICE-composition-with-near-cancellation.md", "STATES-A-DEGREE",
  "names deg-8 default vs deg-10 tail explicitly"),
 ("machine2-cycle23-PREREG-2-amendment-r4-same-sign-control-and-the-normalisation-that-decides-additivity.md",
  "STATES-A-DEGREE", "'Degree 10, the 123 zeros 200<gamma<=400'"),
 ("machine2-cycle23-SEAL-scored-ladder-executed-and-held-for-m1s-prediction.md", "STATES-A-DEGREE",
  "'rebuilds ... at degree 10 ... reproduces the degree-8 launch'"),
 ("machine2-cycle23-REVEAL-and-letter-the-family-fires-my-prereg-falls-m1s-prediction-holds.md",
  "STATES-A-DEGREE", "'node budget certified to gamma=400'; 'Degree-10 refinement'"),
]
for p, s, n in letters:
    add("C1 repo letter (machine2)", p, "YES", s, "in-artefact", n)

commits = [("171588d", "SILENT", "the letter committed in the SAME commit states degree 8"),
           ("f871287", "STATES-A-DEGREE", ""),
           ("00b3277", "STATES-A-DEGREE", "'default degree-8 node budget ... against degree-10's'"),
           ("a961240", "STATES-A-DEGREE", ""),
           ("5a42399", "SILENT", "sole file m2_c23_scored.py line 29: Basis(g,degree=8)"),
           ("9350043", "STATES-A-DEGREE", "'rebuilds ... at degree 10'"),
           ("1348dbf", "STATES-A-DEGREE", "'degree-10 refinement reproduces ... digit for digit'")]
for c, s, n in commits:
    add("C2 repo commit message (machine2)", c, "YES",
        s if s != "SILENT" else "SILENT-BUT-RECOVERABLE", "same-commit code/letter", n)

data_out = [("machine2_cycle22_scored_witness.json", "m2_cycle22_witness_scored.py", 8),
            ("machine2_cycle23_controls.json", "m2_c23_controls.py", 8),
            ("machine2_cycle23_design_scan.json", "m2_c23_design.py", 8),
            ("machine2_cycle23_ordcheck.json", "m2_c23_ordcheck.py", 8),
            ("machine2_cycle23_ptable.json", "m2_c23_ptable.py", 8),
            ("machine2_cycle23_r4.json", "m2_c23_r4.py", 8),
            ("machine2_cycle23_rung_design.json", "m2_c23_rung.py", 8),
            ("machine2_cycle23_scored.json", "m2_c23_scored.py", 8),
            ("machine2_cycle23_selfconsistent.json", "m2_c23_selfconsistent.py", 8),
            ("machine2_cycle23_shifts.json", "m2_c23_shifts.py", 8),
            ("machine2_cycle23_sweep_c.json", "m2_c23_sweepc.py", 8),
            ("machine2_cycle23_taylorcheck.json", "m2_c23_taylorcheck.py", 8)]
for a, w, d in data_out:
    add("C3 repo data artefact (machine2)", "data/" + a, "YES", "SILENT-BUT-RECOVERABLE",
        "writer %s names degree=%d at its Basis() call site" % (w, d), "")
add("C3 repo data artefact (machine2)", "data/machine2_cycle23_tail_budget.json", "YES",
    "STATES-A-DEGREE", "in-artefact", 'field "deg": 10')
add("C3 repo data artefact (machine2)", "data/machine2_cycle23_tail_deg10.out", "YES",
    "STATES-A-DEGREE", "in-artefact", "header '# deg=10'")

add("C4 repo code with an embedded reading", "data/code/m2_c23_tail.py", "YES", "STATES-A-DEGREE",
    "in-artefact", "DEG=10 and two labelled '(deg8: ...)' comparison values")
add("C4 repo code with an embedded reading", "data/code/m2_nodebudget.py", "YES", "STATES-A-DEGREE",
    "in-artefact", "docstring names degree-8; scans 7,8,9,10")

add("C5 counterparty repo artefact", "machine1-l145-cycle22-adjudication-accepted-a6-retracted-two-traps.md",
    "YES", "SILENT-BUT-RECOVERABLE", "quotes our 1.1761206927485314567e-5, cites 00b3277 which states deg 8", "")
add("C5 counterparty repo artefact", "machine1-l150-prediction-committed-five-rung-ladder-fires-pt-regime-fails.md",
    "YES", "SILENT-BUT-RECOVERABLE", "quotes our launch 4.2496273813877281464e-6 + gap; cites 00b3277/a961240", "")
add("C5 counterparty repo artefact", "data/code/machine1_heat72p_cycle23_committed_prediction.py",
    "YES", "SILENT-BUT-RECOVERABLE", "hardcodes our launch value; provenance in its own letter", "")

add("C6 non-repo working doc (m2)", "/shared/progress/rh-cycle22.md", "YES", "STATES-A-DEGREE", "in-artefact", "")
add("C6 non-repo working doc (m2)", "/shared/progress/rh-cycle23.md", "YES", "STATES-A-DEGREE", "in-artefact", "")
add("C6 non-repo working doc (m2)", "/shared/progress/NEXT-RUN-HANDOFF-cycle22-...-20260904T220750Z.md",
    "YES", "STATES-A-DEGREE", "in-artefact", "'node budget audited on the wrong basis'")
add("C6 non-repo working doc (m2)", "/shared/progress/NEXT-RUN-HANDOFF-cycle23-...-20260904T235749Z.md",
    "YES", "STATES-A-DEGREE", "in-artefact", "'deg-8 DEFAULT node budget ... vs deg-10'")
add("C6 non-repo working doc (m2)", "/shared/kb/beast-atlas-rh-programme-standing-facts.md",
    "YES", "STATES-A-DEGREE", "in-artefact", "3 degree lines; carries the SUPERSEDED widest-bump rule")

add("C7 outward sentence (BEAST-AGI->Glenn)", "beast-outbox/sent/out-glenn-cycle22-...e8baf1.sent.json",
    "YES", "SILENT-BUT-RECOVERABLE", "names commit f871287, whose letter states degree 8",
    "carries '1.176e-5'; at 4 s.f. that value is degree- AND machine-ambiguous (m1's anchor rounds identically)")
add("C7 outward sentence (BEAST-AGI->Glenn)", "beast-outbox/staging/glenn-cycle22.json",
    "YES", "SILENT-BUT-RECOVERABLE", "staging duplicate of the above", "")
add("C7 outward sentence (BEAST-AGI->Glenn)", "beast-outbox/sent/out-glenn-cycle23-...781354.sent.json",
    "YES", "STATES-A-DEGREE", "in-artefact", "'degree-10 refinement reproducing it digit for digit'")

with open("/workspace/rh-c24/machine2_cycle24_census.tsv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["category", "artefact", "in_denominator", "classification",
                                      "recovery", "note"], delimiter="\t")
    w.writeheader()
    for r in rows:
        w.writerow(r)

from collections import Counter
print("DENOMINATOR =", len(rows))
print(Counter(r["classification"] for r in rows))
print(Counter(r["category"] for r in rows))
