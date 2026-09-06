#!/usr/bin/env python3
"""m1 -- units check of the two dead header constants against MY published artefacts
(the c32 s3.3 ask, m1 side; BEAST s5 companion to the derivative route).

Nothing here is scored and nothing touches sealed inputs: it re-runs MY OWN published
heat86b fit path (lsq/poly_basis/r_of imported from the scored runner, byte-identical;
rung u values read from the published results JSON) and answers:

  Q1  Does the dead b (B_OP = -7.4624528767937415788, live -7.4624528767936862675335803,
      error b_hdr - b_live = -5.53113e-14) shift my published V1 c0 = -1.63339469783e-15?
      V1 basis is {eps^0..eps^6, eps^-2} -- NO eps^-1 term, so the contamination
      (-5.53113e-14)/eps is not in the span and leaks into c0 by its eps^-2
      projection coefficient.  Measured directly: fit the pure contamination as
      data through the same design.
  Q2  Does it shift my published a3 values (decisive refit cf[0] "19 s.f." and the
      six-alone c6[1])?  Measured directly: refit with b = B_OP vs b = live, same
      u, same nodes, same basis, subtract.
  Q3  Where does the settlement land once BOTH dead constants are replaced?
      c0 recomputed with a = A_USED (unchanged -- the ladder measures a_true-A_USED,
      this is its signal, not contamination) but b = live.  Does the V1 band
      ("m2-CONFIRMED" [-2.2e-15,-1.0e-15]) survive?  Does a_fix move?
  Q4  The r-columns themselves: per-rung shift -5.53113e-14/eps (absolute) -- the
      published r-values any consumer beyond ~10 s.f. inherits.

Answer format: every number printed VERIFIED-HERE (computed for this letter) from
the published runner + published results JSON + m2-c32's live literals (ECHOED).
"""
import importlib.util
import json
import os

from mpmath import mp, mpf

HERE = os.path.dirname(os.path.abspath(__file__))
ORCH = "/Users/gjw255/astrodata/SWARM/ASTRA-dev-main/Riemann/experiments/orchestrator"
RUN86 = os.path.join(ORCH, "heat86b_a_dispute_ladder.py")
RES86 = os.path.join(ORCH, "heat86b_a_dispute_ladder.results.json")
OUT = os.path.join(HERE, "..", "machine1_c32_units_check.out")

spec = importlib.util.spec_from_file_location("h86b", RUN86)
h86b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h86b)

# published / live literals (ECHOED from m2-c32 C5/C6; compared, not consumed)
B_LIVE = mpf("-7.4624528767936862675335803")   # m2-c32 derivative+ladder, 25-digit
B_HDR = mpf("-7.4624528767937415788")          # shared header (my B_OP, their header)
A3_LIVE = mpf("11.700717320433667601156432")
A3_HDR = mpf("11.70071732105115376305")

db = B_HDR - B_LIVE          # contamination carried by every r formed with the header
mp.dps = 60

res = json.load(open(RES86))
rungs = res["rungs"]
NEW_EPS = h86b.NEW_EPS
E11 = [mpf(e) for e, _ in h86b.L165_9A]
U11 = [mpf(u) for _, u in h86b.L165_9A]
U6 = [mpf(rungs[es]["u"]) for es in NEW_EPS]
E6 = [mpf(e) for e in NEW_EPS]
E17 = E6 + E11
U17 = U6 + U11

lsq, poly_basis, evalfit, r_of, A_USED, B_OP = (h86b.lsq, h86b.poly_basis, h86b.evalfit,
                                                h86b.r_of, h86b.A_USED, h86b.B_OP)

lines = []


def say(s):
    print(s, flush=True)
    lines.append(s)


say("m1 c32 units check -- dead-b/dead-a3 contamination of MY published heat86b numbers")
say("published: V1 c0 = %s (band %s), a_fix = %s" %
    (res["V1"]["c0"], res["V1"]["band"], res["V1"]["a_fix"]))
say("db = b_hdr - b_live = %s   (r-values carry db/eps)" % mp.nstr(db, 8))

# --- Q1: eps^-2 leakage of the pure 1/eps contamination into V1 c0 -------------
bas = poly_basis(6) + [lambda e: 1 / e ** 2]
cont = [db / e for e in E17]                     # pure contamination, no signal
c_cont = lsq(bas, E17, cont)
say("")
say("Q1  V1 c0 shift from dead b (fit of pure db/eps through the V1 design):")
say("    dc0 = %s" % mp.nstr(c_cont[7], 8))
c0_pub = mpf(res["V1"]["c0"])
c0_corr = lsq(bas, E17, [r_of(e, u, b=B_LIVE) for e, u in zip(E17, U17)])[7]
say("    c0 recomputed with b = live:  %s   (shift %s)" %
    (mp.nstr(c0_corr, 12), mp.nstr(c0_corr - c0_pub, 6)))
band = ("m2-CONFIRMED" if mpf("-2.2e-15") <= c0_corr <= mpf("-1.0e-15")
        else ("MINE-STANDS" if abs(c0_corr) <= mpf("3e-16") else "OPEN"))
say("    band with live b: %s  (published: %s)" % (band, res["V1"]["band"]))
a_fix_new = A_USED + c0_corr
a17 = mpf("2.6455214118116629")
say("    a_fix moves %s -> %s ; |a_fix_new - a17(operative)| = %s" %
    (res["V1"]["a_fix"], mp.nstr(a_fix_new, 20), mp.nstr(abs(a_fix_new - a17), 4)))

# --- Q2: a3 shift in the decisive refit and the six-alone fit ------------------
a_fix = mpf(res["V1"]["a_fix"])
say("")
say("Q2  a3 shifts from dead b (same u, same nodes, b_hdr vs b_live):")
for tag, E, U in (("decisive refit (a_fix, K=6..8)", E17, U17),
                  ("six new alone (K=3)", E6, U6)):
    if "six" in tag:
        b6 = [lambda e: 1 / e ** 2] + poly_basis(3)
        a3_hdr = lsq(b6, E, [r_of(e, u, b=B_HDR) for e, u in zip(E, U)])
        a3_liv = lsq(b6, E, [r_of(e, u, b=B_LIVE) for e, u in zip(E, U)])
        say("    %-34s a3(b_hdr) = %s" % (tag, mp.nstr(a3_hdr[1], 21)))
        say("    %-34s a3(b_live) = %s   shift %s" %
            ("", mp.nstr(a3_liv[1], 21), mp.nstr(a3_liv[1] - a3_hdr[1], 6)))
    else:
        for K in (6, 7, 8):
            a3h = lsq(poly_basis(K), E, [r_of(e, u, a=a_fix, b=B_HDR) for e, u in zip(E, U)])[0]
            a3l = lsq(poly_basis(K), E, [r_of(e, u, a=a_fix, b=B_LIVE) for e, u in zip(E, U)])[0]
            say("    %-34s K=%d a3(b_hdr) = %s" % (tag, K, mp.nstr(a3h, 19)))
            say("    %-42s a3(b_live) = %s   shift %s" %
                ("", mp.nstr(a3l, 19), mp.nstr(a3l - a3h, 6)))

say("")
say("    vs m2-c32 live a3 = %s ; dead header a3 = %s (a3_hdr - a3_live = %s)" %
    (mp.nstr(A3_LIVE, 25), mp.nstr(A3_HDR, 21), mp.nstr(A3_HDR - A3_LIVE, 8)))

# --- Q3/Q4: r-column shifts -----------------------------------------------------
say("")
say("Q4  per-rung r shift db/eps (absolute) and vs r scale:")
say("    eps=0.0001 : %s   (r ~ a3 ~ 11.7, rel ~ %s)" %
    (mp.nstr(db / mpf("0.0001"), 4), mp.nstr(abs(db / mpf("0.0001")) / mpf("11.7"), 3)))
say("    eps=0.001  : %s" % mp.nstr(db / mpf("0.001"), 4))
say("    eps=0.1    : %s" % mp.nstr(db / mpf("0.1"), 4))
say("")
say("nothing scored; published artefacts read-only; VERIFIED-HERE from published runner+JSON")

with open(os.path.abspath(OUT), "w") as fh:
    fh.write("\n".join(lines) + "\n")
