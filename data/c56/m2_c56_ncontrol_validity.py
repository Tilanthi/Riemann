#!/usr/bin/env python3
"""m2_c56_ncontrol_validity.py -- IS THE N-CONTROL A CONTROL AT THIS WINDOW?

WHY THIS EXISTS.  The N-control (c53's P6, the programme's trusted-depth instrument) compares the
node count of sector rung k at N=100 with the node count of sector rung k at N=180 and counts the
agreeing PREFIX.  That comparison is only a control if rung k is THE SAME EIGENFUNCTION in both
runs.  Nobody has ever measured whether it is -- the assumption is invisible in every number the
instrument produces, which is the shape this programme keeps finding.

THE MEASUREMENT.  For every window the programme owns, compare log10(lambda) of the LOWEST rungs
between N=100 and N=180, in units of the local rung GAP.  A displacement well below one gap means
the two bases resolve the same mode and the control is valid; a displacement of several gaps means
the larger basis has resolved modes the smaller one never saw, and rung k is a different object in
the two runs -- so the "control" is comparing two different ladders and its agreeing prefix means
nothing.

This reads STAGE A artefacts only (eigenvalues).  It reads no node count and cannot see p2.
"""
import glob, json, os, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, ".."))


def spec_files():
    """CORPUS BY CONTENT: every artefact under data/ that is a stage-A spectrum, i.e. carries
    rungs[] with a log10 field and declares x, N, dps.  No filename pattern is used to decide."""
    out = []
    for root, dirs, fs in os.walk(DATA):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in fs:
            if not f.endswith(".json"):
                continue
            p = os.path.join(root, f)
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if (isinstance(d, dict) and isinstance(d.get("rungs"), list) and d["rungs"]
                    and isinstance(d["rungs"][0], dict) and "log10" in d["rungs"][0]
                    and all(k in d for k in ("x", "N", "parity")) and len(d["rungs"]) > 20):
                out.append((os.path.relpath(p, DATA), d))
    return sorted(out)


def main():
    specs = spec_files()
    by = {}
    for rel, d in specs:
        by.setdefault((d["x"], d["parity"]), {})[d["N"]] = (rel, d)
    rows = []
    for (x, par), byN in sorted(by.items()):
        if 100 not in byN or 180 not in byN:
            continue
        (r100, d100), (r180, d180) = byN[100], byN[180]
        l100 = [Decimal(r["log10"]) for r in d100["rungs"][:6] if r["log10"]]
        l180 = [Decimal(r["log10"]) for r in d180["rungs"][:6] if r["log10"]]
        gap = float(l100[1] - l100[0])
        disp = float(l100[0] - l180[0])
        # how many rungs of the N=180 ladder sit BELOW the lowest rung the N=100 basis resolved
        below = sum(1 for v in [Decimal(r["log10"]) for r in d180["rungs"] if r["log10"]]
                    if v < l100[0])
        rows.append(dict(x=x, parity=par, N100_lowest=str(l100[0]), N180_lowest=str(l180[0]),
                         local_gap=round(gap, 4), displacement=round(disp, 4),
                         displacement_in_gaps=round(disp / gap, 3),
                         N180_rungs_below_the_N100_floor=below,
                         control_valid=bool(abs(disp / gap) < 0.5),
                         reading=("rung k is the same mode in both runs -- the N-control is a control"
                                  if abs(disp / gap) < 0.5 else
                                  "the larger basis resolved %d mode(s) the smaller never saw, so "
                                  "rung k is a DIFFERENT eigenfunction in the two runs and the "
                                  "agreeing prefix is not a convergence measurement" % below)))
    bad = [r for r in rows if not r["control_valid"]]
    out = dict(question="is the N-control comparing the same eigenfunction in both runs?",
               inputs="stage-A spectra only; no node count is read",
               corpus_rule="content: any json with rungs[] carrying log10 and declaring x/N/parity",
               spectra_found=len(specs), window_parity_pairs_compared=len(rows),
               invalid=len(bad), rows=rows,
               finding=("The N-control's validity is a MEASURED property of the window, not a "
                        "standing one. It degrades SILENTLY: nothing in the instrument's output "
                        "says the two ladders have come apart, and the failure looks like an "
                        "honest small trusted depth."))
    json.dump(out, open(os.path.join(HERE, "m2_c56_ncontrol_validity.json"), "w"), indent=1)
    print("%-5s %-6s %-14s %-14s %-9s %-8s %-7s %s" % ("x", "parity", "N100 lowest", "N180 lowest",
                                                       "gap", "displ", "in gaps", "control valid?"))
    for r in rows:
        print("%-5d %-6s %-14s %-14s %-9.4f %-8.4f %-7.3f %s"
              % (r["x"], r["parity"], r["N100_lowest"][:13], r["N180_lowest"][:13], r["local_gap"],
                 r["displacement"], r["displacement_in_gaps"], r["control_valid"]))
    print("%d of %d window/parity pairs have an INVALID N-control" % (len(bad), len(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
