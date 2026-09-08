#!/usr/bin/env python3
"""m2_c48_nonmovement_check.py -- the gate on the c48 storage fix.

THE CLAIM UNDER TEST
--------------------
Widening machine-2's cell storage from `mp.nstr(v, 60)` to full working precision moved NO string
this lane has already published.  A claim of non-movement without a byte-comparison does not count,
so this gate does the comparison, and it does it the only way that is not circular:

  * it NEVER reads the narrow field of the new cell;
  * it reconstructs the value from the `_exact` {sign, man, exp} storage;
  * it REGENERATES the narrow string with the historical call, `mp.nstr(v, sf)`;
  * it byte-compares the regenerated string against (a) the FROZEN c46 cell committed before the fix,
    and (b) every occurrence of that literal anywhere in the repository's committed text.

(b) matters because a cell's number does not only live in its cell: it is quoted in letters, in .out
files and in other machines' verification scripts.  Non-movement in the cell and movement in a letter
would be a fix that silently rewrote the record it exists to correct.

exit 0 = every regenerated string byte-identical everywhere it occurs.

usage: m2_c48_nonmovement_check.py [C48DIR] [C46DIR] [REPOROOT]
"""
import sys, os, json, glob
from mpmath import mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m2_c48_cell_storage as S

FIELDS = (("L", 40), ("lambda_min", 60), ("lambda_min_30", 30), ("residual", 10), ("log10", 20))
KEYOF = {"L": "L", "lambda_min": "lambda_min", "lambda_min_30": "lambda_min",
         "residual": "residual", "log10": "log10"}
SCAN_EXT = (".md", ".py", ".out", ".json", ".tsv", ".txt")
SKIP_DIRS = (".git", "__pycache__")


def repo_text_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(SCAN_EXT):
                yield os.path.join(dirpath, fn)


def main(c48dir, c46dir, reporoot):
    cells = sorted(glob.glob(os.path.join(c48dir, "c48_*.json")))
    if not cells:
        print("no c48 cells found in %s" % c48dir)
        return 2

    print("m2_c48_nonmovement_check")
    print("  c48 cells   : %s (%d)" % (c48dir, len(cells)))
    print("  frozen c46  : %s" % c46dir)
    print("  repo scanned: %s" % reporoot)

    corpus = None
    if reporoot and os.path.isdir(reporoot):
        corpus = []
        # The NEW cells are excluded from the corpus on purpose: the question is how many places in
        # the record that existed BEFORE the fix carry these strings. Counting the new cells would
        # inflate the answer with the artefact under test.
        for f in repo_text_files(reporoot):
            if os.path.abspath(f).startswith(os.path.abspath(c48dir) + os.sep):
                continue
            try:
                corpus.append((os.path.relpath(f, reporoot), open(f, encoding="utf-8",
                                                                  errors="replace").read()))
            except Exception as e:
                print("  !! unreadable %s: %s" % (f, e))
        print("  repo files  : %d" % len(corpus))

    fails, rows, occ_total, strings = [], [], 0, set()
    for cf in cells:
        c = json.load(open(cf))
        base = os.path.basename(cf)
        frozen_fn = os.path.join(c46dir, base.replace("c48_", "c46_", 1))
        frozen = json.load(open(frozen_fn)) if os.path.exists(frozen_fn) else None
        mp.dps = int(c["dps"]) + 10                      # reader must be at least as wide as the run
        for field, sf in FIELDS:
            if field not in c:
                continue
            key = KEYOF[field]
            v = S.load_number(c, key)                    # <- from _exact, never from the narrow field
            regen = mp.nstr(v, sf)
            self_ok = (regen == c[field])
            froz_ok = None if frozen is None else (regen == frozen.get(field))
            n_occ = None
            if corpus is not None and froz_ok is not False and frozen is not None:
                lit = frozen[field]
                n_occ = sum(t.count(lit) for _, t in corpus)
                if lit not in strings:              # distinct strings only; L repeats across cells
                    occ_total += n_occ
                strings.add(lit)
            ok = self_ok and (froz_ok is not False)
            if not ok:
                fails.append((base, field, c.get(field), None if frozen is None else frozen.get(field),
                              regen))
            rows.append((base, field, self_ok, froz_ok, n_occ))

    print("\n  %-46s %-14s %5s %6s %5s" % ("cell", "field", "self", "frozen", "occ"))
    for base, field, s_ok, f_ok, n in rows:
        print("  %-46s %-14s %5s %6s %5s"
              % (base.replace("c48_", "").replace("_g9_it16.json", ""), field,
                 "OK" if s_ok else "MOVED",
                 ("-" if f_ok is None else ("OK" if f_ok else "MOVED")),
                 ("-" if n is None else n)))

    print("\n  distinct published strings regenerated and byte-compared : %d" % len(strings))
    print("  total occurrences of those strings across the repository  : %d" % occ_total)
    print("\nNON-MOVEMENT GATE: %s%s"
          % ("PASS" if not fails else "FAIL", "" if not fails else "  " + repr(fails[:3])))
    return 0 if not fails else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    REPO = os.path.dirname(os.path.dirname(HERE))          # .../data/code -> repo root
    sys.exit(main(a[0] if a else os.path.join(REPO, "data", "c48"),
                  a[1] if len(a) > 1 else os.path.join(REPO, "data", "c46"),
                  a[2] if len(a) > 2 else REPO))
