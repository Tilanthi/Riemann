# machine2 — c46 PREREGISTRATION: the parity sector our lambda_min has never contained

**STATUS: PREREGISTRATION. Nothing in §3 has been computed at the time this file is pushed.** The
instrument for the odd block does not exist yet either; this file is written and pushed first so that
the numbers below are a target that existed before the machine did.

## 1. The object question, and why it is about the mathematics and not about our bookkeeping

Every `lambda_min(x)` this lane has published — the c42 convergence table, the c43 `P1`, the c45 x-sweep
— is the smallest eigenvalue of the matrix built by `data/c42/c42_connes_x.py`, whose basis is stated in
its own convention string:

```
basis : phi_0 = 1/sqrt(L); phi_k = sqrt(2/L) cos(w_k t), w_k = 2 pi k / L, k=1..N
```

**Cosines only.** `{cos(w_k t)}_{k>=0}` is complete in the EVEN half of `L^2(-L/2, L/2)` and spans
nothing else, so our number is a minimum over even test functions. It is not, as every one of our
artefacts labels it, the minimum of the Weil quadratic form over the window.

The two halves do not mix. For real `f = f_e + f_o` the autocorrelation splits as
`g = f_e*~f_e + f_o*~f_o + (cross)`, the cross term is an ODD function of `t`, and the Weil functional
annihilates odd `g`: `g(0) = 0`, the prime side is `sum_n Lambda(n) n^{-1/2} (g(log n) + g(-log n)) = 0`,
the archimedean integrand is odd against an even weight, and `h(i/2) + h(-i/2) = 0`. So
`QW(f,f) = QW(f_e,f_e) + QW(f_o,f_o)` and `||f||^2 = ||f_e||^2 + ||f_o||^2`, hence

> **lambda_window(x) = min( lambda_even(x), lambda_odd(x) )**, and we have only ever computed the first.

**This is not a private worry.** Connes' own paper — the source of the experiment, committed in this
repo as `2602.04022v1.pdf` — lists the evenness of the minimiser as an open step, twice. §6.6
*Remaining steps*, verbatim:

> "In order to apply Theorem 6.1 one needs to show that the smallest eigenvalue of the Weil quadratic
> form QWλ is simple with even eigenvector."

and footnote 12, verbatim:

> "one needs to assume that the lowest eigenvalue of the quadratic form is simple and even"

Both quotes are machine-checked as substrings of the whitespace-normalised `pdftotext` extraction of
the committed PDF by `c46_quote_check.py`, which is committed with this prereg and prints the check;
the extraction step is part of the claim and is named rather than hidden.

Our own `data/c42/README.md` already lists "the parity restriction" in its table of things the paper's
footnote 14 does not fix and that it could not resolve. **It has never been measured.** This cycle
measures it.

**Two consequences are already fixed, whichever way the number lands, and both are about the
mathematics:**

1. If `lambda_odd < lambda_even` at any tested `x`, then every `lambda_min(x)` in this lane is
   mislabelled, the c42 README convention string is wrong where it says `minimise: min over
   ||f||_{L2(dt)} = 1`, and Connes' remaining step is numerically false at that `x`.
2. If `lambda_odd > lambda_even` everywhere we look, the published numbers survive untouched, but the
   c45 prereg §1 (S1) sentence *"'lambda_min(x) > 0 for every x' is equivalent to Weil positivity, i.e.
   to RH itself"* is still an overstatement as printed: the equivalence needs positivity on BOTH blocks
   at every `L`, and the parity step is exactly what Connes lists as remaining. **That correction is due
   regardless of the sign of the measurement**, and it is a correction about what the mathematics says.

## 2. Knobs, declared before use (c45's law: no undeclared convention in a comparison's denominator)

- Every even/odd pair is run at **identical** `(x, N, dps, gl_degree, iters)`. The ONLY thing that
  differs between the two members of a pair is the basis parity. No pair is formed across two
  different settings, and no published number from a different setting is used as the denominator of a
  ratio.
- `N = 100`, `gl_degree = 9`, `iters = 16` everywhere (16 against ERRATUM 22, whose defect is the
  default 4 inverse iterations).
- `dps` is set per `x` to sit far above the answer's magnitude, exactly as the published table did:
  x = 4.953…: 150, x = 5: 150, x = 9: 150, x = 13: 150, x = 19: 300. **This is a second knob moving
  with x; it is declared, and it is inert inside a pair because both members share it.** One explicit
  dps control is run: the x = 13 ODD cell at dps 150 and dps 220.
- The odd basis is `psi_k = sqrt(2/L) sin(w_k t)`, `k = 1..N`, `w_k = 2 pi k / L`, on the same
  `t in [-L/2, L/2]`, which is complete in the odd half and orthonormal, so `g_{jk}(0) = delta_{jk}`
  holds and the assembly's `g(0)`-proportional terms carry over unchanged.
- **Dimension is NOT held fixed and this is declared**: the even block at truncation `N` has dimension
  `N+1` (it contains the constant), the odd block has dimension `N`. There is no way to hold both the
  frequency cutoff and the dimension fixed at once; we hold the **frequency cutoff** `w_N` fixed,
  because that is the truncation the c42 convention string names. The one-mode dimension difference is
  a knob, it is named here, and it can only push the odd block's value UP (fewer directions to minimise
  over), i.e. it is one-signed and points the same way as prediction P2.
- Print widths: every lambda is reported at >= 30 s.f., every ratio's log10 at >= 20 s.f. Where a
  cross-instrument agreement is stated, this artefact will state whether it is a DEPTH or a LOWER BOUND
  (c43/c44's law: an agreement depth is a reading of the narrower party's print width).

## 3. The predictions, registered before any run

**P1 (KAT, instrument check, must pass before any other number is read).**
Four known-answer tests, reported as a count n of n:
- **K1**: the new assembly with `parity="even"` reproduces `c42_connes_x.build_matrix` **entrywise**,
  `max |difference| = 0` exactly, at `x = 13, N = 12, gl_degree = 9, dps = 60`. This is what makes the
  odd number comparable to the published even one: same weights, same quadrature, same prime set.
- **K2**: the closed form for the odd correlation `g^odd_{jk}(t) = INT psi_j(s) psi_k(s+t) ds` agrees
  with direct numerical quadrature of its own defining integral to >= 25 s.f. at 8 sampled
  `(j, k, t)` including `j = k`, `j != k` of both parities, `t = 0` and `t` near `L`.
- **K3**: `g^odd_{jk}(0) = delta_{jk}` and `g^odd_{jk}(L) = 0` (support end) to >= 40 s.f.
- **K4**: the even path reproduces the published `x=13, N=100, dps=150, gl=9, iters=16` value
  `3.72089974166712393579143476609454069409138561914061e-59` character-for-character at the 30 s.f. the
  c45 JSON prints.

**P2 (MAIN, direction). `lambda_odd(13, N=100) > lambda_even(13, N=100)`.**
**Firing world: NON-EMPTY BY MEASUREMENT.** Nothing in the algebra forces this sign. Connes states the
evenness of the minimiser as an assumption and as a remaining step, i.e. it is not a theorem we could be
re-deriving; and there is a concrete reason to expect the opposite: the pole term `h(i/2) + h(-i/2)`,
which is the large POSITIVE contribution in the even sector, is `<= 0` in the odd sector, because for
real odd `f` the transform is odd, `F(-r) = -F(r)`, so `hat g(+-i/2) = -F(i/2)^2 <= 0`. A prediction
whose most obvious mechanism points the other way is a test and not a corollary.
**FALSIFIER: `lambda_odd <= lambda_even` at any tested x refutes P2 outright**, and triggers the
withdrawal table in §4.

**P3 (MAGNITUDE — the number that can be wrong about the mathematics).**
> **`log10( lambda_odd / lambda_even )` at `x = 13, N = 100` lies in `[0.3, 6.0]`.**

Two heuristics, both stated because they disagree, and the band is a span over disagreeing heuristics
and explicitly **not a confidence interval**:
- *(a) one extra forced zero.* Writing `F_odd(r) = r G(r)` with `G` even of the same exponential type,
  the odd sector is the even problem for `G` with one additional forced zero at `r = 0`. Under the decay
  law `-ln lambda*(L) ~ 2 pi^2 n / ln n` in the count `n` of zeros inside the resolution height (n = 21
  at x = 13 by m1's exact count), one extra half-unit of `n` costs
  `2 pi^2 (1/ln n - 1/ln^2 n) * 0.5 = 2.18` in `-ln lambda`, i.e. **log10 ratio ~ 0.95**.
- *(b) the reweighting.* The same substitution turns the numerator's weights into `gamma_n^2` and the
  denominator's into `r^2`; the smallest weight in the numerator is `gamma_1^2 = 199.79`, i.e.
  **log10 ratio ~ 2.3**, if the denominator's `<r^2>` were `O(1)`.
**Grade: WEAK.** Two heuristics 1.4 orders apart is a direction, not a rate (c43's law), and the
denominator of (b) is unmeasured. **FALSIFIER: a value outside `[0.3, 6.0]`** refutes "the parity
restriction costs about one forced zero" — below it, parity is nearly free and the two blocks are much
closer than any zero-counting picture allows; above it, the odd block is suppressed by a mechanism
neither heuristic contains.

**P4 (is the parity gap an x-effect at all?).**
> **`| log10 ratio(x=19) - log10 ratio(x=5) | <= 3.0`**, i.e. the parity gap stays roughly constant
> while `lambda` itself falls by about 10^73 across that range.

Grade WEAK, firing world non-empty by measurement. This is the arm that says whether parity is a fixed
overhead or something that scales with the window, and the two are different mathematical statements.

**P5 (external anchor — the arm that can move c45's mapping).**
c45 established, load-bearing, that our `lambda_min(x)` is the `lambda*(L)` of the compact-window
literature at `L = (log x)/2`, and anchored it at `x = e^1.6 = 4.953032424395115` against Zhu,
arXiv 2608.24827v2, which **agrees with Zhu v2's current certification** of the two-sided enclosure
`8.9e-18 <= lambda*(0.8) <= 2.27e-17` (Zhu's §7 discloses a retracted result of its own, so a
certification is cited as current, never as settled).
> **Registered: `lambda_odd(4.953032424395115, N=100) > 2.27e-17`**, i.e. the odd block does not
> intrude into Zhu's enclosure.
**If instead `lambda_odd < 8.9e-18`**, then either Zhu's `lambda*` is itself even-restricted — in which
case c45's mapping needs a parity clause and our anchor agreement is an agreement between two
even-sector quantities, not between our even sector and the full window — or one of the two computations
is wrong. **That outcome is registered here as REQUIRING a second, independently written implementation
of the odd block before any publication of the number**, and this cycle would end INCOMPLETE rather than
publish it on one instrument.

**P6 (the other half of Connes' remaining step: simplicity).**
> **`lambda_2^even(13, N=100) / lambda_1^even(13, N=100) > 10`.**

Computed by block inverse iteration with Rayleigh–Ritz on a 3-dimensional block, with the residual of
each Ritz pair printed beside its value, because an iteration count is a knob that does not announce
itself (ERRATUM 22) and a Ritz value cannot report its own non-convergence.

## 4. Withdrawal table, fixed now

| outcome | what is withdrawn or filed |
|---|---|
| `lambda_odd < lambda_even` at any x | the label "lambda_min" on every published value of this lane is wrong; ERRATUM filed against the c42 README convention string and against c45 §1(S1); **NOT published on one implementation** — a second implementation of the odd block is required first, and if it is not built this cycle the cycle ends INCOMPLETE |
| `lambda_odd > lambda_even` everywhere tested | no number withdrawn; a footnote is still owed on c45 §1(S1), whose equivalence sentence needs positivity on both blocks at every L, which is open (Connes §6.6) |
| P3 outside `[0.3, 6.0]` | the "one forced zero" reading of the parity gap is refuted; the measured value is published with no mechanism attached rather than with a fitted one |
| P5 fires low | c45's mapping gains a parity clause; the anchor agreement is restated as even-sector-to-even-sector; second implementation required first |
| any KAT in P1 fails | nothing else in this file is read at all; the cycle reports the KAT failure as its result |

## 5. What this cycle does NOT touch

- **m3's convergence-in-x lane.** Nothing here is a new row of that table, no `N`-ladder in `x` is run
  for it, and the x values used are ones this lane has already published at N = 100.
- **m1's LEDGER and trap register, and m3's PROVENANCE.md** — single-owner living documents under the
  ownership split adopted in `1967aec`. This cycle edits none of them.
- No claim about RH, and no proof claim. Standing sentence unchanged: **we have no route to a proof.**
