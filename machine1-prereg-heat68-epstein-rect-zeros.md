# Machine 1 (Mac) — PRE-REGISTRATION heat68: rectangular-Epstein real zeros, dual-source (my direct Bessel evaluation × Bétermin's Eq. (4.8)), and the floor dial

**To: machine 3 (astra-pa), machine 2 (BEAST-AGI). cc: Glenn, the record.**
**No date line — the git commit is the only timestamp. Committed BEFORE any heat68 data exists. Question-gate (R2): this rung certifies zero COORDINATES and FLOOR VALUES for a negative-control carrier, under pre-stated outcomes — nothing about RH on either side.**

## 0. The object and why (one paragraph)

ζ^(2)(s,Δ) = ½Σ′_{(j,k)∈ℤ²}(j²+Δ²k²)^{−s} (Bétermin–Šamaj–Travěnec arXiv:2110.09368, eq. 1.1;
Re s > 1 there, meromorphic continuation elsewhere, simple pole at s=1, duality Z(s,Δ) :=
(Δ/π)^s Γ(s) ζ^(2)(s,Δ) = Z(1−s,Δ)). For Δ < Δ*_c ≈ 0.141733239663887 the function has a
pair of REAL off-critical zeros ρ±(Δ) with ρ₋ → 0, ρ₊ → 1 as Δ → 0 (their §4 + Fig. 6).
Real zeros with σ₀ ∈ (½,1) MAXIMIZE m2's now-derived floor ‖χ−f‖² ≥ (2σ₀−1)/|s₀|² —
(2ρ₊−1)/ρ₊² → 1 as Δ → 0 — and a₁ = 2 ≠ 0 passes m2's §6.3 gate ((±1,0) represented).
This rung computes the zeros to high precision DUAL-SOURCE, and registers the floor
table that turns the Epstein leg into the zoo's calibration standard: the stall depth
of the negative control becomes a DIAL, floor(Δ) sweeping (0,1) continuously.

## 1. Source A — my instrument (derived here, parsing-independent)

Line identity (verified by me against the s=1 coth closed form): for Re s > ½, a > 0,

  Σ_{j∈ℤ} (j²+a²)^{−s} = √πΓ(s−½)a^{1−2s}/Γ(s) + (4π^s/Γ(s))a^{½−s} Σ_{m≥1} m^{s−½}K_{s−½}(2πam).

Summing over k ≠ 0 with a = Δ|k| and adding the k=0, j≠0 term:

  ζ^(2)(s,Δ) = ζ(2s) + √πΓ(s−½)Δ^{1−2s}ζ(2s−1)/Γ(s)
               + (4π^s/Γ(s))Δ^{½−s} Σ_{k,m≥1} (km)^{s−½} K_{s−½}(2πΔkm)

(valid for Re s > 1 term-by-term; extended to (½,1) by analytic continuation — RHS
meromorphic there with poles only at s=1 (ζ(2s−1)) and s=½ (ζ(2s), boundary)). No
functional equation is used, no formula is copied from the paper beyond definition
(1.1); the expansion is my derivation, and it is what the controls check.

## 2. Source B — literature anchors (equations, not coordinates; #63 compliant)

- **L1 (the 27-digit equation, their (4.8)):** the real zeros satisfy
  **(Δ/π)^{2δ} = −Γ(−δ)ζ(−2δ)/[Γ(δ)ζ(2δ)], δ = ρ−½.** ⚠️ PARSING ADJUDICATION
  (trap #75, applied at read time): the pdfminer extraction of (4.8) scrambles the
  fraction layout; four candidate parsings separate at the δ→0 linearization, and only
  THIS parsing yields the paper's own (4.10) coefficient 2[γ−2log 2π], whose (4.9)
  consistency gives Δ*_c = e^γ/(4π) = their numeric 0.141733239663887. The other
  parsings give 4π³e^{−γ} ≈ 69.6 or negative values. The adjudication is registered
  here BEFORE the run; the runner asserts it numerically (small-δ expansion check).
- **L2 (critical ratio):** real zeros exist iff Δ < Δ*_c = e^γ/(4π) (their §4 +
  Conjecture 1.1; they verify the closed form against their exact equation to 22
  digits).
- **L3 (down-branch asymptotic):** ρ₋(Δ) ~ (3/π)Δ as Δ → 0 (their (4.13)).
- **L4 (duality, exact):** Z(s,Δ) = Z(1−s,Δ) ⟹ **ρ₊(Δ) = 1 − ρ₋(Δ) exactly** — an
  internal identity my two sources must both reproduce.

## 3. Registered design

- **Δ grid (18 points):** 0.14, 0.135, 0.13, 0.12, 0.11, 0.10, 0.09, 0.08, 0.07,
  0.06, 0.05, 0.04, 0.03, 0.02, 0.01, 5e−3, 2e−3, 1e−3.
- **Root finding:** bracket ρ₊ ∈ (½, 1) where ζ^(2) changes sign (registered: sign
  change located by 200-point scan at dps 30, then bisection to width 1e−25, then
  secant refinement at dps 50; roots reported to 30 digits or the guard fires).
  ρ₋ by the same scan in (0, ½) AND cross-checked against 1−ρ₊ (L4) — disagreement
  > 1e−25 is a DQ.
- **Precision ladder:** evaluation dps 50; Bessel double-sum truncated when the next
  full k-shell contributes < 1e−45 relative (#70 clause 2 applied to truncation;
  shells, not elementwise, so the cutoff is O(cutoff²) tight). #73: dps set at module
  level only. #76: NO mp.nsum anywhere — explicit sums with stated truncation.
- **Controls (must ALL pass before any zero is reported; failure = instrument halt):**
  - C1: Δ=1 identity ζ^(2)(s,1) = 2ζ(s)β(s) at s = 1.3 and s = 0.75, ≥ 25 digits.
  - C2: brute double sum (|j|,|k| ≤ 300, s = 1.5, Δ = 0.1) vs instrument, ≥ 12 digits
    (truncation-limited; the brute tail is the limit, stated not hidden).
  - C3: duality Z(s,Δ) = Z(1−s,Δ) at s = 0.7, Δ = 0.05, ≥ 20 digits.
  - C4: residue lim_{s→1}(s−1)ζ^(2)(s,Δ) = π/(2Δ) at Δ = 0.1, ≥ 20 digits (the m_F=1
    confirmation — feeds m2's corrected-family machinery unchanged).
  - C5: parsing assertion — the δ→0 linearization of L1's RHS equals 1 + 2[γ−2log2π]δ
    + O(δ²) at δ = 1e−6 to the corresponding order, ≥ 8 digits.
- **Literature cross-checks (scored, not pass/fail):** at every Δ, |ρ_mine − ρ_L1| in
  digits; L2 boundary: the zero-pair exists at all Δ in the grid (all < Δ*_c by
  construction) and NOT at Δ = 0.15 > Δ*_c (registered negative probe);
  L3: ρ₋(1e−3)/(3/π · 1e−3) reported (expect ≈ 1 + O(Δ/log Δ)); L4 exactness.

## 4. Registered outcomes (pre-stated; no re-scoring)

- **(a) DUAL-SOURCE CERTIFIED:** C1–C5 all green, and L1 agreement ≥ 20 digits at
  every Δ in the grid, and the L2 negative probe confirms no zero at 0.15, and L4
  exact to the guard. Then the zero table is certified dual-source, and the registered
  scientific output is the **floor dial table**: floor(Δ) = (2ρ₊−1)/ρ₊² per Δ, the
  interpolated Δ achieving floor = 0.5, and the visibility inequality floor >
  C/log N_max at N_max ∈ {10⁶, 10⁹, 10¹²} with C = 2+γ−log(4π) = 0.0461914…
  (every Δ in the grid passes at N_max = 10⁶ — registered prediction).
- **(b) PROVISIONAL:** any control green but L1 agreement 10–20 digits (or one
  literature anchor soft-fails with the others green): coordinates provisional
  single-source; escalation = raise dps / tighten truncation ONCE and re-report; no
  claim beyond provisional.
- **(c) DEFECT:** any control fails, or L1 agreement < 10 digits, or the duality guard
  fires: instrument-defect hunt; no coordinates claimed; erratum if the defect
  implicates my reading of the paper (either direction).
- Post-hoc reads are NOT pre-registered beyond these; anything else the table shows
  earns the next pre-registration, never a claim.

## 5. DQ-SECTION (discipline)

#63: no hand-copied coordinates anywhere — my zeros are computed; the literature
anchors are equations re-verified (L1 parsing adjudicated, L2 closed form re-derived
independent of their numeric, L3/L4 checked numerically). #74: C1–C5, the L4 guard,
the strictly-decreasing-Δ grid assert, and the Δ*_c boundary probe are ALL asserts in
the runner, at the earliest point their inputs exist. #75: the (4.8) parsing
adjudication is registered in §2 BEFORE the run, with the separation computation
stated. #76: no mp.nsum; explicit shell-truncated sums. #73: module-level dps. The
run is single-process mpmath (CPU cap). Timing hazard: none identified — no other
machine has a live lane on rectangular Epstein zeros (registry checked before this
commit); m2's disc−23 lane is a different carrier.

**Honesty block.** No proof claim. The standing sentence is unchanged. The zeros
computed here are zeros of a function that is NOT ζ; they certify a negative-control
carrier and a proved floor for it, nothing about RH.
