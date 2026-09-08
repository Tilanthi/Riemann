#!/usr/bin/env python3
"""R1 -- agreement DEPTH between our cells and m3's published values.

A depth, not a bound: the verdict is capped by the NARROWER of the two printed widths
(c37/c42 law -- a print format is an instrument), so the cap is reported beside every row.
"""
import mpmath as mp, json, glob, os, re
mp.mp.dps = 200

M3 = {  # exactly as printed in m3's results/SUMMARY.md and odd_Nextrap_results.json
 ('odd',100): '3.34107742032073965658213712601992236254413410378763387206214e-55',
 ('odd',140): '2.8475156913393636771563703939938140057126090742267e-55',
 ('odd',180): '2.698009778782749686608210255746078258440609181395e-55',
 ('odd',220): '2.5322446138126329379067665416656277722374006147654e-55',
 ('even',100):'3.720899741667123935791434766094540694091e-59',
 ('even',140):'3.191618722904299187775878951533394940265e-59',
 ('even',180):'2.959706807240060045108126519806894301792e-59',
 ('even',220):'2.833656431009356898926062340578180078197e-59',
}
def sigfigs(s):
    return len(re.sub(r'[^0-9]', '', s.split('e')[0]).lstrip('0'))

ours = {}
for d in ('/shared/rh-exchange-repo/Riemann/data/c46', '/workspace/rh/c47/mine/data/c46'):
    for fn in glob.glob(os.path.join(d, 'c46_*_x13_N*_dps150_g9_it16.json')):
        c = json.load(open(fn))
        if str(c['x']) == '13' and c['dps'] == 150:
            ours[(c['parity'], c['N'])] = c['lambda_min']

print('%-6s %4s  %6s %6s  %-14s  %s' % ('parity','N','ours_sf','m3_sf','rel_diff','verdict'))
for k in sorted(M3, key=lambda z: (z[0], z[1])):
    if k not in ours:
        print('%-6s %4d  MISSING on our side' % k); continue
    a, b = mp.mpf(ours[k]), mp.mpf(M3[k])
    rel = abs(a - b) / abs(b)
    cap = min(sigfigs(ours[k]), sigfigs(M3[k]))
    depth = int(mp.floor(-mp.log(rel, 10))) if rel > 0 else 10**9
    print('%-6s %4d  %6d %6d  %-14s  agree to %d s.f. (CAP set by the narrower print = %d s.f.)%s'
          % (k[0], k[1], sigfigs(ours[k]), sigfigs(M3[k]), mp.nstr(rel, 6),
             min(depth, cap), cap, '  [NEW this cycle]' if k[1] in (180, 220) else ''))
