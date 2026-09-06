"""
m3-L171 part C -- the real xi_D run: g[m][n] for 1<=m+n<=4 (a4), the implied D* from the g[0][.]
column, and a timing/consistency check before committing to the final numbers.

Optimization over the generic extract_g_table: the m=0 column (needed both for a4/a5's g[0][n]
terms AND for the implied-D* root) is extracted by DIRECT evaluation of the real-valued
xi_D(1/2, D) on the real axis (exact, no contour, no aliasing risk at all -- this is what
m3_L169_G00_and_a.py's f_half already did for g[0][1]). Only m>=1 needs the circle average
(there is no other way to isolate a w^{2m} Taylor coefficient, m>=1, except a contour integral).
"""
import sys, time
sys.path.insert(0, '.')
import mpmath as mp
from m3_L169_xiD_core import xiD
from m3_L171_fornberg import fd_weights

DSTAR_STR = '0.141733239663887191395415685084185023623144561955016655942867'


def g0_column(dstar_str, h_e, npts, max_n, dps):
    """g[0][n] for n=0..max_n via direct real-axis evaluation + Fornberg FD. Cheap, exact (no
    aliasing channel at all -- xi_D(1/2, D) needs no contour)."""
    mp.mp.dps = dps
    Dstar = mp.mpf(dstar_str)
    half_span = (npts - 1) // 2
    p_values = list(range(-half_span, half_span + 1))
    e_nodes = [p * h_e for p in p_values]
    vals = []
    for ee in e_nodes:
        D = Dstar - ee
        vals.append(xiD(mp.mpf('0.5'), D).real)
    Cw = fd_weights(0, e_nodes, max_n)
    g0 = {}
    for n in range(max_n + 1):
        deriv = sum(Cw[n][i] * vals[i] for i in range(len(e_nodes)))
        g0[n] = deriv / mp.factorial(n)
    return g0, e_nodes, vals


def gm_column(dstar_str, m, h_e, npts, max_n, r_w, N_w, dps):
    """g[m][n] for n=0..max_n, m>=1, via circle average (power=2m) + Fornberg FD in e.
    (Kept for standalone/timing use; the production path below shares F(w,D) across all m.)"""
    mp.mp.dps = dps
    Dstar = mp.mpf(dstar_str)
    half_span = (npts - 1) // 2
    p_values = list(range(-half_span, half_span + 1))
    e_nodes = [p * h_e for p in p_values]
    thetas = [2 * mp.pi * k / N_w for k in range(N_w)]
    w_points = [r_w * mp.e ** (mp.mpc(0, th)) for th in thetas]
    c_vals = []
    for ee in e_nodes:
        D = Dstar - ee
        total = mp.mpc(0)
        for w in w_points:
            total += xiD(mp.mpf('0.5') + w, D) * w ** (-2 * m)
        c_vals.append(total / N_w)
    Cw = fd_weights(0, e_nodes, max_n)
    gcol = {}
    for n in range(max_n + 1):
        deriv = sum(Cw[n][i] * c_vals[i] for i in range(len(e_nodes)))
        gcol[n] = deriv / mp.factorial(n)
    return gcol


def gm_columns_shared(dstar_str, m_list, h_e, npts, max_order, r_w, N_w, dps, log=True):
    """g[m][n] for all m in m_list (m>=1), n=0..(max_order-m), sharing the SAME N_w circle-point
    xi_D evaluations across every m (computed once per D-node, reused with different w^-2m
    weights) -- this is the only computationally sane way to get multiple m's, since each raw
    xi_D evaluation is expensive and identical work would otherwise be repeated per m."""
    mp.mp.dps = dps
    Dstar = mp.mpf(dstar_str)
    half_span = (npts - 1) // 2
    p_values = list(range(-half_span, half_span + 1))
    e_nodes = [p * h_e for p in p_values]
    thetas = [2 * mp.pi * k / N_w for k in range(N_w)]
    w_points = [r_w * mp.e ** (mp.mpc(0, th)) for th in thetas]

    t0 = time.time()
    F_vals = []  # F_vals[node_index][k]
    for i, ee in enumerate(e_nodes):
        D = Dstar - ee
        row = [xiD(mp.mpf('0.5') + w, D) for w in w_points]
        F_vals.append(row)
        if log:
            print(f"  node {i+1}/{len(e_nodes)} (e={mp.nstr(ee,3)}) done "
                  f"[{time.time()-t0:.1f}s elapsed]", flush=True)

    Cw = fd_weights(0, e_nodes, max_order)
    out = {}
    for m in m_list:
        n_limit = max_order - m
        c_vals = []
        for i in range(len(e_nodes)):
            total = mp.mpc(0)
            for k, w in enumerate(w_points):
                total += F_vals[i][k] * w ** (-2 * m)
            c_vals.append(total / N_w)
        for n in range(n_limit + 1):
            deriv = sum(Cw[n][i] * c_vals[i] for i in range(len(e_nodes)))
            out[(m, n)] = deriv / mp.factorial(n)
    return out


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


def assemble_a5(g):
    g01, g10, g20, g11, g02 = g[(0, 1)], g[(1, 0)], g[(2, 0)], g[(1, 1)], g[(0, 2)]
    g30, g21, g12, g03 = g[(3, 0)], g[(2, 1)], g[(1, 2)], g[(0, 3)]
    g40, g31, g22, g13, g04 = g[(4, 0)], g[(3, 1)], g[(2, 2)], g[(1, 3)], g[(0, 4)]
    g50, g41, g32, g23, g14, g05 = g[(5, 0)], g[(4, 1)], g[(3, 2)], g[(2, 3)], g[(1, 4)], g[(0, 5)]
    return (-14 * g01 ** 5 * g20 ** 4
            + 7 * g01 ** 4 * g10 * g20 ** 2 * (3 * g01 * g30 + 5 * g11 * g20)
            - g01 ** 3 * g10 ** 2 * (6 * g01 ** 2 * g20 * g40 + 3 * g01 ** 2 * g30 ** 2
                                      + 30 * g01 * g11 * g20 * g30 + 15 * g01 * g20 ** 2 * g21
                                      + 20 * g02 * g20 ** 3 + 30 * g11 ** 2 * g20 ** 2)
            + g01 ** 2 * g10 ** 3 * (g01 ** 3 * g50 + 5 * g01 ** 2 * g11 * g40
                                      + 5 * g01 ** 2 * g20 * g31 + 5 * g01 ** 2 * g21 * g30
                                      + 20 * g01 * g02 * g20 * g30 + 10 * g01 * g11 ** 2 * g30
                                      + 20 * g01 * g11 * g20 * g21 + 10 * g01 * g12 * g20 ** 2
                                      + 30 * g02 * g11 * g20 ** 2 + 10 * g11 ** 3 * g20)
            - g01 * g10 ** 4 * (g01 ** 3 * g41 + 4 * g01 ** 2 * g02 * g40
                                 + 4 * g01 ** 2 * g11 * g31 + 4 * g01 ** 2 * g12 * g30
                                 + 4 * g01 ** 2 * g20 * g22 + 2 * g01 ** 2 * g21 ** 2
                                 + 12 * g01 * g02 * g11 * g30 + 12 * g01 * g02 * g20 * g21
                                 + 6 * g01 * g03 * g20 ** 2 + 6 * g01 * g11 ** 2 * g21
                                 + 12 * g01 * g11 * g12 * g20 + 6 * g02 ** 2 * g20 ** 2
                                 + 12 * g02 * g11 ** 2 * g20 + g11 ** 4)
            - g05 * g10 ** 8
            + g10 ** 7 * (g01 * g14 + g02 * g13 + g03 * g12 + g04 * g11)
            - g10 ** 6 * (g01 ** 2 * g23 + 2 * g01 * g02 * g22 + 2 * g01 * g03 * g21
                          + 2 * g01 * g04 * g20 + 2 * g01 * g11 * g13 + g01 * g12 ** 2
                          + g02 ** 2 * g21 + 2 * g02 * g03 * g20 + 2 * g02 * g11 * g12
                          + g03 * g11 ** 2)
            + g10 ** 5 * (g01 ** 3 * g32 + 3 * g01 ** 2 * g02 * g31 + 3 * g01 ** 2 * g03 * g30
                          + 3 * g01 ** 2 * g11 * g22 + 3 * g01 ** 2 * g12 * g21
                          + 3 * g01 ** 2 * g13 * g20 + 3 * g01 * g02 ** 2 * g30
                          + 6 * g01 * g02 * g11 * g21 + 6 * g01 * g02 * g12 * g20
                          + 6 * g01 * g03 * g11 * g20 + 3 * g01 * g11 ** 2 * g12
                          + 3 * g02 ** 2 * g11 * g20 + g02 * g11 ** 3)
            ) / g10 ** 9


if __name__ == '__main__':
    t0 = time.time()
    dps = 60
    h_e = mp.mpf('1e-4')
    npts = 13
    r_w = mp.mpf('0.04')
    N_w = 20
    max_order = 5

    print(f"=== production run: a5, dps={dps}, npts={npts}, h_e={h_e}, r_w={r_w}, N_w={N_w} ===",
          flush=True)

    g0, e_nodes0, vals0 = g0_column(DSTAR_STR, h_e, npts, max_n=max_order, dps=dps)
    print(f"[{time.time()-t0:.1f}s] g0 column done", flush=True)
    for n in range(max_order + 1):
        print(f"  g[0][{n}] = {mp.nstr(g0[n], 25)}", flush=True)

    g_shared = gm_columns_shared(DSTAR_STR, [1, 2, 3, 4, 5], h_e, npts, max_order, r_w, N_w, dps,
                                  log=True)
    print(f"[{time.time()-t0:.1f}s] shared m=1..5 columns done", flush=True)

    g = {(0, n): g0[n] for n in range(max_order + 1)}
    g.update(g_shared)
    for key in sorted(g.keys()):
        print(f"  g{key} = {mp.nstr(g[key], 25)}", flush=True)

    greal = {k: v.real if isinstance(v, mp.mpc) else v for k, v in g.items()}
    a4 = assemble_a4(greal)
    a5 = assemble_a5(greal)
    print(f"\na4 (this run) = {a4}", flush=True)
    print("BEAST's a4 (m2 convention, x=w^2, e=D*-D) = -20.475538755390412501...", flush=True)
    ref4 = mp.mpf('-20.475538755390412501')
    print("rel diff vs BEAST's a4 =", abs(a4 - ref4) / abs(ref4), flush=True)

    print(f"\na5 (this run) = {a5}", flush=True)
    print("BEAST's a5 (m2 convention, x=w^2, e=D*-D) = 18.271162501149951037...", flush=True)
    ref5 = mp.mpf('18.271162501149951037')
    print("rel diff vs BEAST's a5 =", abs(a5 - ref5) / abs(ref5), flush=True)

    # also recompute 'a' from THIS run's g[0][1], g[1][0] as an internal consistency check
    a_check = -g[(0, 1)] / g[(1, 0)]
    print(f"\ninternal check: a = -g[0][1]/g[1][0] (this run) = {a_check}", flush=True)
    print("(should match the L170 value 2.6455214118... to the precision this run supports)",
          flush=True)

    print(f"\n[{time.time()-t0:.1f}s] done", flush=True)
