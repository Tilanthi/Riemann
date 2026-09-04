#!/usr/bin/env python3
"""letter146 -- the "fourth leg": independently rebuild K_T200 and G_raw for seed s1/M8
straight from the published genome file (c,mu,s triples) and mpmath's own zetazero(n),
with ZERO REFERENCE to Mac's exported K_T200/G_raw numbers anywhere in the computation.
His numbers are loaded ONLY at the very end, as the comparison target -- never as an
ingredient. This retires the "singly-derived surface" flagged in his Letter 147 sec3:
all three witness-test instruments so far have used his K_T200/G_raw export as an input
or validation reference; none had rebuilt it from the genomes alone.

Basis convention (per machine1-spec-n2-n5-second-instrument.md, independently re-read
and re-typed here, not copy-pasted from his export script):
  phi_i(x) = window(x) * sum_k c_k * bump((x-mu_k)/s_k)
  bump(t)  = exp(-1/(1-t^2)) for |t|<1, else 0
  window(x)= theta((8-|x|)/2), theta(u) = exp(-1/u)/(exp(-1/u)+exp(-1/(1-u))) on (0,1),
             0 for u<=0, 1 for u>=1
  breakpoints for quadrature = {-8,-6,6,8} union {mu-s, mu+s per bump}
  U_i(rho) = int phi_i(t) e^{rho t} dt  (mp.quad, piecewise over sorted breakpoints)
  G_raw[i,j] = int phi_i phi_j dt
  K_T[i,j] = sum over zeros rho=1/2+i*gamma, 0<gamma<=T, of 2*Re[U_i(rho)*conj(U_j(rho))]
dps=45 throughout (trap #99 floor). Zeros via mpmath.zetazero(n), independent of any
externally-supplied zero table (T1's own Odlyzko cross-check already answered the
"one implementation" concern for the zero LOCATIONS; this run is about the K MATRIX).
"""
import json, os, time
from mpmath import mp, mpf, exp, quad, zetazero, fabs, conj

mp.dps = 45

HERE = os.path.dirname(os.path.abspath(__file__))
GENOME_JSON = os.path.join(HERE, "machine1_heat70_genomes_m8_m64.json")
TARGET_JSON = os.path.join(os.path.dirname(HERE), "machine1_heat72k_identity_target_m8.json")


def theta(u):
    if u <= 0:
        return mpf(0)
    if u >= 1:
        return mpf(1)
    return exp(-1 / u) / (exp(-1 / u) + exp(-1 / (1 - u)))


def window(x):
    return theta((8 - fabs(x)) / 2)


def bump(t):
    if fabs(t) >= 1:
        return mpf(0)
    return exp(-1 / (1 - t * t))


def make_phi(genome):
    triples = [(mpf(str(c)), mpf(str(mu)), mpf(str(s))) for (c, mu, s) in genome]

    def phi(x):
        tot = mpf(0)
        for (c, mu, s) in triples:
            tot += c * bump((x - mu) / s)
        return window(x) * tot

    edges = sorted(set([mpf(-8), mpf(-6), mpf(6), mpf(8)] +
                        [mu - s for (c, mu, s) in triples] +
                        [mu + s for (c, mu, s) in triples]))
    return phi, edges


def U(phi, edges, rho):
    re = quad(lambda t: (phi(t) * exp(rho * t)).real, edges)
    im = quad(lambda t: (phi(t) * exp(rho * t)).imag, edges)
    return mp.mpc(re, im)


def main():
    t_start = time.time()
    with open(GENOME_JSON) as fh:
        gdata = json.load(fh)
    genomes = gdata["genomes"]["s1/M8"]
    M = len(genomes)
    phis, edges_list = zip(*[make_phi(g) for g in genomes])

    def pair_edges(i, j):
        return sorted(set(edges_list[i]) | set(edges_list[j]))

    # G_raw -- direct, no zeros needed
    G = [[None] * M for _ in range(M)]
    for i in range(M):
        for j in range(M):
            pe = pair_edges(i, j)
            G[i][j] = quad(lambda t: phis[i](t) * phis[j](t), pe)
    print(f"[{time.time()-t_start:.1f}s] G_raw done", flush=True)

    # zeros to T=200, own mpmath.zetazero call, independent of any external table
    T = 200
    zs = []
    n = 1
    while True:
        z = zetazero(n)
        if float(z.imag) > T:
            break
        zs.append(z)
        n += 1
    print(f"[{time.time()-t_start:.1f}s] {len(zs)} zeros to T={T} (own zetazero calls)", flush=True)

    # cache U per (genome, zero)
    Ucache = {}

    def Uc(i, zi, z):
        key = (i, zi)
        if key not in Ucache:
            Ucache[key] = U(phis[i], edges_list[i], z)
        return Ucache[key]

    K = [[mpf(0)] * M for _ in range(M)]
    for zi, z in enumerate(zs):
        Uz = [Uc(i, zi, z) for i in range(M)]
        for i in range(M):
            for j in range(M):
                K[i][j] += 2 * (Uz[i] * conj(Uz[j])).real
        if (zi + 1) % 10 == 0:
            print(f"[{time.time()-t_start:.1f}s] {zi+1}/{len(zs)} zeros folded into K", flush=True)
    print(f"[{time.time()-t_start:.1f}s] K_T200 done", flush=True)

    # ---- ONLY NOW load Mac's export, purely for comparison ----
    with open(TARGET_JSON) as fh:
        tdata = json.load(fh)
    ref = tdata["seeds"]["s1/M8"]
    Gref = [[mpf(x) for x in row] for row in ref["G_raw"]]
    Kref = [[mpf(x) for x in row] for row in ref["K_T200"]]

    def maxrel(A, B):
        worst = mpf(0)
        for i in range(M):
            for j in range(M):
                denom = max(abs(A[i][j]), abs(B[i][j]), mpf('1e-30'))
                rel = abs(A[i][j] - B[i][j]) / denom
                if rel > worst:
                    worst = rel
        return worst

    def maxabs(A, B):
        worst = mpf(0)
        for i in range(M):
            for j in range(M):
                d = abs(A[i][j] - B[i][j])
                if d > worst:
                    worst = d
        return worst

    print("=== COMPARISON (my from-scratch rebuild vs Mac's export, seed s1/M8) ===")
    print("G_raw  max abs diff:", maxabs(G, Gref), " max rel diff:", maxrel(G, Gref))
    print("K_T200 max abs diff:", maxabs(K, Kref), " max rel diff:", maxrel(K, Kref))
    print("K_T200[0][0] mine:", K[0][0], " ref:", Kref[0][0])
    print("G_raw[0][0]  mine:", G[0][0], " ref:", Gref[0][0])

    out = {
        "note": "independent from-scratch rebuild of K_T200/G_raw for s1/M8 from the genome "
                "file + own mpmath.zetazero calls; Mac's export used ONLY at the comparison "
                "step below, never as a computational input",
        "dps": mp.dps, "T": T, "n_zeros": len(zs),
        "G_raw": [[str(x) for x in row] for row in G],
        "K_T200": [[str(x) for x in row] for row in K],
        "max_abs_diff_G": str(maxabs(G, Gref)),
        "max_rel_diff_G": str(maxrel(G, Gref)),
        "max_abs_diff_K": str(maxabs(K, Kref)),
        "max_rel_diff_K": str(maxrel(K, Kref)),
        "wall_seconds": time.time() - t_start,
    }
    with open(os.path.join(HERE, "letter146_k_rebuild_result.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"[{time.time()-t_start:.1f}s] WROTE letter146_k_rebuild_result.json")


if __name__ == "__main__":
    main()
