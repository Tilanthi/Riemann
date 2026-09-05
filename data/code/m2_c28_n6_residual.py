"""machine2 CYCLE 28, leg 3 -- what would actually GRADUATE N6, and can it be measured today?

N6's register criterion (nursery/REGISTER.md, m1's directive letter): "if the locus carries
structure the constants do not predict, N6 graduates to a lane"; "Dies honestly if the a/k/b
operative constants predict the locus."

m1-L163 graduates N6 on two clauses.  Clause 2 is "r(eps) is NOT constant".  But r is not supposed
to be constant: m2 cycle 21 (5f7afe2) measured u^2 = (a - b*eps)*eps + a3*eps^3 + a4*eps^4 +
a5*eps^5 with residual 3.0e-8 over 11 points, and m1 ADOPTED that reformulation at L141 (4c5da84).
So the graduating observable is not the drift -- it is the RESIDUAL of the expansion.  This file
asks whether that residual is measurable at all today.

r(eps) = (u^2 - a*eps + b*eps^2)/eps^3, so
    dr/da = -1/eps^2      dr/db = +1/eps
and the operative constants are published to FINITE precision:
    a = 2.645521411811663      (16 s.f.)
    b = -7.46245287679         (12 s.f.)
Uses m2's own cycle-21 u values (data/machine2_cycle21_birth_locus.out, 25+ digits each, own
1-D real root find on the critical line), NOT the 12-s.f. printed r table.
"""
from mpmath import mp

mp.dps = 50

A = mp.mpf("2.645521411811663")
B = mp.mpf("-7.46245287679")
DA = mp.mpf("5e-16")      # half-ulp of the published a
DB = mp.mpf("5e-12")      # half-ulp of the published b

# eps (exact grid value), u  -- m2 cycle-21 committed .out, lines 43-53
DAT = [
    ("0.001",                "0.05150723818940063653522997"),
    ("0.001123903193255665747441", "0.05461458474016286082927124"),
    ("0.002",                "0.07294509283746563691152741"),
    ("0.0035",               "0.09670183421043065840984313"),
    ("0.006",                "0.1270603431867589315365682"),
    ("0.008266760336112808604584", "0.149621445957808028913411"),
    ("0.012",                "0.1812222345972055203851323"),
    ("0.02",                 "0.236627035028954718936398"),
    ("0.035",                "0.3197940308419042261822956"),
    ("0.06",                 "0.434057465263706265691976"),
    ("0.1",                  "0.5942792183051371124814878"),
]
E = [mp.mpf(a) for a, _ in DAT]
U = [mp.mpf(b) for _, b in DAT]
R = [(u ** 2 - A * e + B * e ** 2) / e ** 3 for e, u in zip(E, U)]

print("=== per-point uncertainty of r induced by the PUBLISHED digits of a and b ===")
print("%-26s %-20s %-11s %-11s %-11s" % ("eps", "r (full precision)", "d r|da", "d r|db", "total"))
for e, r in zip(E, R):
    da = DA / e ** 2
    db = DB / e
    print("%-26s %-20s %-11s %-11s %-11s" %
          (mp.nstr(e, 8), mp.nstr(r, 16), mp.nstr(da, 3), mp.nstr(db, 3), mp.nstr(da + db, 3)))


def fit(xs, ys, K):
    n = K + 1
    M = mp.matrix(n, n); rhs = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            M[i, j] = sum(x ** (i + j) for x in xs)
        rhs[i] = sum(y * x ** i for x, y in zip(xs, ys))
    c = mp.lu_solve(M, rhs)
    res = max(abs(y - sum(c[k] * x ** k for k in range(n))) for x, y in zip(xs, ys))
    return [c[k] for k in range(n)], res


print("\n=== residual ladder on m2's full-precision r (11 points) ===")
print("%-4s %-20s %-12s %-12s %-11s" % ("K", "a3 = c_0", "a4 = c_1", "a5 = c_2", "max resid"))
for K in range(2, 9):
    c, res = fit(E, R, K)
    print("%-4d %-20s %-12s %-12s %-11s" %
          (K, mp.nstr(c[0], 14), mp.nstr(c[1], 8), mp.nstr(c[2], 8) if len(c) > 2 else "-",
           mp.nstr(res, 3)))

print("\n=== the same ladder with a and b PERTURBED by one published half-ulp ===")
for name, aa, bb in (("a + 5e-16", A + DA, B), ("b + 5e-12", A, B + DB)):
    R2 = [(u ** 2 - aa * e + bb * e ** 2) / e ** 3 for e, u in zip(E, U)]
    c0, _ = fit(E, R, 5)
    c1, r1 = fit(E, R2, 5)
    print("%-12s  a3 moves %s   (K=5 residual %s)" %
          (name, mp.nstr(abs(c1[0] - c0[0]), 4), mp.nstr(r1, 3)))
