"""
m3-L171 part B -- the numerical g[m][n] extraction pipeline: circle-average (Cauchy/DFT) for the
m-index (power of w), Fornberg finite-difference weights for the n-index (order of derivative in e),
sharing the underlying complex xi_D evaluations across all m for a given e-node (cheap).

Validated in __main__ against a SYNTHETIC polynomial F(w,D) with HAND-CHOSEN g_true[m][n]
(m3_L169/L170 did not have this kind of from-scratch synthetic dry run -- flagged as a gap in L170,
closed here before trusting the real xi_D run).
"""
import sys
sys.path.insert(0, '.')
import mpmath as mp
from m3_L171_fornberg import fd_weights


def extract_g_table(F, Dstar, r_w, N_w, h_e, npts, max_order, dps):
    """
    F: callable F(w, D) -> mpc, the function to expand (either the synthetic test polynomial or
       the real xi_D(1/2+w, D)).
    Dstar: centre (string or mpf) -- e=Dstar-D.
    r_w, N_w: circle-average parameters for the w (m) index.
    h_e, npts: Fornberg finite-difference parameters for the e (n) index -- npts equally spaced
       nodes centred on e=0 (npts must be odd), i.e. p = -(npts-1)//2 .. +(npts-1)//2, e_p = p*h_e,
       D_p = Dstar - e_p.
    max_order: compute g[m][n] for all (m,n) with 1 <= m+n <= max_order, plus g[0][0].
    Returns dict {(m,n): mpc/mpf}.
    """
    mp.mp.dps = dps
    Dstar = mp.mpf(Dstar) if not isinstance(Dstar, mp.mpf) else Dstar
    half_span = (npts - 1) // 2
    p_values = list(range(-half_span, half_span + 1))
    e_nodes = [p * h_e for p in p_values]
    D_nodes = [Dstar - ee for ee in e_nodes]

    # For each D-node, evaluate F at the N_w circle points ONCE, reuse for every m.
    omega_thetas = [2 * mp.pi * k / N_w for k in range(N_w)]
    w_points = [r_w * mp.e ** (mp.mpc(0, th)) for th in omega_thetas]

    F_vals = {}  # F_vals[node_index][k] = F(w_points[k], D_nodes[node_index])
    for i, D in enumerate(D_nodes):
        F_vals[i] = [F(w, D) for w in w_points]

    # c_{2m}(D_node) for each node, each m
    max_m = max_order
    c_table = {}  # c_table[m][node_index]
    for m in range(0, max_m + 1):
        c_table[m] = []
        for i in range(len(D_nodes)):
            total = mp.mpc(0)
            for k, w in enumerate(w_points):
                total += F_vals[i][k] * w ** (-2 * m)
            c_table[m].append(total / N_w)

    # Fornberg weights in e: nodes are e_nodes, evaluate derivatives 0..max_order at e=0
    fd_max_n = max_order
    Cw = fd_weights(0, e_nodes, fd_max_n)

    g = {}
    for m in range(0, max_m + 1):
        n_limit = max_order - m
        if n_limit < 0:
            continue
        for n in range(0, n_limit + 1):
            # d^n/de^n [c_2m] (0) = sum_i Cw[n][i] * c_table[m][i]; g[m][n] = that / n!
            deriv = sum(Cw[n][i] * c_table[m][i] for i in range(len(e_nodes)))
            g[(m, n)] = deriv / mp.factorial(n)
    return g


if __name__ == '__main__':
    mp.mp.dps = 50

    # ---- synthetic ground truth: g_true[m][n] for 1<=m+n<=4, plus g[0][0]=0 (assume centred) ----
    import random
    random.seed(20260906)
    g_true = {(0, 0): mp.mpf(0)}
    for m in range(0, 5):
        for n in range(0, 5 - m):
            if m == 0 and n == 0:
                continue
            g_true[(m, n)] = mp.mpf(random.randint(-40, 40)) / mp.mpf(random.randint(1, 9))
    g_true[(1, 0)] = mp.mpf('3.7')  # avoid 0/near-0 denominator, make it well-conditioned

    D0 = mp.mpf('0.37')  # synthetic centre, arbitrary

    def Ftest(w, D):
        e = D0 - D
        total = mp.mpc(0)
        for (m, n), val in g_true.items():
            total += val * w ** (2 * m) * e ** n
        return total

    g_est = extract_g_table(Ftest, D0, r_w=mp.mpf('0.04'), N_w=16, h_e=mp.mpf('1e-3'), npts=11,
                             max_order=4, dps=50)

    print("=== synthetic dry-run: extracted vs true g[m][n], m+n<=4 ===")
    maxrel = mp.mpf(0)
    for key in sorted(g_true.keys()):
        if key == (0, 0):
            continue
        true_v = g_true[key]
        est_v = g_est[key]
        rel = abs(est_v.real - true_v) / abs(true_v) if true_v != 0 else abs(est_v.real)
        maxrel = max(maxrel, rel)
        print(f"g{key}: true={true_v}  extracted={mp.nstr(est_v.real, 15)}  rel_err={mp.nstr(rel, 5)}")
    print(f"\nMAX relative error across all 14 synthetic g[m][n], m+n<=4: {mp.nstr(maxrel, 5)}")
    assert maxrel < mp.mpf('1e-20'), "synthetic dry run FAILED -- extraction pipeline has a bug"
    print("PASS: extraction pipeline (circle-average m-index + Fornberg n-index) recovers exact "
          "polynomial coefficients to ~1e-20 or better on the synthetic case.")

    # ---- also validate the a4 closed-form assembly on this same synthetic g-table ----
    def assemble_a4(g):
        g01, g10, g20, g11, g02 = g[(0, 1)], g[(1, 0)], g[(2, 0)], g[(1, 1)], g[(0, 2)]
        g30, g21, g12, g03 = g[(3, 0)], g[(2, 1)], g[(1, 2)], g[(0, 3)]
        g40, g31, g22, g13, g04 = g[(4, 0)], g[(3, 1)], g[(2, 2)], g[(1, 3)], g[(0, 4)]
        return (-5 * g01 ** 4 * g20 ** 3
                + 5 * g01 ** 3 * g10 * g20 * (g01 * g30 + 2 * g11 * g20)
                - g01 ** 2 * g10 ** 2 * (g01 ** 2 * g40 + 4 * g01 * g11 * g30 + 4 * g01 * g20 * g21
                                          + 6 * g02 * g20 ** 2 + 6 * g11 ** 2 * g20)
                + g01 * g10 ** 3 * (g01 ** 2 * g31 + 3 * g01 * g02 * g30 + 3 * g01 * g11 * g21
                                     + 3 * g01 * g12 * g20 + 6 * g02 * g11 * g20 + g11 ** 3)
                - g04 * g10 ** 6
                + g10 ** 5 * (g01 * g13 + g02 * g12 + g03 * g11)
                - g10 ** 4 * (g01 ** 2 * g22 + 2 * g01 * g02 * g21 + 2 * g01 * g03 * g20
                              + 2 * g01 * g11 * g12 + g02 ** 2 * g20 + g02 * g11 ** 2)
                ) / g10 ** 7

    a4_from_true = assemble_a4(g_true)
    a4_from_est = assemble_a4({k: v.real for k, v in g_est.items()})
    rel_a4 = abs(a4_from_est - a4_from_true) / abs(a4_from_true)
    print(f"\na4 from TRUE g-table: {a4_from_true}")
    print(f"a4 from EXTRACTED g-table: {mp.nstr(a4_from_est, 20)}")
    print(f"relative difference: {mp.nstr(rel_a4, 5)}")
    assert rel_a4 < mp.mpf('1e-18')
    print("PASS: a4 closed-form assembly + full extraction pipeline validated end-to-end on a "
          "synthetic case before use on the real xi_D instrument.")
