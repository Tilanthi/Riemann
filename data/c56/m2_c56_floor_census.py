#!/usr/bin/env python3
"""m2_c56_floor_census.py -- does the unstable-lobe cluster track the DETECTOR'S FLOOR?

c55 measured, at STORE_SF = 40: 15 unstable rungs, 14 of them in 1e-43..1e-41, ceiling 5.6e-41 --
i.e. the cluster sits at ~10^(-STORE_SF).  c56 repaired the store to 120, and the binding floor
became the detector's own working precision, `mp.dps = 50` inside c53's `nodes()`.  PREDICTION
IMPLIED BY THE MECHANISM: the cluster must reappear at ~10^(-50).

It also tests, by measurement, the domain rule m1's L200 sec 7 queues for the shared register --
"a rung whose lobe_min_ratio falls below the stored coefficient resolution is OUTSIDE the detector's
domain".  If lobe_min_ratio were such a predicate, stable and unstable rungs would be SEPARATED by
it at every floor.  Measured here at both.
"""
import json, glob, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C55 = os.path.abspath(os.path.join(HERE, "..", "c55"))


def cell(files):
    lo, hi = [], []
    for f in files:
        for r in json.load(open(f))["rungs"]:
            v = r.get("lobe_min_ratio")
            if v is None:
                continue
            (lo if r["nu"] is None else hi).append(float(v))
    return lo, hi


def summarise(tag, files, floor_source, floor_decades):
    lo, hi = cell(files)
    d = dict(regime=tag, files=[os.path.basename(f) for f in files],
             binding_floor=floor_source, floor_decades=floor_decades,
             unstable=len(lo), stable=len(hi),
             unstable_min=(min(lo) if lo else None), unstable_max=(max(lo) if lo else None),
             unstable_median_log10=(round(sorted(math.log10(v) for v in lo)[len(lo) // 2], 2)
                                    if lo else None),
             unstable_max_log10=(round(math.log10(max(lo)), 2) if lo else None),
             stable_min=(min(hi) if hi else None),
             stable_below_the_unstable_max=sorted(v for v in hi if lo and v < max(lo)),
             populations_disjoint=bool(lo and hi and max(lo) < min(hi)))
    return d


def main():
    c55f = sorted(glob.glob(os.path.join(C55, "m2_c55_nodes_*x2[25]*.json")))
    c56f = sorted(glob.glob(os.path.join(HERE, "m2_c56_nodes_*x42*.json")))
    a = summarise("c55: STORE_SF=40 (storage binds)", c55f, "STORE_SF = 40", -40)
    b = summarise("c56: STORE_SF=120, detector dps=50 (working precision binds)", c56f,
                  "mp.dps = 50 inside c53 nodes()", -50)
    out = dict(
        regimes=[a, b],
        cluster_tracks_the_floor=dict(
            statistic="MEDIAN log10 of the unstable lobe ratios (the MAX is dominated by the single "
                      "c55 outlier at 4.6e-5, which is a TOLERANCE effect, not a floor effect -- "
                      "c55's own H4)",
            criterion="|median log10 - (-floor_decades)| <= 5 decades",
            at_store_sf_40=dict(median_log10=a["unstable_median_log10"], floor=-40,
                                within_5=bool(a["unstable_median_log10"] is not None
                                              and abs(a["unstable_median_log10"] + 40) <= 5)),
            at_dps_50=dict(median_log10=b["unstable_median_log10"], floor=-50,
                           within_5=bool(b["unstable_median_log10"] is not None
                                         and abs(b["unstable_median_log10"] + 50) <= 5)),
            disclosure_of_a_defect_in_this_very_file=(
                "the first version of this verdict tested only that both numbers were NOT None, so "
                "it could print CONFIRMED for any values whatever -- a VACUOUS gate, caught by "
                "reading its own output against the numbers above it. Recorded, not deleted."),
            verdict=None),
        domain_rule_test=dict(
            claim_under_test=("m1 L200 sec 7 / our own c55 letter: a rung whose lobe_min_ratio falls "
                              "below the stored resolution is OUTSIDE the detector's domain"),
            disjoint_at_store_sf_40=a["populations_disjoint"],
            disjoint_at_dps_50=b["populations_disjoint"],
            stable_rungs_inside_the_unstable_range_at_dps_50=b["stable_below_the_unstable_max"],
            verdict=("REFUTED AS A PREDICATE: at the dps=50 floor the two populations OVERLAP -- "
                     "stable rungs sit inside the unstable range -- so lobe_min_ratio does not "
                     "decide domain membership. The disjointness c55 saw at STORE_SF=40 was a "
                     "property of a 38-decade gap between the storage floor and the true lobes, "
                     "not a property of the quantity."
                     if not b["populations_disjoint"] else
                     "NOT REFUTED at this floor -- the populations remain disjoint")),
        what_still_works=("the `stable` flag itself: DISAGREEMENT BETWEEN THE TOLERANCE KNOBS. It "
                          "is a property of the reading, not of a number derived from the same "
                          "contaminated reconstruction, so it does not go circular at the floor."))
    json.dump(out, open(os.path.join(HERE, "m2_c56_floor_census.json"), "w"), indent=1)
    for r in (a, b):
        print("%-58s unstable %2d (max %.3e, log10 %.1f)  stable %2d (min %.3e)  disjoint=%s"
              % (r["regime"], r["unstable"], r["unstable_max"], r["unstable_max_log10"],
                 r["stable"], r["stable_min"], r["populations_disjoint"]))
    ct = out["cluster_tracks_the_floor"]
    ct["verdict"] = ("CONFIRMED at both floors"
                     if ct["at_store_sf_40"]["within_5"] and ct["at_dps_50"]["within_5"]
                     else "NOT CONFIRMED at one or both floors")
    json.dump(out, open(os.path.join(HERE, "m2_c56_floor_census.json"), "w"), indent=1)
    print("CLUSTER MEDIAN vs FLOOR: SF=40 median %s (floor -40, within5=%s) | dps=50 median %s "
          "(floor -50, within5=%s) -> %s"
          % (ct["at_store_sf_40"]["median_log10"], ct["at_store_sf_40"]["within_5"],
             ct["at_dps_50"]["median_log10"], ct["at_dps_50"]["within_5"], ct["verdict"]))
    print("DOMAIN RULE: %s" % out["domain_rule_test"]["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
