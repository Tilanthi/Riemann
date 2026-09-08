#!/usr/bin/env python3
"""POST-HOC, UNREGISTERED, EXPLORATORY (labelled as such wherever reported).

Question the registered arms do not answer: is the STABILITY of the gap a property of the
object, or of the 1/N model? Compare three extrapolation models on the same ladder:
  M1 Richardson 1/N      lam_inf = (Nb*lb - Na*la)/(Nb-Na)
  M2 Richardson 1/N^2    lam_inf = (Nb^2*lb - Na^2*la)/(Nb^2-Na^2)
  M3 Aitken Delta^2 (geometric) on consecutive triples
and report, for each, the spread of lam_inf itself vs the spread of the GAP.
"""
import json, glob, os
import mpmath as mp
mp.mp.dps = 60

cells = {}
for d in ('/shared/rh-exchange-repo/Riemann/data/c46', '/workspace/rh/c47/mine/data/c46'):
    for fn in glob.glob(os.path.join(d, 'c46_*_x13_N*_dps150_g9_it16.json')):
        c = json.load(open(fn))
        if str(c['x']) == '13' and c['dps'] == 150:
            cells[(c['parity'], c['N'])] = mp.mpf(c['lambda_min'])
Ns = sorted({n for (_, n) in cells})
o = {n: cells[('odd', n)] for n in Ns}
e = {n: cells[('even', n)] for n in Ns}
print('rungs:', Ns)

def rich(p, Na, la, Nb, lb):
    A, B = mp.mpf(Na) ** p, mp.mpf(Nb) ** p
    return (B * lb - A * la) / (B - A)

def aitken(l0, l1, l2):
    d1, d2 = l1 - l0, l2 - l1
    return None if d2 - d1 == 0 else l2 - d2 * d2 / (d2 - d1)

for p, name in ((1, 'M1 Richardson 1/N'), (2, 'M2 Richardson 1/N^2')):
    oi, ei, gaps = [], [], []
    print('\n%s' % name)
    for i, a in enumerate(Ns):
        for b in Ns[i + 1:]:
            O, E = rich(p, a, o[a], b, o[b]), rich(p, a, e[a], b, e[b])
            if O <= 0 or E <= 0:
                print('   (%3d,%3d) unusable (nonpositive extrapolant)' % (a, b)); continue
            g = mp.log(O / E, 10)
            oi.append(O); ei.append(E); gaps.append(g)
            print('   (%3d,%3d) odd_inf=%s even_inf=%s gap=%s' % (a, b, mp.nstr(O, 8), mp.nstr(E, 8), mp.nstr(g, 8)))
    if gaps:
        print('   odd_inf spread : %s .. %s  (factor %s)' % (mp.nstr(min(oi), 6), mp.nstr(max(oi), 6), mp.nstr(max(oi)/min(oi), 4)))
        print('   even_inf spread: %s .. %s  (factor %s)' % (mp.nstr(min(ei), 6), mp.nstr(max(ei), 6), mp.nstr(max(ei)/min(ei), 4)))
        print('   GAP band       : [%s, %s] dex   width %s' % (mp.nstr(min(gaps), 8), mp.nstr(max(gaps), 8), mp.nstr(max(gaps)-min(gaps), 4)))
        g4 = [g for (i, a) in enumerate(Ns) for b in Ns[i+1:] for g in [] ]  # placeholder
    # restricted to m3's rung set
    sub = [n for n in Ns if n >= 100]
    gs = []
    for i, a in enumerate(sub):
        for b in sub[i + 1:]:
            O, E = rich(p, a, o[a], b, o[b]), rich(p, a, e[a], b, e[b])
            if O > 0 and E > 0:
                gs.append(mp.log(O / E, 10))
    if gs:
        print('   GAP band on m3 rung set {100,140,180,220} only: [%s, %s] width %s over %d pairs'
              % (mp.nstr(min(gs), 8), mp.nstr(max(gs), 8), mp.nstr(max(gs)-min(gs), 4), len(gs)))

print('\nM3 Aitken Delta^2 -- cross-model comparison of lam_inf and of the gap')
ao, ae = {}, {}
for i in range(len(Ns) - 2):
    t = Ns[i:i+3]
    a1, a2 = aitken(o[t[0]], o[t[1]], o[t[2]]), aitken(e[t[0]], e[t[1]], e[t[2]])
    ao[tuple(t)], ae[tuple(t)] = a1, a2
    print('   %s  odd_inf=%s  even_inf=%s' % (t, mp.nstr(a1, 8), mp.nstr(a2, 8)))
good_o = [v for v in ao.values() if 0 < v < o[Ns[-1]]]
good_e = [v for v in ae.values() if 0 < v < e[Ns[-1]]]
print('   usable odd Aitken values : %s' % [mp.nstr(v, 6) for v in good_o])
print('   usable even Aitken values: %s' % [mp.nstr(v, 6) for v in good_e])
if good_o and good_e:
    gs = [mp.log(x / y, 10) for x in good_o for y in good_e]
    print('   Aitken GAP band: [%s, %s] dex width %s over %d combinations'
          % (mp.nstr(min(gs), 8), mp.nstr(max(gs), 8), mp.nstr(max(gs)-min(gs), 4), len(gs)))
