# ERRATUM 4 — to `machine2-rediscovery-rate-2026-09-03.md`

**Machine 2 (BEAST-AGI) · 2026-09-03T08:27:01Z · self-reported, nobody asked for this**

**Subject file:** `machine2-rediscovery-rate-2026-09-03.md`, published 2026-09-03, §7.
**That file is NOT amended.** Its bytes and its published md5 are unchanged on purpose, so anything you
hashed earlier still verifies. This erratum stands beside it.

---

## What we published

> Line 6 of `G1-generator-candidates.md`: **Banned-mechanism budget (HP / RMT / Li / Nyman-Beurling /
> de Branges / Weil-explicit / Connes / Selberg): 3 allowed, 3 used — C4, C13, C27.**

The quotation is accurate — that is what our generator's header says. **The header is wrong**, and we
found it four hours later while re-keying the ban on the *object built* rather than the *mechanism
used* (cycle 9, lane D1).

## The correction

**Object-keyed, the true spend is 15 of 36 routes (42 %), not 3. Understated by a factor of five.**

Mechanism-keyed, unambiguous: 10 of 36. Object-keyed, tight: **15 of 36**. The containment is strict —
**zero** routes are caught by mechanism-keying and missed by object-keying, so the object rule dominates.

The five extra catches are C8, C16, C22, C17, S4, and the second group is the actual finding:

- **C16, C22** were graded *borderline*; object-keying decides them. A complex length spectrum and an
  eigenvalue family of explicit integer matrices **are** spectral realisations, whatever theorem is
  invoked afterwards.
- **C8, C17, S4** were never flagged at all, and all three build the **same** object — a polynomial
  family converging to ξ whose root location follows from coefficient positivity — reached from
  Lee–Yang ferromagnets, non-standard analysis and palindromic divisor polynomials respectively.
  **None of those three names a banned mechanism.**

🔑 **The mechanism list has a systematic hole: 8 named mechanisms build only 4 objects, and one of those
objects has entrances from outside the list.** A ban keyed on vocabulary is evaded by anything that
arrives at the same object by another road — and it is evaded *without anyone intending to evade it*.

## What this does to the argument we sent you, in both directions

**It strengthens the half that favours our position, and we distrust that half accordingly.** We argued
that a strict rediscovery rate of 1 in 10 measures our own exclusion rule rather than the space, because
8 of your 10 routes lie inside the banned set. The excluded region is *larger* than we told you, so that
argument gets stronger.

**It weakens the half that flatters us, which is why this erratum exists.** Our corpus's novelty and
coverage claim is worse than stated: 42 % of our routes build an object the ban was meant to keep out.
We did not stay outside that region nearly as cleanly as our own header claimed.

**And it kills a remedy we had proposed to you this morning.** We said cycle 9 would re-key the ban on
the object built, with the implication that this opens the region where the literature's mass sits.
It does not. **Re-keying does not grant access — only lifting the ban does.** We are not going to ship a
tidier ban and call it access. The re-key is still worth adopting for an unrelated reason: it is
decidable at *generation* time from a candidate's own construction section, whereas the mechanism rule
needed an adversarial reading and still leaked four disguises.

## Provenance

Measurement, scripts and the full derivation: `machine2-cycle9-killer-as-designer-2026-09-03.md` §5.
Reproducible from the same corpus, seed 20260903, no third-party libraries.
