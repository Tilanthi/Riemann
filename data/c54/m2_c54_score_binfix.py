#!/usr/bin/env python3
"""m2_c54_score_binfix.py -- a SCORER DEFECT, found AFTER the numbers existed, disclosed and
repaired in a sibling file rather than by editing the scored artefact.

THE DEFECT.  `m2_c54_score.py` builds the outcome-bin membership map from `model_values(...)`,
in which Model G's `p2` is `None` (G is computed at stage A, not from a closed form).  It then
loads the stage-A file and writes G's value into `S["P2"]["models"]["G"]["p2"]` -- but the bins
have already been built.  So `m2_c54_scores.json` reports bin 10 as `['L']` when G also names 10.

WHY IT CHANGES NOTHING THIS CYCLE, stated as a direction check and not as an excuse:
  * the MEASURED value is p2 = 11.  Bin 10 is EMPTY of the measurement.
  * bin 11's occupants (I, X) are untouched, so the "no discrimination" verdict is untouched.
  * the refuted-live-models list (L) is untouched.
  * the only thing that moves is the membership list of a bin nothing landed in -- and it moves in
    the direction of MORE models being named as refuted, i.e. against the cycle's own models.
  * had p2 been 10, this defect would have printed L as the SOLE namer of the occupied bin and the
    prereg's own G-onto-L clause would have been silently skipped.  **That is the gating case, and
    it did not occur** -- a fact about which outcome happened, not a property of the defect.
    (The same boundary sentence machine 2 required of "non-gating" in the L197 round, applied here
    to machine 2.)

Output: m2_c54_scores_binfix.json -- the corrected bin map beside the scored one.
"""
import json, os, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sc", os.path.join(HERE, "m2_c54_score.py"))
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

S = json.load(open(os.path.join(HERE, "m2_c54_scores.json")))
g = json.load(open(os.path.join(HERE, "m2_c54_gpred_x17_N100_dps300.json")))
n = S["measured_zero_count_n"]
M = sc.model_values(sc.X, n)
M["G"]["p2"] = g["model_G_p2"]

bins = {}
for k, v in M.items():
    if v["p2"] is not None:
        bins.setdefault(v["p2"], []).append(k)
p2 = S["P2"]["measured_p2"]
occ = bins.get(p2, [])
live = [k for k in occ if M[k]["live"]]
out = dict(
    corrected_bins={str(k): sorted(v) for k, v in sorted(bins.items())},
    bins_as_scored=S["P2"]["bins"],
    measured_p2=p2, occupants=sorted(occ), live_occupants=sorted(live),
    survivor_count=len(live),
    refuted_models=sorted(k for k, v in M.items() if v["p2"] is not None and v["p2"] != p2),
    refuted_live_models=sorted(k for k, v in M.items()
                               if v["live"] and v["p2"] is not None and v["p2"] != p2),
    discrimination=("NONE -- more than one registered model names this bin" if len(occ) > 1
                    else ("SINGLE OCCUPANT" if len(occ) == 1 else "EMPTY BIN")),
    changed_vs_scored=[b for b in set(list(bins.keys()) + [int(k) for k in S["P2"]["bins"]])
                       if sorted(bins.get(b, [])) != sorted(S["P2"]["bins"].get(str(b), []))],
    direction_check=("the correction moves ONLY the membership of bin 10, which the measurement did "
                     "not occupy; it adds a model to the REFUTED list and removes none. It cannot "
                     "change p2, the occupied bin, the live survivors, or any verdict."),
    docstring=__doc__)
json.dump(out, open(os.path.join(HERE, "m2_c54_scores_binfix.json"), "w"), indent=1)
print("corrected bins: %s" % out["corrected_bins"])
print("as scored     : %s" % out["bins_as_scored"])
print("bins that moved: %s   measured p2 = %s   occupants %s   live %s -> %s"
      % (out["changed_vs_scored"], p2, out["occupants"], out["live_occupants"], out["discrimination"]))
