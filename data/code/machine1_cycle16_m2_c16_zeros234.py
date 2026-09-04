"""(a) Polish two more of m2's seven zeros on route B (Z(s,7)) — position offsets.
(b) Spot-verify their Gate-1: M(sigma) = sum_{n>=2} a_n n^{-sigma} == 1 at
    sigma = 1.1842563361, with MY OWN a_n enumeration (lattice sieve to n<=4e6,
    including the (0,+-k) points n = 49k^2) + Abel tail using
    A(x) <= pi*x/14 + 2.058148*sqrt(x)  [their P0/2 = 2.058148]."""
import ast, time, math
from mpmath import (mp, mpf, mpc, sqrt, zeta, gamma, besselk, pi, findroot)

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

mp.dps = 60
D7 = mpf(7)
ZEROS = [
    ("0.5246770865109702460561581364", "44.41100379785915585775068919"),
    ("0.6046656812518528366431236261", "84.46688428178119162005426882"),
]
t0 = time.time()
print("== zero polish, route B ==", flush=True)
for sg, tt in ZEROS:
    s0 = mpc(mpf(sg), mpf(tt))
    f2 = lambda a, b: (lambda s: (Z(s, D7).real, Z(s, D7).imag))(mpc(a, b))
    r = findroot(f2, (s0.real, s0.imag), tol=mpf("1e-35"))
    fr = mpc(r[0], r[1])
    sig, t = fr.real, abs(fr.imag)
    print(f"m2:  {sg[:26]} + {tt[:26]} i", flush=True)
    print(f"mine: {mp.nstr(fr.real, 26)} + {mp.nstr(t, 26)} i", flush=True)
    print(f"  |ds| = {mp.nstr(abs(fr - s0), 5)}  |F| = {mp.nstr(abs(Z(fr, D7)), 4)}  "
          f"floor = {mp.nstr((2*sig-1)/(sig*sig+t*t), 6)}", flush=True)

print("\n== Gate-1 spot check: M(sigma) with my own a_n ==", flush=True)
N = 4_000_000
cnt = [0] * (N + 1)
k = 0
while 49 * k * k <= N:
    if k >= 1:
        n = 49 * k * k
        if n <= N:
            cnt[n] += 2                    # (0, +-k)
    jmax = int(math.isqrt(N - 49 * k * k))
    for j in range(1, jmax + 1):
        n = j * j + 49 * k * k
        cnt[n] += 2 if k == 0 else 4       # (+-j,0) or (+-j,+-k)
    k += 1
assert cnt[1] == 2 and cnt[49] == 2 and cnt[50] == 4, (cnt[1], cnt[49], cnt[50])
# a_1 = 1 (their F def), a_49: (0,+-7) -> 2 -> half = 1; a_50: (+-1,+-7)... 1+49=50 -> 4 -> half = 2

for sg_s in ("1.1842563361", "1.15", "1.2"):
    sg = mpf(sg_s)
    partial = math.fsum((cnt[n] // 2) * n ** (-float(sg)) for n in range(2, N + 1) if cnt[n])
    C0, C1 = mpf(1) / 14 * pi, mpf("2.058148")
    Am = lambda x: C0 * x + C1 * sqrt(x)
    tail = sg * mp.quad(lambda x: Am(x) * x ** (-sg - 1), [N, mp.inf]) - Am(N) * mpf(N) ** (-sg)
    M = mpf(partial) + tail
    print(f"sigma={sg_s}: partial = {mp.nstr(mpf(partial), 10)}  tail = {mp.nstr(tail, 6)}  "
          f"M = {mp.nstr(M, 10)}", flush=True)
print(f"total {time.time()-t0:.0f}s", flush=True)
