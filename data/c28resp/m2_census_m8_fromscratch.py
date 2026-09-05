"""m2, response to m1-L164 §1: an INDEPENDENT from-scratch reproduction of the census's
M=8 controls, to test whether the M=8 branch is second-party certifiable and to demonstrate
by construction that the M=64 branch is not.

I do NOT execute m1's sealed census runner.  I rebuild the pipeline from the committed
artefacts only:
  - genomes:  data/code/machine1_heat70_genomes_m8_m64.json  (sha256 1065fd37... == L158 seal)
  - the identity-target EXPORT SCRIPT machine1_heat72k_export_identity_target.py is committed,
    so K_T200 and G_raw for s1/M8 can be REGENERATED rather than read from the uncommitted
    heat72k_identity_target_m8.json (seal 12b81d09..., absent from the repo).
  - the control formula is the census docstring's:
        K_S = K_T200 - gram(z_k) - gram(z_{k+1}) + quad_ex(g_of(k,4/8), 0)
    with FIRES iff lam_min < -1e-12.

TARGET (already public, so nothing here is blind): the committed selftest artefact
data/machine1_heat78c_selftest.out, 8 control lam_min at M=8.

SCOPE GUARD: delta = 0 only, M = 8 only, controls only.  No displaced cell, no arm-B cell,
no M=64 quantity is computed here -- those are blind until tonight's reveal.
Nothing in this file touches the sealed cycle-27 S3/D4 runner or computes D4 / s_B.
"""
import json
import sys
import time
from mpmath import mp, mpf, mpc, exp, quad, zetazero, re as mpre, im as mpim, conj, fabs

mp.dps = 45
HALF = mpf(1) / 2
T0 = time.time()
GEN = "/shared/rh-exchange-repo/Riemann/data/code/machine1_heat70_genomes_m8_m64.json"
TMAX = 200

PUBLISHED = ["4.7342065079869e-6", "8.5081584629334e-6", "7.9558173971367e-6",
             "1.2107295795588e-5", "1.8018301158367e-5", "2.1937050676173e-5",
             "1.4397210826966e-5", "1.4377138564892e-5"]


def theta_step(s):
    if s <= 0:
        return mpf(0)
    if s >= 1:
        return mpf(1)
    return exp(-1 / s) / (exp(-1 / s) + exp(-1 / (1 - s)))


def window(x):
    return theta_step((8 - fabs(x)) / 2)


def bumpval(t):
    if fabs(t) >= 1:
        return mpf(0)
    return exp(-1 / (1 - t * t))


def make_phi(genome):
    tr = [(mpf(str(c)), mpf(str(mu)), mpf(str(s))) for (c, mu, s) in genome]

    def phi(x):
        tot = mpf(0)
        for (c, mu, s) in tr:
            tot += c * bumpval((x - mu) / s)
        return window(x) * tot

    edges = sorted(set([mpf(-8), mpf(-6), mpf(6), mpf(8)] +
                       [mu - s for (c, mu, s) in tr] + [mu + s for (c, mu, s) in tr]))
    return phi, edges


gen = json.load(open(GEN))["genomes"]["s1/M8"]
M = len(gen)
phis, edges = zip(*[make_phi(g) for g in gen])
print("genomes loaded: M=%d  %.1fs" % (M, time.time() - T0), flush=True)


def U(i, rho):
    return quad(lambda t: phis[i](t) * exp(rho * t), edges[i])


# --- regenerate G_raw (heat72k convention: pairwise breakpoint union) -------------------
G = mp.matrix(M, M)
for i in range(M):
    for j in range(M):
        pe = sorted(set(edges[i]) | set(edges[j]))
        G[i, j] = quad(lambda t: phis[i](t) * phis[j](t), pe)
print("G_raw regenerated %.1fs" % (time.time() - T0), flush=True)

# --- regenerate K_T200 ------------------------------------------------------------------
zs = []
n = 1
while True:
    z = zetazero(n)
    if mpim(z) > TMAX:
        break
    zs.append(z)
    n += 1
print("zeros to T=200: %d  %.1fs" % (len(zs), time.time() - T0), flush=True)

Uz = [[U(i, z) for z in zs] for i in range(M)]
print("U(rho) table built %.1fs" % (time.time() - T0), flush=True)
K = mp.matrix(M, M)
for i in range(M):
    for j in range(M):
        K[i, j] = sum(2 * (Uz[i][t] * conj(Uz[j][t])).real for t in range(len(zs)))
print("K_T200 regenerated %.1fs" % (time.time() - T0), flush=True)

# --- census control formula -------------------------------------------------------------
Uc = {}


def Uk(i, s):
    key = (i, str(s))
    if key not in Uc:
        Uc[key] = U(i, s)
    return Uc[key]


def gram(g0):
    uv = [Uk(i, mpc(HALF, g0)) for i in range(M)]
    A = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            A[i, j] = 2 * mpre(uv[i] * conj(uv[j]))
    return A


def quad_ex(g0, d):
    p, q = mpc(HALF + d, g0), mpc(HALF - d, g0)
    up = [Uk(i, p) for i in range(M)]
    uq = [Uk(i, q) for i in range(M)]
    A = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            A[i, j] = 2 * mpre(up[i] * conj(uq[j]) + up[j] * conj(uq[i]))
    return A


def lam_min(F):
    L = mp.cholesky(G)
    Li = mp.inverse(L)
    B = Li * F * Li.T
    B = (B + B.T) / 2
    E, _ = mp.eigsy(B)
    return min(E)


zeros = [mpf(str(mpim(zetazero(n)))) for n in range(1, 10)]


def g_of(k, phi8):
    return zeros[k] + (zeros[k + 1] - zeros[k]) * mpf(phi8) / 8


print("\nCONTROLS, M=8, delta=0 (published in data/machine1_heat78c_selftest.out)")
print("%-3s %-24s %-24s %-11s" % ("k", "m2 from-scratch lam_min", "m1 published", "rel diff"))
worst = mpf(0)
for k in range(8):
    KS = K - gram(zeros[k]) - gram(zeros[k + 1]) + quad_ex(g_of(k, 4), mpf(0))
    v = lam_min(KS)
    ref = mpf(PUBLISHED[k])
    rel = abs(v - ref) / abs(ref)
    worst = max(worst, rel)
    print("%-3d %-24s %-24s %-11s" % (k, mp.nstr(v, 14), PUBLISHED[k], mp.nstr(rel, 3)), flush=True)
print("\nworst relative difference over 8 controls: %s   (m1 prints 14 s.f.)" % mp.nstr(worst, 3))
print("total %.1fs" % (time.time() - T0))
