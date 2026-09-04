#!/usr/bin/env python3
"""machine1_heat72m_verify — one-round-trip localiser for the L123 M64/s3
discrepancy. Loads machine1's persisted RAW-basis matrices (mpmath quad at
dps 30, conventions verbatim from the heat72k export spec: U_a(rho) =
int f_a e^{rho t} dt over f_a's own breakpoint set; G[a,b] = int f_a f_b
over the union set; K = sum_{0<Im rho<=200} 2 Re[U_a conj(U_b)]).

Three checks, cheapest first:
  1. K-rebuild: recompute K from the persisted U; must equal persisted K
     to dps-30 (checks that K is exactly the outer-product sum of U).
  2. lambda_min: scipy.linalg.eigh(K, G) generalized solve in float64 --
     QUICK SCREEN ONLY. The certified route at high cond is the mpmath
     Cholesky congruence (`mp_consolve`, check 3): the float64 pencil
     solve's bottom-eigenvalue error scales eps*cond(G)^2 (~1.6e-6 at
     cond 9.1e4, ~2.4e-5 at cond 4.0e5 -- measured on s3/s1 M64), so
     float64 is sufficient to cond ~1e4 and misleading beyond.
     machine1's first hand-rolled mpmath paths (manual Linv recursion and
     symmetrised G^-1K) both returned garbage while passing a 2x2
     closed-form check -- see traps #96/#97/#98 in machine1-trap-register.
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
# CORRECTED raw-basis anchors (dps-40 two-route; L123r3 letter). The old
# float64-GS anchors are kept as RETRACTED references: s3_M64 9.277105888489333e-10
# (4.6% low), s1_M64 1.181309234334259e-10 (9.1e-6 low).
ANCH = {"s3_M8": 3.944935640028498e-05,   # heat63b grid-GS, triple-confirmed
        "s3_M64": 9.70653446567550195e-10,  # corrected dps-40; = m3 L123 to 5.8e-15
        "s1_M8": 1.1761206927492675e-05,
        "s1_M64": 1.18132670405788889e-10}  # corrected dps-40; = m3 L123 to 4.2e-14
M3 = {"s1_M8": 1.1761206927487696e-05,
      "s1_M64": 1.1813267040579388e-10,
      "s3_M64": 9.7065344656754458e-10}


def mp_consolve(Krows, Grows):
    """Certified dps-30 pencil solve: Cholesky congruence A = L^-1 K L^-T
    via columnwise lu_solve (traps #96/#97/#98 discipline: element-
    assignment RHS construction, sorted-list eigenvalue wrap)."""
    from mpmath import mp, mpf, matrix, lu_solve, cholesky
    mp.dps = 30
    m = len(Krows)
    K = matrix([[mpf(x) for x in r] for r in Krows])
    G = matrix([[mpf(x) for x in r] for r in Grows])
    L = cholesky(G)
    Y = matrix(m, m)
    for j in range(m):
        v = matrix(m, 1)
        for i in range(m):
            v[i, 0] = K[i, j]
        col = lu_solve(L, v)
        for i in range(m):
            Y[i, j] = col[i, 0]
    A = matrix(m, m)
    for j in range(m):
        v = matrix(m, 1)
        for i in range(m):
            v[i, 0] = Y[j, i]
        col = lu_solve(L, v)
        for i in range(m):
            A[i, j] = col[i, 0]
    for i in range(m):
        for j in range(i + 1, m):
            A[i, j] = A[j, i] = (A[i, j] + A[j, i]) / 2
    return sorted(mp.eigsy(A, eigvals_only=True))[0]

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
        # 2. float64 generalized solve (quick screen)
        ev = eigh(K, G, eigvals_only=True)
        print(f"  lambda_min (scipy eigh)  = {ev[0]:.16e}  [screen; eps*cond^2 floor]")
        # 3. certified mpmath congruence solve
        lmp = mp_consolve(blk["K"], blk["G"])
        print(f"  lambda_min (mp congr.)   = {float(lmp):.16e}  [certified at high cond]")
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
