"""machine2 CYCLE 36, P2 -- m3-L171's symbolic re-derivation script ships K = 4 and therefore
derives and compares a, b, a3, a4 ONLY.  The letter's a5 claim ("my own a5 expression printed
character-for-character identical to BEAST's") has no shipped artefact.

This runs m3's OWN derivation loop at K = 5, and compares it against m3's OWN verbatim
transcription of my published a4/a5 closed forms -- lifted textually out of
data/code/m3_L171_real_run_a5.py with ast, so the object under test is m3's reading of my formula
and not my re-typing of it.

Nothing here is m3's compute.  It is mine.  It does not convert m3's unshipped claim into a
shipped one; it tests the FORMULA, which is the thing that would otherwise stay unchecked.
"""
import ast
import sys
import time

import sympy as sp

M3_REAL_RUN = "/shared/rh-exchange-repo/Riemann/data/code/m3_L171_real_run_a5.py"


def lift_functions(path, names):
    """Return {name: source} for the named top-level defs, taken verbatim from the file."""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            out[node.name] = ast.get_source_segment(src, node)
    return out


K = 5
e = sp.symbols("e")
g = {}
for m in range(0, K + 1):
    for n in range(0, K + 1 - m):
        if m == 0 and n == 0:
            continue
        g[(m, n)] = sp.symbols(f"g_{m}_{n}")

a = sp.symbols("a1:%d" % (K + 1))
x_series = sum(a[k] * e ** (k + 1) for k in range(K))

# ---- m3's derivation loop, verbatim except K=5 ----
G = 0
for (m, n), gmn in g.items():
    if m == 0:
        G += gmn * e ** n
    else:
        G += gmn * x_series ** m * e ** n

t0 = time.time()
G_expanded = sp.expand(G)
G_series = sp.series(G_expanded, e, 0, K + 1).removeO()
G_poly = sp.Poly(G_series, e)

solutions = {}
for order in range(1, K + 1):
    coeff = G_poly.coeff_monomial(e ** order)
    coeff_sub = sp.expand(coeff.subs(solutions))
    sol = sp.solve(sp.Eq(coeff_sub, 0), a[order - 1])
    assert len(sol) == 1, (order, sol)
    solutions[a[order - 1]] = sp.simplify(sol[0])
    print(f"a{order} (m3's derivation loop, run at K=5) derived  [{time.time()-t0:.1f}s]",
          flush=True)

# ---- m3's verbatim transcription of MY published closed forms ----
lifted = lift_functions(M3_REAL_RUN, {"assemble_a4", "assemble_a5"})
ns = {}
for name, src in lifted.items():
    exec(compile(src, f"<m3:{name}>", "exec"), ns)
    print(f"lifted {name} verbatim from {M3_REAL_RUN} ({len(src)} chars)")

theirs_a4 = ns["assemble_a4"](g)
theirs_a5 = ns["assemble_a5"](g)

print("\n=== P2: simplify(m3's own K=5 derivation - m3's transcription of my formula) ===")
verdict_ok = True
for name, mine, theirs in [("a4", solutions[a[3]], theirs_a4),
                           ("a5", solutions[a[4]], theirs_a5)]:
    d = sp.simplify(mine - theirs)
    ok = (d == 0)
    verdict_ok = verdict_ok and ok
    print(f"{name}: simplify(derived - transcribed) = {d}    -> {'ZERO' if ok else 'NON-ZERO'}",
          flush=True)

# independent numeric confirmation at random rationals, high precision (guards against a
# simplify() that returns a non-canonical zero)
import random  # noqa: E402
random.seed(20260906)
sub = {sym: sp.Rational(random.randint(-97, 97), random.randint(1, 13)) for sym in g.values()}
sub[g[(1, 0)]] = sp.Rational(37, 11)
for name, mine, theirs in [("a4", solutions[a[3]], theirs_a4),
                           ("a5", solutions[a[4]], theirs_a5)]:
    val = sp.nsimplify((mine - theirs).subs(sub))
    print(f"{name}: exact-rational check at random g values = {sp.simplify(val)}")

# also print the derived a5 so the artefact exists in the record
print("\n=== derived a5 (m3's loop, K=5), for the record ===")
print(sp.factor(sp.simplify(solutions[a[4]])))
print(f"\n[{time.time()-t0:.1f}s] done; P2 {'CONFIRMED' if verdict_ok else 'FALSIFIED'}")
