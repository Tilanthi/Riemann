"""machine2 CYCLE 26 -- scored runner for the BAND-RULE unit.

Attacks a claim WE published (cycle 25, eb45f2b): "m1's 2|ty6-ty4| band rule SURVIVES out of sample,
calibrated to [0.500, 0.543] over ten rungs, two-instrument".

Thesis under test (pre-registered at c26_prereg.json BEFORE this script was run):
    the audit statistic  ratio = |ty4 - exact| / (2|ty6 - ty4|)
    is ALGEBRAICALLY  0.5 / (1 - r),  where  r = |ty6 - exact| / |ty4 - exact|
    is the ladder's own local convergence ratio.  If so the band statistic carries exactly the
    information in r and nothing else, the rule FAILS iff r > 1/2, and "10/10 in band" is one
    claim (the ladder converges by better than 2x per two orders) measured ten times.

Two legs:
  LEG 1  identity + never-at-risk audit on the ten ALREADY-COMMITTED cycle-25 S2 rungs.
  LEG 2  delta_b sweep at the same S2 site, delta_a = 0.1 fixed, hunting the failure boundary
         r = 1/2 that the committed rungs never approached.

Nothing here reads the exact value before ty4/ty6; every quantity is recomputed from the frozen
instrument.  Site parameters come from cycle 25's committed prereg (c25_prereg.json).
"""
import json, os, sys, time
from mpmath import mp

C25 = "/workspace/rh/cycle25"
sys.path.insert(0, C25)
from m2_u_instrument import Basis, load_genomes, load_target          # noqa: E402
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N        # noqa: E402

mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
half = mp.mpf(1) / 2
P = json.load(open(os.path.join(C25, "c25_prereg.json")))
S = P["site"]

gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
bases = [Basis(g, degree=8) for g in gens]
G = gram(); K200 = mat(tgt["K_T200"])
g_a = mp.mpf(S["g_a"]); g_b = mp.mpf(S["g_b"]); g_bs = mp.mpf(S["g_bs"])
GA1, GA2, GB1, GB2 = [mp.mpf(x) for x in S["removed"]]
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))
base = K200 - remA - remB


def Smat(up, uq):
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


def quad(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    return Smat([b.u(p) for b in bases], [b.u(q) for b in bases])


qA0, qB0, qB0s = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b), quad(mp.mpf(0), g_bs)
DERS = {}
for nm, g0 in (("a", g_a), ("b", g_b), ("bs", g_bs)):
    s0 = mp.mpc(half, g0)
    DERS[nm] = [[sum(w * (x ** k) * mp.exp(s0 * x) for x, w in zip(b.xs, b.ws)) for k in range(11)]
                for b in bases]


def quadT(nm, d, K):
    up = [sum(DERS[nm][i][k] * (d ** k) / mp.factorial(k) for k in range(K + 1)) for i in range(N)]
    uq = [sum(DERS[nm][i][k] * ((-d) ** k) / mp.factorial(k) for k in range(K + 1)) for i in range(N)]
    return Smat(up, uq)


def config(da, db, site, orders=(2, 4, 6, 8, 10)):
    """exact lam_min plus the Taylor ladder at the requested orders."""
    Aex = quad(da, g_a) if da != 0 else qA0
    g0b = g_b if site == "b" else g_bs
    Bex = quad(db, g0b) if db != 0 else (qB0 if site == "b" else qB0s)
    ex = lam(base + Aex + Bex, G)[0]
    tys = {}
    for K in orders:
        A = quadT("a", da, K) if da != 0 else qA0
        B_ = quadT(site, db, K) if db != 0 else (qB0 if site == "b" else qB0s)
        tys[K] = lam(base + A + B_, G)[0]
    return ex, tys


def stats(ex, tys):
    e4 = abs(tys[4] - ex); e6 = abs(tys[6] - ex)
    band = 2 * abs(tys[6] - tys[4])
    ratio = e4 / band
    r = e6 / e4 if e4 != 0 else mp.mpf('nan')
    pred = mp.mpf(1) / 2 / (1 - r)
    return dict(exact=mp.nstr(ex, 20), ty4=mp.nstr(tys[4], 20), ty6=mp.nstr(tys[6], 20),
                err_ty4=mp.nstr(e4, 10), err_ty6=mp.nstr(e6, 10),
                band=mp.nstr(band, 10), ratio=mp.nstr(ratio, 12), r=mp.nstr(r, 12),
                ident_pred=mp.nstr(pred, 12),
                ident_relerr=mp.nstr(abs(ratio - pred) / abs(ratio), 6),
                in_band=bool(e4 <= band),
                band_over_err=mp.nstr(band / e4, 8),
                err_ty2=mp.nstr(abs(tys[2] - ex), 8), err_ty8=mp.nstr(abs(tys[8] - ex), 8),
                err_ty10=mp.nstr(abs(tys[10] - ex), 8))


t0 = time.time()
OUT = {"leg1_committed_rungs": {}, "leg2_sweep": {}}

print("LEG 1 -- identity + never-at-risk audit, ten committed cycle-25 S2 rungs")
print("%-5s %7s %8s | %12s %12s %12s %10s %s" %
      ("rung", "d_a", "d_b", "ratio", "r=e6/e4", "0.5/(1-r)", "relerr", "band"))
RUNGS = json.load(open(os.path.join(C25, "c25_scored.json")))["rungs"]
for nm, info in RUNGS.items():
    da = mp.mpf(info["d_a"]); db = mp.mpf(info["d_b"]); site = info["site"]
    ex, tys = config(da, db, site)
    st = stats(ex, tys)
    st["d_a"] = mp.nstr(da, 6); st["d_b"] = mp.nstr(db, 8); st["site"] = site
    OUT["leg1_committed_rungs"][nm] = st
    print("%-5s %7s %8s | %12s %12s %12s %10s %s" %
          (nm, st["d_a"], st["d_b"], st["ratio"], st["r"], st["ident_pred"],
           st["ident_relerr"], "IN" if st["in_band"] else "OUT"), flush=True)

print("\nLEG 2 -- delta_b sweep at the S2 site, delta_a = 0.1 fixed, hunting r = 1/2")
print("%-8s | %12s %12s %12s %10s %s" % ("d_b", "ratio", "r=e6/e4", "0.5/(1-r)", "relerr", "band"))
LADDER = ["0.30", "0.35", "0.40", "0.45", "0.50", "0.55", "0.60", "0.70", "0.80"]
for ds in LADDER:
    db = mp.mpf(ds)
    ex, tys = config(mp.mpf("0.1"), db, "b")
    st = stats(ex, tys)
    st["d_a"] = "0.1"; st["d_b"] = ds; st["site"] = "b"
    OUT["leg2_sweep"][ds] = st
    print("%-8s | %12s %12s %12s %10s %s" %
          (ds, st["ratio"], st["r"], st["ident_pred"], st["ident_relerr"],
           "IN" if st["in_band"] else "OUT"), flush=True)

json.dump(OUT, open(os.path.join(HERE, "c26_bandlaw.json"), "w"), indent=1)
print("\ndone %.1fs" % (time.time() - t0))
