#!/usr/bin/env python3
"""m2_c58_visible_rung_dps.py -- DOES THE VISIBLE TAIL SURVIVE THE DETECTOR REPAIR?

c57's A8 took ONE rung whose committed verdict was `nu = null` (x=42, even, N=100, rung 1) and showed
that the sealed detector's internal `mp.dps = 50` was MANUFACTURING 664 spurious sign changes on a
mode whose node count is 0.  That result is about a rung the detector REFUSED.

The whole of c58's A-arm -- the price of the residual at x=42 -- is computed from the node counts the
detector DID return, i.e. the VISIBLE tail.  Those counts were produced by the SAME dps-50 detector.
A8 says nothing about them.  So:

  IF the detector was wrong where it refused, the visible tail is not thereby trustworthy; it is
  UNTESTED.  Pricing a residual on an untested tail is exactly the c56 defect one layer up.

THE TEST.  Take the FIRST VISIBLE pooled position (selected by rule, not by hand -- pinned with an
exactly-one assertion, trap #177 and register #177's SELECTION-layer form), find its (parity, sector
rung), and run the SAME sealed detector on the SAME committed coefficients twice:

  (K) mp.dps = 50   : KNOWN-ANSWER control.  MUST reproduce the committed cell exactly.  Without it
                      a change at dps=200 could be a bug in this file rather than the detector.
                      If the KAT fails the measurement is VOID and is not run.
  (M) mp.dps = 200  : the measurement.  Registered prediction B1.

WHAT THIS DOES NOT DO.  One rung.  No node cell is written, no pooled table is rebuilt, no depth is
recomputed, no model is scored, p2 is not computed.  A single rung cannot move p1/p2/p3.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
C53 = os.path.abspath(os.path.join(HERE, "..", "c53"))
C55 = os.path.abspath(os.path.join(HERE, "..", "c55"))
C56 = os.path.abspath(os.path.join(HERE, "..", "c56"))
sys.path.insert(0, C53)
sys.path.insert(0, C55)
print("resolver: c53 dir = %s" % C53)
print("resolver: c56 dir = %s" % C56)
import m2_c53_spectrum as S53                    # sealed, imported, never edited
import m2_c55_score as S55                       # sealed, imported, never edited
from mpmath import mp, mpf

P, ND = S53.P, S53.ND
X, N, DPS = 42, 100, 300
CAP_SECONDS = 40 * 60


def pinned(dirname, name):
    hits = [f for f in sorted(os.listdir(dirname)) if f == name]
    assert len(hits) == 1, "selection is not unique for %s: %r" % (name, hits)
    return os.path.join(dirname, hits[0])


def one(dps, spec, rung_index, par):
    mp.dps = dps
    L = mpf(spec["L"])
    om, nr, _ = P.make_basis_parity(spec["N"], L, par)
    r = spec["rungs"][rung_index]
    coef = [mpf(c) for c in r["coef"]]
    t0 = time.time()
    counts, stable, nu = ND.count_all_knobs(coef, om, nr, L, par)
    nu_ref, lobe = ND.refine(coef, om, nr, L, par)
    return dict(dps=dps, rung=r["rung"], lam=r["lam"], log10=r["log10"],
                counts={k: v for k, v in counts.items()}, stable=bool(stable), nu=nu,
                nu_refine_48001=nu_ref,
                lobe_min_ratio=(None if lobe is None else mp.nstr(lobe, 6)),
                sturm=ND.sturm(par, r["rung"]), seconds=round(time.time() - t0, 1))


def main():
    t_start = time.time()
    nf = {p: pinned(C56, "m2_c56_nodes_%s_x%d_N%d_dps%d.json" % (p, X, N, DPS))
          for p in ("even", "odd")}
    tab, _cert, _fo = S55.pooled_table(nf)

    # SELECTION BY RULE: the first pooled position whose committed nu is not None.
    cands = [r for r in tab if r["nu"] is not None]
    assert cands, "no visible pooled position at this window"
    target = cands[0]
    PAR, RUNG = target["parity"], target["sector_rung"]
    print("target selected by rule: first visible pooled position p=%d -> parity=%s sector_rung=%d"
          % (target["p"], PAR, RUNG))

    spec = json.load(open(pinned(C56, "m2_c56_spec_%s_x%d_N%d_dps%d.json" % (PAR, X, N, DPS))))
    cell = json.load(open(nf[PAR]))
    idx = [i for i, r in enumerate(spec["rungs"]) if r["rung"] == RUNG]
    assert len(idx) == 1, "rung selection is not unique in the spectrum -- pin it (trap #177)"
    idx = idx[0]
    committed = [r for r in cell["rungs"] if r["rung"] == RUNG]
    assert len(committed) == 1, "committed rung selection is not unique"
    committed = committed[0]
    assert committed["nu"] is not None, "the selected rung is not VISIBLE -- selection rule broken"

    print("KNOWN-ANSWER control: re-running the detector at the SEALED dps=50 ...", flush=True)
    k = one(50, spec, idx, PAR)
    same = (k["nu"] == committed["nu"] and k["stable"] == committed["stable"]
            and k["nu_refine_48001"] == committed["nu_refine_48001"]
            and k["lobe_min_ratio"] == committed["lobe_min_ratio"])
    print("  committed: nu=%s stable=%s refine=%s lobe=%s"
          % (committed["nu"], committed["stable"], committed["nu_refine_48001"],
             committed["lobe_min_ratio"]), flush=True)
    print("  re-run   : nu=%s stable=%s refine=%s lobe=%s   (%.1fs)"
          % (k["nu"], k["stable"], k["nu_refine_48001"], k["lobe_min_ratio"], k["seconds"]),
          flush=True)
    print("  KAT: %s" % ("REPRODUCES" if same else "DOES NOT REPRODUCE -- measurement VOID"),
          flush=True)

    m = None
    if same and (time.time() - t_start) < CAP_SECONDS:
        print("\nMEASUREMENT: same coefficients, detector at mp.dps = 200 ...", flush=True)
        m = one(200, spec, idx, PAR)
        print("  nu=%s stable=%s refine=%s lobe=%s   (%.1fs)"
              % (m["nu"], m["stable"], m["nu_refine_48001"], m["lobe_min_ratio"], m["seconds"]),
              flush=True)

    if m is None:
        b1 = "UNRUN"
    else:
        b1 = "HELD" if m["nu"] == committed["nu"] else "REFUTED"

    out = dict(cycle=58, prediction="B1", registered_confidence=0.55,
               selection_rule=("the FIRST pooled position with a committed nu that is not None; "
                               "pinned with exactly-one assertions at both the spectrum and the "
                               "cell layer"),
               window=dict(x=X, parity=PAR, N=N, dps_spectrum=DPS, sector_rung=RUNG,
                           pooled_position=target["p"]),
               committed=dict(nu=committed["nu"], stable=committed["stable"],
                              nu_refine_48001=committed["nu_refine_48001"],
                              lobe_min_ratio=committed["lobe_min_ratio"]),
               known_answer_control=dict(dps=50, reproduces=bool(same), detail=k),
               measurement=m,
               B1_verdict=b1,
               B1_statement=("the committed (dps-50) node count at the first VISIBLE pooled "
                             "position is UNCHANGED when the same detector is re-run at dps=200"),
               scope=("ONE rung. No node cell written, no pooled table rebuilt, no depth "
                      "recomputed, no model scored, p2 not computed."),
               cap_seconds=CAP_SECONDS, wall_seconds=round(time.time() - t_start, 1))
    json.dump(out, open(os.path.join(HERE, "m2_c58_visible_rung_dps.json"), "w"), indent=1)
    print("\nB1: %s" % b1, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
