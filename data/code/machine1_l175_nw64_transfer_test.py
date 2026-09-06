"""m1 L175: the N_w 16 -> 64 transfer test routed to m1 by BEAST c33 §3.

Question: does raising the circle N_w 16 -> 64 (r_w unchanged at 0.05) move my L174
circle-stage ceiling as m2's aliasing formula predicts — (2 r_w)^{N_w}: 1e-16 at
N_w=16, 1e-64 at N_w=64 — or does it not move (formula wrong, or my ~1e-15 ceiling
is something else)?

Design (trap #S13/#138: witness at the stage boundary, in the same process):
  step 1  w_coeffs(0) at NW=16 must reproduce the committed v3.stdout WIT-1 circle
          values c2 = -18.816779288625 - 1.88e-69j, c4 = -279.180914118...,
          c6 = -1382.36060778...  (reproduction = the witness that config and
          environment match the frozen run; abort if not).  Tolerances are
          calibrated to what the artefact carries: the WIT-1 prints stop at 12
          decimals, so they are checked at 1e-11 rel, and c2 additionally against
          the g10 line's 28 s.f. at 1e-20 rel.  Attempt 1 of this test falsely
          aborted by demanding 1e-30 against the 12-decimal print (rel 1.913e-14
          = exactly the print rounding); its .out is committed as the receipt.
  step 2  same call with NW=64.  Report |c_k(64) - c_k(16)| vs the formula's
          predicted aliasing magnitude at N_w=16, (2 r_w)^16 = 1e-16.

Output to stdout only.  Nothing scored; a measurement answering a routed ask.
"""
import importlib.util
import os
import time

from mpmath import mp, mpf, mpc, pi, cos, sin

HERE = os.path.dirname(os.path.abspath(__file__))
T0 = time.time()
mp.dps = 70          # matches v3's 60+10 working precision

_spec = importlib.util.spec_from_file_location(
    "v3mod", os.path.join(HERE, "machine1_der_route_a_b_a3_v3.py"))
v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v3)

# v3's main() is what sets mp.dps = MPDPS_RUN + GUARD (its line 177); importing the
# module alone leaves a HIGHER ambient dps (130) that reaches the zeta tail cutoff and
# moves c_k at the 1e-14 level -- the first launch of this test aborted at the step-1
# witness exactly there (rel 1.9e-14).  Replicate main()'s setting so both arms of the
# transfer test run at the committed run's dps (70), DER_* env unset -> committed config.
mp.dps = v3.MPDPS_RUN + v3.GUARD

print(f"# m1 L175 N_w transfer test  r_w={mp.nstr(v3.RW,4)}  dps={mp.dps}"
      f"  (module defaults: N_w={v3.NW}, KX={v3.KX}, MPDPS_RUN={v3.MPDPS_RUN},"
      f" GUARD={v3.GUARD})")

# committed v3.stdout WIT-1 circle values at e=0 (parse from the committed file;
# standalone sign tokens like the "-" in "(-a - bj)" are filtered out)
import re
def _nums(txt):
    toks = re.findall(r"[-0-9.e+]+", txt)
    return [t for t in toks if re.search(r"\d", t)]

COMMITTED = {}
G10 = None
with open(os.path.join(HERE, "..", "machine1_der_route_a_b_a3_v3.stdout")) as fh:
    for line in fh:
        if line.startswith("WIT-1 circle   c2 at e=0"):
            nums = _nums(line.split(":", 1)[1])
            COMMITTED["c2"] = mpc(mpf(nums[0]), -mpf(nums[1]))   # line prints "(-re - im j)"
        if line.startswith("WIT-1 circle   c4/c6 at e=0"):
            nums = _nums(line.split(":", 1)[1])
            COMMITTED["c4"] = mpc(mpf(nums[0]), mpf(nums[1]))
            COMMITTED["c6"] = mpc(mpf(nums[2]), mpf(nums[3]))
        if line.startswith("g10 ="):
            # full-precision (28 s.f.) c2-equivalent from the committed series table;
            # split off the "g10 =" prefix first -- attempt 2 of this test fed the
            # whole line to _nums and the "10" of the name became the real part
            # (receipt committed as ..._attempt2_parsebug.out)
            nums = _nums(line.split("=", 1)[1])
            G10 = mpc(mpf(nums[0]), mpf(nums[1]))

print(f"# committed c2 = {mp.nstr(COMMITTED['c2'], 18)}   (12-decimal print)")
if G10 is not None:
    print(f"# committed g10 (28 s.f., same quantity) = {mp.nstr(G10, 18)}")
print(f"# committed c4 = {mp.nstr(COMMITTED['c4'], 18)}")
print(f"# committed c6 = {mp.nstr(COMMITTED['c6'], 18)}")

# WITNESS TOLERANCES, calibrated to what the committed artefact carries:
#   c2 vs g10 (28 s.f.):        1e-20 rel  (attempt 1 of this test falsely aborted by
#                               demanding 1e-30 against the 12-decimal WIT-1 print --
#                               the .out of that attempt is committed alongside;
#                               tolerance tighter than the print is a false abort)
#   c2/c4/c6 vs 12-dec prints:  1e-11 rel  (print rounding at 12 decimals is < 1e-12
#                               rel for |c| <= 1382; 1e-11 separates cleanly)
TOL_PRINT = mpf("1e-11")
TOL_G10 = mpf("1e-20")

assert v3.NW == 16, f"expected module default NW=16, got {v3.NW}"
c16 = v3.w_coeffs(mpf(0))
print(f"\n# step 1: NW=16 reproduction  [t={time.time()-T0:.0f}s]")
failed = False
for nm, got, want in (("c2", c16[1], COMMITTED["c2"]),
                      ("c4", c16[2], COMMITTED["c4"]),
                      ("c6", c16[3], COMMITTED["c6"])):
    d = got - want
    print(f"   {nm}: {mp.nstr(got, 18)}   diff-vs-committed-print {mp.nstr(d, 4)}"
          f"   (rel {mp.nstr(abs(d / want), 4)})")
    if abs(d / want) > TOL_PRINT:
        print(f"   ABORT: {nm} does not reproduce the committed NW=16 value")
        failed = True
if G10 is not None:
    dg = c16[1] - G10
    print(f"   c2 vs committed g10 (28 s.f.): diff {mp.nstr(dg, 4)}"
          f"   (rel {mp.nstr(abs(dg / G10), 4)})")
    if abs(dg / G10) > TOL_G10:
        print("   ABORT: c2 does not reproduce the committed full-precision g10")
        failed = True
if failed:
    raise SystemExit(1)
print("#   witness PASSED (c2 to 1e-20 vs g10; all three to 1e-11 vs the prints)")

v3.NW = 64
c64 = v3.w_coeffs(mpf(0))
print(f"\n# step 2: NW=64 (same r_w, same dps)  [t={time.time()-T0:.0f}s]")
for nm, j in (("c2", 1), ("c4", 2), ("c6", 3)):
    d = c64[j] - c16[j]
    print(f"   {nm}: {mp.nstr(c64[j], 18)}")
    print(f"        shift 16->64 = {mp.nstr(d, 6)}   (rel {mp.nstr(abs(d / c16[j]), 4)})")
print(f"\n# formula (2 r_w)^N_w at r_w=0.05: N=16 -> {mp.nstr((2*v3.RW)**16, 4)}"
      f"   N=64 -> {mp.nstr((2*v3.RW)**64, 4)}")
print("# reading: if the shifts sit at ~1e-15..1e-16 rel, the N=16 aliasing is the"
      " formula's size and L174's ceiling attribution is CONFIRMED as to mechanism;")
      # noqa
print("# if they sit at ~1e-7, the circle floor is 8 orders larger than the formula;")
print("# if they sit below 1e-25, N=16 aliasing was already negligible and L174's"
      " ~1e-15 ceiling needs a different owner.")
print(f"\n# wall {time.time()-T0:.0f}s; no proof claim; measurement, nothing scored")
