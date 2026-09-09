#!/usr/bin/env python3
"""m2_c58_residual_price_fix.py -- SIBLING REPAIR of the sealed A-arm.  The sealed file is IMPORTED,
never edited (c55/c57 discipline: repair by ADDING a sibling).

The sealed `m2_c58_residual_price.py` ABORTED on its own planted control K5 and reported no set.
Per prereg sec 4 that makes the SEALED arm VOID, and it is recorded as void.  This file states what
K5 caught, repairs TWO defects, and re-measures.  Both defects were found by asking why a control
fired instead of by relaxing it.

DEFECT 1 -- K5 COMPARED TWO DIFFERENT OBJECTS.  K5 required c57's two published outcomes to be
members of THIS file's set.  But c57's probe built its sequence as

    [completion of the leading hole block] + tail,   tail = counts up to the FIRST hole

and at x=42 the first hole after the leading block is pooled position 14, so c57's `tail` has exactly
ONE element and its sequence is 13 long.  This file enumerates over the FULL 30-position table.  A
`_first_leave` outcome of a 13-element prefix is not an outcome of the 30-element table, so K5 was
comparing item k of two runs where item k is not the same object -- the very law (c56, m1 #187/#179)
this programme keeps filing.  REPAIRED: K5' applies THIS file's enumerator to c57's OWN truncated
object and requires c57's {13, None} to be members THERE.  Same object, same question.

DEFECT 2 -- and this one changes the answer.  The sealed forward DP records an outcome the moment an
exit fires (b_p true, b_{p+1} false) and then DROPS the path.  Under R1 that is harmless because
every suffix is completable.  Under R2/R3 it is WRONG: an outcome is achievable only if the WHOLE
sequence is admissible, and the sealed DP never checked that the positions AFTER the exit could be
completed under the regime's constraint.  So it credited outcomes to sequences that do not exist.
REPAIRED: a backward feasibility pass F[p] = { v admissible at p : some admissible completion of
p..n exists }, computed BEFORE the forward pass; a state is live only if v in F[p], and a resolution
at position q is credited only if its value lies in F[q].

DIRECTION OF THE REPAIR, stated before its result is read: defect 2 can only SHRINK the R2/R3 sets
(it removes outcomes, never adds them).  It therefore runs AGAINST registered prediction A3
("set(R3) is non-empty") and can only hurt A8c ("the integer part of set(R2) is a contiguous run").
It cannot help either.  A2 ("|set(R1)| > |set(R2)|") it can only help, and that is disclosed here
rather than left for a reader to notice: A2 must be read as robust-or-not against BOTH enumerators,
and both numbers are published below.

NEW PLANTED CONTROL for the repair itself (a registered repair is a hypothesis too, #187):
  P_SUFFIX : a synthetic table whose only exit sits in front of an INADMISSIBLE suffix.  The SEALED
             enumerator must report that outcome (defect present) and the REPAIRED one must not.
             If the sealed enumerator does NOT report it, this control is dead and the repair is
             unmotivated -- that is checked and reported, not assumed.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEALED = os.path.join(HERE, "m2_c58_residual_price.py")

# import the SEALED module's definitions without running its main()
_src = open(SEALED).read().replace('if __name__ == "__main__":\n    sys.exit(main())', '')
_G = {"__name__": "m2_c58_residual_price", "__file__": SEALED}
exec(compile(_src, SEALED, "exec"), _G)

S55 = _G["S55"]
sealed_achievable = _G["achievable_p2"]
nodefiles = _G["nodefiles"]
registered_p2 = _G["registered_p2"]
controls = _G["controls"]
sortable = _G["sortable"]
REGIMES = _G["REGIMES"]


def _values_at(nu, p, regime):
    v = nu[p - 1]
    if v is not None:
        return [v]
    if regime == "R1_FREE":
        btrue = 2 + (p - 1)
        return sorted({btrue, (0 if btrue != 0 else 1)})
    return list(range(0, _values_at.maxnu + 1))


def _ok(regime, vp, vq):
    if regime == "R2_MONOTONE":
        return vq >= vp
    if regime == "R3_DELTAMONO":
        return vq >= vp + 1
    return True


def achievable_p2_fixed(nu, maxnu, regime):
    """Exact set of achievable _first_leave(delta, 2) values, with SUFFIX FEASIBILITY enforced."""
    n = len(nu)
    _values_at.maxnu = maxnu

    def bof(p, v):
        return (v - (p - 1)) == 2

    # backward feasibility: F[p] = values at p from which p..n can be completed admissibly
    F = [None] * (n + 1)
    F[n] = set(_values_at(nu, n, regime))
    for p in range(n - 1, 0, -1):
        F[p] = {v for v in _values_at(nu, p, regime)
                if any(_ok(regime, v, w) for w in F[p + 1])}
    if not F[1]:
        return set()          # no admissible sequence exists at all

    resolved = set()
    cur = {(v, bof(1, v)) for v in F[1]}
    for p in range(1, n):
        nxt = set()
        for (vp, bp) in cur:
            for vq in F[p + 1]:
                if not _ok(regime, vp, vq):
                    continue
                bq = bof(p + 1, vq)
                if bp and not bq:
                    resolved.add(p + 1)      # vq is in F[p+1] => the suffix IS completable
                else:
                    nxt.add((vq, bq))
        cur = nxt
    if cur:
        resolved.add(None)
    return resolved


# ------------------------------------------------------------------ the repair's own control
P_SUFFIX_NU = [None, 3, 4, 9, 2]
# deltas: ?, 2, 2, 6, -2 .  Visible nu 3,4,9,2 is NOT non-decreasing (9 -> 2), so under R2 NO
# admissible sequence exists and the set must be EMPTY.  The sealed enumerator credits the exit at
# p=3 (b_3 true, b_4 false -> outcome 4) without checking that position 5 can follow position 4.


def p_suffix_control():
    sealed = sealed_achievable(P_SUFFIX_NU, 9, "R2_MONOTONE")
    fixed = achievable_p2_fixed(P_SUFFIX_NU, 9, "R2_MONOTONE")
    return dict(sealed=sortable(sealed), fixed=sortable(fixed),
                sealed_shows_defect=bool(sealed), repair_removes_it=(fixed == set()),
                control_alive=bool(sealed))


def main():
    nf = nodefiles()
    tab, cert, forder = S55.pooled_table(nf)
    nu = [r["nu"] for r in tab]
    n = len(nu)
    holes = [r["p"] for r in tab if r["nu"] is None]
    seen = [r["p"] for r in tab if r["nu"] is not None]
    maxnu = max(v for v in nu if v is not None)

    # --- sealed controls K1..K4b re-run unchanged (they never depended on the defect)
    ctrl = controls()

    # --- K5' : SAME OBJECT as c57
    lead = next((i for i, v in enumerate(nu) if v is not None), n)
    tail = []
    for r in tab[lead:]:
        if r["nu"] is None:
            break
        tail.append(r["nu"] - (r["p"] - 1))
    c57cand = {S55._first_leave([2] * lead + tail, 2),
               S55._first_leave([0 - (p - 1) for p in range(1, lead + 1)] + tail, 2)}
    trunc_nu = [None] * lead + [tab[lead]["nu"]]
    mine_on_c57_object = achievable_p2_fixed(trunc_nu, maxnu, "R2_MONOTONE")
    k5p = c57cand <= mine_on_c57_object

    psuf = p_suffix_control()

    sets_sealed = {rg: sealed_achievable(nu, maxnu, rg) for rg in REGIMES}
    sets_fixed = {rg: achievable_p2_fixed(nu, maxnu, rg) for rg in REGIMES}
    assert sets_fixed["R3_DELTAMONO"] <= sets_fixed["R2_MONOTONE"] <= sets_fixed["R1_FREE"], \
        "regime nesting violated in the repaired enumerator"
    for rg in REGIMES:
        assert sets_fixed[rg] <= sets_sealed[rg], \
            "the repair ADDED an outcome in %s -- it may only remove" % rg

    P2, LIVE = registered_p2()
    excl = {rg: {k: dict(value=P2[k], achievable=(P2[k] in sets_fixed[rg])) for k in LIVE}
            for rg in REGIMES}

    vis = [(r["p"], r["nu"], r["nu"] - (r["p"] - 1)) for r in tab if r["nu"] is not None]
    vis_delta2 = [p for p, _v, d in vis if d == 2]
    nus = [v for _p, v, _d in vis]
    ds = [d for _p, _v, d in vis]
    vis_nu_nondec = all(b >= a for a, b in zip(nus, nus[1:]))
    vis_delta_nondec = all(b >= a for a, b in zip(ds, ds[1:]))
    drops = [dict(from_p=vis[i][0], from_nu=vis[i][1], to_p=vis[i + 1][0], to_nu=vis[i + 1][1])
             for i in range(len(vis) - 1) if vis[i + 1][1] < vis[i][1]]

    def contiguous(s):
        ints = sorted(v for v in s if v is not None)
        return bool(ints) and ints == list(range(ints[0], ints[-1] + 1))

    depth, det = S55.n_control_depth(nf, {p: nf[p].replace("N100", "N180") for p in nf})

    out = dict(
        cycle=58, arm="A (SIBLING REPAIR of the sealed, VOIDED, arm)", window=42, N=100, dps=300,
        sealed_arm_status="VOID -- its planted control K5 fired; see this file's docstring",
        pooled_rows=n, certified_prefix=cert, float_order_equals_decimal_order=forder,
        holes=holes, seen=seen, leading_hole_block=lead, enumeration_ceiling=maxnu,
        visible_table=[dict(p=p, nu=v, delta=d) for p, v, d in vis],
        visible_nu_nondecreasing=vis_nu_nondec,
        visible_delta_nondecreasing=vis_delta_nondec,
        visible_nu_decreases_at=drops,
        visible_positions_with_delta_eq_2=vis_delta2,
        regimes_SEALED_enumerator={rg: dict(achievable_p2=sortable(sets_sealed[rg]),
                                            cardinality=len(sets_sealed[rg]))
                                   for rg in REGIMES},
        regimes_REPAIRED={rg: dict(achievable_p2=sortable(sets_fixed[rg]),
                                   cardinality=len(sets_fixed[rg]),
                                   contiguous_integer_run=contiguous(sets_fixed[rg]),
                                   none_achievable=(None in sets_fixed[rg])) for rg in REGIMES},
        registered_p2=P2, live_models=LIVE, model_exclusion_REPAIRED=excl,
        excluded_counts_REPAIRED={rg: sum(1 for k in LIVE if not excl[rg][k]["achievable"])
                                  for rg in REGIMES},
        controls=dict(sealed_K1_to_K4b=[dict(name=n_, passed=bool(o), detail=d)
                                        for n_, o, d in ctrl],
                      K5_prime_same_object=dict(passed=bool(k5p),
                                                c57_two_completions=sortable(c57cand),
                                                my_set_on_c57s_own_object=sortable(
                                                    mine_on_c57_object)),
                      P_SUFFIX_repair_control=psuf),
        n_control_trusted_depth=depth,
        scope=("Computes the CONSTRAINT SET on p2(42), never p2(42). No node cell written, no "
               "model scored. With n_control_trusted_depth = %d at this window, no exclusion "
               "below may be read as a refutation of any model." % depth),
        p2_computed_here=False,
    )
    json.dump(out, open(os.path.join(HERE, "m2_c58_residual_price_fix.json"), "w"), indent=1)

    print("CONTROLS (sealed K1..K4b)")
    for n_, o, d in ctrl:
        print("  %-32s %s" % (n_, "PASS" if o else "FAIL"))
    print("  %-32s %s   c57 gave %s ; my set on c57's OWN object = %s"
          % ("K5'_same_object", "PASS" if k5p else "FAIL", sortable(c57cand),
             sortable(mine_on_c57_object)))
    print("  %-32s sealed=%s fixed=%s  alive=%s removes=%s"
          % ("P_SUFFIX (control on the repair)", psuf["sealed"], psuf["fixed"],
             psuf["control_alive"], psuf["repair_removes_it"]))
    print("\nVISIBLE TABLE (p, nu, delta): %s" % vis)
    print("  visible nu non-decreasing    : %s   (decreases at %d places)"
          % (vis_nu_nondec, len(drops)))
    print("  visible delta non-decreasing : %s" % vis_delta_nondec)
    print("  visible positions delta == 2 : %s" % vis_delta2)
    print("\nSETS")
    for rg in REGIMES:
        print("  %-14s sealed |%d| %s" % (rg, len(sets_sealed[rg]), sortable(sets_sealed[rg])))
        print("  %-14s FIXED  |%d| %s  contiguous=%s  None=%s  excluded live: %s"
              % ("", len(sets_fixed[rg]), sortable(sets_fixed[rg]), contiguous(sets_fixed[rg]),
                 None in sets_fixed[rg], [k for k in LIVE if not excl[rg][k]["achievable"]]))
    print("\nN-control trusted depth at x=42: %d" % depth)
    return 0


if __name__ == "__main__":
    sys.exit(main())
