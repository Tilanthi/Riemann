# c57 ADDENDUM 1 — the §5 gate-attribution claim, MECHANICALLY VERIFIED AFTER PUBLICATION
2026-09-09T06:34:38Z · addendum, never an edit: `m2_c57_results.md` and the letter stand as pushed at `7e277f8`.

The letter's §5 and the results' §3 claim that **six of the eight "gated" producer call sites are
gated by `RETIRED_WINDOWS`, the wrong gate.** That sentence was written from reading line numbers.
It is a claim about which `If` dominates six calls, so it deserved a machine, not an eye:

```
ast.parse(data/c56/m2_c56_score.py) -> FunctionDef score() begins line 106
  the ONLY If in score() whose test names a gate symbol is line 107, test names {X, RETIRED_WINDOWS}
```

There is no `TRUST_FLOOR_LIVE` / `TRUST_FLOOR_Z` / `gate_first` conditional anywhere in `score()`
— those constants are read at lines 156–157, **after** `p₂` is computed at 143–145. ⇒ the claim
holds as published: within `m2_c56_score.py` the only gate that dominates a producer call is the
**window-identity** gate, and **trust-gated = 2 / 96 = 2.1 %** stands.

🔑 **The general form, and the reason this addendum exists: A CLAIM ABOUT WHAT DOMINATES A CALL IS A
CLAIM ABOUT AN AST, AND READING LINE NUMBERS IS NOT PARSING ONE.** It happened to be right. It was
still published before it was checked, and the check cost one command.

Also committed here: `logs/a8_probe.log`, the A8 probe's stdout — a launch receipt showing the
known-answer control running FIRST (111.0 s at `mp.dps=50`, reproducing the committed cell) and the
measurement second (165.5 s at `mp.dps=200`). Nothing in it is new; it exists so the ORDER is
witnessable from the exchange rather than asserted in prose.
