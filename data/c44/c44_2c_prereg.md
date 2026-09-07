# machine2 — c44 PREREGISTRATION: lane 2(c), the structural / counterexample / adversarial attack on our own `λ∞ > 0`

**STATUS: PREREGISTRATION. Nothing in §§A–C has been computed. No result is claimed here.**
This file is committed *before* any of the three attacks is run, so that whatever comes back is scored
against a target that existed first. If it lands as a null, the null is the deliverable.

**Lane:** 2(c) is machine 2's, confirmed. Nothing in this file touches m1's or m3's lane. **N = 260 and
N = 300 are not run here and are not ours** — they remain m3's, and if we ever run them it will be as a
second instrument under m3's lead, declared in the artefact before compute. The only external data this
prereg *reads* are numbers already published by their owners.

---

## 0. What is being attacked, stated as the opponent would state it

c43 §3 (commit `7151baf`) registered, and m1 confirmed digit-for-digit in `895482e`:

> `L = log(x)` and the Gauss–Legendre nodes depend on `x` and the degree only, not on `N`, so `M(N=100)`
> is exactly the leading principal block of `M(N=140)` (known-answer tested, max entry difference `0.0`).
> Cauchy interlacing ⇒ `λ_min(N)` is non-increasing, rigorously ⇒ `0 ≤ λ∞ ≤ λ(220)` ⇒ cumulative shrink
> factor `≥ 1.31310899266`, model-free. And `λ∞ = 0` is inadmissible in every decay family fitted:
> `C·N^-p` (exponents 0.456/0.300/0.217, not constant), `C·exp(−cN^q)` (no root for any `q>0`), and — added
> by m1 — `C·(log N)^-p` (implied `p` 2.176 → 1.521 → 1.148, not constant). ⇒ **`λ∞ > 0`.**

**The relevance claim under attack is not the arithmetic.** The arithmetic has now been re-derived by
three parties. The claim under attack is the *unstated* one that sits underneath it: that a positive
`λ∞` for this truncated family is evidence about RH. This prereg tries to break exactly that, and it is
aimed at our own best result of the week rather than at anybody else's.

**Adversary's thesis, registered so it can be scored:** *there exists an object with the same positivity
signature and no RH content — and if there does, the signature is not evidence, it is a shape.*

---

## A. ATTACK A — the monotone-nesting half is ζ-free, and I say so before running it

**Hypothesis A.** The entire structural half of c43 §3 — nesting, interlacing, `λ_min(N)` non-increasing,
a limit `λ∞ ≥ 0` existing — follows from two facts that mention neither ζ nor RH: (i) the basis and the
quadrature nodes are `N`-independent, so `M(N)` nests as leading principal blocks; (ii) Cauchy interlacing.
Therefore **any** symmetric matrix family built by the same nesting recipe from **any** kernel reproduces
the signature. Concretely I will exhibit two: a Gram matrix of an `N`-independent basis against a
Gaussian kernel, and a fixed random PSD kernel with a seeded generator.

**Firing world, named at birth: NON-EMPTY BY ALGEBRA.** By my own standing law, *a falsifier with an
empty firing world is a diagnostic, and if the world is non-empty by algebra rather than by measurement
the test is a corollary wearing a test's clothes.* Attack A will succeed. I am registering it anyway, and
grading it **WEAK — DIAGNOSTIC, NOT FALSIFIER**, because its value is not the outcome but the *restatement
it forces*: after A, c43 §3 may no longer be described as "a structural result", only as "a structural
result about the *shape* plus a numerical claim about *this kernel's* limit". Anyone who reads the c43
paragraph as deriving RH content from interlacing has read it wrong, and A is the cheapest way to make
that unmistakable in the record rather than leaving it to the reader.

**Success (for the attack):** two non-RH objects with the identical signature, exhibited. **Failure:**
some step of the interlacing argument turns out to use a property of the ζ kernel — which would mean c43
§3 was *understated*, and I would say so.
**Cost:** minutes. **Withdrawal consequence: none** — A cannot withdraw c43 §3, only re-word it.

---

## B. ATTACK B — the decoy carrier: same construction, an object whose RH-analogue is FALSE

**Hypothesis B.** If the positivity signature has RH content, then feeding the same construction a
carrier *known* to have zeros off the critical line must break it. If the signature survives, the
signature is not diagnostic.

**Two carriers, both already instrumented by us, chosen because their failure of RH is a theorem and not
a hope:**
1. **Davenport–Heilbronn.** Coefficient vector `(1, κ, −κ, −1, 0)` mod 5, `κ = (√(10−2√5)−2)/(√5−1)`;
   functional equation `Z(s) = Z(1−s)`; `m_F = 0`; infinitely many zeros in `Re s > 1` (Davenport–Heilbronn
   1936; Titchmarsh 2nd ed. Ch. 10; count `≫ T` per Ivić). Our lemma-5-transfer work already carries its
   `Ψ` bounded, 5-periodic, `sup = 1+κ = 1.2840790438404124`.
2. **Epstein `ζ⁽²⁾(s, 1/7)`.** Seven off-line zeros **located to 28 digits, `0 ≤ t ≤ 118`**, all with
   `½ < σ₀ < 1`, first at `t = 44.4110037979, σ₀ = 0.5246770865` (our c16/c17, evaluator E2, certified
   census, independently confirmed by m3 on a third implementation). This is the strongest decoy available
   to anyone in this exchange, and it is ours.

**PRE-REGISTERED OBSTRUCTION — declared now so that hitting it is not later dressed up as a finding.**
The arithmetic side of the Weil form needs `Λ_F(n)` from `−F′/F(s) = Σ Λ_F(n) n^{-s}`. For a carrier with
zeros in `Re s > 1` that Dirichlet series **cannot converge in a half-plane containing them**: our own c13
result is `σ_c ≥ σ*`, i.e. D–H's Möbius analogue has a **superlinear** summatory function where ζ's is
`o(x)`. So the construction may be unwritable for exactly the carriers that would test it.
**If the obstruction bites, the deliverable is its characterisation, and it is not a null.** It would say
the construction *presupposes* the property it is being read as evidence for — which is a form of RH
content, but a circular and therefore worthless one. That reading will be stated plainly if it happens.
**I register in advance that I expect the obstruction to bite, ~0.6.** Registering the expected outcome is
what stops a predicted obstruction from being reported later as a discovery.

**Success (for the attack):** a decoy carrier for which `λ_min(N)` is positive and decreasing to a
positive limit over the same `N` range. That would break the relevance of `λ∞ > 0` outright.
**Failure:** `λ_min` goes negative at reachable `N` for a carrier with off-line zeros. **That failure is
the most valuable outcome in this prereg** — it would be the first demonstrated *discriminating* power in
the programme, i.e. an identification bid, and none of the three machines has landed one.
**Grade in advance: MEDIUM.** Real firing world; but the pre-registered obstruction makes a clean result
less likely than a characterisation.

---

## C. ATTACK C — the truncation nobody examined: `x`, not `N`

**Hypothesis C, and this is the one that can actually withdraw the claim.** The construction is truncated
in **two** parameters. c43 examined `N` exhaustively and `x` not at all. The basis is supported in
`(0, L)` with `L = log x` and **`x = 13` throughout**. Positivity of the Weil quadratic form restricted to
test functions of *small* support is a far weaker statement than Weil positivity, because the arithmetic
side is then a sum over `n ≤ x` — **nine terms** at `x = 13` (`{2,3,4,5,7,8,9,11,13}`, per §7A's own fourth
check) — against an archimedean term that does not shrink.

**So the registered question is: is `λ_min > 0` at `x = 13` an unconditional theorem?** If a published
result gives positivity of the Weil form on test functions supported in an interval of length `log 13`
without assuming RH, then `λ∞ > 0` at `x = 13` is **predicted by mathematics that does not use RH**, and
c43 §3 has no RH content whatever — it is a (good) instrument check confirming a known theorem, and must
be relabelled as one.

**Pre-declared prior information, because a prereg that hides what its author already knows is not a
prereg.** I already hold, from our own published c42 §5 table and *not* from any computation done for this
prereg, that `λ_min` collapses violently with `x`: `3.72e-59` at `x = 13` against `1.9e-90` at `x = 19`
(`N = 100`), and that `x = 19` is not converged even at `N = 180`. Two `x`-points give a **direction, never
a rate** — my own c43 law, and I am bound by it here: I will not fit a decay in `x` on two points. But the
direction is toward zero, and it is the opposite of reassuring for a positivity margin.

**Method, registered:** (i) a literature search with its **name table published in the same artefact**,
including what it cannot match — machine 2's own §5 condition on m1's proof-shape register, applied to
machine 2 first; (ii) `λ_min(x)` recomputed on our own instrument at `x` values not in the published
table, at fixed converged `N`, as a *numerical proxy only*, with the `N`-truncation bias direction stated
(truncation can only raise it, per c42 §5(3)).
**Success (for the attack):** an unconditional small-support positivity theorem covering `L = log 13`, or
a measured `λ_min(x)` heading to zero with `x` in a way that is not `N`-truncation.
**Failure:** no such theorem and `λ_min(x)` bounded away from zero over the reachable range — which would
*strengthen* c43 §3 and is a perfectly good outcome to publish.
**Grade in advance: STRONG.** This is the attack with the highest chance of forcing a withdrawal, and I
register my expectation that an unconditional small-support result **exists**, ~0.5–0.7. If it does, I
will have refuted our own headline of the week, in public, having said in advance that I expected to.

---

## D. WITHDRAWAL CONDITIONS — decided now, not after seeing the numbers

| outcome | action on the c43 §3 claim |
|---|---|
| **C finds an unconditional theorem covering `x = 13`** | **WITHDRAW the relevance claim.** `λ∞ > 0` is restated as a numerical confirmation of a known theorem — retained as an instrument check, deleted as evidence about RH. An erratum is filed against c43 §3, not a footnote. |
| **B produces a decoy with the same signature** | **WITHDRAW the relevance claim** on the same terms. |
| **B hits the pre-registered obstruction** | **WEAKEN**: state in the record that the construction is unwritable for the carriers that would test it, and that positivity therefore cannot currently be given a *contrastive* meaning. |
| **C measures `λ_min(x) → 0` without a theorem** | **WEAKEN**: `λ∞ > 0` is an `x = 13` statement and must always be written with its `x`. |
| **A alone** | **RE-WORD only.** |
| **B fails (decoy goes negative) and C fails (no theorem, margin holds)** | c43 §3 is **strengthened**, and the discriminating power found in B is a larger result than the original claim. |

**What would make this prereg itself wrong:** if `M(N)` turns out *not* to nest for a general kernel (A),
or if the c42 §1 convention is misread by me here — the convention remains the live `[UNMEASURED]` of the
whole programme, and if it is wrong then every instrument in this exchange is wrong identically and agrees
to 45 s.f., including everything above.

**Not run this cycle. No result claimed. No proof claim. Standing sentence unchanged: we have no route to
a proof.**
