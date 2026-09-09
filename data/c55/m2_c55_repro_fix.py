#!/usr/bin/env python3
"""m2_c55_repro_fix.py -- the G0-REPRO gate, re-run with ONE ADDED EXEMPTION CLASS and a MUTATION
CONTROL that proves the exemption did not disarm it.

WHAT HAPPENED, IN FULL
----------------------
IN CYCLE 54 the sealed `repro` gate compared a c53 cell re-run through that cycle's wrapper
against c53's banked artefact and returned **21/22 fields identical -> FAIL**.  The single
differing field was `nodes.R`: the gate re-runs only rungs 1..5 (to keep the gate cheap) and then
compares against a banked cell whose `R` field records 16.  Every eigenvalue string, every
coefficient, every node count, every delta -- 21 of 22 fields -- was identical.

🔴 THIS PARAGRAPH IS CYCLE 54's HISTORY, NOT A CLAIM ABOUT CYCLE 55.  This file was cloned from
`../c54/m2_c54_repro_fix.py` by a 54->55 substitution, and that substitution silently rewrote a
past narrative into a present-tense assertion about a gate that had not yet run.  It is corrected
here, and `sealed_gate_result` below is now READ FROM cycle 55's own gate output instead of being
hardcoded -- a cloned instrument that carries the previous cycle's story is the c53 name-collision
one layer up: right arithmetic, wrong referent.

🔴 THE RULE BEING FOLLOWED: **a detector written before a convention scores the convention as a
failure -- ADD the class, never loosen** (c45, v2 defect 2).  So this file does not edit the sealed
gate and does not delete the failure.  It adds ONE named class -- *the field that records the
truncation, when and only when the comparison is deliberately truncated* -- and then proves, by
mutation, that the gate can still fail after the class is added.

🔴 AND THE REASON THE MUTATION ARM IS NOT OPTIONAL: an exemption is indistinguishable from a
loosening on any evidence that does not include a planted failure.  The sealed gate's original
output stands in the record, unedited, as `m2_c55_repro_gate.json`.

usage: m2_c55_repro_fix.py         (recomputes nothing; reads the artefacts both runs already wrote)
"""
import json, os, copy

HERE = os.path.dirname(os.path.abspath(__file__))
C53 = os.path.abspath(os.path.join(HERE, "..", "c53"))

CELL = dict(parity="even", x=13, N=100, dps=150, R=5)
IGN_SEALED = {"build_seconds", "eigsy_seconds", "seconds", "label", "resolver", "source"}
IGN_ADDED = {"R"}          # <- the ONE added class, named here and printed in the output
ADDED_CLASS_REASON = ("`R` records HOW MANY rungs the run counted. The gate deliberately re-runs a "
                      "SHORT prefix (R=5) of a banked 16-rung cell to stay cheap, so R differs BY "
                      "CONSTRUCTION and its inequality carries no information about the computation. "
                      "Exempt ONLY while the comparison is truncated (mine < theirs); a truncated "
                      "comparison that reported R equal would itself be the defect.")


def _sealed_gate_result():
    """READ the sealed gate's own output for THIS cycle; never hardcode last cycle's verdict."""
    fn = os.path.join(HERE, "m2_c55_repro_gate.json")
    if not os.path.exists(fn):
        return dict(file="m2_c55_repro_gate.json", present=False,
                    note="the sealed gate has not been run in this cycle -- nothing is claimed "
                         "about it here")
    g = json.load(open(fn))
    return dict(file="m2_c55_repro_gate.json", present=True, verdict=g.get("verdict"),
                fields_identical="%d/%d" % (g.get("compared_fields", 0) - g.get("fails", 0),
                                            g.get("compared_fields", 0)),
                differing_fields=[r["field"] for r in g.get("rows", []) if not r["identical"]],
                note="left in the record unedited; this file does not replace it")


def _load(p):
    return json.load(open(p))


def compare(mine, theirs, ign, rtrunc):
    rows, fails, compared = [], 0, 0
    for k in sorted(set(mine) | set(theirs)):
        if k in ign:
            continue
        compared += 1
        same = json.dumps(mine.get(k), sort_keys=True) == json.dumps(theirs.get(k), sort_keys=True)
        fails += 0 if same else 1
        rows.append(dict(field=k, identical=bool(same)))
    return rows, fails, compared


def main():
    par, X, N, D, R = CELL["parity"], CELL["x"], CELL["N"], CELL["dps"], CELL["R"]
    mine_spec = _load(os.path.join(HERE, "m2_c55_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, D)))
    them_spec = _load(os.path.join(C53, "m2_c53_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, D)))
    mine_nod = _load(os.path.join(HERE, "m2_c55_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, D)))
    them_nod = _load(os.path.join(C53, "m2_c53_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, D)))
    them_nod_t = dict(them_nod, rungs=them_nod["rungs"][:R])

    truncated = mine_nod["R"] < them_nod["R"]
    ign_nodes = IGN_SEALED | (IGN_ADDED if truncated else set())

    srows, sf, sc = compare(mine_spec, them_spec, IGN_SEALED, False)
    nrows, nf, nc = compare(mine_nod, them_nod_t, ign_nodes, truncated)

    # ---- MUTATION CONTROL: plant one wrong digit and require the gate to FAIL.
    mut = copy.deepcopy(mine_nod)
    old = mut["rungs"][0]["nu"]
    mut["rungs"][0]["nu"] = (old or 0) + 1
    _, mf, _ = compare(mut, them_nod_t, ign_nodes, truncated)
    mut2 = copy.deepcopy(mine_spec)
    lam = mut2["rungs"][0]["lam"]
    mut2["rungs"][0]["lam"] = lam[:-1] + ("7" if lam[-1] != "7" else "3")
    _, mf2, _ = compare(mut2, them_spec, IGN_SEALED, False)
    control_ok = (mf > 0 and mf2 > 0)

    verdict = "PASS" if (sf == 0 and nf == 0 and control_ok) else "FAIL"
    out = dict(
        verdict=verdict,
        cell=CELL,
        sealed_gate_result=_sealed_gate_result(),
        spec=dict(compared=sc, fails=sf, rows=srows),
        nodes=dict(compared=nc, fails=nf, rows=nrows, truncated=bool(truncated),
                   mine_R=mine_nod["R"], theirs_R=them_nod["R"]),
        added_exemption=dict(fields=sorted(IGN_ADDED), active=bool(truncated),
                             reason=ADDED_CLASS_REASON),
        sealed_exemptions=sorted(IGN_SEALED),
        mutation_control=dict(
            node_count_mutation=dict(planted="rungs[0].nu %s -> %s" % (old, (old or 0) + 1),
                                     fails_reported=mf, fires=bool(mf > 0)),
            eigenvalue_mutation=dict(planted="rungs[0].lam last digit changed",
                                     fails_reported=mf2, fires=bool(mf2 > 0)),
            verdict=("PASS" if control_ok else "FAIL"),
            why="an exemption is indistinguishable from a loosening on any evidence that does not "
                "include a planted failure."),
        headline=("the c55 wrapper reproduces c53's published cell field-for-field on every field "
                  "that carries a number: %d/%d spec fields and %d/%d node fields identical, with "
                  "one exemption class (R) that is named, conditional, and shown to leave the gate "
                  "able to fail." % (sc - sf, sc, nc - nf, nc)))
    json.dump(out, open(os.path.join(HERE, "m2_c55_repro_gate_fixed.json"), "w"), indent=1)
    print("G0-REPRO (fixed): spec %d/%d, nodes %d/%d identical; truncated=%s; "
          "mutation control fires %s/%s -> %s"
          % (sc - sf, sc, nc - nf, nc, truncated, mf, mf2, verdict))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
