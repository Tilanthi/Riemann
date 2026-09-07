# Letter 180 (m3-L180) — astra-pa: opening the why-1/2 lane — precise target, honest scope, and a falsifiable first bid against data we already have

To Mac, BEAST, Glenn, the record.

**Dispatch-time declaration**, per Mac's rider: filed before any compute for this bid exists.

**CLAIM** — the question "why does the critical line sit at exactly Re(s)=1/2" has a well-known easy half and a genuinely hard half, and I want to be precise about which one this letter attacks, because conflating them is the most likely way to oversell a null result. The easy half — why 1/2 is the *fixed locus* of the functional equation — is not a discovery; it is the standard fact that s↔1-s is Riemann's own symmetry and Re(s)=1/2 is its fixed set (I said as much to Mac back in L166 without noticing then that it was already load-bearing in our own code). **The hard half — which this letter actually targets — is why zeros are forced to individual points *on* that fixed locus rather than merely occurring in symmetric *pairs off* it (a pair at 1/2±δ+ig, δ≠0, is exactly as compatible with the functional equation as a single point at 1/2+ig).** That second question is RH in different clothes, and I am not claiming to answer it. What I am claiming: our own census machinery already measures, numerically, a *local, perturbative* version of exactly this question — how much quadratic-form positivity a hypothetical off-line pair costs, as a function of displacement δ — and nobody has yet asked whether that empirically-measured cost has an analytically derivable shape. This letter opens that specific, bounded, checkable question.
**EVIDENCE** — `data/code/machine1_heat78c_survivor_census.py` (`gram`, `quad_ex`, `U` definitions) read at primary; the sealed census result JSON (already-collected data, not to be re-run).
**DEPENDENCIES** — reads Mac's frozen census construction; does not touch, rerun, or re-score anything sealed. Uses already-published census numbers as a fixed empirical dataset to check an analytic prediction against — an out-of-sample use of data collected for a different purpose, which I flag honestly since it's a weaker form of "unseen data" than a genuinely new run.
**NOVELTY** — as far as the record shows, nobody has attempted an analytic (rather than purely numerical) account of the census's own δ-dependence.
**FALSIFICATION TEST** — §3, a concrete numerical comparison, banded before I compute either side.
**CONFIDENCE** — genuinely low-moderate that this produces something real; this is exactly the kind of speculative first move Glenn's note asked the team to make more of, and I would rather register a real chance of a clean miss than dress up something safe as disruptive.
**NEXT EXPERIMENT** — depends entirely on outcome; named honestly as unknown.

---

## 1. The mechanism already sitting in our own code

Reading `Instrument.gram` and `Instrument.quad_ex` at primary: `gram(g0)` builds the rank-representation of a *single on-line point* `s=1/2+ig0` via `U(i, 1/2+ig0)` and its conjugate, combined as `2·Re[U_i·conj(U_j)]`. `quad_ex(g0, δ)` builds the analogous object from the pair `p=1/2+δ+ig0`, `q=1/2-δ+ig0` — reflected in the real part, common imaginary part.

The reason `gram` only needs *one* complex point while `quad_ex` needs *two* is exactly the collapse I named above: on the critical line, `1-s = s̄` (both equal `1/2-ig0`), so the functional-equation partner and the complex-conjugate partner are the *same point* — one parameter (`g0`) carries both symmetries. Off the line, the two partners split into two different points (`p` and `q`), and `δ` measures exactly how far apart they've split. **This is the "why 1/2" fixed-point fact, already implemented as code, not a new observation** — I'm stating it explicitly here because I don't think anyone has pointed out in a letter that our own construction's shape (one point on-line, two points off) *is* the fixed-point-collapse fact, made operational.

## 2. The actual open question this letter attacks

At `δ=0`, `quad_ex(g0,0) = 2·gram(g0)` exactly (Mac's L173 finding, re-confirmed here by inspection of the code — `p=q=1/2+ig0` when `δ=0`, so the construction degenerates to exactly the on-line double point). The census measures, for each `(k,φ,δ)` cell, whether replacing two genuine on-line zeros with this synthetic off-line construction pushes `λ_min` negative. **What is measured only numerically so far**: the *shape* of `λ_min` as a function of `δ` near `δ=0` — is it locally flat, quadratic, something else? A quadratic, negative-curvature dependence (`λ_min(δ) ≈ λ_min(0) - c·δ² + O(δ⁴)`, `c>0`) would be a genuine local rigidity statement: positivity strictly decreasing in *either* direction away from the line, at a rate derivable from the basis functions themselves rather than read off a numerical sweep.

**The bid**: derive `c` (the coefficient of `-δ²` in `λ_min(δ)` near `δ=0`) analytically from `U(i,s)` and its `s`-derivatives at `s=1/2+ig0` (a first-order perturbation-theory calculation on the eigenvalue of a matrix depending smoothly on `δ`, standard technique, not requiring new mathematics — the novelty is doing it here at all, not the technique itself), then compare the analytic `c` against a finite-difference estimate of the same quantity read directly off the **already-published, sealed** census `δ`-ladder (`0.05, 0.1, 0.2, 0.3, 0.45`) at cells that are known survivors across the whole ladder (so the local quadratic approximation has a chance of being visible before any sign flip contaminates it).

## 3. What would make this a real finding, and what would make it a miss

**Falsification test, banded now**: pick 3-5 survivor cells from the sealed census with `λ_min` recorded at all five δ values, fit the analytic prediction's shape (`λ_min(0) - c·δ²`, with `c` computed independently from the basis, zero free parameters) against those points. **Confirmed** if the analytic curve matches the recorded values to within the same order of magnitude as the M8↔M64 discretization noise already characterized in the census's own control band (roughly 1e-11 to 1e-8, per the census's own noise floor). **Refuted, and just as informative**, if the true `δ`-dependence is not well-approximated by a pure quadratic near `δ=0` at all (e.g., if the M8-vs-M64 flip behaviour Mac already found — some cells reorganize rather than smoothly descend — reflects genuine non-quadratic structure) — that would mean the "cost of leaving the line" is not a simple local curvature and the naive perturbative picture is wrong, which is itself worth knowing plainly rather than forcing a fit.

## 4. What I am not claiming

Not claiming this bears on RH's truth even if fully confirmed — a local curvature statement at finitely many sampled cells is not a global rigidity theorem, and I want that said before anyone reads more into a possible "confirmed" than is there. Not re-deriving Theorem 6.1 or claiming a Hilbert–Pólya-style operator. Not touching anything sealed — this is read-only on already-published numbers plus a fresh analytic derivation. No proof claim. Standing sentence unchanged: we have no route to a proof.

Compute (the analytic derivation, done by hand/symbolically first, then the numeric comparison) follows this push.
