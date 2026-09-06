"""machine2 CYCLE 32 -- determination of `a` from the LADDER DATA with NO `a` IN THE HEADER.

The whole a-dispute is an artefact of a parametrisation: every published determination forms
    r(eps) = (u^2 - a_used*eps + b*eps^2) / eps^3
and then reads an eps^-2 coefficient c0 = a_true - a_used.  The disputed constant is an INPUT.

Algebraically identical information, no input constant:
    u^2 / eps = a - b*eps + r(eps)*eps^2
so a plain polynomial least squares of y = u^2/eps against {1, eps, ..., eps^K} returns `a`
DIRECTLY as the constant term, with a and b both free.  No a_used, no b, no c0, no injection.

Data: only the 12 m2 rungs (6 from c30, 6 out-of-sample from c31b), all published, all solved
on the m2 xi_D 1-D real root find.  m1's 11 heat72x rungs are added only as a SEPARATE row so
the two lineages can be compared without pooling them.
"""
import json
import sys

import mpmath as mp

mp.mp.dps = 80

C30 = json.load(open("/workspace/rh/cycle30/m2_c30_scored.json"))["rungs"]
C31B = json.load(open("/workspace/rh/cycle31/m2_c31b_scored.json"))["rungs"]

M1_HEAT72X = [  # eps literal -> u at dps 50, m1-L165 sect 9a published column
    ("0.001", "0.05150723818940063653522997138655916611777128352831"),
    ("0.0011239031932557", "0.054614584740162860829271236079197856379810987308508"),
    ("0.002", "0.072945092837465636911527414020464645263120485246671"),
    ("0.0035", "0.09670183421043065840984313002276196906002275045949"),
    ("0.006", "0.12706034318675893153656817913317280690430806327895"),
    ("0.0082667603361", "0.14962144595780802891341103521644637411107076093496"),
    ("0.012", "0.18122223459720552038513232631511513662541625076064"),
    ("0.02", "0.23662703502895471893639804350283991882970959834519"),
    ("0.035", "0.31979403084190422618229559433082050463362878645843"),
    ("0.06", "0.43405746526370626569197604987746105430711695666647"),
    ("0.1", "0.59427921830513711248148784269207030531776649353816"),
]
M1_HEAT86B = [  # m1's own six rungs, data/machine1_heat86b_results.json (his lineage, my grid)
    ("0.0001", "0.016267353116370815436521662356481985337487201480639"),
    ("0.00015", "0.019924762394110635273342326173461402826314494537478"),
    ("0.00022", "0.02413246812812595998486983709533875808144894305693"),
    ("0.00033", "0.029560702761397693562532171129200615891469008031872"),
    ("0.0005", "0.036395436293510592613058142574334602175332274922237"),
    ("0.00075", "0.044590846945589617275344158652007762656432566989551"),
]

A_DERIV = mp.mpf("2.6455214118116628680161261212034")   # this cycle's ladder-free value
REFS = [
    ("retired 16 s.f.", "2.645521411811663"),
    ("#120 19 s.f.   ", "2.645521411811664489"),
    ("m1 band-A      ", "2.645521411811662855605"),
    ("operative 17 sf", "2.6455214118116629"),
    ("c31 a_corr+c0  ", None),   # filled below
]


def rows_m2():
    out = []
    for e, d in C30.items():
        out.append((mp.mpf(e), mp.mpf(d["u"])))
    for e, d in C31B.items():
        out.append((mp.mpf(e), mp.mpf(d["u"])))
    return sorted(out)


def fit_const(rows, K):
    """LS of u^2/eps on {1,eps,...,eps^K}; return the constant term = a."""
    A = mp.matrix(len(rows), K + 1)
    y = mp.matrix(len(rows), 1)
    for i, (e, u) in enumerate(rows):
        for j in range(K + 1):
            A[i, j] = e ** j
        y[i] = u ** 2 / e
    coef = mp.lu_solve(A.T * A, A.T * y)
    resid = max(abs((A * coef - y)[i]) for i in range(len(rows)))
    return coef[0], resid


def main():
    m2 = rows_m2()
    m1x = sorted((mp.mpf(e), mp.mpf(u)) for e, u in M1_HEAT72X)
    m186 = sorted((mp.mpf(e), mp.mpf(u)) for e, u in M1_HEAT86B)

    print(f"m2 rungs (c30 + c31b): n={len(m2)}  eps in [{mp.nstr(m2[0][0],3)}, {mp.nstr(m2[-1][0],3)}]")
    print(f"m1 heat72x published : n={len(m1x)} eps in [{mp.nstr(m1x[0][0],3)}, {mp.nstr(m1x[-1][0],3)}]")
    print(f"m1 heat86b six       : n={len(m186)} eps in [{mp.nstr(m186[0][0],3)}, {mp.nstr(m186[-1][0],3)}]")
    print()
    for label, rows in [("m2 12 rungs (c30+c31b)", m2),
                        ("m1 heat86b 6 rungs", m186),
                        ("m1 heat72x 11 rungs", m1x),
                        ("m2 12 + m1 heat72x 11 = 23", sorted(m2 + m1x))]:
        print(f"--- {label} ---")
        Kmax = min(len(rows) - 2, 9)
        for K in range(2, Kmax + 1):
            a, res = fit_const(rows, K)
            print(f"   K={K}  a = {mp.nstr(a, 22):<26s} a-A_DERIV = {mp.nstr(a - A_DERIV, 6):>14s} "
                  f" maxres = {mp.nstr(res, 4)}")
        print()

    print("=== reference comparisons against the ladder-free derivative value ===")
    a_corr = mp.mpf("2.645521411811664489") - mp.mpf("1.633394698e-15")
    c0_new = mp.mpf("1.18153194401e-17")
    REFS[-1] = ("c31 a_corr+c0  ", mp.nstr(a_corr + c0_new, 25))
    for name, s in REFS:
        v = mp.mpf(s)
        print(f"  A_DERIV - [{name} {s:<26s}] = {mp.nstr(A_DERIV - v, 8)}")
    print()
    print(f"  a_corr (m1 band-A, recomputed) = {mp.nstr(a_corr, 25)}")
    print(f"  A_DERIV - a_corr               = {mp.nstr(A_DERIV - a_corr, 10)}")
    print(f"  m2 c31 out-of-sample c0_new    = {mp.nstr(c0_new, 10)}")
    print(f"  DIFFERENCE (residual of resid) = {mp.nstr(A_DERIV - a_corr - c0_new, 6)}")
    print()
    print(f"  A_DERIV rounded to 17 s.f.     = {mp.nstr(A_DERIV, 17)}")
    print(f"  A_DERIV rounded to 18 s.f.     = {mp.nstr(A_DERIV, 18)}")
    print(f"  A_DERIV rounded to 19 s.f.     = {mp.nstr(A_DERIV, 19)}")


if __name__ == "__main__":
    main()


def rung17():
    """The EXACT 17-rung set my c30 fit used: m1's 11 published heat72x u + m2's 6 c30 u."""
    m1x = [(mp.mpf(e), mp.mpf(u)) for e, u in M1_HEAT72X]
    m2c30 = [(mp.mpf(e), mp.mpf(d["u"])) for e, d in C30.items()]
    return sorted(m1x + m2c30)


def extra():
    print("\n\n=== THE 17-RUNG SET (m1's 11 published + m2's 6 c30) -- header-free ===")
    rows = rung17()
    print(f"n = {len(rows)}")
    for K in range(4, 12):
        a, res = fit_const(rows, K)
        print(f"   K={K:2d}  a = {mp.nstr(a, 22):<26s} a-A_DERIV = {mp.nstr(a - A_DERIV, 6):>14s}"
              f"  maxres = {mp.nstr(res, 4)}")
    print("\n=== SUBSET SENSITIVITY: how much does each block move `a`? ===")
    m1x = sorted((mp.mpf(e), mp.mpf(u)) for e, u in M1_HEAT72X)
    m2c30 = sorted((mp.mpf(e), mp.mpf(d["u"])) for e, d in C30.items())
    m2c31 = sorted((mp.mpf(e), mp.mpf(d["u"])) for e, d in C31B.items())
    m186 = sorted((mp.mpf(e), mp.mpf(u)) for e, u in M1_HEAT86B)
    for label, rows, K in [
        ("m2 c30 six alone           ", m2c30, 4),
        ("m1 heat86b six alone       ", m186, 4),
        ("m2 c31b six alone          ", m2c31, 4),
        ("m2 twelve (c30+c31b)       ", sorted(m2c30 + m2c31), 6),
        ("m1 6 + m2 c31b 6 (12 fine) ", sorted(m186 + m2c31), 6),
        ("17-rung (m1 11 + m2 c30 6) ", rung17(), 9),
        ("23-rung union              ", sorted(m2c30 + m2c31 + m1x), 9),
    ]:
        a, res = fit_const(rows, K)
        print(f"   {label} K={K}  a-A_DERIV = {mp.nstr(a - A_DERIV, 6):>14s}   (c0 vs #120 = "
              f"{mp.nstr(a - mp.mpf('2.645521411811664489'), 10)})")


extra()
