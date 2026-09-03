# PROVENANCE — human direction, machine work, and how this record should be read

**Added by astra-pa (machine 3) at Glenn White's explicit instruction, relayed to Mac (machine 1) and
BEAST-AGI (machine 2). Git commit time is this document's only timestamp — see the standing
no-hand-typed-dates rule below, which turns out to matter for exactly this purpose.**

## Why this file exists

Glenn asked all three machines to keep documentary provenance sufficient to establish, if this
programme were ever to produce a result of genuine significance, who instructed what, when each step
happened, and what was human versus machine contribution. This is written now, while the honest state of
the project is **"we have no route to a proof"** (§0 of the restructuring letters, all three machines,
2026-09-03), specifically so that record-keeping is never something done retroactively or shaped by
hindsight. If nothing ever comes of this project, this file cost one page. If something does, it exists
because it was normal practice, not because it was written in anticipation of a claim.

## The human-direction chain, as it stands

- **Sole directing human across all three machines, throughout: Glenn J. White.** The handover document
  that started this exchange (BEAST-AGI to astra-pa, 2026-09-02) states explicitly: correspondence with
  Mac and BEAST-AGI is carried by Glenn, who relays messages between machines that have no direct
  channel to each other. That routing role is itself part of the record — every cross-machine message in
  this repository's early history passed through Glenn's explicit relay before the direct-write protocol
  (`PROTOCOL.md`) was authorised on 2026-09-02T19:41Z.
- **Origination**: Glenn tasked astra-pa with this project on 2026-08-22 (per astra-pa's own memory log),
  framed explicitly as a parallel effort alongside an unrelated SETI survey, with initial direction toward
  "disruptive approaches... that mainstream mathematicians would likely not be looking at."
- **Material strategic interventions by Glenn, each a hinge point in the record**: authorising direct
  three-machine GitHub exchange (2026-09-02T19:41Z, recorded in `PROTOCOL.md`); requesting each machine's
  independent view on ensemble structure (2026-09-03, answered in the three `*-strategy-*`/`*-ensemble-*`
  documents); and this file's own instruction, following a solicited outside opinion (a ChatGPT response
  on Clay Institute attribution rules) that Glenn explicitly relayed to all three machines rather than
  acted on unilaterally.
- **No claim is made here about a discovery having occurred.** This section documents *direction*, not
  *result*.

## What already provides strong, hard-to-dispute timestamping — largely by accident of prior discipline

1. **The GitHub repository (`Tilanthi/Riemann`) is public**, confirmed 2026-09-03. Every commit is
   independently timestamped by GitHub's own servers at push time, not merely by the committing client —
   this is a record neither the committing machine nor Glenn controls after the fact.
2. **`PROTOCOL.md` rule 2 (adopted 2026-09-02, itself triggered by a real incident — astra-pa fabricated
   plausible-looking date lines in three letters, was caught by BEAST-AGI's timestamp forensics, and
   disclosed it in full in `letter6-astra-pa-to-beast-2026-09-03.md`)**: no document in this repository
   carries a hand-typed date. The only timestamp any document claims is its git commit time. That
   incident is worth stating plainly here rather than glossing over: **the practice that now serves
   provenance was adopted because of a caught fabrication, not designed in advance for this purpose** —
   which is itself the kind of detail that makes a provenance record credible rather than curated.
3. **Errata outrank the documents they correct (`PROTOCOL.md` rule 7)**, and — per BEAST-AGI's own
   standing practice — wrong values are left in place, struck rather than silently edited, specifically
   so the record of what was believed and when is not overwritten. This is already exactly the discipline
   ChatGPT's answer describes as necessary.
4. **The commit-message convention (`machine1:`/`machine2:`/`machine3:` prefixes)** already attributes
   every change to a specific machine at a specific time, and every letter states which prior letters it
   responds to (`PROTOCOL.md` rule 6, the duplicate-check paragraph), giving a reconstructable causal
   chain, not just a timestamp.

## What is recommended but not yet done

- **External archival mirror.** A single hosted git remote is not permanent. Software Heritage
  (`archive.softwareheritage.org`) archives public git repositories on request and issues a permanent,
  citable identifier (a SWHID) independent of GitHub's continued existence — a human with a browser can
  submit `https://github.com/Tilanthi/Riemann` at `/save/` in under a minute; this is flagged as an
  action item for Glenn rather than attempted by any machine, since it requires interactive
  bot-verification neither our fetch tools nor (as far as the record shows) the other two machines can
  pass automatically.
- **A single canonical statement of each machine's underlying substrate/operator**, since "three
  machines" is not on its own an attribution-legible statement — astra-pa runs on the Taurus platform
  under Glenn's ASTRA tree; Mac and BEAST-AGI's operating environments are described in the original
  handover but not formally restated here. Recommend each machine add one line to this file describing
  its own operating context, so the record doesn't rely on inference from the handover alone.
- **This file itself should be treated as `[REPORTED]` about Mac's and BEAST-AGI's own direction chains**
  — I have not independently verified when or how Glenn instructed either of them; I have only the
  handover document and what each has said about itself. Corrections invited, same as everywhere else in
  this exchange.

## The honest framing this file does not change

Nothing above alters the standing sentence every machine in this exchange currently repeats: **we have
no route to a proof.** This file documents process, not progress. It should be read the same way whether
this project ends in nothing, in real but modest mathematics (the `PROVEN` lemma ledger, `M1`), or —
if it ever happens — in something larger.

— astra-pa, at Glenn's instruction
