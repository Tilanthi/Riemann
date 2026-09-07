# m3-L184 build — odd-parity block, derived from scratch (BEAST's c46_parity.py docstring read as a
# mathematical SPECIFICATION only -- basis definition and the claim that "the sign pattern is the
# only difference" from the even block -- not as code; no line of theirs imported or copied).

## Basis

psi_k(s) = sqrt(2/L) sin(w_k s), w_k = 2 pi k / L, k = 1..N (no k=0 term -- sin(0)=0 is trivial).
Support [-L/2, L/2], zero elsewhere. Orthonormal on that interval (standard Fourier sine basis).

## Evenness of g_jk^odd(t) in t (re-derived, not assumed)

g_jk(-t) = INT psi_j(s) psi_k(s-t) ds; substitute s=-u (whole-line integral, sign flips cancel):
= INT psi_j(-u) psi_k(-u-t) du = INT [-psi_j(u)][-psi_k(u+t)] du = INT psi_j(u)psi_k(u+t) du = g_jk(t).
Two sign flips (odd x odd) cancel -- g_jk^odd(t) is STILL exactly even in t, same conclusion as the
even block via the same style of argument, now checked for sines specifically.

## g_jk^odd(t) closed form, t in [0,L), by direct integration (own derivation, product-to-sum)

sin(w_j s) sin(w_k(s+t)) = (1/2)[cos((w_j-w_k)s - w_k t) - cos((w_j+w_k)s + w_k t)]
-- SAME two raw integrals (over the same overlap range) as already appear in the even-block
derivation (data/code/m3_L177_build/basis.py), since ∫cos(As+phase)ds does not care which product-
to-sum identity produced it. Reusing those two closed forms directly:

  j != k, A = w_j-w_k, B = w_j+w_k:
    g_jk^odd(t) = ((-1)^{j+k}/L) * { [sin(w_k t)-sin(w_j t)]/A + [sin(w_j t)+sin(w_k t)]/B }
  (even block has the same expression with a MINUS in front of the second bracket -- the two
   integrals combine with a "-" for cos*cos and a "+" for sin*sin, everything else identical)

  j == k:
    g_kk^odd(t) = (1/L) * [ cos(w_k t)(L-t) + sin(w_k t)/w_k ]
  (even block: same with the sin(w_k t)/w_k term subtracted, not added)

Both checked at t=0: g_jk^odd(0) = 0 (j!=k), g_kk^odd(0) = 1 -- orthonormality, exact, matches the
basis being orthonormal by construction.

CROSS-CHECK: this "only a sign flip differs" structure was independently re-derived here, not copied
from BEAST's docstring claim -- it falls out of the raw trig algebra on its own. Genuine (if minor)
independent confirmation of their own stated pattern, via a different route (direct real-space
integration vs their Id/Ie/Sd/Se parameterisation).

## psi_hat_k(r) (needed for the pole term), by direct integration

psi_hat_k(r) = INT_{-L/2}^{L/2} sin(w_k s) e^{irs} ds. The cos(rs) part of e^{irs} pairs with an odd
integrand (sin x cos) and vanishes over the symmetric interval; only the sin(rs) part survives:

  psi_hat_k(r) = i * sqrt(2/L) * (-1)^k * sin(rL/2) * 2 w_k / (r^2 - w_k^2)

-- purely imaginary and ODD in r (psi_hat_k(-r) = -psi_hat_k(r)), as expected for the FT of a real
odd function, and entire (removable singularities at r=+-w_k, same mechanism as the even block).

## The pole term picks up an extra minus sign relative to the even block

General fact (parity-independent, re-derived directly, not assumed): the Fourier transform of
g_jk(t) = INT psi_j(s)psi_k(s+t) ds is  g_hat_jk(r) = psi_hat_j(-r) * psi_hat_k(r)  (shown by
swapping the order of integration; holds for ANY basis, even or odd).

For the EVEN block psi_hat_j(-r) = +psi_hat_j(r) (transform of an even function is even), giving the
familiar h_jk(r) = phi_hat_j(r) phi_hat_k(r).
For the ODD block psi_hat_j(-r) = -psi_hat_j(r) (transform of an odd function is odd), giving
h_jk^odd(r) = - psi_hat_j(r) psi_hat_k(r) -- an EXTRA MINUS SIGN relative to the even block, coming
from a completely different argument (Fourier-transform parity) than the direct-integration route
above, and landing on the exact same "sign pattern is the only difference" conclusion via a second,
independent path. Since psi_hat_k is odd and entire, psi_hat_k(-i/2) = -psi_hat_k(i/2) too (odd
entire function stays odd under analytic continuation), giving, after evaluating at r=+-i/2 and
using g_jk(0)=delta_jk:

  pole_jk^odd = -2 psi_hat_j(i/2) psi_hat_k(i/2) - delta_jk log(pi)

(even block: +2 phi_hat_j(i/2) phi_hat_k(i/2) - delta_jk log(pi) -- again, only the leading sign
differs.)

psi_hat_k(i/2), evaluated directly (sin(i L/4) = i sinh(L/4), (i/2)^2 = -1/4):

  psi_hat_k(i/2) = sqrt(2/L) * (-1)^k * sinh(L/4) * 2 w_k / (1/4 + w_k^2)     [real]

## Everything else (archimedean-integral machinery, prime-power sum, Gauss-Legendre/adaptive
## quadrature choices, the Fornberg-free O(N) J_sin(w_m) precomputation trick) is REUSED UNCHANGED
## from data/code/m3_L177_build/weil_form2.py, because none of it depends on which closed form for
## g_jk(t) is plugged in -- only the closed-form g_jk/psi_hat functions themselves change.
