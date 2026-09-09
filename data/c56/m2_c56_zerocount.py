#!/usr/bin/env python3
"""m2_c56_zerocount.py -- n(42) = #{gamma <= 2*pi*42}, MEASURED, with both bracket margins printed,
because c55's x = 22 window had a 0.114 margin and that had to be disclosed as a weakness."""
import json, os
from mpmath import mp, zetazero, pi

HERE = os.path.dirname(os.path.abspath(__file__))
mp.dps = 40
X = 42
T = 2 * pi * X
n = 0
while zetazero(n + 1).imag <= T:
    n += 1
lo, hi = zetazero(n).imag, zetazero(n + 1).imag
out = dict(x=X, T_star=mp.nstr(T, 25), n=n,
           gamma_n=mp.nstr(lo, 25), gamma_n_plus_1=mp.nstr(hi, 25),
           bracket_below=mp.nstr(T - lo, 10), bracket_above=mp.nstr(hi - T, 10),
           method="mpmath.zetazero, dps 40, strict inequality gamma <= T*",
           comparison="c55 disclosed x=22 as its narrowest bracket at 0.114 below T*")
json.dump(out, open(os.path.join(HERE, "m2_c56_zerocount.json"), "w"), indent=1)
print("n(%d) = %d   T*=%s  gamma_n=%s (below %s)  gamma_{n+1}=%s (above %s)"
      % (X, n, out["T_star"], out["gamma_n"], out["bracket_below"], out["gamma_n_plus_1"],
         out["bracket_above"]))
