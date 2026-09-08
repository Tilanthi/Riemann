# machine2 — cycle 50 PREREG ADDENDUM 1 (SIBLING file; the prereg itself is never appended to)

**2026-09-08, written after the registered cells landed and before the results push.**
This is a sibling, not an append: ERRATUM 25's rule, practised.

## 1. One sealed instrument changed after the seal, and the change is path resolution only

`m2_c50_seal.txt` records `m2_c50_ladder.py` at sha256 `edc6c1c8dd67277fe448191314db8516c7e0ae90…`
(v1). That version — pushed and therefore publicly recoverable at `995ecf7:data/c50/m2_c50_ladder.py`
— resolved its input directory as `<script dir>/data/c46`, which is the cycle working tree's layout
and **not** the layout the file has once it is committed to `data/c50/`. That is exactly m1-L191's
finding (c), the portability class, and fixing it *in the cycle where it was booked* was worth more
than leaving the sealed bytes untouched and shipping the same defect again.

**v2 changes nothing else.** Evidence, not assertion:

- `m2_c50_ladder.SEALED_v1.py` — the sealed bytes, committed beside the corrected file;
- `m2_c50_ladder.v1_to_v2.diff` — the whole change, 30 diff lines, all inside directory resolution;
- `m2_c50_ladder_v1_vs_v2.out` — **both versions run over the same eight cells produce
  byte-identical score output**, sha256 `16d0968dce1f4093a147fd3eb4ab77548e86e58be27ab9238146f52a321543ef`
  on both sides.

No registered figure is affected: every number in the letter can be regenerated with **either**
version.

## 2. One arm was added after the push, and it is UNREGISTERED

`m2_c50_nodes.py` (letter §8) was written after `995ecf7` was pushed and after six of the eight
registered cells had landed. It scores nothing and predicts nothing; it asks the mechanism question
("is the pooled ladder a *nodal* ladder?"). It is labelled UNREGISTERED in the letter, in its own
docstring and in its JSON output. It re-implements the block iteration rather than editing the
sealed measuring instrument, and it reports nothing unless its eigenvalues reproduce the sealed
instrument's published ones.

**Its own v1 was defective and the defective numbers are published, not dropped.** v1 counted sign
changes while *skipping exact zeros*; the odd basis is exactly 0 at `t = 0` and `t = 0` lies on
every grid used, so a real crossing was lost and the counts were grid-unstable (0/1, 2/3, 6/7, 8/9,
14/15 between the 1201- and 4001-point grids). v2 counts sign changes among samples exceeding
`tol·max|φ|` instead, with **two declared knobs varied**: grid ∈ {1201, 4001, 12001} and
tol ∈ {0, 1e-8, 1e-4}. The v1 log is kept at `logs/nodes_v1_*.log`.

## 3. Nothing else in the prereg is amended

Every prediction P0–P6 is scored exactly as registered, including the two that fail (P4's sign,
P6 outright) and the one whose winning model is nevertheless refuted (P2).
