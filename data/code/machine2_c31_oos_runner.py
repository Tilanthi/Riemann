"""machine2 CYCLE 31 -- RUNNER for the out-of-sample test of the c30 a-correction.

Frozen prereg: m2_c31_prereg.json.  Its sha256 and this file's sha256 are pushed to
Tilanthi/Riemann BEFORE this file is executed.

Emits m2_c31_scored.json with EXACTLY the keys the prereg names.  Grading is done by the
separate m2_c31_grade.py, whose sha256 is also published before the run.
"""
import hashlib
import json
import os
import sys
import time

import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle21")
from m2_zeta2_xi import Zeta2  # noqa: E402

DPS = 60
mp.mp.dps = DPS
TOL = mp.mpf(10) ** (-52)

DSTAR = mp.mpf("0.141733239663887191395415685084185024")
A_OP = mp.mpf("2.645521411811664489")
DA = mp.mpf("-1.633394698e-15")
A_CORR = A_OP + DA
B = -mp.mpf("7.4624528767937415788")

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
C30_NEW = [
    ("0.0001",   "0.01626735311637081543652166235648198533749"),
    ("0.00015",  "0.01992476239411063527334232617346140282631"),
    ("0.00022",  "0.02413246812812595998486983709533875808145"),
    ("0.00033",  "0.02956070276139769356253217112920061589147"),
    ("0.0005",   "0.03639543629351059261305814257433460217533"),
    ("0.00075",  "0.04459084694558961727534415865200776265643"),
]
NEW31 = ["0.000025", "0.000035", "0.00005", "0.00007", "0.00012", "0.00027"]

FROZEN_C6 = [
    "11.7007173210511537630453",
    "20.47553739882611907948",
    "18.2716890360723554429996",
    "64.4770993693074402248845",
    "-89.8393794823499604002842",
    "574.847683356945215920758",
    "-1110.22928803680090303407",
]


def r_of(eps, u, a=None):
    a = A_CORR if a is None else a
    return (u ** 2 - a * eps + B * eps ** 2) / eps ** 3


def polybasis(K):
    return [(lambda x, i=i: x ** i) for i in range(K + 1)]


INV2 = [lambda x: x ** -2]


def design(xs, basis):
    X = mp.matrix(len(xs), len(basis))
    for i, x in enumerate(xs):
        for j, b in enumerate(basis):
            X[i, j] = b(x)
    return X


def fit_normal(xs, ys, basis):
    n = len(basis)
    M = mp.matrix(n, n)
    v = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            M[i, j] = mp.fsum([basis[i](x) * basis[j](x) for x in xs])
        v[i] = mp.fsum([y * basis[i](x) for x, y in zip(xs, ys)])
    c = mp.lu_solve(M, v)
    return [c[i] for i in range(n)]


def fit_qr(xs, ys, basis):
    X = design(xs, basis)
    y = mp.matrix(len(ys), 1)
    for i, yy in enumerate(ys):
        y[i] = yy
    c = mp.qr_solve(X, y)[0]
    return [c[i] for i in range(len(basis))]


def ev(c, basis, x):
    return mp.fsum([ci * b(x) for ci, b in zip(c, basis)])


def first_online_zero(Z, t_guess):
    f = lambda t: mp.re(Z.xi(mp.mpf(0.5) + 1j * mp.mpf(t)))
    f0 = f(mp.mpf(10) ** (-14))
    lo = t_guess / 4
    hi = t_guess * 4
    flo = f(lo)
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
    t_law = mp.sqrt((A_OP - B * eps) * eps + mp.mpf("11.7007173") * eps ** 3)
    t0 = time.time()
    Z = Zeta2(D, dps=DPS)
    u, resid, branch = first_online_zero(Z, t_law)
    return dict(eps=es, u=u, resid=resid, branch=branch, secs=time.time() - t0)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = {
        "unit": "m2 c31 out-of-sample test of the c30 a-correction",
        "dps": DPS,
        "runner_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
        "prereg_sha256": hashlib.sha256(
            open(os.path.join(here, "m2_c31_prereg.json"), "rb").read()).hexdigest(),
        "gate": {}, "rungs": {}, "V1": {}, "V2": {}, "V3": {}, "diagnostics": {}, "notes": {},
    }

    E11 = [mp.mpf(e) for e, _ in L165_9A]
    U11 = [mp.mpf(u) for _, u in L165_9A]
    E6 = [mp.mpf(e) for e, _ in C30_NEW]
    U6 = [mp.mpf(u) for _, u in C30_NEW]
    E17 = E11 + E6
    U17 = U11 + U6
    R17 = [r_of(e, u) for e, u in zip(E17, U17)]
    ENEW = [mp.mpf(e) for e in NEW31]
    c6 = [mp.mpf(s) for s in FROZEN_C6]
    b6 = polybasis(6)

    gate_ok = True
    print("=== LAUNCH GATE ===")

    # G1 cross-lineage anchor
    row = solve("0.001")
    pub = mp.mpf(dict(L165_9A)["0.001"])
    rel = abs(row["u"] - pub) / pub
    g1 = rel <= mp.mpf("1e-24")
    gate_ok = gate_ok and g1
    out["gate"]["G1"] = {"eps": "0.001", "rel_dev_vs_m1_L165_9a": mp.nstr(rel, 8),
                         "threshold": "1e-24", "pass": bool(g1), "secs": round(row["secs"], 1)}
    print("  G1 eps=1e-3 rel=%s  %s (%.0fs)" % (mp.nstr(rel, 8), "PASS" if g1 else "FAIL",
                                                row["secs"]))

    # G2 cross-cycle determinism against m2's own committed c30 literal
    row = solve("0.0001")
    own = mp.mpf(dict(C30_NEW)["0.0001"])
    rel2 = abs(row["u"] - own) / own
    g2 = rel2 <= mp.mpf("1e-40")
    gate_ok = gate_ok and g2
    out["gate"]["G2"] = {"eps": "0.0001", "rel_dev_vs_m2_c30_own_literal": mp.nstr(rel2, 8),
                         "threshold": "1e-40", "pass": bool(g2), "secs": round(row["secs"], 1)}
    print("  G2 eps=1e-4 rel=%s  %s (%.0fs)" % (mp.nstr(rel2, 8), "PASS" if g2 else "FAIL",
                                                row["secs"]))

    # G3 b-drop defect injection at the smallest new rung, on the PREDICTED u (no new solve)
    e0 = mp.mpf("0.000025")
    u0 = mp.sqrt(ev(c6, b6, e0) * e0 ** 3 + A_CORR * e0 - B * e0 ** 2)
    r_clean = r_of(e0, u0)
    r_defect = (u0 ** 2 - A_CORR * e0) / e0 ** 3
    relmove = abs(r_defect - r_clean) / abs(r_clean)
    g3 = relmove > mp.mpf("1e3")
    gate_ok = gate_ok and g3
    out["gate"]["G3"] = {"rel_move_when_b_term_dropped": mp.nstr(relmove, 8), "threshold": "> 1e3",
                         "pass": bool(g3)}
    print("  G3 b-drop rel move = %s  %s" % (mp.nstr(relmove, 8), "PASS" if g3 else "FAIL"))

    # G4 truncation-power control on THIS eps design
    biases = []
    for Ksyn in (6, 7, 8, 9):
        csyn = fit_normal(E17, R17, polybasis(Ksyn))
        bsyn = polybasis(Ksyn)
        rsyn = [ev(csyn, bsyn, e) for e in ENEW]
        for Kfit in (2, 3):
            c = fit_normal(ENEW, rsyn, INV2 + polybasis(Kfit))
            biases.append(abs(c[0]))
    Bmax = max(biases)
    g4 = Bmax <= mp.mpf("1e-18")
    gate_ok = gate_ok and g4
    out["gate"]["G4"] = {"max_synthetic_c0_bias": mp.nstr(Bmax, 8), "threshold": "<= 1e-18",
                         "pass": bool(g4), "n_combinations": len(biases)}
    print("  G4 truncation-power |c0_bias| max = %s  %s" % (mp.nstr(Bmax, 8),
                                                            "PASS" if g4 else "FAIL"))

    out["gate"]["ALL_PASS_pre_rungs"] = bool(gate_ok)
    if not gate_ok:
        out["notes"]["outcome"] = "RED -- gate failed before any new rung; NOTHING graded"
        json.dump(out, open(os.path.join(here, "m2_c31_scored.json"), "w"), indent=1)
        print("\nOUTCOME RED -- gate failed, nothing scored.")
        return

    # ---------------- THE SIX NEW RUNGS ----------------
    print("\n=== SIX NEW RUNGS (four below the entire 17-rung grid) ===")
    Rnew = []
    for es in NEW31:
        row = solve(es)
        eps = mp.mpf(es)
        r = r_of(eps, row["u"])
        r_pred = ev(c6, b6, eps)
        dev = r - r_pred
        t2 = mp.mpf("1.8908475e-16") / eps ** 2 + 3 * mp.mpf("7.005899e-10")
        Rnew.append(r)
        out["rungs"][es] = {
            "u": mp.nstr(row["u"], 40),
            "r_corrected_a": mp.nstr(r, 24),
            "r_pred_frozen_curve": mp.nstr(r_pred, 24),
            "dev_signed": mp.nstr(dev, 10),
            "T2": mp.nstr(t2, 8),
            "within_T2": bool(abs(dev) <= t2),
            "internal_residual_xi": mp.nstr(abs(row["resid"]), 6),
            "bracket_branch": row["branch"],
            "secs": round(row["secs"], 1),
        }
        print("  eps=%-9s u=%s dev=%-13s T2=%-11s %s |xi|=%-9s %.0fs" %
              (es, mp.nstr(row["u"], 24), mp.nstr(dev, 6), mp.nstr(t2, 4),
               "in " if abs(dev) <= t2 else "OUT", mp.nstr(abs(row["resid"]), 4), row["secs"]))

    # ---------------- V1 ----------------
    basis1 = INV2 + polybasis(3)
    c_v1 = fit_normal(ENEW, Rnew, basis1)
    c_v1_qr = fit_qr(ENEW, Rnew, basis1)
    relsolve = abs(c_v1[0] - c_v1_qr[0]) / abs(c_v1[0]) if c_v1[0] != 0 else mp.mpf(0)
    g5 = relsolve <= mp.mpf("1e-8")
    maxres1 = max(abs(ev(c_v1, basis1, e) - r) for e, r in zip(ENEW, Rnew))
    out["gate"]["G5"] = {"rel_dev_lu_vs_qr_on_c0": mp.nstr(relsolve, 8), "threshold": "<= 1e-8",
                         "pass": bool(g5)}
    out["V1"] = {"c0_new_six_rungs_alone": mp.nstr(c_v1[0], 12),
                 "c0_new_qr": mp.nstr(c_v1_qr[0], 12),
                 "max_in_sample_residual": mp.nstr(maxres1, 8),
                 "T1": "1.8908475e-16",
                 "basis": "[eps^-2, 1, eps, eps^2, eps^3]"}
    print("\n=== V1 ===\n  c0_new = %s  (qr %s, rel %s)  max res %s"
          % (mp.nstr(c_v1[0], 12), mp.nstr(c_v1_qr[0], 12), mp.nstr(relsolve, 6),
             mp.nstr(maxres1, 8)))

    # ---------------- V2 ----------------
    c_v2 = fit_normal(ENEW, Rnew, polybasis(3))
    a3_new = c_v2[0]
    ref = mp.mpf("11.70071732105115376305")
    out["V2"] = {"a3_new_six_rungs_alone_plainK3": mp.nstr(a3_new, 22),
                 "reference": "11.70071732105115376305",
                 "dev": mp.nstr(abs(a3_new - ref), 8), "T3": "1.128194e-9"}
    print("=== V2 ===\n  a3_new = %s  dev = %s  (T3 1.128194e-9)"
          % (mp.nstr(a3_new, 22), mp.nstr(abs(a3_new - ref), 8)))

    # ---------------- D1 declared-empty-by-algebra diagnostic ----------------
    rinj = [r + mp.mpf("5e-15") / e ** 2 for e, r in zip(ENEW, Rnew)]
    c_inj = fit_normal(ENEW, rinj, basis1)
    out["diagnostics"]["D1_injection_empty_by_algebra"] = {
        "injected": "+5e-15 into a  (equivalently +5e-15/eps^2 into every r)",
        "recovered_c0_shift": mp.nstr(c_inj[0] - c_v1[0], 12),
        "expected_exactly": "5e-15",
        "status": "implementation diagnostic ONLY -- firing world empty by algebra, declared at birth"}
    print("=== D1 (empty by algebra) ===\n  recovered shift = %s (expect exactly 5e-15)"
          % mp.nstr(c_inj[0] - c_v1[0], 12))

    # ---------------- reported context ----------------
    c_v1_op = fit_normal(ENEW, [r + (-DA) / e ** 2 for e, r in zip(ENEW, Rnew)], basis1)
    out["diagnostics"]["c0_new_with_a_operative"] = mp.nstr(c_v1_op[0], 12)
    E23 = E17 + ENEW
    R23 = R17 + Rnew
    lad = {}
    for K in range(3, 10):
        cc = fit_normal(E23, R23, polybasis(K))
        mr = max(abs(ev(cc, polybasis(K), e) - r) for e, r in zip(E23, R23))
        lad[str(K)] = {"max_res": mp.nstr(mr, 8), "a3": mp.nstr(cc[0], 22)}
    out["diagnostics"]["union_23_rung_plain_fit_corrected_a"] = lad
    out["gate"]["ALL_PASS"] = bool(gate_ok and g5)

    json.dump(out, open(os.path.join(here, "m2_c31_scored.json"), "w"), indent=1)
    print("\nwrote m2_c31_scored.json")


if __name__ == "__main__":
    main()
