#!/usr/bin/env python3
"""m2_c57_offset_drift_census.py -- IS THE MISALIGNMENT A SHIFT, OR IS IT NOT EVEN A SHIFT?

c57's alignment self-check found that at x=42 the best offset between the N=100 and N=180 ladders is
6 at rungs 1-4 and 7 from rung 5 upward, in BOTH parities.  If that also happens at x=13, 17 and 19,
then the published trusted depths there were computed by comparing non-matching objects and the
"no published result is threatened" line of c56 needs re-examining.  This program asks that question
at EVERY window the programme owns, from stage-A spectra only.

PINNING (trap #177): the corpus is derived by content, sorted, and every (x,N,parity) slot must have
EXACTLY ONE spectrum or it is reported as UNPINNABLE rather than silently resolved.
"""
import json, os, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, ".."))
print("resolver: data dir = %s" % DATA)


def corpus():
    out = []
    for root, dirs, fs in os.walk(DATA):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(fs):
            if not f.endswith(".json"):
                continue
            p = os.path.join(root, f)
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if (isinstance(d, dict) and isinstance(d.get("rungs"), list) and len(d["rungs"]) > 20
                    and isinstance(d["rungs"][0], dict) and "log10" in d["rungs"][0]
                    and "nu" not in d["rungs"][0]
                    and all(k in d for k in ("x", "N", "parity"))):
                out.append((os.path.relpath(p, DATA), d))
    return sorted(out)


specs = corpus()
slots = {}
for rel, d in specs:
    slots.setdefault((d["x"], d["parity"], d["N"]), []).append((rel, d))

rows, unpinnable = [], []
for x, par in sorted({(x, p) for x, p, _N in slots}):
    a_c = slots.get((x, par, 100), [])
    b_c = slots.get((x, par, 180), [])
    if len(a_c) != 1 or len(b_c) != 1:
        unpinnable.append(dict(x=x, parity=par, n100=[c[0] for c in a_c], n180=[c[0] for c in b_c]))
        continue
    a = [Decimal(r["log10"]) for r in a_c[0][1]["rungs"] if r.get("log10")]
    b = [Decimal(r["log10"]) for r in b_c[0][1]["rungs"] if r.get("log10")]
    drift = []
    for k in range(1, min(len(a), 20) + 1):
        j = min(range(len(b)), key=lambda t: abs(float(a[k - 1] - b[t])))
        gk = float(a[min(k, len(a) - 1)] - a[min(k, len(a) - 1) - 1])
        drift.append((k, j + 1 - k, round(float(a[k - 1] - b[j]) / gk, 4)))
    offs = [d[1] for d in drift]
    rows.append(dict(x=x, parity=par, n100=a_c[0][0], n180=b_c[0][0],
                     offsets=offs, distinct_offsets=sorted(set(offs)),
                     offset_is_constant=(len(set(offs)) == 1),
                     first_change_at_rung=(None if len(set(offs)) == 1 else
                                           next(d[0] for i, d in enumerate(drift)
                                                if i and d[1] != drift[i - 1][1])),
                     max_residual_in_gaps=max(abs(d[2]) for d in drift),
                     detail=drift))
out = dict(cycle=57, question="is the N=100 -> N=180 misalignment a constant shift?",
           spectra=len(specs), pairs=len(rows), unpinnable=unpinnable,
           constant_offset_pairs=sum(1 for r in rows if r["offset_is_constant"]),
           drifting_offset_pairs=sum(1 for r in rows if not r["offset_is_constant"]),
           rows=rows)
json.dump(out, open(os.path.join(HERE, "m2_c57_offset_drift_census.json"), "w"), indent=1)
print("%-5s %-6s %-9s %-22s %-8s %s" % ("x", "parity", "constant?", "offsets seen", "1st chg",
                                        "max |resid| in gaps"))
for r in rows:
    print("%-5d %-6s %-9s %-22s %-8s %.4f"
          % (r["x"], r["parity"], r["offset_is_constant"], str(r["distinct_offsets"]),
             r["first_change_at_rung"], r["max_residual_in_gaps"]))
print("\nconstant %d / drifting %d of %d pinned pairs; %d unpinnable slots"
      % (out["constant_offset_pairs"], out["drifting_offset_pairs"], len(rows), len(unpinnable)))
for u in unpinnable:
    print("  UNPINNABLE x=%d %s: N100 %s | N180 %s" % (u["x"], u["parity"], u["n100"], u["n180"]))
