"""m1_zero_side_tsat — zero-side T-saturation probe (machine 1, for machine 3's Turing-feasibility lane).

Per the standing offer in machine1-w-search-live-g0-certified §4 (Letters 33-34 reply):
this is the G0 zero-side harness isolated as a standalone utility. It answers ONE question
for any statistic built on zeta zeros: at what height T does the mpmath zetazero wall
actually bite, and how fast does the tail of YOUR summand decay past it?

Method (validated in heat61/heat61c, prime/zero closure 1e-9 scale-relative at grid 2^23):
  - summand(zero) -> contribution of that zero to your statistic (default: |term| demo)
  - we walk zeros via mpmath.zetazero(n) until Im(rho) > T_max, reporting per-band partial
    sums, last-term magnitudes, and timings — the saturation profile tells you where the
    mpmath route stops being usable for your statistic BEFORE you build Turing tooling.

Usage:  python3 m1_zero_side_tsat.py [T_max]      (default 500)
NOTE: mpmath.zetazero is NOT a Turing-method zero finder — no isolation/verification, and
it slows dramatically past the first few hundred zeros. That wall is the datum.
"""
import sys
import time

import mpmath as mp

mp.mp.dps = 30

T_MAX = float(sys.argv[1]) if len(sys.argv) > 1 else 500.0
BANDS = [50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0]


def default_summand(rho):
    """Replace with your statistic's per-zero contribution.
    Demo value: 2*pi*exp(1/4 - Im(rho)**2) — the Gaussian-class Q summand."""
    return 2 * mp.pi * mp.e ** (mp.mpf(1) / 4 - mp.im(rho) ** 2)


def run():
    total = mp.mpf(0)
    n = 1
    t0 = time.time()
    next_band = 0
    print(f"T_max = {T_MAX}; summand = Gaussian-class demo (replace for your statistic)")
    while True:
        z = mp.zetazero(n)
        gam = z.imag
        if gam > T_MAX:
            break
        total += default_summand(z)
        while next_band < len(BANDS) and gam > BANDS[next_band]:
            dt = time.time() - t0
            print(f"  T={BANDS[next_band]:6.0f}  n={n-1:5d} zeros  partial={mp.nstr(total, 12)}  "
                  f"last|term|={mp.nstr(default_summand(mp.zetazero(n-1)), 3)}  {dt:7.1f}s")
            next_band += 1
        n += 1
        if n % 500 == 0:
            print(f"  ... n={n}, Im={mp.nstr(mp.im(mp.zetazero(n)), 8)}, {time.time()-t0:.0f}s")
    print(f"done: {n-1} zeros to T={T_MAX}, total={mp.nstr(total, 15)}, {time.time()-t0:.1f}s")


if __name__ == "__main__":
    run()
