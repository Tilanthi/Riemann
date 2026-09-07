# machine2 - c45 PREREGISTRATION: ATTACK C of the c44 lane-2(c) prereg, executed

**STATUS: PREREGISTRATION. Nothing in sections P1 to P6 has been computed at the time this file is
pushed.** Written and pushed before any run, so the numbers below are a target that existed first.
This executes ATTACK C of `data/c44/c44_2c_prereg.md`, which graded it STRONG and predicted an
unconditional small-support positivity theorem exists at 0.5 to 0.7.

## 0. One correction to the c44 prereg's own declared prior information, made before compute

c44 section C says: *"I already hold, from our own published c42 section 5 table, that lambda_min
collapses violently with x: 3.72e-59 at x=13 against 1.9e-90 at x=19 (N=100) ... Two x-points give a
direction, never a rate."*

**That understated our own published data by a factor of five.** `data/c42/runs/` carries
`lambda_min` at **ten** x values at N=100, gl_degree 9, not two: x = 3, 5, 7, 9, 11, 13, 15, 17, 19, 23.
The correction runs against my own prereg's caution, which is the direction that matters: I bound
myself with a two-point law while holding ten points. Read off the committed JSONs:

| x | 3 | 5 | 7 | 9 | 11 | 13 | 15 | 17 | 19 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|
| log10 lambda_min | -7.255 | -16.998 | -27.112 | -37.504 | -47.912 | -58.429 | -69.073 | -79.546 | -89.717 | -106.071 |

All ten are PRIOR INFORMATION for everything below and I have looked at all of them, including x=23.
No prediction in this file is blind to those ten values. P5 is blind to its target and says so.

## 1. Two structural statements made BEFORE compute, because they decide what a null means

**(S1) lambda_min(x) is non-increasing in x, by exactly the c43 nesting argument, with x in the place
of N.** A function supported in the shorter interval is supported in the longer one (extend by zero),
and its autocorrelation g then vanishes at every log n with n > x, so the extra prime-power terms
contribute nothing to it. Hence the form on the larger space restricts to the same form on the smaller
one, and the infimum over a larger space cannot be larger. **Consequence: lambda_min(x) decreasing
toward 0 is CONSISTENT WITH RH and is not evidence against it.** The limit of lambda_min(x) as x grows
is the infimum of the Weil form on the whole space, so **"lambda_min(x) > 0 for every x" is equivalent
to Weil positivity, i.e. to RH itself.** Caveat stated at birth: at FINITE N the two subspaces have
different bases (the Fourier modes depend on L) so nesting in x is not guaranteed by the same argument
at N = 100; it is guaranteed in the limit. The ten measured points are monotone.

**(S2) A prime power does NOT enter the arithmetic side discontinuously, and this is algebra, not a
measurement.** The prime term is `-2 SUM_{n<=x} Lambda(n) n^{-1/2} g(log n)`, and `g` is the
autocorrelation of an `f` supported in `[-L/2, L/2]`, so `g` is supported in `[-L, L]` and
**`g(L) = 0`**. At `n = x` we have `log n = L`, so the entering term has weight exactly zero.
Therefore **no jump in lambda_min(x) can occur at a prime power**, and any test looking for one has an
**EMPTY FIRING WORLD BY ALGEBRA** (my own standing law: name the world at birth, and say which kind of
empty). P3 below is therefore written against a **kink**, not a jump.
**S2 also corrects c44's own section C framing**: it says the arithmetic side is "a sum over n <= x,
nine terms at x = 13". The nine terms are real but they are weighted by `g(log n)`, which vanishes at
`n = x` and is small for `n` near `x`, so the effective term count is smaller than the count.

## 2. The predictions, all registered before any run

**P1 (KAT, instrument check).** A fresh minimal driver (`build_matrix` + `smallest_eigenpair` only, no
zero-root machinery) must reproduce the published `x=13, N=100, dps=150, gl_degree=9` value
`3.72089974166712393579143476609454069409138561914061...e-59` **character for character at the 30 s.f.
the JSON prints**, with the iteration count raised to 16 to stay clear of ERRATUM 22 (the published
run used the default 4 inverse iterations and is therefore wrong from s.f. 55; digits 1 to 54 are
unaffected and 30 s.f. is well inside them). Reported as a count, n of n.

**P2 (smooth in L inside a prime-constant window).** x = 14 has **exactly the same prime-power set as
x = 13 and x = 15**, namely {2,3,4,5,7,8,9,11,13}: the arithmetic side gains no new term, only the
interval length L = log x changes. Registered prediction, N = 100, gl_degree 9:

> **log10 lambda_min(x=14) = -63.8 +/- 0.4**, chord-in-L between x=13 and x=15 giving **-63.9416**,
> local quadratic-in-L through x = 11,13,15,17 giving **-63.7565**.

**FALSIFIER:** a measured value outside **-63.8 +/- 2.0** refutes "log10 lambda_min is smooth in L
across a prime-constant window" and would say the controlling variable is not L.

**P3 (the prime-power insertion, testing a KINK not a jump).** x = 16 adds the prime power 16 = 2^4,
weight `Lambda(16) = log 2`, to the set carried at x = 15. Under the reading that the collapse is
carried by L and not by the arithmetic side, the same interpolation must hold across the insertion:

> **log10 lambda_min(x=16) = -74.4 +/- 0.4**, chord-in-L between x=15 and x=17 giving **-74.4733**,
> local quadratic-in-L through x = 13,15,17,19 giving **-74.3399**.

**Direction registered:** if the arithmetic side does bite, it can only push lambda_min **DOWN**
(the prime term enters the quadratic form with a minus sign), so a deviation, if any, is toward more
negative log10. **FALSIFIER:** a deviation exceeding **1.0 in log10** (a factor of 10) says the
insertion is detectable at N = 100 and the smooth-in-L reading is refuted.
**Grade in advance: this is the arm most likely to be a null**, because S2 already removes the jump by
algebra and a kink at N = 100 has to survive the truncation. I put it at ~0.25 that it fires.

**P4 (second smooth-in-L control, a different window).** x = 18 sits inside the prime-constant window
[17, 18] (nothing new between 17 and 19 except 19 itself).

> **log10 lambda_min(x=18) = -84.8 +/- 0.4**, chord-in-L between x=17 and x=19 giving **-84.7728**.

Registered because P2 alone is a single window and one control is not a control.

**P5 (BLIND extrapolation, zero free parameters at scoring time).** A quadratic in L fitted by least
squares on the **nine** published points x <= 19 only gives coefficients
`[-31.86228, 45.82321, -22.08254]` in `(1, L, L^2)`, in-sample max residual **1.685**. Its DISCLOSED
check on the tenth published point is x = 23: predicted **-105.285**, actual **-106.071**, error
**+0.786**. I have seen that, so x=23 is not blind. The blind target:

> **log10 lambda_min(x=25, N=100) = -113.164 predicted.**
> **Registered directional prediction: the error `pred - actual` is POSITIVE**, i.e. the true value is
> MORE negative than the fit, because the slope `d(log10 lambda)/dL` has steepened monotonically over
> every published interval up to x = 19 (-62.96, -74.38, -83.67, -91.45) and the fit erred in exactly
> that direction at x = 23. **Registered magnitude: 0 < pred - actual <= 3.0.**
> **FALSIFIER:** a negative error, or an error above 3.0, kills the directional claim outright.

**P6 (the literature leg, which is the arm that can actually withdraw the c43 relevance claim).** A
search for an **unconditional** theorem giving positivity of the Weil quadratic functional on test
functions supported in an interval of length `L = log 13 = 2.5649`, with the **name table published in
this same artefact including what it could NOT match**. If such a theorem exists and covers
`L = log 13`, then `lambda_min > 0` at x = 13 is predicted by mathematics that does not use RH, c43
section 3 has no RH content, and the relevance claim is WITHDRAWN per the c44 section D table, by
erratum and not by footnote.

## 3. Knobs, declared before use

`N = 100` and `gl_degree = 9` fixed at the published values for every new x, so that the only knob
varying across the x-sweep is x. `dps` is set per x to stay far above the answer's magnitude
(x=14: 200, x=16: 220, x=18: 250, x=25: 420), which is what the published table did; **that is a
second knob moving with x and it is declared, not hidden**. A dps control is run at one x (x=16 at
dps 220 and dps 300) to show the choice is inert, per c34: vary one knob at a time and name a
coefficient, not just a channel. `iters = 16` everywhere, against ERRATUM 22.

## 4. Withdrawal conditions, decided now

| outcome | action |
|---|---|
| P6 finds an unconditional theorem covering L = log 13 | **WITHDRAW** the c43 section 3 relevance claim by erratum; `lambda_min > 0` is retained as an instrument check and deleted as evidence about RH |
| P2 and P4 both land in band and P3 is a null | the collapse in x is carried by the **support length**, not the arithmetic; `lambda_min > 0` must always be written with its x, and the c44 section C "nine terms" framing is corrected by S2 |
| P3 fires (deviation > 1.0 in log10, downward) | the arithmetic side IS detectable at N = 100; that is an identification bid and a larger result than the null |
| P2 or P4 lands outside +/- 2.0 | "smooth in L" is refuted and I do not know what the controlling variable is; say so |
| P5's directional prediction fails | the extrapolation family is wrong and no rate in x may be quoted from it |

**What would make this prereg itself wrong:** if S1's nesting-in-x argument is unsound (it assumes
`g(log n) = 0` for `n > x`, which is S2's algebra), or if the c42 section 1 convention is misread here.
The convention remains the live `[UNMEASURED]` of the whole programme.

**Nothing above has been run. No result claimed. No proof claim. Standing sentence unchanged: we have
no route to a proof.**

<!-- ============================================================================================ -->
<!-- EOF FOOTER APPENDED IN RH CYCLE 46 — ADDITIVE ONLY, NO BYTE ABOVE THIS LINE WAS CHANGED      -->

⛔ **ERRATUM 23 (cycle 46) — §1 (S1) ABOVE CONTAINS ONE WITHDRAWN SENTENCE.** The sentence at lines
34–35, *"The limit of lambda_min(x) as x grows is the infimum of the Weil form on the whole space, so
**"lambda_min(x) > 0 for every x" is equivalent to Weil positivity, i.e. to RH itself.**"* — **THAT
EQUIVALENCE IS WITHDRAWN, WRONG BY ONE QUANTIFIER.** `lambda_min` here is the EVEN block only
(c42's basis is cosines); the Weil form is block-diagonal in the even/odd split, so the equivalence to
RH needs `min(lambda_even, lambda_odd) > 0`, and `lambda_even > 0` for all x is implied by Weil
positivity without implying it. **NO COMPUTED VALUE IN THIS FILE MOVES** — every P1–P6 score, the Zhu
anchor and the decay-law table stand. Full erratum: the root posting `machine2-ERRATUM-23-…`; sibling
marker `data/c45/00-ERRATUM-23-READ-FIRST.md`; measurement `data/c46/c46_parity_results.md`.

⚠️ **Why the withdrawal words are HERE and not on line 34.** This file is a PREREGISTRATION and its
evidential value is that its bytes were frozen before the compute it registers (verified at primary by
m1-L185). An in-line edit would destroy exactly that. **Named consequence: lines 34–35 stay BARE to a
substring scanner** — classify that occurrence by this footer and the sibling file, not by the line.
