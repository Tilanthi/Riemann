"""CORRECTION to m2_c16_zero_check.py: S0 there was parsed at default dps 15
(truncating the 28/26-digit literals), so |ds|=1.617e-15 measured the SEED
truncation, not the cross-evaluator offset. Here: parse at full precision
FIRST, then evaluate. Reports (i) true position offset vs m2's printed
values, (ii) route-B residual at their point, (iii) route-A floor at their
point (the only genuinely open instrument question)."""
import ast, time
from mpmath import (mp, mpf, mpc, sqrt, zeta, gamma, besselk, pi)

mp.dps = 70                      # set BEFORE parsing, unlike script 1
PATH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat68_epstein_rect_zeros.py"
src = open(PATH).read()
tree = ast.parse(src)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "zeta2_A"][0]
ns = dict(mpf=mpf, mp=mp, zeta=zeta, sqrt=sqrt, pi=pi, gamma=gamma,
          besselk=besselk, TRUNC_REL=mpf("1e-45"))
exec(compile(ast.Module(body=[fn], type_ignores=[]), "<zeta2_A>", "exec"), ns)
_z = ns["zeta2_A"]
def Z(s, D):
    return _z(s, D)[0]

S0_M2 = mpc(mpf("0.7159014103823531018264718067"),
            mpf("47.29775881721048753252892984"))
FR    = mpc(mpf("0.715901410382353101826471806686"),
            mpf("47.2977588172104875325289298419"))   # my 30-digit polish (extends theirs)
D17, D7 = mpf(1) / 7, mpf(7)
t0 = time.time()
print(f"|my_polish - m2_printed| = {mp.nstr(abs(FR - S0_M2), 6)}  "
      f"[their printed precision: 28 digits sigma, 26 digits t]", flush=True)
for dps in (50, 60, 70):
    mp.dps = dps
    fb = Z(S0_M2, D7)
    fa = (mpf(49) ** (-S0_M2)) * Z(S0_M2, D17)
    print(f"dps={dps}: routeB |F(s0_m2)| = {mp.nstr(abs(fb), 8)}   "
          f"routeA |F(s0_m2)| = {mp.nstr(abs(fa), 8)}   "
          f"|A-B| = {mp.nstr(abs(fa - fb), 6)}", flush=True)
# slope |F'| at the zero along sigma, for floor->offset conversion
mp.dps = 60
h = mpf("1e-20")
fp = abs((Z(S0_M2 + h, D7) - Z(S0_M2 - h, D7)) / (2 * h))
print(f"|F'(s0)| ~ {mp.nstr(fp, 6)}", flush=True)
print(f"total {time.time()-t0:.0f}s", flush=True)
