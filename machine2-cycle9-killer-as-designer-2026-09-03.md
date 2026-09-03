# LEARNING THE KILLER, THEN USING IT AS A DESIGNER
### Machine 2, cycle 9 lane D1 — a causal-inference pass over our own 36-route mortuary, and the design sites it produces

**From:** machine 2 (BEAST), measured by beast-atlas
**To:** Mac (machine 1) and Prof. Glenn White
**Written:** 2026-09-03T08:22:03Z
**Corpus read, not recalled:** `G1-generator-candidates.md` (100,484 B), `G1-adversary-verdicts.md`
(136,417 B), `G1-predicted-vs-actual-killers.md` (5,868 B), `machine2-rediscovery-rate-2026-09-03.md`
(29,945 B). Coding, scripts and raw output: `/shared/rh-discovery/cycle9/`.
**Status:** every count below is `[MEASURED]` against a named file. Every model is `[DESCRIPTIVE]`,
n = 36. Nothing here is adjudicated by anyone outside machine 2.

---

## 0. The one-paragraph version

We have only ever pointed the adversary at candidates. This pass points it at *itself*: we coded all
36 dead routes by **structural** descriptors — what object the bridge lemma asks you to build, what
does the forcing, whether it needs a limit of finite objects, whether the positivity it wants exists
off the real axis — and asked what predicts **how the route died and what the kill cost**. Three
things came out, and the third is the one we would keep if you only read one line.

1. **A cheap pre-kill screen.** Six lookup filters, already implicit in our adversary's own
   cross-cutting failure modes, dispose of **26 of 36** routes at zero compute. Any future candidate
   should be run through them before anyone spends an hour on it.
2. **A map with real holes.** The 36 routes occupy **19 of 48** structural cells where their own
   marginals would put them in ≈24.7 (permutation p = 0.0013). The emptiness is a property of how we
   generate, not of n. Two whole *forcing genres* are effectively unused, and one is missing from our
   vocabulary entirely.
3. 🔑 **The theorems that killed us are the engines we never used.** Ten of the 36 routes (28 %) were
   killed by a theorem whose *subject is ζ itself* — Riemann–von Mangoldt, Littlewood, Hardy, Landau,
   Mellin–Plancherel, Rodgers–Tao. **Zero of the 36 use a proved ζ-native theorem as their forcing
   engine.** Every route imports its engine from a foreign field. That is not a defect the generator
   could have spotted: *"import a mechanism from another field"* was the instruction. It is a
   property of the instruction, measured after the fact, and inverting it is the cheapest new
   generation rule available to any of the three machines.

We also owe you three corrections that run against our own result, and one against machine 2's own
supervisor's prediction. They are in §1 and §5, not buried.

---

## 1. First, the trap, and the verification condition — published before any fit

The obvious target variable is *"did the route survive"*. It has **zero variance**: 36 of 36 died. A
model fitted on a constant outcome goes green because it has nothing to look at. So we published the
outcome distribution **before** fitting anything, as the gate on whether to fit at all.

| target | levels | counts | varies? |
|---|---|---|---|
| survived | 2 | DEAD **36** · SURVIVED **0** | 🔴 **NO — not modelled** |
| kill **class** | 4 | ARGUMENT 23 · COMPUTATION 7 · VACUOUS 5 · CITATION 1 | yes (largest 63.9 %) |
| kill **cost** | 3 | ZERO-compute 25 · COMPUTE 10 · CITATION 1 | yes (largest 69.4 %) |
| **stage** it died at | 5 | BRIDGE 18 · FORCING 10 · VACUITY 6 · HALF 1 · PREMISE 1 | yes (largest 50.0 %) |
| in the adversary's own hard-to-kill ranking | 2 | ranked 7 · unranked 29 | yes |

The kill-class column reproduces the adversary's own published counts exactly (23 / 7 / 5 / 1), which
is the audit that our recoding did not quietly drift. The **cost** column is taken from the
adversary's own effort denominator — *"items on which I ran an actual computation: 10"* — not from a
judgement made today.

**Denominator of our own search, hand-written so it can be attacked.** 12 structural axes considered,
**8 kept**, 4 dropped and named (seed discipline — a name, forbidden; the generator's own
difficulty-transfer label — known anti-correlated with truth, would import the bias as a predictor;
entry length in bytes; number of theorems invoked — **UNMEASURED**, we could not count it
reproducibly). Tests run: **8 features × 4 targets = 32**, all reported including the nulls, plus **5**
pre-specified hypotheses. **Denominator 37.** Benjamini–Hochberg over 37, and a feature is reportable
only if it also survives all 36 leave-one-out refits.

### 🔴 Correction 1 (against our own result): two of our findings are one finding

`transfer` (is the hardness a construction or an identity?) and `primes_enc` (are the primes natively
present, or encoded into a foreign object?) both came out corrected and LOO-stable. They are
**88 % collinear** (Cramér V = 0.882), and under stratification **neither survives conditioning on the
other** (p = 0.157 and p = 0.535). So there is **one** axis and we cannot say which label it is. We
report it as one.

### 🔴 Correction 2 (against our own result): our two cost measures disagree

`killcost` (was compute spent?) is strongly predicted. `hardrank` (the adversary's *own* ranking of how
hard the kill was) is predicted by **nothing** — every permutation p ≥ 0.39, for all eight features.
They are not measuring the same thing, and the honest reading is that **`killcost` measures whether
the claim was concrete enough to check numerically**, not whether it was hard to dispose of. Every
cost claim below is therefore a claim about *where compute was spent*, and we say so each time it
matters. The difficulty signal is **UNMEASURED at n = 7 ranked items**, not null.

### The associations, in full

Corrected and LOO-stable (BH q < 0.05, min LOO/full > 0.7):

| feature | target | V | perm p | BH q | LOO |
|---|---|---|---|---|---|
| primes_enc | killcost | 0.698 | 0.0001 | 0.002 | 0.97 |
| transfer | killclass | 0.624 | 0.0012 | 0.015 | 0.95 |
| primes_enc | killclass | 0.595 | 0.0027 | 0.025 | 0.95 |
| transfer | killcost | 0.667 | 0.0001 | 0.004 | 0.96 |
| primes_enc | stage | 0.580 | 0.0050 | 0.031 | 0.95 |
| forcing | killcost | 0.769 | 0.0047 | 0.035 | **0.56 — LOO-fragile, do not use** |

Everything else fails correction, including four of our five pre-specified hypotheses. **The nulls are
part of the result**: we predicted that routes needing a limit of finite objects would die cheaply
(they did not: Fisher p = 0.89), and that a COUNTING forcing would be expensive (p = 0.29).

One pre-specified hypothesis came back with **perfect separation**:

> **H4. spectral = 1 ⇒ the route is either VACUOUS or builds a banned object.** 10 of 10. Fisher
> p = 0.0014. Not one spectral-shaped route in the corpus produced anything else.

### The single-axis result, stated with its caveat

| cell | n | needed compute to kill |
|---|---|---|
| CONSTRUCTION-hard **and** primes encoded into a foreign object | 23 | **1** (4 %) |
| CONSTRUCTION-hard, primes natively present (C12, S2) | 2 | 1 |
| IDENTITY-hard **and** primes natively present | 11 | **8** (73 %) |
| IDENTITY-hard, primes encoded into a foreign object | **0** | — (the cell is empty; this is *why* the two features are collinear) |

⚠️ Read with Correction 2. This says the adversary could dispose of foreign-object constructions by
generic argument and had to compute against native claims. It does **not** say native routes are
better. It says foreign-object routes are refuted *without the adversary ever engaging ζ* — which is
a statement about what those routes were made of.

---

## 2. The screen: the part of the "learned killer" that is not a fit at all

Our adversary already published six cross-cutting failure modes. Read as a **lookup table applied to a
feature vector**, they are a pre-kill screen that costs nothing:

| filter | what it catches | n |
|---|---|---|
| **F1 periodicity** | ξ written as a limit of functions of `q^{−s}` or `e^{L(s−1/2)}` at fixed scale ⇒ N(T) linear, contradicting Riemann–von Mangoldt | 5 |
| **F2 real engine** | the positivity/order the forcing needs exists only for a *real* parameter | 11 |
| **F3 over-proof** | the mechanism delivers a clean `O(x^{1/2})` (Littlewood makes it false) or excludes the on-line zeros too (Hardy) | 6 |
| **F4 point vs line** | the construction produces the *numeral* ½, not the *locus* Re(s) = ½ | 7 |
| **F5 pairing is free** | a nondegenerate duality into a 1-dimensional object gives the functional equation, not weight ½ | 6 |
| **F6 self-specifying** | the bridge lemma specifies its object *by the property to be proved* | 4 |

**Union: 26 of 36 (72 %).** Of the 10 the screen lets through, **4 (40 %) required real compute** to
dispose of, against 6 of 26 (23 %) among the caught ones. That is the screen's whole value: it does not
find good candidates, it removes the free kills, leaving a residue that costs the adversary something.

🔑 **F3 is the one to design against, and it is the most useful sentence in this document.** Six kills
came from a mechanism that produced a bound *without the ε*. RH is `O(x^{1/2+ε})`; the clean
`O(x^{1/2})` is **false** by Littlewood. Concentration inequalities, martingale/CLT arguments,
least-action majorants and curvature bounds all deliver the clean version and are therefore refuted
before you build anything. ⇒ **a forcing engine is admissible only if it has an ε-shaped loss built
in.** That single constraint eliminates most of the physics-flavoured engine vocabulary at zero cost.

---

## 3. The map, and whether its holes are real

Cross of **object built** × **what does the forcing**, 8 × 6 = 48 cells:

| | POSITIVITY | DUALITY | RIGIDITY | COUNTING | REALITY | CLASSIFICATION |
|---|---|---|---|---|---|---|
| **OPERATOR** | C4 | · | · | C14 | C25 C27 I3 | · |
| **POLYFAM** | C8 C12 C13 | C2 C17 S4 | · | · | · | · |
| **MEASURE-DYN** | · | · | C1 C7 C10 C20 | · | · | C19 |
| **COMBIN** | C16 | C3 I2 | C9 | C15 C21 C23 | · | · |
| **GEOM** | C5 | · | C18 C22 | · | · | · |
| **CATSHEAF** | · | I1 | C26 | · | · | · |
| **FUNCTIONAL** | C6 I4 | · | · | · | · | · |
| **NONE-IDENTITY** | S1 S5 | S2 | · | C11 C24 S3 | · | · |

**Occupied 19 of 48.** Is that emptiness real, or just 36 routes in a 48-cell grid? Permutation test
(shuffle the forcing column, both marginals preserved exactly, B = 20,000): null mean occupancy
**24.69** (sd 1.71); observed **19**; **P(null ≤ observed) = 0.0013**. ⇒ **The corpus is significantly
more clustered than its own marginals require.** The holes are a property of how we generate.

Two facts the map makes visible that no route-by-route reading would:

- **REALITY is 3 of 36, and all three are the same cell**: OPERATOR, spectral, and banned under
  object-keying. We know exactly one way to use a reality constraint — self-adjointness. Every kill of
  that cell (C25, C27, I3) attacks the *operator*, never the *reality*. The reality engine itself is
  **UNTESTED** by this corpus.
- **CLASSIFICATION is 1 of 36**, and that one route produced the corpus's **only DEAD-BY-CITATION** —
  the only kill our adversary could not manufacture from generic properties and had to look up, and
  the one it flagged as *"the single verdict most exposed to citation error"*.

Marginal compute-spend, the only model n = 36 supports (additive, no interactions estimable):

| object | n | needed compute | | forcing | n | needed compute |
|---|---|---|---|---|---|---|
| POLYFAM | 6 | **5 (83 %)** | | COUNTING | 7 | 3 (43 %) |
| FUNCTIONAL | 2 | 1 | | DUALITY | 7 | 3 (43 %) |
| NONE-IDENTITY | 6 | 2 (33 %) | | POSITIVITY | 10 | 4 (40 %) |
| COMBIN | 7 | 2 (29 %) | | **RIGIDITY** | 8 | **0 (0 %)** |
| **OPERATOR** | 5 | **0** | | **REALITY** | 3 | **0** |
| **MEASURE-DYN** | 5 | **0** | | CLASSIFICATION | 1 | 0 |
| **GEOM** | 3 | **0** | | | | |
| **CATSHEAF** | 2 | **0** | | | | |

---

## 4. 🔑 The inversion that matters: our killers are engines we never tried

Two columns, both read off the two documents:

- **ENGINE** = the mechanism named in field *3. Forcing mechanism* of each candidate.
- **KILLER** = the theorem named in the adversary's KILLING LAYER column and its provenance block.

**Proved ζ-native forcing engines among the 36: zero.** (Three items — S2, S3, S5 — are native in
*name*: S2's midpoint operation and S3's per-zero parity bookkeeping are **hypothesised, and both were
refuted**; S5 is an invertible change of variable graded VACUOUS. So the count of *proved* native
engines is 0/36, denominator 36, no exclusions.)

**Distinct routes killed by a theorem whose subject is ζ: 10 of 36 = 28 %** — C1, C3, C5, C8, C9, C14,
C16, I2, S2, S4.

| ζ-native theorem | routes it disposed of | ever used as an engine? |
|---|---|---|
| Riemann–von Mangoldt `N(T) ~ (T/2π)log(T/2π)` | **5** (C3, C8, C16, I2, S4) | **NO** |
| Littlewood `Ω±(x^{1/2}logloglog x)` | 2 (C5, C9) | **NO** |
| Hardy 1914 (infinitely many zeros *on* the line) | 2 (C1, S2) | **NO** |
| Landau (non-negative Dirichlet coefficients) | 1 (C1) | **NO** |
| Mellin–Plancherel completeness of the Re = ½ axis | 1 (C14) | **NO** |
| Rodgers–Tao `Λ ≥ 0` | 1 (C8) | **NO** |

Of the 17 distinct killer theorems in the corpus, **15 were never used as an engine by any route**.

**What this licenses, and what it does not.** Licensed: the 0/36 count, with an auditable column.
**Not licensed:** "therefore ζ-native engines would work". The obvious objection is that they are
circular — `N(T)` and Littlewood's Ω are both perfectly consistent with RH being false, so neither
forces anything on its own. The claim the data supports is weaker and still worth acting on: these
engines are **untried**, they are the only engines in the room with a *demonstrated* ability to decide
a question about ζ, and the corpus cannot say whether they are circular **because it never asked**.

---

## 5. Re-keying the ban on the OBJECT BUILT rather than the MECHANISM USED

Machine 2 promised Prof. White on 09-02 (item 4) to re-key our generator's ban list. The eight banned
mechanisms (HP / RMT / Li / Nyman–Beurling / de Branges / Weil-explicit / Connes / Selberg) require you
to build one of only **four** objects:

- **B1 spectral realisation** — an operator, algebra, flow, length- or resonance-set whose spectrum is
  the zero ordinates.
- **B2 positivity functional** — a quadratic form or functional on test functions whose positivity is RH.
- **B3 coefficient-positivity** — a family of finite polynomials converging to ξ whose root location is
  deduced from positivity of its coefficients.
- **B4 Hilbert-space closure** — a closure/approximation statement for a span in a function space.

A route is object-banned iff its **bridge lemma** asks you to construct a B1–B4 object, whatever
theorem it then hopes to apply.

| rule | banned, of 36 | routes |
|---|---|---|
| mechanism-keyed, unambiguous (the blind disguise audit, 2026-09-01) | **10** | C4 C12 C13 C14 C19 C25 C27 I1 I3 I4 |
| mechanism-keyed, + borderline | 13 | + C16 C18 C22 |
| **object-keyed, tight** | **15** | + C8 C16 C17 C22 S4 |
| object-keyed, loose | 18 | + C6 C18 S5 |

### 🔴 Correction 3 — this is the opposite of what machine 2 expected

The brief for this lane predicted: *"If that number is small, the ban was doing far less work than we
believed."* **Measured: it binds more, not less. 10 → 15, i.e. 28 % → 42 % of the corpus.** And the
containment is strict: **zero** routes are caught by mechanism-keying and missed by object-keying. The
object rule *dominates* the mechanism rule.

The five extra catches split into two shapes, and the second one is the finding:

- **C16, C22** were graded *borderline* and object-keying decides them. A complex length spectrum and
  an eigenvalue family of explicit integer matrices **are** spectral realisations, whatever theorem you
  then invoke.
- **C8, C17, S4** were never flagged at all — and all three build the **same** object, B3, reached from
  Lee–Yang ferromagnets, non-standard analysis, and palindromic divisor polynomials respectively.
  **None of those three names a banned mechanism.**

🔑 **The mechanism list has a systematic hole: it names 8 mechanisms, but those 8 build only 4 objects,
and object B3 has entrances from outside the list.** The generator's header says *"3 allowed, 3 used"*.
The true spend, object-keyed, is **15** — understated by a factor of five.

**Three consequences, stated plainly.**

1. **This makes our rediscovery confound worse, not better.** Our 09-03 letter reported 8 of Mac's 10
   routes lying inside the banned region and argued the low rediscovery rate measures our exclusion
   rule rather than the space. The excluded region is *larger* than we said. The argument gets
   stronger and our corpus's coverage claim gets weaker.
2. **If the intent is to attack where the literature's mass sits, re-keying the ban does not do it —
   only lifting it does.** We should say that rather than shipping a tidier ban and calling it access.
3. **The re-key's real value is different and still worth having: it is decidable at *generation*
   time.** "What does the bridge lemma ask you to build?" is answerable from the candidate's own §5,
   by the generator, before anything is written. The mechanism rule needed an adversarial reading and
   still leaked four disguises.

---

## 6. THE DESIGN OUTPUT — ranked sites, with the reason the map says each is expensive

**How to read the ranking.** The deliverable is the **structural descriptor** and the map's reason.
The named instantiations are *illustrations*; killing an instantiation does not kill the cell, and we
would rather you shot at them than at nothing. Each site states which of F1–F6 it passes and whether
it is object-banned. Sites are ranked by strength of the evidence behind them, not by our enthusiasm.

---

### SITE 1 — ζ-NATIVE FORCING ENGINE · evidence: 0/36 occupancy, 28 % of kills · **strongest**

**Descriptor.** The theorem doing the forcing has ζ, its zeros, or ψ(x)/π(x) as its *subject*. A
foreign object may supply the *statement*; it may not supply the *engine*.

**Why the map says it is expensive to kill.** A route whose engine is Riemann–von Mangoldt, Littlewood
or Hardy cannot be killed *by that theorem* — you have removed the three cheapest weapons in the
adversary's arsenal from play, and those three account for 9 of 36 kills. It also satisfies the
adversary's own cheapest unmet test for free: *"Hardy's theorem is the cheapest possible test and no
item ran it."*

**Screens.** Passes F1 (needs no exponential-variable limit), F2 (N(T) and Ω-results are
complex-analytic, not real-order), **F3 by construction** — an Ω-result is a *lower* bound and the
over-proof failure mode is always an upper bound that is too clean — F5, F6. Not B1–B4.

**Instantiations.**
- **1a. The integer-valued deficit.** `N(T) − N₀(T)` is a non-negative *integer* for every T. The
  entire literature attacks this by pushing the proportion (Selberg → Levinson → Conrey → ~41.7 %).
  The unexplored structural move is to stop pushing the proportion and instead **sandwich the deficit
  between a lower bound and an upper bound that meet**, using its integrality as the closing step.
  Forcing genre: integrality (site 2), object: none, natively arithmetic.
- **1b. Ω as an engine.** Every route in the corpus assumed off-line zeros make ψ(x) − x *too big*.
  None asked whether an off-line quadruple forces some explicitly computable quantity to be *too
  small*, contradicting a known Ω-result. ⚠️ **Flagged BORDERLINE B2** — if the instantiation ends up
  as positivity of a functional on test functions it is Weil-explicit and does not count as new. A
  second-moment identity is not that; a test-function cone is.

**First falsifiable step (cheap).** For 1a: compute, for T up to the verified frontier, whether any
known upper bound on `N(T) − N₀(T)` is within an additive constant of zero anywhere. If the gap is
provably Ω(T log T) under current technology, the site is closed in an afternoon and we have lost
nothing.

---

### SITE 2 — INTEGRALITY / DEFINABILITY AS A FORCING GENRE · evidence: a **seventh genre**, 0/36

**Descriptor.** The forcing is *"an explicitly computed quantity must lie in a discrete set"* (ℤ, a
lattice, a finite list of allowed values), and an off-line zero makes it non-discrete. Not positivity,
not duality, not uniqueness, not a spectrum.

**Why the map says it is expensive to kill.** It is structurally immune to **four of the six cheap
filters**: F2 (integrality is not an order or a cone, so it needs no real parameter), F3 (a
discreteness constraint is not an upper bound and cannot over-prove into the false clean `x^{1/2}`),
F4 (integrality of a *t-dependent* quantity yields a **locus**, not a numeral — and point-vs-line is
our single most common failure, 7 of 36), F5 (integrality is not a pairing). **This is the only region
we found for which our own filter battery is silent.**

⚠️ **Caveat, load-bearing:** the silence of our filters is evidence about *our filters*. It is a good
place to look because we learn something either way, not because we predict it works.

**Evidence from inside the corpus.** Kronecker's theorem *is* an integrality forcing, and it killed two
routes (C16, C18). It was never an engine. This region is the clearest single instance of §4.

**Instantiations.**
- **2a. Crystallographic-restriction shape.** A quantity computed from a zero-pair must be the trace of
  an integer matrix, hence an algebraic integer in a bounded family; an off-line pair's invariant is
  not.
- **2b. Ehrhart / lattice-point count** on the Newton polytope of a divisor-polynomial family; RH as an
  exact lattice-point identity rather than an inequality.
- **2c. Pila–Wilkie / o-minimality.** On a bounded box the restriction of ξ is definable in `R_an`.
  Pila–Wilkie bounds the number of rational points of bounded height on the *transcendental* part of a
  definable set by `O_ε(H^ε)`. An off-line zero at Re = ½ + δ is a point with a constrained coordinate
  on such a set. ⚠️ **Two honest holes, stated so you can shoot at them rather than at us:** δ need not
  be rational, and `O_ε(H^ε)` does not exclude finitely many points. The site is worth its place
  because the first falsifiable step is very cheap — compare the Pila–Wilkie permitted count against
  `N(T)` in the same box and see whether the two are even in tension. If they are not, the whole
  o-minimal direction closes for a few hours' work.
- 🔑 We flag 2c as the item most likely to satisfy Prof. White's *"a distinctive approach that differs
  from the way a human mathematician might approach it"*: no RH programme we are aware of reaches for
  definability, and it is not on the eight-mechanism list under any reading.

---

### SITE 3 — CLASSIFICATION **WITH EXCEPTIONS**, NOT UNIQUENESS · evidence: 1/36 genre, and the design rule below

**Descriptor.** Force RH by a classification that has an infinite family **plus finitely many
exceptions** (ADE shape): RH = *"ζ's data lies in the infinite family, not among the exceptions"*.

**Why the map says it is expensive to kill.** Killing a classification route requires **knowing and
applying the classification** — it is the one kill in the corpus the adversary could not manufacture
from generic properties, and it is our only DEAD-BY-CITATION.

🔑 **The design rule, extracted from the map and worth more than the site: replace every UNIQUENESS
forcing with a DICHOTOMY forcing.** RIGIDITY/uniqueness is the second-largest genre block (8 of 36),
**0 of 8 cost the adversary any compute**, and over-proof (F3) catches 3 of the 8 (C1, C7, C9). A uniqueness
theorem strong enough to exclude the off-line configuration excludes the on-line ones too — that is
exactly what killed C19, whose classification was *complete* and therefore left no room for anything,
including the zeros Hardy proved are on the line. A classification with exceptions does not have that
failure mode: it permits an infinite family and forbids only the exceptional list.

**Screens.** Passes F1, F2, F4, F5, F6. **F3 is the live danger and the descriptor is written to
avoid it** — if the classification is a uniqueness theorem in disguise, this site collapses into C19.

**Instantiations.** Finite-type quiver / ADE classifications; crystallographic groups; association
schemes; the finitely many exceptional Weyl groups.

---

### SITE 4 — POLYFAM × COUNTING · evidence: top-scoring **empty** cell in the map

**Descriptor.** A family of finite polynomials built from ζ's *own* data, forced by an exact count that
is **not a root count**. (Root counting via Sturm/Descartes/Jensen is B3 and is banned by
object-keying — that is what §5 catches in C8, C13, C17, S4.)

**Why the map says it is expensive.** POLYFAM is the object class with the highest compute-spend —
**5 of 6 (83 %)** required the adversary to compute; it could not dispose of a polynomial family by
generic argument. COUNTING supplied 3 of the 7 hard-ranked residues. Their intersection is **empty**.

⚠️ **This is an extrapolation into an empty cell from additive marginals.** n = 36 cannot estimate the
interaction. It is a prediction, not a measurement, and we label it as such.

**Counts that are not root counts:** number of irreducible factors over ℚ; Galois group order;
discriminant valuation at a small prime; number of integer points under a Newton polygon.

**Instantiation.** The factorisation type over ℚ, and the discriminant valuation at small primes, of a
divisor-polynomial or partial-sum family as N grows. ⚠️ Partial sums of ζ have zeros far off the line
(Montgomery), so the family must not be a truncation of ζ — F1 and the C17 kill both apply.

---

### SITE 5 — REALITY **OFF** THE OPERATOR OBJECT · evidence: 0/36; reported UNMEASURED, not expensive

**Descriptor.** A reality constraint that is *not* self-adjointness: reality of a Galois action; a real
structure / anti-holomorphic involution whose fixed locus is the critical line; reality forced by
definability or by an integrality.

**Why it is here.** All three REALITY routes are OPERATOR, spectral and object-banned, and **all three
kills attack the operator, never the reality**. The corpus therefore contains *zero* evidence about the
reality engine. We rank this as **unoccupied and untested**, not as predicted-expensive — the
distinction matters and we are not going to blur it.

⚠️ **F5 trap:** an involution *alone* is the functional equation, which is the free half (5 seeds
rediscovered it). The reality must be forced by something other than the involution.

---

### SITE 6 — GENERATION MIX, not a site: invert the object/transfer axis

Measured: 8 of 11 identity-hard, natively-arithmetic routes needed a computation to kill, against 2 of
25 construction-hard, foreign-object routes. Our generator spent **25 of 36** on the side that dies for
free. ⚠️⚠️ **Read with Correction 2:** this may measure checkability rather than strength, and our own
difficulty ranking shows no such pattern. We offer it as a *generation-mix* recommendation with that
caveat attached, not as a claim that native routes are better.

---

### SITE 0 — THE ANTI-REGION: what to stop generating (cheapest output of the whole pass)

- 🔴 **Stop generating spectral-shaped routes.** 10 of 10 were VACUOUS or built a banned object
  (Fisher p = 0.0014). Perfect separation. In 36 attempts the spectral shape has produced no
  information of any kind.
- **OPERATOR / MEASURE-DYN / GEOM / CATSHEAF objects:** 0 of 15 combined required any compute to kill.
- **RIGIDITY/uniqueness forcing:** 0 of 8 required compute; see the dichotomy rule in Site 3.
- **Any limit of finite objects in an exponential variable:** pre-killed by Riemann–von Mangoldt at
  zero cost, five times already.

---

## 7. What we could not determine — UNMEASURED, with the reason

- **What a *blind* coder would produce.** The coder had already read the verdicts before coding the
  features. Every feature cell carries the generator-side clause it was read from, so a third party can
  re-code from the pre-existing text and diff — but that diff has not been run. This is the single
  biggest threat to §1 and we are not going to describe it as controlled.
- **Whether kill *difficulty* has any structural predictor.** n = 7 ranked items; every permutation
  p ≥ 0.39. Unmeasured, not null.
- **Whether the six screens generalise beyond this corpus.** They were derived from it. Applying them
  to Mac's ten routes would be the first genuine out-of-sample test and we have not run it.
- **The causal claim.** Nothing here is an intervention. We fitted a descriptive model to an
  observational corpus of 36 items generated by one instruction and killed by one adversary. Every
  arrow in this document is *"the map says"*, never *"therefore"*.
- **Number of theorems per route** — we could not count it reproducibly from the text without a
  judgement call per clause, so it was dropped rather than measured badly.

---

## 8. The falsifiers, so this is a claim and not a story

1. **Blind re-coding.** Hand `G1-candidates-for-adversary.md` (verdict-free) to a coder who has never
   seen `G1-adversary-verdicts.md`, have them fill the same 8 feature columns, and diff. If the
   feature columns move on more than ~5 of 36 rows, §1 is not safe.
2. **Out-of-sample screen.** Run F1–F6 against Mac's ten routes. Our model predicts the screen fires on
   few of them, because they sit in the classical programmes rather than in imported foreign
   mechanisms. If it fires on most, the screen is fitting our generator's style, not mathematics.
3. **The object-keyed ban.** Re-run the disguise audit under DEF-BANOBJ with a different adjudicator.
   If object-keying does **not** dominate mechanism-keying — if even one route is mechanism-banned and
   object-free — §5's central claim fails.
4. **Site 1.** If someone shows every ζ-native engine is circular by a general argument, Site 1 closes
   and the whole §4 inversion becomes a curiosity rather than a lead.
5. **The clustering result.** Recompute occupancy under a different structural coding. If a coding of
   equal defensibility puts occupancy at ≥ 24 cells, the "the holes are real" claim in §3 dies and the
   inversion has to be ranked on cost alone.

---

## 8b. Provenance of the literature claims in §6 — UNVERIFIED AT PRIMARY in this run

This pass fetched **no** external sources. Every named theorem in the design sites is quoted from
memory of the standard literature and carries that caveat rather than having it dropped:
Riemann–von Mangoldt · Littlewood Ω± · Hardy 1914 · Landau · Kronecker · Rodgers–Tao Λ ≥ 0 ·
Montgomery (zeros of partial sums of ζ lie off the line) · Pila–Wilkie (`O_ε(H^ε)` rational points on
the transcendental part of a definable set) · `R_an` definability of a real-analytic function
restricted to a compact box · the critical-line proportion series (Selberg → Levinson → Conrey ≈ 40 % →
Pratt–Robles–Zaharescu ≈ 41.7 %) · Ehrhart · the crystallographic restriction · ADE / finite-type
classifications.
**No count, model or verdict in §§1–5 depends on any of them** — those rest only on the two G1 files
and the scripts. The literature enters only in §6, where it names *where to look*, and a
misremembered attribution there costs a site, not a result. Sites 1a, 2c and 4 should be checked
against primary sources before anyone spends a day on them.

---

## 9. Reproduction

```
/shared/rh-discovery/cycle9/
  r9_coding.py     36 rows: 8 structural features, 4 graded targets, provenance clause per row
  r9_analysis.py   steps 0-5: distribution, denominator, associations, occupancy, ban re-key, inversion
  r9_confound.py   collinearity + stratified conditioning + the six-filter screen
  r9_engines.py    engines vs killers, the 0/36 native-engine count
  *.out            raw output of each, as run
```
`python3 r9_analysis.py` reproduces every number in §1, §3 and §5 in about 18 s, no third-party
libraries, seed 20260903.
