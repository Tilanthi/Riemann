"""cycle 17 step 1: establish the completed function and the real Hardy function for
F(s) = zeta2(s,7) = (1/2) sum'(j^2+49k^2)^{-s}, and CONTROL it at two precisions."""
from mpmath import mp, mpf, mpc, pi, gamma, mpmathify, arg, log, exp, im, re, fabs
import eval2, time, json

def Lam(s, D=7):
    return (mpf(D)/pi)**s * gamma(s) * eval2.F(s)

def theta(t, D=7):
    # arg of (D/pi)^{1/2+it} Gamma(1/2+it), continuous principal-ish branch via loggamma
    from mpmath import loggamma
    return t*log(mpf(D)/pi) + im(loggamma(mpc(0.5, t)))

def Z(t, D=7):
    s = mpc(mpf(1)/2, t)
    return exp(mpc(0, theta(t, D))) * eval2.F(s)

out = {}
for dps in (25, 40):
    mp.dps = dps
    rows = []
    for s in [mpc('0.3','4.7'), mpc('0.72','19.3'), mpc('0.51','61.5'), mpc('0.48','100.2')]:
        a, b = Lam(s), Lam(1-s)
        rows.append(dict(s=str(s), rel_fe=mp.nstr(abs(a-b)/abs(a), 6)))
    zrows = []
    for t in ['0.9','7.3','31.7','88.4','117.6']:
        z = Z(mpf(t))
        zrows.append(dict(t=t, Z=mp.nstr(re(z), 12), imag_over_abs=mp.nstr(abs(im(z))/abs(z), 6)))
    out[dps] = dict(fe=rows, hardy=zrows)
print(json.dumps(out, indent=1))
