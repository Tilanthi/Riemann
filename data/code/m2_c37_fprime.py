"""machine2 CYCLE 37 -- score P1. Re-serialise f'(D*) at FULL working precision.

The frozen cycle-34 runner is IMPORTED, not edited: root_at() is used verbatim.  Only the
SERIALISATION changes -- which is precisely the object under test.
"""
import sys, time, mpmath as mp
sys.path.insert(0, "/workspace/rh/cycle34")
sys.path.insert(0, "/workspace/rh/cycle21")
from m2_c34_dstar_refine import root_at, LIT   # frozen, imported not edited
import hashlib
src = open("/workspace/rh/cycle34/m2_c34_dstar_refine.py","rb").read()
print("frozen runner sha256 =", hashlib.sha256(src).hexdigest())
print("LIT (carried literal) =", LIT)

mp.mp.dps = 200
res = {}
for dps in (130, 150):
    t0=time.time(); D, r, fp, wall = root_at(dps)
    res[dps]=(D,r,fp)
    print(f"\ndps={dps}  [{wall:.0f}s]")
    print("  f'(D*) as PUBLISHED   nstr(fp,12) :", mp.nstr(fp,12))
    print("  f'(D*) FULL PRECISION nstr(fp,120):", mp.nstr(fp,120))
    print("  residual              nstr(|r|,6) :", mp.nstr(abs(r),6))
d = res[130][2]-res[150][2]
rel = abs(d)/abs(res[150][2])
print("\n## P1 SCORING")
print("  f'_130 - f'_150            =", mp.nstr(d, 12))
print("  |f'_130 - f'_150| / |f'|   =", mp.nstr(rel, 12))
print("  band was [1e-92, 1e-78], point 3e-86")
print("  VERDICT:", "CONFIRMED" if mp.mpf("1e-92") <= rel <= mp.mpf("1e-78") else "FALSIFIED")
print("  first-12-figure reproduction:", mp.nstr(res[130][2],12), mp.nstr(res[150][2],12))
hidden = -mp.log10(rel) - 12
print("  digits HIDDEN by the published 12-figure print: %.1f" % float(hidden))
# what the PUBLISHED string is worth
halfulp = mp.mpf(5)*mp.mpf(10)**(-12)
print("  half-ulp of published 'f'(D*) = -37.4819713608' (12 s.f.) = %s relative"
      % mp.nstr(halfulp/1, 3))
print("\n## remedy: f'(D*) re-serialised at the resolution actually achieved (dps-150 determination)")
print("   f'(D*) =", mp.nstr(res[150][2], 90))
print("   error bar on that value (|f'_130 - f'_150|) =", mp.nstr(abs(d),6),
      "abs /", mp.nstr(rel,6), "rel")
