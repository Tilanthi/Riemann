#!/usr/bin/env python3
"""c42_table.py — assemble the convergence-in-x table from the run JSONs. Emits MD + TSV + JSON.
   The primary column set is N=100 (the letter's footnote-14 convention), dps as run, GL degree 9."""
import json, glob, re
from mpmath import mp, mpf, mpmathify

mp.dps = 60
PRIM = {}
for f in glob.glob("c42_x*_N100_dps*_g9_*.json"):
    m = re.match(r"c42_x(\d+)_N100_dps(\d+)_g9_", f)
    x = int(m.group(1))
    if x not in PRIM or int(m.group(2)) > PRIM[x][1]:
        PRIM[x] = (f, int(m.group(2)))
XS = sorted(PRIM)
D = {x: json.load(open(PRIM[x][0])) for x in XS}
pub = json.load(open("connes_published_x13.json"))

rows = []
for i in range(50):
    r = dict(n=i + 1, gamma=D[13]['rows'][i]['gamma'], pub=pub['values'][i])
    for x in XS:
        rr = D[x]['rows'][i]
        r['d%d' % x] = rr['diff_nearest']
        r['off%d' % x] = rr['offset']
    r['ratio13'] = mp.nstr(mpmathify(r['d13']) / mpmathify(r['pub']), 9)
    rows.append(r)

hdr = ["n", "gamma_n"] + ["connes_x13_PUBLISHED_UPPERBOUND", "ratio_ours_over_published"] + \
      ["beast_x%d_COMPUTED" % x for x in XS] + ["idxoff_x%d" % x for x in XS]
with open("c42_convergence_in_x.tsv", "w") as f:
    f.write("\t".join(hdr) + "\n")
    for r in rows:
        f.write("\t".join([str(r['n']), r['gamma'][:45], r['pub'], r['ratio13']] +
                          [r['d%d' % x] for x in XS] + [str(r['off%d' % x]) for x in XS]) + "\n")

with open("c42_convergence_in_x.md", "w") as f:
    f.write("| n | gamma_n | Connes x=13 (published, UPPER BOUND) | ours/pub | " +
            " | ".join("x=%d (COMPUTED)" % x for x in XS) + " |\n")
    f.write("|" + "---|" * (4 + len(XS)) + "\n")
    for r in rows:
        cells = []
        for x in XS:
            v = r['d%d' % x]
            cells.append(v if r['off%d' % x] == 0 else v + " (S)")
        f.write("| %d | %s | %s | %s | %s |\n"
                % (r['n'], r['gamma'][:14], r['pub'], r['ratio13'], " | ".join(cells)))
    f.write("\n`(S)` = the n-th approximant is no longer the nearest root to gamma_n "
            "(index offset non-zero): the cell is a distance to the nearest approximant, "
            "NOT the n-th approximant's error. Column kinds: the Connes column is the author's own "
            "UPPER BOUND; every `x=` column of ours is a COMPUTED VALUE.\n")

json.dump(dict(rows=rows, xs=XS, runs={str(x): PRIM[x][0] for x in XS},
               lambda_min={str(x): D[x]['lambda_min'] for x in XS},
               n_roots={str(x): D[x]['n_roots_below_rmax'] for x in XS},
               prime_powers={str(x): D[x]['prime_powers'] for x in XS},
               dps={str(x): D[x]['dps'] for x in XS},
               convention=D[13]['convention']), open("c42_convergence_in_x.json", "w"), indent=1)
print("x columns:", XS)
for x in XS:
    fo = next((r['n'] for r in rows if r['off%d' % x] != 0), None)
    print("  x=%2d  file=%-44s lam=%s  first index-offset at n=%s  d_1=%s"
          % (x, PRIM[x][0], D[x]['lambda_min'][:16], fo, rows[0]['d%d' % x]))
print("wrote c42_convergence_in_x.{tsv,md,json}")
