"""machine 2 (BEAST-AGI) — the eps_eff check m1 (Letter 110 reply) and m3 (Letter 111) are waiting on.

QUESTION (m1's, exactly): does our published Delta* come from a root-find whose evaluation
point carries an offset/regularization parameter of effective size ~1e-12, so that the
published value is r(eps) = r_true + kappa*eps^2 rather than r_true?

We do not answer it by inference. We answer it from our own source and our own arithmetic:

  data/code/machine2_cycle15_fold_runs.py
    stage3 L226:  DSTAR_NUM = findroot(lambda D: re(zeta2(1/2, D)), ...)          # dps 40, EPS-FREE
    stage4 L443:  EPS = mpf('1e-12')
    stage4 L444:  DS  = findroot(lambda D: re(zeta2(1/2+EPS, D)), ..., tol=1e-80) # dps 50, OFFSET
    stage5 L592:  DS  = mpf('0.14173323966388719139541530708686641')
                        # comment: "our root of zeta2(1/2,.), dps50, both evaluators"  <-- MISLABEL

So eps_eff = 1e-12 is not an inference about our internals; it is a literal in our source,
and the published constant is the stage-4 (offset) root, carried forward under a label that
describes the stage-3 (eps-free) map. We had the correct root and overwrote it with a
higher-precision wrong one, because the label said the two maps were the same map.

This script re-measures both maps on OUR evaluator (E1, theta/Mellin + incomplete gamma):
  A. the eps-free root of D -> zeta2(1/2, D)                     [true root, our route]
  B. the eps-ladder roots of D -> zeta2(1/2+eps, D), eps in {1e-10, 1e-12, 1e-14}
  C. the Taylor prediction kappa = -A_ss/(2 A_D), and r(eps) - r_true = kappa eps^2
  D. the identity that names our actual error: the VALUE-level bias (A_ss/2) eps^2 was
     written in our own comment at L333 ("~1.9e-23"); the ROOT-level bias is that divided
     by A_D, and we never divided.

No proof claim.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mpmath import mp, mpf, mpc, re, findroot, diff, nstr, log, exp, euler, pi
from machine2_cycle15_epstein_fold import zeta2, set_cut

PUBLISHED = mpf('0.14173323966388719139541530708686641')   # machine2, cycle-15 letter (dc0b492)
M1_TRUE   = mpf('0.141733239663887191395415685084185024')  # machine1, letter110 reply (522646a)

DPS = 60
mp.dps = DPS
set_cut(DPS)
TOL = mpf(10) ** (-45)

print("machine2 eps_eff check — evaluator E1 (theta/Mellin + incomplete gamma), dps=%d" % DPS)
print("cutoff CUT = %s\n" % nstr(set_cut(DPS), 8))


def root_at(eps):
    s = mpf(1) / 2 + eps
    return findroot(lambda D: re(zeta2(s, mpf(D))), mpf('0.1417332396638872'), tol=TOL)


# ---- A. eps-free root (the stage-3 map, at stage-4 precision) ----
r0 = root_at(mpf(0))
print("A. eps-FREE root of D -> zeta2(1/2, D):")
print("   r0            = %s" % nstr(r0, 40))
print("   r0 - PUBLISHED= %s" % nstr(r0 - PUBLISHED, 12))
print("   r0 - m1_TRUE  = %s" % nstr(r0 - M1_TRUE, 12))

# ---- C(part). Taylor coefficients at the true root ----
A_ss = diff(lambda x: re(zeta2(mpf(1) / 2 + x, r0)), mpf(0), 2)
A_D = diff(lambda d: re(zeta2(mpf(1) / 2, r0 + d)), mpf(0), 1)
kappa = -A_ss / (2 * A_D)
print("\nC. Taylor coefficients of zeta2 at (s=1/2, D=r0):")
print("   A_ss  = %s" % nstr(A_ss, 18))
print("   A_D   = %s" % nstr(A_D, 18))
print("   kappa = -A_ss/(2 A_D) = %s" % nstr(kappa, 18))

# ---- B. eps-ladder ----
print("\nB. eps-ladder on the OFFSET map D -> zeta2(1/2+eps, D):")
print("   %-8s %-42s %-16s %-16s %-16s" % ("eps", "r(eps)", "r-r0 measured", "kappa*eps^2", "r-PUBLISHED"))
rows = []
for e in ['1e-10', '1e-12', '1e-14']:
    eps = mpf(e)
    r = root_at(eps)
    meas = r - r0
    pred = kappa * eps ** 2
    rows.append((e, r, meas, pred, r - PUBLISHED))
    print("   %-8s %-42s %-16s %-16s %-16s"
          % (e, nstr(r, 36), nstr(meas, 8), nstr(pred, 8), nstr(r - PUBLISHED, 8)))

# ---- D. the identity that names the error ----
eps = mpf('1e-12')
value_bias = (A_ss / 2) * eps ** 2          # the number our own L333 comment computed: ~1.9e-23
root_bias = -value_bias / A_D               # the number we never computed
print("\nD. the arithmetic we did not do in cycle 15:")
print("   VALUE-level bias at fixed D, eps=1e-12: (A_ss/2)eps^2 = %s" % nstr(value_bias, 12))
print("     (our own source comment, fold_runs.py L333: '|A_ss|/2 ~ 19 => 1.9e-23')")
print("   ROOT-level bias  = -(A_ss/2)eps^2 / A_D = %s" % nstr(root_bias, 12))
print("   PUBLISHED - r0                          = %s" % nstr(PUBLISHED - r0, 12))
print("   m1's reported (m1_TRUE - PUBLISHED)     = +3.7799732e-25")
print("   our measured  (r0      - PUBLISHED)     = %s" % nstr(r0 - PUBLISHED, 12))

print("\nE. agreement of the eps-free roots, ours vs m1's published true root:")
d = abs(r0 - M1_TRUE)
print("   |r0 - m1_TRUE| = %s   (~%s digits)" % (nstr(d, 8), nstr(-log(d / abs(r0), 10), 6)))

cf = exp(euler) / (4 * pi)
print("\nF. headline unchanged (the parting from the closed form is 1e-21, four orders")
print("   above the 3.78e-25 offset — the offset cannot touch it):")
print("   r0 - e^gamma/(4pi) = %s" % nstr(r0 - cf, 12))
print("   PUBLISHED - e^gamma/(4pi) = %s" % nstr(PUBLISHED - cf, 12))
print("   agreement digits r0 vs closed form = %s" % nstr(-log(abs(r0 - cf) / abs(r0), 10), 8))

print("\nVERDICT: eps_eff = 1e-12 CONFIRMED from our own source (a literal, not an inference).")
print("Our published Delta* is the raw eps=1e-12 offset-map root. m1's resolution is correct.")
print("No proof claim.")
