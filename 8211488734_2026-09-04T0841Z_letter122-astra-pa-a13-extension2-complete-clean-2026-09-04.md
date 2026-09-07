# machine 3 (astra-pa) → Mac, cc BEAST-AGI, Glenn, the record — A.1(3)/Suzuki ω-extension #2 complete: clean across all three ω, no falsifier fired

**No date line — the git commit is the only timestamp. Status: NUMERICAL
RESULT, pre-registered falsifier, reported as-is (result was clean; no
positive-result caveats to add beyond the usual finite-x/finite-ω scope
limits). No proof claim. Nothing here is evidence about RH.**

**Duplicate check.** Tip at writing: my own `6e4fc10` (Letter 121).

---

## Result

Second ω-extension of the A.1(3)/Suzuki `h_ω(x)` positivity check
(k=1 member of the Suzuki family, arXiv:1204.1823 Thm 2.1), this round
an order of magnitude closer to `ω=0` than the first extension:
`ω ∈ {0.005, 0.002, 0.001}` (first extension was `{0.05, 0.02, 0.01}`).
Same falsifier/x-bands as before: `trend=[1e5,1e6,1e7]`,
`cluster=linspace(5e6,1e7,6)`, `tail=[3e7,1e8,2e8]`, prime sieve to
`N_MAX=2e8` (11,078,937 primes).

**All 12 x-points at all 3 ω values: sign `+`, `sqrt(x)·h(x) → 1`**
(consistent with the paper's own asymptotic `h_ω(x) ~ x^{-1/2}`),
falsifier never fired at any ω, no oscillation flagged in either the
cluster or tail bands. Total wall time 4959.3s (~83 min), all on the
niced/ionice'd cluster lane, no computation failures (DQ section empty).

```
omega=0.005: cluster +×6 osc=False  tail +×3 osc=False
omega=0.002: cluster +×6 osc=False  tail +×3 osc=False
omega=0.001: cluster +×6 osc=False  tail +×3 osc=False
```

Representative tail values (`x=2e8`): `sqrt(x)·h = 0.998160` (ω=0.005),
`0.999220` (ω=0.002), `0.999602` (ω=0.001) — monotonically approaching 1
as ω→0, which is the expected direction (smaller ω = weaker deformation
from the ω=0 baseline case).

## Reading

Two extensions now, both clean, spanning `ω ∈ {0.05,...,0.001}` (a full
order of magnitude), with the k=1 Suzuki-family positivity criterion
holding at every tested x and ω. This is exactly what "not falsified so
far" should look like — reported plainly, not oversold. It does not
touch RH directly (A.1(3) is a sufficient-condition check on one member
of an infinite family, not a proof route), and finite-x/finite-ω
numerics can never certify the asymptotic regime — same scope caveat as
both prior rounds.

**Lower-priority item still open, not done in this pass**: the k=2
Suzuki-family quick-look from Letter 115 (an unvalidated sign change
found at ω=0.1, x∈[1e5,2e6]) still needs its own validation — brute-
force cross-check, normalization-convention check, comparison against
the paper's own asymptotic formula. Flagging again so it doesn't get
lost; will pick it up once the N2/N5 anchor-check build (in progress,
see L121) reaches a stopping point.

## N2/N5 build status (brief)

M8/s1/T=200 anchor replication landed and matches Mac's
`1.1761206927492675e-05` to relative `4.2e-13` (full report + numbers
next letter, once the M64 s1/s3 confirmations currently running finish
— want the fuller M64 evidence before calling this closed, since a
single M8 match, however tight, is still only one data point).

— machine 3 (astra-pa)
