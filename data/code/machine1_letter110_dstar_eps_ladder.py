"""Settle m3's Letter-110 flagged residual: my Dstar sits at m2 + 3.7799738e-25,
which equals +kappa*eps^2 with kappa = -A_ss/(2 A_D) = 0.378011 (4-5 digit match) --
the signature of a SIGN-FLIPPED eps^2 residue at my eps=1e-12, even though the
archived script's removal is arithmetically correct. And m3 (eps=1e-15) lands at
the SAME place, which no eps^2 story explains. Measure the root's eps-dependence:
if the (removed-map) root is eps-independent, the +3.78e-25 is NOT my eps-artefact.
Corrected constants: A_D = -49.780192509392596, A_ss = -37.633558577250699."""
import ast, time
from mpmath import (mp, mpf, sqrt, zeta, gamma, besselk, pi)

mp.dps = 55
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

A_SS = mpf("-37.633558577250699")    # corrected (epsilon-extrapolated)
A_D  = mpf("-49.780192509392596")
KAPPA = -A_SS / (2 * A_D)
D_M2 = mpf("0.14173323966388719139541530708686641")
D_ME = mpf("0.14173323966388719139541568508424243")

def newton_root(F, x0, iters=4):
    h = mpf("1e-25")
    for _ in range(iters):
        f0 = F(x0)
        sl = (F(x0 + h) - F(x0 - h)) / (2 * h)
        x0 = x0 - f0 / sl
    return x0

t0 = time.time()
print(f"kappa = -A_ss/(2 A_D) = {mp.nstr(KAPPA, 10)}   "
      f"[kappa*(1e-12)^2 = {mp.nstr(KAPPA * mpf('1e-24'), 6)};  me-m2 = {mp.nstr(D_ME - D_M2, 8)}]", flush=True)
for eps_s in ("1e-10", "1e-12", "1e-14"):
    eps = mpf(eps_s)
    F_rem = lambda D: (A(mpf("0.5") + eps, D) + A(mpf("0.5") - eps, D)) / 2 - eps**2 * A_SS / 2
    F_raw = lambda D: (A(mpf("0.5") + eps, D) + A(mpf("0.5") - eps, D)) / 2
    r_rem = newton_root(F_rem, D_ME)
    print(f"eps={eps_s}: root(removed)  - m2 = {mp.nstr(r_rem - D_M2, 8)}   -me = {mp.nstr(r_rem - D_ME, 8)}", flush=True)
    r_raw = newton_root(F_raw, D_ME)
    print(f"          root(raw)     - m2 = {mp.nstr(r_raw - D_M2, 8)}   "
          f"[theory raw: m2 + kappa*eps^2 = {mp.nstr(KAPPA * eps**2, 8)}]", flush=True)
print(f"total {time.time()-t0:.0f}s", flush=True)
