"""machine2 cycle22 — independent u_i / K instrument for the N2/N5 witness build.

Adopted from m1 (declared): the raw BUMP genomes
    data/code/machine1_heat70_genomes_m8_m64.json
and the test-function convention in machine1-spec-n2-n5-second-instrument.md sect 1.
Everything else here (quadrature, node generation, zero list, matrix assembly) is ours.

phi_i(x) = w(x) * sum_bumps c*exp(-1/(1-t^2)) 1_{|t|<1},  t = (x-mu)/s
w(x)     = theta((8-|x|)/2),  theta(y)=e^{-1/y}/(e^{-1/y}+e^{-1/(1-y)}) on (0,1), 0 for y<=0, 1 for y>=1
u_i(rho) = int_{-8}^{8} phi_i(x) e^{rho x} dx
"""
import json, sys, time
from mpmath import mp, mpf, mpc, exp, quad

DPS = 40
mp.dps = DPS

REPO = "/shared/rh-exchange-repo/Riemann"


def theta(y):
    if y <= 0:
        return mp.mpf(0)
    if y >= 1:
        return mp.mpf(1)
    a = exp(-1 / y)
    b = exp(-1 / (1 - y))
    return a / (a + b)


def window(x):
    return theta((8 - abs(x)) / 2)


def make_phi(genome):
    bumps = [(mp.mpf(str(c)), mp.mpf(str(mu)), mp.mpf(str(s))) for c, mu, s in genome]

    def phi(x):
        tot = mp.mpf(0)
        for c, mu, s in bumps:
            t = (x - mu) / s
            if abs(t) < 1:
                tot += c * exp(-1 / (1 - t * t))
        if tot == 0:
            return mp.mpf(0)
        return window(x) * tot

    return phi, bumps


def breakpoints(bumps):
    """Interval endpoints: bump supports clipped to [-8,8], split at +-6 and +-8."""
    pts = set()
    for c, mu, s in bumps:
        lo, hi = mu - s, mu + s
        if hi <= -8 or lo >= 8:
            continue
        lo = max(lo, mp.mpf(-8))
        hi = min(hi, mp.mpf(8))
        pts.add(lo)
        pts.add(hi)
        for cut in (mp.mpf(-6), mp.mpf(6)):
            if lo < cut < hi:
                pts.add(cut)
    return sorted(pts)


def intervals(bumps):
    """Per-bump intervals (do NOT merge: sum of bumps is fine, but keep each bump's
    own support endpoints as breakpoints -> union of all endpoints, then integrate the
    FULL phi on each sub-interval)."""
    pts = breakpoints(bumps)
    out = []
    for k in range(len(pts) - 1):
        a, b = pts[k], pts[k + 1]
        if b > a:
            out.append((a, b))
    return out


# ---- fixed Gauss-Legendre nodes (ours; mpmath's GaussLegendre node generator) ----
from mpmath.calculus.quadrature import GaussLegendre

_gl = GaussLegendre(mp)
_node_cache = {}


def gl_nodes(a, b, degree):
    key = (str(a), str(b), degree, mp.prec)
    if key in _node_cache:
        return _node_cache[key]
    raw = _gl.get_nodes(a, b, degree, mp.prec)
    # get_nodes returns list of levels; degree m -> single level list of (x,w)
    nodes = raw[0] if isinstance(raw[0], list) else raw
    _node_cache[key] = nodes
    return nodes


class Basis:
    """Precompute phi_i on fixed GL nodes over each sub-interval; u_i(rho) is then a dot
    product with e^{rho x}. Node budget set by the oscillation e^{i t x}, |t| <= TMAX."""

    def __init__(self, genome, degree=8):
        self.phi, self.bumps = make_phi(genome)
        self.ivs = intervals(self.bumps)
        self.xs = []
        self.ws = []  # w_k * phi(x_k)
        for (a, b) in self.ivs:
            for (x, w) in gl_nodes(a, b, degree):
                v = self.phi(x)
                if v != 0:
                    self.xs.append(x)
                    self.ws.append(w * v)

    def u(self, rho):
        tot = mp.mpc(0)
        for x, w in zip(self.xs, self.ws):
            tot += w * exp(rho * x)
        return tot

    def u_real(self, sigma):
        tot = mp.mpf(0)
        for x, w in zip(self.xs, self.ws):
            tot += w * exp(sigma * x)
        return tot


def load_genomes(key="s1/M8"):
    with open(f"{REPO}/data/code/machine1_heat70_genomes_m8_m64.json") as f:
        d = json.load(f)
    return d["genomes"][key]


def load_target(key="s1/M8"):
    with open(f"{REPO}/data/machine1_heat72k_identity_target_m8.json") as f:
        d = json.load(f)
    return d["seeds"][key]


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "s1/M8"
    deg = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    gens = load_genomes(key)
    tgt = load_target(key)
    t0 = time.time()
    bases = [Basis(g, degree=deg) for g in gens]
    print(f"# {key} degree={deg} dps={DPS} nodes/basis={[len(b.xs) for b in bases]} build={time.time()-t0:.1f}s")
    print("i   |u_i(0)-U0_m1|      |u_i(1)-U1_m1|")
    for i, b in enumerate(bases):
        u0 = b.u_real(mp.mpf(0))
        u1 = b.u_real(mp.mpf(1))
        d0 = abs(u0 - mp.mpf(tgt["U0"][i]))
        d1 = abs(u1 - mp.mpf(tgt["U1"][i]))
        print(f"{i}   {mp.nstr(d0,4):>12}   {mp.nstr(d1,4):>12}")
