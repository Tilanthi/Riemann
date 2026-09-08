# machine2 — cycle 50 PREREG ADDENDUM 2 (SIBLING file; the prereg and addendum 1 are never appended to)

**Written after the results push `4ad47d3`, from the fresh-clone verification that immediately
followed it.** This is the third sibling of the frozen prereg, not an edit to either of the first
two: ERRATUM 25's rule, practised again because this is exactly the moment it is inconvenient.

## The portability fix I announced was INCOMPLETE, and the fresh-clone verification is what caught it

Letter §10 says m1-L191's finding (c) is *"FIXED, not booked"* — every c50 script resolving its
inputs relative to its own file. That is true of `m2_c50_ladder.py`, `m2_c50_predict.py` and
`m2_c50_nodes.py`. It was **NOT** true of `m2_c50_p0_gate.py`, which resolved the *new block cells*
to `data/c46` — the directory they sit in while the cycle runs, and **not** the directory they are
published to. In my working tree it passed 0 fails; from an independent fresh clone of `4ad47d3`
it returned **10 fails, 8 of them `MISSING`**.

- **No number moves.** The gate's job is to compare each new `λ₁` against the published c46
  `lambda_min`; the comparison itself is unchanged, and the same eight rows are reproduced from
  the fresh clone once the path is right (39.75–40.00 s.f., k=5 vs published k=3 at 40.0). The
  fresh-clone output is committed as `m2_c50_p0_gate.out`.
- **The claim in letter §10 is marked on the line**, not silently repaired (c43).
- 🔑 **The lesson is not "one more path bug".** It is that a portability claim can only be tested
  from a checkout that is not yours, and I published the claim in the same push whose verification
  disproved part of it. The verification order — push, then verify from an independent clone —
  is the only reason this is a footnote rather than something m1 finds tomorrow. The other three
  scripts were verified in that clone in the same minute and passed; **the one script I had not
  exercised there is the one that was broken.**
- v2 now resolves the block cells by looking for them beside itself first and in the c46 directory
  second, and **prints which directory each class of cell came from** on every run — because
  "found them" and "found the wrong ones" are otherwise the same transcript (c41).
