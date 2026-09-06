"""machine1 L171 -- INDEPENDENT REIMPLEMENTATION of m2-c30's fit chain (adjudication).

Every statistic in m2's c30 section 4 is recomputed here from their committed data
(m2_c30_scored.json rung u values + m1-L165 sect9a published u column) with an
independently written fitter: QR solve on the rectangular design matrix (m2 used
normal equations + lu_solve). dps 60 throughout. No zeta, no root find -- this file
is pure linear algebra on published numbers.

Sections (mirroring their letter):
  A. r on the 11 published rungs, operative constants (their design.out section A)
  B. 11-rung LOO order table (their G3 / design.out section B)
  C. 17-rung union fit table K=3..10 (their fit17) + Q1 per-rung deviations
  D. power discrimination at K=6, one extra basis function (their posthoc2 section A)
  E. delta_a supports: a_true vs retired 16 s.f. vs m1 a(0) ladder value
  F. decisive test: plain-poly refit with a_true / a_retired (their posthoc2 section C)
  G. six new rungs ALONE (their posthoc3 (i)); eleven published ALONE (posthoc3 (ii))
  H. one-parameter delta_a scan minimising the 17-rung K=6 max residual (posthoc2 D)
  I. counterfactual re-grade of Q1..Q5 with a_true (their counterfactual.out)
  J. R30-B chain arithmetic check (reform_threshold.out)
"""
from mpmath import mp, mpf, sqrt
mp.dps = 60

A_OP = mpf("2.645521411811664489")
B_OP = -mpf("7.4624528767937415788")
A_RET = mpf("2.645521411811663")          # retired 16 s.f.
A_TRUE_M2 = mpf("2.645521411811662855605")  # m2's ladder value (19 s.f. print)
A0_LADDER = mpf("2.645521411811663079")     # m1's eps->0 derivative-ladder a(0)

# m1-L165 sect9a published u column (heat72x republication, native dps 50)
PUB = [
    ("0.001",              "0.05150723818940063653522997138655916611777128352831"),
    ("0.0011239031932557", "0.054614584740162860829271236079197856379810987308508"),
    ("0.002",              "0.072945092837465636911527414020464645263120485246671"),
    ("0.0035",             "0.09670183421043065840984313002276196906002275045949"),
    ("0.006",              "0.12706034318675893153656817913317280690430806327895"),
    ("0.0082667603361",    "0.14962144595780802891341103521644637411107076093496"),
    ("0.012",              "0.18122223459720552038513232631511513662541625076064"),
    ("0.02",               "0.23662703502895471893639804350283991882970959834519"),
    ("0.035",              "0.31979403084190422618229559433082050463362878645843"),
    ("0.06",               "0.43405746526370626569197604987746105430711695666647"),
    ("0.1",                "0.59427921830513711248148784269207030531776649353816"),
]
# m2 c30's six new rungs (m2_c30_scored.json, xi_D at dps 60)
NEW = [
    ("0.0001",  "0.01626735311637081543652166235648198533749"),
    ("0.00015", "0.01992476239411063527334232617346140282631"),
    ("0.00022", "0.02413246812812595998486983709533875808145"),
    ("0.00033", "0.02956070276139769356253217112920061589147"),
    ("0.0005",  "0.03639543629351059261305814257433460217533"),
    ("0.00075", "0.04459084694558961727534415865200776265643"),
]


def r_of(eps, u, a=A_OP, b=B_OP):
    return (u * u - a * eps + b * eps ** 2) / eps ** 3


def lsq(basis, xs, ys):
    """QR least squares on the rectangular design matrix (independent of m2's
    normal-equations path). basis: list of callables eps -> value."""
    n = len(basis)
    Am = mp.matrix(len(xs), n)
    bv = mp.matrix(len(xs), 1)
    for i, (x, y) in enumerate(zip(xs, ys)):
        for j, f in enumerate(basis):
            Am[i, j] = f(x)
        bv[i] = y
    c, _ = mp.qr_solve(Am, bv)
    return [c[j] for j in range(n)]


def evalfit(basis, c, x):
    return mp.fsum(f(x) * cj for f, cj in zip(basis, c))


def maxres(basis, xs, ys):
    c = lsq(basis, xs, ys)
    return max(abs(evalfit(basis, c, x) - y) for x, y in zip(xs, ys)), c


def loo_rms(basis, xs, ys):
    """Interior leave-one-out rms, endpoints excluded (m2's declared convention)."""
    errs = []
    for i in range(1, len(xs) - 1):
        xr = xs[:i] + xs[i + 1:]
        yr = ys[:i] + ys[i + 1:]
        c = lsq(basis, xr, yr)
        errs.append(evalfit(basis, c, xs[i]) - ys[i])
    return sqrt(mp.fsum(e ** 2 for e in errs) / len(errs))


def poly_basis(K):
    return [((lambda j: (lambda e: e ** j))(j)) for j in range(K + 1)]


def n(v, d=6):
    return mp.nstr(v, d)


print("=== A. r on the 11 published rungs, operative constants ===")
E11 = [mpf(e) for e, _ in PUB]
U11 = [mpf(u) for _, u in PUB]
R11 = [r_of(e, u) for e, u in zip(E11, U11)]
for e, r in zip(E11, R11):
    print("  eps=%-22s r=%s" % (e, n(r, 24)))

print("\n=== B. 11-rung LOO order table (K=3..8) ===")
for K in range(3, 9):
    mr, c = maxres(poly_basis(K), E11, R11)
    lo = loo_rms(poly_basis(K), E11, R11)
    print("  K=%d  maxres=%s  loo=%s  a3=%s" % (K, n(mr), n(lo), n(c[0], 20)))

print("\n=== C. 17-rung union fit (K=3..10) + Q1 deviations ===")
E17 = [mpf(e) for e, _ in NEW] + E11
U17 = [mpf(u) for _, u in NEW] + U11
R17 = [r_of(e, u) for e, u in zip(E17, U17)]
for K in range(3, 11):
    mr, c = maxres(poly_basis(K), E17, R17)
    lo = loo_rms(poly_basis(K), E17, R17)
    print("  K=%-2d loo=%-12s maxres=%-12s a3=%s" % (K, n(lo), n(mr), n(c[0], 20)))
c6, _ = maxres(poly_basis(6), E17, R17)
a3_by_K = [maxres(poly_basis(K), E17, R17)[1][0] for K in (6, 7, 8)]
spread = max(a3_by_K) - min(a3_by_K)
print("  LOO-optimal K = 3 expected; a3 spread K6..8 = %s" % n(spread, 9))
c11_6 = lsq(poly_basis(6), E11, R11)
print("  Q1 per-rung |r - r_pred(K=6 on 11 published)|:")
for (es, _), u in zip(NEW, U17[:6]):
    dev = abs(r_of(mpf(es), u) - evalfit(poly_basis(6), c11_6, mpf(es)))
    print("    eps=%-8s dev=%s" % (es, n(dev, 9)))

print("\n=== D. power discrimination: K=6 poly + ONE extra basis (17 rungs) ===")
base6 = poly_basis(6)
EXTRAS = [
    ("none",        []),
    ("eps^-1 (b)",  [lambda e: 1 / e]),
    ("eps^-2 (a)",  [lambda e: 1 / e ** 2]),
    ("eps^-3 (D*)", [lambda e: 1 / e ** 3]),
    ("eps^-3/2",    [lambda e: 1 / (e * sqrt(e))]),
    ("eps^-2+-3",   [lambda e: 1 / e ** 2, lambda e: 1 / e ** 3]),
]
for tag, ex in EXTRAS:
    mr, c = maxres(base6 + ex, E17, R17)
    tail = ("  coeffs " + " ".join(n(cf, 8) for cf in c[7:])) if ex else ""
    print("  %-13s max res = %-12s%s" % (tag, n(mr, 9), tail))
c0 = lsq(base6 + [lambda e: 1 / e ** 2], E17, R17)[7]
print("  c0 (eps^-2 coeff) = %s   ->  a_true = a_used + c0 = %s" % (n(c0, 10), n(A_OP + c0, 21)))

print("\n=== E. delta_a supports ===")
print("  a_true - a_retired16 = %s" % n(A_OP + c0 - A_RET, 7))
print("  a_true - m1 a(0)     = %s" % n(A_OP + c0 - A0_LADDER, 7))
print("  a_used - a_retired16 = %s  (the #120 move)" % n(A_OP - A_RET, 6))

print("\n=== F. decisive test: plain-poly refit under a_true / a_retired ===")
for tag, a in (("a_used", A_OP), ("a_true(m2)", A_TRUE_M2), ("a_retired16", A_RET)):
    R = [r_of(e, u, a=a) for e, u in zip(E17, U17)]
    print("  --- %s" % tag)
    best, bestK = None, None
    a3s = {}
    for K in range(3, 9):
        mr, c = maxres(poly_basis(K), E17, R)
        lo = loo_rms(poly_basis(K), E17, R)
        a3s[K] = c[0]
        if best is None or lo < best:
            best, bestK = lo, K
        print("    K=%d  max res %-12s LOO %-12s a3 %s" % (K, n(mr, 8), n(lo, 8), n(c[0], 20)))
    sp = max(a3s[k] for k in (6, 7, 8)) - min(a3s[k] for k in (6, 7, 8))
    print("    LOO-optimal K=%d  a3 spread K6..8 = %s" % (bestK, n(sp, 9)))

print("\n=== G. disjoint fits ===")
E6 = [mpf(e) for e, _ in NEW]
U6 = [mpf(u) for _, u in NEW]
R6 = [r_of(e, u) for e, u in zip(E6, U6)]
for K in (2, 3):
    bas = [lambda e: 1 / e ** 2] + poly_basis(K)
    mr, c = maxres(bas, E6, R6)
    print("  six new alone, c0/eps^2 + poly K=%d:  c0=%s  a3=%s  max res=%s"
          % (K, n(c[0], 10), n(c[1], 20), n(mr, 9)))
for K in (5, 6, 7):
    bas = poly_basis(K) + [lambda e: 1 / e ** 2]
    mr, c = maxres(bas, E11, R11)
    print("  11 published alone, K=%d + eps^-2:    c0=%s  max res=%s"
          % (K, n(c[-1], 10), n(mr, 9)))

print("\n=== H. 1-D delta_a scan minimising 17-rung K=6 max residual ===")
def scan_res(da):
    R = [r_of(e, u, a=A_OP + da) for e, u in zip(E17, U17)]
    return maxres(poly_basis(6), E17, R)[0]
lo_b, hi_b = mpf("-3e-15"), mpf("0")
for _ in range(200):  # golden-section in mp
    m1_ = lo_b + (hi_b - lo_b) * mpf("0.3819660112501051")
    m2_ = hi_b - (hi_b - lo_b) * mpf("0.3819660112501051")
    if scan_res(m1_) < scan_res(m2_):
        hi_b = m2_
    else:
        lo_b = m1_
das = (lo_b + hi_b) / 2
print("  delta_a* = %s  ->  a = %s   max res = %s" % (n(das, 12), n(A_OP + das, 21), n(scan_res(das), 9)))

print("\n=== I. counterfactual re-grade with a_true (POST-HOC, not a re-grade) ===")
Rt = [r_of(e, u, a=A_TRUE_M2) for e, u in zip(E17, U17)]
mr, _ = maxres(poly_basis(6), E17, Rt)
c11t = lsq(poly_basis(6), E11, [r_of(e, u, a=A_TRUE_M2) for e, u in zip(E11, U11)])
q1 = max(abs(r_of(mpf(es), u, a=A_TRUE_M2) - evalfit(poly_basis(6), c11t, mpf(es)))
         for (es, _), u in zip(NEW, U6))
a3t = {K: maxres(poly_basis(K), E17, Rt)[1][0] for K in (6, 7, 8)}
best, bestK = None, None
for K in range(3, 9):
    lo = loo_rms(poly_basis(K), E17, Rt)
    if best is None or lo < best:
        best, bestK = lo, K
spr = max(a3t.values()) - min(a3t.values())
lohs = [loo_rms(poly_basis(K) + [lambda e: sqrt(e)], E17, Rt) for K in range(3, 9)]
print("  Q1 %s  Q2 K=%d  Q4 spread %s  min-K loo(half)/loo(base) = %s"
      % (n(q1, 9), bestK, n(spr, 9), n(min(lohs) / best, 9)))

print("\n=== J. R30-B chain arithmetic (log10 n = C^2 |s0|^2 / ((2 sigma0 - 1) ln 10)) ===")
C2 = mpf("0.046189857")
for sig, tag in (("0.7159014103823531", "measured"), ("0.55", ""), ("0.65", "")):
    s0thr = sqrt(mpf(8) * (2 * mpf(sig) - 1) * mpf("2.302585092994046") / C2)
    print("  sigma0=%-18s |s0|<= %.8f for n<=1e8" % (sig + " " + tag, s0thr))
for s0v in ("47.2977588172104875", "20", "13.12", "10", "5"):
    s0 = mpf(s0v)
    lg = C2 * s0 ** 2 / ((2 * mpf("0.7159014103823531") - 1) * mpf("2.302585092994046"))
    print("  |s0|=%-20s n = 10^%.5g" % (s0v, lg))
print("\nl171 refit done")
