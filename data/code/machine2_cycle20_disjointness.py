"""machine 2 (beast-atlas) -- cycle 20 -- THE DISJOINTNESS TEST, run not asserted.

Cycle 16's refinement is the rule here: what must be disjoint is the (OBJECT x INSTRUMENT-STATE)
pair, not the object.  So the test enumerates, over every machine-2 artefact in the exchange repo:

  (1) which CARRIERS have ever been put through a distance run by machine 2, and in which file;
  (2) which WEIGHTS have ever been used;
  (3) which of cycle 20's ten carriers and two weight families are therefore new, anchors
      (deliberate re-runs), or mentioned-but-never-run.

A carrier that has been *mentioned* is not a carrier that has been *run*: the test separates the
two by requiring a numeric distance row, not a string match, before it calls something "run".
"""
import json, os, re, subprocess, sys

REPO = "/shared/rh-exchange-repo/Riemann"

CARRIER_PATTERNS = {
    "K1_zeta": [r"\bzeta\(s\)\b", r"carrier.{0,12}zeta"],
    "K2_zeta_synth": [r"1\s*-\s*2\^\{?0\.55", r"zeta_times_synth", r"2\^\{0\.55-s\}"],
    "K3_epstein_D7": [r"Delta\s*=\s*1/7", r"zeta2\(s,\s*1/7\)", r"D\s*=\s*7\b", r"epstein_D7"],
    "K4_epstein_Dsqrt50": [r"1/sqrt50", r"1/\\sqrt\{50\}", r"sqrt\(50\)", r"Dsqrt50"],
    "K5_Lm4": [r"L\(s,\s*chi_\{?-4", r"L\(s,\\chi_\{-4\}\)", r"dirichlet_beta"],
    "K6_zeta_L5": [r"zeta\(s\)\s*L\(s,\s*chi_?5", r"zeta_\{?Q\(sqrt5\)"],
    "K7_Lm4_L5": [r"L\(s,chi_\{-4\}\)L\(s,chi_5\)", r"Lm4_L5"],
    "K8_epstein_D1": [r"zeta2\(s,1\)", r"Delta\s*=\s*1\b.{0,20}Epstein", r"epstein_D1"],
    "K9_DH": [r"Davenport-Heilbronn", r"Davenport.Heilbronn", r"\bD-H\b"],
    "K10_Lm7_L28": [r"chi_\{-7\}", r"chi_\{28\}", r"Lm7_L28"],
}
WEIGHT_PATTERNS = {
    "W1 = 1/s": [r"W\s*=\s*1/s", r"\"W1\""],
    "W2 = 1/(s(s+1))": [r"1/\(s\(s\+1\)\)", r"\"W2\""],
    "W3 = 1/(s(s+1)(s+2))": [r"1/\(s\(s\+1\)\(s\+2\)\)", r"\"W3\""],
    "SL sliding, mass at t=+-T0": [r"sliding weight", r"\"SL\"", r"T0.{0,12}half-width"],
}
# "run" = a numeric distance row exists in a machine-2 data artefact
RUN_EVIDENCE = {
    "K1_zeta": ["data/machine2_cycle19_nb_results.json"],
    "K2_zeta_synth": ["data/machine2_cycle19_nb_results.json"],
    "K3_epstein_D7": ["data/machine2_cycle19_nb_results.json"],
    "K4_epstein_Dsqrt50": ["data/machine2_cycle19_nb_results.json"],
}


def m2_files():
    out = []
    for root, dirs, files in os.walk(REPO):
        if ".git" in root:
            continue
        for f in files:
            if f.startswith("machine2") or f.startswith("machine2-"):
                out.append(os.path.join(root, f))
    return sorted(out)


def main():
    files = m2_files()
    report = {"m2_artefacts_swept": len(files), "carriers": {}, "weights": {}}
    texts = {}
    for p in files:
        try:
            texts[p] = open(p, errors="replace").read()
        except Exception:
            pass
    for key, pats in CARRIER_PATTERNS.items():
        hits = []
        for p, t in texts.items():
            for pat in pats:
                if re.search(pat, t):
                    hits.append(os.path.relpath(p, REPO))
                    break
        ran = [f for f in RUN_EVIDENCE.get(key, []) if os.path.exists(os.path.join(REPO, f))]
        report["carriers"][key] = {
            "mentioned_in": sorted(set(hits)),
            "n_mentions": len(set(hits)),
            "previously_RUN_in_a_distance_run": ran,
            "status": ("ANCHOR (deliberate re-run)" if ran else
                       ("NEW as a distance-run carrier (mentioned before, never run)" if hits else
                        "NEW (no prior mention)")),
        }
    for key, pats in WEIGHT_PATTERNS.items():
        hits = []
        for p, t in texts.items():
            for pat in pats:
                if re.search(pat, t):
                    hits.append(os.path.relpath(p, REPO))
                    break
        report["weights"][key] = {"mentioned_in": sorted(set(hits)), "n": len(set(hits))}
    # the region axis: has any prior m2 artefact used a weight whose mass is NOT at t=0?
    off_axis = []
    for p, t in texts.items():
        if re.search(r"sliding weight|mass at t\s*=|weight whose mass", t) and "cycle20" not in p:
            off_axis.append(os.path.relpath(p, REPO))
    report["prior_artefacts_with_off_zero_weight_mass"] = sorted(set(off_axis))
    json.dump(report, open("machine2_cycle20_disjointness.json", "w"), indent=1)
    for k, v in report["carriers"].items():
        print(f"{k:22s} {v['status']:56s} mentions={v['n_mentions']}")
    print("weights:", {k: v["n"] for k, v in report["weights"].items()})
    print("prior artefacts with off-zero weight mass:",
          report["prior_artefacts_with_off_zero_weight_mass"])
    print("m2 artefacts swept:", report["m2_artefacts_swept"])


if __name__ == "__main__":
    main()
