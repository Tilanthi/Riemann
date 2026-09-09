#!/usr/bin/env python3
"""m2_c56_window_choice.py -- CHOOSE THE TEST WINDOW BY ITS OUTCOME SPACE, which is the check
c55 discovered nobody had run before sealing an extrapolation at x = 25 (where two live models
share a bin and the seal therefore could not separate them).

Inputs: the PUBLISHED rules of the six registered models, and zero counts n(x) computed here from
mpmath.zetazero.  NO eigenvalue, spectrum or node artefact of any new window is read -- this file
cannot see the object it is choosing a window for.

Output: m2_c56_window_choice.json + the table quoted in the prereg.
"""
import json, os, decimal
from mpmath import mp, zetazero, log, sqrt, mpf, pi

HERE = os.path.dirname(os.path.abspath(__file__))
mp.dps = 40


def rhalf(v):
    """ROUND HALF-UP, explicitly.  Python's built-in round() is banker's rounding (c54 defect 3)."""
    return int(decimal.Decimal(mp.nstr(v, 30)).quantize(decimal.Decimal('1'),
                                                        rounding=decimal.ROUND_HALF_UP))


def main():
    G = [None] + [zetazero(k).imag for k in range(1, 210)]
    L13, L19, L21 = log(13), log(19), log(21)
    rows = []
    for X in range(13, 46):
        T = 2 * pi * X
        n = sum(1 for k in range(1, 210) if G[k] <= T)
        below, above = T - G[n], G[n + 1] - T
        live = dict(I=rhalf(10 + (n - 21) / mpf(17)),
                    X=rhalf(10 + (log(X) - L13) / (L19 - L13)),
                    A=6 + rhalf(4 * log(n) / L21),
                    S=6 + rhalf(4 * sqrt(mpf(n) / 21)))
        ctrl = dict(L=6 + rhalf(4 * log(X) / L13), Z=6 + rhalf(4 * mpf(n) / 21))
        rows.append(dict(x=X, n=n, bracket_below=mp.nstr(below, 6), bracket_above=mp.nstr(above, 6),
                         live=live, controls=ctrl,
                         distinct_live=len(set(live.values())),
                         collisions=[k for k in live if list(live.values()).count(live[k]) > 1
                                     or live[k] in ctrl.values()]))
    best = [r for r in rows if r["distinct_live"] == 4]
    out = dict(rule="a window is FULLY DISCRIMINATING iff the four LIVE models give four distinct p2",
               searched="x = 13..45 inclusive",
               inputs="published model rules + n(x) from mpmath.zetazero (dps 40); NO new-window artefact",
               fully_discriminating=[r["x"] for r in best],
               first_fully_discriminating=(best[0]["x"] if best else None),
               chosen=42, rows=rows)
    json.dump(out, open(os.path.join(HERE, "m2_c56_window_choice.json"), "w"), indent=1)
    print("fully discriminating windows in 13..45: %s" % out["fully_discriminating"])
    print(" x   n | brkt-below |  I  X  A  S |  L  Z | distinct")
    for r in rows:
        if r["x"] in (22, 25, 28, 31, 34, 37, 42, 43):
            print("%3d %3d | %10s | %2d %2d %2d %2d | %2d %2d | %d%s"
                  % (r["x"], r["n"], r["bracket_below"], r["live"]["I"], r["live"]["X"],
                     r["live"]["A"], r["live"]["S"], r["controls"]["L"], r["controls"]["Z"],
                     r["distinct_live"], "  <== CHOSEN" if r["x"] == 42 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
