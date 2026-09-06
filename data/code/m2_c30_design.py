"""machine2 CYCLE 30 -- DESIGN COLUMN for the denser small-epsilon ladder.

Uses ONLY already-published data:
  - m1-L165 sect9a full-precision (dps-50) u column, 11 rows, the eps values being the
    exact grid literals of heat72_birth_locus.py  (granted ASK from our da0a601 Part A)
  - the operative constants of m1-L165 bookkeeping (L164 sect5 as corrected by the #120 erratum):
        a = 2.645521411811664489        (19 s.f.)
        |b| = 7.4624528767937415788     (20 s.f.)
No new rung is computed here.  This file exists to FORM the predictions; it is run BEFORE
the prereg is frozen and its outputs are the design column.

Model (m1's heat72 birth-locus reformulation, adopted by m1 at L141):
        u(eps)^2 = (a - b*eps)*eps + a3*eps^3 + a4*eps^4 + a5*eps^5 + ...
    <=> r(eps) := (u^2 - a*eps + b*eps^2) / eps^3  =  a3 + a4*eps + a5*eps^2 + ...
so r is fitted by a polynomial of degree K in eps; a3 is the intercept.
"""
from mpmath import mp

mp.dps = 60

A = mp.mpf("2.645521411811664489")
B = -mp.mpf("7.4624528767937415788")
A_OLD = mp.mpf("2.645521411811663")
B_OLD = -mp.mpf("7.46245287679")

# m1-L165 sect9a table: (eps grid literal, u at dps 50)
L165_9A = [
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


def r_of(eps, u, a=A, b=B):
    return (u ** 2 - a * eps + b * eps ** 2) / eps ** 3


def polyfit(xs, ys, K):
    """Least squares fit of degree-K polynomial, normal equations in mp arithmetic."""
    n = K + 1
    M = mp.matrix(n, n)
    v = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            M[i, j] = mp.fsum([x ** (i + j) for x in xs])
        v[i] = mp.fsum([y * x ** i for x, y in zip(xs, ys)])
    c = mp.lu_solve(M, v)
    return [c[i] for i in range(n)]


def polyval(c, x):
    s = mp.mpf(0)
    for i in reversed(range(len(c))):
        s = s * x + c[i]
    return s


def loo_rms(xs, ys, K):
    """Leave-one-out rms, interior points only (endpoints excluded: extrapolation, not LOO)."""
    errs = []
    for i in range(1, len(xs) - 1):
        xr = xs[:i] + xs[i + 1:]
        yr = ys[:i] + ys[i + 1:]
        c = polyfit(xr, yr, K)
        errs.append(polyval(c, xs[i]) - ys[i])
    return mp.sqrt(mp.fsum([e ** 2 for e in errs]) / len(errs))


def maxres(xs, ys, K):
    c = polyfit(xs, ys, K)
    return max(abs(polyval(c, x) - y) for x, y in zip(xs, ys)), c


if __name__ == "__main__":
    E = [mp.mpf(e) for e, _ in L165_9A]
    U = [mp.mpf(u) for _, u in L165_9A]
    R = [r_of(e, u) for e, u in zip(E, U)]

    print("=== A. r on the 11 published rungs, OPERATIVE constants (a 19 s.f., |b| 20 s.f.) ===")
    for e, r in zip(E, R):
        print("  eps=%-22s r=%s" % (mp.nstr(e, 18), mp.nstr(r, 24)))

    print()
    print("=== B. LOO order selection on the 11 published rungs ===")
    print("  %-4s %-16s %-16s" % ("K", "max in-sample res", "interior LOO rms"))
    best, bestK = None, None
    for K in range(3, 9):
        mr, _ = maxres(E, R, K)
        lo = loo_rms(E, R, K)
        print("  %-4d %-16s %-16s" % (K, mp.nstr(mr, 6), mp.nstr(lo, 6)))
        if best is None or lo < best:
            best, bestK = lo, K
    print("  LOO-optimal K = %d   (LOO rms %s)" % (bestK, mp.nstr(best, 6)))

    cK = polyfit(E, R, bestK)
    print("  a3 (intercept, K=%d) = %s" % (bestK, mp.nstr(cK[0], 20)))
    print("  a4 = %s   a5 = %s" % (mp.nstr(cK[1], 12), mp.nstr(cK[2], 12)))

    print()
    print("=== C. INPUT-PRECISION BUDGET: dr/da = -1/eps^2 , dr/db = +1/eps ===")
    print("  half-ulp(a operative, 19 s.f.) = 5e-19 ; half-ulp(|b| operative, 20 s.f.) = 5e-19")
    print("  DEFICIT of the 12-digit b lineage (m1-L165 sect9a, delta_b ~ -3.7e-12):")
    print("    b_operative - b_12digit = %s" % mp.nstr(B - B_OLD, 8))
    print("    a_operative - a_16digit = %s" % mp.nstr(A - A_OLD, 8))
    print()
    print("  %-12s %-14s %-14s %-14s %-14s" % ("eps", "dr|da(5e-19)", "dr|db(5e-19)",
                                               "dr from b_12dig", "dr from a_16dig"))
    for es in ["0.1", "0.001", "0.00075", "0.0005", "0.00033", "0.00022", "0.00015",
               "0.0001", "0.00005", "0.00002", "0.00001"]:
        e = mp.mpf(es)
        print("  %-12s %-14s %-14s %-14s %-14s" % (
            es,
            mp.nstr(mp.mpf("5e-19") / e ** 2, 5),
            mp.nstr(mp.mpf("5e-19") / e, 5),
            mp.nstr(abs(B - B_OLD) / e, 5),
            mp.nstr(abs(A - A_OLD) / e ** 2, 5)))

    print()
    print("=== D. EXTRAPOLATION of the K=%d fit to the proposed new rungs ===" % bestK)
    NEW = ["0.0001", "0.00015", "0.00022", "0.00033", "0.0005", "0.00075"]
    for es in NEW:
        e = mp.mpf(es)
        print("  eps=%-10s r_pred=%s   u_pred=%s" % (
            es, mp.nstr(polyval(cK, e), 18),
            mp.nstr(mp.sqrt((A - B * e) * e + polyval(cK, e) * e ** 3), 18)))
