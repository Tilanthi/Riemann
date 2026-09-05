"""machine2 cycle27 -- THE SCORED RUNNER for SITE S3 = m1's corrected pick D4 (m1-L155a, b4f784d).

HASH-FROZEN AND PUSHED UNRUN.  Under m1's +12 h reveal gap (m1 de9ab99, m3 9129bd6, adopted by me
at 3454981) this file is not executed until at least 12 h after the prereg commit lands.

It reads the committed site + Taylor ladder from c27_s3_prereg.json and evaluates, with the
UNTRUNCATED quadruple:
  * exact lam_min (generalized, metric G) at the launch, the launch' (same-sign control) and at
    every rung of the ten-rung ladder,
  * the additivity defect D = shift - s_A - s_B and R_c = |D|/(|f_a|+|f_b|) at R2/R3/R3b/R4,
  * D / X_2nd against the pre-registered PT band (the family-vs-site test),
  * the eigenvector continuity census (G-overlap with the launch ground and first-excited vectors),
  * and -- discharging my own ask 1 to m1, granted in his L160 sect3 -- the band statistic REPORTED
    WITH r = |ty6-exact|/|ty4-exact| AND t = (exact-ty6)/(ty6-ty4) ALONGSIDE, never alone, because
    cycle 26 proved ratio = 0.5|1+t| is an IDENTITY and the published window [0.500,0.543] is NOT
    injective in r.  The surviving device is the tripwire: same-sign AND |t| <= 3.

TRAP #117 ADOPTION, AS AMENDED BY CYCLE 27 LEG B: this is a PORT of the cycle-25 S2 machinery, so
it carries a TWO-POINT external anchor -- ANCHOR-0 (S2 composed launch, d = 0) and ANCHOR-D (S2 R0
exact at d_a = 0.1, DISPLACED) -- plus m1's own S3 launch value.  Leg B measured that a d = 0
anchor alone is blind to the whole displacement layer: a transplant of m1's own cross-form defect
left ANCHOR-0 bit-identical while flipping the FIRES verdict at cycle-25's R3b.
"""
import json, os, time
from mpmath import mp

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("RH_REPO", "/shared/rh-exchange-repo/Riemann")
mp.dps = 40
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

half = mp.mpf(1) / 2
P = json.load(open(os.path.join(HERE, "c27_s3_prereg.json")))
S = P["geometry"]
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
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


def anchor(name, got, want, tol):
    rel = abs(got - mp.mpf(want)) / abs(mp.mpf(want))
    print("ANCHOR %-9s got %s  want %s  rel %s  %s"
          % (name, mp.nstr(got, 20), want, mp.nstr(rel, 4), "PASS" if rel < mp.mpf(tol) else "FAIL"))
    if not (rel < mp.mpf(tol)):
        raise SystemExit("ANCHOR %s FAILED -- aborting before any scored value is computed" % name)


# ---- two-point external anchor from the S2 source path, BEFORE any S3 value is computed --------
S2 = json.load(open(os.path.join(HERE, "c25_prereg.json")))["site"]
s2_ga = mp.mpf(S2["g_a"]); s2_gb = mp.mpf(S2["g_b"])
s2rem = sum((zero_pair_K(mp.mpc(half, mp.mpf(x))) for x in S2["removed"]), mp.matrix(N, N))
s2base = K200 - s2rem
anchor("ANCHOR-0", eig_full(s2base + quad(mp.mpf(0), s2_ga) + quad(mp.mpf(0), s2_gb), G)[0][0],
       "2.0004746865698620975e-5", "1e-19")
anchor("ANCHOR-D", eig_full(s2base + quad(mp.mpf("0.1"), s2_ga) + quad(mp.mpf(0), s2_gb), G)[0][0],
       "1.9160562986370759475e-5", "1e-19")

# ---- site S3 ------------------------------------------------------------------------------------
g_a = mp.mpf(S["g_a"]); g_b = mp.mpf(S["g_b"]); g_bs = mp.mpf(S["g_bs"])
GA1, GA2, GB1, GB2 = [mp.mpf(x) for x in S["removed"]]
DA = mp.mpf(S["delta_a"]); DC = mp.mpf(S["delta_c"])
D3 = mp.mpf(S["delta_b_R3"]); D4v = mp.mpf(S["delta_b_R3b"])
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))
base = K200 - remA - remB
qA0, qB0, qB0s = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b), quad(mp.mpf(0), g_bs)
LAUNCH = {"b": base + qA0 + qB0, "bs": base + qA0 + qB0s}
lv, lvec = {}, {}
for k, Lm in LAUNCH.items():
    vals, vecs = eig_full(Lm, G)
    lv[k] = vals; lvec[k] = vecs
anchor("S3launch", lv["b"][0], "1.2965524199220303e-5", "1e-14")
print("launch  lam_min %s  gap %s" % (mp.nstr(lv["b"][0], 20), mp.nstr(lv["b"][1] - lv["b"][0], 10)))
print("launch' lam_min %s  gap %s" % (mp.nstr(lv["bs"][0], 20), mp.nstr(lv["bs"][1] - lv["bs"][0], 10)))

RUNGS = {"R0": (DA, mp.mpf(0), "b"), "R1": (mp.mpf(0), DC, "b"), "R2": (DA, DC, "b"),
         "R1b": (mp.mpf(0), D3, "b"), "R3": (DA, D3, "b"),
         "R1e": (mp.mpf(0), D4v, "b"), "R3b": (DA, D4v, "b"),
         "R0s": (DA, mp.mpf(0), "bs"), "R1d": (mp.mpf(0), DA, "bs"), "R4": (DA, DA, "bs")}
res = {}
print("\n%-5s %8s %8s %24s %18s %10s %10s" % ("rung", "d_a", "d_b", "lam_min EXACT", "shift", "ovl_v0", "ovl_v1"))
for r, (da, db, site) in RUNGS.items():
    A = quad(da, g_a) if da != 0 else qA0
    B_ = quad(db, g_b if site == "b" else g_bs) if db != 0 else (qB0 if site == "b" else qB0s)
    vals, vecs = eig_full(base + A + B_, G)
    o0 = abs(bil(G, vecs[0], lvec[site][0])); o1 = abs(bil(G, vecs[0], lvec[site][1]))
    res[r] = {"d_a": mp.nstr(da, 25), "d_b": mp.nstr(db, 25), "site": site,
              "lam": mp.nstr(vals[0], 20), "spectrum": [mp.nstr(x, 12) for x in vals],
              "shift": mp.nstr(vals[0] - lv[site][0], 18), "fires": bool(vals[0] < 0),
              "ovl_launch_v0": mp.nstr(o0, 10), "ovl_launch_v1": mp.nstr(o1, 10)}
    print("%-5s %8s %8s %24s %18s %10s %10s"
          % (r, mp.nstr(da, 4), mp.nstr(db, 6), mp.nstr(vals[0], 16),
             mp.nstr(vals[0] - lv[site][0], 10), mp.nstr(o0, 6), mp.nstr(o1, 6)), flush=True)

# ---- defects + the family-vs-site test ---------------------------------------------------------
F = P["functionals"]
fmap = {"R2": ("f_a", "f_b"), "R3": ("f_a", "f_b3"), "R3b": ("f_a", "f_b4"), "R4": ("f_as", "f_bs")}
arms = {"R2": ("R0", "R1"), "R3": ("R0", "R1b"), "R3b": ("R0", "R1e"), "R4": ("R0s", "R1d")}
defects = {}
print("\n%-4s %16s %16s %16s %10s %10s %12s" % ("rung", "s_A", "s_B", "D", "R_c", "|D|/|sh|%", "D/X_2nd"))
for r in ("R2", "R3", "R3b", "R4"):
    a, b = arms[r]
    sA = mp.mpf(res[a]["shift"]); sB = mp.mpf(res[b]["shift"]); sh = mp.mpf(res[r]["shift"])
    D = sh - sA - sB
    fa = abs(mp.mpf(F[fmap[r][0]])); fb = abs(mp.mpf(F[fmap[r][1]]))
    X = mp.mpf(P["second_order"][r][2])
    defects[r] = {"s_A": mp.nstr(sA, 14), "s_B": mp.nstr(sB, 14), "shift": mp.nstr(sh, 14),
                  "D": mp.nstr(D, 14), "R_c": mp.nstr(abs(D) / (fa + fb), 10),
                  "frac_pct": mp.nstr(100 * abs(D / sh), 8),
                  "cross_2nd": P["second_order"][r][2], "D_over_cross": mp.nstr(D / X, 8),
                  "PT": P["PT_by_rung"][r]}
    print("%-4s %16s %16s %16s %10s %10s %12s"
          % (r, mp.nstr(sA, 8), mp.nstr(sB, 8), mp.nstr(D, 8), defects[r]["R_c"],
             defects[r]["frac_pct"], defects[r]["D_over_cross"]))
ratio_R2_R3 = mp.mpf(defects["R2"]["frac_pct"]) / mp.mpf(defects["R3"]["frac_pct"])
print("\nPRIMARY ratio (cancellation defect fraction)/(ordinary opposing) = %s" % mp.nstr(ratio_R2_R3, 8))

# ---- band statistic, ALWAYS with r and t alongside (my ask 1, granted m1-L160 sect3) -----------
band = {}
print("\n%-5s %14s %14s %14s %10s %10s %8s" % ("rung", "|ty4-exact|", "band=2|ty6-ty4|", "ratio", "r", "t", "tripwire"))
for r in RUNGS:
    ty4 = mp.mpf(P["taylor"][r]["ty4"]); ty6 = mp.mpf(P["taylor"][r]["ty6"])
    ex = mp.mpf(res[r]["lam"])
    e4 = abs(ty4 - ex); e6 = abs(ty6 - ex)
    bw = 2 * abs(ty6 - ty4)
    rr = e6 / e4 if e4 != 0 else mp.mpf("nan")
    tt = (ex - ty6) / (ty6 - ty4) if ty6 != ty4 else mp.mpf("nan")
    same = (ty6 - ty4) * (ex - ty4) > 0
    trip = bool(same and abs(tt) <= 3)
    band[r] = {"err_ty4": mp.nstr(e4, 12), "band": mp.nstr(bw, 12), "ratio": mp.nstr(e4 / bw, 12),
               "r": mp.nstr(rr, 12), "t": mp.nstr(tt, 12), "same_sign": bool(same),
               "tripwire_ok": trip, "band_holds": bool(e4 <= bw)}
    print("%-5s %14s %14s %14s %10s %10s %8s"
          % (r, mp.nstr(e4, 8), mp.nstr(bw, 8), mp.nstr(e4 / bw, 8), mp.nstr(rr, 6),
             mp.nstr(tt, 6), "OK" if trip else "**"))

out = {"cycle": 27, "site": "S3 = D4", "prereg_sha256": P.get("self_sha256"),
       "launch": {"lam": mp.nstr(lv["b"][0], 20), "lam_s": mp.nstr(lv["bs"][0], 20)},
       "rungs": res, "defects": defects, "ratio_R2_over_R3": mp.nstr(ratio_R2_R3, 10),
       "band": band, "seconds": round(time.time() - t0, 1)}
json.dump(out, open(os.path.join(HERE, "c27_s3_scored.json"), "w"), indent=1)
print("\nscored in %.1fs" % (time.time() - t0))
