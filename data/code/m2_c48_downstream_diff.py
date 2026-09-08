#!/usr/bin/env python3
"""m2_c48_downstream_diff.py -- does the storage fix move anything DOWNSTREAM?

A cell's number does not stop at the cell. `c46_analyse.py` builds the published parity table out of
the 60-s.f. `lambda_min` literals, and its output `c46_analyse.out` is committed. If widening the
storage changes any number that script prints, the fix has moved a published string in the one place
a per-cell byte-comparison cannot see.

METHOD -- and the point is that the INSTRUMENT IS NOT TOUCHED. `c46_analyse.py` is run twice,
unmodified, byte-for-byte as committed. Only its INPUT DIRECTORY changes:

  run A : the frozen c46 cells, exactly as committed        -> must reproduce c46_analyse.out
  run B : the same cells with `lambda_min` replaced by the full working-precision string from the
          c48 storage (every other field untouched, and cells with no c48 counterpart left frozen)

diff(A, B) is the downstream movement. diff(A, committed .out) is the control: if run A does not
reproduce the committed output, the comparison is meaningless and the script says so first.

usage: m2_c48_downstream_diff.py [C48DIR] [C46DIR] [WORK]
"""
import sys, os, json, glob, shutil, subprocess, difflib, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mpmath import mp
import m2_c48_cell_storage as S


def stage(src_c46, dst, c48dir=None):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src_c46, dst, ignore=shutil.ignore_patterns("__pycache__"))
    swapped = []
    if c48dir:
        for cf in sorted(glob.glob(os.path.join(c48dir, "c48_*.json"))):
            c = json.load(open(cf))
            tgt = os.path.join(dst, os.path.basename(cf).replace("c48_", "c46_", 1))
            if not os.path.exists(tgt):
                continue
            d = json.load(open(tgt))
            mp.dps = int(c["dps"]) + 10
            v = S.load_number(c, "lambda_min")            # from _exact, never the narrow field
            assert mp.nstr(v, 60) == d["lambda_min"], "staged cell would move a published string"
            d["lambda_min"] = c["lambda_min_full"]        # <-- the ONLY change
            json.dump(d, open(tgt, "w"), indent=1)
            swapped.append(os.path.basename(tgt))
    return swapped


def run(d):
    p = subprocess.run([sys.executable, os.path.join(d, "c46_analyse.py")],
                       capture_output=True, text=True, cwd=d)
    return p.stdout


def main(c48dir, c46dir, work):
    os.makedirs(work, exist_ok=True)
    A, B = os.path.join(work, "runA_frozen"), os.path.join(work, "runB_fullprec")
    stage(c46dir, A)
    swapped = stage(c46dir, B, c48dir)
    outA, outB = run(A), run(B)

    committed = os.path.join(c46dir, "c46_analyse.out")
    ctrl = "NO COMMITTED .out"
    if os.path.exists(committed):
        txt = open(committed).read()
        dl = list(difflib.unified_diff(txt.splitlines(), outA.splitlines(),
                                       "committed", "runA", lineterm="", n=0))
        body = [l for l in dl if l[:1] in "+-" and not l.startswith(("+++", "---"))]
        removed = [l for l in body if l.startswith("-")]
        if txt.strip() == outA.strip():
            ctrl = "REPRODUCES"
        elif not removed:
            # Pure insertion: every committed line survives byte-identically and the run has EXTRA
            # rows. That is not a failed control, it is a STALE committed output -- the cell set grew
            # after the .out was written. Reported as its own verdict, not folded into either bucket.
            ctrl = "REPRODUCES-EVERY-COMMITTED-LINE (committed .out is STALE: %d rows added since)" \
                   % len([l for l in body if l.startswith("+")])
        else:
            ctrl = "DIFFERS -- %d committed lines changed or lost" % len(removed)
            print("CONTROL FAILED -- run A does not reproduce the committed output")
            print("\n".join(dl[:40]))
    print("control (frozen cells vs committed c46_analyse.out) : %s" % ctrl)
    print("cells staged with full-precision lambda_min          : %d %s" % (len(swapped), swapped))

    d = list(difflib.unified_diff(outA.splitlines(), outB.splitlines(),
                                  "frozen-60sf", "full-precision", lineterm="", n=0))
    if not d:
        print("\nDOWNSTREAM MOVEMENT: NONE -- c46_analyse.py prints byte-identical output from")
        print("60-s.f. and from full-precision inputs. No published derived number moves.")
    else:
        print("\nDOWNSTREAM MOVEMENT: %d diff lines" % len(d))
        print("\n".join(d))
    open(os.path.join(work, "downstream_diff.txt"), "w").write("\n".join(d) or "(no differences)\n")
    return 0 if not ctrl.startswith("DIFFERS") else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    REPO = os.path.dirname(os.path.dirname(HERE))
    # the work dir is a temp dir OUTSIDE the repository on purpose: this script copies cells and
    # rewrites one field in the copies, and a staging tree must never be able to land in the repo.
    sys.exit(main(a[0] if a else os.path.join(REPO, "data", "c48"),
                  a[1] if len(a) > 1 else os.path.join(REPO, "data", "c46"),
                  a[2] if len(a) > 2 else tempfile.mkdtemp(prefix="m2_c48_downstream_")))
