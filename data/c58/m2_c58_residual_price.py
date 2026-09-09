#!/usr/bin/env python3
"""m2_c58_residual_price.py -- PRICE THE RESIDUAL AT x = 42, EXACTLY.

c57 established that p2(42) is NOT DETERMINED by the committed bytes, by exhibiting TWO admissible
completions of the leading hole block that give two different `_first_leave` outcomes.  That is a
CARDINALITY-ONLY, LOWER-BOUND statement: "at least 2".  c57 then declared the residual
"UNPRICED BY DESIGN", on the ground (m1 register #183) that

    YOU CANNOT MEASURE HOW MUCH OF A BLIND WINDOW REMAINS WITHOUT SPENDING WHAT REMAINS.

This file prices it.  It computes the COMPLETE set of achievable values of p2 = _first_leave(delta, 2)
over ALL admissible completions of EVERY hole in the pooled table -- not two hand-picked ones -- under
three DECLARED admissibility regimes, and reports which registered model predictions each regime's
set excludes.  Doing so IS the spend; c58's prereg records the decision to spend and its reason.

WHAT IT DOES NOT DO.  It does not compute p2(42).  It computes the CONSTRAINT SET that the committed
bytes place on p2(42).  A model value absent from the set is excluded BY THE COMMITTED BYTES PLUS A
NAMED REGIME ASSUMPTION -- and since the N-control trusted depth at x=42 is 0, no such exclusion may
be scored as a refutation.  The grader is not touched, no node cell is written, no model is scored.

THE OBSERVATION THAT MAKES THIS CHEAP.  p2 depends on the delta sequence ONLY through the boolean
    b_p := (delta_p == 2),      delta_p := nu_p - (p - 1)
because _first_leave(delta, 2) = min{ p+1 : b_p and not b_{p+1} } (or None).  So the outcome space is
a function of the achievable boolean patterns, and each regime is a constraint on those patterns.

THE THREE REGIMES, DECLARED BEFORE THE RUN:
  R1 FREE      : nu_p is any integer >= 0 at a hole.  No order constraint.  (The weakest assumption
                 the physics licenses: node counts are non-negative integers.)
  R2 MONOTONE  : additionally nu_{p+1} >= nu_p along the pooled ladder.
  R3 DELTAMONO : additionally delta_{p+1} >= delta_p, i.e. nu_{p+1} >= nu_p + 1.  (The staircase
                 reading: delta rises through 0, 2, 6, ... and never falls.)
By construction set(R3) subseteq set(R2) subseteq set(R1); the program ASSERTS this and fails if not.
R3 may be EMPTY: the visible deltas themselves may not be non-decreasing (c50/c51 measured a NODAL
DISLOCATION).  An empty R3 is a RESULT, not an error.

CONTROLS, PLANTED, WITH THEIR FIRING WORLDS NAMED IN SOURCE BEFORE THE RUN:
  K1 no-hole KAT       : a fully visible synthetic table.  The set MUST be the singleton returned by
                         the SEALED S55._first_leave applied directly.  Firing world: non-empty by
                         construction (the table is written below).
  K2 hole-but-forced   : a synthetic table with a hole whose value cannot change the outcome.
                         KNOWN ANSWER {4}.  Catches an enumerator that multiplies outcomes spuriously.
  K3 hole-and-free     : a synthetic table with a hole that CAN change the outcome.
                         KNOWN ANSWER {2, None}.  Catches an enumerator that collapses outcomes.
  K4 planted DEAD      : R3 run on a synthetic table whose visible deltas STRICTLY DECREASE.
                         MUST return the EMPTY set.  A control that comes back dead is the
                         instrument working -- here "dead" is the PASS condition and it is declared.
  K5 c57 continuity    : c57's own two completions must both be MEMBERS of this file's R2 set.
Every control is checked in main() and the run ABORTS if any fails.
"""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C55 = os.path.abspath(os.path.join(HERE, "..", "c55"))
C56 = os.path.abspath(os.path.join(HERE, "..", "c56"))
sys.path.insert(0, C55)
print("resolver: c55 dir = %s" % C55)
print("resolver: c56 dir = %s" % C56)
import m2_c55_score as S55                       # sealed, imported, never edited

X, N, DPS = 42, 100, 300
REGIMES = ("R1_FREE", "R2_MONOTONE", "R3_DELTAMONO")


# ---------------------------------------------------------------- inputs, pinned (trap #177)
def nodefiles():
    out = {}
    for par in ("even", "odd"):
        pat = "m2_c56_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS)
        hits = [f for f in sorted(os.listdir(C56)) if f == pat]
        assert len(hits) == 1, "input selection is not unique for %s: %r" % (par, hits)
        out[par] = os.path.join(C56, hits[0])
    return out


def registered_p2():
    """REGISTERED_P2 read from the SEALED c56 grader BY AST -- never grep, never import (importing
    the grader would execute its module body).  A claim about a constant is a claim about a parse
    tree (register #189)."""
    src = open(os.path.join(C56, "m2_c56_score.py")).read()
    tree = ast.parse(src)
    found = {}
    live = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "REGISTERED_P2":
                    found = ast.literal_eval(node.value)
                if isinstance(t, ast.Name) and t.id == "LIVE":
                    live = list(ast.literal_eval(node.value))
    assert found and live, "REGISTERED_P2 / LIVE not found by AST in the sealed c56 grader"
    return found, live


# ---------------------------------------------------------------- the enumerator
def achievable_p2(nu, maxnu, regime):
    """nu: list of length n, entries int (visible) or None (hole), 1-based position p = index+1.
    Returns the SET of achievable _first_leave(delta, 2) values (ints, and None for 'never leaves').

    Exact forward DP.  State = (nu_p, b_p) for paths that have not yet produced an exit.  An exit at
    position p (b_p and not b_{p+1}) resolves the path with outcome p+1 and the path stops mattering.
    """
    n = len(nu)
    assert n >= 2

    def values_at(p):
        """admissible nu values at 1-based position p, given the regime's LOCAL constraint set.
        For R1 the value itself is irrelevant to the future, so two representatives suffice:
        the one that makes b true, and one that makes b false."""
        v = nu[p - 1]
        if v is not None:
            return [v]
        if regime == "R1_FREE":
            btrue = 2 + (p - 1)
            bfalse = 0 if btrue != 0 else 1
            return sorted({btrue, bfalse})
        return list(range(0, maxnu + 1))

    def bof(p, v):
        return (v - (p - 1)) == 2

    resolved = set()
    # position 1
    cur = set()
    for v in values_at(1):
        cur.add((v, bof(1, v)))
    for p in range(1, n):
        nxt = set()
        for (vp, bp) in cur:
            for vq in values_at(p + 1):
                if regime == "R2_MONOTONE" and vq < vp:
                    continue
                if regime == "R3_DELTAMONO" and vq < vp + 1:
                    continue
                bq = bof(p + 1, vq)
                if bp and not bq:
                    resolved.add(p + 1)
                else:
                    nxt.add((vq, bq))
        cur = nxt
    if cur:
        resolved.add(None)
    return resolved


def sortable(s):
    return sorted([v for v in s if v is not None]) + ([None] if None in s else [])


# ---------------------------------------------------------------- controls
def _direct(nu):
    return S55._first_leave([v - i for i, v in enumerate(nu)], 2)


def controls():
    """Each control returns (name, passed, detail).  Firing worlds are named in the docstring."""
    out = []

    # K1: no holes.  Set must be the singleton the SEALED function returns.
    k1nu = [1, 3, 4, 5, 9, 10]                 # delta = 1,2,2,2,5,5 -> exit at p=4 -> p2 = 5
    got = achievable_p2(k1nu, max(k1nu), "R1_FREE")
    want = {_direct(k1nu)}
    out.append(("K1_no_hole_KAT", got == want, dict(got=sortable(got), want=sortable(want))))

    # K2: a hole that CANNOT change the outcome.  KNOWN ANSWER {4}.
    k2nu = [None, 3, 4, 7]                     # delta = ?,2,2,4 -> exit at p=3 -> p2 = 4 always
    got = achievable_p2(k2nu, 9, "R1_FREE")
    out.append(("K2_forced_hole_KAT", got == {4}, dict(got=sortable(got), want=[4])))

    # K3: a hole that CAN change the outcome.  KNOWN ANSWER {2, None}.
    k3nu = [None, 5, 7, 9]                     # delta = ?,4,5,6 ; b_1 true -> exit p=1 -> p2 = 2
    got = achievable_p2(k3nu, 9, "R1_FREE")
    out.append(("K3_free_hole_KAT", got == {2, None}, dict(got=sortable(got), want=[2, None])))

    # K4: planted DEAD -- R3 on strictly DECREASING visible deltas must be EMPTY.
    k4nu = [9, 8, 7, 6]                        # delta = 9,7,5,3 : strictly decreasing
    got = achievable_p2(k4nu, 9, "R3_DELTAMONO")
    out.append(("K4_planted_dead_R3", got == set(), dict(got=sortable(got), want=[])))

    # K4b: the SAME table under R1 must be NON-empty -- otherwise K4's death proves nothing.
    got = achievable_p2(k4nu, 9, "R1_FREE")
    out.append(("K4b_same_table_alive_under_R1", got != set(), dict(got=sortable(got))))

    return out


# ---------------------------------------------------------------- main
def main():
    nf = nodefiles()
    tab, cert, forder = S55.pooled_table(nf)
    nu = [r["nu"] for r in tab]
    n = len(nu)
    holes = [r["p"] for r in tab if r["nu"] is None]
    seen = [r["p"] for r in tab if r["nu"] is not None]
    vis = [v for v in nu if v is not None]
    assert vis, "no visible node count in the pooled table -- nothing to price against"
    # the enumeration ceiling is only sound if every hole lies BELOW the last visible position
    assert max(holes) < max(seen), ("a hole sits above the last visible position; the monotone "
                                    "regimes are then unbounded above and this ceiling is invalid")
    maxnu = max(vis)

    ctrl = controls()
    print("CONTROLS")
    for name, ok, det in ctrl:
        print("  %-32s %s   %s" % (name, "PASS" if ok else "FAIL", det))
    if not all(ok for _, ok, _ in ctrl):
        print("\nABORT: a planted control failed.  No result is reported.")
        return 2

    sets = {}
    for rg in REGIMES:
        sets[rg] = achievable_p2(nu, maxnu, rg)
    # structural self-check: strictly stronger constraints can only shrink the set
    assert sets["R3_DELTAMONO"] <= sets["R2_MONOTONE"] <= sets["R1_FREE"], \
        "regime nesting violated -- the enumerator is wrong, not the data"

    # K5: c57's own two completions must be MEMBERS of the R2 set
    lead = next((i for i, v in enumerate(nu) if v is not None), n)
    tail = []
    for r in tab[lead:]:
        if r["nu"] is None:
            break
        tail.append(r["nu"] - (r["p"] - 1))
    c57cand = {S55._first_leave([2] * lead + tail, 2),
               S55._first_leave([0 - (p - 1) for p in range(1, lead + 1)] + tail, 2)}
    k5 = c57cand <= sets["R2_MONOTONE"]
    print("  %-32s %s   %s" % ("K5_c57_continuity", "PASS" if k5 else "FAIL",
                               dict(c57_two_completions=sortable(c57cand))))
    if not k5:
        print("\nABORT: this file contradicts c57's own published probe.  No result is reported.")
        return 2

    P2, LIVE = registered_p2()
    excl = {}
    for rg in REGIMES:
        excl[rg] = {k: dict(value=P2[k], achievable=(P2[k] in sets[rg]))
                    for k in LIVE}

    # does the visible tail itself host a delta == 2 anywhere?
    vis_delta2 = [r["p"] for r in tab if r["nu"] is not None and (r["nu"] - (r["p"] - 1)) == 2]
    vis_deltas_nondecreasing = True
    prev = None
    for r in tab:
        if r["nu"] is None:
            continue
        d = r["nu"] - (r["p"] - 1)
        if prev is not None and d < prev:
            vis_deltas_nondecreasing = False
        prev = d

    def contiguous(s):
        ints = sorted(v for v in s if v is not None)
        return bool(ints) and ints == list(range(ints[0], ints[-1] + 1))

    depth, det = S55.n_control_depth(nf, {p: nf[p].replace("N100", "N180") for p in nf})

    out = dict(
        cycle=58, window=X, N=N, dps=DPS,
        pooled_rows=n, certified_prefix=cert, float_order_equals_decimal_order=forder,
        holes=holes, seen=seen, leading_hole_block=lead,
        enumeration_ceiling=maxnu,
        regimes={rg: dict(achievable_p2=sortable(sets[rg]),
                          cardinality=len(sets[rg]),
                          contiguous_integer_run=contiguous(sets[rg]),
                          none_achievable=(None in sets[rg])) for rg in REGIMES},
        registered_p2=P2, live_models=LIVE,
        model_exclusion=excl,
        excluded_counts={rg: sum(1 for k in LIVE if not excl[rg][k]["achievable"])
                         for rg in REGIMES},
        visible_positions_with_delta_eq_2=vis_delta2,
        visible_deltas_nondecreasing=vis_deltas_nondecreasing,
        n_control_trusted_depth=depth,
        controls=[dict(name=nm, passed=bool(ok), detail=d) for nm, ok, d in ctrl]
                 + [dict(name="K5_c57_continuity", passed=bool(k5),
                         detail=dict(c57_two_completions=sortable(c57cand)))],
        scope=("Computes the CONSTRAINT SET on p2(42), never p2(42). No node cell written, no "
               "model scored, the grader untouched. Any exclusion below is BY THE BYTES PLUS A "
               "NAMED REGIME, and with n_control_trusted_depth = %d at this window it may not be "
               "read as a refutation of any model." % depth),
        p2_computed_here=False,
    )
    json.dump(out, open(os.path.join(HERE, "m2_c58_residual_price.json"), "w"), indent=1)

    print("\nPOOLED: %d rows, %d holes (leading block %d), %d seen, ceiling %d"
          % (n, len(holes), lead, len(seen), maxnu))
    for rg in REGIMES:
        s = sets[rg]
        print("  %-14s |set| = %-3d  contiguous=%s  None in set=%s  excluded live models: %s"
              % (rg, len(s), contiguous(s), None in s,
                 [k for k in LIVE if not excl[rg][k]["achievable"]]))
    print("  visible positions with delta == 2 : %s" % vis_delta2)
    print("  visible deltas non-decreasing     : %s" % vis_deltas_nondecreasing)
    print("  N-control trusted depth at x=42   : %d" % depth)
    return 0


if __name__ == "__main__":
    sys.exit(main())
