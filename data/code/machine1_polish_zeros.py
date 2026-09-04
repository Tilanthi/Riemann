"""Polish the three smallest-x line-side zeros to tol 1e-40 and re-adjudicate a.
Roots are shallow at small x (|A_y| ~ A_ss*y ~ 0.03), where default findroot
tolerance leaves y wobbly at ~3e-7 rel -- that wobble, not the evaluator,
is why the 9-zero fit could not discriminate a at the 2.7e-7 level.
Large-y roots already match m2's census to every printed digit (15)."""
import ast, time
from mpmath import (mp, mpf, sqrt, findroot, zeta, gamma, besselk, pi)

mp.dps = 50

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

DSTAR_ME = mpf("0.14173323966388719139541568508424243")
B_M2 = mpf("-7.46245287679")          # m2's b, 9 digits
A_MINE = mpf("2.6455211439765270943")  # from my published A_D, A_ss
A_M2   = mpf("2.645521411811663")

# y values returned by the first pass (seeds):
prev = {("2.5e-7"): mpf("0.000813253231998744251"),
        ("8e-7"):   mpf("0.00145479273624292001"),
        ("3e-6"):   mpf("0.00281720276122021447"),
        ("1.2e-5"): mpf("0.00563447704362822627"),
        ("5e-5"):   mpf("0.0115019445393156357"),
        ("2e-4"):   mpf("0.0230087564660915475")}

t0 = time.time()
pts = []
for xs in ["2.5e-7", "8e-7", "3e-6", "1.2e-5", "5e-5", "2e-4"]:
    x = mpf(xs)
    D = DSTAR_ME + x
    y0 = prev[xs]
    g = lambda y: A(mpf("0.5") + 1j * y, D)
    y = findroot(g, (y0 * mpf("0.999"), y0 * mpf("1.001")), tol=mpf("1e-40"))
    yr = abs(y)
    res = abs(g(yr))
    a_pt = yr * yr / x + B_M2 * x
    pts.append((x, yr))
    print(f"x={xs:>7}  y={mp.nstr(yr, 22)}  |A(y)|={mp.nstr(res, 3)}  "
          f"a_pt={mp.nstr(a_pt, 14)}")
print(f"\na_m2   = {mp.nstr(A_M2, 14)}")
print(f"a_mine = {mp.nstr(A_MINE, 14)}")

# 2-param refit on polished zeros, all 6 and smallest 3
def fit2(sel):
    M11 = sum(x * x for x, y in sel);  M12 = sum(x ** 3 for x, y in sel)
    M22 = sum(x ** 4 for x, y in sel)
    r1 = sum(x * y * y for x, y in sel); r2 = sum(x ** 2 * y * y for x, y in sel)
    det = M11 * M22 - M12 * M12
    return (r1 * M22 - r2 * M12) / det, (M11 * r2 - M12 * r1) / det

for tag, sel in (("all6", pts), ("smallest3", pts[:3])):
    af, cf = fit2(sel)
    print(f"fit[{tag}]: a = {mp.nstr(af, 14)}  k = {mp.nstr(2*sqrt(af), 12)}  "
          f"b = {mp.nstr(-cf, 12)}")
    print(f"   |a-a_m2|   = {mp.nstr(abs(af-A_M2), 3)}")
    print(f"   |a-a_mine| = {mp.nstr(abs(af-A_MINE), 3)}")
print(f"\ntotal {time.time()-t0:.0f}s")
