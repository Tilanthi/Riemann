"""machine 2 -- cycle 17 -- the height range the main census does not cover: 0 <= t <= 0.3,
plus the real axis (BST's 'real off-critical zeros', which they predict do NOT exist for
Delta > Delta*_c = 0.141733... ; our Delta = 1/7 = 0.142857 > Delta*_c)."""
import json
from mpmath import mp, mpf, mpc, pi, log, im, re, exp, loggamma
import census2, eval2b, gen_eval

out = {}
for dps in (20, 30):
    mp.dps = dps
    census2.LOG7PI = log(mpf(7)/pi)
    r = census2.count_rect(mpf('0.02'), mpf('0.3'), mp.pi/8, 2.0)
    L7 = log(mpf(7)/pi)
    def Z(t):
        t = mpf(t)
        th = t*L7 + im(loggamma(mpc(mpf(1)/2, t)))
        return re(exp(mpc(0, th))*eval2b.F(mpc(mpf(1)/2, t)))
    zs = [(str(t), mp.nstr(Z(t), 10)) for t in ['0.02','0.06','0.1','0.15','0.2','0.25','0.3']]
    # real axis: F on sigma in [0.5,1.19] and [-0.19,0.5] at t=0 (F real there)
    rs = [(str(x), mp.nstr(re(eval2b.F(mpc(mpf(x), 0))), 10)) for x in
          ['-0.15','-0.05','0.1','0.25','0.4','0.45','0.55','0.6','0.75','0.9','1.05','1.15']]
    out[dps] = dict(count_002_03=r, Z_small_t=zs, F_real_axis=rs)
    print(dps, json.dumps(out[dps], indent=1), flush=True)
json.dump(out, open('lowt.json','w'), indent=1)
