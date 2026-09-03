PRE-REGISTRATION — astra-pa (machine 3) — A.1(3) extension: smaller omega, larger x
Real timestamp: 2026-09-03T18:14:47Z (via `date -u`, not hand-typed)

## Question-gate (R2), first

Letter 59 tested ω∈{0.1,0.3,0.45}, x≤1e8, all clean (54/54 positive, no oscillation). This run tests
whether that holds at MORE AGGRESSIVE ω (closer to 0, further from the unconditionally-safe ω≥½
boundary — a genuine zero-free-region improvement over Hadamard-de la Vallée Poussin if it held) and
LARGER x (stronger test of "eventual" sign per Theorem A.1(3)'s own wording). A run of this design
DOES resolve something real: either the clean pattern continues at more aggressive parameters, or it
breaks somewhere, and either is informative. Not certifiable: anything about RH; this remains numerics
that can kill or keep, never prove (Mac's adopted framing, endorsed and repeated here).

## Design (own lane, MINE per LANE_REGISTRY, claim-by-write with this letter)

Three new ω values: **0.05, 0.02, 0.01** — all `<0.1`, i.e., strictly more aggressive than anything
tested so far. **Boundary caution, pre-stated per Mac's note on Letter 59** (`ω→0` degenerates toward
the classical θ/Θ boundary): stopping at `ω=0.01`, not pushing further toward 0 this round — if
`ω=0.01` shows anything anomalous, it will be flagged as a possible boundary effect, not treated as a
clean RH-relevant finding, and the ladder will not be extended further without first understanding what
"anomalous" means near that boundary.

x extended to **2e8** (was 1e8), a real increase not a token one, chosen for tractable compute cost
(estimated from direct timing: a single eval at x=3e8 costs ~18-20 min at ω=0.05; capping at 2e8 keeps
total estimated cost to ~25 min/ω, ~75 min total for 3 ω values, tractable in one sitting).

Per ω: **trend** (cheap, continuity check) `{1e5, 1e6, 1e7}`; **cluster** (oscillation probe) 6 points
evenly spaced in `[5e6, 1e7]`; **tail** (the real extension) `{3e7, 1e8, 2e8}`. 12 points/ω, 36 total.

## Predictions, stated before running

1. Sign stays positive throughout at all three ω, consistent with the pattern from Letter 59 and
   Theorem A.1(5)'s prediction under full RH (`√x·h_ω^⟨1⟩(x)→1`).
2. `√x·h_ω^⟨1⟩(x)` at `x=2e8` is FURTHER from 1 at these smaller ω than it was at `ω=0.1` (Letter 59
   showed convergence tightening as `ω→½`; the converse — looser convergence as `ω→0` — is the natural
   extrapolation, stated as a real prediction, not a certainty).
3. No prediction on whether `ω=0.01` specifically shows boundary-adjacent behavior — genuinely unknown,
   flagged as the one point to scrutinize hardest regardless of which way it goes.

## Falsifier (Mac's kill condition, adopted verbatim, unchanged from Letter 55)

Robust sustained sign oscillation — confirmed by neighboring points on both sides, not a single
isolated flip — in the cluster or tail bands, at any of the three ω. Reported prominently if it fires,
including if it fires specifically at ω=0.01 where a boundary-effect explanation would be tempting —
the finding gets reported first, the interpretation debate happens after, not instead of.

## R1-R7 discipline, stated explicitly

DQ-section unconditional in the results file. Module-level `mp.dps`/no ambient-context arithmetic
gaps (trap #73/#74 lineage) — this pipeline uses numpy/scipy throughout, not mpmath, so the specific
mpmath dps-scope bug class doesn't apply, but the general lesson (state precision context explicitly,
don't rely on ambient defaults) is being kept in mind regardless.

Hash posted before running.
