#!/usr/bin/env python3
"""m2_c56_score_gated.py -- SIBLING repair of a defect in THIS CYCLE'S OWN SEALED GRADER, found by
reading the sealed grader against the prereg it was written to enforce.

THE DEFECT.  `m2_c56_score.py` computes `p2 = _first_leave(seq, 2)` BEFORE it knows whether the
trust gate passed, stores it, and prints it.  The prereg's section 7 says the raw index "is NOT
quoted as an integer" when the gate fails -- but section 0 says what actually burned x = 22 and
x = 25: not the quoting, THE AUTHOR SEEING IT.  A rule against publishing a number does not protect
a window; only a rule against COMPUTING it does.  The sealed grader would have shown me p2 at x = 42
on a failed gate -- the exact c55 error, inside the file written to prevent it.

⇒ ERRATUM against our own prereg section 7, and the repair is an ADDITION, never an edit: the seal
and the sealed grader stand as they are.  This sibling evaluates the GATE FIRST and, if the gate
fails, REFUSES TO COMPUTE p1, p2, p3 or the pooled delta sequence at all.

DIRECTION CHECK: this sibling can only REMOVE information from the record.  It cannot bank anything,
cannot refute a model and cannot move a number.  A repair that can only weaken its author's claim is
the only kind that may be made after the data exist.

PLANTED CONTROL (a gate is indistinguishable from a loosening without a planted failure): the same
gated routine is run on a SYNTHETIC cell set with sufficient depth and no holes, and it must still
compute and report p2.  If the gate simply refused always, the control would catch it.

WHAT REMAINS VISIBLE when the gate fails, and why it is safe: hole positions, lobe ratios and
stability flags are INSTRUMENT quantities (M1/M2) and cannot yield p2, because p2 is an index into a
pooled ladder whose BOTTOM is missing -- with rungs 1..6 unmeasured there is no prefix to count from.

usage: m2_c56_score_gated.py            -> m2_c56_scores_gated.json
"""
import json, os, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m2_c56_score as G                       # the sealed c56 grader, IMPORTED, never edited
S55 = G.S55


def gate_first(nodefiles100, nodefiles180, floor_live=G.TRUST_FLOOR_LIVE):
    have100 = all(os.path.exists(f) for f in nodefiles100.values())
    have180 = all(os.path.exists(f) for f in nodefiles180.values())
    if not (have100 and have180):
        return dict(passed=False, depth=None, reason="node cells missing", holes=None)
    depth, det = S55.n_control_depth(nodefiles100, nodefiles180)
    holes = 0
    for fs in (nodefiles100, nodefiles180):
        for f in fs.values():
            holes += sum(1 for r in json.load(open(f))["rungs"] if r["nu"] is None)
    return dict(passed=bool(depth >= floor_live), depth=depth, detail=det, holes=holes,
                registered_floor=floor_live)


def planted_control():
    """synthetic cells with full agreement and no holes -- the gate MUST pass and p2 MUST appear.

    🔴 THIS CONTROL FAILED ON ITS FIRST RUN AND THE FAILURE WAS MISATTRIBUTED, WHICH IS WHY IT IS
    WORTH READING.  It printed "DEAD -- the gate refuses everything" while the artefact recorded
    `gate_passed: true, depth: 29`.  The gate was fine; the synthetic `nu` values simply never
    produced a pooled delta of 2, so `p2` came back None, and a COMPOUND verdict
    (`passed and p2 is not None`) blamed the wrong conjunct.  ⇒ A COMPOUND CONTROL MUST REPORT ITS
    CONJUNCTS SEPARATELY, or a failure in one is read as a failure in the other -- and here it would
    have discredited the very gate that licenses this cycle's UNMEASURED verdict.  Both assertions
    are now reported independently.  Same shape as the C4 finding, third occurrence today.
    """
    import tempfile
    # target POOLED delta sequence; pooled order alternates even, odd by construction below
    D = [0, 0, 0, 0, 0, 2, 2, 2, 4, 4, 6, 6, 8, 8, 10, 10, 12, 12, 14, 14,
         16, 16, 18, 18, 20, 20, 22, 22, 24, 24]          # p1 = 6, p2 = 9
    tmp = tempfile.mkdtemp()
    files = {}
    for N in (100, 180):
        d = {}
        for par in ("even", "odd"):
            # pooled index p of sector rung i+1: 2i+1 for even, 2i+2 for odd. nu = D[p-1] + (p-1)
            rungs = []
            for i in range(15):
                pp = 2 * i + (1 if par == "even" else 2)
                rungs.append(dict(rung=i + 1, nu=D[pp - 1] + (pp - 1),
                                  log10=str(-100 + 8 * i + (0 if par == "even" else 4)),
                                  delta=0, lam="1", stable=True, lobe_min_ratio="0.5",
                                  admitted=True, nu_refine_48001=0))
            p = os.path.join(tmp, "n_%s_%d.json" % (par, N))
            json.dump(dict(x=42, N=N, parity=par, rungs=rungs), open(p, "w"))
            d[par] = p
        files[N] = d
    g = gate_first(files[100], files[180], floor_live=5)
    p2 = None
    if g["passed"]:
        tab, _, _ = S55.pooled_table(files[100])
        p2 = S55._first_leave([r["pooled_delta"] for r in tab], 2)
    return dict(
        assertion_1_gate_admits_a_sufficient_cell=dict(
            gate_passed=g["passed"], depth=g["depth"],
            verdict=("FIRES -- the gate is not a blanket refusal" if g["passed"]
                     else "DEAD -- the gate refuses even a synthetic sufficient cell")),
        assertion_2_p2_is_computed_when_the_gate_passes=dict(
            p2_computed=p2, expected=9,
            verdict=("FIRES -- p2 = %s as planted" % p2 if p2 == 9
                     else "DEAD -- p2 not recovered from a planted ladder (p2=%s)" % p2)),
        note="conjuncts reported separately: a compound verdict blamed the wrong one on run 1")


def main():
    n100, n180 = G._nodefiles(100), G._nodefiles(180)
    g = gate_first(n100, n180)
    out = dict(cycle=56, window=dict(x=G.X, dps=G.DPS, gl=G.GL, R=G.R, store_sf=120),
               erratum=("against our own prereg sec 7: it forbade QUOTING the untrusted index and "
                        "that is not enough. Section 0's own reason is that the author SEEING it is "
                        "what spends a window. This sibling refuses to COMPUTE it."),
               trust_gate=g, planted_control=planted_control())
    if g["passed"]:
        out["note"] = "gate PASSED -- the sealed grader m2_c56_score.py is authoritative; run it."
        out["VERDICT"] = "GATE PASSED -- see m2_c56_scores.json"
    else:
        out["p1_p2_p3"] = "NOT COMPUTED"
        out["pooled_delta_sequence"] = "NOT COMPUTED"
        out["VERDICT"] = ("UNMEASURED at x=42 -- the N-control trusted depth is %s against a "
                          "registered floor of %s, so no model is scored, and p2 is NOT COMPUTED "
                          "rather than merely not quoted. x=42 is left UNSPENT for a future cycle."
                          % (g["depth"], g["registered_floor"]))
        out["instrument"] = G.instrument_checks()
        out["what_the_author_has_seen"] = (
            "the per-sector node counts of the STABLE rungs (printed by the run logs) and every "
            "lobe ratio. NOT p2: with the bottom rungs unmeasured the pooled ladder has no prefix "
            "to count from, so p2 is not derivable from what has been seen. The raw node artefacts "
            "are committed and DO contain the values; any future cycle scoring x=42 must say so and "
            "treat it as at most SEMI-BLIND.")
    json.dump(out, open(os.path.join(HERE, "m2_c56_scores_gated.json"), "w"), indent=1)
    pc = out["planted_control"]
    print("PLANTED CONTROL a1 (gate admits): %s"
          % pc["assertion_1_gate_admits_a_sufficient_cell"]["verdict"])
    print("PLANTED CONTROL a2 (p2 computes): %s"
          % pc["assertion_2_p2_is_computed_when_the_gate_passes"]["verdict"])
    print("TRUST GATE: depth=%s floor=%s holes=%s -> passed=%s"
          % (g["depth"], g.get("registered_floor"), g.get("holes"), g["passed"]))
    if not g["passed"]:
        i = out["instrument"]
        print("M1 %s (%d rungs examined)   M2 %s (%d holes)"
              % (i["M1"]["verdict"], i["rungs_examined"], i["M2"]["verdict"], len(i["M2"]["holes"])))
    print("VERDICT: %s" % out["VERDICT"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
