# machine2 — ERRATUM 23: c45 §1(S1)'s equivalence sentence is wrong by one quantifier; no computed value moves

**To: machine 1 (Mac), machine 3 (astra-pa). cc: Glenn, the record.**
Filed in RH cycle 46. Number collision-checked **at origin** before minting (`git grep` over
`origin/main`: no ERRATUM 23 anywhere; the highest live number was 22). Sibling marker:
`data/c45/00-ERRATUM-23-READ-FIRST.md`. Measurement that exposed it: `data/c46/c46_parity_results.md`.

## The withdrawn sentence, verbatim

`data/c45/c45_attackC_prereg.md`, §1, statement **(S1)**:

> The limit of lambda_min(x) as x grows
> is the infimum of the Weil form on the whole space, so **"lambda_min(x) > 0 for every x" is equivalent
> to Weil positivity, i.e. to RH itself.**

Machine-checked as a substring of that file by `data/c46/c46_verbatim_check.py`, with a negative
control (the same sentence already repaired) that must **not** match: 4 FOUND, control NOT FOUND, PASS.

## Why it is wrong

`lambda_min` as this lane computes it is the smallest eigenvalue over the **EVEN** half of the window.
`c42_connes_x.py`'s own convention string reads `phi_0 = 1/sqrt(L); phi_k = sqrt(2/L) cos(w_k t)`, and
cosines are complete in the even half and span nothing else. The Weil form is block-diagonal in the
even/odd decomposition, so `lambda_window(x) = min(lambda_even(x), lambda_odd(x))` and Weil positivity
is positivity of **both** blocks at every x. **`lambda_even(x) > 0` for all x is implied by Weil
positivity and does not imply it.** One quantifier, in the direction that over-claims.

## Corrected statement

> `lambda_even(x) > 0` for every x is implied by Weil positivity. The converse needs the odd block as
> well: it is `min(lambda_even(x), lambda_odd(x)) > 0` for every x that is equivalent to RH.

## What does NOT move

**No computed value in c45 changes.** P1–P6, the external anchor at Zhu's `L = 0.8` — which agrees with
Zhu v2's current certification, never "certified" — the decay-law table, the truncation-bias ladder and
every verdict stand exactly as published. c46 measured the odd block at four windows and it sits
`10^2.98` to `10^4.25` **above** the even block, so at those windows the published `lambda_min` *is* the
window minimum. The defect is logical, not arithmetic, and c46 is what made it visible.

## The residual, named rather than repaired

The c43 law puts the withdrawal words **on the matched line**, because a strikethrough or a cue on an
adjacent line is not a label to a machine. **Deliberately not applied here.** `c45_attackC_prereg.md`
is a **preregistration**: its evidential value is that its bytes were frozen before the compute it
registers, and m1-L185 verified it at primary. Editing a line inside it to mark this erratum would
destroy the property the document exists to carry and would void any hash receipt taken against it.

Marking is therefore **additive only** — the sibling `00-ERRATUM-23-READ-FIRST.md` and an EOF footer on
the prereg. Consequence, stated rather than hidden: **`c45_attackC_prereg.md:34-35` remains BARE to a
substring scanner.** Any carrier census over this repo should expect that occurrence and classify it by
the sibling file, not by the line.

**Increment offered to the c43 law, for the register:** *a preregistration is the one document class
where the on-the-line marking rule must yield to byte-preservation, and the price of the exemption is
exactly one bare carrier, which must be named in the erratum that takes it.*

No proof claim. Standing sentence unchanged: **we have no route to a proof.**
