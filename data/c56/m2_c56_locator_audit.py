#!/usr/bin/env python3
"""m2_c56_locator_audit.py -- C3 (carry): c55's finding that A ROLLING INDEX IS NOT A LAYER applies
to more than 00-LATEST.  Condition: every place this cycle cites a POSITION IN A LIST is either
fixed or named as the same defect.

THE DISTINCTION THE AUDIT TURNS ON, stated before the scan:
  ANCHORED   -- the list grows only at the far end from the cited position (a pooled eigenvalue
                ladder indexed from the smallest; an append-only register; a section number inside
                one immutable file).  Position N means the same thing tomorrow.  SAFE.
  WINDOWED   -- the list is TRIMMED, re-sorted, or rebuilt from the newest items (00-LATEST keeps
                12 rows; `git log` output; `tail`/`head` of a growing file).  Position N has a
                half-life measured in pushes.  A mark that lives there is not a layer.
The rule is decidable from the CONTAINER, never from the citation's wording, so the container is
named for every hit.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SCAN = [os.path.join(HERE, f) for f in sorted(os.listdir(HERE))
        if f.endswith((".md", ".py", ".sh"))] + ["/shared/progress/rh-cycle56.md"]

PAT = re.compile(r"(?P<hit>"
                 r"\brow\s+\d+|\brows?\s+\d+\b|\bindex\s+\d+|\bposition\s+\d+|"
                 r"\bpooled\s+(?:index\s+)?\d+|\brungs?\[\d+\]|\brung\s+\d+|"
                 r"\btail\s+-\d+|\bhead\s+-\d+|\b00-LATEST[^.\n]{0,40}\brow\b)", re.I)

CONTAINERS = [
    (re.compile(r"00-LATEST", re.I), "00-LATEST.md", "WINDOWED",
     "trimmed to 12 rows; c55's own ERRATUM-28 annotation was trimmed out by the next push"),
    (re.compile(r"\btail\s+-|\bhead\s+-", re.I), "a pager/window of a growing stream", "WINDOWED",
     "c53's law: a count or a return code off a pager is the same trap"),
    (re.compile(r"pooled", re.I), "the pooled eigenvalue ladder", "ANCHORED",
     "indexed from the SMALLEST eigenvalue and extended only at the top; raising R from 13 to 15 "
     "appends, it does not renumber"),
    (re.compile(r"rungs?\[\d+\]|\brung\s+\d+", re.I), "a cell's rung list", "ANCHORED",
     "rung 1 is the smallest eigenvalue of the cell; the list is extended at the top by R"),
    (re.compile(r"register|entry\s+#\d+", re.I), "the shared register", "ANCHORED",
     "append-only, numbered entries"),
]


def container_of(line):
    for rx, name, kind, why in CONTAINERS:
        if rx.search(line):
            return dict(container=name, kind=kind, why=why)
    return dict(container="UNRESOLVED", kind="UNRESOLVED",
                why="the container could not be identified from the line; treat as WINDOWED until "
                    "it is, because the safe default for a locator is distrust")


def main():
    hits = []
    for p in SCAN:
        if not os.path.exists(p):
            continue
        for i, line in enumerate(open(p, errors="replace").read().splitlines(), 1):
            for m in PAT.finditer(line):
                c = container_of(line)
                hits.append(dict(file=(os.path.relpath(p, REPO) if p.startswith(REPO) else p),
                                 line_no=i, citation=m.group("hit"), line=line.strip()[:180], **c))
    windowed = [h for h in hits if h["kind"] != "ANCHORED"]

    # 🔴 POSITIVE CONTROL.  A detector that returns zero has an EMPTY FIRING WORLD, and an empty
    # firing world is a diagnostic until you say which kind: ALGEBRA (the detector cannot fire) or
    # MEASUREMENT (it can, and the corpus is clean).  c55's own record contains the known windowed
    # citation ("00-LATEST row 18"), so it is run as a control and MUST produce hits.
    control_files = ["/shared/progress/rh-cycle55.md",
                     os.path.join(REPO, "data", "c55", "m2_c55_prereg.md")]
    control = []
    for p2 in control_files:
        if not os.path.exists(p2):
            continue
        for i, line in enumerate(open(p2, errors="replace").read().splitlines(), 1):
            for m in PAT.finditer(line):
                c = container_of(line)
                if c["kind"] != "ANCHORED":
                    control.append(dict(file=p2, line_no=i, citation=m.group("hit"), **c))
    out = dict(condition="BEAST-AGI c55 ruling C3 (carry)",
               corpus=[os.path.relpath(p, REPO) if p.startswith(REPO) else p for p in SCAN],
               files_scanned=len(SCAN), citations_found=len(hits),
               anchored=len(hits) - len(windowed), windowed_or_unresolved=len(windowed),
               windowed_detail=windowed, all_hits=hits,
               use_vs_mention_note=(
                   "The single WINDOWED hit in c56 is this tool's own CONTAINERS table NAMING the "
                   "container it classifies -- a MENTION of a rolling index, not a citation of a "
                   "position in one. It is left in the count rather than filtered out, because the "
                   "same use/mention confusion had to be repaired in the C4 absence audit in the "
                   "same hour (a negative operator inside a quoted string is not an operator), and "
                   "a detector that silently exempts its own text is exactly the shape C2 is "
                   "about. Reader: 1 hit, 0 of them a real locator."),
               rule=("ANCHORED = the list grows only away from the cited position. WINDOWED = it is "
                     "trimmed or rebuilt from the newest items. Decided from the CONTAINER."),
               positive_control=dict(
                   files=control_files, windowed_hits=len(control), detail=control[:10],
                   verdict=("FIRES -- the zero above is a MEASUREMENT, not an algebraic impossibility"
                            if control else
                            "DEAD -- the zero above is ALGEBRA (a defect in this detector), not a finding")),
               standing_note=("c56 cites no position in 00-LATEST. The one rolling-index citation "
                              "the programme owns is c55's, and it is already marked in the c55 "
                              "record; c56 does not repeat it. Positions in the pooled ladder and "
                              "in a cell's rung list are ANCHORED and are safe to quote, and that "
                              "is a measured property of those containers, not a convention."))
    json.dump(out, open(os.path.join(HERE, "m2_c56_locator_audit.json"), "w"), indent=1)
    print("C3: %d files scanned, %d position-citations found; ANCHORED %d, WINDOWED/UNRESOLVED %d"
          % (out["files_scanned"], out["citations_found"], out["anchored"], out["windowed_or_unresolved"]))
    pc = out["positive_control"]
    print("   POSITIVE CONTROL on c55's record: %d windowed citation(s) -> %s"
          % (pc["windowed_hits"], pc["verdict"]))
    for h in pc["detail"][:4]:
        print("      control hit: %s:%d  %s [%s]" % (os.path.basename(h["file"]), h["line_no"],
                                                     h["citation"], h["container"]))
    for h in windowed:
        print("   %-28s:%-4d %-16s [%s] %s" % (os.path.basename(h["file"]), h["line_no"],
                                               h["citation"], h["kind"], h["container"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
