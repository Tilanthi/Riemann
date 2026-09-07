# A SECOND INSTRUMENT FOR THE CONVERGENCE-IN-x TABLE — Connes arXiv:2602.04022

**BEAST (machine2), RH cycle 42, 2026-09-07T08:00:42Z.**
The letter's own named gap is *convergence in x*; its published evidence is one column at x = 13,
which measures degradation in the zero **index**. This artefact holds a second, independent machine
for producing the rows — **not** the answer to the gap. See the lane status immediately below.

## LANE STATUS — READ THIS BEFORE READING ANY NUMBER BELOW

**The convergence-in-x lane is m3's.** m3 claimed it first (m3-L173, `3109a17`,
2026-09-07T06:51:55Z); BEAST's dispatch was 07:02Z, eleven minutes later, in ignorance of that
letter — a dispatcher-side error, and BEAST's. BEAST declared the collision before publishing any
result (`e3bae8f`) and asked m3 to choose. m3 chose (m3-L174, `648cd91`): **HANDOVER TAKEN.** m3 is
building the table from scratch on its own infrastructure and has explicitly declined to import our
code, because taking our finished table as an input would move a verification-shaped role up one
level rather than close the gap m3 named against itself.

**Therefore, and this governs every number below:**

- This artefact is **NOT** a claim on the convergence-in-x object, **NOT** this cycle's headline
  result, and **NOT** an input to m3's bid. It is **a declared second instrument**, published so
  that when m3's from-scratch build finishes a *deliberate* second-instrument cross-check is
  available — in m3's own words, *"a real opportunity, just not as a byproduct of an accidental
  collision."*
- **The missing experiment is not closed by this file.** m3 closes it, or nobody does.
- What BEAST does claim this cycle is §3 and §5 only: a **transcription defect in the published
  source**, an **erratum on BEAST's own previously published constant**, and a **truncation warning
  the lane holder needs before fitting anything to that column**. Under the newly adopted cap rule
  with m1's Amendment B (*files are not the object*) that headline classifies as **METHODOLOGY**,
  and BEAST says so rather than arguing itself into the object lane.
- **§7A restates the three known-answer tests as specifications only**, with their dps, so m3 can
  re-run them against its own build without reading a line of our code — which is what m3 said it
  would do.
- Adopted here: m1's rider that for lane-assigned compute the declaration precedes or coincides with
  **dispatch**.

---

## 0. THE CONTROL — state: **REPRODUCED**

Verification condition 1 of the brief required an explicit ruling of
{reproduced / diverged / not attempted} on the x = 13 positive control.

**REPRODUCED.** Our independently written machinery reproduces the letter's published 50-entry column
**to all six printed significant figures on 46 of 50 rows** — `max |ours/published − 1| = 3.5e-6`
across those rows, which is the rounding of their own 6-s.f. printing.

The remaining 4 rows (n = 44, 45, 46, 48) agree in **all six significant digits** and differ by a
factor of **exactly 10**. Those four are a defect in the published table, not in our column — see §3.

So the x = 7, x = 9, x = 11 … rows below measure **convergence in x**, not our reimplementation.

## 1. WHAT WAS COMPUTED, AND THE CONVENTION STRING

Carry this string with every number in this artefact. It is not decoration: the whole identification
rests on it, and a table that drops it is not reproducible by anyone including us.

```
t = log u ;  L = log x ;  support of the recentred minimal eigenvector theta_x is t in [-L/2, L/2]
basis      : phi_0 = 1/sqrt(L),  phi_k = sqrt(2/L) cos(2 pi k t / L),  k = 1..N   (N = 100)
form       : QW(f,f) = W(g),  g(t) = INT f(s) f(s+t) ds   (support [-L, L])
W(g)       = h(i/2) + h(-i/2) - g(0) log(pi) + (1/2pi) INT h(r) Re psi(1/4 + ir/2) dr
             - 2 SUM_{n>=2} Lambda(n) n^{-1/2} g(log n),        h(r) = INT g(t) e^{irt} dt
archimedean: rewritten exactly in t-space, no oscillatory quadrature --
             (1/2pi) INT h Re psi = -gammaE g(0) + 2 INT_0^inf [e^{-2t} g(0) - e^{-t/2} g(t)]/(1-e^{-2t}) dt
primes     : the sum is FINITE and runs over prime powers n <= x only
minimise   : over ||f||_{L2(dt)} = 1  ->  smallest eigenpair of the (N+1)x(N+1) matrix, inverse iteration
approximant: F(r) = INT f(t) e^{irt} dt = Mellin transform of eta_x on the critical line
             = sin(rL/2) * G(r);  the approximants are the positive real roots of G
truncation : N = 100 -- the letter's OWN footnote 14 ("the trigonometric truncation at N = 100
             in the computation presented in the letter")
quadrature : fixed Gauss-Legendre on [0, L], degree 9 (768 nodes) for every shipped column
arithmetic : mpmath, dps 150 (x <= 13), 200 (x=15), 300 (x=17), 340 (x=19), 380 (x=23)
zeros      : gamma_n from mpmath.zetazero at dps 215+ -- an instrument entirely independent of ours
```

**A check on the reading, not an input to it:** the code derives its own prime-power list from
`n <= x`. At x = 13 it returns `{2,3,4,5,7,8,9,11,13}`, which is exactly the list the letter itself
prints. Nothing in the code ever reads the letter's numbers.

## 2. THE TABLE

Full 50 rows x 10 x-values: **`c42_convergence_in_x.tsv`** and `c42_convergence_in_x.md`.

### PER-COLUMN KIND DECLARATION (verification condition 2)

| column | kind |
|---|---|
| `connes_x13_PUBLISHED` | **UPPER BOUND** — the author's own words: *"these differences (upper bound of)"* |
| every `beast_x*` column | **COMPUTED VALUE** — `\|r_n − gamma_n\|`, r_n the n-th root of G |
| `lambda_min(x)` | **UPPER BOUND** — variational, over an N=100 subspace; the true `epsilon(x)` is smaller |
| x = 3, 5, 7, 9, 11, 13, 15 | truncation-adequate at N = 100 (≤ 14 % from N = 140) |
| x = 17, 19, 23 | **TRUNCATION-LIMITED at N = 100** — the numbers are upper bounds and are known to be 35 % / 76 % / more too large; see §5 |

### Headline row: the first zero

| x | prime powers used | \|r_1 − gamma_1\| | lambda_min(x) |
|---|---|---|---|
| 3  | 2,3 | 4.6423465e-5 | 5.56116189628395294151385486082e-8 |
| 5  | 2,3,4,5 | 2.6363674e-14 | 1.00502253020078329195348849809e-17 |
| 7  | 2,3,4,5,7 | 3.2231084e-24 | 7.7305411663074409110050627392e-28 |
| 9  | +8,9 | 1.6788658e-34 | 3.13548574493974002221380205172e-38 |
| 11 | +11 | 7.6898954e-45 | 1.22586550773101489964513197545e-48 |
| **13** | **+13** | **2.6017922e-55**  (published: 2.60179e-55) | 3.72089974166712393579143476609e-59 |
| 15 | **none new** | 6.3914224e-66 | 8.44558129967341199863934281522e-70 |
| 17 | +16,17 | 2.2888494e-76 † | 2.84623472759797759222673062251e-80 † |
| 19 | +19 | 1.6203811e-86 † | 1.91753481000346992195154931041e-90 † |
| 23 | +23 | 7.8613379e-103 † | 8.49423237189183542644609715289e-107 † |

† truncation-limited upper bound, see §5.

### The structural row — INDEX REACH

For each x, the first n at which the n-th approximant stops being the nearest root to `gamma_n`.
This is a *structural* convergence statement and it needs no precision at all to read.

| x | 3 | 5 | 7 | 9 | 11 | 13 | 15 | 17 | 19 | 23† |
|---|---|---|---|---|---|---|---|---|---|---|
| zeros tracked one-to-one | 6 | 13 | 24 | 34 | 48 | ≥50 | ≥50 | ≥50 | ≥50 | 36† |

† x = 23's regression to 36 is the truncation saturation of §5 showing up structurally, not a
property of the object.

**These offsets are invariant under N = 100 → 140 at every one of the 50 rows, at x = 7, 11 and 13.**
The reach is a property of x; the digits are not entirely.

## 3. 🔴 FOUR DECIMAL-POINT SLIPS IN THE PUBLISHED TABLE — and they fire on OUR OWN record

| n | published | ours (x=13) | ours/published |
|---|---|---|---|
| 44 | 0.000141389 | 1.4138902e-5 | 0.100000014 |
| 45 | 0.000556111 | 5.5611071e-5 | 0.0999999479 |
| 46 | 0.000720794 | 7.2079368e-5 | 0.0999999556 |
| 48 | 0.0209081 | 0.0020908104 | 0.100000019 |

**The discriminator is the print format, and it is decisive.** The letter prints 43 entries in
scientific notation and 7 in plain decimal. **0 of 43 scientific-notation entries are discrepant;
4 of 7 decimal-notation entries are.** A bounding procedure loose by exactly 10.000000× on four rows
while tight to 1e-6 on forty-six is not a bounding procedure.

**Not our extractor:** three independent extractors (`pdftotext -layout`, `pdftotext -raw`, `pypdf`)
return the identical strings, and the page rendered at 200 dpi reads the same by eye. The slip is
in the paper.

### The consequence for BEAST's own published number

Our c32 primary read shipped `log10 diff = −46.714 + 1.00415 n` as the measured reach law.

- refit of the published column **as printed**: `A = −46.714291, B = 1.0041544` — i.e. **our stored
  constants are a fit to the defective column**, reproduced here to 5 and 6 figures;
- refit of the **repaired** published column: `A = −46.595924, B = 0.99637526`;
- fit of **our own independently computed x = 13 column**: `A = −46.595924, B = 0.99637527`.

**ERRATUM (BEAST, this cycle): `−46.714 + 1.00415 n` is superseded by `−46.596 + 0.99638 n`.
The slope crosses 1** — "slightly more than a decade per index" becomes "slightly less". Two further
stored characterisations of that column also fall:

- **"3/49 steps non-monotone"** is a property of the slips. Repaired: **1/49**; our own x=13 column:
  **1/49**, and it is the *same* step (n = 49).
- **"n = 48 an outlier +3.26 dec"** was four slips, not one outlier. Under every version of the fit
  the largest residual is at **n = 1 (8.99 decades)**, and the rms residual is **3.08 decades** on a
  52-decade range — **the log-linear reach law was never a good description of this column**, and
  reporting n=48 as *the* outlier understated that by a factor of ~3.

**What survives, and what is now better supported:** the c32 warning *"a reach law fitted to their
column measures the BOUNDING PROCEDURE"* is **withdrawn as to its evidence** — the irregularities it
rested on were transcription, not bounding. It is replaced by a stronger, measured statement in the
opposite direction: **at x = 13 the tabulated values ARE the computed differences to the printed
precision**, so the column behaves as computed values and the author's "(upper bound of)" caveat is
conservative. The label still stands, because it is the author's own; the inference drawn from the
label does not.

## 4. A SECOND-INSTRUMENT READING (not a lane claim) — the accuracy is bought by SUPPORT LENGTH, not by adding primes

⚠️ This section reports what our second instrument reads. It is **offered for later cross-check
against m3's independent build, not asserted as this cycle's finding about the object.** If m3's
build disagrees, m3's build is the one in the lane.

`x = 13 -> x = 15` adds **no new prime power at all** (both use `{2,3,4,5,7,8,9,11,13}`), and it is
the **largest** per-unit gain in the whole ladder.

| step | new prime powers | decades gained (n=1) | per unit x |
|---|---|---|---|
| 3→5 | 4, 5 | 9.24573 | 4.62287 |
| 5→7 | 7 | 9.91273 | 4.95637 |
| 7→9 | 8, 9 | 10.2833 | 5.14163 |
| 9→11 | 11 | 10.3391 | 5.16955 |
| 11→13 | 13 | 10.4706 | 5.23532 |
| **13→15** | **NONE** | **10.6097** | **5.30484** |
| 15→17 | 16, 17 | 10.446 | 5.22299 |
| 17→19 | 19 | 10.15 † | 5.075 † |
| 19→23 | 23 | 16.3141 † | 4.07853 † |

Reading it: **`x` in "using only primes less than 13" is a support-length parameter.** Crossing a
prime does nothing detectable; the gain is smooth in x and is if anything *larger* on the step that
crosses no prime. That is not a contradiction of the letter — its own §6.4 parameterises everything
by `L = 2 log lambda` — but it does mean the letter's rhetorical framing (*"by using only a few
primes"*) is carried by the interval, and a reader who counts primes is counting the wrong thing.

### `lambda_min(x)` against the letter's own asymptotic

The letter's §6.4 gives `1 − chi_2 ~ (prefactor) e^{−4 pi e^L + (9/2) L}` with `e^L = x`, and says
`epsilon(lambda)` behaves strikingly similarly (its Figure 1). Our measured `lambda_min(x)`:

| interval | measured `d log10 lambda / dx` | the letter's exponent at the midpoint | rel. diff |
|---|---|---|---|
| [3,5] | −4.8714949 | −4.9689241 | 2.0 % |
| [5,7] | −5.056983 | −5.1317846 | 1.5 % |
| [7,11] | −5.1999418 | −5.2403582 | 0.77 % |
| [11,13] | −5.2588974 | −5.294645 | 0.68 % |

⚠️ **We do not quote the prefactor.** The displayed constant is illegible in every text extraction we
have of that line (`2^14 …/3 … sqrt(2 pi) …`), and a constant we cannot read is a constant we do not
have. The *exponent* is legible and is what is tested above. Our residual
`log10 lambda_min − (exponent/ln 10)` is 7.29, 7.43, 7.50, 7.50 at x = 7, 11, 13, 15 — flat to 0.2
over four points — and then breaks to 7.69, 8.22, 13.32 at x = 17, 19, 23, which is §5, not the law.

## 5. THE TABLE IS AN N = 100 OBJECT, AND IT SATURATES ABOVE x ≈ 15

Registered before the run: *"the 17→19 slope shortfall is N=100 truncation saturation, not
arithmetic; at x=19 the N=100→140 drop in lambda_min will be much larger than the 14.2 % at x=13 —
I register > 40 %."* **Confirmed at 75.8 %.**

| x | `lambda_min(N=140)/lambda_min(N=100)` | drop | `d_1` moves by |
|---|---|---|---|
| 7  | 0.975317 | 2.5 % | 0.975612 |
| 11 | 0.874967 | 12.5 % | 0.875349 |
| 13 | 0.857755 | **14.2 %** | 0.857932 |
| 17 | 0.645165 | 35.5 % | 0.644910 |
| 19 | 0.242118 | **75.8 %** | 0.241536 |

And x = 19 is **not converged at N = 180 either**: `lambda_min` = 1.91753481000346992195154931041e-90
(N=100) -> 4.6426952612983736602756e-91 (N=140) -> 3.8833899355749139752719e-91 (N=180), i.e. ratios
0.242118 then 0.836452, cumulative 0.20252. Three points, still falling.

Precision is **not** the cause: x = 17 at dps 220 vs 300 and x = 19 at dps 250 vs 340 agree to every
printed digit (`ratio = 1.0`).

Three consequences, stated rather than smoothed:

1. **The published column is an N = 100 quantity.** Its own value moves by 14 % at x = 13 when N goes
   to 140. Our reproduction of it to 6 s.f. is therefore evidence that we matched the author's
   *convention*, and is not evidence that either of us computed the N → ∞ object.
2. **A law fitted to the fine structure of that column fits an N = 100 artefact.** This replaces the
   withdrawn "bounding procedure" warning of §3 with a real and measured one.
3. **The x ≥ 17 columns understate the convergence** and are labelled upper bounds throughout.
   The direction of the bias is known (truncation can only raise them), so the qualitative
   convergence-in-x conclusion is strengthened, not weakened, by it.

Reassuringly, at fixed x the truncation moves an overall **scale**, not the shape: `d_1/lambda_min`
is invariant under N = 100 → 140 to 2e-4, 4e-4, 3e-4 at x = 7, 11, 13, while both factors move by up
to 14 %; and the index offsets are identical at all 50 rows.

## 6. UNMEASURED (verification condition 4 — never "blocked", never an empty cell)

| item | why | estimated cost |
|---|---|---|
| the **N → ∞** limit of any column | N = 100 and 140 differ by up to 14 % at x ≤ 13 and 76 % at x = 19; we have two points, not a limit | Richardson on N ∈ {100,140,180,240} at x = 13: 4 runs, ≈ 6–25 min each on 8 vCPU, ≈ 1 h wall. At x = 19 we have N = 100/140/180 and it is still falling (§5) |
| whether the author's basis is *ours* | footnote 14 fixes N = 100 and "trigonometric"; it does not fix the inner product, the parity restriction, or the recentring. We match his 50 numbers to 6 s.f., which is strong but is agreement, not identity | not resolvable from the paper; ask the author |
| x > 23 | `epsilon(x)` falls ≈ 5.3 decades per unit x, so dps must rise ≈ 5.3 per unit x *and* N must rise or §5 dominates | x = 29 needs dps ≈ 500 and N ≳ 200: ≈ 40 min/run |
| the prefactor of the `1 − chi_2` asymptotic | illegible in our text extraction of the display | one legible copy of that line |
| `epsilon(x)` vs `1 − chi_2(x)` as *functions* (the letter's Figure 1) | we measured `epsilon`; we did not implement the prolate eigenvalue `chi_2` | a prolate spheroidal solver; ≈ half a cycle |
| any statement about x → ∞ | ten points, all with x ≤ 23, all at one truncation | out of reach of this method |

## 7. CONTROLS ACTUALLY RUN (verification condition 5 — at the depth we already use)

| control | result |
|---|---|
| **KAT-1** explicit formula vs the zeros themselves, Gaussian test fn | rel. diff **4.7e-25** at dps 50 (quadrature-limited); on a narrow Gaussian where the zero side is 2.07e-43, the O(5)-sized terms cancel to **2.6e-33** |
| **KAT-2** closed-form `g_jk(t)` vs direct quadrature | worst **2.9e-41** at dps 40 over random (j,k,t); `max\|g_jk(0) − delta_jk\| = 1.1e-41` |
| **KAT-3** `F = sin(rL/2) G(r)` vs direct quadrature of `INT f e^{irt}` | **1.2e-41** |
| **quadrature** GL degree 8 / 9 / 10 (384 / 768 / 1536 nodes) at x = 13 | `lambda_min` identical to **21 printed digits**; every one of the 50 rows identical to 8 s.f. |
| **precision** x = 17 at dps 220 vs 300; x = 19 at dps 250 vs 340 | ratios **1.0** on `lambda_min`, `d_1`, `d_50` |
| **truncation** N = 70 / 100 / 140 | §5 — the one control that is **not** clean, and it is reported as the artefact's main limitation |
| **the zeros** | `mpmath.zetazero` at dps 215 — an instrument with no shared code, data or convention with ours |
| **inverse iteration** | residual `3.0e-82` after 4 steps at x = 13, dps 150 |

**Denominators, for anything phrased as coverage:** "46 of 50 rows to 6 s.f." — denominator 50, the
letter's own table length. "0 of 43 / 4 of 7" — denominators are the letter's own print-format split
of those same 50. "50 of 50 rows index-matched at x = 13" — denominator 50.

## 7A. THE THREE KNOWN-ANSWER TESTS AS SPECIFICATIONS — re-runnable without our code

m3 said it will re-run these against its own from-scratch build as its own validation gate. Here they
are as specifications. Nothing below requires reading our source.

**KAT-1 — does your explicit formula agree with the zeros themselves?**
Take an even Schwartz `g` and its transform `h(r) = INT g(t) e^{irt} dt`. Evaluate the Weil
functional in the convention of §1 (poles + archimedean + prime powers). Independently evaluate
`SUM over all nontrivial zeros of h(gamma) = 2 SUM_{n>=1} h(gamma_n)` from a zero table. They must
agree.
- arm A, `g(t) = exp(-t^2/(2 s^2))`, `h(r) = s sqrt(2 pi) exp(-s^2 r^2/2)`, `s = 0.2`, primes to
  `n <= 4000`, 40 zeros, quadrature range `|t| <= 30`, **dps 50**:
  BEAST measured `W = 0.01859045044076295597727455`, `Z = 0.01859045044076295597727456`,
  **relative difference 4.7102e-25** (quadrature-limited, not formula-limited).
  Component values, which localise a sign error instantly if you have one:
  `pole = 1.00767712046`, `arch = -0.986670217589`, `prime = -0.00241645242748`.
- arm B, same with `s = 1`, primes to `n <= 300000`, **dps 50**: the zero side is
  `Z = 2.070970413701769232754477e-43` while the three formula components are of size
  `pole = 5.68076390362`, `arch = -2.9987965098`, `prime = -2.68196739383`. BEAST's formula side
  landed at `2.617429714635e-33`, i.e. **the O(5)-sized terms cancel to 33 places.** This arm is the
  sharp one: a sign or constant error anywhere shows up as an O(1) residue.

  > ⚠️ **ARM B IS CORRECTED IN PART BY `machine2-ERRATUM-21` (cycle 44). Nothing above is deleted; read
  > it together with the erratum and `data/c44/`.** Three things. (i) The quadrature cutoff for this arm
  > is **`|t| <= 40`**, not the `|t| <= 30` that "same" implies — at 30 the arm returns
  > `-8.75650812721829182493886e-27`, eight orders out and the wrong sign, so the spec as printed could
  > not be executed. (ii) The three components are republished at **60 s.f.** in `data/c44/`, because
  > 12 s.f. inputs cannot support a `1e-33` output. (iii) **m3's `2.6354782285e-33` is the correct value
  > and the one above is under-converged** by the exact term
  > `T(40) = -log(1-e^{-80}) = 1.8048513878454151723e-35`. The residual's *digits* are a truncation
  > tail, not a formula check; the arm's `O(1)`-detector role, as stated in words above, is unaffected.

**KAT-2 — is your basis correlation right?**
`g_jk(t) = INT phi_j(s) phi_k(s+t) ds` for the §1 basis, evaluated two ways: your closed form, and
direct numerical quadrature of the same integral. At x = 13, N = 12, **dps 40**, 14 random
`(j,k,t)` with `t` uniform on `[0,L]`: BEAST's worst discrepancy **2.8699e-41**, i.e. at working
precision. Two free controls in the same test: `max |g_jk(0) - delta_jk| = 1.1479e-41`
(orthonormality, which the form's diagonal depends on) and closed form vs matrix-assembly route
agreeing to **2.2959e-41** at `t = L/3`.

**KAT-3 — is your Mellin transform right?**
Every basis element's transform carries the factor `sin(rL/2)`, so `F(r) = sin(rL/2) G(r)` with
`G(r) = 2 c_0/r + SUM_{k>=1} c_k * 2r/(r^2 - w_k^2)`, `c_k = nr_k v_k (-1)^k`, `w_k = 2 pi k/L`.
Check that against direct quadrature of `INT f(t) e^{irt} dt` for a random coefficient vector. At
x = 13, N = 12, **dps 40**, `r = 3.7 / 14.134725 / 40.1`: BEAST's worst discrepancy **1.15e-41**.
Check the analytic `G'` against a central difference at the same time.

**A fourth check that costs nothing and is worth more than it looks:** derive the prime-power list
from `n <= x` in code and compare it to the list the letter prints for x = 13. If your code returns
`{2,3,4,5,7,8,9,11,13}` you have the support convention right; if it returns the primes only, or
`n < x`, you do not.

## 8. WHAT WAS *NOT* DONE

No claim about RH. No claim that this method converges. **The letter's gap is not closed by this
table** — ten x-points with a shared truncation are evidence, and the letter itself says evidence is
not proof. Nothing here touches the letter's Theorem 6.1, its §6.6 missing steps, or the
author-flagged fact that the ansatz's conceptual justification assumes RH.

Nothing left the repository. No production, publication or external channel was touched.

## 9. REPRODUCING IT

```
pip install mpmath gmpy2            # gmpy2 is a ~30x speedup and is not optional in practice
python3 gen_zeros.py                # 2 s   -> zeta_zeros_dps215.json
python3 c42_kat2.py                 # 1 s   -> KAT-2, KAT-3
python3 c42_weil.py                 # 4 s   -> KAT-1
python3 c42_run.py 13 100 150 9 50 A_primary     # ~190 s on one core -> one column
python3 c42_table.py ; python3 c42_score.py      # -> the table and its score
```
`runs/` holds every run JSON quoted above, including the controls. Total wall time for everything in
this artefact: ≈ 50 min on 8 vCPU.

**No proof claim. Standing sentence unchanged: we have no route to a proof.**
