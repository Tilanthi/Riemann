"""
m3-L169 -- from-scratch implementation of xi_D(s) = 2(D/pi)^s Gamma(s) zeta2(s,D), the completed,
self-dual 2D Epstein zeta function central to the "a/b/a3/a4/a5" fold-catastrophe dispute (BEAST's
c34 ask). Classical formula (Epstein/Riemann incomplete-Gamma continuation), independently re-typed
from BEAST's cycle-21 letter's STATED formula (not their code):

  2 pi^{-s} Gamma(s) zeta2(s,D)
     = -1/s + 1/(D(s-1))
       + sum'_{(j,k)} (pi*q)^{-s}   Gamma(s,   pi*q)          q  = j^2 + D^2 k^2
       + (1/D) sum'_{(j,k)} (pi*qt)^{s-1} Gamma(1-s, pi*qt)   qt = j^2 + k^2/D^2

xi_D(s) := 2 (D/pi)^s Gamma(s) zeta2(s,D) = (D/pi)^s * [ -1/s + 1/(D(s-1))
             + sum' (pi q)^{-s} Gamma(s,pi q) + (1/D) sum' (pi qt)^{s-1} Gamma(1-s,pi qt) ]

No code shared with either Mac's or BEAST's implementation -- built directly from the mathematical
formula (classical, textbook Epstein zeta theory).
"""
import mpmath as mp


def xiD(s, D, guard_extra=15):
    """Clean version: xi_D(s) = (D)^s * pi^{-s} * Gamma(s) * 2 * zeta2(s,D)
    Using the identity 2*pi^{-s}*Gamma(s)*zeta2(s,D) = term_pole+sum1+sum2/D directly:
    xi_D(s) = D^s * (term_pole + sum1 + sum2/D).

    BUG FOUND AND FIXED (m3-L169, self-caught via a D* root-find discrepancy against a published
    value): a single rectangular (j,k) cutoff is wrong for D far from 1 -- sum1's q=j^2+D^2 k^2
    needs a k-range ~1/D times the j-range when D<1 (and the opposite for sum2's q~=j^2+k^2/D^2).
    Using one shared jkmax under-samples sum1's k-direction badly at small D. Fixed: each sum gets
    its own (j,k) bound derived from its own q formula, matching an elliptical cutoff q>threshold
    with rectangular (safe, slightly oversampled) bounds."""
    D = mp.mpf(D)
    pi = mp.pi
    term_pole = -1 / s + 1 / (D * (s - 1))
    guard = mp.mp.dps + guard_extra
    Q = guard * mp.log(10) / pi  # need q > Q for the incomplete-gamma tail to be negligible
    sqrtQ = mp.sqrt(Q)
    # sum1: q = j^2 + D^2 k^2 > Q  =>  |j| <= sqrt(Q), |k| <= sqrt(Q)/D
    j1max = int(mp.ceil(sqrtQ)) + 2
    k1max = int(mp.ceil(sqrtQ / D)) + 2
    # sum2: qt = j^2 + k^2/D^2 > Q  =>  |j| <= sqrt(Q), |k| <= D*sqrt(Q)
    j2max = int(mp.ceil(sqrtQ)) + 2
    k2max = int(mp.ceil(D * sqrtQ)) + 2

    sum1 = mp.mpc(0)
    for j in range(-j1max, j1max + 1):
        for k in range(-k1max, k1max + 1):
            if j == 0 and k == 0:
                continue
            q = j * j + D * D * k * k
            piq = pi * q
            sum1 += (piq) ** (-s) * mp.gammainc(s, piq)

    sum2 = mp.mpc(0)
    for j in range(-j2max, j2max + 1):
        for k in range(-k2max, k2max + 1):
            if j == 0 and k == 0:
                continue
            qt = j * j + (k * k) / (D * D)
            piqt = pi * qt
            sum2 += (piqt) ** (s - 1) * mp.gammainc(1 - s, piqt)

    bracket = term_pole + sum1 + sum2 / D
    return (D ** s) * bracket


def zeta2_direct(s, D, N=200):
    """Direct Dirichlet-series control, valid for Re(s)>1: zeta2(s,D)=(1/2)sum'_{j,k}(j^2+D^2k^2)^-s."""
    D = mp.mpf(D)
    total = mp.mpc(0)
    for j in range(-N, N + 1):
        for k in range(-N, N + 1):
            if j == 0 and k == 0:
                continue
            total += (j * j + D * D * k * k) ** (-s)
    return total / 2


if __name__ == '__main__':
    mp.mp.dps = 30
    # Control 1: zeta2(s,1) = 2*zeta(s)*beta(s)  (classical, D=1 case)
    for stest in [mp.mpf('2.5'), mp.mpf('3.3')]:
        lhs_xi = xiD(stest, 1)
        # xi_D(s) at D=1: xi_1(s) = 2*pi^{-s}*Gamma(s)*zeta2(s,1) per definition (since (D/pi)^s*bracket
        # = D^s*bracket, and bracket = 2*pi^{-s}*Gamma(s)*zeta2(s,D)); so zeta2(s,1) = xi_1(s)/(2*pi^{-s}*Gamma(s))
        zeta2_from_xi = lhs_xi / (2 * mp.pi ** (-stest) * mp.gamma(stest))
        rhs = 2 * mp.zeta(stest) * mp.mpf(mp.nstr(1)) # placeholder
        beta_val = mp.mpf(0)
        # Dirichlet beta function via mpmath: beta(s) = sum (-1)^n/(2n+1)^s -- use mpmath's built-in if available
        try:
            beta_val = mp.beta and None
        except Exception:
            pass
        # mpmath has no direct 'dirichlet beta'; compute via lerchphi or hurwitz zeta combo:
        beta_val = 4 ** (-stest) * (mp.zeta(stest, mp.mpf(1) / 4) - mp.zeta(stest, mp.mpf(3) / 4))
        rhs = 2 * mp.zeta(stest) * beta_val
        print(f"s={stest}: zeta2(s,1) from xi = {zeta2_from_xi}")
        print(f"           2*zeta*beta        = {rhs}")
        print(f"           rel diff = {abs(zeta2_from_xi/rhs - 1)}")
        direct = zeta2_direct(stest, 1, N=150)
        print(f"           direct Dirichlet   = {direct}  rel to formula: {abs(direct/zeta2_from_xi-1)}")
        print()
