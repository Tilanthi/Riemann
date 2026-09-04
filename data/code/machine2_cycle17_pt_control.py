"""machine 2 -- cycle 17 -- EXTERNAL POSITIVE CONTROL on the zero-finding instrument.

Ground truth supplied by beast-scout (via BEAST-AGI 09:28Z) from Potter-Titchmarsh 1935:
the Epstein zeta of Q = m^2 + 5 n^2 has an OFF-CRITICAL zero at
        rho = 0.932969697... + i 15.668249531...
Q corresponds to Delta = sqrt(5) in zeta2(s,Delta) = (1/2) sum'(j^2 + Delta^2 k^2)^{-s}
(zeta2 = E(s,Q)/2, so the zeros coincide).

This is an EXTERNAL ground truth: nothing in our lane produced it.  Passing it tests the
evaluator, the root polisher and the whole pipeline against a 1935 published number.
"""
import json
from mpmath import mp, mpf, mpc, findroot, nstr
import gen_eval

PT = mpc('0.932969697', '15.668249531')
D  = mp.sqrt(5)
out = {}
for dps in (30, 45):
    mp.dps = dps
    D = mp.sqrt(5)
    v = gen_eval.zeta2(PT, D)
    r = findroot(lambda z: gen_eval.zeta2(z, D), PT, tol=mp.mpf(10)**(-(dps-8)))
    out[dps] = dict(value_at_published=nstr(abs(v), 8),
                    refined=nstr(r, dps-6),
                    residual=nstr(abs(gen_eval.zeta2(r, D)), 6),
                    dist_from_published=nstr(abs(r-PT), 6))
    print(dps, json.dumps(out[dps], indent=1), flush=True)
json.dump(out, open('pt_control.json','w'), indent=1)
