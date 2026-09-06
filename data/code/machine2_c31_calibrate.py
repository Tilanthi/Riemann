"""machine2 CYCLE 31 -- TOLERANCE CALIBRATION for the a-correction out-of-sample test.

Runs on SEEN DATA ONLY (m1-L165 sect9a's 11 published u literals + m2's own 6 c30 u literals,
both already committed to Tilanthi/Riemann).  NO new rung is solved here.  Its whole purpose is
to fix the numeric tolerances of the cycle-31 prereg by a MECHANICAL rule BEFORE any new rung
exists, so that the verdict cannot be reached by a movable tolerance.

Outputs -> c31_calib.out  (quoted verbatim into the prereg).
"""
import mpmath as mp

mp.mp.dps = 60

A_OP = mp.mpf("2.645521411811664489")          # m1-L164 sect5 as corrected by #120, operative
DA = mp.mpf("-1.633394698e-15")                # c30 joint 17-rung K=6 measurement, FROZEN literal
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

# the six PROPOSED cycle-31 rungs.  Fixed here, before any of them is solved.
# four are BELOW the entire 17-rung grid; two interpolate inside it.  None has been computed by
# any machine: m1's heat86 re-uses m2's c30 six, and the 11 published are m1-L165 sect9a's grid.
NEW31 = ["0.000025", "0.000035", "0.00005", "0.00007", "0.00012", "0.00027"]


def r_of(eps, u, a):
    return (u ** 2 - a * eps + B * eps ** 2) / eps ** 3


def fit(xs, ys, basis):
    n = len(basis)
    M = mp.matrix(n, n)
    v = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            M[i, j] = mp.fsum([basis[i](x) * basis[j](x) for x in xs])
        v[i] = mp.fsum([y * basis[i](x) for x, y in zip(xs, ys)])
    c = mp.lu_solve(M, v)
    return [c[i] for i in range(n)]


def polybasis(K):
    return [(lambda x, i=i: x ** i) for i in range(K + 1)]


def inv2():
    return [lambda x: x ** -2]


def ev(c, basis, x):
    return mp.fsum([ci * b(x) for ci, b in zip(c, basis)])


E11 = [mp.mpf(e) for e, _ in L165_9A]
U11 = [mp.mpf(u) for _, u in L165_9A]
E6 = [mp.mpf(e) for e, _ in C30_NEW]
U6 = [mp.mpf(u) for _, u in C30_NEW]
E17 = E11 + E6
U17 = U11 + U6
ENEW = [mp.mpf(e) for e in NEW31]

out = []
P = out.append

P("=== 0. constants (all FROZEN literals) ===")
P("  a_operative = %s" % mp.nstr(A_OP, 22))
P("  delta_a     = %s   (c30 joint 17-rung K=6, frozen literal)" % mp.nstr(DA, 12))
P("  a_corrected = %s" % mp.nstr(A_CORR, 24))

# ---------------------------------------------------------------- S: estimator spread
P("\n=== 1. S -- the spread of the cycle-30 estimator family for c0 ===")
FAMILY = {
    "joint 17-rung K=6, basis [eps^-2 + poly6]": mp.mpf("-1.633394698e-15"),
    "joint 17-rung K=6 + eps^-1 in basis":       mp.mpf("-1.585179e-15"),
    "joint 17-rung K=5":                          mp.mpf("-1.927230284e-15"),
    "six c30 rungs alone, K=3":                   mp.mpf("-1.623411826e-15"),
    "six c30 rungs alone, K=2":                   mp.mpf("-1.64820725e-15"),
    "1-D max-residual scan":                      mp.mpf("-1.639822722e-15"),
}
for k, v in FAMILY.items():
    P("  %-42s %s" % (k, mp.nstr(v, 12)))
vals = list(FAMILY.values())
S_all = max(vals) - min(vals)
# K=5 is excluded from the headline spread by a rule stated here: c30's own LOO convention
# selected K=6; K=5 is a rejected model, not a member of the accepted estimator family.
vals6 = [v for k, v in FAMILY.items() if "K=5" not in k]
S = max(vals6) - min(vals6)
P("  full range incl. the LOO-REJECTED K=5 : S_all = %s" % mp.nstr(S_all, 8))
P("  full range of the ACCEPTED family     : S     = %s" % mp.nstr(S, 8))

# ---------------------------------------------------------------- B: truncation bias
P("\n=== 2. B -- model-truncation bias of the PROPOSED design, from seen data ===")
P("  method: take the corrected 17-rung data, fit a HIGHER-order plain polynomial (K=8) to it,")
P("  use that as a synthetic truth, evaluate it at the six proposed eps, then run the GRADED")
P("  estimator (six rungs alone, basis [eps^-2, 1, eps, eps^2, eps^3]) on the synthetic values.")
P("  Truth has c0 == 0 exactly, so whatever c0 comes back is pure truncation/conditioning bias.")
R17c = [r_of(e, u, A_CORR) for e, u in zip(E17, U17)]
for Ksyn in (6, 7, 8, 9):
    csyn = fit(E17, R17c, polybasis(Ksyn))
    bsyn = polybasis(Ksyn)
    rsyn = [ev(csyn, bsyn, e) for e in ENEW]
    for Kfit in (2, 3):
        basis = inv2() + polybasis(Kfit)
        c = fit(ENEW, rsyn, basis)
        P("    synth K=%d -> graded fit K=%d : c0_bias = %s" % (Ksyn, Kfit, mp.nstr(c[0], 8)))
BIAS = []
for Ksyn in (6, 7, 8, 9):
    csyn = fit(E17, R17c, polybasis(Ksyn))
    bsyn = polybasis(Ksyn)
    rsyn = [ev(csyn, bsyn, e) for e in ENEW]
    for Kfit in (2, 3):
        c = fit(ENEW, rsyn, inv2() + polybasis(Kfit))
        BIAS.append(abs(c[0]))
Bmax = max(BIAS)
P("  B = max |c0_bias| over the 8 synthetic/graded combinations = %s" % mp.nstr(Bmax, 8))

# ---------------------------------------------------------------- the mechanical rule
P("\n=== 3. THE MECHANICAL TOLERANCE RULE (stated before any new rung is solved) ===")
P("  T1 := 3 * max(S, B).   S = the correction's own estimator spread; B = the design's")
P("  truncation bias.  A correction cannot be held to a standard finer than either.")
T1 = 3 * max(S, Bmax)
P("  S = %s ; B = %s ; T1 = %s" % (mp.nstr(S, 8), mp.nstr(Bmax, 8), mp.nstr(T1, 8)))
P("  ALTERNATIVE HYPOTHESIS (a_operative is right, no correction needed) predicts")
P("  c0_new = %s .  Discrimination margin = |delta_a| / T1 = %s"
  % (mp.nstr(-DA, 10), mp.nstr(abs(DA) / T1, 6)))
P("  PRE-STATED ABORT: if the margin is < 10 the test is UNDERPOWERED and is reported as such")
P("  instead of graded.   margin >= 10 ? %s" % ("YES" if abs(DA) / T1 >= 10 else "NO"))

# ---------------------------------------------------------------- frozen prediction curve
P("\n=== 4. THE FROZEN PREDICTION CURVE (17-rung K=6 plain poly on corrected r) ===")
c6 = fit(E17, R17c, polybasis(6))
res17 = max(abs(ev(c6, polybasis(6), e) - r) for e, r in zip(E17, R17c))
P("  in-sample max residual = %s" % mp.nstr(res17, 8))
for i, ci in enumerate(c6):
    P("    c[%d] = %s" % (i, mp.nstr(ci, 24)))
P("  a3 (= c[0]) = %s      [9 s.f. public form stays 11.7007173 -- ERRATUM 11 stands]"
  % mp.nstr(c6[0], 22))
P("\n  per-rung POINT PREDICTIONS at the six proposed eps (r and u), tolerance T2(eps):")
P("  T2(eps) := T1/eps^2 + 3 * in-sample max residual")
P("  %-10s %-26s %-32s %-14s %-14s" % ("eps", "r_pred", "u_pred", "T2(eps)", "alt-H dev"))
for e in ENEW:
    rp = ev(c6, polybasis(6), e)
    up = mp.sqrt(rp * e ** 3 + A_CORR * e - B * e ** 2)
    t2 = T1 / e ** 2 + 3 * res17
    alt = abs(DA) / e ** 2
    P("  %-10s %-26s %-32s %-14s %-14s" % (mp.nstr(e, 6), mp.nstr(rp, 20), mp.nstr(up, 28),
                                           mp.nstr(t2, 6), mp.nstr(alt, 6)))

# ---------------------------------------------------------------- T3 for a3
P("\n=== 5. T3 -- tolerance on a3 from the six new rungs alone (plain poly, corrected a) ===")
P("  same synthetic construction as section 2, but reading a3 out of a PLAIN K=3 poly fit")
A3REF = c6[0]
d3 = []
for Ksyn in (6, 7, 8, 9):
    csyn = fit(E17, R17c, polybasis(Ksyn))
    bsyn = polybasis(Ksyn)
    rsyn = [ev(csyn, bsyn, e) for e in ENEW]
    for Kfit in (2, 3):
        c = fit(ENEW, rsyn, polybasis(Kfit))
        d3.append(abs(c[0] - A3REF))
        P("    synth K=%d -> plain K=%d : a3 = %s  dev = %s"
          % (Ksyn, Kfit, mp.nstr(c[0], 20), mp.nstr(abs(c[0] - A3REF), 6)))
T3 = 3 * max(d3)
P("  T3 := 3 * max dev = %s   (reference a3 = %s)" % (mp.nstr(T3, 8), mp.nstr(A3REF, 22)))
P("  ALT-H: with a_operative the same plain fit is off by ~|delta_a|/eps^2 propagated into a3;")
P("  c30 measured that as a 1.2264073e-6 shift on the 17-rung grid -- margin is >1e3 T3.")

txt = "\n".join(out)
open("c31_calib.out", "w").write(txt + "\n")
print(txt)
