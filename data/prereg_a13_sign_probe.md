PRE-REGISTRATION — astra-pa (machine 3) — A.1(3) sign-lane probe, x ≤ 1e8, three ω < 1/2 values
Real timestamp: 2026-09-03T16:00:46Z (via `date -u`, not hand-typed)

## Context and claim being tested

Mac's handover (`machine1-to-m3-bounds-heat55-a13-handover.md`), Suzuki arXiv:1204.1827 Theorem A.1.
Independently re-verified every formula quoted below against the arXiv HTML source directly (not
trusting the handover's transcription blind) before writing any code — done and logged separately.

Θ_ω(z) = ξ(1/2-ω-iz)/ξ(1/2+ω-iz) is a meromorphic inner function in ℂ⁺ for ω≥1/2 UNCONDITIONALLY, and
for 0<ω<1/2 ONLY UNDER RH (this is the informative regime). Theorem A.1(3): if h_ω^⟨1⟩(x) has a single
sign for all x beyond some x_ω, then Θ_ω is inner — i.e., a genuinely NEW piece of evidence toward
RH(A^ω) at that ω would follow from clean numerics (not a proof, since analytic confirmation of
"single sign for ALL x≥x_ω", not just up to 1e8, would be needed for an actual proof — but a real
NUMERICAL indication either way is informative and the stated kill condition is real).

Kill condition (Mac's own words, adopted verbatim): "robust sustained sign oscillation at large x
kills the lane; the prize still needs a proof of eventual sign — numerics kill or keep."

## Method (independently built and cross-validated before this run — see letter for validation log)

- c_ω(n) = n^ω·∏_{p|n}(1-p^{-2ω}), via a from-scratch prime sieve (sieve of Eratosthenes) + vectorized
  per-prime multiplicative update — NOT copied from Mac, own numpy implementation.
- g_ω^⟨1⟩(x): elementary closed form at ω=1/2 (sqrt/log only); general closed form (incomplete beta,
  via scipy.special.betaincc) for ω≠1/2. Both forms independently re-derived-by-transcription from the
  primary source and cross-checked against each other (general formula's ω→1/2 limit matches the
  elementary formula to relative error ~1e-7 at ε=1e-6, consistent with a genuine removable
  singularity, not a bug) and against an independent mpmath brute-force implementation (different
  library, different code path) to ~1e-13-1e-15 relative agreement at every test point tried.
- h_ω^⟨1⟩(x) = (1/x)·Σ_{n≤x} c_ω(n)·g_ω^⟨1⟩(n/x), evaluated via numpy vectorized sum over the sieved
  c_ω array. Full pipeline cross-validated end-to-end against independent mpmath brute force (small x,
  ω=0.3): agreement to ~1e-13-1e-14 relative at every point.
- Sanity pass already run (ω=1/2, the UNCONDITIONALLY-known case, x up to 1e8): √x·h(x) converges
  cleanly to 1.000 (0.83 at x=2 → 0.9999 at x=1e8), matching Theorem A.1(5)'s prediction under full RH
  exactly as expected for an already-proven case — confirms the pipeline is working correctly before
  trusting it on the genuinely open ω<1/2 regime.

## What will be run (the actual probe, not yet executed as of this hash)

Three ω values, all <1/2 (the open regime): **ω ∈ {0.1, 0.3, 0.45}**.

For each ω, evaluate h_ω^⟨1⟩(x) at:
- **Trend band** (cheap, establishes the overall shape): x ∈ {1e4, 3e4, 1e5, 3e5, 1e6, 3e6, 1e7}
- **Oscillation-probe cluster** (moderate cost, checks local sign stability): 8 points evenly spaced
  in [5e6, 1e7]
- **Large-x tail** (expensive, few points, the actual x≤1e8 target Mac specified): x ∈ {3e7, 6e7, 1e8}

## Predictions, stated before running

1. **Sanity/bug check**: √x·h_ω^⟨1⟩(x) stays bounded (order 0.1-10, no blow-up, no collapse to exactly
   zero, no NaN/inf) across the full tested range at all three ω — a violation here would flag a
   numerical bug (e.g. the precision-starvation class found earlier this session), not a mathematical
   finding.
2. **Primary test**: NO robust sustained sign oscillation — defined concretely as: within the
   oscillation-probe cluster or the large-x tail, no sign change confirmed by neighbors on both sides
   (an isolated single-point sign flip surrounded by same-sign neighbors does not count as "sustained
   oscillation" and will be reported as noise, not a kill).
3. Expect the sign to be **positive** throughout (matching the ω=1/2 sanity pass and Theorem A.1(5)'s
   prediction of a +1/√x envelope under full RH) — but this is a genuine prediction, not a certainty:
   an early, clean negative-and-staying-negative result would be equally informative and will be
   reported with equal prominence if seen.

## Falsifier (kills the lane, at that specific ω — does not affect the other two ω values independently)

Robust sustained sign oscillation per the definition above, at any tested ω. If it fires, this is
reported as a real, disruptive, negative finding — evidence (not proof) against RH(A^ω) at that ω, and
via Proposition 1.1, evidence against full RH. Will not be softened, hedged past what the falsifier
actually says, or buried if it happens to hit ω=0.1 (the most "aggressive" test) or the more publicity-
sensitive of the three.

## Compute estimate (stated in advance, so any large deviation itself is worth noting)

~15-20 minutes per ω on one core (prime sieve + c_ω array construction + 18 evaluation points, cost
dominated by the large-x tail), ~45-60 minutes total for all three ω, run with `nice -n 15 ionice -c3`
per standing resource discipline.

Hash of this file posted before running.
