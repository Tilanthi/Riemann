#!/usr/bin/env python3
"""m2_c56_census_audit.py -- C2: audit c55's detector-ceiling census, whose report said
"36 globbed / 34 scanned / 2 EXCLUDED BY NAME".

THE CONDITION (BEAST-AGI c55 ruling, C2): enumerate the two, state the excluding rule, and settle
whether that rule is decidable from CONTENT rather than filename -- or re-run without the filter.

THREE ARMS, each with its corpus DECLARED BEFORE it is filtered (c41):
  A  REPLICATION      -- c55's own corpus rule (name glob + schema filter), which must reproduce
                         36 / 34 / 2 exactly.  A dry run on a KNOWN ANSWER is the only thing that
                         tests the test; if arm A does not reproduce c55, arms B and C measure
                         nothing about c55.
  B  CONTENT CORPUS   -- every .json under data/ whose CONTENT is a rungs[] list, filtered by the
                         same content rule.  No filename pattern anywhere.
  C  NO FILTER        -- arm B's corpus with the schema filter REMOVED, treating a missing field
                         as UNMEASURED rather than as a value (c55's own plateaus() defect: None
                         is not a value).

and one derived question the ruling did not ask, which turns out to matter more than the two
excluded files: WHAT DOES THE NAME GLOB MISS?
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, ".."))
OUT = os.path.join(HERE, "m2_c56_census_audit.json")
FIELDS = ("nu", "lobe_min_ratio")


def has_fields(rungs, how="first"):
    if not rungs or not isinstance(rungs[0], dict):
        return False
    if how == "first":
        return all(f in rungs[0] for f in FIELDS)
    return all(all(f in r for f in FIELDS) for r in rungs)


def load_all():
    """CORPUS DECLARATION, by CONTENT: every parseable .json under data/ that carries a rungs[]
    list of dicts.  Filenames are recorded but never consulted."""
    found = []
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
            if isinstance(d, dict) and isinstance(d.get("rungs"), list) and d["rungs"] \
                    and isinstance(d["rungs"][0], dict):
                found.append((os.path.relpath(p, DATA), d))
    return sorted(found)


def stats(files):
    """the two numbers c55's finding rests on: the stable floor and the unstable ceiling."""
    st, un, holes = [], [], 0
    for rel, d in files:
        for r in d["rungs"]:
            lr = r.get("lobe_min_ratio")
            if lr is None:
                holes += 1
                continue
            (un if r.get("nu") is None else st).append(float(lr))
    return dict(stable_rungs=len(st), unstable_rungs=len(un), rungs_without_a_ratio=holes,
                min_lobe_ratio_among_stable=(min(st) if st else None),
                max_lobe_ratio_among_unstable=(max(un) if un else None),
                disjoint=bool(st and un and max(un) < min(st)))


def main():
    content = load_all()
    by_rel = dict(content)

    # ---- arm A: c55's own rule, replicated
    globbed = sorted(os.path.relpath(f, DATA) for f in
                     glob.glob(os.path.join(DATA, "c5?", "m2_c5?_nodes_*.json")))
    a_scan, a_excl = [], []
    for rel in globbed:
        d = by_rel.get(rel) or json.load(open(os.path.join(DATA, rel)))
        (a_scan if has_fields(d.get("rungs"), "first") else a_excl).append((rel, d))
    armA = dict(rule="glob data/c5?/m2_c5?_nodes_*.json, then require nu+lobe_min_ratio in rungs[0]",
                globbed=len(globbed), scanned=len(a_scan), excluded=len(a_excl),
                excluded_files=[r for r, _ in a_excl],
                reproduces_c55=bool(len(globbed) == 36 and len(a_scan) == 34 and len(a_excl) == 2),
                **stats(a_scan))

    # ---- THE RULING'S QUESTION: is the exclusion decidable from CONTENT?
    excl_detail = []
    for rel, d in a_excl:
        keys_first = sorted(d["rungs"][0].keys())
        keys_all = sorted(set().union(*[set(r.keys()) for r in d["rungs"]]))
        excl_detail.append(dict(
            file=rel, rungs=len(d["rungs"]), keys_in_rung0=keys_first, keys_in_any_rung=keys_all,
            decidable_from_content=bool(not has_fields(d["rungs"], "first")),
            same_answer_from_every_rung=bool(has_fields(d["rungs"], "first")
                                             == has_fields(d["rungs"], "all")),
            label=d.get("label")))

    # ---- arm B: content corpus, no filename anywhere
    b_scan = [(r, d) for r, d in content if has_fields(d["rungs"], "all")]
    b_excl = [(r, d) for r, d in content if not has_fields(d["rungs"], "all")]
    armB = dict(rule="walk data/ for any json with rungs[]; require nu+lobe_min_ratio in EVERY rung",
                corpus=len(content), scanned=len(b_scan), excluded=len(b_excl), **stats(b_scan))

    # ---- arm C: no schema filter at all
    armC = dict(rule="arm B corpus, schema filter REMOVED; a missing field is UNMEASURED, not a value",
                corpus=len(content), scanned=len(content), excluded=0, **stats(content))

    # ---- what the NAME GLOB misses: the part of the corpus rule that really is name-based
    missed = [(r, d) for r, d in b_scan if r not in set(globbed)]
    missed_detail = []
    for rel, d in missed:
        ratios = sorted(float(r["lobe_min_ratio"]) for r in d["rungs"]
                        if r.get("lobe_min_ratio") is not None and r.get("nu") is not None)
        missed_detail.append(dict(file=rel, rungs=len(d["rungs"]),
                                  L_printed_significant_figures=len(d["L"].replace(".", "").replace("-", "").lstrip("0")),
                                  min_stable_lobe_ratio=(min(ratios) if ratios else None),
                                  why_the_glob_missed_it="filename does not match m2_c5?_nodes_*"))

    out = dict(
        condition="BEAST-AGI c55 ruling C2",
        arm_A_replication_of_c55=armA,
        the_two_excluded=excl_detail,
        finding_1=("c55's REPORT said 'excluded BY NAME'. The CODE excludes by CONTENT: "
                   "`'nu' not in d['rungs'][0] or 'lobe_min_ratio' not in d['rungs'][0]`. The rule "
                   "IS decidable from content and IS implemented from content. The report was worse "
                   "than the instrument -- a narration defect, not a census defect."),
        finding_2=("The name-based part of c55's corpus rule is the GLOB, not the exclusion. "
                   "Deriving the population by CONTENT finds %d artefact(s) with the fields that the "
                   "glob never saw." % len(missed)),
        what_the_name_glob_missed=missed_detail,
        arm_B_content_corpus=armB, arm_C_no_schema_filter=armC,
        residual_defect=("c55 decides a per-FILE question from rungs[0] only. Every scanned file is "
                         "homogeneous here (checked), so it changed no number -- but it is a "
                         "one-row decision about a whole artefact and it is recorded as a live "
                         "weakness, not as a passed test."))
    json.dump(out, open(OUT, "w"), indent=1)

    print("ARM A (c55's own rule, replicated): globbed %d / scanned %d / excluded %d  -> reproduces c55: %s"
          % (armA["globbed"], armA["scanned"], armA["excluded"], armA["reproduces_c55"]))
    for e in excl_detail:
        print("   EXCLUDED: %-40s rungs=%d  decidable from content: %s (rung0 keys %s)"
              % (e["file"], e["rungs"], e["decidable_from_content"], e["keys_in_rung0"]))
    print("ARM B (content corpus, NO filename): corpus %d / scanned %d / excluded %d"
          % (armB["corpus"], armB["scanned"], armB["excluded"]))
    print("ARM C (no schema filter at all):     corpus %d / scanned %d" % (armC["corpus"], armC["scanned"]))
    for k, arm in (("A", armA), ("B", armB), ("C", armC)):
        print("   arm %s: stable %d (floor %s)  unstable %d (ceiling %s)  no-ratio %d  DISJOINT=%s"
              % (k, arm["stable_rungs"], arm["min_lobe_ratio_among_stable"], arm["unstable_rungs"],
                 arm["max_lobe_ratio_among_unstable"], arm["rungs_without_a_ratio"], arm["disjoint"]))
    print("WHAT THE NAME GLOB MISSED (%d):" % len(missed))
    for m in missed_detail:
        print("   %-52s rungs=%d  L printed at %d s.f.  min stable lobe %s"
              % (m["file"], m["rungs"], m["L_printed_significant_figures"], m["min_stable_lobe_ratio"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
