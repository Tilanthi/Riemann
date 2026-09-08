#!/usr/bin/env python3
"""m2_c48_storage_census.py -- how much of machine 2's committed storage still discards digits?

The c47 promise was made about the cells m3 compared against, and c48 discharges it there. That is a
fix with no denominator, and a fix with no denominator is the shape that ages out quietly: nothing
ever reports what is left. This census gives the remainder a number.

WHAT IT MEASURES, and the convention is stated because it decides the count:
for every committed JSON artefact attributable to machine 2 that declares a working precision
(`dps`), every string field that parses as a decimal number is scored

    stored_sf   = significant digits actually in the string
    run_sf      = floor(dps * 1) ... the digits the run had available   (we use dps directly;
                  mpmath's dps IS a decimal-digit count, so this is the right unit)
    DISCARDED   = run_sf - stored_sf   when stored_sf < run_sf - 2

The -2 slack keeps a field that stores essentially everything from being scored as a defect for a
rounding digit. A field printed *wider* than the run is scored separately as OVERWIDE -- c38's
ERRATUM 19 was that defect, and a census that only looks one way would miss it.

ATTRIBUTION is by two independent signals, as in c37: the filename prefix, and the creating commit's
subject line. Disagreements are REPORTED, never silently resolved.

SCOPE: machine 2's own artefacts only. The other machines' storage is theirs to census; the module
is offered, not applied to their files.

usage: m2_c48_storage_census.py [REPOROOT] [OUT.tsv]
"""
import sys, os, re, json, subprocess, glob

DEC = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")


def sig_digits(s):
    m = s.split("e")[0].split("E")[0].replace("-", "").replace("+", "").replace(".", "")
    m = m.lstrip("0")
    return len(m.rstrip("0")) if m else 0


def creating_commit_subject(repo, rel):
    try:
        return subprocess.run(["git", "log", "--diff-filter=A", "--format=%s", "-1", "--", rel],
                              cwd=repo, capture_output=True, text=True).stdout.strip()[:60]
    except Exception:
        return ""


def main(repo, outtsv):
    files = sorted(glob.glob(os.path.join(repo, "data", "**", "*.json"), recursive=True))
    rows, disagree = [], []
    tot_files = tot_fields = tot_disc = tot_over = 0
    for f in files:
        rel = os.path.relpath(f, repo)
        base = os.path.basename(f)
        by_name = base.startswith(("machine2", "m2_", "c30", "c31", "c33", "c34", "c35", "c36",
                                   "c37", "c38", "c42", "c43", "c44", "c45", "c46", "c48"))
        subj = creating_commit_subject(repo, rel)
        by_commit = subj.startswith("machine2")
        if by_name != by_commit:
            disagree.append((rel, by_name, by_commit, subj))
        if not (by_name or by_commit):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        if not isinstance(d, dict) or "dps" not in d or not isinstance(d["dps"], int):
            continue
        dps = d["dps"]
        tot_files += 1
        for k, v in sorted(d.items()):
            if not isinstance(v, str) or not DEC.match(v.strip()):
                continue
            if k.endswith("_full") or k.endswith("_sf"):
                continue
            sd = sig_digits(v)
            tot_fields += 1
            has_exact = (k.split("_30")[0] + "_exact") in d or (k + "_exact") in d
            if sd > dps + 2:
                verdict, gap = "OVERWIDE", sd - dps
                tot_over += 1
            elif sd < dps - 2 and not has_exact:
                verdict, gap = "DISCARDED", dps - sd
                tot_disc += 1
            elif sd < dps - 2 and has_exact:
                verdict, gap = "NARROW-BUT-BACKED", dps - sd
            else:
                verdict, gap = "FULL", 0
            rows.append((rel, k, dps, sd, gap, verdict))

    with open(outtsv, "w") as fh:
        fh.write("file\tfield\trun_dps\tstored_sf\tgap\tverdict\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    print("m2_c48_storage_census   repo=%s" % repo)
    print("  machine-2 JSON artefacts declaring a dps : %d" % tot_files)
    print("  numeric string fields scored             : %d" % tot_fields)
    print("  DISCARDED (stored narrower, no _exact)   : %d" % tot_disc)
    print("  NARROW-BUT-BACKED (c48 storage present)  : %d"
          % sum(1 for r in rows if r[5] == "NARROW-BUT-BACKED"))
    print("  FULL                                     : %d"
          % sum(1 for r in rows if r[5] == "FULL"))
    print("  OVERWIDE (printed wider than the run)    : %d" % tot_over)
    if tot_over:
        for r in rows:
            if r[5] == "OVERWIDE":
                print("      %s :: %s  stored %d s.f. from a dps=%d run" % (r[0], r[1], r[3], r[2]))
    # PER-FILE rollup. The per-field count above over-reports: `lambda_min_30` is a deliberate
    # reading form, not a defect, when a wider form sits beside it. The load-bearing question is
    # per ARTEFACT -- does this file retain its number at the precision its run had, ANYWHERE?
    byfile = {}
    for r in rows:
        byfile.setdefault(r[0], []).append(r[5])
    full_files = sum(1 for f, vs in byfile.items()
                     if any(v in ("FULL", "NARROW-BUT-BACKED") for v in vs))
    print("  --- per-ARTEFACT rollup (the load-bearing convention) ---")
    print("  artefacts retaining full working precision anywhere : %d of %d"
          % (full_files, len(byfile)))
    print("  artefacts whose every numeric field is narrower     : %d of %d"
          % (len(byfile) - full_files, len(byfile)))
    print("  attribution-signal disagreements         : %d  (direction: %d name-only, %d commit-only)"
          % (len(disagree), sum(1 for d_ in disagree if d_[1] and not d_[2]),
             sum(1 for d_ in disagree if d_[2] and not d_[1])))
    for d_ in disagree[:10]:
        print("      %s  name=%s commit=%s  [%s]" % d_)
    worst = sorted([r for r in rows if r[5] == "DISCARDED"], key=lambda r: -r[4])[:8]
    if worst:
        print("  widest remaining discards:")
        for r in worst:
            print("      %-58s %-14s dps=%-4d stored=%-4d  -%d digits" % (r[0][-58:], r[1], r[2],
                                                                         r[3], r[4]))
    print("  census written to %s" % outtsv)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    HERE = os.path.dirname(os.path.abspath(__file__))
    REPO = os.path.dirname(os.path.dirname(HERE))
    sys.exit(main(a[0] if a else REPO,
                  a[1] if len(a) > 1 else os.path.join(REPO, "data", "c48",
                                                       "m2_c48_storage_census.tsv")))
