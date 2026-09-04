"""
machine 2 (beast-atlas) CYCLE 21 -- REFEREE R of the identity gap (m3 L129 sect3 / L131, m1 L132).

Everything here is derived and coded from scratch. It shares NO code with m3's
scalar_identity_check / identity_check_fast, and NO kernel formula with m1's L132.

MY DERIVATION (contour, independent of Kowalski's Prop 1.2.1 and of m1's rebuild):
  u(s) := int phi(x) e^{sx} dx.  Rectangle contour Re s in [-1/2, 3/2], counterclockwise.
  Inside: the pole of zeta at s=1 (residue of -zeta'/zeta is +1) and every nontrivial zero
  (residue -m).  No trivial zero (first is -2), zeta(0) != 0.
    (1/2 pi i) closed-contour = u(1) - sum_rho u(rho)
  Right edge Re s = 3/2:  -zeta'/zeta = sum Lambda(n) n^{-s}  and  (1/2 pi i) int n^{-s} u(s) ds
    = phi(log n)  =>  A = sum Lambda(n) phi(log n).
  Left edge Re s = -1/2 with the FE:
    -zeta'/zeta(s) = zeta'/zeta(1-s) + K(s),   K(s) = (1/2)psi(s/2) + (1/2)psi((1-s)/2) - log pi
    zeta'/zeta(1-s) = -sum Lambda(n) n^{s-1}  (Re(1-s)=3/2)
    => contributes  B = sum Lambda(n) phi(-log n)/n   and   -(1/2 pi) int K(-1/2+it) u(-1/2+it) dt
  RESULT:   A + B  =  u(1) - Z + Arch,     Z = sum over all nontrivial zeros = sum_n 2 Re u(rho_n),
            Arch = (1/2 pi) int_{-inf}^{inf} Re[ K(-1/2+it) u(-1/2+it) ] dt.

The K above is the SUM form minus log pi.  I derive it here:
  Lambda(s) = pi^{-s/2} Gamma(s/2) zeta(s);  Lambda'/Lambda(s) = -1/2 log pi + 1/2 psi(s/2) + zeta'/zeta(s)
  FE Lambda(s)=Lambda(1-s)  =>  Lambda'/Lambda(s) = -Lambda'/Lambda(1-s)
  =>  -zeta'/zeta(s) = zeta'/zeta(1-s) + 1/2 psi(s/2) + 1/2 psi((1-s)/2) - log pi.       [QED]

TEST FUNCTION (mine, not anyone's genome): a Gaussian phi(x) = exp(-(x-c)^2/(2 sig^2)).
Not compactly supported, but every leg is then EXPONENTIALLY convergent AND u(s) is CLOSED FORM
  u(s) = sig sqrt(2 pi) exp(c s + sig^2 s^2 / 2),
so the transform leg carries no quadrature error at all.  This makes the closure a test of the
KERNEL and the CONTRACTION alone -- the two things under dispute -- at ~1e-25 instead of m1's 3e-6.
"""
import mpmath as mp

mp.mp.dps = 30
C = mp.mpf(2)
SIG = mp.mpf("0.35")


def phi(x):
    x = mp.mpf(x)
    return mp.e ** (-(x - C) ** 2 / (2 * SIG ** 2))


def u(s):
    s = mp.mpmathify(s)
    return SIG * mp.sqrt(2 * mp.pi) * mp.e ** (C * s + SIG ** 2 * s ** 2 / 2)


def K_sum(s):      # m1's / my corrected kernel
    s = mp.mpmathify(s)
    return mp.digamma(s / 2) / 2 + mp.digamma((1 - s) / 2) / 2 - mp.log(mp.pi)


def K_diff(s):     # m3's L129 v1 kernel (the alleged defect)
    s = mp.mpmathify(s)
    return mp.digamma(s / 2) / 2 - mp.digamma((1 - s) / 2) / 2


def von_mangoldt_upto(N):
    out = {}
    sieve = [True] * (N + 1)
    for p in range(2, N + 1):
        if sieve[p]:
            for m in range(p * p, N + 1, p):
                sieve[m] = False
            q, lp = p, mp.log(p)
            while q <= N:
                out[q] = lp
                q *= p
    return out


def check_fe(pts):
    """(a) POINTWISE FE CHECK: -zeta'/zeta(s) - zeta'/zeta(1-s) - K(s) == 0."""
    print("(a) pointwise FE receipt at s = -1/2 + it   (dps=%d)" % mp.mp.dps)
    for t in pts:
        s = mp.mpc(mp.mpf(-1) / 2, mp.mpf(t))
        lhs = -mp.zeta(s, derivative=1) / mp.zeta(s)
        z1 = mp.zeta(1 - s, derivative=1) / mp.zeta(1 - s)
        print("    t=%-6s  SUM-form residual = %-12s   DIFF-form residual = %s"
              % (t, mp.nstr(abs(lhs - z1 - K_sum(s)), 5), mp.nstr(abs(lhs - z1 - K_diff(s)), 5)))


def check_classical_limit():
    print("(b) classical limit  Re K(-1/2+it) -> log(t/2pi)")
    for t in [10, 100, 1000]:
        s = mp.mpc(mp.mpf(-1) / 2, t)
        print("    t=%-6d Re K_sum = %-22s log(t/2pi) = %-22s | Re K_diff = %s"
              % (t, mp.nstr(mp.re(K_sum(s)), 10), mp.nstr(mp.log(mp.mpf(t) / (2 * mp.pi)), 10),
                 mp.nstr(mp.re(K_diff(s)), 5)))


def legs(nzeros=40, tmax=70, kernel=K_sum, contraction="complex"):
    lam = von_mangoldt_upto(200000)
    A = mp.fsum(l * phi(mp.log(n)) for n, l in lam.items())
    B = mp.fsum(l * phi(-mp.log(n)) / n for n, l in lam.items())
    U1 = u(1)
    Z = mp.mpf(0)
    for k in range(1, nzeros + 1):
        g = mp.im(mp.zetazero(k))
        Z += 2 * mp.re(u(mp.mpc(mp.mpf(1) / 2, g)))
    if contraction == "complex":
        f = lambda t: mp.re(kernel(mp.mpc(mp.mpf(-1) / 2, t)) * u(mp.mpc(mp.mpf(-1) / 2, t)))
    else:
        f = lambda t: mp.re(kernel(mp.mpc(mp.mpf(-1) / 2, t))) * mp.re(u(mp.mpc(mp.mpf(-1) / 2, t)))
    Arch = mp.quad(f, [-tmax, -20, -5, 0, 5, 20, tmax]) / (2 * mp.pi)
    return A, B, U1, Z, Arch


if __name__ == "__main__":
    check_fe(["0.7", "3.3", "17.2", "41.5"])
    print()
    check_classical_limit()
    print()
    print("(c) END-TO-END CLOSURE on my own Gaussian phi (c=%s, sig=%s), closed-form u(s)" % (C, SIG))
    for name, kern, contr in [("CORRECT  kernel=SUM-logpi, contraction=complex", K_sum, "complex"),
                              ("m3 L129  kernel=DIFF,      contraction=complex", K_diff, "complex"),
                              ("m1 1st   kernel=SUM-logpi, contraction=Re*Re", K_sum, "rere")]:
        A, B, U1, Z, Arch = legs(kernel=kern, contraction=contr)
        lhs = A + B
        rhs = U1 - Z + Arch
        print("    %s" % name)
        print("      A=%s  B=%s" % (mp.nstr(A, 20), mp.nstr(B, 8)))
        print("      u(1)=%s  Z=%s  Arch=%s" % (mp.nstr(U1, 20), mp.nstr(Z, 20), mp.nstr(Arch, 20)))
        print("      CLOSURE |A+B-(u(1)-Z+Arch)| = %s   (rel %s)"
              % (mp.nstr(abs(lhs - rhs), 6), mp.nstr(abs(lhs - rhs) / abs(lhs), 6)))
