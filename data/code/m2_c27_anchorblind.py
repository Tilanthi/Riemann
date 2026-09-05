"""machine2 cycle27 -- ATTACK on the trap-#117 remedy as worded ("the only defence is an external
anchor ... one published certified number (here: launch lam_min)").

CLAIM UNDER ATTACK (m1, machine1-trap-register.md #117 @ 0692b52, and m1-L160 sect2 @ 414c550):
    "internal-consistency checks are blind to this by construction ... the only defence is an
     external anchor -- a published certified value asserted before any swept configuration runs"
    Remedy as worded: "every port of certified machinery carries a hard EXTERNAL anchor assertion
    before any swept configuration is computed -- ONE published certified number (here: launch
    lam_min to its last digit)".

MY CONTENTION: the anchor's firing world is a PROPER SUBSET of the corruption space, and the
excluded region contains m1's OWN second defect.  His defect 2 (cross-form second term
conj(up_i) for conj(uq_i)) is EXACT at d = 0 by construction; his prescribed anchor is evaluated
at d = 0; therefore that anchor cannot see it.  He was rescued only because defect 1 (window ramp)
was co-present and does break d = 0.  A single-defect world with only defect 2 passes the remedy
and is wrong at every graded configuration.

This is the layer law from our own cycle-11 (d) recurring inside somebody's remedy: a check that
is sound at its own layer certifies nothing about the layer beneath it.  The launch anchor
certifies the basis / window / Gram / K-assembly layer.  Every graded number in cycles 23/25/26
lives in the DISPLACEMENT layer (quad -> Smat -> composition), which the launch anchor never
touches.

INSTRUMENT VARIANTS (all three run the identical published S2 site, same code path otherwise):
    clean : as published in cycle 25 (m2_c25_scored.py), machinery IMPORTED not transcribed
    c1    : m1 defect-2 transplant  -- quad()'s second term uses conj(up[i]) for conj(uq[i])
    c2    : m1 defect-1 transplant  -- theta()'s second exponential drops its (1-y) => ramp == 1/2

ANCHORS TESTED
    ANCHOR-U  untouched launch lam_min(K_T200, G)  = 1.1761206927485314567e-5
              (our own CERT line, c25_prereg.out; same object m1/m3 rebuild)
    ANCHOR-0  S2 composed launch lam_min           = 2.0004746865698620975e-5
              (m1 heat75 + heat81 "the certified CYCLE-25 value, to its last digit"; m3 L156)
              == the exact analogue of the anchor #117 prescribes
    ANCHOR-D  R0 displaced exact lam_min           = 1.9160562986370759475e-5
              (d_a = 0.1, d_b = 0; m1-L160 sect1 verified the ten committed rungs, worst rel 3.81e-20)
              == the anchor #117 does NOT prescribe, and the one this file argues for

INTERNAL CHECKS (the class #117 says is blind; measured here rather than asserted)
    I1  trace identity     sum_i lam_i  ==  tr(G^-1 F)
    I3  G-orthonormality   v_i^T G v_j  ==  delta_ij

Outputs c27_anchorblind_<variant>.json.  No prediction is read by this file.
"""
import json, os, sys, time
from mpmath import mp, exp

VARIANT = sys.argv[1]
assert VARIANT in ("clean", "c1", "c2")
mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("RH_REPO", "/shared/rh-exchange-repo/Riemann")

import m2_u_instrument as ui

if VARIANT == "c2":
    # m1 heat81 defect 1, transplanted verbatim in spirit: the second exponential loses its (1-y)
    def theta_corrupt(y):
        if y <= 0:
            return mp.mpf(0)
        if y >= 1:
            return mp.mpf(1)
        a = exp(-1 / y)
        b = exp(-1 / y)          # <-- was exp(-1/(1-y))
        return a / (a + b)
    ui.theta = theta_corrupt

import m2_witness_analysis as wa
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

half = mp.mpf(1) / 2
P = json.load(open(os.path.join(HERE, "c25_prereg.json")))
S = P["site"]
tgt = ui.load_target("s1/M8")
t0 = time.time()
bases = wa.bases                      # built at import, under the active (possibly corrupt) theta
G = gram()
K200 = mat(tgt["K_T200"])

g_a = mp.mpf(S["g_a"]); g_b = mp.mpf(S["g_b"])
GA1, GA2, GB1, GB2 = [mp.mpf(x) for x in S["removed"]]
DA = mp.mpf(S["delta_a"]); DC = mp.mpf(S["delta_c"])
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))


def quad(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            if VARIANT == "c1":
                # m1 heat81 defect 2, transplanted: second term's conj argument is up, not uq
                M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(up[i]))
            else:
                M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


def eig_full(F, Gm):
    L = mp.cholesky(Gm); Li = mp.inverse(L)
    B = Li * F * Li.T; B = (B + B.T) / 2
    E, V = mp.eigsy(B)
    idx = sorted(range(N), key=lambda i: E[i])
    return [E[i] for i in idx], [Li.T * mp.matrix([V[r, i] for r in range(N)]) for i in idx]


def bil(M, v, w):
    s = mp.mpf(0)
    for i in range(N):
        for j in range(N):
            s += v[i] * M[i, j] * w[j]
    return s


def trace_check(F, Gm, vals):
    T = mp.inverse(Gm) * F
    tr = sum(T[i, i] for i in range(N))
    return abs(sum(vals) - tr) / abs(tr)


def ortho_check(Gm, vecs):
    worst = mp.mpf(0)
    for i in range(N):
        for j in range(N):
            d = abs(bil(Gm, vecs[i], vecs[j]) - (1 if i == j else 0))
            worst = max(worst, d)
    return worst


out = {"variant": VARIANT, "dps": mp.dps}

# ---- untouched launch (ANCHOR-U layer: basis/window/Gram/K only) ----
uvals, uvecs = eig_full(K200, G)
out["untouched_launch"] = mp.nstr(uvals[0], 20)

# ---- S2 composed launch (ANCHOR-0: the anchor #117 prescribes) ----
qA0, qB0 = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b)
base = K200 - remA - remB
Lm = base + qA0 + qB0
lvals, lvecs = eig_full(Lm, G)
out["composed_launch"] = mp.nstr(lvals[0], 20)
out["I1_launch"] = mp.nstr(trace_check(Lm, G, lvals), 6)
out["I3_launch"] = mp.nstr(ortho_check(G, lvecs), 6)

# ---- rungs ----
RUNGS = {"R0": (DA, mp.mpf(0)), "R1": (mp.mpf(0), DC), "R2": (DA, DC)}
res = {}
for r, (da, db) in RUNGS.items():
    A = quad(da, g_a) if da != 0 else qA0
    B_ = quad(db, g_b) if db != 0 else qB0
    F = base + A + B_
    vals, vecs = eig_full(F, G)
    res[r] = {"lam": mp.nstr(vals[0], 20),
              "shift": mp.nstr(vals[0] - lvals[0], 18),
              "I1": mp.nstr(trace_check(F, G, vals), 6),
              "I3": mp.nstr(ortho_check(G, vecs), 6),
              "ovl_v0": mp.nstr(abs(bil(G, vecs[0], lvecs[0])), 10)}
    print("%-4s lam %s  I1 %s  I3 %s" % (r, res[r]["lam"], res[r]["I1"], res[r]["I3"]), flush=True)
out["rungs"] = res

sA = mp.mpf(res["R0"]["shift"]); sB = mp.mpf(res["R1"]["shift"]); sh = mp.mpf(res["R2"]["shift"])
D = sh - sA - sB
Fn = P["functionals"]
fa = abs(mp.mpf(Fn["f_a"])); fb = abs(mp.mpf(Fn["f_b"]))
out["R2_defect"] = {"s_A": mp.nstr(sA, 14), "s_B": mp.nstr(sB, 14), "shift": mp.nstr(sh, 14),
                    "D": mp.nstr(D, 14), "R_c": mp.nstr(abs(D) / (fa + fb), 10)}
out["seconds"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(HERE, "c27_anchorblind_%s.json" % VARIANT), "w"), indent=1)
print(json.dumps(out, indent=1))
