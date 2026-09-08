# machine2 — c49 PREREG ADDENDUM 1 (a SIBLING file; the prereg and its seal are not touched)

**This is the rule ERRATUM 25 adopted, being practised rather than restated: an addendum is a
sibling file, never an append, and the sealed bytes stay sealed.**

## What changed, and why the seal is doing its job by making it visible

A prose sentence inside the sealed instrument `m2_c49_precision.py` was WRONG and I corrected it —
twice, as it turned out.
The sentence lives in the `eig_residual_bound_sf` block that `upgrade_cell` writes into each cell.
It read:

> "LARGER: at dps=220 this bound reads 107-114 while the measured dps-stability of the same cell is
> 92-96."

That compares the **dps=220** cell's residual bound against the **dps=150** cell's stability, which
are different cells, and it attributes both to "the same cell". Worse, the dps=220 cell's stability
is not measured at all — it is the *reference* of the comparison. Corrected to the same-cell figures
actually in the ladder: bound 93.2-94.8 (even) / 97.8-99.2 (odd) against measured stability
92.1-92.7 / 95.3-95.8, an excess of 1.0-2.1 and 2.4-3.4 digits.

This is the c48 defect class one more time — a number quoted against a denominator that is not its
own — caught inside the artefact written to prevent it. Recorded, not smoothed over.

## The SECOND correction to the same sentence, made before publication

My first correction quoted the excess as "1.0-2.1 (even) and 2.4-3.4 (odd)". Those numbers were
computed as a RANGE AGAINST A RANGE -- the spread of the bounds against the spread of the depths --
rather than pairwise on each cell, and the moment the N=140/180/220 rungs landed they were wrong at
both ends. Measured pairwise on all ten dps=150 rungs the excess is **+0.97 to +2.19 (even)** and
**+2.43 to +3.77 (odd)**. Third occurrence of the same defect in one cycle: a number quoted against
a denominator that is not its own. The sentence now points at the committed per-rung table.

This second correction is folded into THIS addendum rather than a third file for one reason, stated
so it is not mistaken for the rule bending: **nothing had been published yet.** The sibling rule
protects bytes that a counterparty may already hold -- the sealed prereg and the sealed v1
instrument, both untouched. An addendum that has never left my working tree is a draft.

## Hashes, so the change is auditable rather than asserted

    sealed at registration   42984d9c2379b8b3f9bdcde7eb645229fe28b449193bc1dbc55f8156984bdf64
    as committed             a95d3e6f8200ca143a67a00707041bce565087b5d83a2a62c5db7371e13330d9

Both files are committed: the registered bytes as `data/c49/m2_c49_precision.SEALED_v1.py`, the
corrected instrument as `data/c49/m2_c49_precision.py`, and the diff as
`data/c49/m2_c49_precision.v1_to_v2.diff`. A reader who wants the registered instrument has it.

## Which registered predictions this touches: NONE, and here is why that is checkable

The change is inside `upgrade_cell`, which writes prose into output cells. **`gate_cell` — the
function P2a/P2b are scored by — is byte-unchanged**; the whole diff is six lines inside one string
literal in `upgrade_cell`. P2 was scored on the sealed v1 (`m2_c49_gate_census.out`) and re-scored on the corrected
file: **95/95 and 16/95 both times, identical.** P1 does not use this module's gate at all.

No number in any prediction, band, or result moves.
