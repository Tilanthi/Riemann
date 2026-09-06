"""machine2 CYCLE 30 -- SCORED RUNNER for the denser small-epsilon birth-locus ladder.

Frozen prereg: m2_c30_prereg.json (sha256 recorded in c30_seals.txt BEFORE this file existed).

Instrument: m2's own cycle-21 xi_D self-dual Epstein instrument (m2_zeta2_xi.Zeta2), a 1-D REAL
root find on the critical line -- structurally different lineage from m1's 2-D Newton.

CONFIG DISCLOSURES (not thresholds; stated because they differ from the cycle-21 call):
  * dps 60 (cycle 21 ran dps 45).
  * findroot tolerance 1e-52.  Cycle 21 passed 10^(-2*dps+6) = 1e-84 at dps 45, which mpmath
    cannot attain; at dps 60 that would be 1e-114.  The attainable target is used instead.
  * Delta* = 0.141733239663887191395415685084185024 -- the THREE-MACHINE confirmed operative
    root (m1 letter110 adjudication; m2 eps-free source root; m3 eps=1e-15 raw + kappa*eps^2).
    Identical literal to the cycle-21 run, so the Delta*-error is common-mode against m1's
    heat72x column and cancels in G1/G2.

Emits m2_c30_scored.json with EXACTLY the keys the prereg names.  Any headline this file
prints that is not a named key is NOT the graded statistic (prereg convention C, #123).
"""
import json
import sys
import time

import mpmath as mp

# The instrument module is committed in this repo as data/code/machine2_cycle21_zeta2_xi.py
# (byte-identical to the workspace copy imported here; verified with diff at commit time).
sys.path.insert(0, "/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2  # noqa: E402

DPS = 60
mp.mp.dps = DPS
TOL = mp.mpf(10) ** (-52)

DSTAR = mp.mpf("0.141733239663887191395415685084185024")
A = mp.mpf("2.645521411811664489")
B = -mp.mpf("7.4624528767937415788")
B_OLD = -mp.mpf("7.46245287679")

# m1-L165 sect9a published column (eps literal -> u at dps 50).  Used for G1/G2 and for the
# 11-rung side of the union fit.  PUBLISHED DATA, not recomputed except at the two gate rungs.
L165_9A = [
    ("0.001",              "0.05150723818940063653522997138655916611777128352831"),
    ("0.0011239031932557", "0.054614584740162860829271236079197856379810987308508"),
    ("0.002",              "0.072945092837465636911527414020464645263120485246671"),
    ("0.0035",             "0.09670183421043065840984313002276196906002275045949"),
    ("0.006",              "0.12706034318675893153656817913317280690430806327895"),
    ("0.0082667603361",    "0.14962144595780802891341103521644637411107076093496"),
    ("0.012",              "0.18122223459720552038513232631511513662541625076064"),
    ("0.02",               "0.23662703502895471893639804350283991882970959834519"),
    ("0.035",              "0.31979403084190422618229559433082050463362878645843"),
    ("0.06",               "0.43405746526370626569197604987746105430711695666647"),
    ("0.1",                "0.59427921830513711248148784269207030531776649353816"),
]
NEW_EPS = ["0.0001", "0.00015", "0.00022", "0.00033", "0.0005", "0.00075"]
GATE_EPS = ["0.001", "0.0082667603361"]


def r_of(eps, u, a=A, b=B):
    return (u ** 2 - a * eps + b * eps ** 2) / eps ** 3


def polyfit(xs, ys, K, extra=None):
    """LS fit on basis [1, x, ..., x^K] (+ optional extra basis functions)."""
    basis = [(lambda x, i=i: x ** i) for i in range(K + 1)]
    if extra:
        basis = basis + list(extra)
    n = len(basis)
    M = mp.matrix(n, n)
    v = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            M[i, j] = mp.fsum([basis[i](x) * basis[j](x) for x in xs])
        v[i] = mp.fsum([y * basis[i](x) for x, y in zip(xs, ys)])
    c = mp.lu_solve(M, v)
    return [c[i] for i in range(n)], basis


def evalfit(c, basis, x):
    return mp.fsum([ci * b(x) for ci, b in zip(c, basis)])


def loo_rms(xs, ys, K, extra=None):
    """Interior leave-one-out rms (endpoints excluded: dropping them is extrapolation)."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    interior = order[1:-1]
    errs = []
    for i in interior:
        xr = [xs[j] for j in range(len(xs)) if j != i]
        yr = [ys[j] for j in range(len(ys)) if j != i]
        c, basis = polyfit(xr, yr, K, extra)
        errs.append(evalfit(c, basis, xs[i]) - ys[i])
    return mp.sqrt(mp.fsum([e ** 2 for e in errs]) / len(errs))


def maxres(xs, ys, K, extra=None):
    c, basis = polyfit(xs, ys, K, extra)
    return max(abs(evalfit(c, basis, x) - y) for x, y in zip(xs, ys)), c, basis


def first_online_zero(Z, t_guess):
    f = lambda t: mp.re(Z.xi(mp.mpf(0.5) + 1j * mp.mpf(t)))
    f0 = f(mp.mpf(10) ** (-14))
    lo = t_guess / 4
    hi = t_guess * 4
    flo = f(lo)
    branch = None
    if mp.sign(flo) != mp.sign(f0):
        branch = "left-of-guess (bracket [1e-14, t_guess/4])"
        hi, lo = lo, mp.mpf(10) ** (-14)
        flo = f0
    else:
        branch = "right-expansion (bracket grown by 1.5x from t_guess*4)"
        fhi = f(hi)
        n = 0
        while mp.sign(flo) == mp.sign(fhi) and n < 60:
            lo, flo = hi, fhi
            hi = hi * mp.mpf("1.5")
            fhi = f(hi)
            n += 1
        if mp.sign(flo) == mp.sign(fhi):
            raise RuntimeError("no sign change found")
    root = mp.findroot(f, (lo, hi), solver="anderson", tol=TOL)
    u = mp.mpf(root.real if hasattr(root, "real") else root)
    return u, f(u), branch


def solve(es):
    eps = mp.mpf(es)
    D = DSTAR + eps
    t_law = mp.sqrt((A - B * eps) * eps + mp.mpf("11.7007173") * eps ** 3)
    t0 = time.time()
    Z = Zeta2(D, dps=DPS)
    u, resid, branch = first_online_zero(Z, t_law)
    return dict(eps=es, u=u, resid=resid, branch=branch, secs=time.time() - t0)


def main():
    out = {"unit": "m2 c30 denser small-eps ladder", "dps": DPS,
           "prereg_sha256_expected_from_seals_file": "see c30_seals.txt",
           "gate": {}, "rungs": {}, "fit17": {}, "control": {}, "notes": {}}

    E11 = [mp.mpf(e) for e, _ in L165_9A]
    U11 = [mp.mpf(u) for _, u in L165_9A]
    R11 = [r_of(e, u) for e, u in zip(E11, U11)]

    # ---------------- LAUNCH GATE ----------------
    print("=== LAUNCH GATE ===")
    gate_ok = True
    for es in GATE_EPS:
        row = solve(es)
        pub = mp.mpf(dict(L165_9A)[es])
        rel = abs(row["u"] - pub) / pub
        ok = rel <= mp.mpf("1e-24")
        gate_ok = gate_ok and ok
        key = "G1" if es == "0.001" else "G2"
        out["gate"][key] = {"eps": es, "u_mine": mp.nstr(row["u"], 40),
                            "u_published_m1_L165_9a": mp.nstr(pub, 40),
                            "rel_dev": mp.nstr(rel, 8), "threshold": "1e-24",
                            "pass": bool(ok), "internal_residual_xi": mp.nstr(abs(row["resid"]), 6),
                            "bracket_branch": row["branch"], "secs": round(row["secs"], 1)}
        print("  %s eps=%-18s rel_dev=%-14s %s  (%.0fs)" %
              (key, es, mp.nstr(rel, 8), "PASS" if ok else "FAIL", row["secs"]))

    # G3: the design fit reproduces the published ladder
    lo_best, K_best = None, None
    for K in range(3, 9):
        lo = loo_rms(E11, R11, K)
        if lo_best is None or lo < lo_best:
            lo_best, K_best = lo, K
    c6, b6 = polyfit(E11, R11, 6)
    a3_11 = c6[0]
    mr8, _, _ = maxres(E11, R11, 8)
    g3 = (K_best == 6 and abs(a3_11 - mp.mpf("11.700717319895873971")) < mp.mpf("1e-15")
          and abs(mr8 - mp.mpf("8.67039e-11")) / mp.mpf("8.67039e-11") < mp.mpf("0.01"))
    gate_ok = gate_ok and g3
    out["gate"]["G3"] = {"loo_optimal_K_11rung": K_best, "a3_K6_11rung": mp.nstr(a3_11, 22),
                         "max_res_K8_11rung": mp.nstr(mr8, 8), "pass": bool(g3)}
    print("  G3 K*=%d a3=%s res8=%s  %s" % (K_best, mp.nstr(a3_11, 22), mp.nstr(mr8, 8),
                                            "PASS" if g3 else "FAIL"))

    # G4: defect injection -- drop the b*eps^2 term at eps=1e-4 and demand rel > 1e3
    e4 = mp.mpf("0.0001")
    u4_pred = mp.sqrt((A - B * e4) * e4 + mp.mpf("11.7027650564465416") * e4 ** 3)
    r_clean = r_of(e4, u4_pred)
    r_defect = (u4_pred ** 2 - A * e4) / e4 ** 3          # b term DROPPED
    relmove = abs(r_defect - r_clean) / abs(r_clean)
    g4 = relmove > mp.mpf("1e3")
    gate_ok = gate_ok and g4
    out["gate"]["G4"] = {"rel_move_when_b_term_dropped": mp.nstr(relmove, 8),
                         "threshold": "> 1e3", "pass": bool(g4)}
    print("  G4 defect-injection rel move = %s  %s" % (mp.nstr(relmove, 8), "PASS" if g4 else "FAIL"))

    out["gate"]["ALL_PASS"] = bool(gate_ok)
    if not gate_ok:
        out["notes"]["outcome"] = "RED -- gate failed, NOTHING graded (prereg convention D)"
        json.dump(out, open("m2_c30_scored.json", "w"), indent=1)
        print("\nOUTCOME RED -- gate failed, nothing scored.")
        return

    # ---------------- THE NEW RUNGS ----------------
    print("\n=== NEW RUNGS (all below the entire published grid) ===")
    Enew, Unew, Rnew = [], [], []
    for es in NEW_EPS:
        row = solve(es)
        eps = mp.mpf(es)
        r = r_of(eps, row["u"])
        r_pred = evalfit(c6, b6, eps)
        dev = abs(r - r_pred)
        r_bold = r_of(eps, row["u"], b=B_OLD)
        Enew.append(eps); Unew.append(row["u"]); Rnew.append(r)
        out["rungs"][es] = {
            "u": mp.nstr(row["u"], 40),
            "r": mp.nstr(r, 24),
            "r_pred_K6_11rung": mp.nstr(r_pred, 24),
            "dev_K6_extrap": mp.nstr(dev, 10),
            "internal_residual_xi": mp.nstr(abs(row["resid"]), 6),
            "bracket_branch": row["branch"],
            "r_with_retired_12sf_b": mp.nstr(r_bold, 24),
            "shift_from_retired_b": mp.nstr(abs(r_bold - r), 10),
            "secs": round(row["secs"], 1),
        }
        print("  eps=%-9s u=%s r=%s dev=%-12s |xi|=%-10s %.0fs" %
              (es, mp.nstr(row["u"], 26), mp.nstr(r, 18), mp.nstr(dev, 6),
               mp.nstr(abs(row["resid"]), 4), row["secs"]))

    # ---------------- UNION FIT ----------------
    E17 = E11 + Enew
    R17 = R11 + Rnew
    print("\n=== 17-RUNG UNION FIT ===")
    lo_best, K_best = None, None
    ladder = {}
    for K in range(3, 11):
        lo = loo_rms(E17, R17, K)
        mr, c, _ = maxres(E17, R17, K)
        ladder[K] = {"loo_rms": mp.nstr(lo, 8), "max_res": mp.nstr(mr, 8), "a3": mp.nstr(c[0], 22)}
        print("  K=%-3d loo=%-14s res=%-14s a3=%s" % (K, mp.nstr(lo, 6), mp.nstr(mr, 6),
                                                      mp.nstr(c[0], 22)))
        if lo_best is None or lo < lo_best:
            lo_best, K_best = lo, K
    cbest, bbest = polyfit(E17, R17, K_best)
    a3_17 = cbest[0]
    a3s = {}
    for K in (6, 7, 8):
        c, _ = polyfit(E17, R17, K)
        a3s[K] = c[0]
    spread17 = max(a3s.values()) - min(a3s.values())
    lo_half = loo_rms(E17, R17, K_best, extra=[lambda x: mp.sqrt(x)])

    out["fit17"] = {
        "ladder": ladder,
        "loo_optimal_K": K_best,
        "a3": mp.nstr(a3_17, 22),
        "a3_reference_11rung_K6": "11.700717319895873971",
        "a3_shift_abs": mp.nstr(abs(a3_17 - mp.mpf("11.700717319895873971")), 10),
        "a3_spread_K6to8": mp.nstr(spread17, 10),
        "a3_spread_K6to8_11rung_reference": "3.4931094e-9",
        "loo_rms_base": mp.nstr(lo_best, 10),
        "loo_rms_half": mp.nstr(lo_half, 10),
        "a3_by_K": {str(k): mp.nstr(v, 22) for k, v in a3s.items()},
    }
    print("  LOO-optimal K = %d ; a3 = %s ; shift = %s" %
          (K_best, mp.nstr(a3_17, 22), mp.nstr(abs(a3_17 - mp.mpf("11.700717319895873971")), 8)))
    print("  a3 spread K6..8 = %s  (11-rung reference 3.4931094e-9)" % mp.nstr(spread17, 8))
    print("  LOO rms base = %s ; with eps^(1/2) = %s" % (mp.nstr(lo_best, 8), mp.nstr(lo_half, 8)))

    # ---------------- DECLARED CONTROL C1 ----------------
    small = [es for es in NEW_EPS if mp.mpf(es) <= mp.mpf("0.00033")]
    minshift = min(mp.mpf(out["rungs"][es]["shift_from_retired_b"]) for es in small)
    out["control"]["C1_min_shift_over_small_rungs"] = mp.nstr(minshift, 10)
    out["control"]["C1_rungs"] = small
    out["control"]["C1_note"] = ("firing world EMPTY BY ALGEBRA, declared at birth; "
                                 "implementation control, not an object prediction")
    print("\n  C1 control: min shift from the retired 12-s.f. b over eps<=3.3e-4 = %s"
          % mp.nstr(minshift, 8))

    json.dump(out, open("m2_c30_scored.json", "w"), indent=1)
    print("\nwrote m2_c30_scored.json")


if __name__ == "__main__":
    main()
