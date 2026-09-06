#!/usr/bin/env python3
"""m1 -- evaluator decomposition probe for the der-route v1 diagnosis (L174 1).

Re-runs the t1/t2/t3 decomposition of zeta2_C_deep (the v1/v2 evaluator,
byte-identical formula to the scored heat72 runner) at five dps x zcut
configs, printing each PART separately.  Purpose: the pre-v2 diagnosis ran
this comparison interactively; this script re-executes it so the committed
probe log carries it.  Expected (from the diagnosis): all five configs agree
per-part to ~14+ digits, i.e. the raw evaluator was never the corruption
site; v1's failure lived between raw evals and the printed constants.

Probe point: s = 1/2 + 0.05, D = D* (the same point the diagnosis used).
Nothing here is scored; this is a channel probe.
"""
import importlib.util
import os
import sys

from mpmath import mp, mpf, mpc, pi, gamma, zeta, sqrt, besselk, im

HERE = os.path.dirname(os.path.abspath(__file__))
ORCH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator"
RUN72 = os.path.join(ORCH, "heat72_birth_locus.py")

spec = importlib.util.spec_from_file_location("h72", RUN72)
h72 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h72)
DSTAR = h72.DSTAR

CONFIGS = [(50, "149.66"), (60, "172.69"), (60, "287.82"),
           (70, "172.69"), (70, "287.82")]


def parts(s, D, zcut_base):
    nu = s - mpf("0.5")
    zcut = zcut_base + h72.ZCUT_A * (mpf(float(abs(im(s)))) ** 2)
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
    return t1, t2, t3


def main():
    s = mpc(mpf("0.5") + mpf("0.05"))
    print("evaluator decomposition probe: s = 0.55 + 0i, D = D* = %s" % mp.nstr(DSTAR, 30))
    ref = None
    for dps, zcut_s in CONFIGS:
        mp.dps = dps + 10          # guard digits as in v2
        t1, t2, t3 = parts(s, DSTAR, mpf(zcut_s))
        h = t1 + t2 + t3
        print("dps %3d zcut %6s : t1 %s" % (dps, zcut_s, mp.nstr(t1, 18)))
        print("                    t2 %s" % mp.nstr(t2, 18))
        print("                    t3 %s" % mp.nstr(t3, 18))
        print("                    h  %s" % mp.nstr(h, 18))
        if ref is None:
            ref = (t1, t2, t3)
        else:
            for name, a, b in zip(("t1", "t2", "t3"), ref, (t1, t2, t3)):
                d = abs(a - b) / max(abs(a), abs(b))
                print("                    %s rel-vs-first %.3e" % (name, float(d)))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
