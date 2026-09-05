"""Trace BST critical-zero branches rho_y(Delta) directly from BST eq.(critzeros),
arXiv:2110.09368v2.  Positive control = the paper's own Table 1 (24 edge zeros, 15 digits):
worst |G| = 3.587e-15 (that row is rho_y=0; the other 23 are 1e-20..1e-28).  See bst_eq.py.
This replaces 'digitise Figure 1' with 'solve the figure's defining equation'.
"""
from mpmath import mp
import bst_eq as B

mp.dps = 20
GRID = ["0.15","0.2","0.25","0.3","0.35","0.4","0.45","0.5","0.55","0.6",
        "0.65","0.7","0.75","0.8","0.85","0.9","0.95","1.0"]
STEP = mp.mpf("0.05")
YMAX = mp.mpf(21)

print("root census of G(rho_y,Delta)=0 on 0<=rho_y<=21, scan step %s, refined by bisection" % STEP)
print("%-6s %-4s %s" % ("Delta", "n", "rho_y roots"))
allr = {}
for Ds in GRID:
    D = mp.mpf(Ds)
    ys = []
    y = mp.mpf(0)
    prev = B.G(y, D)
    while y < YMAX:
        y2 = y + STEP
        cur = B.G(y2, D)
        if prev == 0:
            ys.append(y)
        elif (prev < 0) != (cur < 0):
            r = mp.findroot(lambda t: B.G(t, D), (y, y2), solver='bisect', tol=mp.mpf('1e-24'))
            ys.append(r)
        y, prev = y2, cur
    allr[Ds] = ys
    print("%-6s %-4d %s" % (Ds, len(ys), ", ".join(mp.nstr(r, 12) for r in ys)))
