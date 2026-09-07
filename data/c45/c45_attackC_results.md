# machine2 - c45 ATTACK C: results, scored against `c45_attackC_prereg.md`

**Order of operations, machine-checkable from `git log` and not asserted here:** the prereg was
committed and pushed as `2a5c696` and verified at origin by md5 **before** the first run was launched,
and the literature search (P6) was run **after** that push. Everything below is scored against a
target that existed first.

## 1. Scorecard

| item | registered | measured | verdict |
|---|---|---|---|
| **P1** KAT, x=13 N=100 dps150 g9 | reproduce the published value at its printed 30 s.f. | `3.72089974166712393579143476609e-59` | **PASS, 1 of 1**, character for character |
| **P2** x=14 (prime-constant window) | log10 = **-63.8 +/- 0.4**; chord -63.9416, quad -63.7565 | **-63.784600435709796469** | **IN BAND**, 0.015 from the registered centre, 0.028 from the quadratic |
| **P3** x=16 (prime-power insertion) | log10 = **-74.4 +/- 0.4**; falsifier: deviation > 1.0 | **-74.311338960702944350** | **IN BAND. NULL.** deviation 0.029 from the quadratic |
| **P4** x=18 (second window) | log10 = **-84.8 +/- 0.4**; chord -84.7728 | **-84.846808298336073757** | **IN BAND**, 0.047 from the registered centre |
| **P5** x=25, BLIND | pred **-113.164**; **direction: pred - actual > 0**, magnitude <= 3.0 | at N=100 (the registered comparand) **-112.487668936617622800**, `pred - actual = -0.676`; at N=140 **-121.468157991880829670**, `pred - actual = +8.30` | 🔴 **FAILED, under both readings and differently under each.** Against the registered N=100 quantity the SIGN is wrong; against the better-converged N=140 value the sign is right and the registered magnitude bound of 3.0 is violated 2.8-fold |
| **dps control** at x=16 | inert | dps 220 and dps 300 agree to **all 30 printed s.f.** | **PASS**, coefficient 0 at 30 s.f. |
| **P6** literature | a name table including what it could NOT match | delivered, section 3 | **ANSWERED: no unconditional theorem covers x = 13** |

**KAT count: 1 of 1. Registered numeric predictions: 3 of 4 in band, 1 falsified by sign.**

## 2. P3 is a null with its own internal control, which is the only reason it is worth reporting

The deviation from the local quadratic-in-L interpolation is **0.029 at x = 16, where the prime power
`16 = 2^4` with weight `Lambda(16) = log 2` enters**, and **0.028 at x = 14, where nothing enters**.
The two are the same size. Inserting a prime power is therefore not detectable at N = 100 against the
interpolation's own noise floor, and section S2 of the prereg already excluded a jump by algebra
(`g(log x) = g(L) = 0`, so the entering term has weight exactly zero). What remained testable was a
kink, and there is none at this resolution.

⇒ **The collapse of lambda_min with x is carried by the support length L, not by the arithmetic side.**
x = 13, 14 and 15 have identical prime-power sets `{2,3,4,5,7,8,9,11,13}` and lambda_min falls by
**10.6 orders of magnitude** across them.

## 3. P6: the literature, with the name table and with what it could not match

Our object is studied, under a different parametrisation. **Mapping, stated so the comparison is
checkable:** their test function is supported in `[-L,L]` and its autocorrelation in `[-2L,2L]`, with
prime powers `log n < 2L`; ours is supported in `[-L_our/2, L_our/2]` with `L_our = log x`, its
autocorrelation in `[-log x, log x]`, prime powers `n <= x`. Hence

> **L_theirs = (log x) / 2**, and their resolution height `T* = 2 pi e^{2L}` is **`2 pi x`** in ours.

| result | statement | our x | covers x = 13? |
|---|---|---|---|
| **Yoshida (1992)**, *On Hermitian forms attached to zeta functions* | positivity of the Weil form unconditionally for autocorrelation support `2L <= log 2` | **x <= 2** | no |
| **Connes-Consani**, *Weil positivity and trace formula, the archimedean place*, Selecta Math. (2021), arXiv 2006.13771 | re-proves the same range by trace-formula / von Neumann algebra methods; exhibits the extreme smallness of the lower spectral edge | **x <= 2** | no |
| **Bombieri**, *Remarks on Weil's quadratic functional in the theory of prime numbers I* | the functional attains its minimum in the unit ball of L2 with support in `[-t,t]`; re-proves Yoshida's small-support positivity | small t only | no |
| **Zhu**, arXiv **2608.24827v2** (2 Sep 2026), *Weil positivity in compact windows* | **certified** `Q(f) >= 8.9e-18 ||f||^2` for support 1.6, i.e. `2L = 1.6`; two-sided `8.9e-18 <= lambda*(0.8) <= 2.27e-17`; measured window floor `1.656e-17` | **x <= e^1.6 = 4.9530** | **no** |
| same, exploratory (explicitly **not** a certificate) | support 2.38 | x <= e^2.38 = 10.80 | no, and not certified |
| **Connes-Consani-Moscovici**, **Connes-van Suijlekom** (prolate operator programme) | needs the window ground state to be simple and even; Zhu certifies that at support 1.6 | - | not a positivity theorem at x = 13 |

**What the search could NOT match, stated because a name table without its misses is an advertisement:**
no unconditional positivity theorem at any support beyond 1.6 that is refereed; Zhu explicitly notes
that "claims beyond log 2 exist in unrefereed preprints" and declines to rely on them, and we do the
same. We did not find an unconditional result covering `L_theirs = 1.28245`, which is x = 13.

### 3.1 Consequences, applied to the c44 section D table rather than argued around

- **Row "C finds an unconditional theorem covering x = 13": NOT MET.** The certified record stops at
  x = 4.953, a factor of 2.6 in x and 0.48 in `L_theirs` short of 13. **The c43 section 3 relevance
  claim is NOT withdrawn on that ground and no erratum is filed against it.**
- **Row "C measures lambda_min(x) -> 0 without a theorem": MET. WEAKEN, as pre-registered.**
  `lambda_min > 0` is an **x = 13 statement** and must always be written with its x from here on.
- **Row "P5's directional prediction fails": MET.** No rate in x may be quoted from the quadratic-in-L
  family. We do not quote one.
- **Not anticipated by the prereg, and it cuts against us:** Zhu's **Proposition 2.3** proves that
  **under RH, `lambda*(L) > 0` for every L**. So `lambda_infinity > 0` at x = 13 is an *implication of
  RH*, and measuring it confirms an implication rather than discovering anything. The same paper states
  that an **unconditional** proof of `lambda*(L) > 0` at a given L "is a finite fragment of RH". That
  raises the value of the unconditional question and lowers the value of the numerical one, and both
  halves of that sentence are against our own week's headline.

## 4. The unregistered result, labelled as unregistered: an EXTERNAL CERTIFIED ANCHOR for the c42 convention

This was not in the prereg. It became possible only after P6 identified the paper, and it is reported
as a discovery made after the seal, not as a prediction.

The c42 section 1 convention string is the live `[UNMEASURED]` of this whole programme: if it is
misread, every instrument in the exchange is wrong identically and agrees to 45 s.f. It has never had
an **external** anchor. It has one now.

We ran our own pipeline at the **non-integer** cutoff `x = e^{1.6} = 4.953032424395115`, which is
exactly Zhu's window `L_theirs = 0.8`, at the published N and gl_degree:

| run | lambda_min | log10 |
|---|---|---|
| ours, N = 100, dps 150, g9, iters 16 | `1.73573784262049859362564244089e-17` | -16.760515867927276798 |
| ours, N = 140, dps 150, g9, iters 16 | `1.68553341319012487588775302832e-17` | -16.773262633816244541 |
| Zhu, certified two-sided | `8.9e-18 <= lambda*(0.8) <= 2.27e-17` | |
| Zhu, measured converged window floor | `1.656e-17` | -16.7809 |

- **Both of our values lie inside Zhu's certified enclosure.**
- Ours is a **variational upper bound** (minimising over an N-dimensional subspace can only overshoot),
  so it **must** sit above the true floor, and it does, at **+4.8 % at N = 100** and **+1.8 % at
  N = 140**, moving the right way when the only knob varied is N.
- The two implementations share nothing: different basis (our cosine Fourier modes on `[-L/2,L/2]`
  versus their Legendre and sine bases), different quadrature, different archimedean rewriting,
  different authors, no code in common.

🔑 **Two independent implementations agreeing to 1.8 % on a quantity of size 1.7e-17, with the residual
in the direction one of them is forced to err, is the first external check this convention has ever
had.** It does not close the `[UNMEASURED]`, because agreement of two readings is not a proof of the
convention; it does mean that if the convention is misread, it is misread the same way by a party
outside this exchange.

## 5. The decay law: our data corroborates a published empirical law with zero fitted parameters

Zhu's law is `-ln lambda*(L) ~= 2 pi^2 N(T*) / ln N(T*)` with `T* = 2 pi e^{2L}`, which in our
variables is `T* = 2 pi x`, so `N(T*) = x ln x - x + 7/8 + ...`. The implied constant
`-ln(lambda) * ln N(T*) / N(T*)` read off **our own ten published points**, none of which was produced
with any knowledge of this law:

| x | 3 | 5 | 7 | 9 | 11 | 13 | 15 | 17 | 19 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|
| implied constant | 2.25 | 13.64 | 16.78 | 18.20 | 18.93 | 19.37 | 19.67 | **19.82** | **19.84** | 19.11 |

It rises monotonically to within **0.5 %** of `2 pi^2 = 19.7392` at x = 17 and 19. The fall-back at
x = 23 is in the direction the N = 100 truncation must push, and section 6 measures that truncation
directly.

**Recomputed at the best-converged N available for each x, the constant is not 2 pi^2, it is Zhu's
plateau**, and that is the sharper statement:

| x | at N = 100 | at the best N we have | best N |
|---|---|---|---|
| 13 | 19.369 | 19.391 | 140 |
| 17 | 19.820 | 19.867 | 140 |
| 19 | 19.844 | **19.997** | 180 |
| 25 | 18.532 | **20.179** | 180 |

Zhu's Table 3 caption states the same column "plateaus at **20.1** ~= 2 pi^2 = 19.74". Our
independently produced value at the largest window we can reach is **20.179**. The two implementations
agree on the plateau's *value*, including its excess over 2 pi^2, to within 0.4 %.

**Stated as a limitation, not buried:** this is a corroboration of a *law fitted by someone else*, on
data of ours that was produced first; it is not a derivation, and Zhu says plainly that "the constant is
fitted, not derived".

**One open comparison we could not close, named rather than dropped.** At x = 25 the law predicts
`-ln lambda* = 275.89`, i.e. log10 = -119.82. Our N = 140 upper bound is log10 = **-121.4682** and our N = 180 upper bound is
**-122.4839**, i.e. `-ln lambda* >= 281.99`, which is **2.2 % more decay than the law gives**, and
since ours is an upper bound the true value can only be further below. Zhu quotes residuals below 0.7 % for the law at
L = 1.4 to 2.0, fitted against their own certified upper bounds. Our x = 25 is their L = 1.60944.
Whether 1.4 % is a real deviation or simply says our N = 140 trial space beats their trial function at
that window cannot be decided without their Table 3 entry at L = 1.6, which did not render in the HTML
extraction we retrieved. **Flagged as open, not resolved, and not counted as a discrepancy.**

## 6. Why P5 failed, measured rather than explained away

The N = 100 truncation bias is not constant in x. Measured from the published pairs, same x, same
gl_degree, only N varied:

| x | log10 lambda(N=100) - log10 lambda(N=140) |
|---|---|
| 7 | +0.0109 |
| 11 | +0.0580 |
| 13 | +0.0666 |
| 17 | +0.1903 |
| 19 | **+0.6160** (and +0.6935 against N = 180) |
| **25** (run this cycle, three N, only N varied) | **+8.9804** (N=100 vs 140), **+9.9963** (N=100 vs 180), +1.0158 (N=140 vs 180) |

**The bias grows monotonically and it is not slow.** At x = 25 we measured it directly rather than
inferring it: `log10 lambda_min(25, N=100) = -112.4877` `log10 lambda_min(25, N=140) = -121.4682` and
`log10 lambda_min(25, N=180) = -122.4839`. The N = 100 value that P5 was registered against is **ten
orders of magnitude** above the N = 180 value, at an x where the N = 100 point in the published sweep
would have been taken at face value. It is still falling at N = 180.

**P5 therefore fails under BOTH readings, and it fails differently under each, which is the finding.**
Scored against the quantity actually registered, `lambda_min(x=25, N=100)`: the sign is wrong,
`pred - actual = -0.676`. Scored against the better-converged N = 140 value: the sign is **right**
(`pred - actual = +8.30`) and the registered magnitude bound of 3.0 is violated by a factor of 2.8.
🔑 **A PREDICTION ABOUT A TRUNCATED MEASUREMENT IS NOT A PREDICTION ABOUT THE OBJECT, AND WHICH ONE
YOU REGISTERED DECIDES WHICH WAY IT FAILS.** We registered the measurement. It failed. Had we
registered the object we would have been right about the direction and wrong about the size. P2, P3 and P4 are **interpolations** between neighbouring x
at the same N, and a slowly varying bias largely cancels between neighbours, which is why all three
landed inside 0.05 of their centres. **P5 is an extrapolation**, and a fit calibrated on points whose
bias runs from 0.01 to 0.62 was asked to predict a point whose bias is larger still.

🔑 **THE LAW: A SMOOTHLY VARYING SYSTEMATIC IS NEARLY INVISIBLE TO INTERPOLATION AND FULLY VISIBLE TO
EXTRAPOLATION.** Three predictions passing at 0.03 and one failing at 0.68 is not four tests of one
model; it is three tests of a difference and one test of a level.

**And it lands on c43.** c43 section 3 concluded `lambda_infinity > 0` partly from the fact that
`lambda_infinity = 0` is inadmissible in every decay family fitted **in N**. That is the same move,
in the other truncation variable, that has just failed its first out-of-sample test **in x**. The
conclusion is not thereby wrong (it is an implication of RH by Zhu Prop 2.3, and interlacing still
gives `0 <= lambda_infinity <= lambda(220)` rigorously), but **the evidential weight of the
decay-family half of that argument must come down, and we say so against our own result.**

## 7. What is NOT claimed

No proof claim. Nothing here bears on RH. `lambda_min > 0` at x = 13 remains unproven unconditionally
and is, per Zhu, a finite fragment of RH if anyone proves it. We did not extend the certified range and
we did not try. Every value above is a variational upper bound on the true window floor, at the stated
N, and the truncation direction is stated with each.

**Standing sentence unchanged: we have no route to a proof.**
