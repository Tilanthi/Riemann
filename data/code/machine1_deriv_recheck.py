"""Re-derive A_D and A_ss at the fold with step ladders + eps-sensitivity,
to locate the ~1e-7 relative artefact in my published a = 2 A_D/A_ss
(published: A_D = -49.78019502929013, A_ss = -37.63356429233802,
from /tmp/k_analytic2.py: hD=1e-25 FD at s=1/2+1e-8; h2=1e-17 2nd diff)."""
import ast, time
from mpmath import (mp, mpf, sqrt, zeta, gamma, besselk, pi)

mp.dps = 60

PATH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat68_epstein_rect_zeros.py"
src = open(PATH).read()
tree = ast.parse(src)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "zeta2_A"][0]
ns = dict(mpf=mpf, mp=mp, zeta=zeta, sqrt=sqrt, pi=pi, gamma=gamma,
          besselk=besselk, TRUNC_REL=mpf("1e-45"))
exec(compile(ast.Module(body=[fn], type_ignores=[]), "<zeta2_A>", "exec"), ns)
_z = ns["zeta2_A"]
def A(s, D):
    return _z(s, D)[0]

DSTAR = mpf("0.14173323966388719139541568508424243")  # my exact root
t0 = time.time()

print("== A_D (central FD in D at s=1/2+eps) ==")
for eps_s in ("1e-8", "1e-10", "1e-6"):
    s0 = mpf("0.5") + mpf(eps_s)
    f0 = A(s0, DSTAR)
    for hD in ("1e-20", "1e-18", "1e-16"):
        h = mpf(hD)
        AD = (A(s0, DSTAR + h) - A(s0, DSTAR - h)) / (2 * h)
        print(f"  eps={eps_s:>6} hD={hD:>7}: A_D = {mp.nstr(AD, 18)}")
print(f"  published A_D = -49.78019502929013")

print("== A_ss (2nd diff in s centered at 1/2+eps) ==")
for eps_s in ("1e-8", "1e-10"):
    s0 = mpf("0.5") + mpf(eps_s)
    f0 = A(s0, DSTAR)
    for h2 in ("1e-16", "1e-15", "1e-14", "1e-13"):
        h = mpf(h2)
        Ass = (A(s0 + h, DSTAR) - 2 * f0 + A(s0 - h, DSTAR)) / h ** 2
        print(f"  eps={eps_s:>6} h2={h2:>7}: A_ss = {mp.nstr(Ass, 18)}")
print(f"  published A_ss = -37.63356429233802")

# best-estimate a from the ladder's mid steps
s0 = mpf("0.5") + mpf("1e-8"); h = mpf("1e-18")
AD = (A(s0, DSTAR + h) - A(s0, DSTAR - h)) / (2 * h)
h = mpf("1e-15")
Ass = (A(s0 + h, DSTAR) - 2 * A(s0, DSTAR) + A(s0 - h, DSTAR)) / h ** 2
a = 2 * AD / Ass
print(f"\nbest-estimate a = 2 A_D/A_ss = {mp.nstr(a, 16)}  k = {mp.nstr(2*sqrt(a), 14)}")
print(f"a_m2 = 2.645521411811663   a_mine_published = 2.6455211439765270943")
print(f"total {time.time()-t0:.0f}s")
