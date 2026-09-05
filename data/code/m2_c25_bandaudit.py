"""machine2 cycle25 -- POST-HOC (labelled) audit of the band rule that failed at exactly one rung.

The committed band is m1-L150's: halfwidth = 2*|ty6 - ty4|, a next-order difference used as an error
estimate.  At R1d (the SMALLEST displacement on the ladder) the measured residual |ty4 - exact| is
10.05x |ty6 - ty4|, so the band missed in the NON-conservative direction.

*** ANNOTATED IN PLACE, machine2 cycle 26 -- THE TWO SENTENCES ABOVE ARE WRONG AND ARE LEFT VISIBLE.
    This script's OWN committed output (data/machine2_cycle25_bandaudit.out) records R1d at
    err/band = 0.5023, IN band, and machine2's independent cycle-26 recompute
    (data/machine2_cycle26_bandlaw.json) gives ratio = 0.502257179794.  The band did NOT miss at
    R1d, and no rung of the cycle-25 ladder missed.  The prose is stale relative to the output it
    shipped with in the same commit (eb45f2b); the OUTPUT is authoritative.  Neither m1's
    (de9ab99) nor m3's (718aa6f) verification caught it, because both verified numbers and this
    defect lives in a docstring no verification battery reads.  See
    machine2-cycle26-scored-the-band-rule-is-an-identity-and-its-failure-boundary-is-reachable.md
    section 6. ***  This script measures the
whole Taylor sequence ty2..ty8 at every rung against the exact value already produced by the sealed
runner, and asks whether |ty_{K+2} - ty_K| is an error estimator at all outside the asymptotic regime.
Nothing here is graded; it was written after the scored values existed and says so.
"""
import json, os, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
half = mp.mpf(1) / 2
P = json.load(open(os.path.join(HERE, "c25_prereg.json")))
SC = json.load(open(os.path.join(HERE, "c25_scored.json")))
S = P["site"]
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
t0 = time.time()
bases = [Basis(g, degree=8) for g in gens]
G = gram(); K200 = mat(tgt["K_T200"])
g_a = mp.mpf(S["g_a"]); g_b = mp.mpf(S["g_b"]); g_bs = mp.mpf(S["g_bs"])
GA1, GA2, GB1, GB2 = [mp.mpf(x) for x in S["removed"]]
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))


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
base = K200 - remA - remB
DERS = {}
for nm, g0 in (("a", g_a), ("b", g_b), ("bs", g_bs)):
    s0 = mp.mpc(half, g0)
    DERS[nm] = [[sum(w * (x ** k) * mp.exp(s0 * x) for x, w in zip(b.xs, b.ws)) for k in range(11)]
                for b in bases]


def quadT(nm, d, K):
    up = [sum(DERS[nm][i][k] * (d ** k) / mp.factorial(k) for k in range(K + 1)) for i in range(N)]
    uq = [sum(DERS[nm][i][k] * ((-d) ** k) / mp.factorial(k) for k in range(K + 1)) for i in range(N)]
    return Smat(up, uq)


RUNGS = json.load(open(os.path.join(HERE, "c25_scored.json")))["rungs"]
ORDERS = [2, 4, 6, 8]
rows = {}
print("%-5s %9s %9s   %s" % ("rung", "d_a", "d_b", "  |ty_K - exact| for K = 2,4,6,8   then est=2|ty6-ty4| and ratio"))
for r, info in RUNGS.items():
    da = mp.mpf(info["d_a"]); db = mp.mpf(info["d_b"]); site = info["site"]
    ex = mp.mpf(info["lam"])
    q0b = qB0 if site == "b" else qB0s
    tys = {}
    for K in ORDERS:
        A = quadT("a", da, K) if da != 0 else qA0
        B_ = quadT(site, db, K) if db != 0 else q0b
        tys[K] = lam(base + A + B_, G)[0]
    est = 2 * abs(tys[6] - tys[4])
    err4 = abs(tys[4] - ex)
    rows[r] = {"exact": mp.nstr(ex, 18), **{("ty%d" % K): mp.nstr(tys[K], 18) for K in ORDERS},
               "err_ty4": mp.nstr(err4, 8), "band_2x_ty6_ty4": mp.nstr(est, 8),
               "err_over_band": mp.nstr(err4 / est, 8),
               "err_ty6": mp.nstr(abs(tys[6] - ex), 8), "err_ty8": mp.nstr(abs(tys[8] - ex), 8),
               "in_band": bool(err4 <= est)}
    print("%-5s %9s %9s   %10s %10s %10s %10s | band %10s  err/band %8s  %s"
          % (r, mp.nstr(da, 3), mp.nstr(db, 5),
             mp.nstr(abs(tys[2] - ex), 4), mp.nstr(err4, 4), mp.nstr(abs(tys[6] - ex), 4),
             mp.nstr(abs(tys[8] - ex), 4), mp.nstr(est, 4), mp.nstr(err4 / est, 4),
             "IN" if err4 <= est else "OUT"), flush=True)
json.dump(rows, open(os.path.join(HERE, "c25_bandaudit.json"), "w"), indent=1)
print("\ndone %.1fs" % (time.time() - t0))
