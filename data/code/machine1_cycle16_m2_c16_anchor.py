"""Ancestry-diverse anchor for zeta2_A at m2's zero height t=47.3:
   zeta2(s,1) = 2*zeta(s)*beta(s)  [programme convention: (1/2) sum' (j^2+k^2)^{-s}]
mpmath's zeta/hurwitz (Euler-Maclaurin family) do NOT descend from the theta
transform — so agreement at this height is identity-level ancestry-diverse.
beta(s) = 4^{-s} (zeta(s,1/4) - zeta(s,3/4)).
Also: mini height-ladder of the same anchor (t = 20, 47.3, 98.6)."""
import ast, time
from mpmath import (mp, mpf, mpc, sqrt, zeta, hurwitz, gamma, besselk, pi)

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

def beta(s):
    return mpf(4) ** (-s) * (hurwitz(s, mpf(1) / 4) - hurwitz(s, mpf(3) / 4))

t0 = time.time()
for dps in (50, 60):
    mp.dps = dps
    for ts in ("20", "47.29775881721048753252892984", "98.61599811620170433773193031"):
        s = mpc(mpf("0.7159014103823531"), mpf(ts))
        mine = Z(s, mpf(1))
        ref = 2 * zeta(s) * beta(s)
        rel = abs(mine - ref) / abs(ref)
        print(f"dps={dps} t={ts[:8]}: |zeta2_A - 2*z*beta|/|2*z*beta| = {mp.nstr(rel, 4)}   |ref| = {mp.nstr(abs(ref), 6)}", flush=True)
print(f"total {time.time()-t0:.0f}s", flush=True)
