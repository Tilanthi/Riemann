#!/usr/bin/env python3
"""R2/R3/R4 -- decay ratios, Aitken(Delta^2) and Richardson(1/N) on a parity ladder.

Runs on ANY value table, so the same instrument scores m3's published numbers and ours.
Usage:  c47_extrap.py m3 | ours | both
Every printed number is computed here from the lambda values in the table; nothing is copied
from m3's SUMMARY except the lambda values themselves (their derived columns are AUDITED
against this instrument, not trusted).
"""
import sys, json, glob, os
import mpmath as mp
mp.mp.dps = 60

# ---- m3's published ladder (letter185 / results/SUMMARY.md, commit 59b515a0), values only
M3_ODD = {
    100: '3.34107742032073965658213712601992236254413410378763387206214e-55',
    140: '2.8475156913393636771563703939938140057126090742267e-55',
    180: '2.698009778782749686608210255746078258440609181395e-55',
    220: '2.5322446138126329379067665416656277722374006147654e-55',
}
M3_EVEN = {
    100: '3.720899741667123935791434766094540694091e-59',
    140: '3.191618722904299187775878951533394940265e-59',
    180: '2.959706807240060045108126519806894301792e-59',
    220: '2.833656431009356898926062340578180078197e-59',
}

CELLDIR_PUB = '/shared/rh-exchange-repo/Riemann/data/c46'      # READ ONLY
CELLDIR_NEW = '/workspace/rh/c47/mine/data/c46'

def load_ours():
    odd, even = {}, {}
    for d in (CELLDIR_PUB, CELLDIR_NEW):
        for fn in glob.glob(os.path.join(d, 'c46_*_x13_N*_dps150_g9_it16.json')):
            c = json.load(open(fn))
            if str(c['x']) != '13' or c['dps'] != 150:
                continue
            (odd if c['parity'] == 'odd' else even)[c['N']] = c['lambda_min']
    return odd, even

def tomp(d):
    return {k: mp.mpf(v) for k, v in d.items()}

def ratios(lab, s):
    Ns = sorted(s)
    print('  %s ladder:' % lab)
    for n in Ns:
        print('     N=%-4d lambda=%s' % (n, mp.nstr(s[n], 20)))
    print('  %s decay ratios lambda(N_k)/lambda(N_{k-1}):' % lab)
    rs = []
    for a, b in zip(Ns, Ns[1:]):
        r = s[b] / s[a]
        rs.append((a, b, r))
        print('     %3d -> %3d : %s' % (a, b, mp.nstr(r, 8)))
    shape = []
    for i in range(1, len(rs)):
        shape.append('UP(re-accel of decay)' if rs[i][2] < rs[i-1][2] else 'DOWN(decel)')
    print('  %s shape of the ratio sequence: %s' % (lab, shape if shape else 'UNDEFINED (<3 rungs)'))
    if len(rs) < 3:
        print('     NOTE: %d ratio(s) only -- a re-acceleration needs >=3 ratios (>=4 rungs). '
              'With this ladder the question is UNMEASURABLE, not answered.' % len(rs))
    return rs

def aitken(l0, l1, l2):
    d1, d2 = l1 - l0, l2 - l1
    den = d2 - d1
    if den == 0:
        return None
    return l2 - d2 * d2 / den

def richardson(Na, la, Nb, lb):
    return (Nb * lb - Na * la) / (Nb - Na)

def report(name, odd, even):
    print('=' * 78)
    print('LADDER SOURCE: %s' % name)
    o, e = tomp(odd), tomp(even)
    ratios('ODD ', o)
    ratios('EVEN', e)

    Ns = sorted(set(o) & set(e))
    print('\n  finite-N gap log10(odd/even):')
    for n in Ns:
        print('     N=%-4d %s' % (n, mp.nstr(mp.log(o[n] / e[n], 10), 10)))

    print('\n  R3 Aitken(Delta^2) on consecutive triples (ratio = lam_inf / lam(first N)):')
    for lab, s in (('ODD ', o), ('EVEN', e)):
        Ss = sorted(s)
        for i in range(len(Ss) - 2):
            t = Ss[i:i+3]
            a = aitken(s[t[0]], s[t[1]], s[t[2]])
            if a is None:
                print('     %s %s : DEGENERATE denominator' % (lab, t)); continue
            r = a / s[t[0]]
            flag = 'NONSENSICAL (>=1: predicts an increasing tail)' if r >= 1 else \
                   ('NONSENSICAL (<=0)' if r <= 0 else 'usable')
            print('     %s %-15s lam_inf=%s  ratio_to_N%d=%s  %s'
                  % (lab, str(t), mp.nstr(a, 10), t[0], mp.nstr(r, 6), flag))

    print('\n  R4 Richardson(1/N) over matched pairs, and the extrapolated gap:')
    pairs = [(a, b) for i, a in enumerate(Ns) for b in Ns[i+1:]]
    gaps = []
    for (a, b) in pairs:
        oi = richardson(a, o[a], b, o[b])
        ei = richardson(a, e[a], b, e[b])
        if oi <= 0 or ei <= 0:
            print('     pair (%3d,%3d): NONPOSITIVE extrapolant odd=%s even=%s -- unusable'
                  % (a, b, mp.nstr(oi, 6), mp.nstr(ei, 6)))
            continue
        g = mp.log(oi / ei, 10)
        gaps.append((a, b, g))
        print('     pair (%3d,%3d): odd_inf=%s even_inf=%s  gap=%s dex   ordering %s'
              % (a, b, mp.nstr(oi, 10), mp.nstr(ei, 10), mp.nstr(g, 8),
                 'SURVIVES' if g > 0 else 'FAILS'))
    if gaps:
        lo = min(g for _, _, g in gaps); hi = max(g for _, _, g in gaps)
        print('     BAND over %d pairs: [%s, %s] dex   WIDTH = %s dex'
              % (len(gaps), mp.nstr(lo, 8), mp.nstr(hi, 8), mp.nstr(hi - lo, 6)))

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    if which in ('m3', 'both'):
        report("m3-L185 published lambda values (arithmetic re-derived here, not copied)",
               M3_ODD, M3_EVEN)
    if which in ('ours', 'both'):
        oo, ee = load_ours()
        report("OUR OWN cells (c46 published + c47 new), x=13 dps=150 gl=9 it=16", oo, ee)
