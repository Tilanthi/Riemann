#!/usr/bin/env python3
"""machine2 -- c40 -- RULE K, IMPLEMENTATION A.

Derived from the HIGH run's committed code, data/code/m2_c39_knob_column.py (32.72%), by changing
ONLY the clauses where that code deviates from RULE K as pre-registered in
machine2-c40-PREREG-membership-rule-K-...-20260907T035213Z.md and its two addenda:

  K2 + A4  the join key becomes EXPONENT-AWARE and matching becomes symmetric prefix-at-the-shorter-
           length after truncation to 12 significant digits.  The c39 code keyed on digits[:12] with
           the exponent DISCARDED and joined the census by exact dict equality.
  K7       guard digits are ADDED to dps to form the working precision.  The c39 code kept guard in
           a separate column, so its published values are a different quantity from the low run's.
  A4       carrier floor is a parameter (--floor), reported at 10 and at 12.

Everything else -- corpus-wide index (K6), literal containment only (K1/K5), the dps/guard regexes
(K3), the is_ours attribution (A2), the 486-row c37 denominator (K8) -- is the c39 code's behaviour,
unchanged, because those clauses already agreed with RULE K.

This file is one of TWO independent implementations of one specification.  F1 in the prereg says
they must agree EXACTLY; a difference of one row means RULE K does not name every axis.
"""
import argparse, collections, csv, json, os, re, subprocess

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# c39's tokeniser, unchanged: a literal must contain a decimal point (K2).
NUM = re.compile(r"(?<![\w.])(\d+)\.(\d+)(?:[eEdD]([+-]?\d+))?(?![\w.])")
DPS = re.compile(r"(?:mp\.dps\s*=\s*|[\"']dps[\"']\s*:\s*|\bdps\s*=\s*)(\d{1,4})")
GUARD = re.compile(r"(?:[\"']guard[\"']\s*:\s*|\bguard\s*=\s*)(\d{1,4})")

OURS_PREFIX = ("machine2", "m2_", "machine2_", "c3")


def is_ours(path):                      # A2: adopted verbatim from the committed c39 code
    b = os.path.basename(path)
    if b.startswith(("machine1", "machine3", "m3_", "m1_", "letter", "BEAST", "SAPIENS")):
        return False
    return b.startswith(OURS_PREFIX)


def tracked():
    out = subprocess.run(["git", "-C", R, "ls-files"], capture_output=True, text=True).stdout
    return [f for f in out.split("\n") if f and not f.lower().endswith(".pdf")]


def read(p):
    try:
        return open(os.path.join(R, p), encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def key_of(ip, fp, ex):
    """(significant digits truncated to 12, decimal exponent).  K2, exponent-aware."""
    alld = ip + fp
    d = alld.lstrip("0")
    if not d:
        return None
    lead = len(alld) - len(d)
    e = len(ip) - lead + (int(ex) if ex else 0)
    return d, e                                        # digits as printed; no trailing-zero strip


def norm(digits, floor):
    return digits[:12] if len(digits) >= floor else None


def pref(a, b):
    return a.startswith(b) or b.startswith(a)          # A4: symmetric prefix-at-the-shorter-length


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", type=int, default=10)
    ap.add_argument("--exp-blind", action="store_true",
                    help="restore the high run's K2 violation: discard the decimal exponent")
    ap.add_argument("--exact-join", action="store_true",
                    help="restore the high run's join: exact key equality, not symmetric prefix")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    files = [f for f in tracked() if is_ours(f)]
    dat = [f for f in files if not f.endswith(".md")]

    # K3: working precision declared IN the file; K7: guard ADDED to dps.
    W = {}
    for f in dat:
        t = read(f)
        ds = sorted({int(x) for x in DPS.findall(t)})
        gs = sorted({int(x) for x in GUARD.findall(t)})
        if ds:
            W[f] = {d + g for d in ds for g in (gs or [0])}

    # K1/K5/K6: literal containment in a tracked our-side NON-.md file, corpus-wide, no inheritance.
    idx = collections.defaultdict(set)                 # (digits12, exp) -> set of precisions
    for f in dat:
        if f not in W:
            continue
        for m in NUM.finditer(read(f)):
            k = key_of(m.group(1), m.group(2), m.group(3))
            if not k:
                continue
            d12 = norm(k[0], a.floor)
            if d12:
                idx[(d12, 0 if a.exp_blind else k[1])] |= W[f]

    rows = list(csv.DictReader(open(os.path.join(R, "data", "m2_c37_published_constants_census.tsv")),
                               delimiter="\t"))
    by_exp = collections.defaultdict(list)
    for (d12, e), ws in idx.items():
        by_exp[e].append((d12, ws))

    st = collections.Counter()
    detail = {}
    for r in rows:
        s = r["our_string"].strip()
        mm = NUM.fullmatch(s) or NUM.search(s)
        k = key_of(mm.group(1), mm.group(2), mm.group(3)) if mm else None
        d12 = norm(k[0], a.floor) if k else None
        ws = set()
        if d12:
            e = 0 if a.exp_blind else k[1]
            if a.exact_join:
                for cand, w in by_exp.get(e, ()):
                    if cand == d12:
                        ws |= w
            else:
                for cand, w in by_exp.get(e, ()):
                    if pref(d12, cand):
                        ws |= w
        if not d12:
            st["UNKEYABLE (below floor)"] += 1
            status = "UNKEYABLE"
        elif not ws:
            st["UNRESOLVED-BY-KNOB"] += 1
            status = "UNRESOLVED-BY-KNOB"
        elif len(ws) == 1:
            st["POINT"] += 1
            status = "POINT"
        else:
            st["RANGE"] += 1
            status = "RANGE"
            if max(ws) <= 2 * min(ws):
                st["  (of which TIGHT RANGE, max/min <= 2)"] += 1
        detail[s] = (status, sorted(ws))

    n = len(rows)
    rec = st["POINT"] + st["RANGE"]
    print("IMPLEMENTATION A (from the high run's code) | floor=%d" % a.floor)
    print("  our-side tracked files %d, non-.md %d, declaring a working precision %d"
          % (len(files), len(dat), len(W)))
    print("  indexed keys %d" % len(idx))
    for s, c in st.most_common():
        print("  %-42s %5d  (%.2f%%)" % (s, c, 100.0 * c / n))
    print("  RECOVERED %d/%d = %.2f%%" % (rec, n, 100.0 * rec / n))
    if a.json_out:
        json.dump({k: v for k, v in detail.items()}, open(a.json_out, "w"), indent=0)
        print("  written: %s" % a.json_out)


if __name__ == "__main__":
    main()
