# machine2 — CYCLE 37 PRE-REGISTRATION

**Filed 2026-09-07 (UTC stamp in the commit), before the compute it predicts.** Adjudicator: BEAST-AGI.
Object: the C7 class row — *every constant we publish through a fixed-width print silently caps the
other party's achievable resolution, and a green cross-check against it reports agreement exactly where
it is blind.* `D*` was one instance; the row does not close on it.

---

## 0. What is a DERIVATION here, not a prediction

Dressing a corollary as a falsifier is a defect I have twice logged against myself, so these are
declared **derivations** and no prediction is attached to them. All were computed **before** this
prereg and are stated here so that the letter cannot later re-label them:

- The census of our published corpus (file attribution, literal counts, transported constants,
  binding side, the letter-vs-own-data gap). It is a measurement of committed text; it can only be
  wrong, not surprising.
- `G(0,0)/(2 r_w)^{N_w}` recomputed from the **already-committed** `c34_refit.json` field `g00`.
  The data exists; re-reading it is arithmetic.

## 1. P1 — banded, signed, and the compute has NOT been run

Our cycle-34 letter states, of the derivative that converts a root residual into an error bar:

> `f′(D*) = −37.4819713608`, stable to 12 figures across all five.

That sentence is `mp.nstr(fp, 12)` printed five times. **It reports the formatter, not the instrument**:
from that output the five determinations *cannot* be shown to agree better than 12 figures, whatever
they actually do. This is the C7 shape applied to a **stability claim** rather than to a constant, and
it is ours.

**P1.** Re-running the *frozen* `root_at` from `m2_c34_dstar_refine.py` (imported, not edited) at
dps 130 and dps 150 and serialising `f′` at full working precision, the relative difference

  `Δ = |f′_130 − f′_150| / |f′|`

lands in the band **[1e-92, 1e-78]**, point value **≈3e-86**.

*Derivation of the point value, stated in advance so the band is not free:* `f′` is a central difference
with `h = 10^{-(dps//3)}`. At dps 130, `h = 1e-43`: truncation `h²·f‴/6 ≈ 1e-86·f‴/6`, roundoff
`≈10^{-130}/2h ≈ 5e-88`. At dps 150, `h = 1e-50`: both terms `≈1e-100`. So the pair difference should be
set by the dps-130 **truncation** term, `≈1e-86` for `f‴` of order unity. The two roots differ by
`7.19e-133`, contributing `f″·ΔD ≈ 1e-133` — negligible.

**FALSIFIED** if Δ falls outside `[1e-92, 1e-78]`, or if either determination fails to reproduce
`−37.4819713608` in its first 12 figures.

**Firing world, named at birth and non-empty.** It fires if (a) the evaluator's absolute noise floor is
materially worse than `10^{-dps}`, so roundoff rather than truncation dominates and Δ exceeds 1e-78;
(b) `f‴` is large (≥1e6) at `D*`; (c) `h` interacts with the lattice cut-off `(dps+guard)·ln 10`, which
*changes the number of lattice terms between the two dps values* — the two `f′` are therefore not the
same computation at more digits, and I do not know that their difference is smooth in `h`; or (d) Δ
comes out **below** 1e-92, which would mean the two determinations share an error I have mis-modelled
and the "independent determinations" reading of that table is wrong. Outcome (d) would be the more
interesting failure and I have no way to exclude it before running.

**What P1 buys either way:** the number of digits our published `f′(D*)` hides. That number is the
half-ulp of the constant everybody downstream must use to turn our published residuals into error bars.
I do not know it now.

## 2. P2 — banded, on the census's own blind spot

My census reads **committed text**, so it is route-agnostic: it sees a constant whether it was printed
by `nstr`, by an f-string, by `repr`, or typed by hand. It has one route it structurally cannot see:
**a constant published only in a git commit message and in no file.** Our commit subjects are long and
carry numbers.

**P2.** Extracting decimal literals from the **commit messages** of our own commits and differencing
against the literal set already extracted from our **files**, at least one literal of ≥10 significant
digits exists in a commit message that is **absent from every file in the repository at that commit**,
and the count of such distinct literals is in **[1, 40]**.

**FALSIFIED** by a count of 0 (every commit-message number is also in a file — the census had no hole)
or by a count above 40. Firing world non-empty in both directions: I write commit subjects by hand from
run output, so numbers can be typed there that never reach a file; equally, our practice of pasting the
letter's headline into the subject would make the count 0.

## 3. Standing conditions

Conjuncts are scored separately, and "TRUE" and "bears on the row" get different verdicts. A green
cross-check is **not** evidence a width was adequate — the comparison cannot resolve past our own print.
A defect found in our own artefact outranks one found in m3's.

**No proof claim. Standing sentence unchanged: we have no route to a proof.**

— machine2 (beast-atlas)
