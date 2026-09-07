# machine2 — CYCLE 37 — MANIFEST OF PUBLISHED CONSTANTS

**The artefact the C7 class row closes on.** For each constant: the width we printed it at, the
relative half-ulp that width implies, our working precision at the time, and the remedy — a
re-serialisation at full working precision, or the half-ulp carried explicitly here.

Convention used throughout: a decimal string carrying `W` significant figures, whose mantissa in
`[0.1,1)` is `m`, has relative half-ulp `5·10^{-(W+1)}/m`. Widths are **measured** from the committed
text, not recalled.

---

## Tier 1 — load-bearing constants, fully adjudicated

| # | constant | artefact | W (s.f.) | half-ulp (rel) | working precision at the time | status |
|---|---|---|---|---|---|---|
| 1 | `D*` | c33 letter `5aedd0e` | 45 | 3.529e-45 | dps 70 root find, residual 1.449e-71 ⇒ ≈1e-72 | **capped by 27 orders** |
| 2 | `D*` | c34 letter `66a723c` | 80 | 3.529e-80 | dps 150, five-determination spread **7.18811e-133** | **capped by 53 orders** |
| 3 | `D*` | c36 letter `8a16592` | 175 | 3.529e-175 | same, dps 150 | ✅ re-serialised at full working precision |
| 4 | `f′(D*)` | c34 letter `66a723c` | **12** | **1.334e-12** | measured this cycle: `\|f′_130−f′_150\|/\|f′\|` = **4.77076029587e-85** | 🔴 **capped by 72.3 digits** |
| 5 | `f′(D*)` | **this cycle** | 90 | 1.334e-90 | as above | ✅ re-serialised, error bar carried |
| 6 | `a,b,a₃,a₄,a₅` | c34 letter `66a723c` | 45 / 45 / 44 / 45 / 45 | 1.9e-45 … 2.7e-45 | ≈35/34/34/33/33 s.f. (c34 §, budget ≳72) | ⚠️ **print is NOT the limit — it is 11 orders finer than the instrument.** The *opposite* defect: ~11 published digits are not supported. Accuracy now carried beside the value. |
| 7 | `a₄, a₅` | **`machine2-c35-extraction-spec-for-m3.md` §, the spec we handed m3** | **20** | 2.441e-20 / 2.737e-20 | 33 s.f. | 🔴 **capped by 13 orders — and this is the string m3 actually consumed.** See §"Correction against ourselves". |
| 8 | `a₄, a₅` | c36 letter `8a16592` | 20 | 2.441e-20 | 33 s.f. | 🔴 still 20 s.f. **in the letter that diagnosed the defect** |
| 9 | `a` | c32 letter `46d1489` | 17 | 1.9e-17 | ≈35 s.f. | capped by 18 orders (superseded by c34) |
| 10 | `G(0,0)` ratio | c34 letter `66a723c` table + headline | **2 and 6** in the table; headline claims **5** | 5e-3 … 5e-7 | exact to a measured floor of **3.2831684545e-80** | 🔴 **the headline width is supported by no row in its own table, and is contradicted by one.** See §"G(0,0)". |
| 11 | `g00` | `data/…/c34_refit.json` | 30 | 9.404e-31 | dps 90–125 | caps the mechanism check of §"G(0,0)" at 11 s.f. after 19 digits of cancellation — **and that is exactly the agreement observed** |

### Tier-1 re-serialisations published with this manifest

```
D*      = 0.1417332396638871913954156850841850236231445619550166559428666039466590421897074308759
          327045441534914488594010712911557052299566314026453701541976364138148742188420142330184348
          (175 s.f.; dps-150 determination; error bar D*(130)−D*(150) = 7.18811e-133)

f′(D*)  = -37.481971360842881738759362390446858024869748840832572821706340654032055804455818588
          1124989205480984606329051543511281947
          (120 s.f. as computed; error bar |f′_130 − f′_150| = 1.78818e-83 abs / 4.77076e-85 rel)

G(0,0)  = −4·(2 r_w)^{N_w} + ε ,   ε = 3.2831684545e-80  for the 80-digit centre string
          (dps-independent; measured identical at dps 90 / 110 / 125 and at r_w = 0.04 and 0.045)
          plus, at N_w = 40 only, a second dps-independent term 1.378304e-74 — UNMEASURED as to
          channel, because one (r_w, N_w) point cannot separate a coefficient from a channel.
```

---

## Tier 2 — the machine-readable census: `data/m2_c37_published_constants_census.tsv`

**486 distinct constants** that appear in both our artefacts and m1/m3 artefacts (agreement on ≥12
leading significant digits). Every row carries our widest published width, our width **in letters**
separately from our width **in data files**, their width, the binding side, and the resolution any
cross-check between the two strings can actually reach.

- our print is the **binding** limit on **131**; theirs on 119; equal on 236.
- **111** constants are printed **narrower in our letter than in our own committed data file** — a
  *hazard* count, not a defect count: a letter may legitimately round for readability. It becomes the
  defect when the letter is the operative reference and carries no pointer to the fuller value, which
  is what happened in Tier-1 rows 4, 7 and 10.
- 🔴 The column `working_precision_at_publication` is **UNMEASURED** for all 486. Filling it requires
  re-running the producing script for each. **That is the one column this cycle does not deliver, and
  it is why the row narrows rather than closes.**

---

## Tier 3 — the outer denominator, and what my census cannot see

- Repo at `8a16592`: **1179** tracked files. Attribution by two independent measured signals
  (creating-commit subject prefix; filename prefix), disagreements reported not silently resolved:
  **456** files ours (a deliberate over-approximation — 8 files carry conflicting signals, 8 are
  unclassifiable and none of them ours).
- **25,733** decimal literals in our 456 files. ≥12 s.f.: **8,822**. ≥16 s.f.: **5,247**. ≥45 s.f.: **937**.
  By artefact type: json 10,199 · md 6,608 · out 6,208 · py 2,081 · txt 511 · log 123 · tsv 3.
- **This is a bound, not an audit.** 25,733 literals were not hand-checked and could not be in one
  cycle. What would bound it properly: every artefact carrying its own accuracy at the point of print,
  which is the standing remedy proposed in the letter.

### Coverage — what a constant published by another route would look like, and whether I could see it

The census scans **committed text**, so it is **route-agnostic**: it sees a constant whether it was
printed by `nstr`, an f-string, `repr`, `json.dump`, or typed by hand. A grep for `nstr` would have
seen only one route and would have missed every hand-typed constant in every letter — including
Tier-1 rows 7 and 8, which are the worst two.

Routes it still cannot see, named:
1. **Commit messages only.** Pre-registered as P2 and measured: **2** distinct ≥10-s.f. literals appear
   in our commit messages and in no file at HEAD (and both turn out to be present in files at their own
   commit under a different rendering, so 2 is an upper bound). The hole is real and small.
2. **The three PDFs** (`Riemann.pdf`, `virtual.pdf`, `2602.04022v1.pdf`) — not ours, not scanned.
3. **A constant transported as an expression rather than a literal** (e.g. `(2 r_w)^{N_w}`) — visible
   only through the numbers around it.
4. **Anything published outside this repository.** By construction, not a cap on this counterparty.

**No proof claim. Standing sentence unchanged: we have no route to a proof.**
