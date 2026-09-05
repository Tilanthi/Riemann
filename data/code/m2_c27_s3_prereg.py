"""machine2 cycle27 LEG A -- PRE-REGISTRATION for SITE S3 = m1's corrected pick D4 (m1-L155a, b4f784d).

This file computes DESIGN quantities and nothing else.  It never evaluates lam_min of a composed
matrix built from the UNTRUNCATED quadruple at nonzero delta on BOTH legs -- that is the scored
object and it lives in m2_c27_s3_scored.py, whose sha256 is recorded in the prereg JSON and which
IS NOT RUN THIS CYCLE (m1's 12 h reveal gap).

TRAP #117 ADOPTION, AS AMENDED BY THIS CYCLE'S LEG B.
    #117 (m1) prescribes ONE external anchor: the launch lam_min.  Leg B measured that anchor's
    firing world and it is a PROPER SUBSET of the corruption space: m1's own defect 2 (cross-form
    conj(up) for conj(uq)) is EXACT at d = 0, so a d = 0 anchor cannot see it, and on my cycle-25
    site that invisible corruption flips the FIRES verdict at R3b.  Therefore this port carries a
    TWO-POINT anchor -- one undisplaced, one DISPLACED -- both external, both from the source path:
        ANCHOR-0  S2 composed launch  2.0004746865698620975e-5
                  (m1 heat75/heat81 "certified CYCLE-25 value to its last digit"; m3-L156)
        ANCHOR-D  S2 R0 exact at d_a = 0.1  1.9160562986370759475e-5
                  (m1-L160 sect1: ten committed rungs verified, worst rel 3.81e-20)
    and, at the NEW site, a third cross-machine anchor from m1-L155a's heat77b:
        ANCHOR-S3 D4 launch lam_min 1.2965524199220303e-5, f_a(0.1) -1.004419853e-6,
                  delta_c 0.22348896097863643215, PT_a 60.019, PT_b(delta_c) 17.803
    The machinery is IMPORTED, not transcribed (#117's own stronger remedy).
"""
import json, os, sys, time, hashlib
from mpmath import mp

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("RH_REPO", "/shared/rh-exchange-repo/Riemann")
mp.dps = 40
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

half = mp.mpf(1) / 2
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open(os.path.join(HERE, "zeros210.json")))]
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


def gnorm(P):
    Lc = mp.cholesky(G); Lic = mp.inverse(Lc)
    B = Lic * P * Lic.T; B = (B + B.T) / 2
    E, _ = mp.eigsy(B)
    return max(abs(E[i]) for i in range(N))


def anchor(name, got, want, tol):
    rel = abs(got - mp.mpf(want)) / abs(mp.mpf(want))
    ok = rel < mp.mpf(tol)
    print("ANCHOR %-9s got %s  want %s  rel %s  %s"
          % (name, mp.nstr(got, 20), want, mp.nstr(rel, 4), "PASS" if ok else "*** FAIL ***"))
    if not ok:
        raise SystemExit("ANCHOR %s FAILED -- aborting before any S3 quantity is computed" % name)
    return mp.nstr(rel, 6)


# ================= TWO-POINT EXTERNAL ANCHOR (from the S2 source path) =========================
S2 = json.load(open(os.path.join(HERE, "c25_prereg.json")))["site"]
s2_ga = mp.mpf(S2["g_a"]); s2_gb = mp.mpf(S2["g_b"])
s2A1, s2A2, s2B1, s2B2 = [mp.mpf(x) for x in S2["removed"]]
s2rem = (zero_pair_K(mp.mpc(half, s2A1)) + zero_pair_K(mp.mpc(half, s2A2))
         + zero_pair_K(mp.mpc(half, s2B1)) + zero_pair_K(mp.mpc(half, s2B2)))
s2base = K200 - s2rem
s2launch = s2base + quad(mp.mpf(0), s2_ga) + quad(mp.mpf(0), s2_gb)
av = {}
av["ANCHOR-0"] = anchor("ANCHOR-0", eig_full(s2launch, G)[0][0], "2.0004746865698620975e-5", "1e-19")
s2R0 = s2base + quad(mp.mpf("0.1"), s2_ga) + quad(mp.mpf(0), s2_gb)
av["ANCHOR-D"] = anchor("ANCHOR-D", eig_full(s2R0, G)[0][0], "1.9160562986370759475e-5", "1e-19")
print("two-point anchor PASSED at %.1fs -- displacement layer certified, not only the d=0 layer\n"
      % (time.time() - t0))

# ================= SITE S3 = D4 ================================================================
KA, KB = 1, 7
GA1, GA2 = up200[KA], up200[KA + 1]
GB1, GB2 = up200[KB], up200[KB + 1]
g_a = GA1 + (GA2 - GA1) * 4 / mp.mpf(8)
g_b = GB1 + (GB2 - GB1) * 3 / mp.mpf(8)
print("S3=D4  gap A k=%d (%s,%s)  g_a = %s" % (KA, mp.nstr(GA1, 10), mp.nstr(GA2, 10), mp.nstr(g_a, 25)))
print("       gap B k=%d (%s,%s)  g_b = %s" % (KB, mp.nstr(GB1, 10), mp.nstr(GB2, 10), mp.nstr(g_b, 25)))
assert abs(g_a - mp.mpf("23.016448609458621877921135")) < mp.mpf("1e-20"), "g_a != m1's D4 pick"
assert abs(g_b - mp.mpf("45.081352381009559597663504")) < mp.mpf("1e-20"), "g_b != m1's D4 pick"

remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))
base = K200 - remA - remB
qA0, qB0 = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b)
vals, vecs = eig_full(base + qA0 + qB0, G)
v0 = vecs[0]; nrm = bil(G, v0, v0); gapL = vals[1] - vals[0]
av["ANCHOR-S3-launch"] = anchor("S3launch", vals[0], "1.2965524199220303e-5", "1e-14")
print("       launch gap = %s   (m1 heat77b quoted 1.05047976563e-4)" % mp.nstr(gapL, 12))

DA = mp.mpf("0.1")
Pa = quad(DA, g_a) - qA0
fa = bil(Pa, v0, v0) / nrm
av["ANCHOR-S3-fa"] = anchor("S3 f_a", fa, "-1.004419853e-6", "1e-8")


def fb_of(d, g=None):
    g = g_b if g is None else g
    return bil(quad(d, g) - quad(mp.mpf(0), g), v0, v0) / nrm


lo, hi = mp.mpf("0.02"), mp.mpf("0.45")
glo = fb_of(lo) + fa; ghi = fb_of(hi) + fa
assert (glo > 0) != (ghi > 0), "no cancellation bracket at S3"
for it in range(120):
    mid = (lo + hi) / 2; gm = fb_of(mid) + fa
    if (gm > 0) == (glo > 0):
        lo, glo = mid, gm
    else:
        hi, ghi = mid, gm
    if hi - lo < mp.mpf("1e-30"):
        break
DC = (lo + hi) / 2
av["ANCHOR-S3-dc"] = anchor("S3 d_c", DC, "0.22348896097863643215", "1e-15")
Pb = quad(DC, g_b) - qB0
fb = bil(Pb, v0, v0) / nrm
print("f_b(delta_c) = %s   f_a+f_b = %s  (depth %s of |f_a|)"
      % (mp.nstr(fb, 18), mp.nstr(fa + fb, 8), mp.nstr(abs(fa + fb) / abs(fa), 6)))

D3 = mp.mpf("0.30"); D4v = mp.mpf("0.40")
Pb3 = quad(D3, g_b) - qB0; fb3 = bil(Pb3, v0, v0) / nrm
Pb4 = quad(D4v, g_b) - qB0; fb4 = bil(Pb4, v0, v0) / nrm
print("f_b(0.30) = %s   [ordinary opposing rung R3]" % mp.nstr(fb3, 12))
print("f_b(0.40) = %s   [exploratory rung R3b]" % mp.nstr(fb4, 12))

# same-sign control site on gap B: scan the 1/8 grid for sign(f_b') == sign(f_a)
print("\nsame-sign control scan on gap B (grid m/8, delta = 0.1):")
cand = []
for m_ in range(1, 8):
    if m_ == 3:
        continue
    gg = GB1 + (GB2 - GB1) * m_ / mp.mpf(8)
    val = fb_of(DA, gg)
    same = (val > 0) == (fa > 0)
    print("   m=%d  g=%s  f_b'(0.1)=%s  %s" % (m_, mp.nstr(gg, 14), mp.nstr(val, 10),
                                               "SAME SIGN as f_a" if same else "opposing"))
    if same:
        cand.append((m_, gg, val))
assert cand, "no same-sign control available on gap B"
m_s, g_bs, fbs_probe = max(cand, key=lambda c: abs(c[2]))
print("   -> control site m=%d  g_b' = %s" % (m_s, mp.nstr(g_bs, 25)))
qB0s = quad(mp.mpf(0), g_bs)
vals_s, vecs_s = eig_full(base + qA0 + qB0s, G)
v0s = vecs_s[0]; nrm_s = bil(G, v0s, v0s); gapLs = vals_s[1] - vals_s[0]
Pas = quad(DA, g_a) - qA0
Pbs = quad(DA, g_bs) - qB0s
fas = bil(Pas, v0s, v0s) / nrm_s
fbs = bil(Pbs, v0s, v0s) / nrm_s
print("launch' lam_min = %s  gap = %s   f_a = %s  f_b' = %s"
      % (mp.nstr(vals_s[0], 20), mp.nstr(gapLs, 10), mp.nstr(fas, 12), mp.nstr(fbs, 12)))


def second_order(Pa_, Pb_, vals_, vecs_, nrm_):
    sa = sb = X = mp.mpf(0)
    for k in range(1, N):
        nk = bil(G, vecs_[k], vecs_[k])
        A = bil(Pa_, vecs_[0], vecs_[k]) / mp.sqrt(nrm_ * nk)
        B_ = bil(Pb_, vecs_[0], vecs_[k]) / mp.sqrt(nrm_ * nk)
        den = vals_[0] - vals_[k]
        sa += A * A / den; sb += B_ * B_ / den; X += 2 * A * B_ / den
    return sa, sb, X


so = {}
for rung, (PA_, PB_, vv, ve, nn) in {"R2": (Pa, Pb, vals, vecs, nrm),
                                     "R3": (Pa, Pb3, vals, vecs, nrm),
                                     "R3b": (Pa, Pb4, vals, vecs, nrm),
                                     "R4": (Pas, Pbs, vals_s, vecs_s, nrm_s)}.items():
    sa, sb, X = second_order(PA_, PB_, vv, ve, nn)
    so[rung] = [mp.nstr(sa, 12), mp.nstr(sb, 12), mp.nstr(X, 12)]
    print("2nd order %-3s self_a %s  self_b %s  CROSS %s" % (rung, mp.nstr(sa, 10), mp.nstr(sb, 10), mp.nstr(X, 12)))

PT = {"P_a": mp.nstr(gnorm(Pa) / gapL, 8), "P_b(d_c)": mp.nstr(gnorm(Pb) / gapL, 8),
      "P_b(0.30)": mp.nstr(gnorm(Pb3) / gapL, 8), "P_b(0.40)": mp.nstr(gnorm(Pb4) / gapL, 8),
      "P_bs": mp.nstr(gnorm(Pbs) / gapLs, 8), "gap": mp.nstr(gapL, 12), "gap_s": mp.nstr(gapLs, 12)}
av["ANCHOR-S3-PTa"] = anchor("S3 PT_a", mp.mpf(PT["P_a"]), "60.019", "1e-4")
av["ANCHOR-S3-PTb"] = anchor("S3 PT_b", mp.mpf(PT["P_b(d_c)"]), "17.803", "1e-4")
print("\nPT (G-norm / launch gap): %s" % json.dumps(PT))


# ================= Taylor predictor: truncate the QUADRUPLE in delta, re-solve ==================
def Smat(up, uq):
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


DERS = {}
for gname, g0 in (("a", g_a), ("b", g_b), ("bs", g_bs)):
    s0 = mp.mpc(half, g0)
    DERS[gname] = [[sum(w * (x ** k) * mp.exp(s0 * x) for x, w in zip(b.xs, b.ws)) for k in range(9)]
                   for b in bases]


def utay(gname, d, K):
    return [sum(DERS[gname][i][k] * (d ** k) / mp.factorial(k) for k in range(K + 1)) for i in range(N)]


def ty(rung, K):
    (da, db, site) = rung
    q0b = qB0 if site == "b" else qB0s
    A = Smat(utay("a", da, K), utay("a", -da, K)) if da != 0 else qA0
    B_ = Smat(utay(site, db, K), utay(site, -db, K)) if db != 0 else q0b
    return lam(base + A + B_, G)[0]


RUNGS = {"R0": (DA, mp.mpf(0), "b"), "R1": (mp.mpf(0), DC, "b"), "R2": (DA, DC, "b"),
         "R1b": (mp.mpf(0), D3, "b"), "R3": (DA, D3, "b"),
         "R1e": (mp.mpf(0), D4v, "b"), "R3b": (DA, D4v, "b"),
         "R0s": (DA, mp.mpf(0), "bs"), "R1d": (mp.mpf(0), DA, "bs"), "R4": (DA, DA, "bs")}
lam_launch = {"b": vals[0], "bs": vals_s[0]}
taylor = {}
print("\n%-5s %8s %8s %18s %18s %18s %14s" % ("rung", "d_a", "d_b", "ty2", "ty4", "ty6", "band(+-)"))
for r, (da, db, site) in RUNGS.items():
    t2 = ty((da, db, site), 2); t4 = ty((da, db, site), 4); t6 = ty((da, db, site), 6)
    taylor[r] = {"d_a": mp.nstr(da, 25), "d_b": mp.nstr(db, 25), "site": site,
                 "ty2": mp.nstr(t2, 20), "ty4": mp.nstr(t4, 20), "ty6": mp.nstr(t6, 20),
                 "band_halfwidth": mp.nstr(2 * abs(t6 - t4), 10),
                 "shift_ty4": mp.nstr(t4 - lam_launch[site], 18), "fires_ty4": bool(t4 < 0)}
    print("%-5s %8s %8s %18s %18s %18s %14s"
          % (r, mp.nstr(da, 4), mp.nstr(db, 6), mp.nstr(t2, 12), mp.nstr(t4, 12), mp.nstr(t6, 12),
             mp.nstr(2 * abs(t6 - t4), 4)), flush=True)

D_pred = {}
print()
for rung, aarm, barm in (("R2", "R0", "R1"), ("R3", "R0", "R1b"), ("R3b", "R0", "R1e"), ("R4", "R0s", "R1d")):
    site = RUNGS[rung][2]
    sA = mp.mpf(taylor[aarm]["ty4"]) - lam_launch[RUNGS[aarm][2]]
    sB = mp.mpf(taylor[barm]["ty4"]) - lam_launch[RUNGS[barm][2]]
    sh = mp.mpf(taylor[rung]["ty4"]) - lam_launch[site]
    Dv = sh - sA - sB
    fa_ = fa if site == "b" else fas
    fb_ = {"R2": fb, "R3": fb3, "R3b": fb4, "R4": fbs}[rung]
    Xr = mp.mpf(so[rung][2])
    D_pred[rung] = {"s_A": mp.nstr(sA, 12), "s_B": mp.nstr(sB, 12), "shift": mp.nstr(sh, 12),
                    "D": mp.nstr(Dv, 12), "R_c": mp.nstr(abs(Dv) / (abs(fa_) + abs(fb_)), 10),
                    "defect_frac_pct": mp.nstr(100 * abs(Dv / sh), 8),
                    "cross_2nd": so[rung][2], "D_over_cross_ty4": mp.nstr(Dv / Xr, 8)}
    print("PRED %-3s s_A %s  s_B %s  shift %s  D %s  R_c %s  |D|/|sh| %s%%  D/X %s"
          % (rung, mp.nstr(sA, 8), mp.nstr(sB, 8), mp.nstr(sh, 8), mp.nstr(Dv, 8),
             D_pred[rung]["R_c"], D_pred[rung]["defect_frac_pct"], D_pred[rung]["D_over_cross_ty4"]))

PT_by_rung = {"R2": PT["P_b(d_c)"], "R3": PT["P_b(0.30)"], "R3b": PT["P_b(0.40)"], "R4": PT["P_bs"]}

# ---- the pre-registered PT band: cycle-25's D/X_2nd vs PT points, power law on the 3 in range ----
S2pts = [(mp.mpf("19.389386"), mp.mpf("1.120")), (mp.mpf("56.078834"), mp.mpf("2.140")),
         (mp.mpf("84.778974"), mp.mpf("2.927"))]
slope = mp.log(S2pts[2][1] / S2pts[0][1]) / mp.log(S2pts[2][0] / S2pts[0][0])
def pt_pred(x):
    return S2pts[0][1] * (mp.mpf(x) / S2pts[0][0]) ** slope
H1band = {r: {"PT": PT_by_rung[r], "point": mp.nstr(pt_pred(PT_by_rung[r]), 8),
              "band": [mp.nstr(pt_pred(PT_by_rung[r]) / 2, 8), mp.nstr(pt_pred(PT_by_rung[r]) * 2, 8)],
              "in_fitted_PT_range": bool(mp.mpf("19.389386") <= mp.mpf(PT_by_rung[r]) <= mp.mpf("84.778974"))}
         for r in PT_by_rung}
print("\nH1 pre-registered PT band (slope %s from cycle-25's three in-range points):" % mp.nstr(slope, 8))
for r in ("R2", "R3", "R3b", "R4"):
    print("   %-4s PT %-11s point %-10s band [%s, %s]  %s"
          % (r, H1band[r]["PT"], H1band[r]["point"], H1band[r]["band"][0], H1band[r]["band"][1],
             "interpolation" if H1band[r]["in_fitted_PT_range"] else "EXTRAPOLATION"))

sc = os.path.join(HERE, "m2_c27_s3_scored.py")
sha = hashlib.sha256(open(sc, "rb").read()).hexdigest()
out = {"cycle": 27, "machine": "machine2", "site": "S3 = m1's corrected pick D4 (m1-L155a, b4f784d)",
       "anchors_passed": av,
       "geometry": {"gap_A_k": KA, "gap_B_k": KB,
                    "removed": [mp.nstr(x, 25) for x in (GA1, GA2, GB1, GB2)],
                    "g_a": mp.nstr(g_a, 25), "g_b": mp.nstr(g_b, 25),
                    "g_bs": mp.nstr(g_bs, 25), "grid_bs": m_s,
                    "delta_a": "0.1", "delta_c": mp.nstr(DC, 25),
                    "delta_b_R3": "0.30", "delta_b_R3b": "0.40"},
       "launch": {"lam": mp.nstr(vals[0], 20), "gap": mp.nstr(gapL, 14),
                  "lam_s": mp.nstr(vals_s[0], 20), "gap_s": mp.nstr(gapLs, 14)},
       "functionals": {"f_a": mp.nstr(fa, 18), "f_b": mp.nstr(fb, 18),
                       "f_b3": mp.nstr(fb3, 18), "f_b4": mp.nstr(fb4, 18),
                       "f_as": mp.nstr(fas, 18), "f_bs": mp.nstr(fbs, 18),
                       "f_sum": mp.nstr(fa + fb, 8)},
       "second_order": so, "PT": PT, "PT_by_rung": PT_by_rung,
       "taylor": taylor, "prediction_D_from_ty4": D_pred, "H1_PT_band": H1band,
       "scored_runner": "m2_c27_s3_scored.py", "scored_runner_sha256": sha,
       "scored_runner_NOT_RUN_THIS_CYCLE": True,
       "reveal_gap_hours": 12,
       "seconds": round(time.time() - t0, 1)}
json.dump(out, open(os.path.join(HERE, "c27_s3_prereg.json"), "w"), indent=1)
print("\nPREREG written, %.1fs; SEALED scored runner sha256 = %s" % (time.time() - t0, sha))
