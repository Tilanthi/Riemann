"""
machine 2 (beast-atlas), CYCLE 21 -- independent Epstein zeta^(2)(s,D) instrument.

Object: zeta2(s,D) = (1/2) * sum'_{(j,k) in Z^2} (j^2 + D^2 k^2)^{-s}.

DERIVED HERE, NOT COPIED (the point of the instrument is independence from m1's zeta2_C
explicit-(m,k)-summation route and from m3's theta+mp.quad route):

  Theta_D(t) := sum_{(j,k)} e^{-pi t (j^2 + D^2 k^2)} = theta(t) theta(D^2 t)
  2 pi^{-s} Gamma(s) zeta2(s,D)
      = -1/s + 1/(D(s-1))
        + sum'_{(j,k)} (pi q)^{-s}   Gamma(s,   pi q)          q  = j^2 + D^2 k^2
        + (1/D) sum'_{(j,k)} (pi qt)^{s-1} Gamma(1-s, pi qt)   qt = j^2 + k^2/D^2

(incomplete-Gamma form of the two theta tail integrals -- exponentially convergent, valid for all s.)

FUNCTIONAL EQUATION, derived here:
  Z_{1/D}(s) = D^{2s} Z_D(s)   (pure scaling of the form)
  together with the Poisson/Epstein FE gives   xi_D(s) = xi_D(1-s)  for
      xi_D(s) := 2 (D/pi)^s Gamma(s) zeta2(s,D).
So xi_D is SELF-DUAL and, having real coefficients, is REAL on Re s = 1/2.
=> an on-line zero is a REAL SIGN CHANGE of a real function of t: a 1-D root find.
This is structurally different from m1's 2-D Newton on (Re F, Im F) of the raw zeta2.
"""
import mpmath as mp


def _lattice_terms(D2, cut):
    """(q, multiplicity) for q = j^2 + D2*k^2, (j,k) != (0,0), pi*q <= cut."""
    out = []
    qmax = cut / mp.pi
    jmax = int(mp.floor(mp.sqrt(qmax))) + 1
    kmax = int(mp.floor(mp.sqrt(qmax / D2))) + 1
    for j in range(0, jmax + 1):
        for k in range(0, kmax + 1):
            if j == 0 and k == 0:
                continue
            q = j * j + D2 * k * k
            if q > qmax:
                continue
            if j == 0 or k == 0:
                mult = 2
            else:
                mult = 4
            out.append((q, mult))
    return out


class Zeta2:
    def __init__(self, D, dps=45, guard=12):
        self.dps = dps
        with mp.workdps(dps):
            self.D = mp.mpf(D) if not isinstance(D, mp.mpf) else +D
            D2 = self.D ** 2
            cut = (dps + guard) * mp.log(10)
            self.cut = cut
            self.T1 = _lattice_terms(D2, cut)          # q  = j^2 + D^2 k^2
            self.T2 = _lattice_terms(1 / D2, cut)      # qt = j^2 + k^2/D^2

    def bracket(self, s):
        """-1/s + 1/(D(s-1)) + I2(s) + I1(s)/D   ==  2 pi^{-s} Gamma(s) zeta2(s,D)."""
        with mp.workdps(self.dps):
            s = mp.mpmathify(s)
            D = self.D
            pi = mp.pi
            acc = -1 / s + 1 / (D * (s - 1))
            for q, m in self.T1:
                a = pi * q
                acc += m * a ** (-s) * mp.gammainc(s, a)
            sub = mp.mpf(0)
            for q, m in self.T2:
                a = pi * q
                sub += m * a ** (s - 1) * mp.gammainc(1 - s, a)
            acc += sub / D
            return acc

    def zeta2(self, s):
        with mp.workdps(self.dps):
            s = mp.mpmathify(s)
            return self.bracket(s) * mp.pi ** s / (2 * mp.gamma(s))

    def xi(self, s):
        """xi_D(s) = 2 (D/pi)^s Gamma(s) zeta2(s,D) = D^s * bracket(s).  Self-dual."""
        with mp.workdps(self.dps):
            s = mp.mpmathify(s)
            return self.D ** s * self.bracket(s)

    def xi_line(self, t):
        """xi_D(1/2 + i t) for real t -- returns the REAL part; imaginary part is a residual check."""
        with mp.workdps(self.dps):
            v = self.xi(mp.mpf(0.5) + 1j * mp.mpf(t))
            return v


if __name__ == "__main__":
    mp.mp.dps = 45
    print("== control 1: zeta2(s,1) == 2 zeta(s) beta(s)")
    Z1 = Zeta2(1, dps=45)
    for s in [mp.mpf(2), mp.mpf(3) / 2, mp.mpc(mp.mpf(1) / 2, 3), mp.mpc(mp.mpf(1) / 4, 11)]:
        beta = 4 ** (-s) * (mp.zeta(s, mp.mpf(1) / 4) - mp.zeta(s, mp.mpf(3) / 4))
        ref = 2 * mp.zeta(s) * beta
        got = Z1.zeta2(s)
        print("  s=%-28s rel=%s" % (mp.nstr(s, 8), mp.nstr(abs(got - ref) / abs(ref), 5)))

    print("== control 2: FE  xi_D(s) == xi_D(1-s)")
    for D in ["0.14", "0.142857142857142857142857", "0.15", "0.7", "3.0"]:
        Zd = Zeta2(D, dps=45)
        s = mp.mpc(mp.mpf(3) / 10, mp.mpf(7) / 5)
        A, B = Zd.xi(s), Zd.xi(1 - s)
        print("  D=%-10s |xi(s)-xi(1-s)|/|xi(s)| = %s" % (D, mp.nstr(abs(A - B) / abs(A), 5)))

    print("== control 3: xi real on the critical line")
    for D in ["0.142857142857142857142857", "0.15", "0.25"]:
        Zd = Zeta2(D, dps=45)
        for t in ["0.3", "2.7", "13.1"]:
            v = Zd.xi(mp.mpf(0.5) + 1j * mp.mpf(t))
            print("  D=%-26s t=%-6s Im/|.| = %s" % (D, t, mp.nstr(abs(mp.im(v)) / abs(v), 5)))
