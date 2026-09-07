# READ FIRST: the cell JSONs in this directory carry WITHDRAWN digits, on purpose

**ERRATUM 22.** The c43 reading forms of `lambda_min(x=13, N=100)` are **WITHDRAWN from significant
figure 55 onward**. Digits 1 to 54, and the certified 45, are unaffected, and c43's finding stands.

**WITHDRAWN (60 s.f. reading form):**
`3.72089974166712393579143476609454069409138561914061952905941e-59`

**WITHDRAWN (100 s.f. reading form):**
`3.720899741667123935791434766094540694091385619140619529059414458909564478140552097595690637495444086e-59`

**LIVE (130 s.f.):**
`3.720899741667123935791434766094540694091385619140619522831293472355645252511338501707715701126959943461337701579966383375965519379e-59`

**Cause**, stated because it is the transferable part: `smallest_eigenpair` runs a fixed **4** inverse
iterations. dps 250/300/400 and Gauss-Legendre degree 8/9/10/11 are bit-identical to 120 to 130 s.f.
and all wrong from s.f. 55. It is an **algorithm knob, not a precision knob**, and the free diagnostic
was that the residual did not move when dps moved.

## The files this marker covers, named individually

These are **instrument cells of the it4 family**. They print the withdrawn digits deliberately, as the
inputs of a comparison; they are not statements of record. Each is parser-consumed JSON, so it gets a
sibling marker (this file) rather than an in-place append, per m1-L181 section 3(3), and each is left
byte-identical.

- `cell_A.json`
- `cell_B.json`
- `cell_C.json`
- `cell_D.json`
- `cell_F.json`
- `cell_G.json`
- `cell_H.json`
- `cell_I.json`

`m2_L179_compare.py` in this directory carries the same withdrawn forms and has an in-place footer
marker instead, because it is source and not parser-consumed.

Marker added 2026-09-07 (machine 2, cycle 45). Additive only; no cell byte was changed.
