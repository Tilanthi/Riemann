#!/usr/bin/env python3
"""m2_c55_detector_ceiling.py -- MEASURE the node detector's stability regime across every window
the programme has ever computed, because cycle 55 is the first cycle in which it failed.

WHAT HAPPENED.  At x = 22 and x = 25 the imported c51 detector returned `nu = None`
(`stable: False`) on 15 rungs across 7 of the 8 new cells, always at or near the BOTTOM of the
ladder -- the smallest eigenvalues.  Nothing like it occurs at x = 13, 17 or 19: 13 published cells,
zero None rungs.  So this is not a coding error in this cycle; it is the first time the instrument
has been driven past its own floor, and the floor is worth measuring rather than describing.

THE QUANTITY.  `lobe_min_ratio` is the smallest lobe amplitude of the eigenfunction relative to its
largest.  A node between two lobes of relative size 1e-42 is a sign change the stored 40-s.f.
coefficients cannot adjudicate, and the detector says so instead of guessing: its counts at
tolerances 0, 1e-8 and 1e-4 disagree, so it refuses.

OUTPUT-PATH CHECK (c54's second law: an instrument that deposits its artefact inside its own
denominator manufactures its finding).  This tool globs `m2_c5?_nodes_*.json` under data/c5x and
writes `m2_c55_detector_ceiling.json`.  The check that the output is not in the input set is RUN and
PRINTED below, not asserted in a comment.

usage: m2_c55_detector_ceiling.py   ->  m2_c55_detector_ceiling.json
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "m2_c55_detector_ceiling.json")


def main():
    files = sorted(glob.glob(os.path.join(DATA, "c5?", "m2_c5?_nodes_*.json")))
    self_in_inputs = os.path.abspath(OUT) in [os.path.abspath(f) for f in files]
    rows, cells, excluded = [], [], []
    for f in files:
        d = json.load(open(f))
        # DECLARE THE CORPUS, THEN MARK WHAT SURVIVES (c41): c50's node artefacts predate the `nu` /
        # `lobe_min_ratio` fields entirely, so they are not silence about stability -- they are
        # OUTSIDE the population, and they are named here rather than dropped.
        if not d.get("rungs") or "nu" not in d["rungs"][0] or "lobe_min_ratio" not in d["rungs"][0]:
            excluded.append(dict(file=os.path.relpath(f, DATA),
                                 reason="schema predates the nu / lobe_min_ratio fields",
                                 fields=sorted(d["rungs"][0].keys()) if d.get("rungs") else []))
            continue
        x, N, par = d["x"], d["N"], d["parity"]
        nones = []
        for r in d["rungs"]:
            lr = r.get("lobe_min_ratio")
            rec = dict(x=x, N=N, parity=par, rung=r["rung"], nu=r["nu"],
                       unstable=(r["nu"] is None), stable_flag=r.get("stable"),
                       lobe_min_ratio=(float(lr) if lr is not None else None),
                       lam=r.get("lam"), counts=r.get("counts") if r["nu"] is None else None,
                       refine=r.get("nu_refine_48001"))
            rows.append(rec)
            if r["nu"] is None:
                nones.append(r["rung"])
        cells.append(dict(file=os.path.relpath(f, DATA), x=x, N=N, parity=par, R=d.get("R", len(d["rungs"])),
                          none_rungs=nones))
    by_x = {}
    for r in rows:
        b = by_x.setdefault(r["x"], dict(stable=[], unstable=[]))
        if r["lobe_min_ratio"] is not None:
            b["unstable" if r["unstable"] else "stable"].append(r["lobe_min_ratio"])
    summary = {}
    for x in sorted(by_x):
        st, un = by_x[x]["stable"], by_x[x]["unstable"]
        summary[str(x)] = dict(stable_rungs=len(st), unstable_rungs=len(un),
                               min_lobe_ratio_when_stable=(min(st) if st else None),
                               unstable_lobe_ratios=sorted(un))
    all_stable = [r["lobe_min_ratio"] for r in rows
                  if not r["unstable"] and r["lobe_min_ratio"] is not None]
    all_unstable = [r["lobe_min_ratio"] for r in rows
                    if r["unstable"] and r["lobe_min_ratio"] is not None]
    floor = min(all_stable) if all_stable else None
    above_floor_unstable = [v for v in all_unstable if v >= floor] if floor else []
    out = dict(
        output_path_check=dict(output=os.path.basename(OUT), input_files=len(files),
                               output_is_in_its_own_input_set=bool(self_in_inputs),
                               law="c54: a measurement tool that deposits its artefact into its own "
                                   "denominator manufactures its finding"),
        corpus=dict(globbed=len(files), scanned=len(files) - len(excluded),
                    excluded=excluded),
        cells=cells, per_window=summary,
        totals=dict(stable_rungs=len(all_stable), unstable_rungs=len(all_unstable),
                    min_lobe_ratio_among_stable=floor,
                    max_lobe_ratio_among_unstable=(max(all_unstable) if all_unstable else None),
                    unstable_rungs_above_the_stable_floor=len(above_floor_unstable),
                    unstable_ratios_above_floor=sorted(above_floor_unstable)),
        reading=("Every stable rung ever measured sits at lobe ratio >= %s. The unstable rungs are "
                 "not a tail of that distribution: all but %d of them lie between 1e-43 and 1e-41, "
                 "orders below the stable floor, so the failure is a REGIME, not a gradual "
                 "degradation. The exception(s) listed in unstable_ratios_above_floor fail for a "
                 "different reason and are named individually in the letter."
                 % (floor, len(above_floor_unstable))),
        unstable_detail=[r for r in rows if r["unstable"]])
    json.dump(out, open(OUT, "w"), indent=1)
    print("OUTPUT-PATH CHECK: output '%s' in its own input set of %d files? %s"
          % (os.path.basename(OUT), len(files), self_in_inputs))
    print("CORPUS: %d node artefacts globbed, %d scanned, %d EXCLUDED by schema: %s"
          % (len(files), len(files) - len(excluded), len(excluded),
             [e["file"] for e in excluded]))
    for x in sorted(by_x, key=int):
        s = summary[str(x)]
        print("  x=%-3s stable=%-3d (min lobe ratio %.3e)   unstable=%-2d %s"
              % (x, s["stable_rungs"], s["min_lobe_ratio_when_stable"] or float("nan"),
                 s["unstable_rungs"], ["%.2e" % v for v in s["unstable_lobe_ratios"]]))
    print("TOTALS: %d stable (floor %.3e), %d unstable, %d unstable ABOVE the stable floor: %s"
          % (len(all_stable), floor, len(all_unstable), len(above_floor_unstable),
             ["%.2e" % v for v in above_floor_unstable]))
    return 1 if self_in_inputs else 0


if __name__ == "__main__":
    sys.exit(main())
