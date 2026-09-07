# m3-L180 build — the why-1/2 perturbation derivation (worked by hand before any code)

## Setup

`K_S(delta) = K - gram(z_k) - gram(z_{k+1}) + quad_ex(g, delta)`. Only `quad_ex` depends on delta;
`K, gram(z_k), gram(z_{k+1})`, and `G` are all delta-independent. `eig(F)` solves the GENERALIZED
eigenproblem `F v = lambda G v` via Cholesky whitening `B = L^-1 F L^-T` (G = L L^T), so
`lambda_min(delta)` is the smallest generalized eigenvalue of the pencil `(K_S(delta), G)`.

`quad_ex(g0,delta)[i,j] = 2 Re[ U_i(p) conj(U_j(q)) + U_i(q) conj(U_j(p)) ]`,
`p(delta) = 1/2+delta+i g0`, `q(delta) = 1/2-delta+i g0`, `p'=1, q'=-1` (affine, so p''=q''=0).

## Step 0 — exact evenness (no perturbation theory needed for this part)

`p(-delta) = q(delta)` and `q(-delta) = p(delta)` -- i.e. delta -> -delta exactly SWAPS p and q.
`quad_ex[i,j]` is `Term1 + Term2 := U_i(p)conj(U_j(q)) + U_i(q)conj(U_j(p))`, which is manifestly
invariant under swapping p<->q (the two terms just swap with each other, sum unchanged). So
`quad_ex(g0,-delta) = quad_ex(g0,delta)` IDENTICALLY, for every delta, not just to some order --
hence `K_S(delta)` is an even matrix-valued function of delta, hence `lambda_min(delta) =
lambda_min(-delta)` EXACTLY (same matrix has the same spectrum). No odd powers of delta can appear
in the Taylor expansion; fitting `lambda_min(0) - c delta^2` needs no separate check that the linear
term vanishes -- it is automatic, and confirmed independently by direct differentiation below.

## Step 1 — first derivative is the zero matrix (confirms Step 0 by direct computation)

Chain rule on Term1 = U_i(p(delta)) * conj(U_j(q(delta))), using p'=1, q'=-1 (both constant, real):

  d(Term1)/d(delta) = U_i'(p) conj(U_j(q)) - U_i(p) conj(U_j'(q))
  d(Term2)/d(delta) = -U_i'(q) conj(U_j(p)) + U_i(q) conj(U_j'(p))

At delta=0, p=q=s0 := 1/2+i g0: the two lines above become NEGATIVES of each other term-by-term,
so d(Term1+Term2)/d(delta)|_0 = 0 for every (i,j). d(quad_ex)/d(delta)|_0 = 0 as a matrix (A1 = 0).

## Step 2 — second derivative (the Hessian A2)

Differentiate the first-derivative expressions again (p''=q''=0 throughout):

  d^2(Term1)/d(delta)^2 = U_i''(p)conj(U_j(q)) - 2 U_i'(p)conj(U_j'(q)) + U_i(p)conj(U_j''(q))
  d^2(Term2)/d(delta)^2 = U_i''(q)conj(U_j(p)) - 2 U_i'(q)conj(U_j'(p)) + U_i(q)conj(U_j''(p))

At delta=0 (p=q=s0) these two are IDENTICAL, so:

  d^2(Term1+Term2)/d(delta)^2 |_0 = 2*[ U_i''(s0)conj(U_j(s0)) - 2 U_i'(s0)conj(U_j'(s0))
                                          + U_i(s0)conj(U_j''(s0)) ]

  A2[i,j] := d^2(quad_ex[i,j])/d(delta)^2 |_0 = 2*Re[ 2*(...) ]
           = 4 Re[U_i'' conj(U_j)] + 4 Re[U_i conj(U_j'')] - 8 Re[U_i' conj(U_j')]

(all U, U', U'' evaluated at s0 = 1/2 + i g0). Symmetric in (i,j) by inspection (matches the
manifest symmetry of quad_ex for all delta, a free consistency check).

## Step 3 — generalized eigenvalue perturbation (standard, re-derived here not quoted)

For a smooth pencil A(t) v(t) = lambda(t) G v(t), G fixed, normalized v(t)^T G v(t) = 1:
differentiate once, left-multiply by v^T, use v^T A = lambda v^T G (transpose of the eigen-eq):
  lambda'(t) = v(t)^T A'(t) v(t).
Differentiate again the same way: the v^T A v'' term cancels an identical term on the RHS, leaving
  lambda''(t) = v(t)^T A''(t) v(t) + 2 lambda'(t) v(t)^T G v'(t).
At t=0 here, A'(0) = 0 (Step 1) hence lambda'(0) = 0 too, killing the second term:
  lambda_min''(0) = v0^T A2 v0,     v0 := the delta=0 minimal-eigenvalue eigenvector,
                                     G-normalized: v0^T G v0 = 1.
(No G^-1 or Cholesky factor appears explicitly in the final formula -- they cancel against the
G-normalization of v0, which is exactly the eigenvector `eig()` already returns un-whitened.)

## Result

  lambda_min(delta) ~ lambda_min(0) - c delta^2 + O(delta^4),   c := -(1/2) v0^T A2 v0

with A2 as in Step 2, U'_i(s) = d/ds INT phi_i(t) e^{st} dt = INT t phi_i(t) e^{st} dt (differentiate
under the integral sign -- valid since phi_i is smooth and compactly supported), and similarly
U''_i(s) = INT t^2 phi_i(t) e^{st} dt. No new mathematics; the content is doing this here for THIS
construction, on real data, and checking it.

## Validation plan (before trusting c on real cells)

1. Reproduce K_S(0)'s lambda_min at several cells EXACTLY against the sealed JSON, using an
   independently-written loader (own hash check, own matrix assembly) -- gate before anything else.
2. Cross-check the ANALYTIC A2 formula against a raw finite-difference second derivative of the
   ACTUAL quad_ex(g0,delta) matrix (built from the same U/gram/quad_ex definitions) at small delta,
   BEFORE using A2 in the eigenvalue formula -- catches a wrong derivative independently of the
   eigenvector step.
3. Only then assemble c and compare lambda_min(0) - c delta^2 against the sealed delta-ladder.
