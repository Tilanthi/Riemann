"""machine2 cycle22 — the N2/N5 witness-test design, attacked before the scored run.

Objects (our derivation; only the genomes + the reference matrices are m1's):

  For the bilinear entry (i,j) the explicit-formula test function Phi_ij has transform
      U_ij(s) = 1/2 [ u_i(s) u_j(1-s) + u_i(1-s) u_j(s) ]
  (symmetric, s <-> 1-s covariant).  U_ij is ANALYTIC in s, so the zero-side term of a
  hypothetical object with zero multiset Z is  sum_{rho in Z} U_ij(rho)  -- unambiguous
  off the line.

  ON the critical line rho = 1/2 + i gamma one has 1-rho = conj(rho), hence
      sum over {rho, rho-bar} U_ij = 2 Re[ u_i(rho) conj(u_j(rho)) ]   = m1's K entry.
  OFF the line the two expressions are DIFFERENT.  For an FE-closed off-line quadruple
  Q = {1/2 +- delta +- i gamma}:
      analytic form :  x^T S x = 4 Re[ g(p) conj(g(p')) ],  p = 1/2+delta+i gamma,
                                                            p'= 1/2-delta+i gamma
      m1 spec form  :  x^T K x = 2|g(p)|^2 + 2|g(p')|^2
      difference    :  x^T (K - S) x = 2 |g(p) - g(p')|^2  >= 0     (exactly)
  so m1's recipe dominates the true zero side in the Loewner order, by
  2|g(p)-g(p')|^2 = 8 delta^2 |g'|^2 + O(delta^4).
"""
import json, sys, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target, make_phi, breakpoints, gl_nodes

mp.dps = 40
KEY = "s1/M8"
DEG = 8
N = 8

gens = load_genomes(KEY)
tgt = load_target(KEY)
gam = [mp.mpf(g) for g in json.load(open("/workspace/rh/cycle22/zeros210.json"))]
bases = [Basis(g, degree=DEG) for g in gens]
half = mp.mpf(1) / 2

# ---------- our own Gram matrix ----------
def gram():
    phis = [b.phi for b in bases]
    allpts = sorted(set(sum([breakpoints(b.bumps) for b in bases], [])))
    ivs = [(allpts[k], allpts[k + 1]) for k in range(len(allpts) - 1) if allpts[k + 1] > allpts[k]]
    xs, ws = [], []
    for (a, b) in ivs:
        for (x, w) in gl_nodes(a, b, DEG):
            xs.append(x); ws.append(w)
    vals = [[p(x) for x in xs] for p in phis]
    G = mp.matrix(N, N)
    for i in range(N):
        for j in range(i, N):
            s = mp.mpf(0)
            for k in range(len(xs)):
                s += ws[k] * vals[i][k] * vals[j][k]
            G[i, j] = s; G[j, i] = s
    return G


def lam(F, G):
    """generalized eigenvalues of F v = lam G v, G SPD."""
    L = mp.cholesky(G)
    Li = mp.inverse(L)
    B = Li * F * Li.T
    B = (B + B.T) / 2
    return sorted(mp.eigsy(B, eigvals_only=True))


def mat(rows):
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = mp.mpf(rows[i][j])
    return M


def zero_pair_K(rho):
    """m1 spec form for one UPPER-half zero rho (covers rho and its conjugate)."""
    u = [b.u(rho) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(u[i] * mp.conj(u[j]))
    return M


def zero_pair_S(rho):
    """analytic form, summed over {rho, conj(rho)}: u_i(rho)u_j(1-rho) + c.c., symmetrised."""
    u = [b.u(rho) for b in bases]
    v = [b.u(1 - rho) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            t = u[i] * v[j] + u[j] * v[i]
            M[i, j] = mp.re(t)   # + conj part -> 2*Re, /2 from symmetrisation
    return M


if __name__ == "__main__":
    t0 = time.time()
    print("=== 1. instrument checks (ours vs m1's export) ===", flush=True)
    G = gram()
    Gm1 = mat(tgt["G_raw"])
    dG = max(abs(G[i, j] - Gm1[i, j]) for i in range(N) for j in range(N))
    print(f"|G_ours - G_m1|_max = {mp.nstr(dG,4)}   ({time.time()-t0:.0f}s)", flush=True)

    K200 = mat(tgt["K_T200"]); K150 = mat(tgt["K_T150"])
    br_abs = max(abs(K200[i, j] - K150[i, j]) for i in range(N) for j in range(N))
    print(f"m1 T200-T150 bracket, abs max = {mp.nstr(br_abs,4)}")

    # our own tail estimate: zeros 200 < gamma <= 209.58
    tail = mp.matrix(N, N)
    ntail = 0
    for g in gam:
        if g > 200:
            tail += zero_pair_K(mp.mpc(half, g)); ntail += 1
    print(f"our tail 200<gamma<=209.58 ({ntail} zeros), abs max = "
          f"{mp.nstr(max(abs(tail[i,j]) for i in range(N) for j in range(N)),4)}")

    lm = lam(K200, G)
    print(f"lambda_min(K_T200, G_ours) = {mp.nstr(lm[0],12)}   (m1 anchor 1.1761206927492675e-05)")
    print(f"lambda_max = {mp.nstr(lm[-1],8)}  cond(G) = "
          f"{mp.nstr(max(mp.eigsy(G, eigvals_only=True))/min(mp.eigsy(G, eigvals_only=True)),6)}")

    print("\n=== 2. the delta-ladder, both forms ===", flush=True)
    # count-matched FE-closed move: remove the two on-line zeros gamma_1, gamma_2,
    # add the off-line quadruple {1/2 +- delta +- i gamma_0}, gamma_0 = (g1+g2)/2.
    g1, g2 = gam[0], gam[1]           # 14.1347..., 21.0220...
    g0 = (g1 + g2) / 2
    B_rem = zero_pair_K(mp.mpc(half, g1)) + zero_pair_K(mp.mpc(half, g2))
    print(f"removed on-line zeros gamma = {mp.nstr(g1,10)}, {mp.nstr(g2,10)}; "
          f"added quadruple at gamma_0 = {mp.nstr(g0,10)}")
    print(f"{'delta':>8} {'lam_min ANALYTIC':>22} {'lam_min m1-SPEC':>22} {'gap (PSD) max':>14}")
    rows = []
    for d in ["0", "0.001", "0.01", "0.05", "0.2", "0.5"]:
        dd = mp.mpf(d)
        p = mp.mpc(half + dd, g0)
        q = mp.mpc(half - dd, g0)
        # analytic: the quadruple contributes 2Re[u_i(p)u_j(1-p)+u_j(p)u_i(1-p)]  (= zero_pair_S(p) doubled?)
        up = [b.u(p) for b in bases]
        uq = [b.u(q) for b in bases]          # note 1-p = conj(q), so u(1-p) = conj(u(q))
        A_an = mp.matrix(N, N); A_m1 = mp.matrix(N, N)
        for i in range(N):
            for j in range(N):
                A_an[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i])) / 2 * 2
                A_m1[i, j] = 2 * mp.re(up[i] * mp.conj(up[j])) + 2 * mp.re(uq[i] * mp.conj(uq[j]))
        F_an = A_an - B_rem
        F_m1 = A_m1 - B_rem
        gapm = A_m1 - A_an
        la = lam(F_an, G)[0]
        lb = lam(F_m1, G)[0]
        gmax = max(abs(gapm[i, j]) for i in range(N) for j in range(N))
        rows.append((d, la, lb, gmax))
        print(f"{d:>8} {mp.nstr(la,12):>22} {mp.nstr(lb,12):>22} {mp.nstr(gmax,6):>14}", flush=True)

    print("\n=== 3. the exact gap identity: K_spec - S_analytic = 2|g(p)-g(p')|^2 (PSD, rank<=2) ===")
    dd = mp.mpf("0.05")
    p = mp.mpc(half + dd, g0); q = mp.mpc(half - dd, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    D = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            w_i = up[i] - uq[i]; w_j = up[j] - uq[j]
            D[i, j] = 2 * mp.re(w_i * mp.conj(w_j))
    A_an = mp.matrix(N, N); A_m1 = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            A_an[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
            A_m1[i, j] = 2 * mp.re(up[i] * mp.conj(up[j])) + 2 * mp.re(uq[i] * mp.conj(uq[j]))
    resid = max(abs((A_m1 - A_an)[i, j] - D[i, j]) for i in range(N) for j in range(N))
    ev = sorted(mp.eigsy(D, eigvals_only=True))
    print(f"|(K_spec - S) - 2Re[(u(p)-u(p'))(u(p)-u(p'))^*]|_max = {mp.nstr(resid,4)}")
    print(f"eigenvalues of the gap matrix: {[mp.nstr(e,4) for e in ev]}")
    print(f"done {time.time()-t0:.0f}s")
