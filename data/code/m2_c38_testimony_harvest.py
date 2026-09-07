"""CYCLE 38, ruling section 7: HARVEST m1's and m3's OWN LETTERS for testimony about the width at
which WE published a constant.  Testimony from the party our print width bound beats our recollection
(a recalled value is never admissible) and beats re-running a producing script (which measures TODAY's
script, not the publication-time state).

CLASSES ARE FIXED HERE, BEFORE ANY EXTRACTION IS READ (c37's law: classes assigned before counting):
  BIND   -- the other party records OUR print width as the limit on what they could check
  ADEQ   -- the other party records our printed digits as sufficient / exact / reproduced in full
  OVER   -- the other party records our print as WIDER than our accuracy (the opposite defect)
  SELF   -- the width discussed is the other party's own, not ours          [not testimony about us]
  OTHER  -- matched the pattern, carries no width claim about our publication [not testimony]

DETECTOR SCOPE, declared: this is a LINE-level regex over committed text of files NOT authored by
machine 2 (a file list is a detector excerpt -- so the denominators of files scanned and lines
matched are both printed, and every accepted row is quoted verbatim with file:line).
"""
import os, re, subprocess, sys

R = "/shared/rh-exchange-repo/Riemann"
os.chdir(R)
files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()
ours = re.compile(r"^(machine2-|data/(code/)?(m2_|machine2_))")
skip = re.compile(r"\.(png|pdf|json|sha256)$")
cand = [f for f in files if not ours.match(f) and not skip.search(f)]

WIDTH = re.compile(r"(\d{1,3})[- ]?(?:\w+[- ])?(s\.f\.|significant figures?|digits?|figures?|dps)", re.I)
THEM  = re.compile(r"\b(their|theirs|m2's|m2 |BEAST's|BEAST |machine ?2'?s?|the ladder value)", re.I)
PRINT = re.compile(r"print|publish|quote|literal|string|census|stated|carried", re.I)

rows = []
scanned = 0
for f in cand:
    try:
        txt = open(f, errors="replace").read()
    except Exception:
        continue
    scanned += 1
    for i, ln in enumerate(txt.splitlines(), 1):
        if len(ln) > 1200:
            continue
        if WIDTH.search(ln) and THEM.search(ln) and PRINT.search(ln):
            rows.append((f, i, ln.strip()))

print("files in repo: %d   files not authored by m2 and scanned: %d   candidate lines: %d"
      % (len(files), scanned, len(rows)))
with open("/workspace/rh/cycle38/c38_testimony_raw_v2.tsv", "w") as out:
    out.write("file\tline\ttext\n")
    for f, i, ln in rows:
        out.write("%s\t%d\t%s\n" % (f, i, ln.replace("\t", " ")))
for f, i, ln in rows:
    print("%s:%d\t%s" % (f, i, ln[:300]))
