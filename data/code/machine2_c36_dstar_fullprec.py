"""machine2 CYCLE 36, P1 -- re-serialise my own dps-150 D* at FULL WORKING PRECISION and
difference it against m3's published dps-150 Newton-refined D_new (m3-L171, f3c8e755).

The c34 script printed nstr(D, 80).  That 80-digit string is what m3 compared against, so m3's
reported 6.18e-81 is read against a half-ulp of ~5e-81: the ADDENDUM-1 print-width defect changed
sides.  Nothing here is new physics -- it is the SAME root find, re-run with the serialisation
fixed.  The frozen c34 code is IMPORTED, not edited.
"""
import sys
import time

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
sys.path.insert(0, "/workspace/rh/cycle34")
from m2_c34_dstar_refine import root_at  # noqa: E402  (frozen c34 code, imported not edited)

# m3-L171 data/results/m3_L171_Dstar_newton_refine_output.txt, verbatim
M3_DNEW = (
    "0.141733239663887191395415685084185023623144561955016655942866603946659042189707430"
    "875932704544153491448859401071291155704123242008525016251392377082433"
)
# my own c34 published string (data/... machine2 c34 letter), verbatim -- the 80-digit nstr
M2_PUBLISHED_80 = "0.14173323966388719139541568508418502362314456195501665594286660394665904218970743"

if __name__ == "__main__":
    mp.mp.dps = 400  # ambient, so every mpf(str) below is built at more precision than any input
    t0 = time.time()

    results = {}
    for dps in [130, 150]:
        D, res, fp, wall = root_at(dps)
        results[dps] = D
        print(f"dps={dps}: residual={mp.nstr(abs(res), 6)}  f'={mp.nstr(fp, 12)}  "
              f"residual/|f'|={mp.nstr(abs(res / fp), 6)}  [{wall:.0f}s]", flush=True)

    D150 = results[150]
    D130 = results[130]
    print(f"\n## my D*, dps=150 root find, computed at working dps=175 (root_at uses dps+25),")
    print(f"## SERIALISED AT 175 DIGITS -- the full working precision, per my own ADDENDUM 1:")
    print("  " + mp.nstr(D150, 175, strip_zeros=False), flush=True)
    print(f"\n## certified portion: the dps130-vs-dps150 spread is the error bar")
    print(f"  D*(130) - D*(150) = {mp.nstr(D130 - D150, 6)}")

    m3 = mp.mpf(M3_DNEW)
    pub80 = mp.mpf(M2_PUBLISHED_80)

    print("\n## P1 -- the measurement")
    d_abs = D150 - m3
    d_rel = d_abs / D150
    print(f"  D*(m2, full precision) - D_new(m3)  ABS = {mp.nstr(d_abs, 12)}")
    print(f"  D*(m2, full precision) - D_new(m3)  REL = {mp.nstr(d_rel, 12)}")
    print(f"  PREREG P1 band: sign POSITIVE, rel in [1.0e-120, 6.0e-119], centre 7.808e-120")

    print("\n## the serialisation arithmetic (DERIVATION, not a prediction)")
    print(f"  my published 80-digit string - my full-precision value = "
          f"{mp.nstr(pub80 - D150, 6)}  (this is my own rounding error)")
    print(f"  |m3 - my 80-digit string| / D  = {mp.nstr(abs(m3 - pub80) / D150, 6)}   "
          f"<- the 6.18e-81 m3 reported")
    print(f"  half-ulp of an 80-s.f. string at D~0.1417, relative = "
          f"{mp.nstr(mp.mpf('5e-81') / D150, 6)}")
    print(f"\n[{time.time() - t0:.0f}s] done")
