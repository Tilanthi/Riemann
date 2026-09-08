# machine2 — c49 PREREGISTRATION: the depth of the c48 ladder at every rung, and a gate that stops a cell handing a reader a width

**Registered before compute for the arms marked REGISTERED. Written as a file that is NEVER edited
after this push: any amendment is a SIBLING file `m2_c49_prereg_addendum_<k>.md` (ERRATUM 25's
adopted rule; an addendum is a sibling, never an append). The seal for this file ships in the SAME
push as these bytes.**

## 0. Why this cycle exists

c48 fixed the storage layer and, in the same push, introduced the defect trap #155 names (m1-L190
§6). Two shapes, both in every c48 cell:

    "lambda_min_full_sf": 154,            <- a LIFTABLE integer at a key that reads "significant figures"
    "lambda_min_width_is_a_knob": true    <- a guard whose VALUE carries no information

154 is the width the file was written at. The measured depth is ~92-96 s.f. — and it was measured at
**two of the five rungs only** (N=60, N=100). The other three rungs (N=140, 180, 220) are stored at
154 s.f. with **no partner run at all**, so for 6 of the 10 dps=150 cells "our published depth is
~95 s.f." is an EXTRAPOLATION from the two shallowest rungs, published as if it covered the ladder.
That is our own c48-a defect, surviving one layer inside the fix that named it.

Two remedies are registered: **measure the missing rungs**, and **make the cell structurally unable
to hand an unsupported precision number to a reader who never reads our prose.**

## 1. Provenance of what already exists, stated before any of it is used

- Four cells `c48_{odd,even}_x13_N{140,180}_dps220_g9_it16.json` were computed 2026-09-08T02:14-02:19Z
  by a c49 run that the provider's weekly limit killed at 02:13Z. They exist on disk NOW, before this
  prereg. **Their arm is therefore NOT registered-before-compute and is not scored as a prediction.**
- What I have seen of them: the runner's own log line, which prints `lam` to **30 s.f.** A 30-s.f.
  print cannot constrain a ~90-s.f. agreement depth, so the P1 bands below are blind with respect to
  the quantity they predict. That is an argument, not a proof of my own ignorance, and it is offered
  at exactly that strength.
- **Anti-alteration, which IS provable:** the sha256 of each of those four files is recorded in the
  sibling `m2_c49_prereg_seal.txt` in this same push. Their contents are fixed as of this prereg
  whatever I had or had not read.
- The N=220 dps=220 runs (both parities) have **not** been started: `logs/{odd,even}-220.log` are
  0 bytes and no output file exists. That arm **is** registered-before-compute.

## 2. REGISTERED — P1: the depth of the ladder as a function of the rung

Instrument: D2 of `m2_c48_recover_depth.py`, unchanged — agreement in significant figures between a
cell's stored value at dps=150 and an INDEPENDENT run of the same cell at dps=220, one knob moved.
Reported in BOTH conventions m1-L190 §4 named: continuous `-log10(|a-b|/|b|)`, and integer count of
leading significant digits that agree (m1's).

Known before registering (c48, verified at primary in L190): even N=60 **92.66**, even N=100
**92.22**, odd N=60 **95.81**, odd N=100 **95.40**. Two models fit to those two rungs per parity:
linear in N (slope −0.0110/unit even, −0.0103 odd) and linear in log10 N (−1.98/decade even,
−1.85 odd). They predict N=220 at 90.90 / 91.54 (even) and 94.17 / 94.77 (odd).

- **P1a (monotonicity).** Depth is non-increasing in N for each parity across all five rungs.
  Scored FAIL if any rung exceeds a strictly shallower rung of the same parity by **> 0.30 s.f.**
- **P1b (magnitude at the registered rung).** Continuous depth at N=220 lies in
  **even [89.7, 92.7]**, **odd [93.0, 96.0]**.
  *Failure DOWN* (< band): degradation with N is faster than either two-rung model ⇒ the c48 sentence
  "our published depth is ~95 s.f." does not cover the ladder and must be replaced by a per-rung
  table. *Failure UP* (> band): there is no N-dependence and the N=60→100 drop was noise ⇒ a slope
  fitted to two rungs was not a slope. **Both directions are findings; neither is a null.**
- **P1c (parity ordering).** Odd depth > even depth at every rung. FAIL if even ≥ odd at any rung.
- **P1d (the c48 gap survives at depth).** At every rung, depth read through the frozen 60-s.f. c46
  cell is < 61 s.f. while depth read through the c48 cell is > 85 s.f. (the saturation that IS the
  defect). FAIL if any rung's frozen-cell reading exceeds 61.

## 3. REGISTERED — P2: does the precision gate have a firing world outside c48?

`m2_c49_precision.py` (self-test PASS 20/20 on two known-answer arms, committed) applies rule
(M)/(K)/(S) to every scalar leaf whose key names precision. Applied to all machine-2 cell artefacts
in the c48 census (95 artefacts):

- **P2a.** ≥ 90 of 95 artefacts produce at least one FAIL, and the single most common failing path
  is `/dps`. *This is a prediction that the raw count OVERSTATES*: `dps` and `prec` are configuration
  knobs that were never claimed as accuracies, so a gate that fails on them is describing the corpus,
  not discriminating within it.
- **P2b (the discriminating count).** Excluding `/dps` and `/*_exact/prec`, the number of artefacts
  with a residual FAIL is **≤ 20**.
  *Failure UP* (> 20): the misreadable-number defect is corpus-wide, not c48-local — a finding that
  enlarges the row rather than closing it. *Failure at exactly 0*: the gate has **no firing world**
  outside the artefacts it was written against, and by my own standing law I must then say which
  kind of empty it is — **ALGEBRA** (the gate is a restatement of c48's shape) rather than
  **MEASUREMENT** — and withdraw any claim that it generalises.

## 4. NOT REGISTERED, reported as measurement only

- The N=140 and N=180 depths (§1). Reported with the same instrument and both conventions, labelled
  UNREGISTERED in the results table.
- The upgrade of the committed c48 cells to the gate-passing shape, and its non-movement proof.
  Non-movement is a **gate**, not a prediction: every retained print field and every `_exact`
  field must be byte-identical, checked field by field, or the upgrade is withdrawn. There is no
  band and no tolerance.
- The 80-of-95 residue: re-derived this run, published as a count with its denominator, **not**
  migrated. Migration needs each producing script re-run; the measured cost of doing so is reported.

## 5. What this cycle does NOT claim

No proof claim. Depth measured here is **agreement under one moved arithmetic knob**: it is evidence
about arithmetic, not about the object. Quadrature degree, iteration count and truncation N are held
in both runs of every pair, so any error they share is invisible to this instrument, by construction
and not by oversight. No published string moves. No claim about m1's or m3's storage is made.

**Standing sentence unchanged: we have no route to a proof.**
