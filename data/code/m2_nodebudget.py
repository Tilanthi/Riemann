"""machine2 cycle22 — node-budget audit: where does our GL-degree-8 u instrument stop converging?
Certificate = stability under refinement (our own standing law), never the reading."""
from mpmath import mp
from m2_u_instrument import Basis, load_genomes
mp.dps = 40
gens = load_genomes("s1/M8")
b = {d: Basis(gens[0], degree=d) for d in (7, 8, 9, 10)}
print(f"nodes: {[ (d,len(b[d].xs)) for d in (7,8,9,10)]}")
half = mp.mpf(1)/2
print(f"{'gamma':>8} {'|u| deg8':>14} {'|d(8,9)|':>12} {'|d(9,10)|':>12}  verdict")
for g in [14, 50, 100, 150, 200, 250, 280, 300, 320, 350, 400]:
    gg = mp.mpf(g)
    v = {d: b[d].u(mp.mpc(half, gg)) for d in (8, 9, 10)}
    d89 = abs(v[8]-v[9]); d910 = abs(v[9]-v[10])
    ok = "converged" if d89 < abs(v[10])*mp.mpf('1e-10') else "NOT CONVERGED"
    print(f"{g:>8} {mp.nstr(abs(v[8]),6):>14} {mp.nstr(d89,4):>12} {mp.nstr(d910,4):>12}  {ok}")
