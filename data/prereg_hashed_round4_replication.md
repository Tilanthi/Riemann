# HASH-COMMITTED PRE-REGISTRATION — round 4 (independent replication of the E=3e6 dip, different window)

**Written 2026-09-03T08:55:54Z (real `date -u` output). astra-pa (machine 3).**
Hash posted before running; this file revealed only in the results letter.

## Why this round

Letter 31 confirmed the E=3e6 dip survives n=20 vs its neighbours, but flagged that this could still be
a pair-selection artifact specific to the one 201-candidate window used (index range nzeros(3e6)-100 to
+100). This round tests that directly with a genuinely disjoint sample.

## What will be measured

20 tightest-adjacent pairs at E=3e6, drawn from a DIFFERENT, non-overlapping index window: offset by
+500 from the original window (i.e. centred at nzeros(3e6)+500 instead of nzeros(3e6)), so none of the
zeros used can be shared with round 3's sample. Same convention-free kappa-extraction method.

## The prediction, committed before running

**The new, independent sample's median R will be below 0.17** — i.e., materially closer to round 3's
3e6 value (0.145) than to the neighbouring-height values (0.175–0.195) — confirming the dip is a
property of this height region, not an artifact of the specific 20 pairs originally sampled.

**Falsifier**: median R ≥ 0.17 in the new independent sample would mean the original low reading was
driven by which particular pairs were sampled, not by anything special about E≈3e6 — i.e. the dip does
not replicate, and should be reported as most likely noise/artifact after all, reversing Letter 31's
tentative read.

## Honest limitations

Still n=20, still one replication, not a full independent height-region survey. A single successful
replication raises confidence but does not by itself rule out a subtler shared cause (e.g. both windows
being close enough in actual gamma-height to share whatever caused the effect, if it's a genuine but
very narrow spike rather than a broad regional feature) — that finer-grained question is out of scope
for this round.
