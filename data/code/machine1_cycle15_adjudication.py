"""Adjudicate m2 cycle-15 §7.1-§7.3 against my independent zeta2_A evaluator.

Checks:
  (1) A(1/2, e^g/(4pi))  -- m2 says 2.9601861097249e-19 != 0 (their falsifier:
      an independent implementation returning 0 to better than 1e-25 kills it)
  (2) A(1/2, m2's exact root) -- expect ~0
  (3) my own root-find of D -> A(1/2,D)  -> digit-for-digit Delta* comparison
  (4) line-side zeros: A(1/2+i y, D) = 0 root-find over a Delta ladder,
      fit y^2 = a*x + c*x^2 (x = Delta - Delta*), compare
      a vs mine (2*A_D/A_ss from my published constants) and vs m2's
      2.645521411811663;  b = -c vs m2's -7.46245287679
  (5) spot-check y(1/7), y(0.15) vs m2's measured values
"""
import ast, math, time
from mpmath import (mp, mpf, sqrt, log, exp, findroot, zeta, gamma,
                    besselk, pi)

mp.dps = 55

PATH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat68_epstein_rect_zeros.py"
src = open(PATH).read()
tree = ast.parse(src)
fns = {}
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and n.name == "zeta2_A":
        mod = ast.Module(body=[n], type_ignores=[])
        ns = dict(mpf=mpf, mp=mp, zeta=zeta, sqrt=sqrt, pi=pi, gamma=gamma,
                  besselk=besselk, TRUNC_REL=mpf("1e-45"))
        exec(compile(mod, "<zeta2_A>", "exec"), ns)
        fns["zeta2_A"] = ns["zeta2_A"]
assert fns, "zeta2_A not found"
_A_raw = fns["zeta2_A"]
def A(s, D):
    """scalar wrapper: zeta2_A returns (value, n_bessel_terms)."""
    v, n = _A_raw(s, D)
    return v

GAMMA = mp.euler
DSTAR_C5 = exp(GAMMA) / (4 * mp.pi)
DSTAR_M2 = mpf("0.14173323966388719139541530708686641")

# my published fold constants (from L103 receipt)
A_D_MINE   = mpf("-49.78019502929013")
A_SS_MINE  = mpf("-37.63356429233802")
A_MINE     = 2 * A_D_MINE / A_SS_MINE
K_MINE     = 2 * sqrt(A_MINE)
print(f"my published constants -> a_mine = {mp.nstr(A_MINE, 20)}  k_mine = {mp.nstr(K_MINE, 17)}")
print(f"m2 claims: a = 2.645521411811663  k = 3.25301178098799  b = -7.46245287679")

EPS = mpf("1e-12")
ASS_HALF = A_SS_MINE / 2  # correction term eps^2 * A_ss/2 (odd terms cancel)

def F(D):
    """limit A(1/2, D) via symmetric eps-average, eps^2-corrected."""
    hi = A(mpf("0.5") + EPS, D)
    lo = A(mpf("0.5") - EPS, D)
    return (hi + lo) / 2 - EPS ** 2 * ASS_HALF

t0 = time.time()
v_c5 = F(DSTAR_C5)
print(f"\n(1) A(1/2, e^g/(4pi))  = {mp.nstr(v_c5, 25)}")
print(f"    m2 value           = 2.9601861097249e-19")
v_m2 = F(DSTAR_M2)
print(f"(2) A(1/2, m2 Dstar)   = {mp.nstr(v_m2, 25)}")

# (3) my own root-find: Newton in D using local slope ~ A_D
D = DSTAR_M2
for it in range(3):
    f0 = F(D)
    h = mpf("1e-25")
    fp = (F(D + h) - F(D - h)) / (2 * h)
    step = f0 / fp
    D = D - step
    print(f"    newton it{it}: A={mp.nstr(f0,8)} step={mp.nstr(step,8)}")
DSTAR_ME = D
print(f"(3) my Dstar  = {mp.nstr(DSTAR_ME, 35)}")
print(f"    m2 Dstar  = {mp.nstr(DSTAR_M2, 35)}")
print(f"    e^g/4pi   = {mp.nstr(DSTAR_C5, 35)}")
print(f"    me-m2     = {mp.nstr(DSTAR_ME - DSTAR_M2, 8)}")
print(f"    me-C5     = {mp.nstr(DSTAR_ME - DSTAR_C5, 8)}")
print(f"    C5-m2     = {mp.nstr(DSTAR_C5 - DSTAR_M2, 8)}   [m2 printed 5.946514e-21]")

# (4) line-side zeros and the (a,b) fit
X_TARGETS = [mpf("1.1239032e-3"), mpf("3.2667603e-3"), mpf("8.2667603e-3"),
             mpf("2e-4"), mpf("5e-5"), mpf("1.2e-5"), mpf("3e-6"), mpf("8e-7"),
             mpf("2.5e-7")]
a_guess = mpf("2.64552141")
pts = []
for x in X_TARGETS:
    D = DSTAR_ME + x
    y0 = sqrt(a_guess * x)
    def g(y, D=D):
        return A(mpf("0.5") + 1j * y, D)
    try:
        y = findroot(g, y0 * (1 + 1j * mpf("1e-8")))
    except Exception:
        y = findroot(lambda yy: abs(g(yy)), y0)
    yr = abs(y)
    pts.append((x, yr))
    print(f"    D={mp.nstr(D,10)}  x={mp.nstr(x,6)}  y={mp.nstr(yr, 18)}  |Im|={mp.nstr(abs(abs(y)-yr),3)}")

# linear least squares y^2 = a*x + c*x^2  (through-origin two-parameter)
def fit2(sel):
    M11 = sum(x * x for x, y in sel);  M12 = sum(x ** 3 for x, y in sel)
    M22 = sum(x ** 4 for x, y in sel)
    rhs1 = sum(x * y * y for x, y in sel); rhs2 = sum(x ** 2 * y * y for x, y in sel)
    det = M11 * M22 - M12 * M12
    return (rhs1 * M22 - rhs2 * M12) / det, (M11 * rhs2 - M12 * rhs1) / det

def fit3(sel):
    # y^2 = a*x + c*x^2 + d*x^3 via normal equations (mp.lu_solve)
    from mpmath import matrix, lu_solve
    Am = matrix(3, 3)
    b_ = matrix(3, 1)
    for i, pi in enumerate((1, 2, 3)):
        for j, pj in enumerate((1, 2, 3)):
            Am[i, j] = sum(x ** (pi + pj) for x, y in sel)
        b_[i] = sum(x ** pi * y * y for x, y in sel)
    v = lu_solve(Am, b_)
    return v[0], v[1], v[2]

small = [p for p in pts if p[0] <= mpf("2e-4")]
a_full, c_full = fit2(pts)
a_sml, c_sml = fit2(small)
a3, c3, d3 = fit3(pts)
for tag, (af, cf) in (("full", (a_full, c_full)), ("small-x", (a_sml, c_sml))):
    print(f"\n(4) 2-param fit [{tag}, {len(small) if tag=='small-x' else len(pts)} zeros]:")
    print(f"    a_fit = {mp.nstr(af, 18)}   k_fit = {mp.nstr(2*sqrt(af), 16)}")
    print(f"    b_fit = {mp.nstr(-cf, 18)}   [m2: -7.46245287679]")
print(f"(4) 3-param fit [full]: a = {mp.nstr(a3, 18)}  b = {mp.nstr(-c3, 18)}  d = {mp.nstr(d3, 8)}")
print(f"    a_mine(from published A_D,A_ss) = {mp.nstr(A_MINE, 18)}")
print(f"    a_m2 = 2.645521411811663")

# (5) spot values
for x, label in ((mpf(1) / 7 - DSTAR_ME, "1/7"), (mpf("0.15") - DSTAR_ME, "0.15")):
    y0 = sqrt(a_full * x)
    try:
        y = findroot(lambda yy: A(mpf("0.5") + 1j * yy, DSTAR_ME + x), y0 * (1 + 1j * mpf("1e-8")))
    except Exception:
        y = findroot(lambda yy: abs(A(mpf("0.5") + 1j * yy, DSTAR_ME + x)), y0)
    print(f"(5) y({label}) = {mp.nstr(abs(y), 18)}")
print("    m2 measured: y(1/7) = 0.054614584740162  y(0.15) = 0.149621445957927")
print(f"\ntotal {time.time()-t0:.0f}s")
