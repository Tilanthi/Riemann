"""
machine 2 (beast-atlas) CYCLE 21 -- RUNG A: independent scoring of m1's PRE-REGISTERED heat72
birth-locus prediction   r(eps) = (u^2 - (a - b*eps)*eps)/eps^3  in  [11, 13]
(prereg: machine1-prereg-heat72-birth-locus.md, commit 201f70a, scored grid NOT yet published).

Instrument: my own completed self-dual xi_D (see m2_zeta2_xi.py) -- a REAL 1-D root find on the
critical line, structurally different from m1's 2-D Newton on (Re F, Im F).

SCORING RULE FIXED BEFORE ANY NUMBER EXISTED -- see /shared/progress/rh-cycle21.md MILESTONE 1.
"""
import sys
import time
import mpmath as mp
from m2_zeta2_xi import Zeta2

DPS = 45
mp.mp.dps = DPS

# registry constants (m1's published operative set; three-machine confirmed Delta*)
DSTAR = mp.mpf("0.141733239663887191395415685084185024")
A_CONST = mp.mpf("2.645521411811663")
B_CONST = mp.mpf("-7.46245287679")
A3_ANCHOR = mp.mpf("11.7975")

GRID = ["0.001", "0.0011239031932557", "0.002", "0.0035", "0.006",
        "0.0082667603361", "0.012", "0.02", "0.035", "0.06", "0.1"]

ANCHORS = {  # published cross-receipts (the S1 gate)
    "0.0011239031932557": mp.mpf("0.054614584740162026"),
    "0.0082667603361": mp.mpf("0.149621445957926652"),
}


def first_online_zero(Z, t_guess, verbose=False):
    """First positive real root of xi_D(1/2+it). Bracket by sign change, then bisect+secant."""
    f = lambda t: mp.re(Z.xi(mp.mpf(0.5) + 1j * mp.mpf(t)))
    f0 = f(mp.mpf(10) ** (-12))          # sign at t -> 0+
    # expand a bracket around the law's guess
    lo = t_guess / 4
    hi = t_guess * 4
    flo = f(lo)
    if mp.sign(flo) != mp.sign(f0):
        hi = lo
        lo = mp.mpf(10) ** (-12)
        flo = f0
    else:
        fhi = f(hi)
        n = 0
        while mp.sign(flo) == mp.sign(fhi) and n < 40:
            lo, flo = hi, fhi
            hi = hi * mp.mpf("1.5")
            fhi = f(hi)
            n += 1
        if mp.sign(flo) == mp.sign(fhi):
            raise RuntimeError("no sign change found")
    root = mp.findroot(f, (lo, hi), solver="anderson", tol=mp.mpf(10) ** (-2 * DPS + 6))
    return mp.mpf(root.real if hasattr(root, "real") else root), f


def scan_extra_zeros(Z, t_lo, t_hi, n=160):
    """Count sign changes of xi on [t_lo,t_hi] -- m1's outcome-(b) second-pair probe."""
    f = lambda t: mp.re(Z.xi(mp.mpf(0.5) + 1j * mp.mpf(t)))
    ts = [t_lo + (t_hi - t_lo) * mp.mpf(i) / n for i in range(n + 1)]
    vals = [f(t) for t in ts]
    roots = []
    for i in range(n):
        if mp.sign(vals[i]) != mp.sign(vals[i + 1]):
            r = mp.findroot(f, (ts[i], ts[i + 1]), solver="anderson")
            roots.append(mp.mpf(r.real if hasattr(r, "real") else r))
    return roots


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "gate"
    print("# m2 cycle21 birth-locus, dps=%d" % DPS)
    print("# Delta* = %s" % mp.nstr(DSTAR, 36))
    rows = []
    for es in GRID:
        eps = mp.mpf(es)
        if mode == "gate" and es not in ANCHORS:
            continue
        D = DSTAR + eps
        t_law = mp.sqrt((A_CONST - B_CONST * eps) * eps + A3_ANCHOR * eps ** 3)
        t0 = time.time()
        Z = Zeta2(D, dps=DPS)
        u, f = first_online_zero(Z, t_law)
        el = time.time() - t0
        resid = f(u)
        r = (u ** 2 - (A_CONST - B_CONST * eps) * eps) / eps ** 3
        line = dict(eps=es, D=D, u=u, r=r, resid=resid, t=el, t_law=t_law)
        rows.append(line)
        tag = ""
        if es in ANCHORS:
            dev = abs(u - ANCHORS[es])
            tag = "  ANCHOR dev=%s %s" % (mp.nstr(dev, 5), "PASS" if dev < mp.mpf("5e-16") else "FAIL")
        print("eps=%-20s u=%s  r=%s  |xi(u)|=%s  %.1fs%s" %
              (es, mp.nstr(u, 25), mp.nstr(r, 12), mp.nstr(abs(resid), 3), el, tag))
    if mode != "gate":
        rs = [x["r"] for x in rows]
        eps_v = [mp.mpf(x["eps"]) for x in rows]
        med = sorted(rs)[len(rs) // 2]
        n = len(rs)
        mx = sum(eps_v) / n
        my = sum(rs) / n
        num = sum((eps_v[i] - mx) * (rs[i] - my) for i in range(n))
        den = sum((eps_v[i] - mx) ** 2 for i in range(n))
        slope = num / den
        dmax = max(eps_v) - min(eps_v)
        print("\n# median r = %s   min = %s   max = %s" %
              (mp.nstr(med, 10), mp.nstr(min(rs), 10), mp.nstr(max(rs), 10)))
        print("# slope = %s   |slope*dmax| = %s   0.25*|median| = %s   => outcome %s" %
              (mp.nstr(slope, 8), mp.nstr(abs(slope * dmax), 8), mp.nstr(mp.mpf("0.25") * abs(med), 8),
               "(a) r-constant" if abs(slope * dmax) < mp.mpf("0.25") * abs(med) else "(b) STRUCTURED"))
        inband = all(mp.mpf(11) <= x <= mp.mpf(13) for x in rs)
        print("# S2 VERDICT: %s  (band [11,13], %d/%d points inside)" %
              ("CONFIRMED" if inband else "REFUTED",
               sum(1 for x in rs if mp.mpf(11) <= x <= mp.mpf(13)), len(rs)))


if __name__ == "__main__":
    main()
