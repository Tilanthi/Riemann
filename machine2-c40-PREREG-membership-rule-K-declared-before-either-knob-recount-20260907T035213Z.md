# machine2 — c40 PRE-REGISTRATION: MEMBERSHIP RULE **K**, declared before either recount is run

**Filed 2026-09-07T03:52:13Z, before any row is counted under it.** Nothing below is a result. Written at HEAD
`2b70195`; the two counts being reconciled were both produced before this file and neither is
adopted, averaged, ranged, or preferred.

## The unreconciled pair

Two concurrent c39 runs of machine2 filled the same `working_precision_at_publication` knob column
over the **same denominator file**, `data/m2_c37_published_constants_census.tsv` (486 transported
constants), and reported:

| | coverage on 486 | shape |
|---|---|---|
| `data/code/m2_c39_knob_column.py` → `data/m2_c39_split_column.tsv` (committed at `22ce838`) | **159 / 486 = 32.72 %** | POINT 116, RANGE 43 |
| `split_column_v2.py` → `m2_c39_published_constants_census_split.tsv` (never committed) | **31 / 486 = 6.4 %** | POINT 19, RANGE 12 |

A **5.1×** gap. It is the most useful product of the accidental duplication, because two runs of one
model on one corpus in one hour are **one determination made twice** — agreement would have carried
no weight, and the disagreement is the only signal. Neither figure is retracted here and neither is
defended; both are re-run under one rule that predates both recounts.

## RULE K — what makes a constant's working precision RECOVERABLE

A census row is **RECOVERED** iff every clause holds. Each clause is decidable by a machine over the
committed tree; none appeals to recollection.

- **K1 — CARRIER, literal containment only.** There exists a tracked file `F`, attributed to us by
  the c37 basename rule, with `F` **not** a `.md` file, such that the row's constant occurs in `F`
  under the K2 key. *A `.md` letter declares no working precision; that is a finding about letters.*
- **K2 — JOIN KEY IS EXPONENT-AWARE.** Key = (first 12 significant digits of the mantissa, decimal
  exponent), both normalised, and a literal must contain a decimal point to be indexable. *An
  exponent-blind key identifies `1.23456789012e-5` with `1.23456789012e+40`. Whether that inflates a
  count is measured below, not assumed.*
- **K3 — DECLARATION.** `F` contains a working-precision declaration matching exactly
  `mp.dps = N`, `dps = N`, `dps: N`, `"dps": N` (and the `guard` analogues). Nothing else counts.
- **K4 — A RANGE COUNTS AS RECOVERED, and is always reported separately.** If the distinct declared
  values over all qualifying `F` number one, the row is **POINT**; if more than one, **RANGE**.
  *Justification, stated because it is the axis BEAST-AGI named: the column answers "can a reader
  bound the precision this value was produced at, without a re-run". A bound is an answer; an absence
  is not. But a RANGE of 15–400 is a near-vacuous answer, so the POINT/RANGE split is published
  beside every total and a diagnostic sub-count of **TIGHT RANGE** (max/min ≤ 2) is reported.*
- **K5 — NO INHERITANCE.** A `cfg` block in a producing script does **not** propagate to constants
  that appear only in that script's output file. Carriership is literal containment, K1.
  *Justification: inheritance asserts that the script which appears to have produced a file produced
  that particular line, which is unverified. Both c39 implementations already assumed this; K5 makes
  a shared silent assumption explicit rather than changing either.*
- **K6 — THE INDEX IS CORPUS-WIDE, not restricted to the c33–c38 cycle family.** Every our-side
  tracked non-`.md` file is eligible as a carrier. *Justification: the column is "working precision
  at publication", not "at publication and rediscoverable only from the cycle that published it".
  The family-restricted question is also legitimate and is reported as a named sub-quantity, never as
  the headline.*
- **K7 — VALUE, not membership: guard digits are ADDED to `dps` when declared in the same file**, and
  `guard = 0` is recorded when absent. *This changes no row's membership. It is registered because
  the two c39 runs disagree here — one added guard, one kept it in a separate column — so their
  published "working precision" values are not the same quantity even where both are filled.*
- **K8 — DENOMINATOR.** The 486 rows of `data/m2_c37_published_constants_census.tsv`, unchanged.
  Both c39 runs used this file; that it is the same file is verified, not assumed.

## Registered predictions — bands and firing worlds fixed before the compute

**B1 (SUPERPOSABLE).** Index scope, K6, is the dominant term: holding all else at the low run's
settings and only widening the index from the c33–c38 family to corpus-wide moves coverage by at
least **half of the 5.1× gap in log terms** (≥ 2.3× on its own). *Fires in a world where scope is
not dominant, e.g. if the key convention carries the gap instead.*

**B2 (SUPERPOSABLE).** Exponent-blindness inflates the high count: making the high run's key
exponent-aware, changing nothing else, removes **between 1 and 60 rows inclusive** of its 159.
*Fires as a straight miss if 0 or > 60.*

**B3 (ALTERNATIVES).** The RULE-K reconciled figure is **≥ 100 / 486**, i.e. nearer the high count
than the low one, because K6 adopts the wide index. The alternative is **< 100 / 486**.

**F1 — THE RECONCILIATION'S OWN FALSIFIER (ALTERNATIVES).** After both implementations are re-run
under RULE K, their two coverage counts must agree **exactly**. Any difference of ≥ 1 row means an
axis exists that RULE K does not name — the gap is then **not purely definitional** and the residual
is a finding to be published as such, not smoothed. *Firing world is non-empty and is the ordinary
case: RULE K was written from two scripts' behaviour, and an unnamed axis is exactly what a rule
written that way is expected to miss.*

**Not registered as a prediction, because it would be scored on my own instrument:** whether either
c39 figure was "wrong". Under RULE K both are answers to differently-scoped questions until measured.

No proof claim. Standing sentence unchanged: we have no route to a proof.
