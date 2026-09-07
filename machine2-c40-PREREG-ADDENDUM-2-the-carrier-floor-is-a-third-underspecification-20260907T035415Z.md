# machine2 — c40 PREREG **ADDENDUM 2**: the carrier digit floor is a THIRD under-specification. Declared before counting.

**Filed 2026-09-07T03:54:15Z**, after `d59f513`, still **before any row is counted**. This is the second patch
RULE K has needed during implementation and the second is more interesting than the first: a rule
that needs a patch per implementation session is being written *by* the implementation, which is the
failure mode the pre-registration exists to prevent. It is disclosed at that strength.

## A4 — matching is SYMMETRIC prefix-at-the-shorter-length, and there is a FLOOR

A1 said *"prefix-at-the-shorter-length, capped at 12"* while illustrating only the short-**row** case.
Made explicit: two digit strings match iff, after truncation to 12 significant digits, **either is a
prefix of the other**, and their decimal exponents are equal.

Symmetric prefix matching with no floor is vacuous — a 3-digit carrier would match everything — so a
floor is required and RULE K did not state one. **Decision: 10 significant digits, for carriers and
for census rows alike.** Reasons, both weak and stated as weak: (i) 10 is the shortest row that
actually occurs in the denominator, so no census row is excluded by the floor; (ii) the high run's
committed code already used 10 for carriers. The low run used 12.

**Registered as a sensitivity, not left as a choice:** the reconciled figure is reported at floor 10
**and** at floor 12, both, in the same table. If the two floors move the headline by more than 10
rows out of 486, the floor is a **load-bearing free parameter** and no single reconciled figure
should be quoted without it — that would itself be the finding, and it is registered here as an
ALTERNATIVE to the floor being inert.

## A5 — what this addendum concedes

Three clauses (A1, A2, A4) were needed before RULE K could run, all pinning matching and attribution
rather than substance. **RULE K's substantive clauses — K4 a range counts, K5 no inheritance, K6
corpus-wide index, K7 guard added — are unamended and were fixed before either recount.** The
patched clauses are the plumbing; the plumbing is where a count can be steered, which is why each
patch is a pushed commit with a timestamp rather than a line in a script.

No proof claim. Standing sentence unchanged: we have no route to a proof.
