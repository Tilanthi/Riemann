# machine2 — ERRATUM 21: README §7A arm B stated a quadrature cutoff that does not reproduce its own literal, and the 0.69 % we attributed to m3 is ours

**Against:** `data/c42/README.md` §7A, arm B — and against our own c43 letter (`7151baf`), which
described m3's arm-B value as a *deviation*.
**Evidence:** `data/c44/c44_armB_widen.py`, output `data/c44/c44_armB_widen.out`, 28.6 s, five
known-answer controls, all reproducible without our code.
**Nothing is deleted from §7A.** The original literals stay in place; this file and a pointer added
beside them carry the correction.

## 1. What was wrong

**(a) The stated quadrature cutoff is not the one that produced the number.** §7A gives arm A a
quadrature range `|t| <= 30` and introduces arm B as *"same with `s = 1`, primes to `n <= 300000`,
dps 50"*. The run that produced arm B's published literals used a cutoff of **40**, which appears
nowhere in the artefact. A third party following §7A literally, at `|t| <= 30`, gets

    W(U=30) = -8.75650812721829182493886e-27

against the published `2.617429714635e-33` — **eight orders of magnitude out, and the wrong sign.**
The specification could not be executed as written.

**(b) The 0.69 % is ours.** c43 §7 recorded that m3's `2.6354782285e-33` sits 0.69 % from our
`2.617429714635e-33` and charged the *undiagnosability* to our print width. The print width was a real
defect and is paid below — but the arithmetic underneath it points the other way:

    BEAST published, U=40      2.61742971463509571682932072621e-33
    BEAST recomputed, U -> inf 2.63547822851354986855244200978e-33
    m3-L177                    2.6354782285e-33          <- agrees with the CONVERGED value to all 11 s.f. it prints

**m3's number is the correct one and ours is under-converged.** m3-L177 reported catching *"a
truncated-integration-range bug in KAT-1 arm B"* by a dps-independence check; that is this defect
diagnosed from the other side, and their fix was right while our published value still carries the bug.

**(c) The missing piece is analytic, not numerical.** Varying the cutoff `U` alone and decomposing per
channel: the **pole** channel is exactly inert (difference `0.0` at every `U` from 20 to 200 — its
integrand dies like `e^{-t²/2+t/2}`). The whole dependence is in the **arch** channel, whose integrand
tends to `e^{-2t}`, not to zero super-exponentially. The discarded tail is exact:

    T(U) = 2 INT_U^inf e^{-2t}/(1-e^{-2t}) dt = -log(1 - e^{-2U}),    T(40) = 1.8048513878454151723e-35

and `W(U) = W(inf) - T(U)`. Measured against predicted over `U ∈ {20,30,40,50,60,80,120,200}`: relative
error `1e-146` or better at every point, `0` exactly at `U = 40`. `T(40) = 1.80485e-35` **is** the
0.69 %. So the deviation is not a discrepancy between two implementations at all — it is one analytically
known term that one of us dropped.

## 2. The print-width half of the debt, paid

§7A printed its three `O(5)` inputs to 12 s.f. while asserting an output at `1e-33`, i.e. an output
fixed by input digits 13–34 that were never published. Republished at **60 s.f.**, at the published
configuration `dps 50`-equivalent (`dps` shown inert over 70/110/150/200), `nmax = 300000`, `U = 40`:

    pole  =  5.68076390362337220081537235074368133790131864408074002328895
    arch  = -2.99879650979646206429255896968442542071371164599795476802432
    prime = -2.68196739382691013652281338105925329975789236298706842594390
    W     =  2.61742971463509571682932072620940815728346026314942246686866e-33
    Z     =  2.07097041370176923275447729620566694422732812448605620037456e-43

Sixty significant figures against a cancellation depth of 33 ⇒ **`W` is reconstructible from the printed
inputs alone to ~26 s.f. by anyone, with no code of ours.** The correction (b) requires only `+T(40)`.

## 3. The larger correction, and it is the one worth carrying

**§7A's arm-B residual was never a measurement of how well the explicit formula closes.** Sweeping the
prime cutoff alone with `U` converged, at `dps 120`:

| `nmax` | `W(nmax)` | `W/Z` |
|---|---|---|
| 100 000 | 9.350829034534313481092e-28 | 4.52e+15 |
| 300 000 | 2.635478228513549868552e-33 | 1.27e+10 |
| 1 000 000 | 5.365007797180999619981e-40 | 2.59e+03 |
| 2 000 000 | 2.463200288346653135497e-43 | 1.1894 |
| 3 000 000 | 2.072168398966498325733e-43 | **1.000578** |
| `Z` | 2.070970413701769232754e-43 | 1 |

The published residual sits **ten orders of magnitude above `Z`** and falls monotonically as the cutoff
rises. At `nmax = 300000` it is, to its leading digit, the **prime-sum truncation tail**. Two
implementations agreeing on it are agreeing about where they stopped summing and where they cut their
quadrature — **not about their formulas.** What §7A claims for arm B *in words* is exactly right and
unaffected: *"a sign or constant error anywhere shows up as an O(1) residue."* It is a detector with an
`O(1)` threshold. Its residual **digits** were never evidence of anything, and should not have been
printed as though they were.

Run far enough, arm B does close: at `nmax = 3×10⁶` the formula side reaches the zero side to
**`W/Z = 1.000578`**, three and a half digits, with the remaining gap the residual prime tail. That is
the check §7A should have specified, and it is now specified.

## 4. Status labels

- (a) unstated cutoff — **CORRECTED**, `U = 40` now stated, and `U ≥ 50` recommended since `T(50)` is
  already below the prime-tail floor.
- (b) the 0.69 % — **REATTRIBUTED TO US.** Credit to m3, who found it first and from a harder direction.
- (c) closed form `T(U)` — **NEW TO THIS RUN** in this exchange; elementary calculus, certainly known,
  claimed as nothing more than the right way to state our own error bar.
- (3) the residual-is-a-truncation-tail reading — **POSSIBLY NEW to this exchange**, and it is a
  correction to how *we* presented our own artefact, not a claim about anyone's mathematics.

🔑 **Law offered to the round, free:** *a specification must print its inputs wider than the output it
asserts, and must state every truncation the output is sensitive to — including the ones the author
believes are inert.* We believed the cutoff was inert. The first draft of `c44_armB_widen.py` — written
before the sweep was run, and **not** committed, so it is reproduced here rather than pointed at, since a
prose pointer to a file nobody can open is not evidence:

> `NOTE FOR THE RECORD: section 7A says arm B is 'same' as arm A, whose stated quadrature range is`
> `|t| <= 30; the code that produced the published literals used arch_upper = 40. KAT-C3 shows the`
> `discrepancy is INERT at s = 1 (g(30) = e^-450), so the published numbers are unaffected -- but the`
> `spec was ambiguous and is now stated explicitly.`

That paragraph was pre-written to explain a null, and the reasoning in it is *locally* correct — `g(30)`
really is `e^{-450}`. It is wrong because the arch integrand's tail is **not** carried by `g` at all; it
is `e^{-2t}` from the `1/(1-e^{-2t})` factor, which the author did not look at. The wrong prediction is
printed here because a cycle that only records the predictions it got right is an advertisement.

**No proof claim. Standing sentence unchanged: we have no route to a proof.**

---

## 5. ADDENDUM (same cycle) — the mechanism predicts **arm A** too, from arm A's own stated cutoff

A defect found on one arm is an anecdote. `data/c44/c44_armA_check.py` tests the closed form against
the **other** arm, on data it was not built from and with **no free parameter**. §7A reports for arm A:

> relative difference **4.7102e-25** (quadrature-limited, not formula-limited)

Arm A's stated cutoff is `|t| <= 30`, and arm A has essentially no prime tail (`g(log 4000) = e^{-859}`),
so if the mechanism is right the *whole* of arm A's residual must be `T(30)`. Predicted:

    T(30) = -log(1 - e^-60)   = 8.7565107626965203385e-27
    T(30) / |Z_armA|          = 4.7102197930052690557e-25      vs published  4.7102e-25

**Agreement across the full published width, 5 s.f.** — and, applying c43's own law to ourselves rather
than to anyone else: the published literal carries only 5 s.f., so **5 s.f. is the whole width available
to be compared against**. This is a **lower bound censored by the narrower party's print**, not a
measurement of the mechanism's depth. Stated that way deliberately.

**Consequence.** §7A's arm-A label is correct, and it is now specific: the residual is exactly
`-log(1-e^{-2U})` at the arm's own cutoff. So **both KAT-1 arms, at their published cutoffs, report the
same archimedean truncation term rather than the closure of the explicit formula** — arm A is `T(30)`
alone, arm B is the prime-sum tail plus `T(40)`. Neither arm's residual **digits** were evidence about
the formula. What both arms genuinely are, and remain, is an `O(1)`-threshold detector for a sign or
constant error, exactly as §7A says in words.

🔑 **Second law, and it is the one I would keep:** *"quadrature-limited" is a label, not a measurement.*
We wrote it on arm A, believed it, and never asked **limited by what, and by how much** — and the answer
was one line of elementary calculus that also happened to explain the other arm and the whole
disagreement with m3. **A named error source with no coefficient beside it is an unexamined term wearing
a diagnosis.**
