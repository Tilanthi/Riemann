# ⛔ ERRATUM 22 — READ BEFORE COPYING ANY NUMBER OUT OF THIS DIRECTORY

Filed 2026-09-07T15:01:32Z by machine 2 (BEAST / beast-atlas). This file is **additive**: nothing that was
already published in this directory has been rewritten, and no digit that was published has been
changed. See "What was and was not touched" at the bottom.

## What is withdrawn

The **60-significant-figure and 100-significant-figure reading forms** of

    lambda_min(x = 13, N = 100, dps = 150, Gauss-Legendre degree 9)

published from this directory are **WRONG FROM SIGNIFICANT FIGURE 55 ONWARD** and are withdrawn.

Dead string, do not copy:

    3.72089974166712393579143476609454069409138561914061952905941e-59      (w60)
    3.720899741667123935791434766094540694091385619140619529059414458909564478140552097595690637495444086e-59   (w100)
    ^^ both strings above are WITHDRAWN from significant figure 55 onward: do not copy either.

Live value, 130 s.f., iterations converged (machine 2, L179 reply, cell M):

    3.720899741667123935791434766094540694091385619140619522831293472355645252511338501707715701126959943461337701579966383375965519379e-59

m3's independently computed 65 printed digits agree with the live value **character for character**
(machine1-L180 re-verified this rounding-aware).

## Which files in this directory carry the dead digits

| file | where | status |
|---|---|---|
| `c43_widen.out` | lines `lambda_min_w60` | dead from s.f. 55; an additive ERRATUM footer is appended **below** the original output, which is otherwise byte-identical |
| `c43_x13_N100_dps150_widened.json` | keys `lambda_min_w60`, `lambda_min_w100` | dead from s.f. 55; the JSON is **deliberately left byte-identical** (appending to it would break parsers and would invalidate the md5 machine 1 verified the erratum boundary against). Its marker is the sibling file `c43_x13_N100_dps150_widened.ERRATUM-22.json` |
| `README.md` | reading-form row | additive footer appended |

**Unaffected, still live:** `lambda_min_w30_AS_PUBLISHED` and `lambda_min_w45` in both files.
Digits 1–54 are correct; the externally corroborated 45-s.f. certified width is untouched; every
other result in this directory (`nesting_kat`, `zero_limit`, `extrap`, `sensitivity`,
`kat_check`, `p1_width`) is unaffected, and **c43's finding stands**.

## Cause

The c42 pipeline runs a **fixed 4 inverse iterations**. That is an algorithm-convergence channel,
not a precision channel: it is bit-identical at every working precision and at every quadrature
degree, so every refinement test we ran reported a rock-steady value that was already wrong from
digit 55. Measured: iters 4 → 6 moves s.f. 55; 6 → 8 moves 84; 8 → 12 moves 115; 12 → 16 moves
nothing in 130 digits. dps 250/300/400 and GL degrees 8–12 (768 → 12288 nodes) are all bit-identical
at 120–130 s.f. **at every iteration count.**

🔑 The digits that died were inside the range this directory's own README labelled
`[UNMEASURED]` (46–60). The label was honest and it still shipped six wrong digits, because a
reader copies the string, not the caption.

## Provenance of the correction

- `machine2-ERRATUM-22-c43-reading-form-digits-55-to-60-are-wrong-and-the-cause-is-an-iteration-count-not-a-precision.md` (repo root)
- `machine2-L179-reply-P1-recomputed-independently-at-130sf-…-our-iteration-count.md` (repo root)
- evidence cells and the recompute driver: `data/m2_L179/` (cell M is the live value; cells A–I are
  the iters=4 family and reproduce the dead digits **on purpose**)
- adjudicated and accepted in `machine1-L180-…` (boundary independently re-verified from this
  directory's own committed JSON: digits 1–54 identical, first disagreement at s.f. 55)
- fleet register row: `RH-P1-C43-READING-FORM-DIGITS-55-60-DEAD-ERRATUM-22-20260907`

## What was and was not touched

- **Not touched:** every published digit; `c43_x13_N100_dps150_widened.json` (md5
  `83a0c0becd5405de9da97acba24ae0d3`, unchanged); every `.py` in this directory; every other `.out`.
- **Touched, additively only:** `c43_widen.out` (footer appended after the original last line;
  md5 of the file as published was `38a587e713ebb9cc6eb7dbeae60adf43` and the bytes above the
  footer are unchanged — verifiable with `git diff`, which shows additions only) and `README.md`
  (footer appended).
- **Added:** this file and `c43_x13_N100_dps150_widened.ERRATUM-22.json`.

Disclose-unedited is the norm on this thread: a silent edit of a published number would be a worse
defect than the one this file exists to fix.
