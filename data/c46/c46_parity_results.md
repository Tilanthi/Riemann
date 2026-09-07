# machine2 — c46 RESULTS: the odd block, measured

Registered before compute in `c46_parity_prereg.md` (commit `49a2675`). Nothing below was computed
before that commit was on `origin/main`.

## 0. Verdict in one line

**The minimum is in the even block at every window we can reach, by 3.0 to 4.2 orders of magnitude,
and the gap does not come from the truncation.** Connes' remaining step is corroborated numerically
where our instrument reaches; it is not proved, and this cycle does not prove it.

## 1. Scorecard

| arm | registered | measured | verdict |
|---|---|---|---|
| **P1 K1** | rebuilt EVEN assembly entrywise identical to `c42.build_matrix` | `max abs diff = 0.0` exactly, same prime set | **PASS** |
| **P1 K2** | odd closed form vs quadrature of its own integral, >= 25 s.f., 8 cases | max rel err **2.2959e-41** (dps 40) | **PASS** |
| **P1 K3** | `g_odd(0) = I`, `g_odd(L) = 0`, >= 40 s.f. | `0.0` exactly / **3.6351e-62** | **PASS** |
| **P1 K4** | published `x=13, N=100` literal reproduced at the 30 s.f. printed | `3.72089974166712393579143476609e-59`, character-for-character | **PASS** |
| **P2** | `lambda_odd(13,100) > lambda_even(13,100)` | `3.3411e-55` vs `3.7209e-59`, ratio **8977.4** | **PASS** |
| **P3** | `log10(odd/even)` at x=13,N=100 in `[0.3, 6.0]` | **3.9532385710728263766** | **PASS on the band, FAIL on both of its mechanisms** — see §4 |
| **P4** | `abs(log10 ratio(19) - log10 ratio(5)) <= 3.0` | **1.2272030926088045631** | **PASS** |
| **P5** | `lambda_odd(e^1.6, N=100) > 2.27e-17` | **1.6660665631763857853981985599e-14**, i.e. **734.0x** Zhu v2's current certified upper bound | **PASS** |
| **P6** | `lambda_2^even / lambda_1^even > 10` at x=13, N=100 | **3.91576e+07** | **PASS** |

**Nine of nine scorecard rows** — which is **six registered arms**, P1 through P6, P1 carrying four
KATs. (Self-caught count slip: the first draft of this file and of the c46 letter said "seven of
seven", which is neither the row count nor the arm count. Corrected here before adjudication;
`c46_parity_results.md` and the letter carried it and `data/c46` carried nothing wrong.)
The one row that is not a clean pass is P3, and it is reported as a partial below rather
than as a pass, because a band wide enough to survive while both of the heuristics that generated it
miss is a weak instrument, and saying "PASS" without that sentence would be the c43 defect again.

## 2. The measurement

Every pair is at **identical** `(x, N, dps, gl_degree = 9, iters = 16)`. The only difference inside a
pair is the basis parity. Instrument `c46_parity.py`, table generator `c46_analyse.py`, raw cells in
the committed `c46_{even,odd}_x*_N*_dps*_g*_it*.json`.

| x | N | dps | `lambda_EVEN` (30 s.f.) | `lambda_ODD` (30 s.f.) | `log10(odd/even)` (20 s.f.) |
|---|---|---|---|---|---|
| 4.953032424395115 | 100 | 150 | `1.73573784262049859362564244089e-17` | `1.6660665631763857853981985599e-14` | `2.9822082164042423351` |
| 5 | 100 | 150 | `1.00502253020078329195348849809e-17` | `1.05647662938859768787043976697e-14` | `3.0216840966374248640` |
| 13 | 60 | 150 | `1.01356290716919907359975938527e-58` | `8.54687683010904448605585589299e-55` | `3.9259567368247825561` |
| 13 | 100 | 150 | `3.72089974166712393579143476609e-59` | `3.34107742032073965658213712602e-55` | `3.9532385710728263766` |
| 13 | 140 | 150 | `3.19161872290429918777587895153e-59` | `2.84751569133936367715637039399e-55` | `3.9504551218551783503` |
| 19 | 100 | 300 | `1.91753481000346992195154931041e-90` | `3.40118649457081143325142161008e-86` | `4.2488871892462294270` |

Every ratio in the last column is computed from the **60-s.f.** literals stored in the JSONs, not from
the 30-s.f. reading forms printed above: a quantity asserted at 20 s.f. must be built from inputs
stored wider than the assertion.

**dps control.** The `x = 13` ODD cell at dps 150 and at dps 220 are **identical at all 60 s.f.
printed**. Per the c43 law that is a **LOWER BOUND of 60 s.f., not an agreement depth** — the
agreement equals the print width, so the width is what is being read. The `dps` knob is inert here to
at least that depth, and we do not know how much further.

**Solver control.** The three-dimensional block Rayleigh–Ritz solver (`c46_parity.py block`) is a
different algorithm from the single-vector inverse iteration used for the table, and its smallest
Ritz value reproduces the table value at both parities, at all **40 s.f.** it prints — again a lower
bound at the print width, not a depth. Residuals are printed beside every Ritz value because a Ritz
value cannot report its own non-convergence.

## 3. What this settles, and exactly what it does not

**The object.** For real `f` supported in `[-L/2, L/2]`, the Weil quadratic form is block-diagonal in
the even/odd decomposition: the cross terms produce an **odd** autocorrelation `g`, and the functional
kills odd `g` — `g(0) = 0`, the prime side pairs as `sum_n Lambda(n) n^{-1/2} (g(log n) + g(-log n)) = 0`,
the archimedean integrand is odd against an even weight, and `h(i/2) + h(-i/2) = 0`. Complex `f` adds
nothing: writing `f = u + i v` with `u, v` real, the cross term in `|F(r)|^2` is odd in `r` and cancels
over the `+-gamma`-symmetric zero set, so `QW(f,f) = QW(u,u) + QW(v,v)` and
`||f||^2 = ||u||^2 + ||v||^2`. Hence **`lambda_window(x) = min(lambda_even(x), lambda_odd(x))`** and
the two sectors above are the whole story.

**What is now measured.** At `x = 4.953, 5, 13, 19` the even block is lower by `10^2.98` to `10^4.25`.
So at these windows the number this lane has published as `lambda_min(x)` **is** the window minimum,
and it has stopped being an assumption there.

**What is NOT proved, stated plainly.** `lambda_even(N)` and `lambda_odd(N)` are both **variational
upper bounds** on their own block's infimum (a minimum over a subspace cannot be below the minimum
over the space), and both are non-increasing in `N` by Cauchy interlacing, since both bases are nested.
So `lambda_even(N) < lambda_odd(N)` at every computed cell **does not imply** `lambda_even(inf) <
lambda_odd(inf)`: a bound below a bound is not an ordering of the limits. What survives rigorously is
the weaker and still useful statement `lambda_window(inf) <= lambda_even(N)` for every `N` — our
published numbers were always valid **upper bounds on the window minimum** whatever the parity answer
is; what was at risk was the label, not the bound.

**The evidence against a late crossing, as a measurement rather than an argument.** Across a 2.3x
change of dimension at `x = 13` the gap moves by **0.028 in log10 and not monotonically**
(N=60: 3.92596, N=100: 3.95324, N=140: 3.95046), while `lambda` itself falls by 0.502 (even) and
0.477 (odd) over the same range. For the odd block to take the minimum it would have to fall about
4 orders faster than the even block from `N = 140` onward, having tracked it to within 0.03 orders
over `60 -> 140`. That is evidence, not a proof, and this cycle does not claim more.

**Both blocks obey Cauchy interlacing as they must** (a diagnostic with an **empty firing world by
ALGEBRA**, run because it catches gross assembly bugs, not because a pass is informative):
even `1.0136e-58 -> 3.7209e-59 -> 3.1916e-59`, odd `8.5469e-55 -> 3.3411e-55 -> 2.8475e-55`.

## 4. P3: the band held and neither mechanism did

Registered band `[0.3, 6.0]` in `log10(odd/even)`, from two heuristics: *(a)* one extra forced zero at
`r = 0` costing `2 pi^2 (1/ln n - 1/ln^2 n) * 0.5` in `-ln lambda`, giving **0.95**; *(b)* the
`F_odd(r) = r G(r)` reweighting with `gamma_1^2 = 199.79`, giving **2.3**. Measured **3.95**. The band
passed; **both mechanisms are wrong, in the same direction, and the band passed only because it was
wide enough to be a weak test.** Registering a span over two disagreeing heuristics and grading it
WEAK was the right call and it is still not much of a test.

Inverting heuristic (a) instead of predicting with it, and declaring that this is a **post-hoc fit and
not a prediction**: define `delta_n := ln(odd/even) / (2 pi^2 (1/ln n - 1/ln^2 n))`, the number of
extra forced zeros the gap is worth under the decay law. Measured, with `n` the **EXACT** count of
ordinates `0 < gamma <= T* = 2 pi x` (m1-L185's convention item; the smooth Riemann–von Mangoldt count
gives different numbers and the choice must be named every time):

| x | n | `delta_n` |
|---|---|---|
| 4.953032424395115 | 4 | 1.7307 |
| 5 | 4 | 1.7536 |
| 13 | 21 | 2.0907 |
| 19 | 38 | 2.4865 |

**The parity restriction is worth about two forced zeros, and that cost drifts upward with the
window.** Four points give a direction, never a rate — this lane's own standing law — so no exponent
is fitted to them and none is quoted.

The implied constant of the decay law itself, same exact-count convention, for reference and not as a
claim: `K = (-ln lambda) ln n / n` reads **19.505 (even, x=13, N=100), 19.527 (even, x=13, N=140),
19.775 (even, x=19)** against `2 pi^2 = 19.7392`, reproducing c45's published `19.527` at x=13 exactly;
the odd block reads **18.185 / 18.209 / 18.839**. At `x = 4.953` and `x = 5` the count is `n = 4` and
`K` reads 13.4 / 13.6 — the law is asymptotic in `n` and four zeros is not an asymptotic regime, which
is why no anchor claim is built on those two cells.

## 5. Consequences for what this lane has already published

**(a) No number is withdrawn.** Every published `lambda_min(x)` is unchanged and is now, at the four
windows tested, measured to be the window minimum rather than assumed to be.

**(b) One published sentence IS withdrawn — ERRATUM 23.** The c45 prereg §1 (S1) says, of our
`lambda_min`:

> The limit of lambda_min(x) as x grows
> is the infimum of the Weil form on the whole space, so **"lambda_min(x) > 0 for every x" is equivalent
> to Weil positivity, i.e. to RH itself.**

machine-checked as a substring of `data/c45/c45_attackC_prereg.md` by `c46_verbatim_check.py`
(4 quotes FOUND, 1 negative control NOT FOUND, PASS).

As printed that is an overstatement, and this cycle is what makes it visible. Weil positivity is
positivity of the form on the **whole** space; our `lambda_min` is the even block; positivity of the
even block for every `x` is implied by RH but does not imply it, because the odd block is not
mentioned. The corrected sentence is: *"`lambda_even(x) > 0` for every x is implied by Weil
positivity; the converse needs the odd block too, i.e. `min(lambda_even, lambda_odd) > 0` for every x,
which is what is equivalent to RH."* Nothing computed in c45 moves; c45's verdicts, its P1–P6 scores,
its anchor and its decay-law table are all untouched. The defect is one logical quantifier in one
sentence, and it is exactly the quantifier this cycle went looking for.

**(c) c45's mapping survives, and gains a receipt rather than a caveat.** c45's load-bearing mapping
is that our `lambda_min(x)` is the `lambda*(L)` of the compact-window literature at `L = (log x)/2`,
anchored at `x = e^1.6` against Zhu, arXiv 2608.24827v2, which **agrees with Zhu v2's current
certification** of `8.9e-18 <= lambda*(0.8) <= 2.27e-17`. Had the odd block landed inside that
enclosure the mapping would have needed a parity clause. It lands at `1.666e-14`, **734x above the
top of the enclosure**, so `min(even, odd) = even` there and our anchored quantity is the window
minimum, not merely an even-sector quantity. The one thing this does **not** establish is which
convention Zhu uses; it establishes that at `L = 0.8` the two conventions cannot differ, because the
odd block is nowhere near.

**(d) `data/c42/README.md` lists "the parity restriction" among the things the paper's footnote 14
does not fix and that we could not resolve.** It is now resolved as far as measurement can resolve it,
at four windows, and the row should be read with this file beside it.

## 6. The literature status of the question, quoted exactly

Connes, arXiv 2602.04022 (the copy committed in this repo), §6.6 *Remaining steps*, verbatim:

> "In order to apply Theorem 6.1 one needs to show that the smallest eigenvalue of the Weil quadratic
> form QWλ is simple with even eigenvector."

and footnote 12, verbatim:

> "one needs to assume that the lowest eigenvalue of the quadratic form is simple and even"

Both are machine-checked as substrings of a whitespace-normalised `pdftotext` extraction of that PDF
by `c46_quote_check.py`, which also carries a **negative control** — the first sentence with "even"
replaced by "odd" — that must NOT be found. Output committed as `c46_quote_check.out`: 3 FOUND,
negative control NOT FOUND, PASS. A self-read cannot catch an omission in a quotation, so the check
is the claim.

**Both halves of that step are measured here**, and neither was measured before in this exchange:
*simple* — `lambda_2^even / lambda_1^even = 3.9158e7` at x=13, N=100, so the lowest even eigenvalue is
simple with a 7.6-order gap; *even* — the odd block sits 3.95 orders above. **Status label: this is a
NUMERICAL CORROBORATION of a step Connes states as open, at four windows and one truncation ladder.
It is not a proof of that step and must never be quoted as one.**

## 6b. K5 — an end-to-end SECOND PATH to the odd block, and its error term with a coefficient

K1 proves the c46 assembly **is** c42's assembly, so the odd block inherits every receipt m1 and m3
earned against the even one. The only genuinely new algebra in this cycle is the closed form for the
odd correlation. K2/K3 test it pointwise; **K5 tests it end to end**, rebuilding the entire odd matrix
with the closed form replaced by panelled Gauss-Legendre quadrature of the defining integral, and
comparing `lambda_min`. A pointwise agreement and an eigenvalue agreement are different claims: the
smallest eigenvalue of a nearly singular matrix can be moved by an error that is invisible entrywise.

| N | x | dps | panel degree | max entry diff (scale 2.379) | `lambda_min` agreement |
|---|---|---|---|---|---|
| 10 | 13 | 50 | 3 | `5.8298217e-29` | **18 s.f.** |
| 10 | 13 | 50 | 4 | `1.4165653e-49` | **27 s.f.** |

Both are **agreement DEPTHS, not lower bounds**: both sides are printed at 40 s.f., wider than the
agreement, so no print width is censoring the number (the c43 law, applied to our own receipt).
Raising one knob — the per-panel GL degree — by one level moves the entrywise error by **20 orders**
and the eigenvalue agreement by **9 s.f.**, which is what says the residual at degree 3 was the
quadrature's and not the formula's. **At degree 4 the agreement has reached the run's own precision
floor**: at `dps = 50` with `lambda ~ 1.6e-23` against an `O(1)` matrix, about `50 - 23 = 27` digits
are expressible, and 27 is what it reads. So the two paths agree to everything this cell can express.

**The first attempt at K5 is reported because it failed and the failure is instructive**: adaptive
`mp.quad` over the whole interval in one panel was killed at 900 s at `N = 8`. A single panel spends
its degree budget fighting the oscillation of `sin(w_n s)` rather than the integrand, and the fix is
to subdivide at the oscillation scale (`4n + 2` panels, at least four per shortest half-period). The
panel count and the per-panel degree are **quadrature knobs and are declared**; the degree is varied
above precisely so that neither is left as a named error source with no coefficient beside it.

## 6c. The zero counts are MEASURED here, not cited

Every `delta_n` in §4 needs `n = #{0 < gamma <= T* = 2 pi x}`. m1 supplied 21 and 38 at x = 13 and 19
and, correctly, **declined to confirm their own numbers from recall** when witnessing our prereg. So we
computed them rather than carry them (`c46_zerocount.out`, mpmath `zetazero`):

| x | `T* = 2 pi x` | `gamma_n` | `gamma_{n+1}` | n |
|---|---|---|---|---|
| 4.953032424395115 | 31.1208205549 | 30.4248761259 | 32.9350615877 | **4** |
| 5 | 31.4159265359 | 30.4248761259 | 32.9350615877 | **4** |
| 13 | 81.6814089933 | 79.3373750202 | 82.9103808541 | **21** |
| 19 | 119.380520836 | 118.790782866 | 121.370125002 | **38** |

All four agree with the cited values. m1's declined item is closed from our side by measurement, which
is cheaper than either of us reading a record.

## 6d. m1's prereg witness, and the P5 gap it named — scored as a prereg gap

m1 witnessed the prereg (`d259529`, committer 20:17:09Z) and independently re-ran our own quote
checker, re-read the c42 README parity line, the K4 literal at 50 s.f., the c45 S1 quote and the P3
arithmetic. **They also named a real defect: P5's outcome space had no middle.** We registered
`lambda_odd > 2.27e-17` (pass) and `lambda_odd < 8.9e-18` (parity-clause), and left the **interior**
`8.9e-18 < lambda_odd < 2.27e-17` unassigned — which is not a corner case, because c45's own anchor
put `lambda_even` in agreement with that enclosure.

**Naming the clock (c44's law): our run launched at 20:17:00Z by the shell clock on our own host;
m1's witness has committer time 20:17:09Z and was fetched by us at 21:0xZ.** So the ask arrived after
the compute began and we did not see it in time to close it. **We therefore score the interior branch
exactly as m1 asked: as a PREREG GAP, unassigned, not interpreted.** It happens to be empty in fact —
`lambda_odd(e^1.6) = 1.666e-14` is 734x above the top of the enclosure, three orders outside the
interior — so nothing in this cycle turns on it, and that is luck rather than design. Recorded here so
the gap is in the record whether or not it ever fires: **an outcome space with an unassigned middle is
a post-hoc branch waiting to happen, and m1 caught ours at the only moment it was cheap.**

## 7. Novelty label, per Glenn's msg-769 item 14

**NEW TO THIS RUN, rediscovered.** That the even/odd blocks decouple is standard; that the minimiser
is expected to be even is stated in the source paper itself. What is new here is only that the odd
block has been **computed** rather than assumed away, and that its distance from the even block has
been measured and shown to be truncation-stable. We looked for a published numerical value of the odd
block at these windows and did not locate one; that is a **failed search, named** (Connes' footnote 10
says the eigenvectors are compared with prolate vectors in reference [25], which is where such a
number would live, and we have not read [25]) — **POSSIBLY NEW** applies to the measured gap only, and
we would drop it on sight of [25].

## 8. Standing sentence

No proof claim. **We have no route to a proof.**
