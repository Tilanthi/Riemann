#!/usr/bin/env python3
"""m2_c52_grid.py -- cycle 52's REGISTERED CELL GRID, emitted deterministically from a rule.

The grid is a rule, not a list, so that "which cells were registered" cannot drift between the
prereg and the run.  Print it, seal the print, run exactly it.

    x grid      : 12 windows, fixed below.
    parities    : even, odd (both, at every (x,N)).
    N per x     : 60, 100, N_iso(x) = round(100 * log x / log 5)   [dedup if it lands on 60/100]
    dps         : 300 at EVERY cell (deliberately NOT varied with x -- see prereg C2/arm D)
    gl_degree   : 9      iters : 16      k : 3   (per sector)

TIERS.  Cells are emitted in completion-priority order so that an exhausted window degrades
gracefully and the DENOMINATOR is legible:
    tier 1 = every N=60 cell           (the cheap full-shape pass)
    tier 2 = every N=100 cell          (the fixed-N series; with tier 1 this is the N-control AT EACH x)
    tier 3 = every isoresolution cell, ascending N  (the crux arm, most expensive last)
A per-x verdict requires tiers 1 and 2 complete at that x.  Tier 3 missing at an x means the
isoresolution question is UNMEASURED at that x -- stated per x, never averaged away.
"""
import sys
from mpmath import mp

mp.dps = 40

# the 12 windows.  4.00/4.82 share n=3; 4.86/5/5.23 share n=4; 4.82->4.86 crosses gamma_4/(2 pi)
# = 4.8422... , i.e. it moves n by +1 while moving x by 0.83 per cent.  See prereg P3a/P3b.
XGRID = ["4", "4.82", "4.86", "5", "5.23", "7", "9", "11", "13", "16", "19", "23"]
DPS, GLDEG, ITERS, K = 300, 9, 16, 3
NBASE = [60, 100]


def n_iso(xs):
    return int(mp.floor(100 * mp.log(mp.mpf(xs)) / mp.log(5) + mp.mpf("0.5")))


def cells():
    out = []
    for tier, Nof in ((1, lambda xs: [60]), (2, lambda xs: [100])):
        for xs in XGRID:
            for N in Nof(xs):
                for par in ("even", "odd"):
                    out.append((tier, N, xs, par))
    t3 = []
    for xs in XGRID:
        N = n_iso(xs)
        if N in NBASE:
            continue
        for par in ("even", "odd"):
            t3.append((3, N, xs, par))
    t3.sort(key=lambda c: (c[1], c[2]))
    return out + t3


def cellname(par, xs, N):
    return "c46_block_%s_x%s_N%d_dps%d_g%d_it%d_k%d.json" % (
        par, xs.replace(".", "p"), N, DPS, GLDEG, ITERS, K)


if __name__ == "__main__":
    cs = cells()
    if len(sys.argv) > 1 and sys.argv[1] == "--names":
        for (t, N, xs, par) in cs:
            print(cellname(par, xs, N))
    elif len(sys.argv) > 1 and sys.argv[1] == "--cmds":
        for (t, N, xs, par) in cs:
            print("%d\t%s\tblock %s %s %d %d %d %d %d" % (t, cellname(par, xs, N), par, xs, N,
                                                          DPS, GLDEG, ITERS, K))
    else:
        print("x grid (%d): %s" % (len(XGRID), " ".join(XGRID)))
        print("N_iso     : %s" % " ".join("%s->%d" % (x, n_iso(x)) for x in XGRID))
        for t in (1, 2, 3):
            sub = [c for c in cs if c[0] == t]
            print("tier %d: %3d cells   N in {%s}" % (t, len(sub), ",".join(
                sorted({str(c[1]) for c in sub}, key=int))))
        print("TOTAL REGISTERED CELLS: %d" % len(cs))
