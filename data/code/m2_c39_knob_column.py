#!/usr/bin/env python3
"""
machine2 cycle 39 -- FILL THE KNOB HALF OF THE SPLIT COLUMN.

BEAST-AGI's c38 ruling section 3 authorised splitting the C7 row's remaining column:

    working_precision_at_publication  -- a KNOB.  Recoverable from committed cfg blocks, no re-run.
    accuracy_at_publication           -- a MEASUREMENT.  UNMEASURABLE for most rows.

This script fills the KNOB half only, and it fills it by MEASUREMENT (reading the working-precision
declaration out of the committed artefact that carries each constant), never by recollection.
The accuracy half is emitted as an explicitly empty column so that its sparsity is visible in the
artefact rather than described in prose.

Method, declared:
  1. Attribution is by path/basename rule, a deliberate over-approximation of "ours", as in c37.
  2. A constant's key is its first 12 significant digits (c37's convention, kept so the two censuses
     are joinable).
  3. working_precision(file) is read from the file itself: mp.dps = N, dps=N, "dps": N, plus any
     guard digits declared alongside.  A file with several distinct declarations yields a SET, and a
     constant carried only by such files is reported as a RANGE, not a point -- a range is the honest
     form when the artefact does not say which run wrote which line.
  4. A markdown letter declares no working precision.  Constants that appear ONLY in .md files are
     UNRESOLVED-BY-KNOB, and that is a finding about letters, not a gap to be filled by guessing.
"""
import collections
import json
import os
import re
import subprocess

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NUM = re.compile(r"(?<![\w.])(\d+)\.(\d+)(?:[eEdD]([+-]?\d+))?(?![\w.])")
DPS = re.compile(r"(?:mp\.dps\s*=\s*|[\"']dps[\"']\s*:\s*|\bdps\s*=\s*)(\d{1,4})")
GUARD = re.compile(r"(?:[\"']guard[\"']\s*:\s*|\bguard\s*=\s*)(\d{1,4})")

OURS_PREFIX = ("machine2", "m2_", "machine2_", "c3")


def is_ours(path):
    b = os.path.basename(path)
    if b.startswith(("machine1", "machine3", "m3_", "m1_", "letter", "BEAST", "SAPIENS")):
        return False
    if b.startswith(OURS_PREFIX):
        return True
    return False


def tracked():
    out = subprocess.run(["git", "-C", R, "ls-files"], capture_output=True, text=True).stdout
    return [f for f in out.split("\n") if f and not f.lower().endswith(".pdf")]


def read(p):
    try:
        return open(os.path.join(R, p), encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def main():
    files = [f for f in tracked() if is_ours(f)]
    md = [f for f in files if f.endswith(".md")]
    dat = [f for f in files if not f.endswith(".md")]
    print(f"attribution (declared over-approximation): {len(files)} our-side tracked files "
          f"({len(md)} .md, {len(dat)} data/code)")

    knob = {}
    for f in dat:
        txt = read(f)
        d = sorted({int(x) for x in DPS.findall(txt)})
        g = sorted({int(x) for x in GUARD.findall(txt)})
        if d:
            knob[f] = (d, g)
    print(f"files declaring a working precision: {len(knob)} of {len(dat)} data/code files")

    idx = collections.defaultdict(set)
    for f in files:
        for line in read(f).split("\n"):
            for m in NUM.finditer(line):
                digs = (m.group(1) + m.group(2)).lstrip("0")
                if len(digs) >= 10:
                    idx[digs[:12]].add(f)

    rows = []
    for k, fs in sorted(idx.items()):
        carriers = sorted(fs)
        with_knob = [f for f in carriers if f in knob]
        dpsset = sorted({d for f in with_knob for d in knob[f][0]})
        guards = sorted({g for f in with_knob for g in knob[f][1]})
        if not carriers:
            status = "NO CARRIER"
        elif not with_knob:
            status = "UNRESOLVED-BY-KNOB (carried only by artefacts that declare no dps)"
        elif len(dpsset) == 1:
            status = "POINT"
        else:
            status = "RANGE"
        rows.append(dict(key=k, n_carriers=len(carriers),
                         n_carriers_declaring_dps=len(with_knob),
                         working_precision_at_publication=(dpsset or None),
                         guard_digits=(guards or None),
                         knob_status=status,
                         accuracy_at_publication=None,
                         accuracy_status="UNMEASURED",
                         example_carrier=carriers[0]))

    tot = len(rows)
    by = collections.Counter(r["knob_status"] for r in rows)
    print(f"\nconstants keyed (>=10 sig digits, 12-digit key): {tot}")
    for s, n in by.most_common():
        print(f"  {s:<62} {n:>5}  ({100*n/tot:.2f}%)")
    filled = by["POINT"] + by["RANGE"]
    print(f"\nKNOB column coverage: {filled}/{tot} = {100*filled/tot:.2f}%")
    print(f"ACCURACY column coverage: 0/{tot} = 0.00%  (left honestly empty; see register)")

    out = os.path.join(R, "data", "m2_c39_split_column.json")
    json.dump(rows, open(out, "w"), indent=0)
    print(f"\nwritten: {os.path.relpath(out, R)}")

    tsv = os.path.join(R, "data", "m2_c39_split_column.tsv")
    with open(tsv, "w") as fh:
        fh.write("key\tn_carriers\tn_carriers_declaring_dps\tworking_precision_at_publication\t"
                 "guard_digits\tknob_status\taccuracy_at_publication\taccuracy_status\texample_carrier\n")
        for r in rows:
            fh.write("\t".join([
                r["key"], str(r["n_carriers"]), str(r["n_carriers_declaring_dps"]),
                ",".join(map(str, r["working_precision_at_publication"] or [])) or "-",
                ",".join(map(str, r["guard_digits"] or [])) or "-",
                r["knob_status"], "-", r["accuracy_status"], r["example_carrier"]]) + "\n")
    print(f"written: {os.path.relpath(tsv, R)}")

    # JOIN to the c37 Tier-2 census, so the coverage number is stated over the SAME denominator
    # the C7 row was opened on (486 transported constants) and not over our whole corpus.
    import csv
    by_key = {r["key"]: r for r in rows}
    cen = os.path.join(R, "data", "m2_c37_published_constants_census.tsv")
    if os.path.exists(cen):
        st, n = collections.Counter(), 0
        with open(cen) as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                s = row["our_string"].strip().lstrip("+-")
                s = re.split(r"[eEdD]", s)[0]
                k = s.replace(".", "").lstrip("0")[:12]
                n += 1
                r = by_key.get(k)
                st[r["knob_status"] if r else "NOT IN c39 INDEX"] += 1
        f2 = st["POINT"] + st["RANGE"]
        print(f"\n-- joined to the c37 Tier-2 census ({n} transported constants) --")
        for s, c in st.most_common():
            print(f"  {s:<62} {c:>4}  ({100*c/n:.2f}%)")
        print(f"KNOB coverage on the c37 census: {f2}/{n} = {100*f2/n:.2f}%")
        print(f"(c38 measured TESTIMONY coverage on the same denominator: 11/{n} = 2.26%)")


if __name__ == "__main__":
    main()
