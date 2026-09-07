#!/usr/bin/env python3
"""machine2 -- c40 -- RULE K, IMPLEMENTATION B.

Derived from the LOW run's code, split_column_v2.py (6.4%, never committed; preserved at
/shared/progress/c39-atlas-unpushed/), by changing ONLY the clauses where that code deviates from
RULE K as pre-registered:

  K6   the carrier index becomes CORPUS-WIDE.  The low run indexed only data/*c3[3-8]* artefacts
       whose basename starts m2_/machine2_ -- 33 files, 17 of them stating a dps -- which answers
       "recoverable from the cycle that published it", a different question from the one the column
       names.  This is the clause the low run's 6.4% actually measures.
  K2 + A4  key truncated to 12 significant digits with a floor; matching symmetric-prefix at equal
       decimal exponent.  The low run used unbounded prefix-consistency at a floor of 12.

Its band construction {min(dps)+min(guard), max(dps)+max(guard)} is replaced by K7's literal reading,
W(file) = {d + g : d in dps, g in guard or {0}}.

Written from the low run's mant()/index shape rather than from implementation A, so that F1 -- the
prereg's requirement that two implementations of one rule agree EXACTLY -- is a real test and not a
copy compared with itself.
"""
import argparse, collections, csv, json, os, re, subprocess

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NUM = re.compile(r'(?<![\w.])[+-]?\d+\.\d+(?:[eE][+-]?\d+)?(?![\w.])')
DPSRE = re.compile(r"'?\"?dps'?\"?\s*[:=]\s*(\d+)")
GURE = re.compile(r"'?\"?guard'?\"?\s*[:=]\s*(\d+)")
MPDPS = re.compile(r"mp\.dps\s*=\s*(\d+)")


def mant(tok):
    """(significant digits, decimal exponent) -- the low run's mant(), kept."""
    t = tok.strip().lstrip('+-')
    e = 0
    if 'e' in t or 'E' in t:
        h, x = re.split(r'[eE]', t)[:2]
        try:
            e = int(x)
        except Exception:
            return None
        t = h
    ip, fp = t.split('.', 1) if '.' in t else (t, '')
    alld = ip + fp
    d = alld.lstrip('0')
    if not d:
        return None
    return d, len(ip) - (len(alld) - len(d)) + e


def is_ours(b):                                       # A2
    b = os.path.basename(b)
    if b.startswith(("machine1", "machine3", "m3_", "m1_", "letter", "BEAST", "SAPIENS")):
        return False
    return b.startswith(("machine2", "m2_", "machine2_", "c3"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", type=int, default=10)
    ap.add_argument("--family-only", action="store_true",
                    help="restore the low run's K6 violation: index only data/*c3[3-8]* artefacts")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    ls = subprocess.run(["git", "-C", R, "ls-files"], capture_output=True, text=True).stdout.split("\n")
    cand = [f for f in ls if f and not f.lower().endswith(".pdf")
            and not f.endswith(".md") and is_ours(f)]
    if a.family_only:
        cand = [f for f in cand
                if re.search(r"c3[3-8]", os.path.basename(f))
                and os.path.basename(f).startswith(("m2_", "machine2_"))]

    index = collections.defaultdict(set)
    prov = collections.defaultdict(set)
    stated = 0
    for f in cand:
        t = open(os.path.join(R, f), errors='replace').read()
        dps = sorted({int(x) for x in DPSRE.findall(t)} | {int(x) for x in MPDPS.findall(t)})
        gu = sorted({int(x) for x in GURE.findall(t)})
        if not dps:
            continue
        stated += 1
        Ws = {d + g for d in dps for g in (gu or [0])}          # K7
        for m in NUM.finditer(t):
            mm = mant(m.group(0))
            if mm and len(mm[0]) >= a.floor:
                k = (mm[0][:12], mm[1])
                index[k] |= Ws
                prov[k].add(os.path.basename(f))
    print("IMPLEMENTATION B (from the low run's code) | floor=%d | family_only=%s"
          % (a.floor, a.family_only))
    print("  candidate carrier files %d, stating a working precision %d, indexed keys %d"
          % (len(cand), stated, len(index)))

    rows = list(csv.DictReader(open(os.path.join(R, "data", "m2_c37_published_constants_census.tsv")),
                               delimiter='\t'))
    buckets = collections.defaultdict(list)
    for (d, e), w in index.items():
        buckets[e].append((d, w))

    st = collections.Counter()
    detail = {}
    for r in rows:
        s = r["our_string"].strip()
        m = NUM.search(s)
        mm = mant(m.group(0)) if m else None
        if not mm or len(mm[0]) < a.floor:
            st["UNKEYABLE (below floor)"] += 1
            detail[s] = ("UNKEYABLE", [])
            continue
        d, e = mm[0][:12], mm[1]
        Ws = set()
        for cand_d, w in buckets.get(e, ()):
            if cand_d.startswith(d) or d.startswith(cand_d):    # A4
                Ws |= w
        if not Ws:
            st["UNRESOLVED-BY-KNOB"] += 1
            detail[s] = ("UNRESOLVED-BY-KNOB", [])
        elif len(Ws) == 1:
            st["POINT"] += 1
            detail[s] = ("POINT", sorted(Ws))
        else:
            st["RANGE"] += 1
            detail[s] = ("RANGE", sorted(Ws))
            if max(Ws) <= 2 * min(Ws):
                st["  (of which TIGHT RANGE, max/min <= 2)"] += 1

    n = len(rows)
    rec = st["POINT"] + st["RANGE"]
    for k, c in st.most_common():
        print("  %-42s %5d  (%.2f%%)" % (k, c, 100.0 * c / n))
    print("  RECOVERED %d/%d = %.2f%%" % (rec, n, 100.0 * rec / n))
    if a.json_out:
        json.dump(detail, open(a.json_out, "w"), indent=0)
        print("  written: %s" % a.json_out)


if __name__ == "__main__":
    main()
