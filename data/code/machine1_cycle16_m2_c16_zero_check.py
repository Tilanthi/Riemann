"""m2 cycle-16 ask: confirm their best off-line zero of zeta2(s,1/7)
   s0 = 0.7159014103823531 + 47.2977588172104875 i  (28 digits)
on my certified zeta2_A, two argument regimes:
  route A (direct):   F = 49^{-s} * zeta2_A(s, 1/7)   [small-argument K: z = 2 pi mk/7]
  route B (scaling):  F = zeta2_A(s, 7)               [large-argument K: z = 14 pi mk]
plus a 2D zero polish on my evaluator and a dps ladder (my own cancellation receipt).
F(s) := 49^{-s} zeta2(s,1/7) = zeta2(s,7) = (1/2) sum' (j^2+49k^2)^{-s}; a1=1.
"""
import ast, time
from mpmath import (mp, mpf, mpc, sqrt, zeta, gamma, besselk, pi, findroot)

PATH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/heat68_epstein_rect_zeros.py"
src = open(PATH).read()
tree = ast.parse(src)
fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "zeta2_A"][0]
ns = dict(mpf=mpf, mp=mp, zeta=zeta, sqrt=sqrt, pi=pi, gamma=gamma,
          besselk=besselk, TRUNC_REL=mpf("1e-45"))
exec(compile(ast.Module(body=[fn], type_ignores=[]), "<zeta2_A>", "exec"), ns)
_z = ns["zeta2_A"]
def Z(s, D):          # scalar wrapper; programme convention: (1/2) sum' (j^2 + D^2 k^2)^{-s}
    return _z(s, D)[0]

# RECEIPT FIX (m2 cycle-17 §5.2 dispute): the original run parsed S0 at the
# mpmath DEFAULT dps 15 (no mp.dps assignment preceded this line), truncating
# m2's 28-digit value to 15 digits -- every downstream |F| and the printed
# separation 1.61711e-15 were evaluating at the truncated point. Parse at
# dps 60 FIRST; the ladder below then varies dps around a full-precision S0.
mp.dps = 60
S0 = mpc(mpf("0.7159014103823531018264718067"),
         mpf("47.29775881721048753252892984"))
D17 = mpf(1) / 7
D7  = mpf(7)
t0 = time.time()

def FA(s): return s * 0 + (mpf(49) ** (-s)) * Z(s, D17)   # direct
def FB(s): return Z(s, D7)                                  # scaling identity

print("== dps ladder at m2's s0 (stability = my cancellation receipt) ==", flush=True)
for dps in (50, 60, 70, 80):
    mp.dps = dps
    tb = time.time()
    fb = FB(S0)
    ta = time.time()
    fa = FA(S0)
    print(f"dps={dps}: routeB(A=7)     |F| = {mp.nstr(abs(fb), 8)}   [{ta-tb:.0f}s]", flush=True)
    print(f"        routeA(49^-s,1/7) |F| = {mp.nstr(abs(fa), 8)}   [{time.time()-ta:.0f}s]", flush=True)
    print(f"        |A-B|/|B| = {mp.nstr(abs(fa-fb)/abs(fb), 4) if abs(fb) else '0/0'}", flush=True)

mp.dps = 60
print("\n== 2D zero polish on MY evaluator (route B, sweet regime) ==", flush=True)
f2 = lambda sg, tt: (lambda s: (Z(s, D7).real, Z(s, D7).imag))(mpc(sg, tt))
t1 = time.time()
root = findroot(f2, (S0.real, S0.imag), tol=mpf("1e-35"))
fr = mpc(root[0], root[1])
print(f"my s0   = {mp.nstr(fr.real, 30)} + {mp.nstr(fr.imag, 30)} i", flush=True)
print(f"m2 s0   = 0.7159014103823531018264718067 + 47.29775881721048753252892984 i", flush=True)
d = abs(fr - S0)
print(f"|s0_mine - s0_m2| = {mp.nstr(d, 6)}", flush=True)
resB = Z(fr, D7); resA = (mpf(49) ** (-fr)) * Z(fr, D17)
print(f"|F(my root)| routeB = {mp.nstr(abs(resB), 6)}   routeA = {mp.nstr(abs(resA), 6)}", flush=True)
sig, tt = fr.real, abs(fr.imag)
print(f"floor (2s-1)/|s|^2 = {mp.nstr((2*sig-1)/(sig*sig+tt*tt), 8)}   [m2: 1.92977e-4]", flush=True)
print(f"\npolish took {time.time()-t1:.0f}s; total {time.time()-t0:.0f}s", flush=True)
