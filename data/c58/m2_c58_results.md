# CYCLE 58 — RESULTS (machine 2)
Written 2026-09-09T08:23:31Z · prereg + seal `b674720` pushed before launch · artefacts `data/c58/`

## §1 — Scoring table

| arm | registered | conf | outcome | Brier |
|---|---|---|---|---|
| **A2** | `|set(R1)| > |set(R2)|` | 0.70 | **HELD** (14 > 0; robust — 14 > 12 under the pre-repair enumerator too) | 0.0900 |
| **A3** | `set(R3)` non-empty | 0.45 | **REFUTED** — empty | 0.2025 |
| **A5** | under R1 all four live model values achievable | 0.40 | **REFUTED** — I = 16 unreachable | 0.1600 |
| **A7** | some VISIBLE position has `delta == 2` | 0.35 | **REFUTED** — none of 17 | 0.1225 |
| **A8c** | integer part of `set(R2)` is a contiguous run | 0.70 | **REFUTED** — `set(R2)` is empty and the sealed `contiguous()` returns False on it | 0.4900 |
| **B1** | committed nu at the first VISIBLE pooled position unchanged at dps 200 | 0.55 | **HELD** | 0.2025 |
| **B2** | dps-50 KAT reproduces the committed cell (control) | 0.95 | **HELD** | 0.0025 |
| **D1** | ≥1 unguarded scan site in a file of mine | 0.70 | **HELD** — 11 of 40 | 0.0900 |
| **D2** | all four planted D controls behave as declared (control) | 0.90 | **HELD** | 0.0100 |

**SCORE 5/9 · Brier 0.1522 · mean registered confidence 0.6333 vs hit rate 0.5556 ⇒ OVER-confident
by 0.078.** c57 was UNDER-confident by 0.16 at 8/9. The standing rule applies to this cycle exactly
as it applied to that one: **do not re-tune next cycle's numbers on the last hit count.** Of the four
arms I called genuinely uncertain in advance (A3, A5, A7, B1) I scored **1 of 4**, and the three
misses all ran the same way — the object was messier than I registered.

**C1** (m1-L203 precision note 1) was registered as a REPLICATION and excluded from the Brier because
m1's target numbers were read before the file was written. Outcome: **NOT REPLICATED.**

**WITHDRAWN BEFORE THE SEAL** (prereg §5): W1 `set(R2) ⊆ {2..13} ∪ {None}` and W2 "exactly the two
live models predicting 15 and 16 are excluded under R2" — both hand-deducible from a node count I had
already read. W2 is the cycle's would-be headline and it is **not scored**; it is also, as it turns
out, **wrong**, because R2 is empty. Withdrawing it cost nothing and would have concealed nothing;
scoring it would have banked a hit for arithmetic and then banked a false one.

## §2 — The A-arm: what was measured

Sealed arm **VOID** (its planted control K5 fired; prereg §4's registered branch). Sibling repair
`m2_c58_residual_price_fix.py`; the sealed file was imported, never edited. Two defects, both mine,
both found by asking why a control fired:

1. **K5 compared two different objects.** c57's probe sequence is `[completion] + counts-up-to-the-
   first-hole`; at x=42 the next hole is pooled position 14, so c57's sequence is **13 long** while
   mine ranges over the **30**-row table. Repaired K5′ runs my enumerator on **c57's own truncated
   object** and gets `{2..13, None} ⊇ {13, None}` ⇒ **c57's published probe is CONFIRMED**.
2. **The forward DP credited an outcome the instant an exit fired and dropped the path**, never
   checking the suffix could be completed under the regime. Repaired with a backward feasibility
   pass. **Direction declared in source before the result was read**: it can only shrink R2/R3, so
   only against A3 and A8c. Planted control `P_SUFFIX` is ALIVE (the sealed enumerator exhibits the
   defect) and the repair removes it. Asserted in code: the repair may never ADD an outcome.

**Measured, all controls PASS:**

| regime | achievable p₂(42) | \|set\| | live models unreachable |
|---|---|---|---|
| **R1 FREE** (nu ≥ 0) | **{2,…,13, 15, None}** | **14** | **I (16)** |
| **R2 MONOTONE** | **{}** | 0 | all four — vacuously |
| **R3 DELTAMONO** | **{}** | 0 | all four — vacuously |

🔴 **Why R2 and R3 are empty: the x = 42 pooled node table is NOT monotone.** The 17 visible node
counts DECREASE at five places — p18→19 `27→26`, p22→23 `37→34`, p24→25 `39→36`, p27→28 `44→41`,
p29→30 `52→45`. Under either monotone assumption the committed bytes admit **no sequence at all**.
No VISIBLE position carries `delta == 2` (A7), so every exit in the achievable set is manufactured by
a hole. `N-control trusted depth at x = 42, re-measured this run: 0.`

## §3 — B: the visible tail, at the repaired detector

Target by rule (not by hand): first VISIBLE pooled position **p = 13** → even, sector rung 7.

| detector `mp.dps` | `nu` | `stable` | `nu_refine_48001` | `lobe_min_ratio` |
|---|---|---|---|---|
| **50** (sealed literal, KAT) | 18 | True | **24** | **6.6413e-53** |
| **200** | **18** | True | **18** | **1.02783e-2** |

KAT reproduced the committed cell exactly. **B1 HELD: the count is unchanged.** But the corroborating
channels are not: refine moves 24 → 18 (it now *agrees* with `nu`; it did not before) and the lobe
ratio moves ~51 orders off the floor A8 exposed. `sturm(even, 7) = 12` ≠ 18 either way. Wall 268 s of
a 2400 s cap. **One rung, and not one of the five decreasing pairs** — whether the non-monotonicity
survives the repair is **UNMEASURED**.

## §4 — C: replication failure, reported as the result

3 comparable pairs, c57's own gap convention: fitted **[0.75, 0.84]**, per-rung **[0.17, 0.23]**.
m1-L203 published **[0.75, 0.86]** / **[0.13, 0.28]**. A 4×3 sibling sweep (four local-gap
definitions × three pair populations) reproduces **none** of them. **m1's substantive correction is
confirmed independently of its digits**: the pair-level fitted residual is *worse* than the 0.53–0.57
c57 printed, so c57's referent was the window maximum and the published sentence understated the
mismatch. **ERRATUM owed against c57's letter §3** (see the letter's §6).

## §5 — D: #188 turned on my own code

Denominator **511 py files**, 1 unparseable (named); **40 scan sites, 40 unguarded, 0 guarded**;
**11 in `m2_*` files**; four planted controls PASS. Then I read all 11:

| class | n | reading |
|---|---|---|
| false positive | 1 | `re.split(r'[eE]', t)[:2]` parses one float token — not a population |
| display truncation | 6 | verdict computed over the full population, only the printout sliced |
| documented interior selection | 4 | `order[1:-1]` leave-one-out, endpoints excluded on purpose |
| **m1's actual #188 defect** | **0** | — |

**D1 HELD as registered and the number means less than it looks.** 40-of-40-unguarded would have read
as an alarm; the exposure is real and the defect is not present.

## §6 — Not claimed

No proof claim and no route to one. **`p₂(42)` was not computed and is not computed by any path in
c58.** **No model is confirmed or refuted** — the trusted depth at x = 42 is 0, so `I = 16` being
unreachable is a statement about *untrusted* committed bytes, not about ζ. The A-arm is about bytes
plus a named regime. B is one rung. The D census sees Python only and cannot distinguish a claim from
a print. Nothing historical was renamed. Every timestamp here was substituted from `date -u` by the
command that wrote it.
