"""
Efficient full-matrix N2/N5 identity build: precompute u_i(-1/2+it) and u_i(3/2-it) ONCE per basis
function on a shared t-grid, then reuse via interpolation for the archimedean integral of every (i,j)
pair -- avoids the O(M^2) cost of the naive per-pair quadrature (which needed ~727s/pair, unworkable
for a full MxM matrix).

Endpoint[i,j] = u_i(1)*u_j(0)                       (cheap, from Mac's export)
Prime[i,j]    = (as before, per-pair, ~few seconds each -- already cheap)
Arch[i,j]     = (1/2pi) int Re[K(t) u_i(-1/2+it) u_j(3/2-it)] dt
              ~ precompute U_neg[i](t_k) = u_i(-1/2+it_k), U_pos[i](t_k) = u_i(3/2-it_k) on a shared
                grid, interpolate, do the t-integral for ANY (i,j) pair cheaply.
"""
import sys, time
sys.path.insert(0, '/tmp')
from identity_check_fast import load_genome, u_of_s_scipy as u_of_s
import numpy as np
from scipy import special, integrate, interpolate
import json

def digamma_half(s):
    return special.digamma(s / 2)

def kernel_correct(s):
    return 0.5 * digamma_half(s) + 0.5 * digamma_half(1 - s) - np.log(np.pi)

def prime_side_fast(fi, fj, max_shift, grid_n=400):
    shifts = np.linspace(0, max_shift, grid_n)

    def cross_corr(mode):
        vals = np.zeros(len(shifts))
        bpts_i = fi.breakpoints()
        for idx, shift in enumerate(shifts):
            if mode == 'sub':
                lo = max(fi.supp_lo, fj.supp_lo + shift)
                hi = min(fi.supp_hi, fj.supp_hi + shift)
                if lo >= hi:
                    continue
                bpts_j = [p + shift for p in fj.breakpoints()]
                pts = sorted(set([lo, hi]) | {p for p in bpts_i if lo < p < hi} | {p for p in bpts_j if lo < p < hi})
                val, _ = integrate.quad(lambda tau: fi.phi(tau) * fj.phi(tau - shift) * np.exp(tau),
                                         pts[0], pts[-1], points=pts[1:-1], limit=200, epsabs=1e-14, epsrel=1e-12)
            else:
                lo = max(fi.supp_lo, fj.supp_lo - shift)
                hi = min(fi.supp_hi, fj.supp_hi - shift)
                if lo >= hi:
                    continue
                bpts_j = [p - shift for p in fj.breakpoints()]
                pts = sorted(set([lo, hi]) | {p for p in bpts_i if lo < p < hi} | {p for p in bpts_j if lo < p < hi})
                val, _ = integrate.quad(lambda tau: fi.phi(tau) * fj.phi(tau + shift) * np.exp(tau),
                                         pts[0], pts[-1], points=pts[1:-1], limit=200, epsabs=1e-14, epsrel=1e-12)
            vals[idx] = val
        return vals

    Cvals = cross_corr('sub')
    Dvals = cross_corr('add')
    Cinterp = interpolate.interp1d(shifts, Cvals, kind='cubic', bounds_error=False, fill_value=0.0)
    Dinterp = interpolate.interp1d(shifts, Dvals, kind='cubic', bounds_error=False, fill_value=0.0)

    Nmax = int(np.exp(max_shift)) + 10
    Nmax = min(Nmax, 3_000_000)
    is_prime = np.ones(Nmax + 1, dtype=bool)
    is_prime[0:2] = False
    for p in range(2, int(Nmax ** 0.5) + 1):
        if is_prime[p]:
            is_prime[p * p::p] = False
    primes = np.nonzero(is_prime)[0]

    total = 0.0
    for p in primes:
        logp = np.log(p)
        k = 1
        while k * logp <= max_shift:
            shift = k * logp
            c = float(Cinterp(shift))
            d = float(Dinterp(shift))
            if c != 0.0 or d != 0.0:
                total += logp * (np.exp(-k * logp) * c + d)
            k += 1
    return total


from numpy.polynomial.legendre import leggauss

def composite_gauss_legendre(panel_edges, n_per_panel):
    """Fixed composite Gauss-Legendre nodes/weights -- avoids interpolation error entirely
    (found empirically: cubic-spline interpolation of the precomputed u-grid gave WRONG answers,
    even with 700 points, off by 3-13%, apparently because u(3/2-it)'s huge dynamic range near
    t=0 isn't captured well by spline interpolation; fixed quadrature nodes/weights converge
    cleanly instead -- verified against the slow direct adaptive-quadrature method to 0.05% at
    n_per_panel=90, see /tmp/n2n5_gl_quadrature.py)."""
    all_nodes, all_weights = [], []
    for k in range(len(panel_edges) - 1):
        a, b = panel_edges[k], panel_edges[k + 1]
        x, w = leggauss(n_per_panel)
        all_nodes.append(0.5 * (b - a) * x + 0.5 * (b + a))
        all_weights.append(0.5 * (b - a) * w)
    return np.concatenate(all_nodes), np.concatenate(all_weights)

def build_t_grid(t_max, n_per_panel=100):
    panels = sorted(set(p for p in [-t_max, -100, -50, -20, -10, -5, -2, 0, 2, 5, 10, 20, 50, 100, t_max]
                         if abs(p) <= t_max) | {-t_max, t_max})
    return composite_gauss_legendre(panels, n_per_panel)


def precompute_u_variants(fns, t_grid_nodes):
    """For each basis fn, compute u_i(-1/2+it) and u_i(3/2-it) at the exact GL nodes."""
    M = len(fns)
    U_neg = np.zeros((M, len(t_grid_nodes)), dtype=complex)
    U_pos = np.zeros((M, len(t_grid_nodes)), dtype=complex)
    t0 = time.time()
    for i, f in enumerate(fns):
        for k, t in enumerate(t_grid_nodes):
            s_neg = complex(-0.5, t)
            U_neg[i, k] = u_of_s(f, s_neg)
            U_pos[i, k] = u_of_s(f, 1 - s_neg)  # = 3/2 - it
        print(f"  basis {i} done, {time.time()-t0:.1f}s elapsed", flush=True)
    return U_neg, U_pos


def arch_matrix_entry(U_neg_i, U_pos_j, weights, kernel_vals):
    """Arch[i,j] via a pure Gauss-Legendre weighted sum -- no interpolation."""
    integrand_vals = kernel_vals * U_neg_i * U_pos_j
    return np.sum(weights * integrand_vals) / (2 * np.pi)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', default='s1')
    ap.add_argument('--M', type=int, default=8)
    ap.add_argument('--tmax', type=float, default=150)
    args = ap.parse_args()

    fns = load_genome(f"{args.seed}/M{args.M}", args.M)
    d = json.load(open('/workspace/Riemann/repo/data/machine1_heat72k_identity_target_m8.json'))
    tgt = d['seeds'][f"{args.seed}/M{args.M}"]
    U0 = np.array([float(x) for x in tgt['U0']])
    U1 = np.array([float(x) for x in tgt['U1']])
    K200 = np.array(tgt['K_T200'], dtype=float)
    K150 = np.array(tgt['K_T150'], dtype=float)

    print(f"Building Gauss-Legendre nodes and precomputing u_i variants for {args.M} basis functions...")
    t_nodes, t_weights = build_t_grid(args.tmax, n_per_panel=100)
    print(f"  n_nodes: {len(t_nodes)}")
    U_neg, U_pos = precompute_u_variants(fns, t_nodes)

    kernel_vals = np.array([kernel_correct(complex(-0.5, t)) for t in t_nodes])

    M = args.M
    Endpoint = np.outer(U1, U0)
    print("\nComputing Prime matrix...")
    Prime = np.zeros((M, M))
    t0 = time.time()
    for i in range(M):
        for j in range(i, M):
            max_shift = max(fns[i].supp_hi - fns[j].supp_lo, fns[j].supp_hi - fns[i].supp_lo)
            p = prime_side_fast(fns[i], fns[j], max_shift)
            Prime[i, j] = p
            if i != j:
                # Prime[j,i] uses swapped roles -- NOT necessarily equal, compute separately
                max_shift2 = max(fns[j].supp_hi - fns[i].supp_lo, fns[i].supp_hi - fns[j].supp_lo)
                Prime[j, i] = prime_side_fast(fns[j], fns[i], max_shift2)
    print(f"  Prime matrix done in {time.time()-t0:.1f}s")

    print("\nComputing Arch matrix (using precomputed u-grids)...")
    Arch = np.zeros((M, M), dtype=complex)
    t0 = time.time()
    for i in range(M):
        for j in range(M):
            Arch[i, j] = arch_matrix_entry(U_neg[i], U_pos[j], t_weights, kernel_vals)
    print(f"  Arch matrix done in {time.time()-t0:.1f}s")

    RHS = Endpoint - Prime + Arch.real
    diff = RHS - K200
    rel = np.abs(diff) / (np.abs(K200) + 1e-300)
    print(f"\nMax abs diff vs K_T200: {np.max(np.abs(diff)):.3e}")
    print(f"Max rel diff vs K_T200 (entries with |K200|>1e-6): ", end="")
    mask = np.abs(K200) > 1e-6
    print(f"{np.max(rel[mask]):.3e}")
    print(f"Mean rel diff: {np.mean(rel[mask]):.3e}")

    np.savez('/tmp/n2n5_matrix_result.npz', Endpoint=Endpoint, Prime=Prime, Arch=Arch,
              RHS=RHS, K200=K200, K150=K150, U0=U0, U1=U1)
    print("Saved to /tmp/n2n5_matrix_result.npz")
