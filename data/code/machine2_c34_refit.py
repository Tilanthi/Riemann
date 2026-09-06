"""machine2 CYCLE 34 -- the REFIT: what is limiting AFTER the D* literal is removed?

c33 (`5aedd0e`) measured the SIZE of the D* effect: `D*_true - D*_literal = -3.7685544e-37`
times a measured d(coeff)/dD*, giving induced errors 1.61e-35 ... 6.34e-33 and pinning the
five fold constants to ~35/34/34/33/33 s.f. while the instrument refined to 1e-61.

Measuring one member of a set confirms MEMBERSHIP, never DOMINANCE.  This file removes the
member and asks what the maximum of the remaining set is.

NEW SCRIPT, NEW HASH.  c33's artefacts are frozen and untouched.  Machinery inherited from
`m2_c33_fold5.py` (Cauchy extraction in w on |w|=r_w with the even+real quarter-contour
saving; central FD in D; truncated series solve of G(x,e)=0); the four additions are:

  (A) CENTRE is the dps-150 refined D* (`m2_c34_dstar_refine.py`, 5 determinations agreeing,
      spread 7.2e-133), not the carried 36-digit literal.
  (B) g00 = G(0,0) is printed at 25 digits, not 6.  In c33 it printed IDENTICALLY in all four
      configs at 6 digits -- an instrument printing its own limiting error.  A constant that
      is identical across configs is not a measurement, so this run must resolve it.
  (C) SELF-CENTRING, at zero extra evaluation cost.  A wrong centre C enters ONLY as
      e_used = e_true + (C - D*_true), so the pipeline's own g[0][n] column determines the
      offset: solve  sum_n g[0][n] etilde^n = 0  for etilde, then re-expand the double series
      in e about etilde and re-solve.  This makes every config report its OWN D*, and it
      REMOVES the centre channel from within each config.  If the config-to-config spread
      collapses under recentring, the centre channel was dominant; if it does not, it was not.
      Either outcome is decisive -- that is the point.
  (D) The same shift machinery, driven with an artificial offset, gives d(coeff)/dD*
      analytically for free -- an independent cross-check of the three-pipeline-run
      central difference c33 paid for.

DOMINANCE TEST (pre-stated).  For a difference vector Delta_k between two configs, form the
implied centre shift  delta_k = Delta_k / S_k  with S = d(coeff)/dD*.  If the five delta_k
agree, the whole difference IS a centre shift (one number explains five).  If they scatter,
some other channel is contributing and its size is the part not explained.  This is the test
that distinguishes "the centre channel still dominates" from "something else took over", and
it is validated against a synthetic object with a known answer in m2_c34_synthetic.py.
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2  # noqa: E402

# dps-150 refined centre (m2_c34_dstar_refine.py, c34_dstar_refine.out)
DSTAR_REFINED = "0.14173323966388719139541568508418502362314456195501665594286660394665904218970743"
# the literal c32/c33 carried, kept ONLY so the same code path can be run at both centres
DSTAR_LITERAL = "0.141733239663887191395415685084185024"

MMAX = 5
# NMAX = 7, not 5.  The self-centring re-expands the double series in e, so h[m][n] needs
# g[m][j] for j > n; with NMAX = 5 the coefficient of e^5 recentres with a truncation error
# of order g[m][6]*etilde and a5 comes out WRONG.  The synthetic dry-run caught exactly that
# (T3c: a5 recentred error 2.1e-29 vs raw 1.1e-29 -- i.e. no correction at all), and T4 saw
# it independently (free sensitivity for a5 disagreeing with the pipeline FD by a factor 2).
# Two orders of headroom make the shift exact to well below every instrument term.  The
# solved order is still 5: series_solve only ever reads n <= K = 5.
NMAX = 7
NAMES = ["a", "b", "a3", "a4", "a5"]

_CFG = {}


def _init(cfg):
    _CFG.update(cfg)
    mp.mp.dps = cfg["dps"] + 15


# ----------------------------------------------------------------- evaluators
class SynXi:
    """Synthetic stand-in with a KNOWN answer -- see m2_c34_synthetic.py.

    h(w) = (w^2 - A(e)) / (1/4 - w^2),  e = centre - D  (centre passed in cfg).
    Even in w, real coefficients, simple poles at w = +-1/2: the same analytic shape the
    real object has, so the same aliasing law applies.  Exact zero curve x(e) = A(e).
    """

    COEFFS = ["2.6", "-7.4", "11.7", "-20.4", "18.2", "-64.5", "-94.4", "31.9"]
    MU = "3.7"      # e-dependence of the POLE RESIDUE -- see __init__

    def __init__(self, D, dps=45, guard=12, dsyn=None):
        # NOTE, declared: the synthetic forms e at dps+40 where the real Zeta2 rounds D to
        # dps digits.  Deliberate -- this file validates the SERIES / GRADER machinery, and
        # a synthetic evaluator floor would confound that.  The evaluator's own rounding
        # channel is probed on the real object instead, by the dps knob (cfg Q125).
        # `dsyn` is the object's OWN fold point and must NOT be the cfg centre: the first
        # draft of this class used the centre, which made the synthetic's truth move with
        # the quantity under test (a control whose baseline follows its object).  Caught by
        # the dry run, 2026-09-06.
        self.dps = dps
        with mp.workdps(dps + 40):
            self.D = mp.mpf(D) if not isinstance(D, mp.mpf) else +D
            e = mp.mpf(dsyn) - self.D
            self.A = sum(mp.mpf(c) * e ** (i + 1) for i, c in enumerate(self.COEFFS))
            self.mu = mp.mpf(self.MU) * e

    def xi(self, s):
        with mp.workdps(self.dps):
            w = mp.mpmathify(s) - mp.mpf(1) / 2
            # the (1 + MU*e) factor makes the residue at w = +-1/2 depend on e at O(1).
            # Without it the trapezoid aliasing enters G almost independently of e, the
            # forced x(0)=0 absorbs it, and the recovered coefficients are insensitive to
            # N_w -- so the synthetic would have certified an aliasing channel it could not
            # actually exhibit.  The real xi_D's residues (-1/s + 1/(D(s-1)), prefactor D^s)
            # do depend on D at O(1), so this factor makes the synthetic share the real
            # object's aliasing PROPAGATION, not merely its pole locations.
            return (w ** 2 - self.A) * (1 + self.mu) / (mp.mpf(1) / 4 - w ** 2)


def _make(D, cfg):
    if cfg.get("model") == "syn":
        return SynXi(D, dps=cfg["dps"], guard=cfg["guard"], dsyn=cfg["dsyn"])
    return Zeta2(D, dps=cfg["dps"], guard=cfg["guard"])


# ----------------------------------------------------------------- node work
def _node(p):
    dps, guard = _CFG["dps"], _CFG["guard"]
    r = mp.mpf(_CFG["r_w"])
    N = _CFG["N_w"]
    he = mp.mpf(10) ** (-_CFG["he"])
    mp.mp.dps = dps + 15
    D = mp.mpf(_CFG["centre"]) - p * he
    Z = _make(D, _CFG)
    half = mp.mpf(1) / 2
    quarter = N // 4
    base = [Z.xi(half + r * mp.expjpi(mp.mpf(2 * j) / N)) for j in range(quarter + 1)]

    def hval(j):
        j %= N
        if j >= N // 2:
            j -= N // 2
        if j <= quarter:
            return base[j]
        return mp.conj(base[N // 2 - j])

    vals = [hval(j) for j in range(N)]
    out = []
    for k in range(2 * MMAX + 2):
        s = mp.mpc(0)
        for j in range(N):
            s += vals[j] * mp.expjpi(mp.mpf(-2 * k * j) / N)
        out.append((s / N) / r ** k)
    return p, [mp.nstr(v, dps + 5, strip_zeros=False) for v in out]


def fd_weights(n, npts):
    m = npts // 2
    nodes = list(range(-m, m + 1))
    A = mp.matrix(npts, npts)
    for i, p in enumerate(nodes):
        for j in range(npts):
            A[i, j] = mp.mpf(p) ** j
    rhs = mp.matrix(npts, 1)
    rhs[n] = mp.factorial(n)
    return nodes, mp.lu_solve(A.T, rhs)


# ----------------------------------------------------- truncated series algebra
def pmul(u, v, K):
    out = [mp.mpf(0)] * (K + 1)
    for i, ui in enumerate(u):
        if ui == 0:
            continue
        for j, vj in enumerate(v):
            if i + j > K:
                break
            out[i + j] += ui * vj
    return out


def series_solve(g, K):
    """x(e), x(0)=0, solving sum g[m][n] x^m e^n = 0 (c33's solver, unchanged)."""
    x = [mp.mpf(0)] * (K + 1)
    for _ in range(K + 3):
        R = [mp.mpf(0)] * (K + 1)
        xp = [mp.mpf(0)] * (K + 1)
        xp[0] = mp.mpf(1)
        for m in range(MMAX + 1):
            for n in range(min(NMAX, K) + 1):
                gm = g[m][n]
                if gm == 0:
                    continue
                for i, c in enumerate(xp):
                    if i + n > K:
                        break
                    R[i + n] += gm * c
            xp = pmul(xp, x, K)
        x = [x[i] - R[i] / g[1][0] for i in range(K + 1)]
        x[0] = mp.mpf(0)
    return x


def shift_e(g, et):
    """Re-expand the double series G(x,e) about e = et:  h[m][n] = [x^m (e-et)^n] G."""
    h = [[mp.mpf(0)] * (NMAX + 1) for _ in range(MMAX + 1)]
    for m in range(MMAX + 1):
        for n in range(NMAX + 1):
            s = mp.mpf(0)
            for j in range(n, NMAX + 1):
                s += g[m][j] * mp.binomial(j, n) * et ** (j - n)
            h[m][n] = s
    return h


def solve_etilde(g, iters=8):
    """Root of e -> G(0,e) near 0: the offset of the centre used from the true fold point."""
    et = mp.mpf(0)
    for _ in range(iters):
        p = sum(g[0][n] * et ** n for n in range(NMAX + 1))
        dp = sum(n * g[0][n] * et ** (n - 1) for n in range(1, NMAX + 1))
        et = et - p / dp
    return et


def run(cfg, pool):
    dps = cfg["dps"]
    npts = cfg["npts"]
    mp.mp.dps = dps + 15
    ps = list(range(-(npts // 2), npts // 2 + 1))
    t0 = time.time()
    res = {}
    for p, strs in pool.imap_unordered(_node, ps):
        res[p] = [mp.mpmathify(s) for s in strs]
    wall = time.time() - t0

    he = mp.mpf(10) ** (-cfg["he"])
    g = [[None] * (NMAX + 1) for _ in range(MMAX + 1)]
    odd_ctl = mp.mpf(0)
    im_ctl = mp.mpf(0)
    for m in range(MMAX + 1):
        for n in range(NMAX + 1):
            nodes, wts = fd_weights(n, npts)
            s = mp.mpc(0)
            for idx, p in enumerate(nodes):
                s += wts[idx] * res[p][2 * m]
            val = (s / he ** n) / mp.factorial(n)
            im_ctl = max(im_ctl, abs(mp.im(val)) / (abs(val) + mp.mpf(10) ** (-dps)))
            g[m][n] = mp.re(val)
    for p in ps:
        for k in [1, 3, 5, 7, 9, 11]:
            odd_ctl = max(odd_ctl, abs(res[p][k]) / (abs(res[p][0]) + 1))

    x_raw = series_solve(g, 5)                       # c33's answer, at this centre
    et = solve_etilde(g)                             # this config's own view of the offset
    x_rec = series_solve(shift_e(g, et), 5)          # centre channel removed WITHIN the config

    # sensitivity for free: the same shift machinery driven by an artificial offset
    d = mp.mpf(10) ** (-25)
    xp_ = series_solve(shift_e(g, et + d), 5)
    xm_ = series_solve(shift_e(g, et - d), 5)
    # e = centre - D, so an offset et corresponds to centre_implied = centre - et:
    # d(coeff)/d(centre) = -d(coeff)/d(et)
    sens = [-(xp_[i] - xm_[i]) / (2 * d) for i in range(6)]

    return dict(cfg=cfg, wall=wall, g=g, x_raw=x_raw, x_rec=x_rec, et=et,
                g00=g[0][0], g01=g[0][1], sens=sens, odd_ctl=odd_ctl, im_ctl=im_ctl)


# ----------------------------------------------------------------- config grid
BASE = dict(dps=90, guard=25, r_w="0.04", N_w=40, npts=15, he=7)


def cfg(label, **kw):
    c = dict(BASE)
    c.update(kw)
    c["label"] = label
    c.setdefault("centre", DSTAR_REFINED)
    return c


CFGS = [
    # --- c33's own four knob-sets, now at the refined centre -------------------
    cfg("A"),                                             # c33 cfg A
    cfg("Alit", centre=DSTAR_LITERAL),                    # SAME knobs, OLD centre: P-A pair
    # --- one-knob-at-a-time channel probes around A ---------------------------
    cfg("N56", N_w=56),                                   # aliasing (2r)^N: 1e-44 -> 1e-61
    cfg("N72", N_w=72),                                   # aliasing -> 1e-79
    cfg("P17", npts=17),                                  # FD order in D
    cfg("H6", he=6),                                      # FD step 1e-6
    cfg("H8", he=8),                                      # FD step 1e-8
    cfg("Q125", dps=125, guard=30),                       # evaluator roundoff
    # --- the two expensive c33 anchors ----------------------------------------
    cfg("B", dps=110, guard=30, N_w=64),                  # c33 cfg B
    cfg("D", dps=125, guard=30, r_w="0.045", N_w=72, npts=17),   # c33 cfg D
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c34_refit.json")

if __name__ == "__main__":
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    dump = []
    if only and os.path.exists(OUT):
        dump = json.load(open(OUT))
    for c in CFGS:
        if only and c["label"] not in only:
            continue
        with Pool(8, initializer=_init, initargs=(c,)) as pool:
            R = run(c, pool)
        mp.mp.dps = 90
        print(f"\n### cfg {c['label']}: dps={c['dps']} guard={c['guard']} r_w={c['r_w']} "
              f"N_w={c['N_w']} npts={c['npts']} h_e=1e-{c['he']} "
              f"centre={'REFINED' if c['centre'] == DSTAR_REFINED else 'LITERAL'} "
              f"[{R['wall']:.0f}s]", flush=True)
        print(f"   controls: max|odd c_k|/|c_0| = {mp.nstr(R['odd_ctl'],4)}   "
              f"max|Im g|/|g| = {mp.nstr(R['im_ctl'],4)}")
        print(f"   G(0,0) = {mp.nstr(R['g00'], 25)}      g01 = {mp.nstr(R['g01'], 15)}")
        print(f"   etilde (this config's own centre offset) = {mp.nstr(R['et'], 12)}")
        print(f"   implied D* = {mp.nstr(mp.mpf(c['centre']) - R['et'], 60)}")
        for i, nm in enumerate(NAMES):
            print(f"   {nm:>3s} raw = {mp.nstr(R['x_raw'][i+1], 60)}")
            print(f"   {nm:>3s} rec = {mp.nstr(R['x_rec'][i+1], 60)}    "
                  f"d(coeff)/dD* = {mp.nstr(R['sens'][i+1], 12)}")
        dump = [d for d in dump if d["label"] != c["label"]]
        dump.append(dict(label=c["label"], cfg={k: v for k, v in c.items()},
                         wall=R["wall"],
                         odd_ctl=mp.nstr(R["odd_ctl"], 6), im_ctl=mp.nstr(R["im_ctl"], 6),
                         g00=mp.nstr(R["g00"], 30), g01=mp.nstr(R["g01"], 20),
                         et=mp.nstr(R["et"], 30),
                         raw={nm: mp.nstr(R["x_raw"][i + 1], 70) for i, nm in enumerate(NAMES)},
                         rec={nm: mp.nstr(R["x_rec"][i + 1], 70) for i, nm in enumerate(NAMES)},
                         sens={nm: mp.nstr(R["sens"][i + 1], 15) for i, nm in enumerate(NAMES)}))
        with open(OUT, "w") as f:
            json.dump(dump, f, indent=1)
