# der-route v1/v2 diagnosis — probe log (committed for L174 §1 / register #138)

Seven probe families, run 2026-09-06 around the v1/v2 failure. The v1 run's FULL
stdout is committed verbatim as `machine1_der_route_a_b_a3_full.stdout`
(sha256 `32ae2a06…`; the session's original background-task capture; the
shorter `machine1_der_route_a_b_a3.out` in this directory is the partial file
first captured — final constants and control summary only). Nothing here is
scored; these are channel probes. Scripts and raw outputs committed alongside.

**CORRECTION (same day, before L174 shipped).** Families 0–5 were written
under the interim diagnosis "a process-local corruption, never reproduced."
That claim is FALSE. v2 — the two-bug-fixed rerun — reproduced v1's corrupted
digits exactly (rescaled by the FIX-1 factors: a = v1's digit string × 10⁹,
b × 10¹⁸, a₃ × 10²⁷), deterministically, in a separate process. The root
cause is a code defect present in v1 AND v2, located by hand and receipted as
**family 7** below: fd_weights' Vandermonde system solved in the wrong
orientation. Families 1–5 stayed green because they probed the evaluator and
the circle channel — every stage EXCEPT fd_weights. The "two diagnostic
tells" of family 0 remain valid as signatures; their cause is now known.

## 0. The v1 run itself — `machine1_der_route_a_b_a3_full.stdout`

The complete record: controls green at the top (evenness 2.38129e-17, fold
residual -1.87618e-35), stencil timings (252 s/node at dps 60, no guard),
max|Im g| = 7.24507e-64, and THE CORRUPTED CHANNEL VALUES:

    g10 = 1.7369932158316149e-9 + 9.08409e-72j    (truth: -18.816779288625)
    g01 = -1.7778641423755601e-9 - 1.21281e-74j   (truth: -49.7801925391;
         correctly-scaled for v1's own missing /HE division: -4.978e-8)

Two diagnostic tells now receipted: (i) the two channels are wrong at
DIFFERENT ratios (g10 off by ~1e10 and sign; g01 off by ~28x from even its
own bug's predicted scale) — not one global rescaling; (ii) the corrupted
imaginary parts (9.1e-72, 1.2e-74) sit 12+ orders BELOW the dps-60 working
floor, while every healthy channel's imag noise sits AT the floor (1e-59 at
dps 60, 1e-69 at dps 70 — family 3 below). Sub-floor imaginary parts are
themselves a corruption signature. Also visible: the closing-control bug's
own print ("no (eps,u) pairs found in heat86b JSON -- skipped") and the
series-solve residual ~1.77786e-10, equal to |g01|/10 — the "solution" was
solving a corrupted polynomial.

## 1. The D1–D5 diagnostic — `code/machine1_der_route_diag.py` -> `machine1_der_route_diag.out`

Chronologically first. Establishes the truth values directly from h:
c2 from real-axis even differences at two hh (the Richardson inputs),
dh/de, the ladder anchor (h at m2's published rung u, e=1e-4 ~ 1.7e-42 ~ 0:
e-convention and object confirmed), and the implied a from their ratio.
Note: D5's printed sign is an informational slip in the diag script
(-(dh/de)/c2 = -a, magnitude only); the correct quick form is
a = g01/g10 = +2.645519 via the Richardson c2 (2.645482 via the uncorrected
hh=1e-3 c2). v2's series-solve (A = -g01/g10, a = -A) carries the right sign.

```
dps=50 zcut=149.668
D1 h(0.05, 0) = -0.060921187 + 0.0 i
D1 h((0.0 + 0.05j), 0) = 0.045318448 + 0.0117047 i
D1 h(0.01, 0) = -0.0019797878 + 0.0 i
D2 hh=0.001: h+ -1.8912311e-5 h- -1.8721806e-5 -> c2 = (-18.8170584709 + 0.0j)
D2 hh=0.01: h+ -0.0019797878 h- -0.0017891544 -> c2 = (-18.8447112093 + 0.0j)
D3 dh/de(0,0) = -49.7801925391 + 0.0 i
D4 h(i*u, 1e-4) [m2 c30 u] = 1.7042477e-42 + 1.40616e-43 i   (|.| = 1.71004e-42)
D4b sgn=+1: h = 1.7042477e-42 + 1.40616e-43 i
D4b sgn=-1: h = 0.0099302955 + 0.000819569 i
D5 a_implied = -(dh/de)/c2 = (-2.64548216269086 + 0.0j)
done
```

## 2. Evaluator decomposition (t1/t2/t3) — `code/machine1_der_route_probe_evaluator.py` -> `machine1_der_route_probe_evaluator.out`

Re-executed post-diagnosis so the log carries it; five dps x zcut configs,
parts printed separately. All configs agree per-part to rel ~1e-61;
h(0.55, D*) = -0.0609211874686562688 identical everywhere: the raw evaluator
is clean at every configuration probed — v1's corruption was NOT in the evaluator.

```
evaluator decomposition probe: s = 0.55 + 0i, D = D* = 0.141733239663887191395415685084
dps  50 zcut 149.66 : t1 (10.5844484649508098 + 0.0j)
                    t2 (-15.6554372359607195 + 0.0j)
                    t3 (5.01006758354125345 + 0.0j)
                    h  (-0.0609211874686562688 + 0.0j)
dps  60 zcut 172.69 : t1 (10.5844484649508098 + 0.0j)
                    t2 (-15.6554372359607195 + 0.0j)
                    t3 (5.01006758354125345 + 0.0j)
                    h  (-0.0609211874686562688 + 0.0j)
                    t1 rel-vs-first 5.969e-61
                    t2 rel-vs-first 3.310e-61
                    t3 rel-vs-first 2.773e-61
dps  60 zcut 287.82 : t1 (10.5844484649508098 + 0.0j)
                    t2 (-15.6554372359607195 + 0.0j)
                    t3 (5.01006758354125345 + 0.0j)
                    h  (-0.0609211874686562688 + 0.0j)
                    t1 rel-vs-first 5.969e-61
                    t2 rel-vs-first 3.310e-61
                    t3 rel-vs-first 2.773e-61
dps  70 zcut 172.69 : t1 (10.5844484649508098 + 0.0j)
                    t2 (-15.6554372359607195 + 0.0j)
                    t3 (5.01006758354125345 + 0.0j)
                    h  (-0.0609211874686562688 + 0.0j)
                    t1 rel-vs-first 5.969e-61
                    t2 rel-vs-first 3.310e-61
                    t3 rel-vs-first 2.773e-61
dps  70 zcut 287.82 : t1 (10.5844484649508098 + 0.0j)
                    t2 (-15.6554372359607195 + 0.0j)
                    t3 (5.01006758354125345 + 0.0j)
                    h  (-0.0609211874686562688 + 0.0j)
                    t1 rel-vs-first 5.969e-61
                    t2 rel-vs-first 3.310e-61
                    t3 rel-vs-first 2.773e-61
```

## 3. Circle-DFT probes (c2/c4 at e=0) — three dps x zcut configs

All three return c2 = -18.816779288625 exactly; the imaginary parts are
noise-floor and SCALE WITH dps (1e-69 at dps 70, 1e-59 at dps 60) rather than
sitting at the working floor — the signature of a healthy channel. v1's
tabulated g10 was 1.737e-9 against this truth: wrong by 10 orders and sign.

```
VALIDATION-EXACT dps70 NW16 zcut172.69 : c2 = (-18.816779288625 - 1.883581248396e-69j)   c4 = (-279.180914118 + 7.60387260891e-67j)   [214s]
zcut-axis       dps70 NW16 zcut287.82 : c2 = (-18.816779288625 - 1.883581248396e-69j)   c4 = (-279.180914118 + 7.60387260891e-67j)   [217s]
dps-axis        dps60 NW16 zcut172.69 : c2 = (-18.816779288625 - 1.51297058943e-59j)   c4 = (-279.180914118 + 1.11118160801e-56j)   [137s]
```

## 4. Independent manual DFT cross-check (separate script, same circle data path)

c2/c4/c6 agree to 12+ printed digits between the production w_coeffs and a
manually-coded DFT; the odd coefficients a1 = -2.2e-16 confirm evenness of the
object. v1's tabulated g01 was -1.7779e-9 against the correctly-scaled
-4.978e-8: a different per-channel wrong ratio than g10 — two channels
corrupted at different effective scales, not one global rescaling.

```
c_0 (w^0 coeff) = (-2.21655321478e-27 - 7.77876909733e-62j)
c_2 (w^2 coeff) = (-18.8167792886 + 1.89246339611e-59j)
c_4 (w^4 coeff) = (-279.180914118 + 8.50028326869e-57j)
c_6 (w^6 coeff) = (-1382.36060778 - 4.57936545701e-54j)
---manual DFT cross-check---
manual c_0 = (-2.2165531945e-15 + 1.70160574004e-62j)
manual c_2 = (-18.8167792886 - 2.47559326522e-59j)
manual c_4 = (-279.180914118 + 1.65681558758e-56j)
manual c_6 = (-1382.36060778 + 1.27039521361e-53j)
odd a_1 = (-2.2165532e-16 - 1.3430531e-61j)
odd a_3 = (-0.011906431 - 1.4585192e-61j)
odd a_5 = (-0.00020388113 + 4.5578725e-63j)

[exited with code 0]
```

## 5. First v2 launch — the mis-set witness gate (1e-20), aborted healthy run

The witness itself was correct (rel 7.349e-9 = the Richardson path's own
truncation, 12-digit agreement with the circle) but the gate tolerance was set
to 1e-20 — machine epsilon thinking applied to a witness that carries its own
~1e-8 error budget. Abort was the CHEAP failure direction; the gate was
re-set to 1e-6 (the witness's budget) and the run relaunched. Founding #2 of
register #138.

```
CTL evenness |d_w h|_0 = 2.38129e-17
CTL fold residual h(0,0) [even limit] = -1.87618e-35 + 0.0 i
WIT real-axis c2: hh=1e-3 (-18.817058470922 + 0.0j) | hh=1e-2 (-18.84471120931 + 0.0j) | Richardson (-18.816779150332 + 0.0j)
WIT circle   c2 at e=0: (-18.816779288625 - 1.883581248396e-69j)   (circle - rich = (-1.38293e-7 - 1.88358e-69j), rel (7.349e-9 + 1.001e-70j))
WIT circle   c4/c6 at e=0: (-279.180914118 + 7.60387260891e-67j) / (-1382.36060778 + 7.59645419661e-64j)
WITNESS-FAIL: circle c2 disagrees with real-axis Richardson c2 (rel (7.349e-9 + 1.001e-70j)) -- extraction channel corrupted; aborting before the stencil (v1's failure mode, now caught at the boundary).

[exited with code 0]
```

## 7. THE ROOT CAUSE — fd_weights' transposed Vandermonde

`code/machine1_der_route_probe_fdweights.py` → `machine1_der_route_probe_fdweights.out`
(sha256 `9ad85eb2…` / `be286d41…`). fd_weights solved Am[i,j] = offs[i]**j —
the solution is indexed by POWER (coefficients of the polynomial that takes the
rhs values at the nodes) — while the consumer zips the returned weights with
the offsets as if indexed by NODE. The correct system is Am[i,j] = offs[j]**i
(node j's i-th moment). Consequences, all receipted in the output:

- the buggy order-0 weights annihilate constants to 5.1e-57 and pass only
  slope·HE·(Σ w_o o) with Σ w_o o = −1/280: the HEALTHY stencil values through
  them give g10 = +1.73699285714e-9 against v1's observed +1.73699321583e-9
  (rel −2.1e-7, the slope literal's own rounding) — the corruption reproduced
  analytically from healthy inputs;
- a 10-second polynomial self-test catches it: buggy order-1 on t³+2t²+5t+7
  gives 0.6083333333 (truth 5); the fixed system is exact (order 0 = e_center
  exactly, orders 1–4 exact to the dps floor);
- families 1–5 stayed green because they probed the evaluator (family 2), the
  circle DFT (families 3–4) — every stage EXCEPT fd_weights, the one stage
  between the healthy per-node tab prints and the corrupted g-table; v2's
  channel witness (family 5's re-run) watched the circle stage — the one that
  was never broken.

```
fd_weights root-cause probe (dps 50)
order-0 buggy : ['0.0', '0.00357142857143', '-0.000892857142857', '-0.00486111111111', '0.00121527777778', '0.00138888888889', '-0.000347222222222', '-9.92063492063e-5', '2.48015873016e-5']
order-0 fixed : ['0.0', '0.0', '0.0', '0.0', '1.0', '0.0', '0.0', '0.0', '0.0']
fixed == e_center: True | buggy sum w_o: 5.0978941e-57 | buggy sum w_o*o: -0.0035714286
poly self-test order 0: buggy -0.05833333333 (err -7.058) | fixed 7.0 (err 0.0) | truth 7.0
poly self-test order 1: buggy 0.6083333333 (err -4.392) | fixed 5.0 (err 0.0) | truth 5.0
analytic reproduction: healthy tab through BUGGY order-0 weights -> g10 = 1.73699285714e-9
v1 observed g10 = 1.73699321583e-9  | ratio rec/v1 = 0.99999979  (rel dev -2.065e-7)
note: rel dev -2.1e-7 is the rounding of the 6-s.f. slope literal; the
      buggy weights annihilate the constant to 5.1e-57 and pass only
      slope * HE * (sum w_o o) with sum w_o o = -1/280 -- the
      reconstruction is exact to the literal's precision.
```

v2 evidence note: v2's streamed per-node tab prints (used above, via the
measured slope −486.358) were destroyed by v2's own final summary write —
`open(OUT,"w")` on the SAME path the stdout was redirected to — and survive
only in the session's monitor captures; the committed 949-byte
`machine1_der_route_a_b_a3_v2.out` is the final summary alone (one process,
one code version; not a two-writer race as first read). v3 separates the
stdout capture from the summary file (FIX-4).
