"""machine 2 -- cycle 17 -- argument-principle count, v2, WITH AN ANTI-ALIASING SEED RULE.

WHY v2 EXISTS (measured this run, and it is the finding, not a preference):
v1 tracked arg F by bisecting only when the PRINCIPAL value arg(F(s2)/F(s1)) exceeded a
threshold.  That is unsound: if the TRUE argument change over a seed step is close to 2*pi,
its principal value is close to 0, the step is accepted as "converged", and 2*pi of winding
is silently discarded.  v1 reported max per-step |Delta arg| = 0.1962 < pi/16 -- fully GREEN --
while under-counting the strip by ~44 zeros out of ~172 (window [60,75] read 7 against an
expected ~24).  The diagnostic I already require (max step) is necessary and NOT sufficient:
it cannot see an aliased step, because an aliased step LOOKS small.
FIX: seed every edge finely enough that the true change per seed step is provably < pi, using
an a-priori rate bound  |d arg Lam/dz| <= |log(7/pi)| + |psi(s)| + |F'/F|, with |psi(s)| <=
log|s| + 1 and a slack factor; then bisect.  And the certificate is NOT the seed rule, it is
STABILITY: the count is reported only if it is unchanged when seeds are doubled and the leaf
threshold is halved.
"""
import json, sys, time
from mpmath import mp, mpf, mpc, pi, log, loggamma, im, re, arg, sqrt
import eval2b

SIG_L = mpf('-0.19')
SIG_R = mpf('1.19')
LOG7PI = None

def prefarg(s):
    return im(s)*LOG7PI + im(loggamma(s))

class Walk:
    def __init__(self, maxstep):
        self.maxstep = maxstep; self.total = mp.zero; self.maxd = mp.zero
        self.maxseed = mp.zero; self.evals = 0; self.minabs = None
    def _f(self, s):
        self.evals += 1
        v = eval2b.F(s); a = abs(v)
        if self.minabs is None or a < self.minabs: self.minabs = a
        return v
    def segment(self, s1, s2, v1=None, v2=None, depth=0, seed=False):
        if v1 is None: v1 = self._f(s1)
        if v2 is None: v2 = self._f(s2)
        d = arg(v2/v1)
        if seed and abs(d) > self.maxseed: self.maxseed = abs(d)
        if abs(d) <= self.maxstep or depth > 45:
            if abs(d) > self.maxd: self.maxd = abs(d)
            self.total += d
            return
        sm = (s1+s2)/2; vm = self._f(sm)
        self.segment(s1, sm, v1, vm, depth+1)
        self.segment(sm, s2, vm, v2, depth+1)

def rate_bound(a, b):
    """upper bound on |d arg Lam / d(arclength)| on the segment a->b (crude but safe):
    |log(7/pi)| + max(|psi(s)|) + slack for F'/F.  |psi(s)| <= log|s|+1 for Re s > -1."""
    m = max(abs(a), abs(b))
    return abs(LOG7PI) + log(m+2) + 1 + 3

def count_rect(T0, T1, maxstep, seed_mult=1.0):
    W = Walk(maxstep)
    corners = [mpc(SIG_L,T0), mpc(SIG_R,T0), mpc(SIG_R,T1), mpc(SIG_L,T1), mpc(SIG_L,T0)]
    dpref = mp.zero
    seeds = []
    for i in range(4):
        a, b = corners[i], corners[i+1]
        dpref += prefarg(b) - prefarg(a)
        L = abs(b-a)
        n = int(mp.ceil(seed_mult * rate_bound(a,b) * L / mpf('0.9'))) + 4
        seeds.append(n)
        pts = [a + (b-a)*mpf(j)/n for j in range(n+1)]
        vprev = None
        for j in range(n):
            W.segment(pts[j], pts[j+1], seed=True)
    tot = dpref + W.total
    N = tot/(2*mp.pi)
    return dict(N=int(mp.nint(N)), N_real=mp.nstr(N,12), max_leaf_step=mp.nstr(W.maxd,6),
                max_seed_step=mp.nstr(W.maxseed,6), evals=W.evals,
                min_absF=mp.nstr(W.minabs,6), seeds=seeds)

def job(a):
    dps, T0, T1, k, sm = a
    mp.dps = dps
    global LOG7PI
    LOG7PI = log(mpf(7)/pi)
    t0 = time.time()
    r = count_rect(mpf(T0), mpf(T1), mp.pi/k, sm)
    r.update(T0=T0, T1=T1, k=k, seed_mult=sm, dps=dps, secs=round(time.time()-t0,1))
    return r

if __name__ == "__main__":
    from multiprocessing import Pool
    dps = int(sys.argv[1]); k = int(sys.argv[2]); sm = float(sys.argv[3])
    edges = [float(x) for x in sys.argv[4].split(',')]
    tag = sys.argv[5]
    tasks = [(dps, str(edges[i]), str(edges[i+1]), k, sm) for i in range(len(edges)-1)]
    t0 = time.time()
    with Pool(min(8, len(tasks))) as p:
        res = p.map(job, tasks)
    out = dict(dps=dps, maxstep=f"pi/{k}", seed_mult=sm,
               N_total=sum(r['N'] for r in res),
               max_leaf=max(float(r['max_leaf_step']) for r in res),
               max_seed=max(float(r['max_seed_step']) for r in res),
               evals=sum(r['evals'] for r in res), secs=round(time.time()-t0,1), windows=res)
    json.dump(out, open(f"census2_{tag}.json","w"), indent=1)
    print(json.dumps({kk:v for kk,v in out.items() if kk!='windows'}, indent=1))
    for r in res: print(f"  [{r['T0']},{r['T1']}] N={r['N']:4d} leaf={r['max_leaf_step']} seed={r['max_seed_step']} min|F|={r['min_absF']} ev={r['evals']} {r['secs']}s")
