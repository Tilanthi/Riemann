#!/usr/bin/env python3
"""heat87 gen-1 prereg — DERIVATION OF THE REGISTERED BANDS from public data only.

Input: the heat85 launch-4 panel (commit d7a90de, data/machine1_heat85_results.json),
already revealed in m1-L176 (98bc9c6). Nothing in-flight, nothing sealed-only.

Law L1 (the registered extrapolator, stated BEFORE any gen-1 cell is computed):
  For each k, on the pre-crossing segment, the adjacent differences
  d_i = lam(k, d_i + h) - lam(k, d_i)  (h = the local grid step)
  accelerate geometrically:  d_{i+1} = rho(k) * d_i  with rho(k) > 1.
  Registered band per k: rho in {rhohat/1.3, rhohat, rhohat*1.3}, where rhohat is
  the ratio of the last two measured adjacent differences at equal spacing.
  Crossing delta*(k) = the smallest delta with lam < 0 under the geometric sum.

Anchors weaker than two equal-spacing differences are DECLARED (k=25: two points
at h=0.05 only; its per-step d is the window average, rho assumed = 2.0 with the
same 1.3x band — the weakest anchor in the panel, flagged in the prereg).

Outputs: per-k rhohat, the three-rho crossing set, the registered band, and the
acceleration audit of every existing equal-spacing triple (L1's mechanism check
on gen-0 data, 7/7 expected).
"""
import json
import os
from decimal import Decimal, getcontext

getcontext().prec = 50
HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = json.load(open(os.path.normpath(os.path.join(HERE, "..", "machine1_heat85_results.json"))))


def cells():
    out = {}
    for key, v in PANEL["cells"].items():
        k, d = key.split("/")
        out[(int(k), Decimal(d))] = Decimal(v["lam_min"])
    for key, v in PANEL["gate"]["founders"].items():
        k, d = key.split("/")
        out.setdefault((int(k), Decimal(d)), Decimal(v["lam"]))
    return out


C = cells()
KS = sorted({k for k, _ in C})


def diffs(k):
    pts = sorted((d, lam) for (kk, d), lam in C.items() if kk == k)
    out = []
    for i in range(len(pts) - 1):
        h = pts[i + 1][0] - pts[i][0]
        out.append((pts[i][0], h, pts[i + 1][1] - pts[i][1]))
    return pts, out


def cross_from(last_delta, lam_last, d_last, rho):
    """Smallest delta with lam<0 if differences grow by rho per h=0.01 step."""
    lam, d, n = lam_last, d_last, 0
    while lam > 0 and n < 4000:
        d = d * rho
        lam = lam + d
        n += 1
    return last_delta + Decimal(n) * Decimal("0.01"), n


print("=== L1 mechanism audit on gen-0 data: every equal-spacing triple ===")
trip_ok, trip_tot = 0, 0
for k in KS:
    pts, ds = diffs(k)
    for i in range(len(ds) - 1):
        (d1, h1, a), (d2, h2, b) = ds[i], ds[i + 1]
        if h1 == h2:
            trip_tot += 1
            acc = (b - a) < 0
            trip_ok += acc
            print("  k=%2d triple @%.3f h=%.3f: d %.6e -> %.6e  accelerating=%s"
                  % (k, float(d1), float(h1), float(a), float(b), acc))
print("triples accelerating: %d/%d" % (trip_ok, trip_tot))

print("\n=== per-k rho and registered crossing bands ===")
bands = {}
GEN1_KS = [16, 18, 19, 20, 21, 22, 23, 24, 25]
for k in [kk for kk in KS if kk in GEN1_KS]:
    pts, ds = diffs(k)
    lam_last = pts[-1][1]
    del_last = pts[-1][0]
    if lam_last < 0:
        # already crossed in gen-0 (k=16, 18): bracket + linear interpolation only
        pos = [(d, lam) for d, lam in pts if lam > 0]
        lo, lpos = pos[-1]
        hi, lneg = pts[pts.index((lo, lpos)) + 1]
        lin = lo + (hi - lo) * lpos / (lpos - lneg)
        bands[k] = (lo, hi)
        print("  k=%2d  CROSSED in gen-0: bracket (%.4f, %.4f), linear point %.6f"
              % (k, float(lo), float(hi), float(lin)))
        continue
    eq = [(d0, h, dv) for (d0, h, dv) in ds]
    pair = None
    for i in range(len(eq) - 1):
        if eq[i][1] == eq[i + 1][1]:
            pair = eq[i + 1]
    if k == 25:
        # weakest anchor: h=0.05 window only; average per-0.01 d, rho assumed 2.0
        d0, h, dv = ds[-1]
        d_step = dv / (h / Decimal("0.01"))
        rho_hat = Decimal("2.0")
        anchor = "WEAKEST (2 pts, h=0.05; mean d, rho=2.0 assumed)"
    else:
        assert pair is not None, k
        d0, h, dv = pair
        d_step = dv / (h / Decimal("0.01"))
        prev = [x for x in eq if x[1] == h and x[0] < d0]
        rho_hat = dv / prev[-1][2]
        anchor = "h=%.2f @%.3f" % (float(h), float(d0))
    xs = []
    for rho in (rho_hat / Decimal("1.3"), rho_hat, rho_hat * Decimal("1.3")):
        x, n = cross_from(del_last, lam_last, d_step, rho)
        xs.append(x)
    bands[k] = (min(xs), max(xs))
    print("  k=%2d  %s  rhohat=%.4f  lam@%s=%+.6e  d_step=%+.6e  crossings %s  band (%.4f, %.4f)"
          % (k, anchor, float(rho_hat), del_last, float(lam_last), float(d_step),
             ["%.4f" % float(x) for x in xs], float(min(xs)), float(max(xs))))

print("\nRegistered (rounded OUTWARD to the printed 4th decimal):")
for k in GEN1_KS:
    lo, hi = bands[k]
    print("  delta*(%d) in (%.4f, %.4f)" % (k, float(lo), float(hi)))
