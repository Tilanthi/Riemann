#!/usr/bin/env python3
"""m2_c55_score_jointfix.py -- SIBLING repair of TWO defects in the sealed c55 grader, both found by
reading its own output against the artefacts it read.

DEFECT 1: the JOINT arm did not apply the trust gate that every per-window arm applies.
DEFECT 2: `plateaus()` grouped `None` as if it were a plateau VALUE, so a run of unmeasured rungs
          was reported as a plateau of that length (x=22 printed lengths [4,1,5,...] where the 4 is
          four HOLES).  Both are non-gating BY MEASUREMENT -- every affected verdict is UNMEASURED
          for an independent reason -- and both are repaired here by ADDING, never by editing.

THE DEFECT.  `m2_c55_score.py.score()` builds the pair (p2(22), p2(25)) from
`P2.measured_p2` **without checking `P2.verdict`**.  Every single-window prediction degrades to
"UNMEASURED (outside trust)" when the N-control depth does not reach the index -- but the joint
criterion read the raw indices anyway and printed a substantive verdict ("NO BANK -- the pair
(11,11) is named by A and L") over two windows whose measured trusted depth is **0**.

THE REPAIR IS AN ADDITION, NOT AN EDIT.  The sealed grader and its output are left exactly as they
are, defect included, in `m2_c55_scores.json`.  This file recomputes the joint verdict WITH the gate
and writes a separate artefact.

DIRECTION CHECK (m1's discipline, and the reason this repair is safe to make after seeing the data):
the gate can only turn a substantive joint verdict INTO "UNMEASURED".  It cannot create a bank, it
cannot refute a model, and it cannot move any number.  A repair that can only weaken its author's own
claim is the only kind that may be made after the answer is known.

PLANTED CONTROL (an exemption -- or a gate -- is indistinguishable from a loosening without a planted
failure): the same gated function is run on a SYNTHETIC pair whose windows carry sufficient depth,
and it must still produce the substantive verdict.  If the gate simply said UNMEASURED always, the
control would catch it.

usage: m2_c55_score_jointfix.py   ->  m2_c55_scores_jointfix.json
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEALED = os.path.join(HERE, "m2_c55_scores.json")
OUT = os.path.join(HERE, "m2_c55_scores_jointfix.json")

JOINT_SIGNATURES = {"A": (11, 11), "X": (11, 12), "I": (12, 12), "S": (12, 13),
                    "L": (11, 11), "Z": (15, 17)}


def joint(pairs):
    """pairs: [(x, p2, depth, verdict_string), ...] -> the joint record, TRUST-GATED."""
    inside = [p for p in pairs
              if p[1] is not None and p[2] is not None and p[2] >= p[1]]
    pair = tuple(p[1] for p in pairs)
    if len(inside) != len(pairs):
        return dict(measured_pair=list(pair), trust_gated=True,
                    windows=[dict(x=p[0], p2=p[1], trusted_depth=p[2], window_verdict=p[3])
                             for p in pairs],
                    namers=[], live_namers=[],
                    verdict=("UNMEASURED -- %d of %d windows produced p2 OUTSIDE the N-control "
                             "trusted depth, so the pair is not a measurement and no model is "
                             "scored on it" % (len(pairs) - len(inside), len(pairs))))
    named = sorted(k for k, sig in JOINT_SIGNATURES.items() if tuple(sig) == pair)
    live = [k for k in named if k in ("I", "X", "S", "A")]
    if not named:
        v = "EVERY REGISTERED RULE REFUTED -- the pair %s matches no registered signature" % (pair,)
    elif len(named) == 1:
        v = "CONFIRMED: %s is the sole registered namer of the pair %s" % (named[0], pair)
    else:
        v = ("NO BANK -- the pair %s is named by more than one registered rule (%s)"
             % (pair, ", ".join(named)))
    return dict(measured_pair=list(pair), trust_gated=True,
                windows=[dict(x=p[0], p2=p[1], trusted_depth=p[2], window_verdict=p[3])
                         for p in pairs],
                namers=named, live_namers=live, verdict=v)


def plateaus_holeaware(seq):
    """Plateaus with HOLES kept as holes.  A run of None is reported as a gap, never as a value,
    and a plateau interrupted by a hole is not silently joined across it."""
    out = []
    for v in seq:
        tag = "HOLE" if v is None else v
        if out and out[-1][0] == tag:
            out[-1][1] += 1
        else:
            out.append([tag, 1])
    return [dict(value=(None if v == "HOLE" else v), hole=(v == "HOLE"), length=n) for v, n in out]


def main():
    S = json.load(open(SEALED))
    pairs = []
    for x in (22, 25):
        w = S["windows"][str(x)]
        pairs.append((x, w.get("P2", {}).get("measured_p2"),
                      w.get("n_control_trusted_depth"), w.get("P2", {}).get("verdict")))
    gated = joint(pairs)

    # ---- PLANTED CONTROL: same code, sufficient depth, must still discriminate
    control = joint([(22, 11, 25, "MEASURED"), (25, 12, 25, "MEASURED")])
    control_ok = control["verdict"].startswith("CONFIRMED: X")
    control2 = joint([(22, 12, 25, "MEASURED"), (25, 12, 25, "MEASURED")])
    control2_ok = control2["verdict"].startswith("CONFIRMED: I")

    plat = {}
    for x in (22, 25):
        seq = S["windows"][str(x)].get("pooled_delta_N100")
        if seq is not None:
            ha = plateaus_holeaware(seq)
            plat[str(x)] = dict(
                sealed_grader_lengths=S["windows"][str(x)].get("P8", {}).get("all_lengths"),
                hole_aware=ha,
                holes=sum(1 for e in ha if e["hole"]),
                note="the sealed grader's length list counts a run of unmeasured rungs as a plateau; "
                     "here a hole is a hole. Nothing is re-scored: P8 and P9 are UNMEASURED at both "
                     "windows because the N-control trusted depth is 0.")

    out = dict(
        repairs="(1) JOINT arm trust gate, (2) hole-aware plateaus (sibling; the sealed grader and "
                "m2_c55_scores.json are unedited)",
        plateaus_hole_aware=plat,
        sealed_joint_verdict=S["JOINT"]["verdict"],
        gated_joint=gated,
        direction_check=("the gate can only turn a substantive joint verdict into UNMEASURED; it "
                         "cannot create a bank, refute a model, or move a number"),
        planted_controls=dict(
            pair_11_12_with_depth_25=dict(verdict=control["verdict"], fires=bool(control_ok)),
            pair_12_12_with_depth_25=dict(verdict=control2["verdict"], fires=bool(control2_ok)),
            why="if the gate simply said UNMEASURED always, these would fail"),
        verdict=("PASS" if (control_ok and control2_ok) else "FAIL"))
    json.dump(out, open(OUT, "w"), indent=1)
    print("SEALED joint verdict : %s" % out["sealed_joint_verdict"])
    print("GATED  joint verdict : %s" % gated["verdict"])
    print("planted controls: (11,12)->%s [%s] ; (12,12)->%s [%s]"
          % (control["verdict"][:40], control_ok, control2["verdict"][:40], control2_ok))
    for x in ("22", "25"):
        if x in plat:
            print("plateaus x=%s: sealed %s -> hole-aware %s (holes: %d)"
                  % (x, plat[x]["sealed_grader_lengths"],
                     [("HOLE", e["length"]) if e["hole"] else (e["value"], e["length"])
                      for e in plat[x]["hole_aware"]][:8], plat[x]["holes"]))
    print("JOINTFIX: %s" % out["verdict"])
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
