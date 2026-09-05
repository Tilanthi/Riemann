"""m2 response to m1-L164 leg 2, part B: WHICH constant moved a3?

m1-L164 sec.5 attributes the ~7e-9 move of a3^BL to b: "the b-sensitivity (delta a3/delta|b| ~ 1.9e3)
dominates it".  Both constants changed between the registered pair and the rung-3 pair, so the
attribution is a two-variable claim tested with one variable.  Decompose it.

  registered:  a = 2.645521411811663        |b| = 7.46245287679
  rung 3   :   a = 2.645521411811664489     |b| = 7.4624528767937415788
  delta a  = +1.489e-15   (one ulp of the 16-digit a, as m1 notes)
  delta|b| = +3.7415788e-13

Also: what limits a3 AFTER a and b are exact -- input precision, or the truncated model?
That decides whether m1's offered >21-digit re-computation can buy the 10th figure.
"""
from mpmath import mp

mp.dps = 300

A_REG = mp.mpf("2.645521411811663")
B_REG = mp.mpf("-7.46245287679")
A_U1 = mp.mpf("2.645521411811664489")
B_U2 = mp.mpf("-7.4624528767937415788")

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
E = [mp.mpf(x) for x, _ in RUN]
U = [mp.mpf(y) for _, y in RUN]


def fit(a, b, K):
    R = [(u ** 2 - a * e + b * e ** 2) / e ** 3 for e, u in zip(E, U)]
    n = K + 1
    M = mp.matrix(n, n)
    rhs = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            M[i, j] = sum(x ** (i + j) for x in E)
        rhs[i] = sum(y * x ** i for x, y in zip(E, R))
    c = mp.lu_solve(M, rhs)
    rr = [y - sum(c[k] * x ** k for k in range(n)) for x, y in zip(E, R)]
    return c[0], max(abs(t) for t in rr)


print("=" * 84)
print("E8  DECOMPOSITION of the registered -> rung-3 move of a3, per K")
print("=" * 84)
print("%-3s %-14s %-14s %-14s %-14s" % ("K", "d a3 (a only)", "d a3 (b only)", "d a3 (both)", "sum of parts"))
for K in (6, 7, 8):
    base, _ = fit(A_REG, B_REG, K)
    da, _ = fit(A_U1, B_REG, K)
    db, _ = fit(A_REG, B_U2, K)
    both, _ = fit(A_U1, B_U2, K)
    print("%-3d %-14s %-14s %-14s %-14s" % (
        K, mp.nstr(da - base, 4), mp.nstr(db - base, 4),
        mp.nstr(both - base, 4), mp.nstr((da - base) + (db - base), 4)))

print("\n" + "=" * 84)
print("E9  SENSITIVITIES per K:  d a3/da  and  d a3/d|b|  (measured, linear regime confirmed)")
print("=" * 84)
h_a = mp.mpf("1e-16")
h_b = mp.mpf("1e-13")
sens = {}
for K in (5, 6, 7, 8):
    b0, _ = fit(A_REG, B_REG, K)
    ba, _ = fit(A_REG + h_a, B_REG, K)
    bb, _ = fit(A_REG, B_REG - h_b, K)     # |b| larger by h_b
    sa = (ba - b0) / h_a
    sb = (bb - b0) / h_b
    sens[K] = (sa, sb)
    print("K=%d   d a3/da = %-12s   d a3/d|b| = %-12s   ratio |da/db| = %s"
          % (K, mp.nstr(sa, 5), mp.nstr(sb, 5), mp.nstr(abs(sa / sb), 4)))

print("\n" + "=" * 84)
print("E10 ERROR BUDGET for a3^BL under the rung-3 constants and their published guards")
print("     guards from m1-L164 sec.5:  a guard 5.61e-16,  |b| guard 5.01e-13")
print("=" * 84)
ga = mp.mpf("5.61e-16")
gb = mp.mpf("5.01e-13")
vals = {}
for K in (6, 7, 8):
    v, res = fit(A_U1, B_U2, K)
    vals[K] = v
    sa, sb = sens[K]
    ea = abs(sa) * ga
    eb = abs(sb) * gb
    print("K=%d  a3 = %s   from-a %-11s  from-b %-11s  input total %-11s  maxresid %s"
          % (K, mp.nstr(v, 18), mp.nstr(ea, 3), mp.nstr(eb, 3), mp.nstr(ea + eb, 3), mp.nstr(res, 3)))
spread = max(vals.values()) - min(vals.values())
print("\nK=6..8 model spread (m1's +/-4e-9 bar, and my +/-5e-10 bar, are BOTH this construction):")
print("   spread = %s   mid = %s" % (mp.nstr(spread, 4), mp.nstr(sum(vals.values()) / 3, 18)))

print("\n" + "=" * 84)
print("E11 WOULD >21-DIGIT a,b BUY THE 10th FIGURE?  set the constants EXACT-in-model and refit")
print("     (surrogate: perturb a,b by 1e-25 -- i.e. constants effectively infinitely precise)")
print("=" * 84)
v6, _ = fit(A_U1, B_U2, 6)
v6p, _ = fit(A_U1 * (1 + mp.mpf("1e-25")), B_U2 * (1 + mp.mpf("1e-25")), 6)
print("residual constants-induced motion at 25-digit a,b:  %s" % mp.nstr(abs(v6p - v6), 4))
print("K-model spread that REMAINS regardless:              %s" % mp.nstr(spread, 4))
print("10th significant figure of a3 = unit in the          1e-9 place")

print("\n" + "=" * 84)
print("E12 SIGNIFICANT FIGURES that survive BOTH constant sets (K=6..8 mid of each)")
print("=" * 84)
mids = {}
for tag, a, b in (("registered", A_REG, B_REG), ("rung3", A_U1, B_U2)):
    vs = [fit(a, b, K)[0] for K in (6, 7, 8)]
    mids[tag] = sum(vs) / 3
    print("%-11s mid = %s" % (tag, mp.nstr(mids[tag], 18)))
for sf in (8, 9, 10, 11):
    r1 = mp.nstr(mids["registered"], sf)
    r2 = mp.nstr(mids["rung3"], sf)
    print("  %2d s.f.:  registered %-14s  rung3 %-14s  %s" % (sf, r1, r2, "AGREE" if r1 == r2 else "DISAGREE"))
