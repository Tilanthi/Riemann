"""POST-HOC EXTENSION (NOT pre-registered, and labelled as such): does the corruption that the
prescribed launch anchor cannot see FLIP the FIRES verdict at the one cycle-25 rung that fires?
Same code path as m2_c27_anchorblind.py, rungs R0/R1e/R3b instead of R0/R1/R2.
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
RUNGS = {"R0": (DA, mp.mpf(0)), "R1e": (mp.mpf(0), mp.mpf("0.30")), "R3b": (DA, mp.mpf("0.30"))}
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

sA = mp.mpf(res["R0"]["shift"]); sB = mp.mpf(res["R1e"]["shift"]); sh = mp.mpf(res["R3b"]["shift"])
D = sh - sA - sB
Fn = P["functionals"]
fa = abs(mp.mpf(Fn["f_a"])); fb = abs(mp.mpf(Fn["f_b4"]))
out["R3b_defect"] = {"s_A": mp.nstr(sA, 14), "s_B": mp.nstr(sB, 14), "shift": mp.nstr(sh, 14),
                    "D": mp.nstr(D, 14), "R_c": mp.nstr(abs(D) / (fa + fb), 10)}
out["seconds"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(HERE, "c27_firesflip_%s.json" % VARIANT), "w"), indent=1)
print(json.dumps(out, indent=1))
