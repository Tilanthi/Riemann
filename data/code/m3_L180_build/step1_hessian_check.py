"""
Validate the analytic A2 = d^2(quad_ex)/d(delta)^2|_0 formula against a raw central-difference
second derivative of the ACTUAL quad_ex matrix, before trusting A2 in the eigenvalue perturbation
step. Also confirms d(quad_ex)/d(delta)|_0 = 0 (Step 1 of the derivation) numerically.
"""
import sys, time
sys.path.insert(0, '.')
from mpmath import mp, mpf
from why_half import build_instruments, get_zeros, g_of

if __name__ == '__main__':
    t0 = time.time()
    insts = build_instruments()
    zeros = get_zeros(26)
    print(f"[{time.time()-t0:.1f}s] setup done", flush=True)

    inst = insts[8]
    k = 10
    g = g_of(zeros, k, 4)

    h = mpf('1e-8')  # finite-difference step; dps=45 gives ample headroom for a 2nd-order FD at this h

    Q0 = inst.quad_ex(g, mpf(0))
    Qp = inst.quad_ex(g, h)
    Qm = inst.quad_ex(g, -h)

    # first derivative (should be ~0 given evenness)
    D1_fd = (Qp - Qm) / (2 * h)
    max_d1 = max(abs(D1_fd[i, j]) for i in range(8) for j in range(8))
    print(f"max |finite-diff 1st derivative| (should be ~0, evenness check): {mp.nstr(max_d1, 6)}",
          flush=True)

    # second derivative via central difference
    D2_fd = (Qp - 2 * Q0 + Qm) / (h * h)

    A2_analytic = inst.A2_hessian(g)

    maxdiff = mpf(0)
    maxval = mpf(0)
    for i in range(8):
        for j in range(8):
            d = abs(D2_fd[i, j] - A2_analytic[i, j])
            maxdiff = max(maxdiff, d)
            maxval = max(maxval, abs(A2_analytic[i, j]))
    print(f"max |A2_analytic| over the matrix: {mp.nstr(maxval, 10)}", flush=True)
    print(f"max |finite-diff 2nd deriv - analytic A2|: {mp.nstr(maxdiff, 6)}", flush=True)
    print(f"relative (to max|A2|): {mp.nstr(maxdiff/maxval, 6)}", flush=True)

    # try a couple of h values to check FD truncation error is behaving as expected (O(h^2))
    for hh in [mpf('1e-6'), mpf('1e-10')]:
        Qp2 = inst.quad_ex(g, hh)
        Qm2 = inst.quad_ex(g, -hh)
        D2_fd2 = (Qp2 - 2 * Q0 + Qm2) / (hh * hh)
        md = max(abs(D2_fd2[i, j] - A2_analytic[i, j]) for i in range(8) for j in range(8))
        print(f"h={mp.nstr(hh,3)}: max diff vs analytic = {mp.nstr(md, 6)}", flush=True)

    print(f"\n[{time.time()-t0:.1f}s] done", flush=True)
