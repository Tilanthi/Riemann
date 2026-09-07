#!/usr/bin/env python3
"""
machine2 cycle 39 -- SERIALISATION BOUNDARY CENSUS.

BEAST-AGI's c38 ruling section 1: "Stop chasing instances. ENUMERATE THE BOUNDARIES ... and state a
width discipline for each, with the COUNT OF BOUNDARIES as the denominator."

This script measures the population of each enumerated boundary and how many of its objects carry a
high-significant-figure decimal literal.  It does NOT decide the width discipline (that is judgement,
and lives in machine2-c39-serialisation-boundary-register.md); it supplies the denominators so the
register is measured rather than recollected.

Declared scope and limits, up front:
  * A boundary is enumerated here only if we can NAME it.  The count is a LOWER BOUND on the number of
    serialisation surfaces, not a measurement of it -- the c38 finding was precisely that each cycle
    found a layer nobody had listed.
  * "carries a wide literal" is a DETECTOR, and a regex is a detector excerpt (c38).  Its known-answer
    test is m2_c39_boundary_census_selftest() below: it must catch a hand-typed 45 s.f. literal and a
    30 s.f. JSON string, and must not count a date, a commit sha or a version number.
  * Significant figures are counted as: mantissa digits after stripping the sign, the decimal point and
    LEADING zeros.  Trailing zeros are counted -- they are exactly the claim at issue.
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NUM = re.compile(r"(?<![\w.])[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?(?![\w.])")


def sigfigs(tok: str) -> int:
    t = tok.lstrip("+-")
    t = re.split(r"[eE]", t)[0]
    if "." not in t:
        return 0  # integers are not width claims in this census; declared, not incidental
    t = t.replace(".", "")
    t = t.lstrip("0")
    return len(t)


def widest(text: str):
    best, tok = 0, None
    for m in NUM.finditer(text):
        s = sigfigs(m.group(0))
        if s > best:
            best, tok = s, m.group(0)
    return best, tok


def scan_files(paths, threshold=12):
    n, wide, lits, ex = 0, 0, 0, None
    for p in paths:
        try:
            txt = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        n += 1
        w, tok = widest(txt)
        c = sum(1 for m in NUM.finditer(txt) if sigfigs(m.group(0)) >= threshold)
        lits += c
        if w >= threshold:
            wide += 1
            if ex is None or w > ex[1]:
                ex = (os.path.relpath(p, REPO), w, tok)
    return dict(population=n, objects_with_wide_literal=wide, wide_literals=lits,
                widest_example=ex)


def m2_files(pred):
    out = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            p = os.path.join(root, f)
            if pred(os.path.relpath(p, REPO)):
                out.append(p)
    return sorted(out)


def m2_commit_messages():
    raw = subprocess.run(["git", "-C", REPO, "log", "--format=%H%x00%B%x01"],
                         capture_output=True, text=True).stdout
    msgs = []
    for rec in raw.split("\x01"):
        if "\x00" not in rec:
            continue
        sha, body = rec.split("\x00", 1)
        if body.lstrip().lower().startswith("machine2"):
            msgs.append((sha.strip(), body))
    return msgs


def scan_commits(msgs, threshold=12):
    wide, lits, ex = 0, 0, None
    for sha, body in msgs:
        w, tok = widest(body)
        c = sum(1 for m in NUM.finditer(body) if sigfigs(m.group(0)) >= threshold)
        lits += c
        if w >= threshold:
            wide += 1
            if ex is None or w > ex[1]:
                ex = (sha[:7], w, tok)
    return dict(population=len(msgs), objects_with_wide_literal=wide, wide_literals=lits,
                widest_example=ex)


def selftest():
    """KNOWN-ANSWER TEST.  Positive controls MUST be caught, negative controls MUST NOT."""
    pos = {
        "hand-typed 45 s.f. letter literal": ("a = 0.104051654913127452341094763510384719236412236", 45),
        "30 s.f. JSON serialisation": ('"g00": "-5.31691198313966349161522824112e-44"', 30),
        "175 s.f. D* string": ("0." + "1417332396638871913954156850841850236231445619550166559428666039466590421897074308759327045441534914488594010712911557052299566314026453701541976364138148742188420142330184348", 175),
        "12 s.f. boundary case": ("-37.4819713608", 12),
    }
    neg = {
        "ISO date": "2026-09-07",
        "commit sha": "6181e51df47549dabb6a88280b0fbdce7fbec2c1",
        "version number": "protocol v2.1",
        "11 s.f. literal (below threshold)": "-37.481971360",
        "plain integer": "486",
    }
    ok = True
    for name, (text, expect) in pos.items():
        w, tok = widest(text)
        if w != expect:
            print(f"  SELFTEST FAIL (positive) {name}: got {w} s.f. ({tok!r}), expected {expect}")
            ok = False
        else:
            print(f"  selftest pass (positive) {name}: {w} s.f.")
    for name, text in neg.items():
        w, tok = widest(text)
        if w >= 12:
            print(f"  SELFTEST FAIL (negative) {name}: flagged {w} s.f. ({tok!r})")
            ok = False
        else:
            print(f"  selftest pass (negative) {name}: widest {w} s.f.")
    return ok


BOUNDARIES = [
    ("B1  letter body (m2 cycle letters)",
     lambda r: r.startswith("machine2-c") and r.endswith(".md") and "PREREG" not in r),
    ("B2  commit message", None),
    ("B3  pre-registration file",
     lambda r: r.startswith("machine2-") and r.endswith(".md") and "PREREG" in r),
    ("B4  erratum file",
     lambda r: r.startswith("machine2-ERRATUM") or r.startswith("machine2_ERRATUM")),
    ("B5  JSON storage written by our scripts",
     lambda r: r.startswith("data/") and r.endswith(".json") and "m3_" not in r and "machine1" not in r and "machine3" not in r),
    ("B6  plain-text run output / evaluator print",
     lambda r: r.startswith("data/") and (r.endswith(".txt") or r.endswith(".out") or r.endswith(".log")) and "m3_" not in r and "machine1" not in r and "machine3" not in r),
    ("B7  source-code literal in a producing script",
     lambda r: r.startswith("data/code/") and r.endswith(".py") and (os.path.basename(r).startswith("m2_") or os.path.basename(r).startswith("machine2"))),
    ("B8  spec / handover document written FOR another machine",
     lambda r: r.endswith(".md") and "extraction-spec" in r),
    ("B9  filename / label asserting a width", None),
    ("B10 README / index", lambda r: r.lower().startswith(("readme", "protocol", "index"))),
    ("B11 external-lane artefact outside this repo", None),
    ("B12 audit extract / detector excerpt", None),
]


def main():
    print("== KNOWN-ANSWER TEST ==")
    ok = selftest()
    print(f"== selftest {'PASSED' if ok else 'FAILED'} ==\n")
    if not ok:
        sys.exit(2)

    result = {}
    for name, pred in BOUNDARIES:
        if pred is None:
            if name.startswith("B2"):
                result[name] = scan_commits(m2_commit_messages())
            else:
                result[name] = dict(population=None, objects_with_wide_literal=None,
                                    wide_literals=None, widest_example=None,
                                    note="NOT MEASURED BY THIS SCRIPT -- see register")
            continue
        result[name] = scan_files(m2_files(pred))

    for name in sorted(result):
        r = result[name]
        print(f"{name}")
        if r.get("note"):
            print(f"    {r['note']}")
            continue
        print(f"    population {r['population']:>5} | objects with a >=12 s.f. literal "
              f"{r['objects_with_wide_literal']:>5} | >=12 s.f. literals {r['wide_literals']:>7}")
        if r["widest_example"]:
            p, w, tok = r["widest_example"]
            print(f"    widest: {w} s.f. in {p}")
    out = os.path.join(REPO, "data", "m2_c39_boundary_census.json")
    with open(out, "w") as fh:
        json.dump(result, fh, indent=1)
    print(f"\nwritten: {os.path.relpath(out, REPO)}")


if __name__ == "__main__":
    main()
