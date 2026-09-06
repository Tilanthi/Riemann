#!/usr/bin/env python3
"""m1 -- fd_weights root-cause probe for the der-route v1/v2 failure (L174 s1).

Family 7 of the probe log.  Locates the corruption that families 0-5 chased:
fd_weights solved its Vandermonde system TRANSPOSED -- Am[i,j] = offs[i]**j
returns a solution indexed by POWER, but the consumer zips it with the offsets
as if indexed by NODE.  This script receipts, at dps 50:

  1. the buggy order-0 weights vs the fixed ones (fixed = exactly e_center);
  2. a polynomial self-test (orders 0 and 1 on t^3 + 2 t^2 + 5 t + 7): the
     buggy weights give 0.6083 where the truth is 5; the fixed system is exact;
  3. the ANALYTIC REPRODUCTION of v1's corrupted g10: the healthy stencil
     values c2(HE o) ~ c2(0) + (dc2/de) HE o (c2(0) = -18.816779288625 from
     families 3-4; slope -486.358 measured from v2's own per-node prints,
     nodes -4/+4) pushed through the BUGGY order-0 weights gives +1.7357e-9
     against v1's observed +1.7369932158316149e-9 -- the corruption is the
     constant-annihilating weights passing the e-slope leakage of the stencil.

Nothing here is scored; deterministic linear algebra at dps 50.
"""
from mpmath import mp, mpf

mp.dps = 50
HE = mpf("1e-9")
C2_0 = mpf("-18.816779288625")       # families 3/4: circle + manual DFT agree
SLOPE = mpf("-486.358")              # measured from v2's receipted node prints
V1_G10 = mpf("1.7369932158316149e-9")  # v1 full.stdout, the corrupted channel


def fd_weights(order, npts, buggy):
    offs = list(range(-(npts // 2), npts // 2 + 1))
    N = len(offs)
    Am = mp.matrix(N, N)
    if buggy:
        for i, o in enumerate(offs):
            for j in range(N):
                Am[i, j] = mpf(o) ** j          # v1/v2: wrong orientation
    else:
        for i in range(N):
            for j, o in enumerate(offs):
                Am[i, j] = mpf(o) ** i          # FIX-3: moment system
    bv = mp.matrix(N, 1)
    bv[order] = mp.factorial(order)
    x = mp.lu_solve(Am, bv)
    return offs, [x[i] for i in range(N)]


def poly3(t):
    return t ** 3 + 2 * t ** 2 + 5 * t + 7


def main():
    print("fd_weights root-cause probe (dps %d)" % mp.dps)

    offs, w_bug = fd_weights(0, 9, True)
    _, w_fix = fd_weights(0, 9, False)
    print("order-0 buggy :", [mp.nstr(w, 12) for w in w_bug])
    print("order-0 fixed :", [mp.nstr(w, 12) for w in w_fix])
    exp = [mpf(0)] * 9
    exp[4] = mpf(1)
    print("fixed == e_center:", w_fix == exp,
          "| buggy sum w_o:", mp.nstr(mp.fsum(w_bug), 8),
          "| buggy sum w_o*o:", mp.nstr(mp.fsum(w * o for o, w in zip(offs, w_bug)), 8))

    for order in (0, 1):
        truth = {0: mpf(7), 1: mpf(5)}[order]
        _, wb = fd_weights(order, 9, True)
        _, wf = fd_weights(order, 9, False)
        eb = mp.fsum(w * poly3(mpf(o)) for o, w in zip(offs, wb))
        ef = mp.fsum(w * poly3(mpf(o)) for o, w in zip(offs, wf))
        print("poly self-test order %d: buggy %s (err %s) | fixed %s (err %s) | truth %s"
              % (order, mp.nstr(eb, 10), mp.nstr(eb - truth, 4),
                 mp.nstr(ef, 12), mp.nstr(ef - truth, 4), mp.nstr(truth, 4)))

    tab = {o: C2_0 + SLOPE * HE * o for o in offs}
    rec = mp.fsum(w * tab[o] for o, w in zip(offs, w_bug))
    print("analytic reproduction: healthy tab through BUGGY order-0 weights -> g10 = %s"
          % mp.nstr(rec, 12))
    print("v1 observed g10 = %s  | ratio rec/v1 = %s  (rel dev %s)"
          % (mp.nstr(V1_G10, 12), mp.nstr(rec / V1_G10, 8),
             mp.nstr((rec - V1_G10) / V1_G10, 4)))
    print("note: rel dev -2.1e-7 is the rounding of the 6-s.f. slope literal; the")
    print("      buggy weights annihilate the constant to 5.1e-57 and pass only")
    print("      slope * HE * (sum w_o o) with sum w_o o = -1/280 -- the")
    print("      reconstruction is exact to the literal's precision.")


if __name__ == "__main__":
    main()
