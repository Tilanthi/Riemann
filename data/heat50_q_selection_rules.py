"""heat50 — q-selection-rule resolution of the 3.44x GUE discrepancy.
  Machine 3's pushed generator (data/gue_one_matrix_for_mac.py, commit
  43c3c06) settles the convention question: their d = (lam2-lam1)/2
  (half-gap, SAME as ours), q = S2*d^2/2, R = S4/S2^2 — on their pushed
  matrix (seed 20260903) our pipeline reproduces their d/q/R/B/kappa4
  to ratios 1.0. Their construction omits the 1/sqrt(2) on the Gaussian
  entries, but q and R are scale-invariant, so that cannot matter.
  The ONE difference is selection: their published H1-H3 population and
  this generator take the tightest pair among the CENTRAL 40 eigenvalues
  of each N=300 matrix; our heat46 GUE took the GLOBAL tightest pair in
  the matrix. Their single-matrix values: window-40 pick j=148 q=0.02629;
  global pick j=211 q=0.004660 — a 5.6x swing from selection alone on
  one matrix, bracketing the 3.44x population shift.
  THIS SCRIPT (pre-registered, trap #32): apply BOTH selection rules to
  the ZETA side (333 disjoint 300-zero windows of the 100k table;
  central-40 rule = tightest pair among zeros [mid-20, mid+20) of each
  window; global rule = tightest pair in the whole window). Predictions
  registered before running:
    (P1) their rule on zeta gives q median within ~30% of their GUE
         0.01867 (i.e. the 3.4x gap closes), NOT near our-rule 0.0059.
    (P2) R medians under both zeta rules land within ~5% of each other
         (R is an environment statistic, selection-robust) — the GUE
         R match under mismatched rules in heat46 is thereby explained.
  Falsifier: P1 fails (their-rule zeta q stays near 0.0059) => the
  selection explanation is wrong and the anomaly reopens.
  Traps: #36 (quote this .out), #38 (index-based exclusion).
"""
import numpy as np
import datetime

print("TIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
Z = np.sort(np.loadtxt("/tmp/zeros1.dat", dtype=np.float64))


def stats(Z, j):
    m0 = 0.5*(Z[j]+Z[j+1]); d = 0.5*(Z[j+1]-Z[j])
    others = np.concatenate([Z[:j], Z[j+2:]])
    disp = others - m0
    S2 = float(np.sum(1.0/disp**2)); S4 = float(np.sum(1.0/disp**4))
    return S4/S2**2, S2*d*d/2


out = {}
for label, central in (("their-central-40", True), ("our-global", False)):
    Rs, qs = [], []
    for start in range(0, len(Z)-300, 300):
        seg = Z[start:start+300]
        if central:
            mid = len(seg)//2
            w = seg[mid-20:mid+20]
            jl = int(np.argmin(np.diff(w))) + (mid-20)
        else:
            jl = int(np.argmin(np.diff(seg)))
        r, q = stats(Z, start+jl)
        Rs.append(r); qs.append(q)
    Rs = np.array(Rs); qs = np.array(qs)
    out[label] = dict(n=len(Rs), R_med=float(np.median(Rs)),
                      R_p25=float(np.percentile(Rs, 25)),
                      R_p75=float(np.percentile(Rs, 75)),
                      q_med=float(np.median(qs)),
                      q_p25=float(np.percentile(qs, 25)),
                      q_p75=float(np.percentile(qs, 75)))
    print(f"zeta {label:15s} n={len(Rs)}: R med {out[label]['R_med']:.4f} "
          f"[{out[label]['R_p25']:.4f}, {out[label]['R_p75']:.4f}]  "
          f"q med {out[label]['q_med']:.5f} "
          f"[{out[label]['q_p25']:.5f}, {out[label]['q_p75']:.5f}]", flush=True)

print("\n== reference populations (previously on disk) ==", flush=True)
print("GUE, THEIR rule (their Letter 5 H1-H3): R med 0.1878 [0.1494, 0.2426]; q med 0.01867 [0.00988, 0.03023]", flush=True)
print("GUE, OUR  rule (heat46, global-in-300): R med 0.1878 [0.1503, 0.2400]; q med 0.00543", flush=True)
print("zeta low-height, OUR rule (heat45):     R med 0.1661; q med 0.0059", flush=True)

tq, oq = out["their-central-40"]["q_med"], out["our-global"]["q_med"]
tR, oR = out["their-central-40"]["R_med"], out["our-global"]["R_med"]
print(f"\n== registered verdicts ==", flush=True)
print(f"P1 (their rule closes the gap): zeta q(their) {tq:.5f} / GUE q(their) 0.01867 = {tq/0.01867:.2f}x "
      f"(was 3.44x under mismatched rules) -> {'PASS' if abs(tq/0.01867-1) < 0.35 else 'FAIL'}", flush=True)
print(f"    matched-rule ratios: their-rule {tq/0.01867:.2f}x, our-rule {oq/0.00543:.2f}x", flush=True)
print(f"P2 (R selection-robust on zeta): R(their) {tR:.4f} vs R(our) {oR:.4f} = {100*abs(tR-oR)/oR:.1f}% apart "
      f"-> {'PASS' if abs(tR-oR)/oR < 0.05 else 'FAIL'}", flush=True)

print("\nTIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
      .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
print("done", flush=True)
