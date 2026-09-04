"""
Letter 147 -- testing Mac's own open question from his L146 sec3/sec4: does his delta^2-truncated
local theory's systematic 10-50% under-negative magnitude bias close (in the predicted direction)
when the Taylor expansion is extended to delta^4 (adding u''', u'''')?

Exact analytic derivatives, NOT finite differences (trap #104's lesson: finite-difference precision
degrades per derivative order exactly where cancellation demand grows). u_i(s) = int phi_i(t) e^{st} dt
is entire in s (phi_i compactly supported, bounded), so u_i^(n)(s0) = int phi_i(t) t^n e^{st} dt exactly,
differentiating under the integral sign -- no numerical-differentiation error at any order.

Design: PAIR-A midpoint gamma0=17.5783 (same object as Letters 145/146's delta-ladder). For each
delta in the ladder, build S_ij(quadruple) THREE ways:
  (a) EXACT      -- u(p), u(q) computed directly (Letter 145's method, ground truth)
  (b) ORDER-2    -- u(p),u(q) replaced by their delta^2-truncated Taylor series (u0,u',u'' only) --
                    reproduces Mac's own local theory, on MY instrument, as an independent check of it
  (c) ORDER-4    -- adds u''', u'''' (delta^3, delta^4 terms)
Then lambda_min(S_Z, G) for all three, at every delta rung, to see whether (c) moves the truncated
answer toward (a) relative to (b) -- and by how much of the 10-50% gap.
"""
import sys, time
sys.path.insert(0, '/tmp')
from identity_check_m8 import load_genome as load_genome_mp
import mpmath as mp
import json

mp.mp.dps = 45


def u_of_s_mp(fi, s, pts=None):
    if pts is None:
        pts = fi.breakpoints()
    re = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).real, pts)
    im = mp.quad(lambda x: (fi.phi(x) * mp.e**(s * x)).imag, pts)
    return mp.mpc(re, im)


def u_deriv_mp(fi, s, n, pts=None):
    """n-th derivative of u_i at s, exact: int phi_i(t) t^n e^{st} dt."""
    if pts is None:
        pts = fi.breakpoints()
    if n == 0:
        return u_of_s_mp(fi, s, pts)
    re = mp.quad(lambda x: (fi.phi(x) * (x**n) * mp.e**(s * x)).real, pts)
    im = mp.quad(lambda x: (fi.phi(x) * (x**n) * mp.e**(s * x)).imag, pts)
    return mp.mpc(re, im)


def taylor_u(coeffs, delta, order):
    """u(s0 + delta) truncated at `order`, coeffs = [u0, u1=u', u2=u'', ...] (already divided nowhere)."""
    tot = mp.mpc(0)
    fact = mp.mpf(1)
    dpow = mp.mpf(1)
    for n in range(order + 1):
        if n > 0:
            fact *= n
            dpow *= delta
        tot += (dpow / fact) * coeffs[n]
    return tot


def S_quadruple_from_u(Up, Uq):
    M = len(Up)
    S = mp.zeros(M, M)
    for i in range(M):
        for j in range(M):
            S[i, j] = 2 * (Up[i] * mp.conj(Uq[j])).real + 2 * (Uq[i] * mp.conj(Up[j])).real
    return S


def load_K_T200(seed, M):
    d = json.load(open('/workspace/Riemann/repo/data/machine1_heat72k_identity_target_m8.json'))
    tgt = d['seeds'][f"{seed}/M{M}"]
    K200 = mp.matrix(M, M)
    G = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            K200[i, j] = mp.mpf(tgt['K_T200'][i][j])
            G[i, j] = mp.mpf(tgt['G_raw'][i][j])
    return K200, G


def lambda_min_gen_eig(K, G):
    L = mp.cholesky(G)
    Linv = L**-1
    B = Linv * K * Linv.T
    n = B.rows
    for i in range(n):
        for j in range(i + 1, n):
            avg = (B[i, j] + B[j, i]) / 2
            B[i, j] = avg
            B[j, i] = avg
    E, _ = mp.eigsy(B)
    return min(E), E


def main():
    t_start = time.time()
    M = 8
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    K200, G = load_K_T200(seed, M)
    print(f"[{time.time()-t_start:.1f}s] loaded K_T200, G, genomes ({seed}/M{M})", flush=True)

    z0 = mp.zetazero(1)
    z1 = mp.zetazero(2)
    gamma_a, gamma_b = mp.im(z0), mp.im(z1)
    gamma0 = (gamma_a + gamma_b) / 2
    rho_a = mp.mpc('0.5', gamma_a)
    rho_b = mp.mpc('0.5', gamma_b)
    print(f"[{time.time()-t_start:.1f}s] PAIR-A gamma0(midpoint)={gamma0}", flush=True)

    def K_pair_matrix(rho):
        U = [u_of_s_mp(fns[i], rho) for i in range(M)]
        Kr = mp.zeros(M, M)
        for i in range(M):
            for j in range(M):
                Kr[i, j] = 2 * (U[i] * mp.conj(U[j])).real
        return Kr

    K_a = K_pair_matrix(rho_a)
    K_b = K_pair_matrix(rho_b)
    K_base = K200 - K_a - K_b
    lmin_base, _ = lambda_min_gen_eig(K_base, G)
    print(f"[{time.time()-t_start:.1f}s] launch (removal-only) lambda_min = {lmin_base} "
          f"(compare Mac's 3.375751e-7)", flush=True)

    s0 = mp.mpc('0.5', gamma0)
    ORDER_MAX = 4
    print(f"[{time.time()-t_start:.1f}s] computing exact derivative coefficients u^(0..{ORDER_MAX}) "
          f"at s0 for all {M} genomes (analytic, no finite differences)...", flush=True)
    coeffs = []
    for i in range(M):
        row = [u_deriv_mp(fns[i], s0, n) for n in range(ORDER_MAX + 1)]
        coeffs.append(row)
        print(f"  genome {i}: u0={row[0]}", flush=True)
    print(f"[{time.time()-t_start:.1f}s] derivative coefficients done", flush=True)

    delta_ladder = [mp.mpf(x) for x in ['0.01', '0.05', '0.1', '0.2', '0.3', '0.45']]
    results = []
    for delta in delta_ladder:
        t0 = time.time()
        # (a) EXACT
        p = mp.mpc(mp.mpf('0.5') + delta, gamma0)
        q = mp.mpc(mp.mpf('0.5') - delta, gamma0)
        Up_exact = [u_of_s_mp(fns[i], p) for i in range(M)]
        Uq_exact = [u_of_s_mp(fns[i], q) for i in range(M)]
        S_exact = S_quadruple_from_u(Up_exact, Uq_exact)
        lmin_exact, _ = lambda_min_gen_eig(K_base + S_exact, G)

        # (b) ORDER-2 truncation
        Up_o2 = [taylor_u(coeffs[i], delta, 2) for i in range(M)]
        Uq_o2 = [taylor_u(coeffs[i], -delta, 2) for i in range(M)]
        S_o2 = S_quadruple_from_u(Up_o2, Uq_o2)
        lmin_o2, _ = lambda_min_gen_eig(K_base + S_o2, G)

        # (c) ORDER-4 truncation
        Up_o4 = [taylor_u(coeffs[i], delta, 4) for i in range(M)]
        Uq_o4 = [taylor_u(coeffs[i], -delta, 4) for i in range(M)]
        S_o4 = S_quadruple_from_u(Up_o4, Uq_o4)
        lmin_o4, _ = lambda_min_gen_eig(K_base + S_o4, G)

        gap2 = lmin_exact - lmin_o2
        gap4 = lmin_exact - lmin_o4
        frac_closed = (1 - gap4 / gap2) * 100 if gap2 != 0 else mp.mpf('nan')
        print(f"[{time.time()-t0:.1f}s] delta={float(delta):.3f}  exact={lmin_exact}  "
              f"order2={lmin_o2}  order4={lmin_o4}  gap2={gap2}  gap4={gap4}  "
              f"pct_gap_closed_by_order4={float(frac_closed):.1f}%", flush=True)
        results.append({
            "delta": float(delta), "exact": str(lmin_exact), "order2": str(lmin_o2),
            "order4": str(lmin_o4), "gap2": str(gap2), "gap4": str(gap4),
            "pct_gap_closed_by_order4": float(frac_closed),
        })

    out = {
        "note": "PAIR-A midpoint delta-ladder, exact vs order-2 (Mac's local theory) vs order-4 "
                "Taylor truncation of the inserted off-line quadruple, using exact analytic "
                "derivatives (no finite differences)",
        "seed": seed, "M": M, "gamma0": str(gamma0), "dps": mp.mp.dps,
        "results": results,
        "wall_seconds": time.time() - t_start,
    }
    with open('/workspace/Riemann/repo/data/code/letter147_taylor_order_result.json', 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t_start:.1f}s] WROTE letter147_taylor_order_result.json")


if __name__ == '__main__':
    main()
