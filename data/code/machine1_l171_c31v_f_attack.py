"""m1-L171: independent verification of m2 c31b SCORED (ff82743) + the requested
ATTACK on the condition-C draft fitness F (machine2_c31_fitness_constants.json).

Part A (verify, on m2's committed rung literals -- nothing re-typed, trap #S12):
  A1 V1  fit dev ~ [eps^-2, 1, eps, eps^2, eps^3] on the six new rungs -> c0_new
  A2 V2  plain K=3 poly on the six r's -> a3; dev vs published reference
  A3 transfer = dev_V2 / c0_V1 (m2: 2.9078e9); T3/transfer vs T1 (487x)
  A4 identity c0_new_with_a_operative = delta_a + c0_new (sign per m2's convention)
  A5 eps^2 * dev_signed range (m2: +1.066e-17 ... -2.353e-17)

Part B (attack F on the sealed census, heat78c_census_result.json):
  B1 reproduce m2's 125-slice claims (distinct F, 9 survivors, 7 firers above
     worst survivor) and identify WHICH cells invert -- and whether the inversion
     is a cross-site S artifact
  B2 per-site linearization quality: residual of asinh((lam-theta)/u) vs log10(delta)
     least-squares line per site; curvature where S is steepest
  B3 k=25 fallback regime mismatch: median(-8.243) vs the k>=9 phi8=4 family
  B4 the lam-term exchange rate varies by the S spread (5.2x across sites)
No m2 computation re-run; no F value adopted. Attack only, as asked.
"""
import json, math
from mpmath import mp, mpf

mp.dps = 60
D = "data/"

# ---------------- Part A: c31b verification ----------------
sc = json.load(open(D + "machine2_c31b_scored.json"))
rungs = sc["rungs"]
eps = [mpf(k) for k in rungs]
dev = [mpf(rungs[k]["dev_signed"]) for k in rungs]
r_c = [mpf(rungs[k]["r_corrected_a"]) for k in rungs]

def lsq(A, b):
    """Least squares via normal equations with mpf (5x5 max)."""
    n = len(A[0])
    M = [[sum(A[k][i] * A[k][j] for k in range(len(A))) for j in range(n)] for i in range(n)]
    y = [sum(A[k][i] * b[k] for k in range(len(A))) for i in range(n)]
    # Gaussian elimination
    for i in range(n):
        p = max(range(i, n), key=lambda r2: abs(M[r2][i]))
        M[i], M[p] = M[p], M[i]
        y[i], y[p] = y[p], y[i]
        for r2 in range(i + 1, n):
            f = M[r2][i] / M[i][i]
            for c in range(i, n):
                M[r2][c] -= f * M[i][c]
            y[r2] -= f * y[i]
    x = [mpf(0)] * n
    for i in reversed(range(n)):
        x[i] = (y[i] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x

# A1: V1
A1 = [[e ** -2, mpf(1), e, e ** 2, e ** 3] for e in eps]
c1 = lsq(A1, dev)
res = [dev[i] - sum(A1[i][j] * c1[j] for j in range(5)) for i in range(6)]
print("A1 V1 c0 (six rungs alone, my fit) =", mp.nstr(c1[0], 12),
      " m2:", sc["V1"]["c0_new_six_rungs_alone"])
print("   max |res| =", mp.nstr(max(abs(x) for x in res), 8),
      " m2:", sc["V1"]["max_in_sample_residual"])

# A2: V2 plain K=3 -- SCALED basis s = eps*1e4 (the raw eps^3 column ~1e-15 is
# catastrophically conditioned in normal equations; a3 = c3 * (1e4)^3)
A2 = [[mpf(1), e * mpf(10) ** 4, (e * mpf(10) ** 4) ** 2, (e * mpf(10) ** 4) ** 3] for e in eps]
c2 = lsq(A2, r_c)
c2[3] = c2[3] * mpf(10) ** 12
c2[2] = c2[2] * mpf(10) ** 8
c2[1] = c2[1] * mpf(10) ** 4
# a3 in the exchange convention = the CONSTANT term of the K-fit (c30 refit:
# a3_by_K reads coefficient index 0), not the eps^3 coefficient
print("A2 V2 a3 (plain K=3, my fit)  =", mp.nstr(c2[0], 20),
      "\n   m2:", sc["V2"]["a3_new_six_rungs_alone_plainK3"])
d_v2 = abs(c2[0] - mpf(sc["V2"]["reference"]))
print("   dev vs reference =", mp.nstr(d_v2, 8), " m2:", sc["V2"]["dev"])

# A3: transfer + tolerance inconsistency
tr = d_v2 / mpf(sc["V1"]["c0_new_six_rungs_alone"])
t1, t3 = mpf(sc["V1"]["T1"]), mpf(sc["V2"]["T3"])
print("A3 transfer dev_V2/c0_V1 =", mp.nstr(tr, 6), " m2: 2.9078e9")
print("   T3/transfer =", mp.nstr(t3 / tr, 6), " T1 =", mp.nstr(t1, 6),
      " ratio T1/(T3/transfer) =", mp.nstr(t1 / (t3 / tr), 4), " m2: 487x")

# A4: identity
delta_a = mpf("1.633394698e-15")
print("A4 delta_a + c0_new =", mp.nstr(delta_a + mpf(sc["V1"]["c0_new_six_rungs_alone"]), 12),
      " m2 c0_new_with_a_operative:", sc["diagnostics"]["c0_new_with_a_operative"])

# A5: eps^2*dev
es = [dev[i] * eps[i] ** 2 for i in range(6)]
print("A5 eps^2*dev range:", mp.nstr(min(es), 4), "...", mp.nstr(max(es), 4),
      " m2: -2.353e-17 ... +1.066e-17")
print("   138x check: delta_a/c0_new =", mp.nstr(delta_a / mpf(sc["V1"]["c0_new_six_rungs_alone"]), 5))

# ---------------- Part B: F attack ----------------
fc = json.load(open(D + "machine2_c31_fitness_constants.json"))
theta, u_w = mpf(fc["theta"]), mpf(fc["u"])
S = {k: mpf(v) for k, v in fc["S_per_site"].items()}
S_med = mpf(fc["S_median_fallback"])

cen = json.load(open(D + "heat78c_census_result.json"))["results"]
m64 = {k: v for k, v in cen.items() if k.startswith("64/")}
# m2's 125-cell slice: sites k>=6 -- {6,7,8} x {2,4,6} (9 sites) + {9..24} x {4}
# (16 sites) = 25 sites x 5 deltas = 125 cells, containing all 9 survivors
slice_sites = {f"{k}/{p}" for k in (6, 7, 8) for p in (2, 4, 6)} | \
              {f"{k}/4" for k in range(9, 25)}

def F(cell):
    M_, k, phi8, dl = cell.split("/")
    site = f"{k}/{phi8}"
    lam = mpf(m64[cell]["lam_min"])
    s = S.get(site, S_med)
    return mpf(math.log10(mpf(dl))) - mp.asinh((lam - theta) / u_w) / s, site, m64[cell]["fires"]

# NOTE: the exact "125-cell slice" is not reconstructible from the fitness
# constants file (no slice field). The 23-site k>=6 family (115 cells) contains
# all 9 survivors and reproduces the 7-inversion count; the full 205 is computed
# as the robustness check.
cells125 = [c for c in m64 if "/".join(c.split("/")[1:3]) in slice_sites]
for label, cs in [("k>=6 family (115 cells)", cells125), ("FULL M=64 (205 cells)", list(m64))]:
  vals = sorted(((F(c), c) for c in cs), key=lambda t: t[0])
  print(f"\nB1 [{label}] n =", len(vals), " distinct F:", len(set(v[0][0] for v in vals)))
  surv = [v for v in vals if not v[0][2]]
  fire_above = [v for v in vals if v[0][2] and v[0][0] > surv[0][0][0]]
  print("   survivors:", len(surv), " worst survivor F =", mp.nstr(surv[0][0][0], 6),
        " at", surv[0][1], "site", surv[0][0][1])
  print("   firers above worst survivor:", len(fire_above), " m2: 7")
  for v in fire_above:
      print("     ", v[1], "site", v[0][1], "F =", mp.nstr(v[0][0], 6))

# B3: fallback regime -- medians
s_k9 = [abs(S[f"{k}/4"]) for k in range(9, 25)]
s_all = [abs(x) for x in S.values()]
print("\nB3 S medians: all-41 =", mp.nstr(sorted(s_all)[20], 6),
      " k>=9 phi8=4 family =", mp.nstr(sorted(s_k9)[len(s_k9)//2], 6),
      " k=20..24 mean =", mp.nstr(sum(abs(S[f'{k}/4']) for k in range(20,25))/5, 6))

# B4: exchange-rate spread
inv = sorted((1/abs(x), k) for k, x in S.items())
print("B4 lam->F exchange rate 1/|S|: min", mp.nstr(inv[0][0], 4), "at", inv[0][1],
      " max", mp.nstr(inv[-1][0], 4), "at", inv[-1][1],
      " spread =", mp.nstr(inv[-1][0]/inv[0][0], 4), "x")

# B2: per-site linearization residual (5-point least squares line, max |res|)
print("\nB2 per-site line-fit max|res| (asinh vs log10 delta), worst 8:")
qual = []
for site in sorted({"/".join(c.split("/")[1:3]) for c in m64} & slice_sites,
                   key=lambda s: (int(s.split("/")[0]), int(s.split("/")[1]))):
    pts = []
    for c in m64:
        if "/".join(c.split("/")[1:3]) == site:
            lam = mpf(m64[c]["lam_min"])
            pts.append((math.log10(mpf(c.split("/")[3])), mp.asinh((lam - theta) / u_w)))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    n = len(pts); sx = sum(xs); sy = sum(ys)
    sxx = sum(x*x for x in xs); sxy = sum(xs[i]*ys[i] for i in range(n))
    b = (n*sxy - sx*sy) / (n*sxx - sx*sx)
    a_ = (sy - b*sx) / n
    mr = max(abs(ys[i] - (a_ + b*xs[i])) for i in range(n))
    qual.append((mr, site, mp.nstr(b, 6)))
for mr, site, b in sorted(qual, reverse=True)[:8]:
    print("    site", site, "slope", b, "max|res|", mp.nstr(mr, 4))
print("    (S table slope for comparison is in the same units)")
