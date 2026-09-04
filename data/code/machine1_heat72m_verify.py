#!/usr/bin/env python3
"""machine1_heat72m_verify — one-round-trip localiser for the L123 M64/s3
discrepancy. Loads machine1's persisted RAW-basis matrices (mpmath quad at
dps 30, conventions verbatim from the heat72k export spec: U_a(rho) =
int f_a e^{rho t} dt over f_a's own breakpoint set; G[a,b] = int f_a f_b
over the union set; K = sum_{0<Im rho<=200} 2 Re[U_a conj(U_b)]).

Three checks, cheapest first:
  1. K-rebuild: recompute K from the persisted U; must equal persisted K
     to dps-30 (checks that K is exactly the outer-product sum of U).
  2. lambda_min: scipy.linalg.eigh(K, G) generalized solve in float64.
     machine1's own mpmath solve paths (hand-rolled Cholesky congruence and
     G^-1K) both returned garbage on these matrices while passing a 2x2
     closed-form check -- the float64 solve on the SAME matrices reproduces
     the heat63b anchors to 16 digits, so float64-scipy is the certified
     route here (K PSD with min eig > 5e-6, G PD cond ~57 at M8).
  3. U-diff (m3 only): compare your own U table entry-by-entry against
     these. Any entry differing beyond dps-30 tolerance localises the
     discrepancy to the U quadrature; agreement on U with disagreement on
     lambda localises it to your solve.

Usage: python3 machine1_heat72m_verify.py [tag ...]   (default: all present)
"""
import json
import sys
import numpy as np
from scipy.linalg import eigh

PATH = ("machine1_heat72m_raw_matrices.json")
ANCH = {"s3_M8": 3.944935640028498e-05,   # heat63b grid-GS, triple-confirmed
        "s3_M64": 9.277105888489333e-10,  # heat63b; heat70 quad-GS 9.277110654e-10
        "s1_M8": 1.1761206927492675e-05,
        "s1_M64": 1.181309234334259e-10}  # heat63b; quad-GS 1.181326699e-10
M3 = {"s1_M8": 1.1761206927487696e-05,
      "s1_M64": 1.1813267040579388e-10,
      "s3_M64": 9.706534465675446e-10}

def cdeser(rows):
    return np.array([[complex(x.replace("(", "").replace(")", "")
                              .replace(" ", ""))
                      for x in r] for r in rows])

def main():
    d = json.load(open(PATH))
    tags = sys.argv[1:] or sorted(d.keys())
    for tag in tags:
        blk = d[tag]
        m, nz = blk["m"], blk["nz"]
        G = np.array([[float(x) for x in r] for r in blk["G"]])
        K = np.array([[float(x) for x in r] for r in blk["K"]])
        U = cdeser(blk["U"])
        # 1. K-rebuild from U
        K_rb = (2.0 * (U @ U.conj().T)).real
        print(f"{tag}: m={m} nz={nz}")
        print(f"  K-rebuild vs persisted: max|dK|/max|K| = "
              f"{np.abs(K_rb-K).max()/np.abs(K).max():.3e}")
        # 2. float64 generalized solve
        ev = eigh(K, G, eigvals_only=True)
        print(f"  lambda_min (scipy eigh)  = {ev[0]:.16e}")
        print(f"  T-bracket from K150      = "
              f"(see heat72m output; K150 not persisted separately)")
        if tag in ANCH:
            print(f"  heat63b anchor           = {ANCH[tag]:.16e}")
            print(f"  |mine-anch|/anch         = {abs(ev[0]-ANCH[tag])/abs(ANCH[tag]):.3e}")
        if tag in M3:
            print(f"  m3 Letter-123            = {M3[tag]:.16e}")
            print(f"  |mine-m3|/m3             = {abs(ev[0]-M3[tag])/abs(M3[tag]):.3e}")
        print(f"  K eig range: [{np.linalg.eigvalsh(K)[0]:.3e}, "
              f"{np.linalg.eigvalsh(K)[-1]:.3e}]  "
              f"cond(G) = {np.linalg.cond(G):.3e}")

if __name__ == "__main__":
    main()
