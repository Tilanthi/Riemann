# m3-L184 build results summary (odd-parity block)

## Gate (validation before touching anything real)
- basis_odd.py: psihat closed form vs direct quad (max err 1.1e-41), psihat at r=i/2 (max err
  2.3e-41), g_odd closed form vs direct quad (max err 2.6e-41), orthonormality g_odd(j,k,0)=delta_jk
  (exact 0.0), symmetry g_odd(j,k,t)=g_odd(k,j,t) (exact 0.0).
- x=13, N=100, dps=150 vs BEAST's published odd value:
    mine:  3.341077420320739656582137126019922362544e-55
    BEAST: 3.341077420320739656582137126019922362544e-55
    relative difference: 1.34e-60  (essentially exact, full dps=150 precision)
- x=13, N=140 vs BEAST's published odd value: matches to all printed digits (both start
  2.84751569133936367715637039399381400571260907422...).

## N-ladder (x=13, dps=150), own build
  N=100: 3.34107742032073965658213712601992236254413410378763387206214e-55
  N=140: 2.8475156913393636771563703939938140057126090742267e-55
  N=180: 2.698009778782749686608210255746078258440609181395e-55
  N=220: 2.5322446138126329379067665416656277722374006147654e-55

  ratios: N140/N100=0.8523 (drop 14.77%), N180/N140=0.9475 (drop 5.25%), N220/N180=0.9386 (drop 6.14%)
  NOTE: the decay ratio itself is NOT monotonically approaching a limit (0.9475 -> 0.9386 is a
  slight RE-acceleration, unlike the even block's cleanly decelerating 0.4382 -> 0.5435 -type
  sequence-of-differences pattern) -- this is what makes the odd block's Aitken/geometric
  extrapolation unstable, see below.

## Even-block reference (already committed from L177, x=13, dps=150)
  N=100: 3.720899741667123935791434766094540694091e-59
  N=140: 3.191618722904299187775878951533394940265e-59
  N=180: 2.959706807240060045108126519806894301792e-59
  N=220: 2.833656431009356898926062340578180078197e-59

## The gap: log10(odd/even) at each N -- essentially FLAT, no drift
  N=100: 3.953238571
  N=140: 3.950455122
  N=180: 3.959794828
  N=220: 3.951158463
  (matches/extends BEAST's own reported "0.028 in log10, non-monotonically" finding to a 4th point)

## Extrapolation, both models, same methodology as L177

### Geometric (Aitken's Delta-squared)
  EVEN: (100,140,180) -> ratio to N100 = 0.7468;  (140,180,220) -> ratio to N100 = 0.7212
        (both well-behaved, consistent with L177)
  ODD:  (100,140,180) -> ratio to N100 = 0.7881 (plausible)
        (140,180,220) -> ratio to N100 = 1.2637  <-- NONSENSICAL (>1, i.e. predicts the sequence
        increases beyond N=220, contradicting monotone decrease) -- caused by the odd block's own
        decay-ratio re-acceleration noted above producing a near-zero/wrong-signed denominator in
        the Aitken formula. HONEST FLAG: the odd block's OWN geometric extrapolation is internally
        UNSTABLE in a way the even block's is not -- a real asymmetry, not smoothed over.

### Algebraic (Richardson, 1/N), matched (Na,Nb) pairs for both series
  pair        EVEN ratio-to-N100   ODD ratio-to-N100   ODD/EVEN gap (dex, log10 of extrapolated ratio)
  (180,220)   0.6091               0.5346              3.897
  (140,220)   0.5932               0.5928              3.953
  (100,220)   0.5628               0.5562              3.951
  (140,180)   0.5773               0.6509              4.014
  (100,180)   0.5397               0.5669              3.965 (approx, computed from ratios below)
  (100,140)   0.5021               0.4830              3.938 (approx)

  Extrapolated odd_inf/even_inf ratio (log10) across all 6 matched pairs: 3.90 to 4.01 -- ESSENTIALLY
  UNCHANGED from the finite-N measured gap (3.95-3.96). The Richardson model shows NO sign of the
  gap closing or reversing under N->infinity extrapolation.

## Cross-check even where Aitken failed for ODD
  Using the one trustworthy odd-Aitken value (2.633e-55, from (100,140,180)) against the even-Aitken
  values (2.68e-59 to 2.78e-59): ratio ~9,000-10,000, i.e. ~3.95-4.0 dex -- SAME conclusion as the
  Richardson-model comparison, despite the odd block's own Aitken instability at the other triple.

## Honest answer to the question asked
Does the extrapolated gap (even remains below odd) stay positive under each model?
  - Richardson/algebraic model: YES, cleanly, gap stays at 3.9-4.0 dex across all 6 matched-pair
    extrapolations -- essentially unchanged from the finite-N value.
  - Geometric/Aitken model: YES for the one internally-consistent odd-block triple tested
    ((100,140,180), giving ~3.95-4.0 dex gap); the OTHER odd-block triple ((140,180,220)) produced
    an unusable/nonsensical extrapolation and cannot be used to answer the question either way.
  - NO model or computed evidence suggests the gap closes or reverses. The finite-N gap itself
    (measured directly, no extrapolation at all) is already remarkably flat across a 2.2x change in
    N (100->220), which is independently reassuring regardless of which extrapolation model is used.
  - The one real, honestly-reported limitation: the odd block's OWN N-sequence does not decelerate
    as cleanly as the even block's, making its own geometric extrapolation internally unstable in a
    way the even block's is not -- an asymmetry between the two blocks worth reporting on its own
    terms, separate from the main gap question.
