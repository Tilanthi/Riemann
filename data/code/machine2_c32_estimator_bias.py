"""machine2 CYCLE 32 -- is the published c0 estimator BIASED, and is the bias COMMON MODE?

The c30/c31/heat86b headline statistic is c0, the eps^-2 coefficient in
    r(eps) = (u^2 - a_used*eps + b*eps^2)/eps^3      fitted on {eps^-2, 1, eps, ..., eps^K}
with b FIXED.  Its meaning is  c0 = a_true - a_used.

TEST: run the SAME estimator with a_used := the ladder-free a measured this cycle.  If the
estimator were unbiased it must return c0 = 0.  Whatever it returns instead is the estimator's
own bias, and can be compared with the 1.241e-17 gap between the ladder-free a and the value
both machines' 17-rung fits reported.

TEST 2 (independence): swap m1's six heat86b u for m2's six c30 u on the identical grid and
re-run.  If c0 does not move, the second lineage's agreement is a statement about the EVALUATOR
and carries no information about the ESTIMATOR.
"""
import json

import mpmath as mp

mp.mp.dps = 80

C30 = json.load(open("/workspace/rh/cycle30/m2_c30_scored.json"))["rungs"]
C31B = json.load(open("/workspace/rh/cycle31/m2_c31b_scored.json"))["rungs"]

M1_HEAT72X = [
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
M1_HEAT86B = [
    ("0.0001", "0.016267353116370815436521662356481985337487201480639"),
    ("0.00015", "0.019924762394110635273342326173461402826314494537478"),
    ("0.00022", "0.02413246812812595998486983709533875808144894305693"),
    ("0.00033", "0.029560702761397693562532171129200615891469008031872"),
    ("0.0005", "0.036395436293510592613058142574334602175332274922237"),
    ("0.00075", "0.044590846945589617275344158652007762656432566989551"),
]

B = -mp.mpf("7.4624528767937415788")
A_120 = mp.mpf("2.645521411811664489")
A_DERIV = mp.mpf("2.6455214118116628680161261212034")


def r_of(eps, u, a):
    return (u ** 2 - a * eps + B * eps ** 2) / eps ** 3


def fit_c0(rows, a_used, K):
    """LS of r on {eps^-2, 1, eps, ..., eps^K}; return (c0, maxres)."""
    n = len(rows)
    A = mp.matrix(n, K + 2)
    y = mp.matrix(n, 1)
    for i, (e, u) in enumerate(rows):
        A[i, 0] = e ** (-2)
        for j in range(K + 1):
            A[i, j + 1] = e ** j
        y[i] = r_of(e, u, a_used)
    coef = mp.lu_solve(A.T * A, A.T * y)
    res = max(abs((A * coef - y)[i]) for i in range(n))
    return coef[0], res


m1x = sorted((mp.mpf(e), mp.mpf(u)) for e, u in M1_HEAT72X)
m2c30 = sorted((mp.mpf(e), mp.mpf(d["u"])) for e, d in C30.items())
m2c31 = sorted((mp.mpf(e), mp.mpf(d["u"])) for e, d in C31B.items())
m186 = sorted((mp.mpf(e), mp.mpf(u)) for e, u in M1_HEAT86B)

SETS = [
    ("17-rung  m1's 11 + m2's 6   (m2 c30 published fit)", sorted(m1x + m2c30)),
    ("17-rung  m1's 11 + m1's 6   (m1 heat86b V1 fit)   ", sorted(m1x + m186)),
    ("6-alone  m2's c30 six                             ", m2c30),
    ("6-alone  m1's heat86b six                         ", m186),
    ("6-alone  m2's c31b six (OUT OF SAMPLE, finer)     ", m2c31),
    ("12 fine  m2 c30 + m2 c31b                         ", sorted(m2c30 + m2c31)),
    ("12 fine  m1 heat86b + m2 c31b                     ", sorted(m186 + m2c31)),
]

print("=== REPLICATION: c0 with a_used = the #120 value (should reproduce the published c0) ===")
for name, rows in SETS:
    K = 6 if len(rows) > 8 else 3
    c0, res = fit_c0(rows, A_120, K)
    print(f"  {name} K={K}  c0 = {mp.nstr(c0, 12):>18s}   maxres = {mp.nstr(res, 4)}")

print()
print("=== BIAS: c0 with a_used = the LADDER-FREE a  (an unbiased estimator must return 0) ===")
for name, rows in SETS:
    K = 6 if len(rows) > 8 else 3
    c0, res = fit_c0(rows, A_DERIV, K)
    print(f"  {name} K={K}  c0 = {mp.nstr(c0, 12):>18s}   maxres = {mp.nstr(res, 4)}")

print()
print("=== TEST 2: does swapping the LINEAGE of the six fine rungs move c0 at all? ===")
for K in (5, 6, 7):
    c0a, _ = fit_c0(sorted(m1x + m2c30), A_120, K)
    c0b, _ = fit_c0(sorted(m1x + m186), A_120, K)
    print(f"  K={K}: m2's six -> {mp.nstr(c0a, 15)}")
    print(f"       m1's six -> {mp.nstr(c0b, 15)}")
    print(f"       |difference| = {mp.nstr(abs(c0a - c0b), 6)}   "
          f"rel = {mp.nstr(abs(c0a - c0b) / abs(c0a), 6)}")

print()
print("=== K-sensitivity of the published 17-rung estimator (a_used = #120) ===")
for K in range(4, 12):
    c0, res = fit_c0(sorted(m1x + m2c30), A_120, K)
    implied = A_120 + c0
    print(f"  K={K:2d}  c0 = {mp.nstr(c0, 12):>18s}  implied a = {mp.nstr(implied, 22)}  "
          f"err vs ladder-free = {mp.nstr(implied - A_DERIV, 6)}")
