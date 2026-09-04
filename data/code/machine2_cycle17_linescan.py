"""machine 2 -- cycle 17 -- sign-change census of the real Hardy function Z(t) on (T0,T1].

Z(t) = e^{i theta(t)} F(1/2+it),  theta(t) = t log(7/pi) + Im loggamma(1/2+it).
Verified real to working precision at dps 25 and dps 40 (fe_check.py).

Stage 1: uniform grid of step H.
Stage 2: every interval whose endpoints have the SAME sign is re-examined -- a pair of zeros
         can hide there.  Refinement is driven by |Z|: on an interval with equal signs we
         bisect while the interior minimum of |Z| is below MINFRAC * max(|Z| at the ends),
         to a floor of H/64.  This is a HEURISTIC and is declared as one: the certificate of
         completeness is NOT this scan, it is its agreement with the argument-principle count.
"""
import json, sys, time, os
from multiprocessing import Pool
from mpmath import mp, mpf, mpc, pi, log, loggamma, im, re, exp
import eval2b

LOG7PI = None
def theta(t): return t*LOG7PI + im(loggamma(mpc(mpf(1)/2, t)))
def Z(t):
    t = mpf(t)
    return re(exp(mpc(0, theta(t)))*eval2b.F(mpc(mpf(1)/2, t)))

def scan_chunk(args):
    dps, a, b, H, minfrac = args
    mp.dps = dps
    global LOG7PI
    LOG7PI = log(mpf(7)/pi)
    a, b, H = mpf(a), mpf(b), mpf(H)
    n = int((b-a)/H)
    ts = [a + H*i for i in range(n+1)]
    zs = [Z(t) for t in ts]
    evals = len(zs)
    changes = []
    suspect = []
    for i in range(n):
        if zs[i] == 0 or zs[i+1] == 0:
            suspect.append((float(ts[i]), float(ts[i+1]), 'exact-zero-sample'))
            continue
        if (zs[i] > 0) != (zs[i+1] > 0):
            changes.append(float((ts[i]+ts[i+1])/2))
        else:
            # look for a hidden pair
            lo, hi, zl, zh = ts[i], ts[i+1], zs[i], zs[i+1]
            ref = max(abs(zl), abs(zh))
            stack = [(lo, hi, zl, zh, 0)]
            while stack:
                l, h, vl, vh, d = stack.pop()
                m = (l+h)/2
                vm = Z(m); evals += 1
                if (vl > 0) != (vm > 0):
                    changes.append(float((l+m)/2))
                if (vm > 0) != (vh > 0):
                    changes.append(float((m+h)/2))
                if (vl > 0) == (vm > 0) == (vh > 0) and d < 6 and abs(vm) < minfrac*ref:
                    stack.append((l, m, vl, vm, d+1))
                    stack.append((m, h, vm, vh, d+1))
    return dict(a=float(a), b=float(b), changes=sorted(changes), evals=evals)

if __name__ == "__main__":
    dps   = int(sys.argv[1]); T0 = sys.argv[2]; T1 = sys.argv[3]
    H     = sys.argv[4] if len(sys.argv) > 4 else '0.05'
    nproc = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    minfrac = mpf('0.35')
    a, b = mpf(T0), mpf(T1)
    W = (b-a)/nproc
    tasks = [(dps, str(a+W*i), str(a+W*(i+1)), H, float(minfrac)) for i in range(nproc)]
    t0 = time.time()
    with Pool(nproc) as p:
        res = p.map(scan_chunk, tasks)
    ch = sorted([c for r in res for c in r['changes']])
    ev = sum(r['evals'] for r in res)
    out = dict(dps=dps, T0=T0, T1=T1, H=H, n_sign_changes=len(ch), evals=ev,
               secs=round(time.time()-t0,1), changes=ch)
    json.dump(out, open(f"linescan_{dps}_{T0}_{T1}_{H}.json","w"), indent=1)
    print(json.dumps({k:v for k,v in out.items() if k!='changes'}, indent=1))
