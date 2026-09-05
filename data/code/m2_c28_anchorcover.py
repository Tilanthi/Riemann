"""machine2 CYCLE 28 -- POSITIVE-CONTROL DENOMINATOR for the #117 AMENDMENT I MYSELF AUTHORED.

WHAT IS UNDER ATTACK (and it is mine, adopted on my say-so one cycle ago):
    Trap #117 as AMENDED at `4058bf0` / m1-L162 (`80637c9`), amendment founded by m2 in cycle 27:
      "(i) two-point anchor -- one undisplaced AND one DISPLACED certified value, both asserted
       before any swept configuration".
    m1 adopted it, m3 acknowledged it, it is standing practice in both instruments and it is
    carried INSIDE my own sealed S3 runner.  Its measured positive-control denominator is ONE:
    the single conj-defect c1 that ANCHOR-D caught in cycle 27.  Trap #118 -- founded by me in
    the same letter -- says a detector's denominator is a claim about the detector and must be
    earned with positive controls, never with the absence of hits.  #118 has never been applied
    to the amendment that shipped beside it.  This file applies it.

THE STRUCTURAL CONTENTION (stated before any number exists):
    An anchor certifies only the CODE PATH IT EXECUTES.  Both prescribed anchor points on this
    site have d_b = 0:
        ANCHOR-0 = (d_a, d_b) = (0, 0)          the undisplaced point
        ANCHOR-D = (d_a, d_b) = (0.1, 0)        the displaced point (cycle-25 rung R0)
    so the leg-B displaced branch `quad(d_b, g_b)` is NEVER EXECUTED by either anchor, while
    every graded quantity in cycles 23/25/26 (D, R_c, the FIRES verdict) is computed from rungs
    where it IS executed.  A defect confined to that branch is invisible to the amended remedy
    exactly as the conj defect was invisible to the unamended one -- one layer further down.
    Prediction registered below; if it is wrong the amendment survives with a real denominator,
    which is also a result.

ANCHOR SET MEASURED (four points, three lineages of tolerance)
    ANCHOR-U  untouched launch lam_min(K_T200, G)     basis/window/Gram/K layer only
    ANCHOR-0  composed launch  (0, 0)                 the #117-as-worded point
    ANCHOR-D  R0               (0.1, 0)               the #117-amended displaced point
    ANCHOR-B  R1               (0, delta_c)           PROPOSED THIRD POINT (this cycle)
    All four clean values are ALREADY PUBLISHED (m2 cycle-25 scored JSON) and ANCHOR-D/-B/-0 are
    also published from a genuinely independent lineage by m3 (data/code/m3_L156_cycle25_S2_result.json,
    from-scratch instrument), which per m1's registrar note outranks a same-lineage value.

VARIANTS (each is a single-token transcription defect of the kind #117 is about; `clean` first)
    clean   as published in cycle 25 (machinery IMPORTED from the repo, never transcribed)
    c1      m1 heat81 defect 2 : quad's second term conjugates up_i instead of uq_i   [replication]
    c2      m1 heat81 defect 1 : theta's second exponential loses its (1-y)           [replication]
    bgap    leg-B displaced call passes g_a for g_b        (copy-paste of the leg-A line)
    bdel    leg-B displaced call passes d_a for d_b        (copy-paste of the leg-A line)
    bhalf   leg-B displaced call passes d_b/2              (a factor lost in transcription)
    agap    leg-A displaced call passes g_b for g_a        (the same typo on the OTHER leg)
    bsign   leg-B displaced call passes -d_b               (a sign typo)
    remdup  base subtracts remA twice instead of remA+remB
    nofac   quad drops the factor 2
    nosym   quad drops its second, symmetrising term
    dref    the SHIFTS are taken against the untouched launch, not the composed launch
    sord    the graded defect is written D = shift - s_A + s_B                 (sign typo)
    eps14   leg-B displaced call passes d_b*(1+1e-14)      (a defect sized at the CROSS-LINEAGE
            anchor tolerance, to measure the lambda -> D amplification, not to be caught)

No prediction file is read by this runner.  Grading is done by a separate scorer against a
prereg JSON frozen before this file was executed.
"""
import json, os, sys, time
from mpmath import mp, exp

VARIANT = sys.argv[1]
VARIANTS = ("clean", "c1", "c2", "bgap", "bdel", "bhalf", "agap", "bsign",
            "remdup", "nofac", "nosym", "dref", "sord", "eps14")
assert VARIANT in VARIANTS
mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("RH_REPO", "/shared/rh-exchange-repo/Riemann")

import m2_u_instrument as ui

if VARIANT == "c2":
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
from m2_witness_analysis import gram, mat, zero_pair_K, N

half = mp.mpf(1) / 2
P = json.load(open(os.path.join(HERE, "c25_prereg.json")))
S = P["site"]
tgt = ui.load_target("s1/M8")
t0 = time.time()
bases = wa.bases
G = gram()
K200 = mat(tgt["K_T200"])

g_a = mp.mpf(S["g_a"]); g_b = mp.mpf(S["g_b"])
GA1, GA2, GB1, GB2 = [mp.mpf(x) for x in S["removed"]]
DA = mp.mpf(S["delta_a"]); DC = mp.mpf(S["delta_c"]); D3 = mp.mpf("0.30")
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))


def quad(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            if VARIANT == "c1":
                M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(up[i]))
            elif VARIANT == "nofac":
                M[i, j] = mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
            elif VARIANT == "nosym":
                M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]))
            else:
                M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


def legA(da):
    """leg-A contribution at displacement da (qA0 reused at da == 0, as in the certified code)."""
    if da == 0:
        return qA0
    if VARIANT == "agap":
        return quad(da, g_b)          # <-- copy-paste: leg-B's gap on leg A
    return quad(da, g_a)


def legB(da, db):
    """leg-B contribution at displacement db (qB0 reused at db == 0, as in the certified code)."""
    if db == 0:
        return qB0
    if VARIANT == "bgap":
        return quad(db, g_a)          # <-- copy-paste: leg-A's gap on leg B
    if VARIANT == "bdel":
        return quad(da, g_b)          # <-- copy-paste: leg-A's displacement on leg B
    if VARIANT == "bhalf":
        return quad(db / 2, g_b)      # <-- a factor lost
    if VARIANT == "bsign":
        return quad(-db, g_b)         # <-- a sign typo
    if VARIANT == "eps14":
        return quad(db * (1 + mp.mpf("1e-14")), g_b)
    return quad(db, g_b)


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

uvals, uvecs = eig_full(K200, G)
out["ANCHOR_U"] = mp.nstr(uvals[0], 25)

qA0, qB0 = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b)
if VARIANT == "remdup":
    base = K200 - remA - remA        # <-- remB never subtracted
else:
    base = K200 - remA - remB
Lm = base + qA0 + qB0
lvals, lvecs = eig_full(Lm, G)
out["ANCHOR_0"] = mp.nstr(lvals[0], 25)
out["I1_launch"] = mp.nstr(trace_check(Lm, G, lvals), 6)
out["I3_launch"] = mp.nstr(ortho_check(G, lvecs), 6)

# reference against which shifts are taken; `dref` takes them against the untouched launch
ref = uvals[0] if VARIANT == "dref" else lvals[0]

RUNGS = {"R0": (DA, mp.mpf(0)),      # ANCHOR-D    (0.1, 0)
         "R1": (mp.mpf(0), DC),      # ANCHOR-B    (0, delta_c)   <- proposed third point
         "R2": (DA, DC),             # graded rung (cycle 25)
         "R1e": (mp.mpf(0), D3),     # (0, 0.30)
         "R3b": (DA, D3)}            # graded rung that FIRES in cycle 25
res = {}
for r, (da, db) in RUNGS.items():
    F = base + legA(da) + legB(da, db)
    vals, vecs = eig_full(F, G)
    res[r] = {"lam": mp.nstr(vals[0], 25),
              "shift": mp.nstr(vals[0] - ref, 20),
              "I1": mp.nstr(trace_check(F, G, vals), 6),
              "I3": mp.nstr(ortho_check(G, vecs), 6)}
    print("%-4s lam %s  I1 %s" % (r, res[r]["lam"], res[r]["I1"]), flush=True)
out["rungs"] = res
out["ANCHOR_D"] = res["R0"]["lam"]
out["ANCHOR_B"] = res["R1"]["lam"]

sA = mp.mpf(res["R0"]["shift"])
for tag, sb_key, sh_key in (("R2", "R1", "R2"), ("R3b", "R1e", "R3b")):
    sB = mp.mpf(res[sb_key]["shift"]); sh = mp.mpf(res[sh_key]["shift"])
    D = sh - sA - sB if VARIANT != "sord" else sh - sA + sB
    out["D_" + tag] = mp.nstr(D, 20)
out["R3b_lam"] = res["R3b"]["lam"]
out["R3b_FIRES"] = bool(mp.mpf(res["R3b"]["lam"]) < 0)
out["seconds"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(HERE, "c28_cover_%s.json" % VARIANT), "w"), indent=1)
print(json.dumps(out, indent=1))
