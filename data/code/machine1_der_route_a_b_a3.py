#!/usr/bin/env python3
"""m1 -- the derivative route for a, b, a3 on MY evaluator (the c32 3.3 ask).

Fills the empty cell of the 2x2 (evaluator x method):
  ladder method:   m2-c30/c31 (their eval)      | m1-heat86b (my eval)
  derivative:      m2-c32 fold_series (their eval) | THIS RUN (my eval)

Method from m2-c32 section 1.1 + section 3(ii) as published in the LETTER (not
their code): xi_D(1/2+w) is even in w, so h(w,e) = G(w^2, e); extract G's
Taylor coefficients g_{jl} (Cauchy contour in w on |w|=r_w, finite differences
in e), series-solve G(x,e)=0 for x(e) = A e + B e^2 + C e^3 + D e^4, and read
  u^2 = -x(e)   with MY eps-convention e = D - D* (heat86b grid: DSTAR + eps):
  u^2 = a e - b e^2 + a3 e^3 - ...  =>  a = -A, b = B, a3 = -C.
Sign anchor (self-check): a must reproduce the ADOPTED 17-s.f. operative
a = 2.6455214118116629 (three instruments already agree on it).

Evaluator: zeta2_C imported byte-identical from the SCORED heat72 runner
(2-D-Newton Chowla-Selberg lineage; the same function heat86b's rungs used).
Declared shared input: the D* literal (same string as every instrument).

Controls: (i) evenness d_w h|_0; (ii) fold residual h(0,0); (iii) imaginary
parts of every extracted coefficient (must vanish -- free control); (iv) the
closing check u^2_pred(e) = -x(e) against MY OWN published ladder u's at the
six fine eps (heat86b results JSON) -- the derivative route must reproduce the
ladder it replaces; (v) a-anchor.  Nothing is scored; this is a determination
measurement with a stability certificate, not a preregistered band test.
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
OUT = os.path.join(HERE, "..", "machine1_der_route_a_b_a3.out")

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
RW = mpf(os.environ.get("DER_RW", "0.05"))
NW = int(os.environ.get("DER_NW", "28"))
HE = mpf(os.environ.get("DER_HE", "1e-16"))
NPTS = int(os.environ.get("DER_NPTS", "9"))
KX = 3      # x-orders: c_0, c_2, c_4, c_6  (g_{jl}, j<=3)
KE = 4      # e-orders: coefficients up to e^4 (D4 as stability witness)

# tail criterion: Bessel terms beyond zcut are < exp(-zcut); default dps+15 digits
# (DER_ZCUT overrides -- certificate run uses 115 = 50 ln10, tail 1e-50, enough
# for 1e-22-class coefficients with 28 digits of margin)
ZCUT = mpf(os.environ.get("DER_ZCUT", str(float((MPDPS_RUN + 15) * mp.log(10)))))


def zeta2_C_deep(s, D):
    """heat72's zeta2_C with the tail criterion zcut = (dps+15) ln10 (k-Bessel
    terms decay like exp(-2 pi D m k); the scored runner's fixed zcut=160 leaves
    a ~1e-70 tail, above the dps-100 working floor).  Formula identical."""
    nu = s - mpf("0.5")
    zcut = ZCUT + h72.ZCUT_A * (mpf(float(abs(im(s)))) ** 2)
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
    """Exact central FD weights for d^order/dx^order at 0 on npts points
    (stencil offsets -(npts//2)..+(npts//2)), by exact solve of the moment
    system.  Returns (offsets, weights)."""
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
    |w| = r_w.  One circle gives all j simultaneously (h even in w)."""
    acc = [mpc(0) for _ in range(kx + 1)]
    for n in range(NW):
        th = 2 * pi * mpf(n) / NW
        w = RW * mpc(cos(th), sin(th))
        f = h(w, e)
        for j in range(kx + 1):
            # c_k = (1/N) sum f(th_n) r^{-k} e^{-i k th_n}, k = 2j
            acc[j] += f * RW ** (-2 * j) * mpc(cos(-2 * j * th), sin(-2 * j * th))
    return [a / NW for a in acc]


def main():
    mp.dps = MPDPS_RUN + 10
    print("m1 derivative route: dps=%d r_w=%s N_w=%d h_e=%s npts=%d kx=%d ke=%d zcut=%s"
          % (MPDPS_RUN, mp.nstr(RW, 4), NW, mp.nstr(HE, 4), NPTS, KX, KE, mp.nstr(ZCUT, 6)), flush=True)
    print("evaluator: heat72 zeta2_C formula, deep-tail zcut; D* = %s" %
          mp.nstr(DSTAR, 36), flush=True)

    # controls -------------------------------------------------------------
    hh = mpf("1e-8") * RW
    dev = (h(mpc(hh), mpf(0)) - h(mpc(-hh), mpf(0))) / (2 * hh)
    print("CTL evenness |d_w h|_0 = %s" % mp.nstr(fabs(dev), 6), flush=True)
    # fold residual: h(0,0) hits mpmath's zeta(1) refusal exactly at s=1/2;
    # take the even limit (pole cancels between t1,t2 in the sum; ~20 digits
    # lost to cancellation at w=1e-20, ~90 remain at dps 110)
    hh2 = mpf("1e-20")
    fr = (h(mpc(hh2), mpf(0)) + h(mpc(-hh2), mpf(0))) / 2
    print("CTL fold residual h(0,0) [even limit] = %s + %s i" % (mp.nstr(re(fr), 6), mp.nstr(im(fr), 6)), flush=True)

    # stencil: c_{2j}(e) at the 9 e-nodes, then e-derivatives at e=0 ---------
    st = NPTS // 2
    tab = {}
    for p in range(-st, st + 1):
        e = HE * p
        tab[p] = w_coeffs(e)
        print("  stencil e-node %d/%d done [%.0fs]" % (p, st, time.time() - T0), flush=True)

    g = [[mpc(0)] * (KE + 1) for _ in range(KX + 1)]
    for l in range(KE + 1):
        offs, wts = fd_weights(l, NPTS)
        for j in range(KX + 1):
            g[j][l] = mp.fsum(w * tab[o][j] for o, w in zip(offs, wts)) / mp.factorial(l)

    maximag = max(fabs(im(g[j][l])) for j in range(KX + 1) for l in range(KE + 1)
                  if not (j == 0 and l == 0))
    print("CTL max |Im g_jl| (j,l != 0,0) = %s" % mp.nstr(maximag, 6), flush=True)
    print("g10 = %s   g01 = %s" % (mp.nstr(g[1][0], 30), mp.nstr(g[0][1], 30)), flush=True)

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

    # residual of the series solve at finite e (truncation witness)
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
    try:
        r86 = json.load(open(H86B))
        pub = {}
        s = json.dumps(r86)
        # heat86b stored six fine rungs; find (eps, u) pairs heuristically
        def walk(o):
            if isinstance(o, dict):
                if "eps" in o and "u" in o:
                    try:
                        pub[mpf(str(o["eps"]))] = mpf(str(o["u"]))
                    except Exception:
                        pass
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(r86)
        if pub:
            print("", flush=True)
            for ev in sorted(pub)[:6]:
                u2p = -(A * ev + B * ev ** 2 + C * ev ** 3 + D4 * ev ** 4)
                u_p = mp.sqrt(u2p)
                print("closing e=%s: u_pred=%s u_pub=%s  du=%s (rel %s)" %
                      (mp.nstr(ev, 6), mp.nstr(u_p, 18), mp.nstr(pub[ev], 18),
                       mp.nstr(u_p - pub[ev], 6), mp.nstr((u_p - pub[ev]) / pub[ev], 6)), flush=True)
        else:
            print("closing control: no (eps,u) pairs found in heat86b JSON -- skipped", flush=True)
    except Exception as ex:
        print("closing control skipped: %s" % ex, flush=True)

    print("", flush=True)
    print("wall %.0fs; no proof claim; determination measurement, not scored" % (time.time() - T0), flush=True)
    with open(os.path.abspath(OUT), "w") as fh:
        fh.write("dps=%d r_w=%s N_w=%d h_e=%s npts=%d kx=%d ke=%d zcut=%s\n"
                 % (MPDPS_RUN, mp.nstr(RW, 4), NW, mp.nstr(HE, 4), NPTS, KX, KE, mp.nstr(ZCUT, 6)))
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
