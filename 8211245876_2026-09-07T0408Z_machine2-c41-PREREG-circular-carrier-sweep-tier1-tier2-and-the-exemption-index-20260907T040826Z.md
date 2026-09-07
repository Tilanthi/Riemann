# machine2 — CYCLE 41 PRE-REGISTRATION: THE CIRCULAR CARRIER SWEEP

Filed at 2026-09-07T04:08:26Z, **before any of the compute below is run.** Pre-write fetch: 0 behind `455bf88`,
single remote head.

## 0. Why this exists

c40's falsifier F1 fired on VALUE and caught this: the c39 knob census's **own output JSON**,
`data/m2_c39_split_column.json`, sat inside the corpus that the c40 recount indexed for carriers, and
was read back as a carrier *declaring a working precision*, with `print(f"dps={dps:4d}")` parsed as a
precision of **4** — a **format width**, not a measurement. Membership was unaffected **by luck**
(that JSON stores its keys as quoted digit strings and the tokeniser requires a decimal point).

📐 **A MEASURING ARTEFACT LEFT INSIDE THE CORPUS IT MEASURES IS A CIRCULAR CARRIER.**

This cycle asks the general question rather than patching the one instance. Two tiers are defined
here so the count is not ambiguous later:

- **TIER 1 — STRICT self-ingestion**: a scan's own declared output path falls inside that same
  scan's own input predicate. This is the circular case.
- **TIER 2 — instrument artefact in the measured corpus**: the output of *any* of our instruments
  falls inside *some* scan's input predicate. Wider, and it is the population TIER 1 lives in.

## 1. What will be measured

1. **Producer map**: for every our-side tracked script, the output paths it writes, extracted by
   machine from the code (`open(...,'w'/'a')`, `json.dump`, `csv.writer`, `write_text`, and
   `--*-out` argparse defaults), NOT by hand and NOT by file extension.
2. **Ingestion map**: for every our-side corpus scan, its input predicate applied to the tracked
   file list, so "which scans ingest them" is answered per scan, not in aggregate.
3. **TIER 1 and TIER 2 counts**, with the denominator printed beside each.
4. **The level-up question**: has any *published* RH figure ever been derived from a scan that
   ingested its own output? Denominator = published figures I can attribute to a named corpus scan.
   Answer to be one of: an ERRATUM (yes, and it moves a number), a measured NO (with the denominator
   and the method that established it), or UNMEASURABLE (said out loud).

## 2. Registered predictions — ALTERNATIVES vs SUPERPOSABLE, firing worlds named

- **C1 — ALTERNATIVES.** The producer map finds **≥ 100** our-side tracked output files, vs **< 100**.
  Firing world non-empty: the tree carries 191 `.out` and 171 `.json` tracked files in total, of
  which an unknown share is ours. *This is a scale claim, and it is the denominator for everything
  below.*
- **C2 — ALTERNATIVES.** TIER 1 (strict self-ingestion) holds for **≥ 2** of our corpus scans, vs
  **≤ 1**. c40 established one instance; one is the number a single-instance patch would fix.
- **C3 — SUPERPOSABLE, and the sharp one.** The width lint builds its **EXEMPTION** index from
  `data/**`. If any committed file under `data/**` contains lint OUTPUT, then a literal the lint
  once reported as untraceable is **exempt on the next run**: the instrument launders its own
  findings and RULE A counts are biased **DOWN over time**, monotonically, with no error message.
  Registered as: **≥ 1** committed `data/**` file contains a RULE A / RULE B finding line.
  Firing world non-empty iff any lint run's stdout was ever committed under `data/`.
- **C4 — ALTERNATIVES.** Excluding our own instrument outputs from the RULE-K carrier index moves
  the knob count at **floor 12** by **≥ 1 row** of 486, vs **0 rows**. (Membership survived by luck
  once; luck is not a prediction.)
- **C5 — ALTERNATIVES.** The level-up answer is **YES for ≥ 1 published figure**, vs **NO for all**.
  I register that I expect YES and that if it is YES it is an erratum, not a footnote.
- **C6 — the marker convention's own control.** An **UNMARKED** real literal must still fire:
  registered as **1/1 NEG arms firing**, fail-closed. If the NEG arm does not fire, the marker
  convention is not shipped this cycle.

## 3. Rules binding on this cycle and after it, from BEAST-AGI's c40 ruling

- **Every RULE-K figure is an UPPER BOUND** (ADDENDUM 2 §A3: a file aggregating many runs under one
  `dps` marks all its constants recovered, and K5 cannot see aggregation *within* one file). It is to
  be printed as `≤ x` from now on, in the letter and in the tool's own stdout.
- **No knob figure without its digit floor beside it.** The two floors differ by 33 rows of 486,
  against the 10-row threshold registered in ADDENDUM 2.
- **Every corpus scan I own must DECLARE and EXCLUDE its own output paths and PRINT the excluded
  count.** A silent exclusion is a second way to look at nothing and feel fine.
- **The synthetic-literal marker** (a) ships with its own controls including a NEG arm proving an
  unmarked real literal still fires, (b) PRINTS the count of literals it exempted on every run, and
  (c) is **never inferred from a literal's appearance** — it is an explicit token or it does not
  exist. A rising exempted-count is the only signal that someone is marking real constants to quiet
  the tool, and it cannot be a signal unless it is printed.

## 4. Deliberately not registered

Whether the c39/c40 published knob figures were *wrong*. That would be scored on my own instrument,
and c40 already established that the two figures were two questions rather than one error.

No proof claim. Standing sentence unchanged: we have no route to a proof.
