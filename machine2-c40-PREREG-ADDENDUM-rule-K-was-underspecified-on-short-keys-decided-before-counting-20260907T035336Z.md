# machine2 — c40 PREREG **ADDENDUM**: RULE K was under-specified on two axes. Both decided here, still before any count.

**Filed 2026-09-07T03:53:36Z.** Written after RULE K was pushed (`6e4b19f`) and **before any row is counted under
it**. Publishing the gap rather than quietly resolving it in code is the whole point: a rule that has
to be patched during implementation was not a rule, and the patch is where the freedom hides.

## A1 — Rows with fewer than 12 significant digits

K2 says the join key is *"the first 12 significant digits plus the decimal exponent"*. **Measured:
77 of the 486 census rows carry only 10 or 11 significant digits** (10 s.f.: 38 rows; 11 s.f.: 39),
so K2 as written does not key 15.8 % of its own denominator. Silently dropping them would change K8,
the denominator, which is the one clause both c39 runs already agreed on.

**Decision:** a row with fewer than 12 significant digits is keyed by **all** of its significant
digits, and matches a carrier iff the row's digit string is a **prefix** of the carrier's key at the
**same decimal exponent**. Matching is therefore prefix-at-the-shorter-length, capped at 12.

**Disclosed because it is not neutral:** the two c39 implementations differ here and neither is
obviously right. The high run keys carriers at `digits[:12]` and looks the census key up by **exact
dict equality**, so a 10-digit row can match only a carrier whose key is also exactly those 10
digits. The low run used prefix-consistency in **both** directions, which matches more widely. A1
sits between them, and this addendum exists so that nobody can later read the choice as neutral.

## A2 — Attribution rule for K1

K1 says *"attributed to us by the c37 basename rule"* without pinning an implementation. **Decision:**
adopt the `is_ours()` predicate already committed in `data/code/m2_c39_knob_column.py` verbatim —
reject `machine1|machine3|m3_|m1_|letter|BEAST|SAPIENS` basenames, accept `machine2|m2_|machine2_|c3`
— because it is the version already in the repository and adopting the committed one keeps this
reconciliation from inventing a third convention.

## A3 — A limitation of K1+K3 that no decision here removes

A file that **aggregates** constants from many runs while declaring a single `dps` will mark every
constant it carries as RECOVERED at that precision, whether or not that run produced them. K5
forbids inheritance across files but cannot detect aggregation **within** one. This is a known
over-count in the RECOVERED direction, it is not repaired in this cycle, and any RULE-K figure should
be read as an **upper bound** on recoverability for that reason.

No proof claim. Standing sentence unchanged: we have no route to a proof.
