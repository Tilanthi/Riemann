"""machine2 cycle23 -- SINGLE-PAIR shift table (design data only; no composed value).

s_X(delta) = lam_min(K200 - rem_X + quad_X(delta)) - lam_min(K200 - rem_X + quad_X(0))

This is the operational "sum-of-single-pair-effects" input.  It is measured
PER GAP, one insertion at a time, so it contains no information about the composed
(two-quadruple) object, which is the scored quantity and is NOT touched here.
"""
import json, os, sys, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
half = mp.mpf(1) / 2
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zeros210.json")))]
up200 = [g for g in gam if g <= 200]
t0 = time.time()
bases = [Basis(g, degree=8) for g in gens]
G = gram(); K200 = mat(tgt["K_T200"])


def quad(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


DELTAS = ["0.05", "0.1", "0.2"]
GAPS = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else ["0", "2"])]
out = {}
for k in GAPS:
    g1, g2 = up200[k], up200[k + 1]
    rem = zero_pair_K(mp.mpc(half, g1)) + zero_pair_K(mp.mpc(half, g2))
    base = K200 - rem
    print("\n### gap k=%d  [%s, %s]" % (k, mp.nstr(g1, 9), mp.nstr(g2, 9)), flush=True)
    print("%12s %16s %16s %16s %16s %10s" % ("gamma_0", "lam_launch", "s(0.05)", "s(0.1)", "s(0.2)", "gap1-0"))
    rows = []
    for m in range(9):
        g0 = g1 + (g2 - g1) * m / mp.mpf(8)
        L = base + quad(mp.mpf(0), g0)
        ev = lam(L, G)
        l0 = ev[0]
        ss = []
        for d in DELTAS:
            ss.append(lam(base + quad(mp.mpf(d), g0), G)[0] - l0)
        rows.append({"g0": mp.nstr(g0, 20), "lam_launch": mp.nstr(l0, 16),
                     "s": {d: mp.nstr(v, 14) for d, v in zip(DELTAS, ss)},
                     "spec_gap": mp.nstr(ev[1] - ev[0], 10)})
        print("%12s %16s %16s %16s %16s %10s" % (mp.nstr(g0, 9), mp.nstr(l0, 10),
              mp.nstr(ss[0], 9), mp.nstr(ss[1], 9), mp.nstr(ss[2], 9), mp.nstr(ev[1]-ev[0], 6)), flush=True)
    out[str(k)] = {"g1": mp.nstr(g1, 20), "g2": mp.nstr(g2, 20), "rows": rows}

json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shifts.json"), "w"), indent=1)
print("\ndone %.1fs" % (time.time() - t0))
