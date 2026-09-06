"""
m3-L171 part A -- independently RE-DERIVE the a,b,a3,a4 closed forms from the implicit-function
definition (x(e) is the branch with x(0)=0 solving G(x,e)=Sum g[m][n] x^m e^n = 0), via a standard
power-series substitution + sequential solve in sympy -- NOT by trusting BEAST's transcribed formula.
Then compare the two symbolically (should be identically 0 after full simplification, or numerically
0 to high precision under random substitution).
"""
import sympy as sp

K = 4  # solve for a1..a4 (== a, b, a3, a4)

e = sp.symbols('e')
g = {}
for m in range(0, K + 1):
    for n in range(0, K + 1 - m):
        if m == 0 and n == 0:
            continue
        g[(m, n)] = sp.symbols(f'g_{m}_{n}')

a = sp.symbols('a1:%d' % (K + 1))  # a[0]=a1=a, a[1]=a2=b, a[2]=a3, a[3]=a4

x_series = sum(a[k] * e ** (k + 1) for k in range(K))

# Build G(x_series, e) truncated to O(e^(K+1)), using only support m+n<=K (g[0][0] excluded/assumed 0)
G = 0
for (m, n), gmn in g.items():
    if m == 0:
        G += gmn * e ** n
    else:
        G += gmn * x_series ** m * e ** n

G_expanded = sp.expand(G)
G_series = sp.series(G_expanded, e, 0, K + 1).removeO()
G_poly = sp.Poly(G_series, e)

solutions = {}
for order in range(1, K + 1):
    coeff = G_poly.coeff_monomial(e ** order)
    coeff_sub = coeff.subs(solutions)
    coeff_sub = sp.expand(coeff_sub)
    sol = sp.solve(sp.Eq(coeff_sub, 0), a[order - 1])
    assert len(sol) == 1, (order, sol)
    solutions[a[order - 1]] = sp.simplify(sol[0])
    print(f"a{order} (my own re-derivation) =", solutions[a[order - 1]])

# ---- Compare against BEAST's published closed forms (transcribed verbatim from
# machine2-c35-extraction-spec-for-m3.md section 3) ----
g_0_1, g_1_0, g_2_0, g_1_1, g_0_2 = (g[(0, 1)], g[(1, 0)], g[(2, 0)], g[(1, 1)], g[(0, 2)])
g_3_0, g_2_1, g_1_2, g_0_3 = (g[(3, 0)], g[(2, 1)], g[(1, 2)], g[(0, 3)])
g_4_0, g_3_1, g_2_2, g_1_3, g_0_4 = (g[(4, 0)], g[(3, 1)], g[(2, 2)], g[(1, 3)], g[(0, 4)])

beast_a = -g_0_1 / g_1_0
beast_b = (-g_0_1 ** 2 * g_2_0 + g_0_1 * g_1_0 * g_1_1 - g_0_2 * g_1_0 ** 2) / g_1_0 ** 3
beast_a3 = (-2 * g_0_1 ** 3 * g_2_0 ** 2 + g_0_1 ** 2 * g_1_0 * (g_0_1 * g_3_0 + 3 * g_1_1 * g_2_0)
            - g_0_1 * g_1_0 ** 2 * (g_0_1 * g_2_1 + 2 * g_0_2 * g_2_0 + g_1_1 ** 2)
            - g_0_3 * g_1_0 ** 4 + g_1_0 ** 3 * (g_0_1 * g_1_2 + g_0_2 * g_1_1)) / g_1_0 ** 5
beast_a4 = (-5 * g_0_1 ** 4 * g_2_0 ** 3
            + 5 * g_0_1 ** 3 * g_1_0 * g_2_0 * (g_0_1 * g_3_0 + 2 * g_1_1 * g_2_0)
            - g_0_1 ** 2 * g_1_0 ** 2 * (g_0_1 ** 2 * g_4_0 + 4 * g_0_1 * g_1_1 * g_3_0
                                          + 4 * g_0_1 * g_2_0 * g_2_1 + 6 * g_0_2 * g_2_0 ** 2
                                          + 6 * g_1_1 ** 2 * g_2_0)
            + g_0_1 * g_1_0 ** 3 * (g_0_1 ** 2 * g_3_1 + 3 * g_0_1 * g_0_2 * g_3_0
                                     + 3 * g_0_1 * g_1_1 * g_2_1 + 3 * g_0_1 * g_1_2 * g_2_0
                                     + 6 * g_0_2 * g_1_1 * g_2_0 + g_1_1 ** 3)
            - g_0_4 * g_1_0 ** 6
            + g_1_0 ** 5 * (g_0_1 * g_1_3 + g_0_2 * g_1_2 + g_0_3 * g_1_1)
            - g_1_0 ** 4 * (g_0_1 ** 2 * g_2_2 + 2 * g_0_1 * g_0_2 * g_2_1 + 2 * g_0_1 * g_0_3 * g_2_0
                            + 2 * g_0_1 * g_1_1 * g_1_2 + g_0_2 ** 2 * g_2_0 + g_0_2 * g_1_1 ** 2)
            ) / g_1_0 ** 7

mine = [solutions[a[0]], solutions[a[1]], solutions[a[2]], solutions[a[3]]]
theirs = [beast_a, beast_b, beast_a3, beast_a4]
names = ['a', 'b', 'a3', 'a4']

print("\n=== symbolic difference (should simplify to 0) ===")
import random
randvals = {sym: sp.Rational(random.randint(-97, 97), random.randint(1, 13)) for sym in g.values()}
# avoid zero/degenerate g_1_0
randvals[g_1_0] = sp.Rational(37, 11)

for name, m, t in zip(names, mine, theirs):
    diff_sym = sp.simplify(m - t)
    diff_num = sp.nsimplify(0)
    diff_num_val = (m - t).subs(randvals)
    diff_num_val = sp.nsimplify(diff_num_val)
    print(f"{name}: symbolic simplify(mine - beast's) = {diff_sym}   "
          f"numeric check at random rationals = {sp.N(diff_num_val, 30)}")
