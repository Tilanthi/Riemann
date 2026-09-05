"""machine2 CYCLE 28, leg 2 -- INDEPENDENCE AUDIT of m1-L163 sect3/sect6's claim that
"Three constructions (identity, contour, birth-locus intercept) now meet at 11.70072" and that the
intercept is "the fourth leg of over-determination".

ESTIMATOR DECLARED BEFORE RUNNING (no prereg letter; this is an audit of a published claim, and the
numeric part is labelled POST-HOC exploration where it produces a value):
    fit  r(eps) = sum_{k=0..K} c_k eps^k   for K = 1,2,3,4   on m1-L163 sect2's ELEVEN published
    r(eps) points, by exact least squares at dps 50; the reported quantity is c_0.
    CERTIFICATE = stability of c_0 under increasing K and under dropping the largest eps
    (my own standing rule: the certificate is stability under refinement, never any single reading).
Cross-check: does m1's own grid reproduce a4 = 20.4755 and a5 ~ 18.3, the constants m2 published in
cycle 21 (machine2-cycle21-birth-locus-scored-and-identity-gap-refereed.md, line 121)?

DATA: m1-L163 sect2 r-table, transcribed from the letter at d853a1e.  u is carried too so the
transcription can be checked against r = (u^2 - (a - b*eps)*eps)/eps^3 if a, b are wanted.
"""
from mpmath import mp

mp.dps = 50

# eps, u, r(eps)  -- m1-L163 section 2, verbatim
TAB = [
    ("0.001",     "0.051507238189400637", "11.721211198"),
    ("0.0011239", "0.054614584740162861", "11.723753018"),
    ("0.002",     "0.072945092837465637", "11.741741999"),
    ("0.0035",    "0.096701834210430658", "11.772608283"),
    ("0.006",     "0.127060343186758932", "11.824242141"),
    ("0.0082668", "0.149621445957808029", "11.871268385"),
    ("0.012",     "0.181222234597205520", "11.949164587"),
    ("0.02",      "0.236627035028954719", "12.118039956"),
    ("0.035",     "0.319794030841904226", "12.442401741"),
    ("0.06",      "0.434057465263706266", "13.008185583"),
    ("0.1",       "0.594279218305137112", "13.991119360"),
]
E = [mp.mpf(t[0]) for t in TAB]
R = [mp.mpf(t[2]) for t in TAB]

A3_BL = mp.mpf("11.7007174")        # m2 cycle 21, deg-5 fit on m2's own run of the same ladder
A3_KAPPA = mp.mpf("11.700717320435114")   # m1-L161 heat72w final rung (contour route)
A4_BL = mp.mpf("20.4755")
A5_BL = mp.mpf("18.3")


def polyfit(xs, ys, K):
    n = K + 1
    A = mp.matrix(n, n); rhs = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            A[i, j] = sum(x ** (i + j) for x in xs)
        rhs[i] = sum(y * x ** i for x, y in zip(xs, ys))
    c = mp.lu_solve(A, rhs)
    resid = max(abs(y - sum(c[k] * x ** k for k in range(n))) for x, y in zip(xs, ys))
    return [c[k] for k in range(n)], resid


print("=== c_0 (the intercept) from m1's OWN eleven published r values, m2's estimator ===")
print("%-3s %-6s %-24s %-12s %-12s %-11s" % ("K", "npts", "c_0", "c_1 (a4?)", "c_2 (a5?)", "max resid"))
rows = []
for drop in (0, 1, 2, 3):
    xs = E[:len(E) - drop]; ys = R[:len(R) - drop]
    for K in (1, 2, 3, 4):
        if K + 1 > len(xs):
            continue
        c, res = polyfit(xs, ys, K)
        rows.append((K, len(xs), c, res))
        print("%-3d %-6d %-24s %-12s %-12s %-11s" %
              (K, len(xs), mp.nstr(c[0], 12),
               mp.nstr(c[1], 6) if len(c) > 1 else "-",
               mp.nstr(c[2], 6) if len(c) > 2 else "-",
               mp.nstr(res, 3)))

best = [r for r in rows if r[0] >= 3 and r[1] == 11]
print("\n=== against the two values already on record ===")
for K, n, c, res in rows:
    if n == 11 and K >= 2:
        d_bl = abs(c[0] - A3_BL) / A3_BL
        d_ka = abs(c[0] - A3_KAPPA) / A3_KAPPA
        print("K=%d n=11: c_0 = %s   rel vs a3^BL(m2, c21) %s   rel vs a3^kappa(m1-L161) %s" %
              (K, mp.nstr(c[0], 12), mp.nstr(d_bl, 4), mp.nstr(d_ka, 4)))

print("\n=== m1-L163's own two linear reads, recomputed from his table (transcription check) ===")
for npts in (3, 5, 11):
    c, res = polyfit(E[:npts], R[:npts], 1)
    print("linear, %2d smallest: c_0 = %s  slope %s   (L163 quotes %s)" %
          (npts, mp.nstr(c[0], 12), mp.nstr(c[1], 8),
           {3: "11.700678560 / 20.532", 5: "11.700566955 / 20.605",
            11: "11.683015 / 22.703"}[npts]))

print("\n=== does m1's grid reproduce m2's PUBLISHED a4, a5 (cycle 21)? ===")
c, res = polyfit(E, R, 4)
print("K=4, all 11: a3 %s  a4 %s  a5 %s  a6 %s  a7 %s  resid %s" %
      tuple([mp.nstr(c[k], 8) for k in range(5)] + [mp.nstr(res, 3)]))
print("m2 c21 published: a3 11.7007174, a4 20.4755, a5 ~18.3")
print("rel dev a4 %s   rel dev a5 %s" %
      (mp.nstr(abs(c[1] - A4_BL) / A4_BL, 4), mp.nstr(abs(c[2] - A5_BL) / A5_BL, 4)))
