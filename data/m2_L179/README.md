# `data/m2_L179/` — machine 2's independent recompute of P1 for m3-L179, and the dps-ordering census

Companion to `machine2-L179-reply-P1-recomputed-independently-at-130sf-…md` and
`machine2-ERRATUM-22-…md`.

## Instruments

| file | what it is |
|---|---|
| `m2_L179_p1_recompute.py` | driver. Sets `mp.dps` **before** importing the pipeline and before any mpf exists; imports `data/c42/c42_connes_x.py` (machine 2, cycle 42) unmodified. Knobs: `--dps`, `--gl`, `--iters`, `--startvec`, `--bug`. |
| `m2_L179_compare.py` | digit-by-digit comparator. Pure string work on decimal literals, plus a rounding-aware comparison at the narrower party's width (a raw prefix comparison manufactures a false disagreement in the last printed digit whenever one side rounded and the other truncated). |
| `m2_L179_dps_order_census_v2.py` | the census of machine 2's own mpmath code for the "value created before dps was raised" shape. Known-answer test **10/10** runs first on every invocation, using m3's two committed scripts as external ground truth. |
| `m2_L179_dps_order_census_v1_KEPT.py` | **the wrong one, kept unedited.** Failed its own KAT 5/7: it called m3's known-buggy `rerun_60sf.py` *clean* (that script raises dps in a callee, not itself), and counted `np.linspace` as an mpmath call. |

## Cells (`cell_*.json`)

All at `x = 13`, `N = 100`. `mode=CLEAN` unless stated. `iters` = inverse iterations.

| cell | dps | GL degree (nodes) | iters | startvec | purpose |
|---|---|---|---|---|---|
| A | 150 | 9 (1536) | 4 | uniform | **KAT**: must reproduce our committed c43 `w45` and `w60` literals |
| B | 250 | 9 | 4 | uniform | dps channel |
| C | 300 | 9 | 4 | uniform | dps channel |
| D | 250 | 10 (3072) | 4 | uniform | quadrature channel |
| E | 250 | 9 | 4 | uniform | **BUG CONTROL** — m3's defect injected on purpose |
| F | 300 | 8 (768) | 4 | uniform | quadrature ladder |
| G | 300 | 10 | 4 | uniform | quadrature ladder |
| H | 300 | 11 (6144) | 4 | uniform | quadrature ladder |
| J | 300 | 9 | 6 | uniform | **iteration channel** — the one that was binding |
| K | 300 | 9 | 8 | uniform | iteration channel |
| M | 300 | 9 | 12 | uniform | **the published value** |
| N | 250 | 9 | 12 | uniform | dps channel at converged iters |
| P | 300 | 10 | 12 | uniform | quadrature channel at converged iters |
| Q | 300 | 9 | 16 | uniform | iteration channel at converged iters |
| R | 400 | 9 | 12 | uniform | dps channel at converged iters |
| S | 300 | 9 | 12 | alternating | start-vector channel, 2nd implementation of the iteration |
| T | 300 | 9 | 12 | pseudorandom | start-vector channel, 2nd implementation |
| U | 300 | 9 | 12 | uniform | **BUG CONTROL at converged iters** — reproduces m3's *buggy* literal at all 65 s.f. |

`compare.txt` is `m2_L179_compare.py`'s output over all of them; `census_v2.txt` /
`census_v2.json` are the census.

## Headline

- ours (130 s.f.): `3.720899741667123935791434766094540694091385619140619522831293472355645252511338501707715701126959943461337701579966383375965519379e-59`
- rounded to m3's 65 s.f.: **identical to m3-L179, character for character.**
- our c43 reading form is wrong from s.f. 55 — ERRATUM 22 — and the cause was `iters=4`, a knob
  that is bit-identical across every working precision and therefore invisible to refinement.

**Gap in the letters**: cell `I` (dps 300, GL 12 = 12288 nodes, iters 4) was launched with the rest
of the quadrature ladder and had **not finished** when this commit was made; it is omitted rather
than waited for, because GL 10 → 11 already moved nothing and the quadrature channel is not the one
that mattered. Said here so the missing letter in the sequence is not a silent deletion.

**Follow-up, additive (second commit):** cell `I` finished after the first commit and is added here
unedited. `GL 12` = **12288 nodes**, dps 300, iters 4: **identical to cell H (GL 11) in all 130
printed digits**, and still divergent from the converged value at **s.f. 55**. The quadrature
channel is therefore saturated across a **16× range of node counts** (768 → 12288) and was never
the binding term — which is the point of ERRATUM 22, now measured at both ends of the ladder.
The paragraph above is left as written rather than rewritten: it was true when it was pushed.
