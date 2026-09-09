#!/usr/bin/env python3
"""m2_c57_detector_dps_probe.py -- c56's NAMED NEXT REPAIR, tested on ONE rung.

c56 measured that after the storage repair (STORE_SF 40 -> 120) the binding floor is no longer the
STORE at all: it is the DETECTOR's own working precision, a literal `mp.dps = 50` inside c53's
sealed `nodes()`, which no knob reaches.  Corroboration: at x=42 the bottom-rung lobe ratios come
back at ~1e-54, the scale of a dps-50 detector floor, not the 1e-120 scale of the store.

THE TEST.  Take ONE rung whose committed verdict is `nu = null` -- x=42, even, N=100, rung 1 -- and
run the SAME detector on the SAME committed coefficients twice:

  (K) mp.dps = 50   : must REPRODUCE the committed artefact exactly.  A dry run on a KNOWN ANSWER is
                      the only thing that tests the test; without it a change at dps 200 could be a
                      bug in this file rather than a property of the detector.
  (M) mp.dps = 200  : the measurement.  Registered prediction A8 (confidence 0.60): the rung becomes
                      a stable integer.

WHAT THIS DOES NOT DO.  It writes no node cell, it does not touch the sealed c53 module, it scores
no model, and one rung is not a spectrum: a single rung cannot move p1/p2/p3 and none is computed.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
C53 = os.path.abspath(os.path.join(HERE, "..", "c53"))
sys.path.insert(0, C53)
import m2_c53_spectrum as S53                    # sealed, imported, never edited
from mpmath import mp, mpf
P, ND = S53.P, S53.ND

SPEC = os.path.abspath(os.path.join(HERE, "..", "c56",
                                    "m2_c56_spec_even_x42_N100_dps300.json"))
CELL = os.path.abspath(os.path.join(HERE, "..", "c56",
                                    "m2_c56_nodes_even_x42_N100_dps300.json"))
PAR, RUNG = "even", 1
CAP_SECONDS = 45 * 60


def one(dps, spec, rung_index):
    mp.dps = dps
    L = mpf(spec["L"])
    om, nr, _ = P.make_basis_parity(spec["N"], L, PAR)
    r = spec["rungs"][rung_index]
    coef = [mpf(c) for c in r["coef"]]
    t0 = time.time()
    counts, stable, nu = ND.count_all_knobs(coef, om, nr, L, PAR)
    nu_ref, lobe = ND.refine(coef, om, nr, L, PAR)
    return dict(dps=dps, rung=r["rung"], lam=r["lam"], log10=r["log10"],
                counts={k: v for k, v in counts.items()}, stable=bool(stable), nu=nu,
                nu_refine_48001=nu_ref,
                lobe_min_ratio=(None if lobe is None else mp.nstr(lobe, 6)),
                sturm=ND.sturm(PAR, r["rung"]), seconds=round(time.time() - t0, 1))


def main():
    t_start = time.time()
    spec = json.load(open(SPEC))
    cell = json.load(open(CELL))
    idx = [i for i, r in enumerate(spec["rungs"]) if r["rung"] == RUNG]
    assert len(idx) == 1, "rung selection is not unique -- pin it (trap #177)"
    idx = idx[0]
    committed = [r for r in cell["rungs"] if r["rung"] == RUNG]
    assert len(committed) == 1, "committed rung selection is not unique"
    committed = committed[0]

    print("KNOWN-ANSWER control: re-running the detector at the SEALED dps=50 ...", flush=True)
    k = one(50, spec, idx)
    same = (k["nu"] == committed["nu"] and k["stable"] == committed["stable"]
            and k["nu_refine_48001"] == committed["nu_refine_48001"]
            and k["lobe_min_ratio"] == committed["lobe_min_ratio"])
    print("  committed: nu=%s stable=%s refine=%s lobe=%s"
          % (committed["nu"], committed["stable"], committed["nu_refine_48001"],
             committed["lobe_min_ratio"]), flush=True)
    print("  re-run   : nu=%s stable=%s refine=%s lobe=%s   (%.1fs)"
          % (k["nu"], k["stable"], k["nu_refine_48001"], k["lobe_min_ratio"], k["seconds"]),
          flush=True)
    print("  KAT: %s" % ("REPRODUCES -- the probe is measuring the detector, not itself"
                         if same else "DOES NOT REPRODUCE -- the measurement below is VOID"),
          flush=True)

    m = None
    if same and (time.time() - t_start) < CAP_SECONDS:
        print("\nMEASUREMENT: same coefficients, detector at mp.dps = 200 ...", flush=True)
        m = one(200, spec, idx)
        print("  nu=%s stable=%s refine=%s lobe=%s   (%.1fs)"
              % (m["nu"], m["stable"], m["nu_refine_48001"], m["lobe_min_ratio"], m["seconds"]),
              flush=True)

    a8 = ("UNRUN" if m is None else
          ("HELD" if (committed["nu"] is None and m["nu"] is not None and m["stable"])
           else "REFUTED"))
    out = dict(cycle=57, prediction="A8", registered_confidence=0.60,
               window=dict(x=42, parity=PAR, N=100, dps_spectrum=300, rung=RUNG),
               store_sf_of_the_source=120,
               committed=dict(nu=committed["nu"], stable=committed["stable"],
                              nu_refine_48001=committed["nu_refine_48001"],
                              lobe_min_ratio=committed["lobe_min_ratio"]),
               known_answer_control=dict(dps=50, reproduces=bool(same), detail=k),
               measurement=m, A8_verdict=a8,
               scope="ONE rung. No node cell is written, no model is scored, p2 is not computed.",
               cap_seconds=CAP_SECONDS, wall_seconds=round(time.time() - t_start, 1))
    json.dump(out, open(os.path.join(HERE, "m2_c57_detector_dps_probe.json"), "w"), indent=1)
    print("\nA8: %s" % a8, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
