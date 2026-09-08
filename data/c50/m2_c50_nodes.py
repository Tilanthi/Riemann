#!/usr/bin/env python3
"""m2_c50_nodes.py -- UNREGISTERED, EXPLORATORY arm of cycle 50, labelled as such everywhere it
is reported.  It was written AFTER the prereg was pushed (995ecf7) and after six of the eight
registered cells had landed; it therefore scores NOTHING and predicts nothing.  It exists to ask
the mechanism question the registered arms cannot: WHY does the pooled spectrum alternate?

Hypothesis (offered, not registered): the pooled low spectrum is a NODAL ladder -- the m-th rung's
eigenfunction has m-1 sign changes inside the window, as for a Sturm-Liouville / prolate-type
operator with an even weight.  If so, parity alternation is a COROLLARY (an eigenfunction with
m-1 nodes on a symmetric interval has parity (-1)^(m-1)), and Connes sec 6.6's "simple with even
eigenvector" is the m=1 rung of it.

The measuring instrument data/c46/c46_parity.py returns only (lambda, residual) -- the vectors are
discarded -- so the iteration is re-implemented HERE rather than by editing a sealed file (c49's
rule: ship a new script, never edit the registered one).  Its self-test is that its eigenvalues
must reproduce the sealed instrument's PUBLISHED ones; if they do not, nothing below is reported.

The node count is read off a SAMPLED reconstruction, so the sample count is a knob: it is varied
(c34: vary knobs one at a time; c46: a quadrature/sample count is a knob, declare it and vary it)
and both readings are printed.  A node count that moves with the grid is reported as moving.

usage: m2_c50_nodes.py PARITY X N DPS GLDEG ITERS K
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
def _find_dir(name):
    """m1-L191 finding (c): resolve relative to THIS file, working-tree layout first, committed
    data/c50 layout second -- no absolute clone path anywhere in this cycle's scripts."""
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


for _d in ("c42", "code", "c46"):
    sys.path.insert(0, _find_dir(_d))
from mpmath import mp, mpf, sqrt, cos, sin, pi
import c46_parity as P


def block_with_vectors(M, k, iters):
    """same block inverse iteration + Rayleigh-Ritz as c46_parity.smallest_block, but the Ritz
    VECTORS are kept.  Deliberately the same starting block and the same loop so that the
    eigenvalues are comparable to the sealed instrument's digit for digit."""
    n = len(M)
    A = mp.matrix(M)
    V = mp.matrix(n, k)
    for i in range(n):
        for j in range(k):
            V[i, j] = mpf(1) / (1 + ((i * (j + 3) + j) % 7)) + mpf(j + 1) / (n + i + 1)

    def orth(V):
        for j in range(k):
            for i in range(j):
                c = sum(V[r, i] * V[r, j] for r in range(n))
                for r in range(n):
                    V[r, j] -= c * V[r, i]
            nr_ = sqrt(sum(V[r, j] ** 2 for r in range(n)))
            for r in range(n):
                V[r, j] /= nr_
        return V

    V = orth(V)
    lams = None
    for _ in range(iters):
        W = mp.matrix(n, k)
        for j in range(k):
            col = mp.lu_solve(A, mp.matrix([V[r, j] for r in range(n)]))
            for r in range(n):
                W[r, j] = col[r]
        V = orth(W)
        B = mp.matrix(k, k)
        AV = A * V
        for i in range(k):
            for j in range(k):
                B[i, j] = sum(V[r, i] * AV[r, j] for r in range(n))
        for i in range(k):
            for j in range(i):
                B[i, j] = B[j, i] = (B[i, j] + B[j, i]) / 2
        E, Q = mp.eigsy(B)
        V = V * Q
        lams = [E[i] for i in range(k)]
    return lams, V


def sample_and_count(coef, om, nr, L, parity, npts, tol):
    """phi(t) = sum_a coef[a]*nr[a]*{cos,sin}(om[a] t) on (-L/2, L/2), sampled on a uniform interior
    grid; count sign changes among the samples whose magnitude exceeds tol*max|phi| on the grid.

    TWO KNOBS, BOTH DECLARED AND BOTH VARIED (c34/c46): the sample count npts and the significance
    threshold tol.  v1 of this routine skipped exact zeros, which LOSES a crossing that lands on a
    grid point -- the odd basis is exactly 0 at t=0 and t=0 is on every grid here.  That defect
    produced grid-unstable counts (0/1, 2/3, 6/7, 8/9, 14/15) in the first run; it is fixed by
    filtering on significance instead of skipping zeros, and the first run's numbers are reported
    as the defective ones they are rather than dropped."""
    half = L / 2
    vals = []
    for i in range(npts):
        t = -half + (2 * half) * mpf(i + 1) / (npts + 1)
        s = mpf(0)
        for a in range(len(om)):
            s += coef[a] * nr[a] * (cos(om[a] * t) if parity == "even" else sin(om[a] * t))
        vals.append(s)
    mx = max(abs(v) for v in vals)
    cut = tol * mx
    cur, ch = 0, 0
    for v in vals:
        if abs(v) <= cut:
            continue
        sg = 1 if v > 0 else -1
        if cur != 0 and sg != cur:
            ch += 1
        cur = sg
    return ch


def main():
    par, X, N, DPS, GL, IT, K = (sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
                                 int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]),
                                 int(sys.argv[7]))
    mp.dps = DPS
    t0 = time.time()
    M, L, _ = P.build_matrix_parity(N, X, GL, par)
    lams, V = block_with_vectors(M, K, IT)
    om, nr, idx = P.make_basis_parity(N, L, par)

    # ---- self-test: eigenvalues must reproduce the SEALED instrument's published cell
    ref = os.path.join(_find_dir("c46"),
                       "c46_block_%s_x%d_N%d_dps%d_g%d_it%d_k%d.json" % (par, X, N, DPS, GL, IT, K))
    depths = None
    if os.path.exists(ref):
        rr = json.load(open(ref))["ritz"]
        depths = []
        for i in range(K):
            a, b = lams[i], mpf(rr[i]["lam"])
            depths.append(mpf(40) if a == b else min(mpf(40), -mp.log(abs(a - b) / abs(a), 10)))
        ok = all(d >= 30 for d in depths)
        print("SELF-TEST vs sealed instrument's cell: depths %s -> %s"
              % ([mp.nstr(d, 4) for d in depths], "PASS" if ok else "FAIL"), flush=True)
        if not ok:
            print("SELF-TEST FAILED -- nothing reported."); return 1
    else:
        print("SELF-TEST: reference cell %s ABSENT -> nothing reported." % os.path.basename(ref))
        return 1

    mp.dps = 50                       # sampling precision; coefficients are O(1)
    GRIDS = (1201, 4001, 12001)
    TOLS = (mpf(0), mpf("1e-8"), mpf("1e-4"))
    out = []
    for j in range(K):
        coef = [V[r, j] for r in range(len(om))]
        counts = {}
        for g in GRIDS:
            for t in TOLS:
                counts["%d_%s" % (g, mp.nstr(t, 2))] = sample_and_count(coef, om, nr, L, par, g, t)
        vals = list(counts.values())
        out.append(dict(rung=j + 1, lam=mp.nstr(lams[j], 20), counts=counts,
                        stable=(len(set(vals)) == 1),
                        coef=[mp.nstr(c, 40) for c in coef]))
        print("  %-4s rung %d  lam=%s  nodes %s  stable=%s"
              % (par, j + 1, mp.nstr(lams[j], 12),
                 " ".join("%s:%d" % (k, v) for k, v in sorted(counts.items())),
                 len(set(vals)) == 1), flush=True)
    res = dict(parity=par, x=X, N=N, dps=DPS, k=K, L=mp.nstr(L, 40),
               selftest_depths=[mp.nstr(d, 6) for d in depths], rungs=out,
               seconds=time.time() - t0, label="UNREGISTERED EXPLORATORY ARM")
    json.dump(res, open(os.path.join(HERE, "m2_c50_nodes_%s_x%d_N%d.json" % (par, X, N)), "w"),
              indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
