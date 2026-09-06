#!/usr/bin/env python3
"""m1 -- the derivative route for a, b, a3 on MY evaluator (the c32 3.3 ask).  v2.

v1 (sha256 1db6dca6...) returned a = -1.02 against the anchor +2.6455.  Root cause
was NOT the evaluator and NOT the circle DFT (both reproduced correct standalone:
t1/t2/t3 identical across dps 60/70 x zcut 149.66/172.69/287.82; w_coeffs(0) at
dps 60 gives c2 = -18.8167792886, c4 = -279.1809, c6 = -1382.36, matching the
independent real-axis Richardson c2 = -18.8168).  v1 carried two definite bugs and
one open axis:

  FIX-1 (definite): the e-channel FD weights give d^l c/de^l * HE^l (stencil at
        e = HE*o); v1 divided only by l!, printing g01 = -1.78e-9 where the
        correct scaled value is -4.98e-8 (= dhe * HE).  Fixed: / (l! * HE^l).
  FIX-2 (definite): the closing control walked the heat86b JSON for dicts holding
        keys "eps"+"u"; the rungs are keyed BY the eps string.  Fixed: read
        res["rungs"] items directly.
  OPEN (this run measures it): v1's stencil tab values were ~1e-9-scale at
        dps 70 while identical calls at dps 60 are correct -- the g10 = 1.7e-9
        vs true c2 = -18.82 gap localises to the dps-70 circle evals.  v2 runs
        the same stencil under a channel witness that would have caught it:
        a real-axis c2 probe (even symmetric difference + Richardson, real
        Bessel orders only) is printed and compared to the circle-DFT c2 at
        e=0 BEFORE any scored-length compute; both are printed per config.

Method unchanged from v1 (m2-c32 s1.1 + s3(ii) as published in the LETTER):
xi_D(1/2+w) even in w; h(w,e) = G(w^2, e); g_jl by Cauchy contour in w on
|w|=r_w, FD in e; series-solve G(x,e)=0 for x(e) = Ae+Be^2+Ce^3+D4e^4;
u^2 = -x(e) with e = D - D*, so  a = -A, b = B, a3 = -C.  Sign anchor: a must
reproduce the ADOPTED operative 17-s.f. a = 2.6455214118116629.

Controls: (i) evenness d_w h|_0; (ii) fold residual h(0,0); (iii) |Im g_jl|;
(iv) CHANNEL WITNESS: real-axis c2 (Richardson) vs circle c2 at e=0 -- these
agree only if every arithmetic step between raw evals and printed constants
is right; (v) closing u-check against MY published heat86b rungs; (vi) a-anchor.
Nothing scored; determination measurement with stability certificate.
"""
import importlib.util
import json
import os
import time

from mpmath import (mp, mpf, mpc, pi, cos, sin, fabs, re, im,
                    gamma, zeta, sqrt, besselk)

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ORCH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator"
RUN72 = os.path.join(ORCH, "heat72_birth_locus.py")
H86B = os.path.join(ORCH, "heat86b_a_dispute_ladder.results.json")
OUT = os.path.join(HERE, "..", "machine1_der_route_a_b_a3_v2.out")

spec = importlib.util.spec_from_file_location("h72", RUN72)
h72 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h72)
DSTAR = h72.DSTAR

# published reference points (ECHOED from the exchange; compared, not consumed)
A17 = mpf("2.6455214118116629")                 # adopted 17 s.f.
B_HDR = mpf("-7.4624528767937415788")           # published header b
A3_HDR = mpf("11.70071732105115376305")         # published header a3 (m2 V2 ref)
M2_DER = {"a": mpf("2.6455214118116628680161261"),
          "b": mpf("-7.4624528767936862675335803"),
          "a3": mpf("11.700717320433667601156432")}
M2_LAD = {"b": mpf("-7.46245287679368626753358"),
          "a3": mpf("11.7007173204336676011627")}

MPDPS_RUN = int(os.environ.get("DER_DPS", "110"))
GUARD = int(os.environ.get("DER_GUARD", "10"))   # working dps = MPDPS_RUN + GUARD
RW = mpf(os.environ.get("DER_RW", "0.05"))
NW = int(os.environ.get("DER_NW", "28"))
HE = mpf(os.environ.get("DER_HE", "1e-16"))
NPTS = int(os.environ.get("DER_NPTS", "9"))
KX = 3      # x-orders: c_0, c_2, c_4, c_6  (g_{jl}, j<=3)
KE = 4      # e-orders: coefficients up to e^4 (D4 as stability witness)

# tail criterion: Bessel terms beyond zcut are < exp(-zcut); default dps+15 digits
ZCUT = mpf(os.environ.get("DER_ZCUT", str(float((MPDPS_RUN + 15) * mp.log(10)))))


def zeta2_C_deep(s, D):
    """heat72's zeta2_C with the tail criterion zcut = (dps+15) ln10.  Formula
    identical to the scored runner."""
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


def fd_weights(order, npts):
    offs = list(range(-(npts // 2), npts // 2 + 1))
    N = len(offs)
    Am = mp.matrix(N, N)
    for i, o in enumerate(offs):
        for j in range(N):
            Am[i, j] = mpf(o) ** j
    bv = mp.matrix(N, 1)
    bv[order] = mp.factorial(order)
    x = mp.lu_solve(Am, bv)
    return offs, [x[i] for i in range(N)]


def w_coeffs(e, kx=KX):
    """Even Taylor coefficients c_{2j}(e) of h(w,e) at w=0 via Cauchy/DFT on
    |w| = r_w."""
    acc = [mpc(0) for _ in range(kx + 1)]
    for n in range(NW):
        th = 2 * pi * mpf(n) / NW
        w = RW * mpc(cos(th), sin(th))
        f = h(w, e)
        for j in range(kx + 1):
            acc[j] += f * RW ** (-2 * j) * mpc(cos(-2 * j * th), sin(-2 * j * th))
    return [a / NW for a in acc]


def real_axis_c2():
    """CHANNEL WITNESS truth: c2 = h''(0)/2 by even symmetric difference at two
    hh + Richardson (real w, real Bessel orders -- independent of the circle
    path).  Returns (c2_rich, c2_hh1, c2_hh2)."""
    vals = {}
    for hh in (mpf("1e-2"), mpf("1e-3")):
        hp, hm = h(mpc(hh), mpf(0)), h(mpc(-hh), mpf(0))
        vals[hh] = (hp + hm) / (2 * hh ** 2)
    hh1, hh2 = mpf("1e-2"), mpf("1e-3")
    rich = vals[hh2] + (vals[hh2] - vals[hh1]) / ((hh1 / hh2) ** 2 - 1)
    return rich, vals[hh2], vals[hh1]


def main():
    mp.dps = MPDPS_RUN + GUARD
    print("m1 derivative route v2: dps=%d(+%d) r_w=%s N_w=%d h_e=%s npts=%d kx=%d ke=%d zcut=%s"
          % (MPDPS_RUN, GUARD, mp.nstr(RW, 4), NW, mp.nstr(HE, 4), NPTS, KX, KE, mp.nstr(ZCUT, 6)), flush=True)
    print("evaluator: heat72 zeta2_C formula, deep-tail zcut; D* = %s" %
          mp.nstr(DSTAR, 36), flush=True)

    # controls -------------------------------------------------------------
    hh = mpf("1e-8") * RW
    dev = (h(mpc(hh), mpf(0)) - h(mpc(-hh), mpf(0))) / (2 * hh)
    print("CTL evenness |d_w h|_0 = %s" % mp.nstr(fabs(dev), 6), flush=True)
    hh2 = mpf("1e-20")
    fr = (h(mpc(hh2), mpf(0)) + h(mpc(-hh2), mpf(0))) / 2
    print("CTL fold residual h(0,0) [even limit] = %s + %s i" % (mp.nstr(re(fr), 6), mp.nstr(im(fr), 6)), flush=True)

    # CHANNEL WITNESS (new in v2): real-axis c2 vs circle c2, printed BEFORE
    # the stencil -- the v1 failure was invisible to the controls above because
    # they sit upstream of the extraction arithmetic.
    c2_rich, c2_a, c2_b = real_axis_c2()
    print("WIT real-axis c2: hh=1e-3 %s | hh=1e-2 %s | Richardson %s" %
          (mp.nstr(c2_a, 14), mp.nstr(c2_b, 14), mp.nstr(c2_rich, 14)), flush=True)
    circ0 = w_coeffs(mpf(0))
    rel = (circ0[1] - c2_rich) / c2_rich
    print("WIT circle   c2 at e=0: %s   (circle - rich = %s, rel %s)" %
          (mp.nstr(circ0[1], 14), mp.nstr(circ0[1] - c2_rich, 6), mp.nstr(rel, 4)), flush=True)
    print("WIT circle   c4/c6 at e=0: %s / %s" % (mp.nstr(circ0[2], 12), mp.nstr(circ0[3], 12)), flush=True)
    if fabs(rel) > mpf("1e-6"):
        # Tolerance = the witness's OWN error budget: the real-axis Richardson
        # at hh=1e-3/1e-2 carries ~1e-8 relative truncation (measured: circle
        # -18.816779288625 vs rich -18.816779150332, rel 7.3e-9, with the circle
        # value independently confirmed to 12 s.f. by the dps-60/NW-28 probe);
        # v1-class channel corruption was O(1) relative.  1e-6 splits the two
        # regimes by two orders on each side.  (First gate attempt used 1e-20
        # and aborted a healthy run -- caught at minute 7 by the gate itself.)
        print("WITNESS-FAIL: circle c2 disagrees with real-axis Richardson c2 "
              "(rel %s) -- extraction channel corrupted; aborting before the "
              "stencil (v1's failure mode, now caught at the boundary)." % mp.nstr(rel, 4), flush=True)
        raise SystemExit(1)

    # stencil: c_{2j}(e) at the e-nodes, then e-derivatives at e=0 -----------
    st = NPTS // 2
    tab = {}
    for p in range(-st, st + 1):
        e = HE * p
        tab[p] = w_coeffs(e)
        print("  stencil e-node %+d done: c2(e) = %s  [%.0fs]" %
              (p, mp.nstr(tab[p][1], 14), time.time() - T0), flush=True)

    g = [[mpc(0)] * (KE + 1) for _ in range(KX + 1)]
    for l in range(KE + 1):
        offs, wts = fd_weights(l, NPTS)
        for j in range(KX + 1):
            # FIX-1: the stencil sits at e = HE*o, so the FD combination returns
            # d^l c / de^l * HE^l; divide it back out (v1 divided only by l!).
            g[j][l] = mp.fsum(w * tab[o][j] for o, w in zip(offs, wts)) / (mp.factorial(l) * HE ** l)

    maximag = max(fabs(im(g[j][l])) for j in range(KX + 1) for l in range(KE + 1)
                  if not (j == 0 and l == 0))
    print("CTL max |Im g_jl| (j,l != 0,0) = %s" % mp.nstr(maximag, 6), flush=True)
    print("g10 = %s   g01 = %s   g11 = %s   g02 = %s" %
          (mp.nstr(g[1][0], 30), mp.nstr(g[0][1], 30), mp.nstr(g[1][1], 30), mp.nstr(g[0][2], 30)), flush=True)
    print("a quick witness -(g01/g10) negated = %s  vs A17 %s (diff %s)" %
          (mp.nstr(-(-g[0][1] / g[1][0]), 16), mp.nstr(A17, 16),
           mp.nstr(-(-g[0][1] / g[1][0]) - A17, 6)), flush=True)

    # series solve G(x,e) = 0, x(e) = A e + B e^2 + C e^3 + D e^4 ------------
    def G(xv, ev):
        return mp.fsum(g[j][l] * xv ** j * ev ** l
                       for j in range(KX + 1) for l in range(KE + 1))

    A = -g[0][1] / g[1][0]
    B = -(g[2][0] * A ** 2 + g[1][1] * A + g[0][2]) / g[1][0]
    C = -(g[3][0] * A ** 3 + 2 * g[2][0] * A * B + g[2][1] * A ** 2
          + g[1][1] * B + g[1][2] * A + g[0][3]) / g[1][0]
    D4 = -(g[3][0] * (3 * A ** 2 * B) + g[2][0] * (B ** 2 + 2 * A * C)
           + g[3][1] * A ** 3 + g[2][1] * 2 * A * B + g[2][2] * A ** 2
           + g[1][1] * C + g[1][2] * B + g[1][3] * A + g[0][4]) / g[1][0]

    for ee in ("0.0001", "0.001", "0.01"):
        ev = mpf(ee)
        xv = A * ev + B * ev ** 2 + C * ev ** 3 + D4 * ev ** 4
        rres = G(xv, ev)
        print("  series-solve residual G(x(e),e) at e=%s: %s" % (ee, mp.nstr(fabs(rres), 6)), flush=True)

    a, b, a3 = -A, B, -C
    print("", flush=True)
    print("a  = %s" % mp.nstr(a, 30), flush=True)
    print("b  = %s" % mp.nstr(b, 30), flush=True)
    print("a3 = %s" % mp.nstr(a3, 30), flush=True)
    print("D4 witness = %s" % mp.nstr(D4, 20), flush=True)
    print("", flush=True)
    print("a  - A17(operative)      = %s" % mp.nstr(a - A17, 8), flush=True)
    print("a  - m2 der-route        = %s" % mp.nstr(a - M2_DER["a"], 8), flush=True)
    print("b  - header literal      = %s   (b wrong-from claim: +5.53113e-14)" % mp.nstr(b - B_HDR, 8), flush=True)
    print("b  - m2 der-route        = %s" % mp.nstr(b - M2_DER["b"], 8), flush=True)
    print("a3 - header literal      = %s   (a3 wrong-from claim: -6.17486e-10)" % mp.nstr(a3 - A3_HDR, 8), flush=True)
    print("a3 - m2 der-route        = %s" % mp.nstr(a3 - M2_DER["a3"], 8), flush=True)
    print("a3 - m2 ladder-free      = %s" % mp.nstr(a3 - M2_LAD["a3"], 8), flush=True)

    # closing control: predict MY OWN published ladder u's ------------------
    # FIX-2: heat86b's JSON stores rungs = {eps_string: {"u": ..., ...}} --
    # keyed BY the eps; read the dict directly instead of walking for
    # {"eps","u"} key-pairs that never exist in that shape.
    try:
        r86 = json.load(open(H86B))
        rungs = r86["rungs"]
        pub = {mpf(es): mpf(str(rd["u"])) for es, rd in sorted(rungs.items())
               if "u" in rd}
        if pub:
            print("", flush=True)
            for ev in sorted(pub)[:6]:
                u2p = -(A * ev + B * ev ** 2 + C * ev ** 3 + D4 * ev ** 4)
                u_p = mp.sqrt(u2p)
                print("closing e=%s: u_pred=%s u_pub=%s  du=%s (rel %s)" %
                      (mp.nstr(ev, 6), mp.nstr(u_p, 18), mp.nstr(pub[ev], 18),
                       mp.nstr(u_p - pub[ev], 6), mp.nstr((u_p - pub[ev]) / pub[ev], 6)), flush=True)
        else:
            print("closing control: no rungs with u found -- skipped", flush=True)
    except Exception as ex:
        print("closing control skipped: %s" % ex, flush=True)

    print("", flush=True)
    print("wall %.0fs; no proof claim; determination measurement, not scored" % (time.time() - T0), flush=True)
    with open(os.path.abspath(OUT), "w") as fh:
        fh.write("v2 dps=%d(+%d) r_w=%s N_w=%d h_e=%s npts=%d kx=%d ke=%d zcut=%s\n"
                 % (MPDPS_RUN, GUARD, mp.nstr(RW, 4), NW, mp.nstr(HE, 4), NPTS, KX, KE, mp.nstr(ZCUT, 6)))
        fh.write("witness: real-axis c2 rich %s | circle c2 %s (rel diff %s)\n" %
                 (mp.nstr(c2_rich, 14), mp.nstr(circ0[1], 14),
                  mp.nstr((circ0[1] - c2_rich) / c2_rich, 4)))
        fh.write("a  = %s\nb  = %s\na3 = %s\nD4witness = %s\n" %
                 (mp.nstr(a, 36), mp.nstr(b, 36), mp.nstr(a3, 36), mp.nstr(D4, 30)))
        fh.write("controls: evenness %s fold-res %s maximag %s\n" %
                 (mp.nstr(fabs(dev), 6), mp.nstr(fabs(fr), 6), mp.nstr(maximag, 6)))
        fh.write("a-A17 %s  a-m2der %s  b-hdr %s  b-m2der %s  a3-hdr %s  a3-m2der %s  a3-m2lad %s\n" %
                 (mp.nstr(a - A17, 8), mp.nstr(a - M2_DER["a"], 8), mp.nstr(b - B_HDR, 8),
                  mp.nstr(b - M2_DER["b"], 8), mp.nstr(a3 - A3_HDR, 8),
                  mp.nstr(a3 - M2_DER["a3"], 8), mp.nstr(a3 - M2_LAD["a3"], 8)))
        fh.write("wall %.0fs\n" % (time.time() - T0))


if __name__ == "__main__":
    main()
