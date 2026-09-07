#!/usr/bin/env python3
"""c46_analyse.py -- assemble the c46 parity table from the committed cell JSONs.

Every number printed here is derived from the 60-s.f. `lambda_min` literals stored by
c46_parity.py, never from the 30-s.f. reading forms: a ratio asserted at 20 s.f. must be built
from inputs stored wider than the assertion (c43/c44's law -- a specification must print its
inputs wider than the output it asserts).

The parity gap is reported FIRST as the raw, convention-free quantity `ln(lambda_odd/lambda_even)`,
and only THEN converted into an "effective number of extra forced zeros" -- which needs the decay
law AND a zero-count convention, both named at the point of use.
"""
import os, json, glob
from mpmath import mp

HERE = os.path.dirname(os.path.abspath(__file__))
mp.dps = 80

CELLS = {}
for fn in sorted(glob.glob(os.path.join(HERE, "c46_*_x*_N*_dps*_g*_it*.json"))):
    if "block" in os.path.basename(fn):
        continue
    d = json.load(open(fn))
    CELLS[(d["parity"], str(d["x"]), d["N"], d["dps"])] = d

# exact zero counts N(T*) with T* = 2 pi x, i.e. the number of ordinates 0 < gamma <= 2 pi x.
# Convention NAMED: these are EXACT counts of zeros of zeta with 0 < gamma <= T*, from the
# standard tabulated ordinates; m1's exact counts for x = 13, 17, 19, 25 are 21, 32, 38, 56 and
# the two used here at x = 13 and x = 19 are theirs. x = 5 (T* = 31.4159) and x = 4.953032...
# (T* = 31.1207) are counted from the first ordinates 14.1347, 21.0220, 25.0109, 30.4249, 32.9351.
NEXACT = {"13": 21, "19": 38, "5": 4, "4.953032424395115": 4}

print("=" * 108)
print("c46 PARITY TABLE -- lambda_min of the Weil quadratic form, EVEN vs ODD half of the window")
print("all pairs at identical (x, N, dps, gl_degree=9, iters=16); the ONLY difference is basis parity")
print("=" * 108)
rows = []
for (par, xs, N, dps) in sorted(CELLS, key=lambda k: (float(k[1]), k[2], k[0])):
    if par != "even":
        continue
    okey = ("odd", xs, N, dps)
    if okey not in CELLS:
        continue
    e = CELLS[("even", xs, N, dps)]
    o = CELLS[okey]
    le, lo = mp.mpf(e["lambda_min"]), mp.mpf(o["lambda_min"])
    ratio = lo / le
    rows.append(dict(x=xs, N=N, dps=dps, le=le, lo=lo, ratio=ratio,
                     L=mp.mpf(e["L"]), dim_e=e["dim"], dim_o=o["dim"]))

print("\n%-20s %4s %5s  %-34s %-34s %-12s" % ("x", "N", "dps", "lambda_EVEN (30 s.f.)", "lambda_ODD (30 s.f.)", "log10 ratio"))
for r in rows:
    print("%-20s %4d %5d  %-34s %-34s %s"
          % (r["x"], r["N"], r["dps"], mp.nstr(r["le"], 30), mp.nstr(r["lo"], 30),
             mp.nstr(mp.log(r["ratio"], 10), 12)))

print("\n--- the parity gap, raw and convention-free -------------------------------------------------")
print("%-20s %4s  %-24s %-24s %-14s" % ("x", "N", "L = log x", "ln(odd/even)", "log10(odd/even)"))
for r in rows:
    print("%-20s %4d  %-24s %-24s %s"
          % (r["x"], r["N"], mp.nstr(r["L"], 20), mp.nstr(mp.log(r["ratio"]), 20),
             mp.nstr(mp.log(r["ratio"], 10), 20)))

print("\n--- the same gap read through the decay law (CONVENTION-BOUND, do not quote bare) ------------")
print("law: -ln lambda*(L) ~ 2 pi^2 n / ln n, n = N(T*) EXACT count, T* = 2 pi x;")
print("d/dn [n/ln n] = 1/ln n - 1/ln^2 n; delta_n := ln(odd/even) / (2 pi^2 (1/ln n - 1/ln^2 n))")
print("the implied constant is taken at its LAW value 2 pi^2 = %s, NOT at the measured 19.4-20.3;" % mp.nstr(2 * mp.pi ** 2, 8))
print("using the measured constant instead moves delta_n by about 2 per cent. Both are declared.")
print("%-20s %4s %4s  %-22s %-14s" % ("x", "N", "n", "2pi^2 dn/d(n/ln n)", "delta_n"))
for r in rows:
    n = NEXACT.get(r["x"])
    if n is None:
        continue
    dn = 2 * mp.pi ** 2 * (1 / mp.log(n) - 1 / mp.log(n) ** 2)
    print("%-20s %4d %4d  %-22s %s"
          % (r["x"], r["N"], n, mp.nstr(dn, 10), mp.nstr(mp.log(r["ratio"]) / dn, 10)))

print("\n--- N-ladder at x = 13 (Cauchy interlacing: both blocks are NESTED in N) ---------------------")
for par in ("even", "odd"):
    seq = sorted([(k[2], CELLS[k]) for k in CELLS if k[0] == par and k[1] == "13" and k[3] == 150])
    prev = None
    for (N, d) in seq:
        lam = mp.mpf(d["lambda_min"])
        mono = "" if prev is None else ("  non-increasing OK" if lam <= prev else "  ** INCREASED **")
        print("  %-4s N=%-4d dim=%-4d lambda = %-34s log10 = %s%s"
              % (par, N, d["dim"], mp.nstr(lam, 30), mp.nstr(mp.log(lam, 10), 14), mono))
        prev = lam
    seq2 = {N: mp.mpf(d["lambda_min"]) for (N, d) in seq}
print("\n  gap vs truncation:")
for N in sorted(set(k[2] for k in CELLS if k[1] == "13" and k[3] == 150)):
    ke, ko = ("even", "13", N, 150), ("odd", "13", N, 150)
    if ke in CELLS and ko in CELLS:
        r = mp.mpf(CELLS[ko]["lambda_min"]) / mp.mpf(CELLS[ke]["lambda_min"])
        print("    N=%-4d log10(odd/even) = %s" % (N, mp.nstr(mp.log(r, 10), 20)))
