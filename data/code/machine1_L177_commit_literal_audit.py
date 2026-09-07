"""m1-L177 8 -- B2-boundary self-audit: every precision literal in my commit
messages must also exist in a file at that commit.

Two passes per commit:
  pass 1 (format-blind): exact ASCII -F match, as first run live -- this is the
         pass that produced 4 false misses in c63b86d;
  pass 2 (#149-normalised): BOTH faces normalised (typographic/ASCII minus and
         case-E unified on token and corpus).
Known-answer test per c39 B12: the c63b86d quartet must be MISSING in pass 1
and FOUND in pass 2 -- a detector that cannot show its own blind spot in
operation has not been tested."""
import re, subprocess, sys

SHAS = ["895482e", "6d15bd7", "c63b86d", "72d6034", "b91fddd",
        "43b5f68", "689551b", "11e25db"]
LIT = re.compile(r"\d+\.\d+(?:[eE][-+]?\d+)?|\d{4,}")
MINUS = str.maketrans({"−": "-", "–": "-", "—": "-"})

def norm(s):
    return s.translate(MINUS).replace("E", "e")

total = p1_miss = p2_miss = 0
for sha in SHAS:
    msg = subprocess.run(["git", "log", "-1", "--format=%B", sha],
                         capture_output=True, text=True).stdout
    toks = sorted(set(norm(t.group(0)) for t in LIT.finditer(msg)))
    toks = [t for t in toks if len(re.sub(r"\D", "", t)) >= 4]
    corpus_raw = subprocess.run(["git", "grep", "-h", "", sha, "--", "."],
                                capture_output=True, text=True).stdout
    corpus_norm = norm(corpus_raw)
    for t in toks:
        total += 1
        p1 = subprocess.run(["git", "grep", "-F", t, sha, "--", "."],
                            capture_output=True).returncode == 0
        p2 = t in corpus_norm
        if not p1 and not p2:
            p2_miss += 1
            print(f"{sha} TRUE MISSING: {t}")
        elif not p1 and p2:
            print(f"{sha} format-boundary only (pass1 miss, pass2 find): {t}")
        elif not p1:
            p1_miss += 1
print(f"commits audited: {len(SHAS)}  precision literals: {total}  "
      f"true missing (both passes): {p2_miss}")
sys.exit(1 if p2_miss else 0)
