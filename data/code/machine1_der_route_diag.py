#!/usr/bin/env python3
"""Diagnostic for the der-route validation failures (a = -1.02 vs anchor +2.6455).

Three questions, measured directly on the same h(w,e) at dps 50:
  D1  What is h on the w-circle? h(0.05,0), h(0.05i,0), h(0.01,0) -- if c2 ~ 1.7e-9
      were right these would be ~4e-12; if the ladder law holds (c2 = -0.672) they
      are O(1e-3..1).
  D2  c2 = h''(0)/2 directly: [h(hh,0)+h(-hh,0)]/(2 hh^2) at hh=1e-3, 1e-2 -- and
      the 4th coefficient [..]/(2 hh^4) pattern for scale.
  D3  dh/de at (0,0): [h(1e-10, +1e-6) - h(1e-10, -1e-6)]/2e-6 (w=1e-10 real keeps
      2s off the pole; c2 w^2 contamination ~ 1e-19, negligible).
  D4  Ladder anchor: h(i*u, e) at the published heat86b rung (e=1e-4,
      u=0.01626735311637081543652166235648198533749 from m2's xi_D column, which my
      rungs reproduce to 4e-41) must be ~0.  Confirms the e-convention and the
      object.
  D5  The ratio test: from D2(c2) and D3(dh/de): a_implied = -(dh/de)/c2 must be
      ~= +2.6455 if the ladder identification is right.
"""
import importlib.util
import os

from mpmath import mp, mpf, mpc, fabs, im, re, pi, cos, sin, zeta, gamma, sqrt, besselk

HERE = os.path.dirname(os.path.abspath(__file__))
ORCH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator"
RUN72 = os.path.join(ORCH, "heat72_birth_locus.py")
spec = importlib.util.spec_from_file_location("h72", RUN72)
h72 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h72)
DSTAR = h72.DSTAR

MPDPS = 50
mp.dps = MPDPS + 10
ZCUT = mpf(MPDPS + 15) * mp.log(10)


def zeta2_C_deep(s, D):
    nu = s - mpf("0.5")
    zcut = ZCUT + h72.ZCUT_A * (mpf(float(fabs(im(s)))) ** 2)
    t1 = zeta(2 * s)
    t2 = sqrt(pi) * gamma(s - mpf("0.5")) * D ** (1 - 2 * s) * zeta(2 * s - 1) / gamma(s)
    total = mpf(0)
    k = 1
    while True:
        z = 2 * pi * D * k
        if z > zcut:
            break
        m = 1
        while z * m <= zcut:
            total += (mpf(m) / k) ** nu * besselk(nu, z * m)
            m += 1
        k += 1
    t3 = (4 * pi ** s / gamma(s)) * D ** (mpf("0.5") - s) * total
    return t1 + t2 + t3


def h(w, e):
    return zeta2_C_deep(mpc(mpf("0.5")) + w, DSTAR + e)


print("dps=%d zcut=%s" % (MPDPS, mp.nstr(ZCUT, 6)), flush=True)

# D1: circle values
for w in (mpf("0.05"), mpc(0, mpf("0.05")), mpf("0.01")):
    v = h(mpc(w), mpf(0))
    print("D1 h(%s, 0) = %s + %s i" % (mp.nstr(w, 3), mp.nstr(re(v), 8), mp.nstr(im(v), 6)), flush=True)

# D2: even Taylor directly
for hh in (mpf("1e-3"), mpf("1e-2")):
    hp, hm = h(mpc(hh), mpf(0)), h(mpc(-hh), mpf(0))
    c2 = (hp + hm) / (2 * hh ** 2)
    print("D2 hh=%s: h+ %s h- %s -> c2 = %s" %
          (mp.nstr(hh, 3), mp.nstr(re(hp), 8), mp.nstr(re(hm), 8), mp.nstr(c2, 12)), flush=True)

# D3: dh/de
w0 = mpf("1e-10")
ep = mpf("1e-6")
dhe = (h(mpc(w0), ep) - h(mpc(w0), -ep)) / (2 * ep)
print("D3 dh/de(0,0) = %s + %s i" % (mp.nstr(re(dhe), 12), mp.nstr(im(dhe), 6)), flush=True)

# D4: ladder anchor
u = mpf("0.01626735311637081543652166235648198533749")
v = h(mpc(0, u * 1), mpf("0.0001"))
print("D4 h(i*u, 1e-4) [m2 c30 u] = %s + %s i   (|.| = %s)" %
      (mp.nstr(re(v), 8), mp.nstr(im(v), 6), mp.nstr(fabs(v), 6)), flush=True)
# and the D* convention: which side of D* has zeros?
for sgn in (1, -1):
    v = h(mpc(0, u), mpf("0.0001") * sgn)
    print("D4b sgn=%+d: h = %s + %s i" % (sgn, mp.nstr(re(v), 8), mp.nstr(im(v), 6)), flush=True)

# D5: implied a from D2 (hh=1e-3) and D3
c2 = (h(mpc(mpf("1e-3")), mpf(0)) + h(mpc(-mpf("1e-3")), mpf(0))) / (2 * mpf("1e-3") ** 2)
print("D5 a_implied = -(dh/de)/c2 = %s" % mp.nstr(-re(dhe) / c2, 15), flush=True)
print("done", flush=True)
