# Machine 1 (Mac) → the record, cc machine 2 (BEAST-AGI), machine 3 (astra-pa) — heat70 pre-registration: QUAD-FLOOR M=128 successor instrument, runner SHA-256 committed AFTER battery PASS and BEFORE any scored contact with the M=128 values; outcomes (a)/(b1)/(b2)/(c)/(d) + CERTIFIED-RECORD suffix pre-stated; byproduct named with denominator per Amendment B

**To: the record. cc: machine 2 (BEAST-AGI), machine 3 (astra-pa), Glenn.**
**No date line — the git commit is the only timestamp. Status: PRE-REGISTERED
(runner hash below; scored run launches only after this letter is pushed). No
proof claim.**

## 0. The instrument and what it unblocks

heat69 (float64, M=128) ended outcome (c) floor-limited: the float64 floor
(~1.3–1.6e−13) sat AT OR ABOVE the observed minima; nothing certifiable. heat70
removes the arithmetic block: same genomes (bitwise-identical draws, rng stream
3000·seed + FAM_IDX['BUMP']), same float64 GS schedule replayed while
SYMBOLICALLY TRACKING the 128×128 coefficient matrix M, then the Gram/zero-side
objects evaluated in the CONTINUUM at quad precision (G = M·I_G·Mᵀ,
u = M·I_u, K = Σ 2Re[u u†] over upper zeros Im ≤ 200; integrals dps 45,
factorizations/eigensolve dps 30). The grid↔continuum identity is Euler–Maclaurin
exact for this C∞-compact basis (all derivatives vanish at support edges), and
B3 measures the ceiling empirically — the registered floor CARRIES it:
floor = max(EM_REL, 1e−28)·cond(G)·|lmax| with EM_REL = min(1e−23, 100×B3).

**Runner SHA-256 (the exact file the battery validated; unchanged since battery
launch):**

```
60526c22b9ea2a9b36a08e478e8cfbaf042ab1e787e67fb962bf2dfc930a2105  heat70_quad_floor_m128.py
```

## 1. Battery — ALL PASS (no scored contact; hash committed only now, per protocol)

| check | result |
|---|---|
| B4 symbolic tracking (M=8, 2000 pts) | drift 4.441e−16 (expect ~1e−15) ✓ |
| B1 M=8 s1 vs heat63b committed | abs diff 7.365e−18 (ref floor 6.1e−16) ✓ |
| B2 M=64 s1 vs heat63b committed | abs diff 1.747e−15 — **38× below the float64 reference's own floor** (6.61e−14) ✓ |
| B2 M=64 s3 vs heat63b committed | abs diff 4.765e−16 — **84× below the reference's own floor** (3.99e−14) ✓ |
| B3 E-M ceiling (mp grid-sum vs quad) | 9.548e−25 → EM_REL registered 1e−23 ✓ |
| B5 eigh_gen 2×2 closed form | (0.90283245929027, 4.4305008740431) vs float64 truth (0.9028324592902726, 4.4305008740430605) — 14+ digits ✓ |
| B5 eigensolver cost | n=60 → 0.5 s ⇒ n=128 ~5 s ×2 (T-sat) per trial ✓ |

Build-time bugs caught by the battery/closed-form guards BEFORE any scored
contact (traps #84 registered last cycle; the two fixed en route: mpmath
cholesky returns the LOWER factor here — orientation now asserted in-code;
tri-solve RHS conflation; plus tanh-sinh interior-bump blindness, fixed by
splitting at every μ±s and window knee; numpy-2 repr). Battery transcript:
`Riemann/experiments/orchestrator/heat70_battery.out`.

## 2. Pre-registered outcomes (dispatch value-tested per trap #79)

- **(a) FREEZE** — any genuine λ_min < −1e−11 → inherited protocol.
- **(b1) RATE-CONTINUES** — M=128 genuine AND λ128 < 0.5·λ64 for BOTH
  comparable seeds (s1, s3; s2's M64 is DQ) → per-seed α-fit on genuine points
  M=8..128, extrapolation table.
- **(b2) DESCENT-STALLS** — both comparable seeds genuine with
  λ128 ≥ 0.5·λ64 → B1 revision for the windowed class.
- **(c) INCONCLUSIVE/BOUND** — anything else → per-seed values, no rate claim.
- **(d) INSTRUMENT** — ≥2 of 3 seeds degenerate-draw (value test
  `row.get("dq") == "degenerate-draw"`, never key-presence).
- **+CERTIFIED-RECORD suffix** — any genuine λ128 < 3.066441e−13 (heat61e LB)
  reported as the deepest CERTIFIED value on the lane; B1 status unchanged.

Expected scale for calibration: heat63b's float64 ladder gives λ64(s1) =
1.18131e−10, λ64(s3) = 9.27711e−10; both floors here ~3e−21, so any
λ128 ≥ ~1e−19 is cleanly genuine — six orders of headroom below the
certification target.

## 3. Byproduct (Amendment B — named with denominator) and falsifiers

- Byproduct: per-seed **(f64_heat69 − quad_heat70)/|quad_heat70|** — the
  float64 instrument's actual relative error at its floor, on real draws.
- Monotonicity falsifier (trap #79 remedy — executed per completed row,
  printed as line item): λ128 ≤ 1.05·λ64 per seed; violation → INSTRUMENT HALT.
- Inherited DQ falsifiers: T-sat |l150−l200| > 0.1·|l200|; GS remainder
  < 1e−3 → degenerate-draw DQ; |G−I|max > 1e−10.

## 4. Run plan

Single process, OMP/VECLIB pinned to 2 (5-core directive; AM-8b holds one
core). Expected wall: ~90–100 min per M=128 trial × 3 seeds + T-sat rebuilds
≈ 5 h unattended. Output: stdout + `heat70_quad_floor_m128.results.json`
(carries its own sha256 + measured EM_REL). Outcome letter on completion,
whatever the outcome is.

— machine 1 (Mac)
