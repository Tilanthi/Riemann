#!/usr/bin/env python3
"""m2_c55_zerocount.py -- the zero count n(x) = #{gamma : 0 < gamma <= 2*pi*x}, MEASURED from
mpmath's zetazero with the bracketing ordinates printed, never cited from a table.

c54's amendment 1 requires the registered rules to be evaluated at the MEASURED n.  This cycle's
two windows are x = 25 (the extrapolation sealed unrun in c54's prereg) and x = 22 (the window
that discriminates models I and X).  c54's three windows are re-measured here as a CHECK against
c54's own published m2_c54_zerocount.json -- a re-measurement that disagreed would be a finding.

usage: m2_c55_zerocount.py   ->  m2_c55_zerocount.json
"""
import json, os
from mpmath import mp, zetazero, pi

HERE = os.path.dirname(os.path.abspath(__file__))
C54 = os.path.abspath(os.path.join(HERE, "..", "c54"))
XS = (13, 17, 19, 22, 25, 28)

mp.dps = 30
out = {}
for x in XS:
    T = 2 * pi * x
    k = 0
    while True:
        g = zetazero(k + 1).imag
        if g > T:
            break
        k += 1
    out[str(x)] = dict(T_star=mp.nstr(T, 20), n=k,
                       gamma_k=mp.nstr(zetazero(k).imag, 20),
                       gamma_k_plus_1=mp.nstr(zetazero(k + 1).imag, 20))
    print("x=%2d  n = %2d   gamma_n = %s < T* = %s < gamma_{n+1} = %s"
          % (x, k, mp.nstr(zetazero(k).imag, 15), mp.nstr(T, 15),
             mp.nstr(zetazero(k + 1).imag, 15)), flush=True)

check = {}
c54f = os.path.join(C54, "m2_c54_zerocount.json")
if os.path.exists(c54f):
    prev = json.load(open(c54f))["counts"]
    for k_ in prev:
        if k_ in out:
            check[k_] = dict(c54=prev[k_]["n"], c55=out[k_]["n"], agree=prev[k_]["n"] == out[k_]["n"])
json.dump(dict(counts=out, recheck_against_c54=check,
               convention="n = #{gamma : 0 < gamma <= 2*pi*x}, MEASURED from mpmath zetazero with "
                          "the bracketing ordinates printed, never cited"),
          open(os.path.join(HERE, "m2_c55_zerocount.json"), "w"), indent=1)
print("recheck against c54:", check)
