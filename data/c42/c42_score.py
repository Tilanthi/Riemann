#!/usr/bin/env python3
"""c42_score.py — the instrument that scores the table: fits, the decimal-slip discriminator,
   the epsilon(x) law, the truncation sensitivity. Runs against the shipped table, not against
   anything typed by hand."""
import json, glob
from mpmath import mp, mpmathify, log10, mpf, exp, pi, log

mp.dps = 40
T = json.load(open("c42_convergence_in_x.json"))
rows = T['rows']
pub = [mpmathify(r['pub']) for r in rows]
o13 = [mpmathify(r['d13']) for r in rows]
o11 = [mpmathify(r['d11']) for r in rows]
o7 = [mpmathify(r['d7']) for r in rows]


def fit(y):
    """least squares log10(y_n) = A + B n over n=1..len(y); returns A,B,residuals"""
    n = len(y)
    xs = [mpf(i + 1) for i in range(n)]
    ys = [log10(v) for v in y]
    mx = sum(xs) / n
    my = sum(ys) / n
    B = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / sum((xs[i] - mx) ** 2 for i in range(n))
    A = my - B * mx
    res = [ys[i] - (A + B * xs[i]) for i in range(n)]
    return A, B, res


print("== THE DECIMAL-SLIP DISCRIMINATOR (published x=13 column vs ours)")
sci = [i for i in range(50) if "e-" in rows[i]['pub'] or "E" in rows[i]['pub']]
dec = [i for i in range(50) if i not in sci]
bad = [i for i in range(50) if abs(o13[i] / pub[i] - 1) > mpf("0.001")]
print("  rows printed in scientific notation : %d, of which discrepant: %d"
      % (len(sci), len([i for i in bad if i in sci])))
print("  rows printed in decimal notation    : %d, of which discrepant: %d  -> n = %s"
      % (len(dec), len([i for i in bad if i in dec]), [i + 1 for i in bad]))
for i in bad:
    print("     n=%2d published %-12s ours %-16s ratio ours/pub = %s"
          % (i + 1, rows[i]['pub'], rows[i]['d13'], mp.nstr(o13[i] / pub[i], 9)))
rep = list(pub)
for i in bad:
    rep[i] = pub[i] / 10
print("  repaired column = published with those %d entries divided by exactly 10" % len(bad))

print("\n== MONOTONICITY (a step is non-monotone if d_{n+1} <= d_n)")
for name, col in (("published (as printed)", pub), ("published (repaired)", rep), ("ours x=13", o13),
                  ("ours x=11", o11), ("ours x=7", o7)):
    nm = [i + 1 for i in range(49) if col[i + 1] <= col[i]]
    print("  %-24s %d / 49   at n = %s" % (name, len(nm), nm))

print("\n== LOG-LINEAR REACH FIT  log10 d_n = A + B n   (n = 1..50)")
for name, col in (("published (as printed)", pub), ("published (repaired)", rep), ("ours x=13", o13),
                  ("ours x=11", o11), ("ours x=7", o7)):
    A, B, res = fit(col)
    rms = (sum(r ** 2 for r in res) / len(res)) ** mpf("0.5")
    print("  %-24s A=%s  B=%s  rms=%s  resid(n=48)=%s  max|resid|=%s at n=%d"
          % (name, mp.nstr(A, 8), mp.nstr(B, 8), mp.nstr(rms, 5), mp.nstr(res[47], 5),
             mp.nstr(max(abs(r) for r in res), 5),
             1 + max(range(50), key=lambda i: abs(res[i]))))

print("\n== CONVERGENCE IN x  (this is the deliverable's headline)")
for n in (1, 5, 10, 20, 30, 40, 50):
    i = n - 1
    print("  n=%2d  x=7 %-15s x=11 %-15s x=13 %-15s | decades 7->11 %s, 11->13 %s"
          % (n, rows[i]['d7'], rows[i]['d11'], rows[i]['d13'],
             mp.nstr(log10(o7[i] / o11[i]), 5), mp.nstr(log10(o11[i] / o13[i]), 5)))

print("\n== lambda_min(x) AGAINST THE LETTER'S OWN EXPONENT  -4 pi e^L + (9/2) L,  e^L = x")
lm = {int(k): mpmathify(v) for k, v in T['lambda_min'].items()}
for x in sorted(lm):
    xx = mpf(x)
    pred_exp = (-4 * pi * xx + mpf(9) / 2 * log(xx)) / log(10)
    print("  x=%2d  lambda_min=%s  log10=%s  log10 - (exponent/ln10) = %s"
          % (x, mp.nstr(lm[x], 12), mp.nstr(log10(lm[x]), 8), mp.nstr(log10(lm[x]) - pred_exp, 8)))
xs = sorted(lm)
for a, b in ((xs[0], xs[1]), (xs[1], xs[2])):
    meas = (log10(lm[b]) - log10(lm[a])) / (b - a)
    mid = mpf(a + b) / 2
    pred = (-4 * pi + mpf(9) / (2 * mid)) / log(10)
    print("  slope d log10 lambda / dx on [%d,%d] : measured %s, letter's exponent at midpoint %s, "
          "rel diff %s" % (a, b, mp.nstr(meas, 8), mp.nstr(pred, 8), mp.nstr(abs(meas / pred - 1), 3)))

print("\n== TRUNCATION SENSITIVITY N=100 -> N=140 (same x, same dps, same quadrature)")
for x in (7, 11, 13):
    a = json.load(open(glob.glob("c42_x%d_N100_dps150_g9_*.json" % x)[0]))
    b = json.load(open(glob.glob("c42_x%d_N140_dps150_g9_*.json" % x)[0]))
    r1 = mpmathify(b['rows'][0]['diff_nearest']) / mpmathify(a['rows'][0]['diff_nearest'])
    r50 = mpmathify(b['rows'][49]['diff_nearest']) / mpmathify(a['rows'][49]['diff_nearest'])
    rl = mpmathify(b['lambda_min']) / mpmathify(a['lambda_min'])
    offs_same = all(a['rows'][i]['offset'] == b['rows'][i]['offset'] for i in range(50))
    print("  x=%2d  d_1 x%s   d_50 x%s   lambda_min x%s   |  d_1/lambda ratio agree to %s  |  "
          "index offsets identical at all 50 n: %s"
          % (x, mp.nstr(r1, 6), mp.nstr(r50, 6), mp.nstr(rl, 6), mp.nstr(abs(r1 / rl - 1), 3), offs_same))

print("\n== SUPPORT LENGTH vs PRIME CONTENT (x=13 -> x=15 adds NO new prime power)")
T2 = json.load(open("c42_convergence_in_x.json"))
XS = T2['xs']
for i in range(len(XS) - 1):
    a, b = XS[i], XS[i + 1]
    pa, pb = set(T2['prime_powers'][str(a)]), set(T2['prime_powers'][str(b)])
    d_a = mpmathify(T2['rows'][0]['d%d' % a]); d_b = mpmathify(T2['rows'][0]['d%d' % b])
    gain = log10(d_a / d_b)
    print("  x %2d -> %2d : new prime powers %-12s | d_1 gain %s decades, %s decades per unit x"
          % (a, b, sorted(pb - pa) if pb - pa else "NONE", mp.nstr(gain, 6), mp.nstr(gain / (b - a), 6)))

print("\n== INDEX REACH (first n where the n-th approximant stops being nearest to gamma_n)")
for x in XS:
    fo = next((r['n'] for r in T2['rows'] if r['off%d' % x] != 0), None)
    g = T2['rows'][(fo - 2) if fo else 49]['gamma'][:12]
    print("  x=%2d  reach = %s zeros tracked   (last tracked gamma ~ %s)  lambda_min=%s"
          % (x, (fo - 1) if fo else ">=50", g, T2['lambda_min'][str(x)]))
