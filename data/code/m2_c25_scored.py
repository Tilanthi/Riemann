"""machine2 cycle25 -- THE SCORED RUNNER for site S2.  Hash-frozen and pushed before it was run.

Reads the committed site from c25_prereg.json and evaluates, with the UNTRUNCATED quadruple:
  * lam_min (generalized, metric G) at the launch and at every rung of the ladder,
  * the additivity defect D = shift - s_A - s_B and R_c = |D|/(|f_a|+|f_b|) at R2/R3/R3b/R4,
  * the eigenvector continuity census (G-overlap of each perturbed ground vector with the launch
    ground vector and with the launch FIRST EXCITED vector) -- the level-crossing test,
  * the T-truncation budget at the launch from the 123 zeros 200 < gamma <= 400 at DEGREE 10
    (deg 8 is eight orders wrong out there -- cycle-22 own-failure #2, cycle-24 V5).

No prediction is recomputed here and nothing in this file reads the prediction values.
"""
import json, os, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target, breakpoints, gl_nodes
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
half = mp.mpf(1) / 2
P = json.load(open(os.path.join(HERE, "c25_prereg.json")))
S = P["site"]
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open(os.path.join(HERE, "zeros210.json")))]
tail = [mp.mpf(g) for g in json.load(open(os.path.join(HERE, "tailzeros.json")))]
t0 = time.time()
bases = [Basis(g, degree=8) for g in gens]
G = gram(); K200 = mat(tgt["K_T200"])
g_a = mp.mpf(S["g_a"]); g_b = mp.mpf(S["g_b"]); g_bs = mp.mpf(S["g_bs"])
GA1, GA2, GB1, GB2 = [mp.mpf(x) for x in S["removed"]]
DA = mp.mpf(S["delta_a"]); DC = mp.mpf(S["delta_c"]); D3 = mp.mpf("0.20"); D4 = mp.mpf("0.30")
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))


def quad(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
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


qA0, qB0, qB0s = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b), quad(mp.mpf(0), g_bs)
base = K200 - remA - remB
LAUNCH = {"b": base + qA0 + qB0, "bs": base + qA0 + qB0s}
lv, lvec = {}, {}
for k, Lm in LAUNCH.items():
    vals, vecs = eig_full(Lm, G)
    lv[k] = vals; lvec[k] = vecs
print("launch  lam_min %s  gap %s" % (mp.nstr(lv["b"][0], 20), mp.nstr(lv["b"][1] - lv["b"][0], 10)))
print("launch' lam_min %s  gap %s" % (mp.nstr(lv["bs"][0], 20), mp.nstr(lv["bs"][1] - lv["bs"][0], 10)))

RUNGS = {"R0": (DA, mp.mpf(0), "b"), "R1": (mp.mpf(0), DC, "b"), "R2": (DA, DC, "b"),
         "R1b": (mp.mpf(0), D3, "b"), "R3": (DA, D3, "b"),
         "R1e": (mp.mpf(0), D4, "b"), "R3b": (DA, D4, "b"),
         "R0s": (DA, mp.mpf(0), "bs"), "R1d": (mp.mpf(0), DA, "bs"), "R4": (DA, DA, "bs")}
res = {}
print("\n%-5s %8s %10s %24s %18s %10s %10s" % ("rung", "d_a", "d_b", "lam_min EXACT", "shift", "ovl_v0", "ovl_v1"))
for r, (da, db, site) in RUNGS.items():
    A = quad(da, g_a) if da != 0 else qA0
    B_ = quad(db, g_b if site == "b" else g_bs) if db != 0 else (qB0 if site == "b" else qB0s)
    vals, vecs = eig_full(base + A + B_, G)
    o0 = abs(bil(G, vecs[0], lvec[site][0]))
    o1 = abs(bil(G, vecs[0], lvec[site][1]))
    res[r] = {"d_a": mp.nstr(da, 25), "d_b": mp.nstr(db, 25), "site": site,
              "lam": mp.nstr(vals[0], 20), "spectrum": [mp.nstr(x, 12) for x in vals],
              "shift": mp.nstr(vals[0] - lv[site][0], 18), "fires": bool(vals[0] < 0),
              "ovl_launch_v0": mp.nstr(o0, 10), "ovl_launch_v1": mp.nstr(o1, 10)}
    print("%-5s %8s %10s %24s %18s %10s %10s"
          % (r, mp.nstr(da, 4), mp.nstr(db, 6), mp.nstr(vals[0], 16),
             mp.nstr(vals[0] - lv[site][0], 10), mp.nstr(o0, 6), mp.nstr(o1, 6)), flush=True)

F = P["functionals"]
fmap = {"R2": ("f_a", "f_b"), "R3": ("f_a", "f_b3"), "R3b": ("f_a", "f_b4"), "R4": ("f_as", "f_bs")}
arms = {"R2": ("R0", "R1"), "R3": ("R0", "R1b"), "R3b": ("R0", "R1e"), "R4": ("R0s", "R1d")}
defects = {}
print("\n%-4s %16s %16s %16s %16s %10s %10s" % ("rung", "s_A", "s_B", "shift", "D", "R_c", "|D|/|sh|%"))
for r in ("R2", "R3", "R3b", "R4"):
    a, b = arms[r]
    sA = mp.mpf(res[a]["shift"]); sB = mp.mpf(res[b]["shift"]); sh = mp.mpf(res[r]["shift"])
    D = sh - sA - sB
    fa = abs(mp.mpf(F[fmap[r][0]])); fb = abs(mp.mpf(F[fmap[r][1]]))
    defects[r] = {"s_A": mp.nstr(sA, 14), "s_B": mp.nstr(sB, 14), "shift": mp.nstr(sh, 14),
                  "D": mp.nstr(D, 14), "R_c": mp.nstr(abs(D) / (fa + fb), 10),
                  "frac_pct": mp.nstr(100 * abs(D / sh), 8),
                  "cross_2nd": P["second_order"][r][2],
                  "D_over_cross": mp.nstr(D / mp.mpf(P["second_order"][r][2]), 8)}
    print("%-4s %16s %16s %16s %16s %10s %10s"
          % (r, mp.nstr(sA, 8), mp.nstr(sB, 8), mp.nstr(sh, 8), mp.nstr(D, 8),
             defects[r]["R_c"], defects[r]["frac_pct"]))
ratio = mp.mpf(defects["R2"]["frac_pct"]) / mp.mpf(defects["R3"]["frac_pct"])
print("\nPRIMARY ratio (cancellation defect fraction)/(ordinary opposing) = %s" % mp.nstr(ratio, 8))

# ---- truncation budget at DEGREE 10 (deg 8 is 8 orders wrong at gamma ~ 350) ----
DEG = 10
b10 = [Basis(g, degree=DEG) for g in gens]
allpts = sorted(set(sum([breakpoints(bb.bumps) for bb in b10], [])))
ivs = [(allpts[k], allpts[k + 1]) for k in range(len(allpts) - 1) if allpts[k + 1] > allpts[k]]
xs, ws = [], []
for (aa, bb) in ivs:
    for (x, w) in gl_nodes(aa, bb, DEG):
        xs.append(x); ws.append(w)
vv = [[bb.phi(x) for x in xs] for bb in b10]
G10 = mp.matrix(N, N)
for i in range(N):
    for j in range(i, N):
        s = mp.mpf(0)
        for k in range(len(xs)):
            s += ws[k] * vv[i][k] * vv[j][k]
        G10[i, j] = s; G10[j, i] = s
dK = mp.matrix(N, N)
for g in tail:
    u = [bb.u(mp.mpc(half, g)) for bb in b10]
    for i in range(N):
        for j in range(N):
            dK[i, j] += 2 * mp.re(u[i] * mp.conj(u[j]))
dmax = max(abs(dK[i, j]) for i in range(N) for j in range(N))
lam_t = lam(LAUNCH["b"] + dK, G)[0]
budget = lam_t - lv["b"][0]
print("\nT-budget deg %d, 123 zeros 200<gamma<=400: |dK|max %s   d lam_min %s"
      % (DEG, mp.nstr(dmax, 8), mp.nstr(budget, 8)))
smallest = min(abs(mp.mpf(res[r]["shift"])) for r in RUNGS if mp.mpf(res[r]["shift"]) != 0)
print("smallest |shift| on the ladder / budget = %s" % mp.nstr(smallest / abs(budget), 8))

json.dump({"launch": {"lam": mp.nstr(lv["b"][0], 20), "lam_s": mp.nstr(lv["bs"][0], 20),
                      "spectrum": [mp.nstr(x, 14) for x in lv["b"]],
                      "spectrum_s": [mp.nstr(x, 14) for x in lv["bs"]]},
           "rungs": res, "defects": defects, "ratio_R2_over_R3": mp.nstr(ratio, 10),
           "tail_budget": {"deg": DEG, "dK_max": mp.nstr(dmax, 10), "dlam": mp.nstr(budget, 10),
                           "smallest_shift_over_budget": mp.nstr(smallest / abs(budget), 8)}},
          open(os.path.join(HERE, "c25_scored.json"), "w"), indent=1)
print("\ndone %.1fs" % (time.time() - t0))
