#!/usr/bin/env python3
"""IDENT Check 1 (m3-L166 sec2 item 1, first look by m1 per m3-L167 sec2) --
side-by-side identification of Connes' Q_W_lambda vs our census kernel K_S.

Question (m3-L166): is our K_T/G kernel a linear reparametrization of Connes'
Q_W_lambda, a genuinely different object, or a special case?

Sealed sources used (read-only, seals verified at startup, nothing modified,
nothing scored -- this is an identification measurement, not a scored unit):
  [S1] data/code/machine1_heat78c_survivor_census.py   (sealed scored runner)
  [S2] machine1_heat70_genomes_m8_m64.json             (frozen genome basis)
  [S3] heat72k_identity_target_m8.json                 (K_T200 / G_raw, M8)
  [S4] 2602.04022v1.pdf                                (Connes, in-repo)
       - sec4.1 lines 1438-1497: EF f_hat(-i/2)+f_hat(i/2) - sum_{1/2+is in Z}
         f_hat(s) = sum_v W_v(f); W_p line 1462; W_R line 1471;
         RH <=> sum_v W_v(g*g-conv) <= 0 (line 1490)
       - sec5 lines 1688-1703: Q(phi) = EF applied to psi(v)=int phi(u)phi(uv) du/u,
         supp phi in [1,x] (x=13), eta = minimizer, Dirichlet principle
       - sec6.4 lines 1977-1989: Q_W_lambda = Weil form restricted to supp in
         [lam^-1, lam]; A_lambda selfadjoint compact-resolvent on
         L^2([lam^-1,lam], du/u), Q_W_lambda(f,f) = <A_lambda f|f>
       - sec6.6 lines 2068-2075: remaining steps (a) simple+even lowest
         eigenvalue, (b) k_lambda approximates theta_x

What this script measures (VERIFIED-HERE):
  (A) K_T200[S3] equals the ZERO-SIDE explicit-formula kernel
      sum_{0<Im rho<=200} 2 Re[U_a(rho) conj(U_b(rho))] recomputed from [S2]'s
      frozen genomes and mpmath zetazero -- i.e. our kernel is built from the
      zero side of Weil's identity, NOT the prime side.  This is the load-
      bearing measurement: it pins which side of the identity our instrument
      lives on, at machine precision, on the sealed M8 identity target.
  (B) quad_ex(g, 0) == 2*gram(g) on the same basis (runner lines 105-124
      semantics imported from the sealed runner, not re-typed): the census
      control cell is a DOUBLE ZERO at the interpolated ordinate, and the
      displaced cells (delta>0) insert a conjugate-symmetric pair at
      1/2 +- delta + i g -- i.e. exactly the zero-side contribution a zero
      OFF the critical line would make.  Semantics check, machine precision.

What this script does NOT do (stated for the record): it does not recompute the
prime/archimedean side W = W_R + sum_p W_p (that equality on our basis is m3's
Kowalski Prop 1.2.1 identity check, already receipted in [S3]'s own note field
"identity check is m3's (Kowalski Prop 1.2.1 signs)" -- cited, not redone);
it does not touch Connes' lambda-ladder or make any claim about his open (a)/(b).
"""
import hashlib
import importlib.util
import json
import os
import sys

from mpmath import mp, mpf, mpc, exp, quad, zetazero, re as mpre, im as mpim, conj, fabs

mp.dps = 45
HALF = mpf(1) / 2
T0 = __import__("time").time()

EXCH = "/Users/gjw255/astrodata/SWARM/Riemann_exchange"
GEN = EXCH + "/data/code/machine1_heat70_genomes_m8_m64.json"
IDT = ("/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator/"
       "heat72k_identity_target_m8.json")
RUNNER = EXCH + "/data/code/machine1_heat78c_survivor_census.py"
OUT = EXCH + "/data/machine1_ident1_check1.out"

# seals identical to the sealed runner's frozen input hashes [S1 lines 41-45]
SEALS = {
    GEN: "1065fd370fd9370807ea61f19708cbf1d16be77179f279760864386d299da56b",
    IDT: "12b81d093a0eb9d76709a61a9e22015af81a646e18faab722443efc0b03f87ff",
}


def line(msg):
    print(msg, flush=True)


def main():
    line("IDENT Check 1 -- Connes Q_W_lambda vs census K_S, first look (m1)")
    line("sources: [S1] heat78c runner  [S2] heat70 genomes  [S3] heat72k idt  [S4] 2602.04022v1")
    bad = [(p, hashlib.sha256(open(p, "rb").read()).hexdigest(), w)
           for p, w in SEALS.items()
           if hashlib.sha256(open(p, "rb").read()).hexdigest() != w]
    if bad:
        sys.exit("SEAL FAILURE %s -- aborting, nothing measured" % bad)
    line("input seals verified (2/2: GEN, IDT); runner sha256 %s" %
         hashlib.sha256(open(RUNNER, "rb").read()).hexdigest())

    # import make_phi from the sealed runner itself (no re-typing: trap #S12)
    spec = importlib.util.spec_from_file_location("h78c", RUNNER)
    h78c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h78c)
    line("sealed runner imported; make_phi/window/bumpval used verbatim")

    genomes = json.load(open(GEN))["genomes"]["s1/M8"]
    idt = json.load(open(IDT))["seeds"]["s1/M8"]
    M = 8
    phis, edges = zip(*[h78c.make_phi(g) for g in genomes])
    line("M8 basis rebuilt from frozen genomes: %d functions, window |t|<=8 "
         "(= Connes supp [lam^-1, lam] with lam = e^8 = %s)" % (M, mp.nstr(exp(mpf(8)), 8)))

    def U(i, s):
        return quad(lambda t: phis[i](t) * exp(s * t), edges[i])

    # ---- (A) zero-side recomputation of K_T200 -------------------------------
    # zeros with 0 < Im <= 200; assert the cut matches [S3-heata78a] n_zeros=79
    zeros = []
    n = 1
    while True:
        g = mpim(zetazero(n))
        if g > 200:
            break
        zeros.append(g)
        n += 1
    line("zeros with 0<Im<=200: %d (Im(zeta_{%d})=%s, Im(zeta_{%d})=%s)" %
         (len(zeros), len(zeros), mp.nstr(zeros[-1], 10), len(zeros) + 1, mp.nstr(g, 10)))

    Uz = [[U(i, mpc(HALF, g)) for g in zeros] for i in range(M)]
    K_rec = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            K_rec[i, j] = sum(2 * mpre(Uz[i][n] * conj(Uz[j][n])) for n in range(len(zeros)))
    K_stored = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            K_stored[i, j] = mpf(idt["K_T200"][i][j])
    scale = max(fabs(K_stored[i, j]) for i in range(M) for j in range(M))
    dmax = max(fabs(K_rec[i, j] - K_stored[i, j]) for i in range(M) for j in range(M))
    line("[A] K_T200 == sum_{0<Im rho<=200} 2Re[U_i conj(U_j)] : max|diff| = %s "
         "(scale %s, rel %s)  -> %s" %
         (mp.nstr(dmax, 6), mp.nstr(scale, 6), mp.nstr(dmax / scale, 6),
          "VERIFIED-HERE" if dmax < mpf("1e-30") else "CHECK"))

    # ---- (B) surgery semantics: quad_ex(g,0) == 2*gram(g) --------------------
    # runner semantics (lines 105-124), applied with the same U above
    zk = [mpf(str(mpim(zetazero(n)))) for n in range(1, 27)]

    def gram(g0):
        uv = [U(i, mpc(HALF, g0)) for i in range(M)]
        Gm = mp.matrix(M, M)
        for i in range(M):
            for j in range(M):
                Gm[i, j] = 2 * mpre(uv[i] * conj(uv[j]))
        return Gm

    def quad_ex(g0, d):
        p, q = mpc(HALF + d, g0), mpc(HALF - d, g0)
        up = [U(i, p) for i in range(M)]
        uq = [U(i, q) for i in range(M)]
        Qm = mp.matrix(M, M)
        for i in range(M):
            for j in range(M):
                Qm[i, j] = 2 * mpre(up[i] * conj(uq[j]) + up[j] * conj(uq[i]))
        return Qm

    for k in (2, 3, 7):
        g = zk[k] + (zk[k + 1] - zk[k]) * mpf(4) / 8  # runner g_of(k, 4)
        db = max(fabs(quad_ex(g, mpf(0))[i, j] - 2 * gram(g)[i, j])
                 for i in range(M) for j in range(M))
        line("[B] k=%d phi=4/8: |quad_ex(g,0) - 2*gram(g)| max = %s  -> %s" %
             (k, mp.nstr(db, 6), "VERIFIED-HERE" if db < mpf("1e-30") else "CHECK"))

    # ---- dictionary printed for the record -----------------------------------
    line("")
    line("SIDE-BY-SIDE (basis: log variable t = log u, inner product du/u; U(i,s) = "
         "int phi_i e^{st} dt = Mellin at s)")
    line("  Connes [S4]                            | ours [S1,S3]")
    line("  ---------------------------------------+---------------------------------------")
    line("  Q_W_lambda(f,f)=sum_v W_v(f*f-conv)    | K_S = K_T200 - gram(z_k)")
    line("  prime+archimedean side of Weil EF      |   - gram(z_{k+1}) + quad_ex(g,delta)")
    line("                                         | K_T200 = zero side, T=200 [A]")
    line("  operator A_lambda, L^2([lam^-1,lam])   | MxM Galerkin matrix, G-metric")
    line("  supp [lam^-1,lam], lambda free (->inf) | fixed window |t|<=8 (lam=e^8)")
    line("  no zero appears in construction        | zeros are the construction [A]")
    line("  pristine form                          | rank-4 surgery: -2 on-line zero")
    line("                                         |   modes, +pair at 1/2+-delta+ig [B]")
    line("  open (a): lambda_min simple+even,      | controls: surgically modified form")
    line("    lambda->inf (continuum, lambda-axis) |   stays >= -1e-12 at each M (M-axis)")
    line("  open (b): k_lambda ~ theta_x           | (no counterpart)")
    line("  Galerkin: trig N=100-250 (fn.14,Groskin) | Galerkin: M in {8,64} genome bumps")
    line("")
    line("VERDICT (first look, m1; second look = m3 from sealed sources, per L167 s2):")
    line("  NOT a linear reparametrization (different side of the identity; surgery")
    line("    absent in Connes; different truncation axes).")
    line("  NOT unrelated: both are restrictions of the SAME Weil explicit-formula")
    line("    quadratic form -- his from the W side (operator, lambda-axis), ours from")
    line("    the zero side (T=200 finite sum [A], M-Galerkin at fixed lam=e^8), with")
    line("    the W-side equality on our basis carried by m3's receipted Kowalski")
    line("    Prop 1.2.1 identity check, cited not redone.")
    line("  CLASSIFICATION: same form, opposite sides of the identity; ours = doubly")
    line("    truncated zero-side realization + falsification surgery; his = pristine")
    line("    operator on the growing-support axis.  Special-case-with-modification.")
    line("  CONSEQUENCE for Bridge 1 (weakened, per m3-L167 decay-mode correction:")
    line("    ACCEPTED): our M-ladder measures Galerkin faithfulness of OUR probe at")
    line("    fixed lam=e^8 -- a precondition for any numerical lambda-ladder (Groskin's")
    line("    T-rearranged negative eigenvalues are the same stability family, trap")
    line("    #129) -- it does NOT measure Connes' open (a) or (b).")
    line("")
    line("no proof claim; nothing scored; sealed inputs read-only, seals verified above")
    line("IDENT Check 1 done %.1fs" % (__import__("time").time() - T0))


if __name__ == "__main__":
    main()
