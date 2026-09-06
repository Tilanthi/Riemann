#!/usr/bin/env python3
"""m1 -- L176 window: the c34 s9 self-centring ask, on MY lineage.  v2.

v2 = v1 (sha256 45b93519776cae0c4c4bb792b3d071502766658202e05bdc4e95fbc36fadb1c1)
with ONE fix: the series-reversion triangular solve.  v1 lazily built the
x^j memo polynomials inside the n-loop at first touch -- at n=1, while X was
still all zeros -- so xpow[1] froze at all-zeros and xpow[j>=2] froze at the
zero polynomial; every g[j][l] row with j >= 2 was silently dropped from the
e^2+ equations (X1 was unaffected: its equation only legitimately involves
first-order g's, which is why v1's a came out exact while b/a3/a4 were wrong,
knob-independently, and WIT-3 carried an order-e^2 residual that v1's smoke
dismissed as truncation).  v2 rebuilds all xpow[j] fresh at the start of each
n-step -- X[m] for m < n are final by then, and X[m] >= n contributes only at
orders > n, so the rebuild is exact for the e^n equation.

Everything upstream of the reversion (evaluator, fd_weights, w_coeffs,
g-table extraction, witnesses WIT-1/2, Delta/prefactor, etilde, e_root,
identity) is byte-identical logic to v1; the additional change is that the
FULL g-table is printed and written to JSON (v1 printed only g00/g10/g01),
so the erratum's term inventory is machine-recorded.

Boundary (unchanged from v1's launch note): no import of any m2 code; the
reversion is derived BY MACHINE, not transcribed from any published closed
form.  Descent: machine1_der_route_a_b_a3_v3.py.  Dictionary (#147): e := D
- D_centre (m1/m3 direction, = -e(m2)); x(e) = w^2(e) solves G(x,e)=0;
u^2 = -x(e); L141 formula u^2 = (a - b*eps)*eps + a3*eps^3 + a4*eps^4 +
a5*eps^5 with eps = e gives a = -X1, b = X2, a3 = -X3, a4 = -X4, a5 = -X5.
"""
import importlib.util
import json
import os
import time

from mpmath import mp, mpf, mpc, pi, cos, sin, fabs, re, im, sqrt, gamma, zeta, besselk

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ORCH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator"
RUN72 = os.path.join(ORCH, "heat72_birth_locus.py")
OUTJ = os.path.join(HERE, "..", "..", "data", "machine1_L176_selfcentring_v2.json")
OUTT = os.path.join(HERE, "..", "..", "data", "machine1_L176_selfcentring.out")

spec = importlib.util.spec_from_file_location("h72", RUN72)
h72 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h72)

DST_OP = "0.141733239663887191395415685084185024"     # h72.DSTAR's exact literal
# (h72 parses at its own dps=130; v3's import therefore carried the full
# literal -- captured here as the string so every cfg rebuilds it after the
# dps raise, #146.  mpf(DST_OP) == h72.DSTAR exactly.)
DST_M2 = ("0.14173323966388719139541568508418502362314456195501665594"
          "286660394665904218970743")            # m2 c34 dps-150 refined, 77 digits

# acceptance-check anchors (ECHOED committed strings; compared, not consumed)
V3_ANCHORS = {"a": "2.64552141181166079036703582773993027",
              "b": "-7.46245287679360120222517372996362553",
              "a3": "11.7007173204313486662476372807001087",
              "D4": "14725.6521755469360386231717695"}
M2_CFGA = {"g00": "-5.316911983139663491615228e-44",
           "g10": "-14.16808467075497560605419228419387228304",
           "g01": "37.48197136084288173875936239044685802487",
           "etilde": "1.41852517093e-45"}

CONFIGS = [
    # name, dps, guard, r_w, N_w, h_e, npts, KX, KE, centre, hhw
    # hhw: the real-axis probe half-step for the even limit h0(e).  Never 0
    # (zeta(1) pole in t1, cancelled only in the sum), and sized so that
    # (i) hh^2*|c2| stays below the smallest Delta probed and (ii) the
    # t1/t2 pole cancellation 1/hhw * 10^-(dps+guard) stays below it too:
    #   R    Delta ~ 4e-16  -> 1e-40 (err 1e-30 at working 70)
    #   A/B  Delta ~ 5e-44/1.9e-26 -> 1e-40 (err 1e-65 at working 105)
    #   N64  Delta ~ 4e-64  -> dps 95(+15)=110, hhw 1e-35 (err 1e-75)
    ("R",   60, 10, "0.05", 16, "1e-9",  9, 3, 4, "OP", "1e-40"),
    ("A",   90, 15, "0.04", 40, "1e-7", 11, 5, 5, "M2", "1e-40"),
    ("B",   90, 15, "0.04", 24, "1e-7", 11, 5, 5, "M2", "1e-40"),
    ("N64", 95, 15, "0.05", 64, "1e-9",  9, 5, 5, "OP", "1e-35"),
]


def zeta2_C_deep(s, D, zcut_base):
    """heat72's zeta2_C formula, deep-tail criterion (v3 lineage)."""
    nu = s - mpf("0.5")
    zcut = zcut_base + h72.ZCUT_A * (mpf(float(fabs(im(s)))) ** 2)
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


def fd_weights(order, npts):
    offs = list(range(-(npts // 2), npts // 2 + 1))
    N = len(offs)
    Am = mp.matrix(N, N)
    for i in range(N):
        for j in range(N):
            Am[i, j] = mpf(offs[j]) ** i
    bv = mp.matrix(N, 1)
    bv[order] = mp.factorial(order)
    x = mp.lu_solve(Am, bv)
    return offs, [x[i] for i in range(N)]


def polymul(p, q, kmax):
    r = [mpc(0)] * (kmax + 1)
    for i, pi in enumerate(p):
        if pi == 0:
            continue
        for j, qj in enumerate(q):
            if qj == 0 or i + j > kmax:
                continue
            r[i + j] += pi * qj
    return r


def run_cfg(name, dps, guard, rw_s, nw, he_s, npts, kx, ke, centre_kind, hhw_s, smoke=False):
    mp.dps = dps + guard
    RW = mpf(rw_s)
    NW = int(nw)
    HE = mpf(he_s)
    HHW = mpf(hhw_s)
    ZCUT_BASE = mpf(float((dps + 15) * mp.log(10)))
    # #146: centre rebuilt from string AFTER the dps raise
    centre = mpf(DST_OP) if centre_kind == "OP" else mpf(DST_M2)

    def h(w, e):
        return zeta2_C_deep(mpc(mpf("0.5")) + w, centre + e, ZCUT_BASE)

    def h0(e):
        # h(0,e) via the even limit -- w=0 exactly hits the zeta(1) pole in
        # t1 which only t2's gamma pole cancels in the sum; v3 probed the
        # same way and never evaluated w=0.
        return (h(mpc(HHW), e) + h(mpc(-HHW), e)) / 2

    print("\n########## cfg %s [v2]: dps=%d(+%d) r_w=%s N_w=%d h_e=%s npts=%d kx=%d ke=%d centre=%s hhw=%s"
          % (name, dps, guard, rw_s, NW, he_s, npts, kx, ke, centre_kind, hhw_s), flush=True)

    # WIT-2: FD exactness on a polynomial of degree npts-1 (the stencil's
    # exactness span -- v3 used degree 8 at npts=9; a degree above the span
    # fires the witness correctly, as the smoke run demonstrated)
    poly = [mpf(k + 3) / mpf(7 ** (k % 5)) for k in range(npts)]
    worst = mpf(0)
    for order in range(ke + 1):
        offs, wts = fd_weights(order, npts)
        est = mp.fsum(w * mp.fsum(c * mpf(o) ** k for k, c in enumerate(poly))
                      for o, w in zip(offs, wts))
        worst = max(worst, fabs(est - mp.factorial(order) * poly[order]))
    tol2 = mpf(10) ** (-(dps - 15))
    print("WIT-2 FD poly exactness orders 0..%d: worst %s (tol %s)" % (ke, mp.nstr(worst, 4), mp.nstr(tol2, 4)), flush=True)
    if worst > tol2:
        print("WITNESS-2 FAIL -- aborting cfg", flush=True)
        return None

    def w_coeffs(e):
        acc = [mpc(0)] * (kx + 1)
        for n in range(NW):
            th = 2 * pi * mpf(n) / NW
            w = RW * mpc(cos(th), sin(th))
            f = h(w, e)
            for j in range(kx + 1):
                acc[j] += f * RW ** (-2 * j) * mpc(cos(-2 * j * th), sin(-2 * j * th))
        return [a / NW for a in acc]

    def h00_direct():
        return h0(mpf(0))

    # ---- G(0,0) analogue + aliasing law ------------------------------------
    h00d = h00_direct()
    circ0 = w_coeffs(mpf(0))
    c0_dft = circ0[0]
    delta = c0_dft - h00d
    two_rw_pow = (2 * RW) ** NW
    pref = delta / two_rw_pow
    print("h(0,0) direct(even-limit) = %s" % mp.nstr(h00d, 30), flush=True)
    print("c_0 (DFT mean)            = %s" % mp.nstr(c0_dft, 30), flush=True)
    print("Delta = c_0 - h(0,0)      = %s" % mp.nstr(delta, 30), flush=True)
    print("(2 r_w)^N_w               = %s" % mp.nstr(two_rw_pow, 20), flush=True)
    print("prefactor Delta/(2r_w)^Nw = %s   [strong form -4]" % mp.nstr(pref, 24), flush=True)

    # WIT-1: circle c2 vs real-axis Richardson --------------------------------
    vals = {}
    for hh in (mpf("1e-2"), mpf("1e-3")):
        hp, hm = h(mpc(hh), mpf(0)), h(mpc(-hh), mpf(0))
        vals[hh] = (hp + hm) / (2 * hh ** 2)
    rich = vals[mpf("1e-3")] + (vals[mpf("1e-3")] - vals[mpf("1e-2")]) / ((mpf("1e-2") / mpf("1e-3")) ** 2 - 1)
    rel1 = (circ0[1] - rich) / rich
    print("WIT-1 circle c2 rel-to-Richardson = %s (tol 1e-6)" % mp.nstr(rel1, 4), flush=True)
    if fabs(rel1) > mpf("1e-6"):
        print("WITNESS-1 FAIL -- aborting cfg", flush=True)
        return None

    # ---- e-stencil and g-table ----------------------------------------------
    st = npts // 2
    tab = {}
    for p in range(-st, st + 1):
        tab[p] = w_coeffs(HE * p)
        print("  stencil node %+d: c2 = %s  [%.0fs]" % (p, mp.nstr(tab[p][1], 14), time.time() - T0), flush=True)

    g = [[mpc(0)] * (ke + 1) for _ in range(kx + 1)]
    for l in range(ke + 1):
        offs, wts = fd_weights(l, npts)
        for j in range(kx + 1):
            g[j][l] = mp.fsum(w * tab[o][j] for o, w in zip(offs, wts)) / (mp.factorial(l) * HE ** l)
    maximag = max(fabs(im(g[j][l])) for j in range(kx + 1) for l in range(ke + 1)
                  if not (j == 0 and l == 0))
    print("CTL max |Im g| (j,l!=0,0) = %s" % mp.nstr(maximag, 6), flush=True)
    print("g[0][0] = %s" % mp.nstr(g[0][0], 24), flush=True)
    print("g[1][0] = %s" % mp.nstr(g[1][0], 40), flush=True)
    print("g[0][1] = %s" % mp.nstr(g[0][1], 40), flush=True)
    # v2 addition: the FULL g-table, printed and JSON'd (the erratum's
    # term inventory is then machine-recorded, not hand-transcribed)
    print("g-table full (row j, cols l=0..%d):" % ke, flush=True)
    for j in range(kx + 1):
        print("  g[%d] = %s" % (j, "  ".join(mp.nstr(g[j][l], 24) for l in range(ke + 1))), flush=True)

    # ---- machine reversion: x(e) = sum X_k e^k solving G(x,e)=0 -------------
    # v2 FIX: rebuild all x^j powers fresh at each n.  X[m] for m < n are
    # final; X[m] >= n contributes to x^j only at orders > n (any product
    # containing X_n has another factor of order >= 1), so the rebuild is
    # exact for the e^n equation.  v1's lazy one-time build froze xpow[1]
    # at zeros and xpow[j>=2] at the zero polynomial (first touch at n=1
    # while X was all zeros), dropping every j>=2 g-row from e^2+ on.
    KORD = ke
    X = [mpc(0)] * (KORD + 1)
    for n in range(1, KORD + 1):
        xpow = [None] * (kx + 1)
        xpow[0] = [mpc(1)] + [mpc(0)] * KORD
        for j in range(1, kx + 1):
            xpow[j] = polymul(xpow[j - 1], X, KORD)
        rest = mpc(0)
        for j in range(kx + 1):
            for l in range(ke + 1):
                m = n - l
                if m < 0 or g[j][l] == 0:
                    continue
                if j == 1 and l == 0:
                    continue                       # the g[1][0]*X_n term, solved for
                rest += g[j][l] * xpow[j][m]
        X[n] = -rest / g[1][0]
    a, b, a3 = -X[1], X[2], -X[3]
    a4, a5 = (-X[4] if KORD >= 4 else None), (-X[5] if KORD >= 5 else None)
    print("a  = %s" % mp.nstr(a, 44), flush=True)
    print("b  = %s" % mp.nstr(b, 44), flush=True)
    print("a3 = %s" % mp.nstr(a3, 44), flush=True)
    if a4 is not None:
        print("a4 = %s   [m1 eps-basis, L141 formula]" % mp.nstr(a4, 44), flush=True)
    if a5 is not None:
        print("a5 = %s   [m1 eps-basis, L141 formula]" % mp.nstr(a5, 44), flush=True)
    if KORD >= 4:
        print("X4 raw (the v3 'D4' slot, now full-support) = %s" % mp.nstr(X[4], 30), flush=True)

    # WIT-3: reversion residual G(x(e), e) at probe points --------------------
    def G(xv, ev):
        return mp.fsum(g[j][l] * xv ** j * ev ** l for j in range(kx + 1) for l in range(ke + 1))
    for ee in ("0.001", "0.0001"):
        ev = mpf(ee)
        xv = mp.fsum(X[k] * ev ** k for k in range(KORD + 1))
        print("WIT-3 resid G(x(e),e) at e=%s: %s" % (ee, mp.nstr(fabs(G(xv, ev)), 6)), flush=True)

    # ---- recentring shift etilde (Newton on the c_0(e) series) --------------
    def c0_series(t):
        return mp.fsum(g[0][l] * t ** l for l in range(ke + 1))
    et = -g[0][0] / g[0][1]
    for _ in range(8):
        f0 = c0_series(et)
        d1 = mp.fsum(g[0][l] * l * et ** (l - 1) for l in range(1, ke + 1))
        step = f0 / d1
        et -= step
        if fabs(step) < fabs(et) * mpf(10) ** (-(dps + guard - 10)):
            break
    print("etilde (recentring shift, c_0 series root) = %s" % mp.nstr(et, 40), flush=True)
    print("implied D* = centre + etilde = %s" % mp.nstr(centre + et, 60), flush=True)

    # ---- direct root e_root (Newton on h0(e), the FUNCTION via even limit) --
    # the derivative probe dd must clear the even-limit pole-cancellation
    # noise ~ 10^(log10(1/hhw) - dps - guard): f' * 2dd >> that, so
    # dd = 10^-(guard+5) (1e-15 at R, 1e-20 at A/B/N64).
    er = mpf(0)
    dd = mpf(10) ** (-(guard + 5))
    for _ in range(60):
        f0 = h0(er)
        d1 = (h0(er + dd) - h0(er - dd)) / (2 * dd)
        if d1 == 0:
            print("e_root: derivative probe vanished below noise -- stopping", flush=True)
            break
        step = f0 / d1
        er = (er - step).real  # keep er real: h0's residual imaginary is noise
        if fabs(step) < mpf(10) ** (-(dps - 5)):
            break
    print("e_root (direct h(0,e) Newton)            = %s" % mp.nstr(er, 40), flush=True)
    print("root D* = centre + e_root = %s" % mp.nstr(centre + er, 60), flush=True)
    ident_lhs = et - er
    ident_rhs = -delta / g[0][1]
    print("identity: etilde - e_root = %s   vs  -Delta/g[0][1] = %s   ratio = %s"
          % (mp.nstr(ident_lhs, 24), mp.nstr(ident_rhs, 24),
             mp.nstr(ident_lhs / ident_rhs, 12)), flush=True)

    # ---- acceptance checks (labels: these compare against published strings) -
    acc = {}
    if name == "R":
        for kk, v in (("a", a), ("b", b), ("a3", a3), ("D4", X[4])):
            d = (re(v) - mpf(V3_ANCHORS[kk])) / fabs(mpf(V3_ANCHORS[kk]))
            acc["v3_" + kk] = mp.nstr(d, 4)
            print("ACCEPT v3 %s rel diff = %s" % (kk, mp.nstr(d, 4)), flush=True)
    if name == "A":
        for kk, v in (("g00", g[0][0]), ("g10", g[1][0]), ("g01", g[0][1])):
            d = (v - mpc(M2_CFGA[kk])) / mpc(M2_CFGA[kk])
            acc["m2_" + kk] = mp.nstr(d, 6)
            print("ACCEPT m2 cfgA %s rel diff = %s" % (kk, mp.nstr(d, 6)), flush=True)
        d = (et - mpf(M2_CFGA["etilde"])) / mpf(M2_CFGA["etilde"])
        acc["m2_etilde"] = mp.nstr(d, 6)
        print("ACCEPT m2 cfgA etilde rel diff = %s" % mp.nstr(d, 6), flush=True)

    c6 = circ0[3] if kx >= 3 else None
    print("c2/c4/c6/c8/c10 at e=0: %s / %s / %s / %s / %s"
          % (mp.nstr(circ0[1], 20), mp.nstr(circ0[2], 20),
             mp.nstr(c6, 20) if c6 is not None else "n/a",
             mp.nstr(circ0[4], 20) if kx >= 4 else "n/a",
             mp.nstr(circ0[5], 20) if kx >= 5 else "n/a"), flush=True)

    res = {"cfg": name, "dps": dps, "guard": guard, "r_w": rw_s, "N_w": NW,
           "h_e": he_s, "npts": npts, "kx": kx, "ke": ke, "centre": centre_kind,
           "h00_direct": mp.nstr(h00d, 60), "c0_dft": mp.nstr(c0_dft, 60),
           "delta": mp.nstr(delta, 60), "prefactor": mp.nstr(pref, 40),
           "g00": mp.nstr(g[0][0], 50), "g10": mp.nstr(g[1][0], 50),
           "g01": mp.nstr(g[0][1], 50),
           "g_table": [[mp.nstr(g[j][l], 40) for l in range(ke + 1)] for j in range(kx + 1)],
           "a": mp.nstr(a, 50), "b": mp.nstr(b, 50), "a3": mp.nstr(a3, 50),
           "a4": mp.nstr(a4, 50) if a4 is not None else None,
           "a5": mp.nstr(a5, 50) if a5 is not None else None,
           "X4_raw": mp.nstr(X[4], 40) if KORD >= 4 else None,
           "etilde": mp.nstr(et, 50), "e_root": mp.nstr(er, 50),
           "implied_Dstar": mp.nstr(centre + et, 80),
           "root_Dstar": mp.nstr(centre + er, 80),
           "ident_ratio": mp.nstr(ident_lhs / ident_rhs, 15),
           "c6": mp.nstr(c6, 40), "wit1_rel": mp.nstr(rel1, 4),
           "wit2_worst": mp.nstr(worst, 4), "maximag": mp.nstr(maximag, 6),
           "accept": acc, "wall_s": round(time.time() - T0, 1)}
    print("cfg %s done [%.0fs] (v2 fixed reversion)" % (name, time.time() - T0), flush=True)
    return res


def main():
    import sys
    smoke = os.environ.get("L176_SMOKE", "0") == "1"
    names = [a for a in sys.argv[1:] if a in {c[0] for c in CONFIGS}]
    sel = [c for c in CONFIGS if (not names) or (c[0] in names)]
    suffix = "".join(n.lower() for n in names) if names else "all"
    outj = OUTJ.replace(".json", "_%s.json" % suffix)
    results = []
    if smoke:
        r = run_cfg("SMOKE", 25, 5, "0.05", 8, "1e-4", 5, 2, 3, "OP", "1e-17", smoke=True)
        results.append(r)
    else:
        for cfg in sel:
            r = run_cfg(*cfg[:11])
            if r is None:
                print("ABORT at cfg %s -- witness failure" % cfg[0], flush=True)
                break
            results.append(r)
    with open(os.path.abspath(outj), "w") as fh:
        json.dump(results, fh, indent=1)
    with open(os.path.abspath(OUTT), "a") as fh:
        fh.write("run complete (%s, v2): %d cfgs, wall %.0fs; no proof claim; "
                 "determination measurement, not scored\n"
                 % (suffix, len(results), time.time() - T0))
    print("run complete: %d cfgs, wall %.0fs (v2)" % (len(results), time.time() - T0), flush=True)


if __name__ == "__main__":
    main()
