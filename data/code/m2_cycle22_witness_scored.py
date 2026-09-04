"""machine2 cycle22 — SCORED RUN for the pre-registered bare-zero-side witness test.

Pre-registration: machine2-cycle22-PREREG-witness-analytic-zero-side.md (pushed before this ran).
Scored object:  lam_min( S_Z(delta), G )   with

    S_Z[i,j] = sum_{rho in Z} 1/2 [ u_i(rho) u_j(1-rho) + u_i(1-rho) u_j(rho) ]

    Z = { 1/2 +- i gamma_n : 0 < gamma_n <= 200 }  \  { gamma_k, gamma_{k+1} }
        U  { 1/2 +- delta +- i gamma_0 },  gamma_0 = (gamma_k + gamma_{k+1})/2

On-line pairs contribute 2Re[u_i(rho) conj(u_j(rho))] (= m1's K).  The off-line quadruple
contributes 2Re[ u_i(p) conj(u_j(q)) + u_j(p) conj(u_i(q)) ],  p = 1/2+delta+i g0,
q = 1/2-delta+i g0  (verified against a contour residue sum to 1.1e-41).
"""
import json, time
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N

mp.dps = 40
DELTAS = ["0", "0.001", "0.01", "0.05", "0.1", "0.2", "0.3", "0.45"]
ETAS = ["0", "0.5", "1", "2", "3"]
FLOOR = mp.mpf("1e-25")

gens = load_genomes("s1/M8")
tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open("/workspace/rh/cycle22/zeros210.json"))]
bases = [Basis(g, degree=8) for g in gens]
half = mp.mpf(1) / 2
G = gram()
K200 = mat(tgt["K_T200"])
up200 = [g for g in gam if g <= 200]
print(f"# upper-half zeros with gamma <= 200: {len(up200)}")
print(f"# lam_min(K_T200, G) = {mp.nstr(lam(K200,G)[0],12)}")


def quad_analytic(delta, g0):
    p = mp.mpc(half + delta, g0); q = mp.mpc(half - delta, g0)
    up = [b.u(p) for b in bases]; uq = [b.u(q) for b in bases]
    M = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            M[i, j] = 2 * mp.re(up[i] * mp.conj(uq[j]) + up[j] * mp.conj(uq[i]))
    return M


PAIRS = {"PAIR-A": 0, "PAIR-B": 70}
out = {}
for name, k in PAIRS.items():
    g1, g2 = up200[k], up200[k + 1]
    g0 = (g1 + g2) / 2
    B_rem = zero_pair_K(mp.mpc(half, g1)) + zero_pair_K(mp.mpc(half, g2))
    base = K200 - B_rem
    print(f"\n### {name}: k={k} gamma={mp.nstr(g1,10)}, {mp.nstr(g2,10)} gap={mp.nstr(g2-g1,6)} "
          f"gamma_0={mp.nstr(g0,10)}", flush=True)
    print(f"{'delta':>8} {'lam_min(S_Z,G)':>26}   fires?")
    res = {}
    for d in DELTAS:
        S = base + quad_analytic(mp.mpf(d), g0)
        l = lam(S, G)[0]
        res[d] = mp.nstr(l, 20)
        print(f"{d:>8} {mp.nstr(l,16):>26}   {'YES' if l < -FLOOR else 'no'}", flush=True)
    # diagnostics
    print(" -- diagnostics (NOT falsifiers: on-line => PSD by construction) --")
    diag = {}
    for e in ETAS:
        A = zero_pair_K(mp.mpc(half, g0 + mp.mpf(e))) + zero_pair_K(mp.mpc(half, g0 - mp.mpf(e)))
        l = lam(base + A, G)[0]
        diag[e] = mp.nstr(l, 16)
        print(f"  eta={e:>6}  lam_min = {mp.nstr(l,12):>20}  {'PASS' if l >= -FLOOR else 'FAIL'}")
    eta_star = (g2 - g1) / 2
    A = zero_pair_K(mp.mpc(half, g0 + eta_star)) + zero_pair_K(mp.mpc(half, g0 - eta_star))
    dk = max(abs((base + A)[i, j] - K200[i, j]) for i in range(N) for j in range(N))
    print(f"  eta*={mp.nstr(eta_star,10)}: |S_Z - K_T200|_max = {mp.nstr(dk,4)}  "
          f"{'PASS' if dk < mp.mpf('1e-30') else 'FAIL'}")
    out[name] = {"k": k, "g1": mp.nstr(g1, 20), "g2": mp.nstr(g2, 20), "ladder": res,
                 "eta_diag": diag, "eta_star_dK": mp.nstr(dk, 6)}

json.dump(out, open("/workspace/rh/cycle22/scored_witness.json", "w"), indent=1)
print("\ndone")
