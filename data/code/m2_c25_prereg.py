"""machine2 cycle25 -- PRE-REGISTRATION for a SECOND cancellation site (site S2).

SITE S2  (selected by the composed-launch first-order functional, NEVER by a single-pair lam_min sign)
    gap A = k=2  (25.0108575801/30.4248761259)   gamma_a = grid 7 of 8   delta_a = 0.1
    gap B = k=4  (32.9350615877/37.5861781588)   gamma_b = grid 4 of 8   delta_b = solved to cancel
Disjoint from cycle 23's site in BOTH insertion ordinates and in gap B's removal pair.

THE LADDER (8 configurations, 6 of them composed or single-leg arms of a composed rung):
    launch  (0, 0)
    R0      (d_a, 0)             leg A alone                              -> s_A
    R1      (0, d_c)             leg B alone at the cancelling delta      -> s_B(d_c)
    R2      (d_a, d_c)           THE EXACT-CANCELLATION RUNG              -> shift, D, R_c
    R1b     (0, 0.30)            leg B alone, non-cancelling              -> s_B(0.30)
    R3      (d_a, 0.30)          ORDINARY OPPOSING rung (control 1)       -> shift, D, R_c
    R1d     (0, 0.1) at gamma_b' leg B' alone, SAME-SIGN site (grid 3)    -> s_B'
    R4      (d_a, 0.1) at gamma_b'  SAME-SIGN rung (control 2)            -> shift, D, R_c

GRADED QUANTITY = the ADDITIVITY DEFECT  D = shift - s_A - s_B  and  R_c = |D|/(|f_a|+|f_b|),
per m1-L150 sect3 (his L149 relative band is degenerate at a cancellation rung -- he owned that and
re-banded before cycle 23 was scored).  Bands here follow HIS rule: |ty6 - ty4| x 2 safety, computed
from a next-order measurement of my own instrument and from NO exact value.

This script computes DESIGN quantities and PREDICTIONS only.  It never evaluates lam_min of a
composed matrix built from the UNTRUNCATED quadruple at nonzero delta -- that is the scored object and
it lives in m2_c25_scored.py, whose sha256 is committed with this output.
"""
import json, os, hashlib, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
HERE = os.path.dirname(os.path.abspath(__file__))
half = mp.mpf(1) / 2
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open(os.path.join(HERE, "zeros210.json")))]
up200 = [g for g in gam if g <= 200]
t0 = time.time()
bases = [Basis(g, degree=8) for g in gens]
G = gram(); K200 = mat(tgt["K_T200"]); Graw = mat(tgt["G_raw"])
d0 = max(abs(b.u_real(mp.mpf(0)) - mp.mpf(tgt["U0"][i])) for i, b in enumerate(bases))
dG = max(abs(G[i, j] - Graw[i, j]) for i in range(N) for j in range(N))
Kus = mp.matrix(N, N)
for g in up200:
    Kus += zero_pair_K(mp.mpc(half, g))
dK = max(abs(Kus[i, j] - K200[i, j]) for i in range(N) for j in range(N))
print("CERT u0 %s  G %s  K200 %s  lam_min(K200,G) %s"
      % (mp.nstr(d0, 4), mp.nstr(dG, 4), mp.nstr(dK, 4), mp.nstr(lam(K200, G)[0], 14)))


def quad(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    return Smat(up, uq)


def Smat(up, uq):
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


# ---- the site -------------------------------------------------------------------------------
KA, KB = 2, 4
GA1, GA2 = up200[KA], up200[KA + 1]
GB1, GB2 = up200[KB], up200[KB + 1]
g_a = GA1 + (GA2 - GA1) * 7 / mp.mpf(8)
g_b = GB1 + (GB2 - GB1) * 4 / mp.mpf(8)
g_bs = GB1 + (GB2 - GB1) * 3 / mp.mpf(8)      # same-sign control site (leg B', grid 3)
remA = zero_pair_K(mp.mpc(half, GA1)) + zero_pair_K(mp.mpc(half, GA2))
remB = zero_pair_K(mp.mpc(half, GB1)) + zero_pair_K(mp.mpc(half, GB2))
qA0, qB0, qB0s = quad(mp.mpf(0), g_a), quad(mp.mpf(0), g_b), quad(mp.mpf(0), g_bs)
L = K200 - remA - remB + qA0 + qB0
vals, vecs = eig_full(L, G); v0 = vecs[0]; nrm = bil(G, v0, v0)
Ls = K200 - remA - remB + qA0 + qB0s
vals_s, vecs_s = eig_full(Ls, G); v0s = vecs_s[0]; nrm_s = bil(G, v0s, v0s)
print("\ngamma_a  = %s" % mp.nstr(g_a, 25))
print("gamma_b  = %s   (cancellation site)" % mp.nstr(g_b, 25))
print("gamma_b' = %s   (same-sign control site)" % mp.nstr(g_bs, 25))
print("launch  lam_min = %s   gap lam1-lam0 = %s" % (mp.nstr(vals[0], 20), mp.nstr(vals[1] - vals[0], 12)))
print("launch' lam_min = %s   gap = %s" % (mp.nstr(vals_s[0], 20), mp.nstr(vals_s[1] - vals_s[0], 12)))
print("launch  spectrum %s" % [mp.nstr(x, 8) for x in vals])

DA = mp.mpf("0.1")
Pa = quad(DA, g_a) - qA0
fa = bil(Pa, v0, v0) / nrm
print("\nf_a(delta_a=0.1) = %s" % mp.nstr(fa, 18))


def fb_of(d):
    return bil(quad(d, g_b) - qB0, v0, v0) / nrm


lo, hi = mp.mpf("0.02"), mp.mpf("0.40")
glo = fb_of(lo) + fa; ghi = fb_of(hi) + fa
print("cancellation bracket: g(%s)=%s  g(%s)=%s" % (lo, mp.nstr(glo, 6), hi, mp.nstr(ghi, 6)))
assert (glo > 0) != (ghi > 0), "no bracket"
for it in range(120):
    mid = (lo + hi) / 2; gm = fb_of(mid) + fa
    if (gm > 0) == (glo > 0):
        lo, glo = mid, gm
    else:
        hi, ghi = mid, gm
    if hi - lo < mp.mpf("1e-30"):
        break
DC = (lo + hi) / 2
Pb = quad(DC, g_b) - qB0
fb = bil(Pb, v0, v0) / nrm
print("delta_c (cancelling) = %s   [%d bisections]" % (mp.nstr(DC, 25), it))
print("f_b(delta_c) = %s ;  f_a+f_b = %s  (depth %s of |f_a|)"
      % (mp.nstr(fb, 18), mp.nstr(fa + fb, 8), mp.nstr(abs(fa + fb) / abs(fa), 6)))

D3 = mp.mpf("0.20")
D4 = mp.mpf("0.30")
Pb3 = quad(D3, g_b) - qB0
fb3 = bil(Pb3, v0, v0) / nrm
Pbs = quad(DA, g_bs) - qB0s
Pas = quad(DA, g_a) - qA0
fas = bil(Pas, v0s, v0s) / nrm_s
fbs = bil(Pbs, v0s, v0s) / nrm_s
Pb4 = quad(D4, g_b) - qB0
fb4 = bil(Pb4, v0, v0) / nrm
print("f_b(0.20) = %s   [ordinary opposing rung R3]" % mp.nstr(fb3, 12))
print("f_b(0.30) = %s   [exploratory rung R3b, predictor unconverged]" % mp.nstr(fb4, 12))
print("same-sign launch': f_a = %s  f_b' = %s" % (mp.nstr(fas, 12), mp.nstr(fbs, 12)))


def second_order(Pa_, Pb_, vals_, vecs_, nrm_):
    sa = sb = X = mp.mpf(0)
    for k in range(1, N):
        nk = bil(G, vecs_[k], vecs_[k])
        A = bil(Pa_, vecs_[0], vecs_[k]) / mp.sqrt(nrm_ * nk)
        B_ = bil(Pb_, vecs_[0], vecs_[k]) / mp.sqrt(nrm_ * nk)
        den = vals_[0] - vals_[k]
        sa += A * A / den; sb += B_ * B_ / den; X += 2 * A * B_ / den
    return sa, sb, X


sa2, sb2, X2 = second_order(Pa, Pb, vals, vecs, nrm)
sa3, sb3, X3 = second_order(Pa, Pb3, vals, vecs, nrm)
sa3b, sb3b, X3b = second_order(Pa, Pb4, vals, vecs, nrm)
sa4, sb4, X4 = second_order(Pas, Pbs, vals_s, vecs_s, nrm_s)
print("\n2nd order at R2: self_a %s  self_b %s  CROSS %s   |self sum|/|X| = %s"
      % (mp.nstr(sa2, 10), mp.nstr(sb2, 10), mp.nstr(X2, 12), mp.nstr(abs((sa2 + sb2) / X2), 6)))
print("2nd order at R3: self_a %s  self_b %s  CROSS %s" % (mp.nstr(sa3, 10), mp.nstr(sb3, 10), mp.nstr(X3, 12)))
print("2nd order at R4: self_a %s  self_b %s  CROSS %s" % (mp.nstr(sa4, 10), mp.nstr(sb4, 10), mp.nstr(X4, 12)))

# ---- Taylor predictor: truncate the QUADRUPLE in powers of delta, re-solve the eigensystem ----
DERS = {}
for gname, g0 in (("a", g_a), ("b", g_b), ("bs", g_bs)):
    s0 = mp.mpc(half, g0)
    DERS[gname] = [[sum(w * (x ** k) * mp.exp(s0 * x) for x, w in zip(b.xs, b.ws)) for k in range(9)]
                   for b in bases]


def utay(gname, d, K):
    return [sum(DERS[gname][i][k] * (d ** k) / mp.factorial(k) for k in range(K + 1)) for i in range(N)]


def quadT(gname, d, K):
    return Smat(utay(gname, d, K), utay(gname, -d, K))


def ty(rung, K):
    (da, db, site) = rung
    q0b = qB0 if site == "b" else qB0s
    A = quadT("a", da, K) if da != 0 else qA0
    B_ = quadT(site, db, K) if db != 0 else q0b
    return lam(K200 - remA - remB + A + B_, G)[0]


RUNGS = {"R0": (DA, mp.mpf(0), "b"), "R1": (mp.mpf(0), DC, "b"), "R2": (DA, DC, "b"),
         "R1b": (mp.mpf(0), D3, "b"), "R3": (DA, D3, "b"),
         "R1e": (mp.mpf(0), D4, "b"), "R3b": (DA, D4, "b"),
         "R0s": (DA, mp.mpf(0), "bs"), "R1d": (mp.mpf(0), DA, "bs"), "R4": (DA, DA, "bs")}
lam_launch = {"b": vals[0], "bs": vals_s[0]}
pred = {}
print("\n%-5s %8s %10s %18s %18s %18s %14s" % ("rung", "d_a", "d_b", "ty2", "ty4", "ty6", "band(+-)"))
for r, (da, db, site) in RUNGS.items():
    t2 = ty((da, db, site), 2); t4 = ty((da, db, site), 4); t6 = ty((da, db, site), 6)
    band = 2 * abs(t6 - t4)
    pred[r] = {"d_a": mp.nstr(da, 25), "d_b": mp.nstr(db, 25), "site": site,
               "ty2": mp.nstr(t2, 18), "ty4": mp.nstr(t4, 18), "ty6": mp.nstr(t6, 18),
               "band_halfwidth": mp.nstr(band, 8),
               "shift_ty4": mp.nstr(t4 - lam_launch[site], 18),
               "fires_ty4": bool(t4 < 0)}
    print("%-5s %8s %10s %18s %18s %18s %14s"
          % (r, mp.nstr(da, 4), mp.nstr(db, 6), mp.nstr(t2, 12), mp.nstr(t4, 12), mp.nstr(t6, 12),
             mp.nstr(band, 4)), flush=True)

# predicted additivity defects from the ty4 column (a PREDICTION: the exact eigensolve is not run here)
D_pred = {}
for rung, aarm, barm in (("R2", "R0", "R1"), ("R3", "R0", "R1b"), ("R3b", "R0", "R1e"),
                         ("R4", "R0s", "R1d")):
    site = RUNGS[rung][2]
    l0 = lam_launch[site]
    sA = mp.mpf(pred[aarm]["ty4"]) - lam_launch[RUNGS[aarm][2]]
    sB = mp.mpf(pred[barm]["ty4"]) - lam_launch[RUNGS[barm][2]]
    sh = mp.mpf(pred[rung]["ty4"]) - l0
    Dv = sh - sA - sB
    fa_ = fa if site == "b" else fas
    fb_ = {"R2": fb, "R3": fb3, "R3b": fb4, "R4": fbs}[rung]
    D_pred[rung] = {"s_A": mp.nstr(sA, 12), "s_B": mp.nstr(sB, 12), "shift": mp.nstr(sh, 12),
                    "D": mp.nstr(Dv, 12), "R_c": mp.nstr(abs(Dv) / (abs(fa_) + abs(fb_)), 10),
                    "defect_frac_pct": mp.nstr(100 * abs(Dv / sh), 8),
                    "cross_2nd": mp.nstr({"R2": X2, "R3": X3, "R3b": X3b, "R4": X4}[rung], 10)}
    print("PRED %-3s  s_A %s  s_B %s  shift %s  D %s  R_c %s  |D|/|shift| %s%%"
          % (rung, mp.nstr(sA, 8), mp.nstr(sB, 8), mp.nstr(sh, 8), mp.nstr(Dv, 8),
             D_pred[rung]["R_c"], D_pred[rung]["defect_frac_pct"]))

def gnorm(P):
    Lc = mp.cholesky(G); Lic = mp.inverse(Lc)
    B = Lic * P * Lic.T; B = (B + B.T) / 2
    E, _ = mp.eigsy(B)
    return max(abs(E[i]) for i in range(N))


gapL = vals[1] - vals[0]; gapLs = vals_s[1] - vals_s[0]
PTP = {"P_a": mp.nstr(gnorm(Pa), 12), "P_b(d_c)": mp.nstr(gnorm(Pb), 12),
       "P_b(0.20)": mp.nstr(gnorm(Pb3), 12), "P_b(0.30)": mp.nstr(gnorm(Pb4), 12),
       "P_as": mp.nstr(gnorm(Pas), 12), "P_bs": mp.nstr(gnorm(Pbs), 12),
       "gap": mp.nstr(gapL, 12), "gap_s": mp.nstr(gapLs, 12),
       "ratio_Pa_gap": mp.nstr(gnorm(Pa) / gapL, 8),
       "ratio_Pb_dc_gap": mp.nstr(gnorm(Pb) / gapL, 8),
       "ratio_Pb020_gap": mp.nstr(gnorm(Pb3) / gapL, 8),
       "ratio_Pb030_gap": mp.nstr(gnorm(Pb4) / gapL, 8),
       "ratio_Pbs_gap_s": mp.nstr(gnorm(Pbs) / gapLs, 8)}
print("\nPT parameters (G-metric operator norm / launch gap):")
for k in ("ratio_Pa_gap", "ratio_Pb_dc_gap", "ratio_Pb020_gap", "ratio_Pb030_gap", "ratio_Pbs_gap_s"):
    print("   %-18s %s" % (k, PTP[k]))

sc = os.path.join(HERE, "m2_c25_scored.py")
sha = hashlib.sha256(open(sc, "rb").read()).hexdigest() if os.path.exists(sc) else "NOT-YET-WRITTEN"
out = {"site": {"kA": KA, "kB": KB, "g_a": mp.nstr(g_a, 25), "g_b": mp.nstr(g_b, 25),
                "g_bs": mp.nstr(g_bs, 25),
                "removed": [mp.nstr(x, 25) for x in (GA1, GA2, GB1, GB2)],
                "delta_a": mp.nstr(DA, 10), "delta_c": mp.nstr(DC, 25), "delta_3": mp.nstr(D3, 10)},
       "cert": {"u0": mp.nstr(d0, 6), "G": mp.nstr(dG, 6), "K200": mp.nstr(dK, 6)},
       "launch": {"lam": mp.nstr(vals[0], 20), "spectrum": [mp.nstr(x, 14) for x in vals],
                  "lam_s": mp.nstr(vals_s[0], 20), "spectrum_s": [mp.nstr(x, 14) for x in vals_s]},
       "functionals": {"f_a": mp.nstr(fa, 18), "f_b": mp.nstr(fb, 18), "f_sum": mp.nstr(fa + fb, 8),
                       "f_b3": mp.nstr(fb3, 18), "f_b4": mp.nstr(fb4, 18), "f_as": mp.nstr(fas, 18), "f_bs": mp.nstr(fbs, 18)},
       "second_order": {"R2": [mp.nstr(sa2, 12), mp.nstr(sb2, 12), mp.nstr(X2, 12)],
                        "R3": [mp.nstr(sa3, 12), mp.nstr(sb3, 12), mp.nstr(X3, 12)],
                        "R3b": [mp.nstr(sa3b, 12), mp.nstr(sb3b, 12), mp.nstr(X3b, 12)],
                        "R4": [mp.nstr(sa4, 12), mp.nstr(sb4, 12), mp.nstr(X4, 12)]},
       "PT": PTP, "prediction": pred, "prediction_D": D_pred, "scored_runner_sha256": sha}
json.dump(out, open(os.path.join(HERE, "c25_prereg.json"), "w"), indent=1)
print("\nscored runner sha256: %s" % sha)
print("done %.1fs" % (time.time() - t0))
