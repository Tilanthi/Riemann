"""machine2 CYCLE 29 PART B -- POST-HOC retro-certification of the branches NO ANCHOR COVERED.

Written and run AFTER the sealed runner, at reveal.  It is NOT an anchor and is NOT presented as
one: an anchor is asserted before the scored value exists, and every value here already existed.
It is the retro-certification path m1 used for his own UNCOVERED M64 branch (L165 sect8).

WHAT IT COVERS.  Coverage statement (amendment v2.1: name every BRANCH the runner takes):
  branch 1  da == 0   vs  da != 0            -- ANCHOR-0 / ANCHOR-S3launch cover ==0, ANCHOR-D covers !=0
  branch 2  db == 0   vs  db != 0            -- all three anchors sit at db == 0  =>  db != 0 UNCOVERED
  branch 3  site == "b" vs site == "bs"      -- all three anchors are on "b"      =>  "bs"    UNCOVERED
  branch 4  e4 == 0 / ty6 == ty4 NaN guards  -- not taken (measured: no zero denominators)
This script recomputes lam_min at all ten rungs through two independent paths and so exercises
branches 2 and 3 at every rung that takes them.

TWO INDEPENDENT PATHS, and exactly what each does NOT share with the sealed runner:
  PATH A (quad construction).  The runner builds
        M[i,j] = 2*Re( up[i]*conj(uq[j]) + up[j]*conj(uq[i]) )
  using complex conj().  Path A splits into real and imaginary parts first and uses REAL arithmetic
  only:  Re(up_i conj(uq_j)) = a_i c_j + b_i d_j.  This is the code path m1's defect-2 class
  (cross-form conj(up) written for conj(uq)) lives in, and cycle 27 measured that a d=0 anchor is
  bit-blind to it.  Shared with the runner: the basis evaluations b.u(p) themselves.
  PATH B (eigenvalue extraction).  The runner uses mp.cholesky + mp.eigsy on the congruence
  transform.  Path B forms A = G^{-1} F explicitly and gets the characteristic polynomial by
  Leverrier-Faddeev, then mp.polyroots.  Shares neither cholesky nor eigsy.

Both paths are run in all four combinations, so a disagreement localises.
"""
import json, os, sys, time
from mpmath import mp

os.environ.setdefault("RH_REPO", "/shared/rh-exchange-repo/Riemann")
sys.path.insert(0, "/workspace/rh/cycle27")
mp.dps = 40
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, mat, zero_pair_K, N

half = mp.mpf(1) / 2
PRE = json.load(open("/shared/rh-exchange-repo/Riemann/data/machine2_cycle27_s3_prereg.json"))
SC = json.load(open("/workspace/rh/cycle27/c27_s3_scored.json"))
S = PRE["geometry"]
gens = load_genomes("s1/M8")
tgt = load_target("s1/M8")
bases = [Basis(g, degree=8) for g in gens]
G = gram()
K200 = mat(tgt["K_T200"])
t0 = time.time()


def quad_runner(delta, g0):
    """byte-for-byte the sealed runner's construction (reference path)."""
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


def quad_pathA(delta, g0):
    """PATH A: real/imag split, real arithmetic only, no conj() anywhere."""
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    a = [mp.re(b.u(p)) for b in bases]; bb = [mp.im(b.u(p)) for b in bases]
    c = [mp.re(b.u(q)) for b in bases]; d = [mp.im(b.u(q)) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * ((a[i] * c[j] + bb[i] * d[j]) + (a[j] * c[i] + bb[j] * d[i]))
    return M


def lam_runner(F, Gm):
    """reference path: cholesky congruence + eigsy."""
    L = mp.cholesky(Gm); Li = mp.inverse(L)
    B = Li * F * Li.T; B = (B + B.T) / 2
    E, _ = mp.eigsy(B)
    return min(E)


def lam_pathB(F, Gm):
    """PATH B: A = G^-1 F, Leverrier-Faddeev char poly, polyroots.  No cholesky, no eigsy."""
    A = mp.inverse(Gm) * F
    Mk = mp.eye(N)
    coeffs = [mp.mpf(1)]
    for k in range(1, N + 1):
        Mk = A * Mk
        ck = -mp.mpf(sum(Mk[i, i] for i in range(N))) / k
        coeffs.append(ck)
        Mk = Mk + ck * mp.eye(N)
    roots = mp.polyroots(coeffs, maxsteps=200, extraprec=200)
    return min(mp.re(r) for r in roots)


g_a = mp.mpf(S["g_a"]); g_b = mp.mpf(S["g_b"]); g_bs = mp.mpf(S["g_bs"])
GA1, GA2, GB1, GB2 = [mp.mpf(x) for x in S["removed"]]
DA = mp.mpf(S["delta_a"]); DC = mp.mpf(S["delta_c"])
D3 = mp.mpf(S["delta_b_R3"]); D4v = mp.mpf(S["delta_b_R3b"])
base = K200 - zero_pair_K(mp.mpc(half, GA1)) - zero_pair_K(mp.mpc(half, GA2)) \
             - zero_pair_K(mp.mpc(half, GB1)) - zero_pair_K(mp.mpc(half, GB2))
RUNGS = {"R0": (DA, mp.mpf(0), "b"), "R1": (mp.mpf(0), DC, "b"), "R2": (DA, DC, "b"),
         "R1b": (mp.mpf(0), D3, "b"), "R3": (DA, D3, "b"),
         "R1e": (mp.mpf(0), D4v, "b"), "R3b": (DA, D4v, "b"),
         "R0s": (DA, mp.mpf(0), "bs"), "R1d": (mp.mpf(0), DA, "bs"), "R4": (DA, DA, "bs")}

print("%-5s %-9s %-9s %26s %12s %12s %12s" % ("rung", "branch2", "branch3", "sealed lam_min",
                                              "relA", "relB", "relAB"))
worst = {"A": mp.mpf(0), "B": mp.mpf(0), "AB": mp.mpf(0)}
rows = {}
for r, (da, db, site) in RUNGS.items():
    gB = g_b if site == "b" else g_bs
    sealed = mp.mpf(SC["rungs"][r]["lam"])
    F_ref = base + quad_runner(da, g_a) + quad_runner(db, gB)
    F_A = base + quad_pathA(da, g_a) + quad_pathA(db, gB)
    lA = lam_runner(F_A, G)          # path A construction, reference extraction
    lB = lam_pathB(F_ref, G)         # reference construction, path B extraction
    lAB = lam_pathB(F_A, G)          # both independent
    rel = lambda x: abs(x - sealed) / abs(sealed)
    rows[r] = {"sealed": mp.nstr(sealed, 20), "relA": mp.nstr(rel(lA), 6),
               "relB": mp.nstr(rel(lB), 6), "relAB": mp.nstr(rel(lAB), 6),
               "branch2_db_nonzero": bool(db != 0), "branch3_site_bs": site == "bs"}
    for k, v in (("A", rel(lA)), ("B", rel(lB)), ("AB", rel(lAB))):
        if v > worst[k]:
            worst[k] = v
    print("%-5s %-9s %-9s %26s %12s %12s %12s" % (
        r, "db!=0" if db != 0 else "db==0", site, mp.nstr(sealed, 18),
        mp.nstr(rel(lA), 4), mp.nstr(rel(lB), 4), mp.nstr(rel(lAB), 4)))

print("\nworst relative disagreement:  pathA %s   pathB %s   both %s"
      % (mp.nstr(worst["A"], 6), mp.nstr(worst["B"], 6), mp.nstr(worst["AB"], 6)))
nb2 = sum(1 for r in RUNGS if RUNGS[r][1] != 0)
nb3 = sum(1 for r in RUNGS if RUNGS[r][2] == "bs")
print("branch 2 (db != 0, UNCOVERED by every anchor) exercised at %d of 10 rungs" % nb2)
print("branch 3 (site == 'bs', UNCOVERED by every anchor) exercised at %d of 10 rungs" % nb3)
print("NOT covered even here: the derivation layer (D = shift - s_A - s_B and its reference rungs)"
      " -- cycle 28's {dref, sord} escapes are algebraically invisible to any lam_min check.")
json.dump({"rows": rows, "worst": {k: mp.nstr(v, 8) for k, v in worst.items()},
           "branch2_rungs": nb2, "branch3_rungs": nb3, "seconds": round(time.time() - t0, 1)},
          open("/workspace/rh/cycle29/c29_s3_branch_recheck.json", "w"), indent=1)
print("\ndone in %.1fs" % (time.time() - t0))
