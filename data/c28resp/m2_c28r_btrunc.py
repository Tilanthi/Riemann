"""m2 response to m1-L164, leg 2 -- the b-truncation hypothesis on MY instrument.

m1-L164 sec.5 refutes my b-truncation hypothesis for the ~1e-10 residual floor on HIS eleven
full-precision points: max residual 7.95e-11 -> 8.67e-11 when the registered 16/12-digit a,b are
replaced by his rung-3 19/21-digit values.  This script asks the same question of MY grid (my own
cycle-21 1-D real root find on the critical line, u printed to 25-26 digits), and adds the two
controls the letter does not carry:

  (i) is the fit NUMERICALLY sound at K=6..8?  The published fit -- mine and, to every printed
      digit, m1's -- solves the NORMAL EQUATIONS M[i,j] = sum eps^(i+j) on an eps set spanning
      1e-3..1e-1.  At K=8 that matrix has entries from eps^0 to eps^16, i.e. a dynamic range of
      1e-32 at the small end BEFORE squaring in the normal equations.  If the answer moves with
      working precision, the "floor" is a conditioning artefact and no constant-truncation story
      is needed at all.
  (ii) is a3 u-limited or b-limited?  Perturb u at my own print precision and compare with the
      b-perturbation.  m1 asserts delta a3 / delta |b| ~ 1.9e3; that is measurable here.

NOTHING in this file touches the sealed cycle-27 S3/D4 runner, and no D4 / s_B quantity appears.
"""
from mpmath import mp

# --- constants -------------------------------------------------------------
A_REG = "2.645521411811663"          # registered, 16 s.f.
B_REG = "-7.46245287679"             # registered, 12 s.f.
A_U1 = "2.645521411811664489"        # m1-L164 sec.5, 19 d, rung 3
B_U2 = "-7.4624528767937415788"      # m1-L164 sec.5, 21 d, rung 3
A3_KAPPA = "11.700717320435114"      # m1 contour rung 3

# eps AS RUN (printed values, per my c28 eps-truncation self-catch), u = m2 cycle-21 committed .out
RUN = [("0.001", "0.05150723818940063653522997"),
       ("0.0011239031932557", "0.05461458474016286082927124"),
       ("0.002", "0.07294509283746563691152741"),
       ("0.0035", "0.09670183421043065840984313"),
       ("0.006", "0.1270603431867589315365682"),
       ("0.0082667603361", "0.149621445957808028913411"),
       ("0.012", "0.1812222345972055203851323"),
       ("0.02", "0.236627035028954718936398"),
       ("0.035", "0.3197940308419042261822956"),
       ("0.06", "0.434057465263706265691976"),
       ("0.1", "0.5942792183051371124814878")]


def fit_normal(E, R, K):
    """the PUBLISHED estimator: normal equations in the raw variable eps."""
    n = K + 1
    M = mp.matrix(n, n)
    rhs = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            M[i, j] = sum(x ** (i + j) for x in E)
        rhs[i] = sum(y * x ** i for x, y in zip(E, R))
    c = mp.lu_solve(M, rhs)
    rr = [y - sum(c[k] * x ** k for k in range(n)) for x, y in zip(E, R)]
    return [c[k] for k in range(n)], max(abs(t) for t in rr)


def fit_qr_scaled(E, R, K):
    """same model, conditioned estimator: QR least squares on t = eps/eps_max."""
    n = K + 1
    s = max(E)
    T = [x / s for x in E]
    Amat = mp.matrix(len(E), n)
    for r, t in enumerate(T):
        for j in range(n):
            Amat[r, j] = t ** j
    bvec = mp.matrix(R)
    c, _ = mp.qr_solve(Amat, bvec)
    cs = [c[k] / s ** k for k in range(n)]                      # back to eps basis
    rr = [y - sum(cs[k] * x ** k for k in range(n)) for x, y in zip(E, R)]
    return cs, max(abs(t) for t in rr)


def build(rows, a, b, du_rel=None):
    E = [mp.mpf(x) for x, _ in rows]
    U = [mp.mpf(y) for _, y in rows]
    if du_rel is not None:
        U = [u * (1 + mp.mpf(du_rel)) for u in U]
    R = [(u ** 2 - a * e + b * e ** 2) / e ** 3 for e, u in zip(E, U)]
    return E, R


def table(tag, dps, aS, bS, fitter):
    mp.dps = dps
    a, b = mp.mpf(aS), mp.mpf(bS)
    E, R = build(RUN, a, b)
    out = []
    for K in (5, 6, 7, 8):
        c, res = fitter(E, R, K)
        out.append((K, c[0], res))
    print("\n--- %s | dps=%d | %s ---" % (tag, dps, fitter.__name__))
    print("%-3s %-24s %-11s" % ("K", "a3", "max resid"))
    for K, a3, res in out:
        print("%-3d %-24s %-11s" % (K, mp.nstr(a3, 18), mp.nstr(res, 3)))
    return out


print("=" * 78)
print("E1/E2  registered (16/12 d) vs m1-L164 rung-3 (19/21 d) constants, PUBLISHED estimator")
print("=" * 78)
reg50 = table("registered a,b", 50, A_REG, B_REG, fit_normal)
u1250 = table("U1/U2 a,b", 50, A_U1, B_U2, fit_normal)

print("\n" + "=" * 78)
print("E3  WORKING-PRECISION SWEEP -- does the published estimator's answer depend on dps?")
print("=" * 78)
for dps in (50, 80, 150, 300):
    table("registered a,b", dps, A_REG, B_REG, fit_normal)

print("\n" + "=" * 78)
print("E4  CONDITIONED ESTIMATOR (QR on scaled Vandermonde), same model, same data")
print("=" * 78)
for dps in (50, 300):
    table("registered a,b", dps, A_REG, B_REG, fit_qr_scaled)
    table("U1/U2 a,b", dps, A_U1, B_U2, fit_qr_scaled)

print("\n" + "=" * 78)
print("E5  SENSITIVITY d a3 / d|b|  (measured, both estimators, dps=300)")
print("=" * 78)
mp.dps = 300
for fitter in (fit_normal, fit_qr_scaled):
    for K in (6, 7, 8):
        base = mp.mpf(B_REG)
        for db in ("1e-13", "1e-12"):
            E0, R0 = build(RUN, mp.mpf(A_REG), base)
            E1, R1 = build(RUN, mp.mpf(A_REG), base - mp.mpf(db))   # |b| larger by db
            c0, _ = fitter(E0, R0, K)
            c1, _ = fitter(E1, R1, K)
            print("%-14s K=%d  d|b|=%s -> d a3 = %-12s  ratio %s"
                  % (fitter.__name__, K, db, mp.nstr(c1[0] - c0[0], 4),
                     mp.nstr((c1[0] - c0[0]) / mp.mpf(db), 4)))

print("\n" + "=" * 78)
print("E6  IS a3 u-LIMITED?  perturb every u by 1e-25 relative (my print floor / m1's 2.35e-25)")
print("=" * 78)
mp.dps = 300
for K in (6, 7, 8):
    E0, R0 = build(RUN, mp.mpf(A_REG), mp.mpf(B_REG))
    E1, R1 = build(RUN, mp.mpf(A_REG), mp.mpf(B_REG), du_rel="1e-25")
    c0, _ = fit_qr_scaled(E0, R0, K)
    c1, _ = fit_qr_scaled(E1, R1, K)
    print("K=%d  d a3 from du/u = 1e-25 : %s" % (K, mp.nstr(abs(c1[0] - c0[0]), 4)))

print("\n" + "=" * 78)
print("E7  CROSS-ROUTE AGREEMENT |a3^BL - a3^kappa|, a3^kappa = %s" % A3_KAPPA)
print("=" * 78)
mp.dps = 300
kap = mp.mpf(A3_KAPPA)
for tag, aS, bS in (("registered", A_REG, B_REG), ("U1/U2", A_U1, B_U2)):
    for fitter in (fit_normal, fit_qr_scaled):
        E, R = build(RUN, mp.mpf(aS), mp.mpf(bS))
        vals = []
        for K in (6, 7, 8):
            c, _ = fitter(E, R, K)
            vals.append(c[0])
        spread = max(vals) - min(vals)
        mid = sum(vals) / 3
        print("%-11s %-14s K=6..8 mid %s  spread %-10s  |mid-kappa| %s"
              % (tag, fitter.__name__, mp.nstr(mid, 18), mp.nstr(spread, 3),
                 mp.nstr(abs(mid - kap), 4)))
