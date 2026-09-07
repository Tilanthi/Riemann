#!/usr/bin/env python3
"""machine2 -- cycle 41 -- THE CIRCULAR CARRIER SWEEP.

WHY THIS EXISTS
  c40's falsifier F1 fired on VALUE: the c39 knob census's own output JSON,
  data/m2_c39_split_column.json, sat inside the corpus that the c40 recount indexed for CARRIERS and
  was read back as a carrier declaring a working precision, with print(f"dps={dps:4d}") parsed as a
  precision of 4 -- a FORMAT WIDTH, not a measurement.  Membership survived by luck.

  A MEASURING ARTEFACT LEFT INSIDE THE CORPUS IT MEASURES IS A CIRCULAR CARRIER.

WHAT IT MEASURES, and the two tiers are defined so the count cannot be argued about later
  TIER 1  STRICT self-ingestion: a scan's own declared output path falls inside that same scan's own
          input predicate.  This is the circular case.
  TIER 2  Instrument artefact in the measured corpus: the output of ANY of our instruments falls
          inside SOME scan's input predicate.  Wider, and it is the population TIER 1 lives in.

TWO DETERMINATIONS, AND THEY MEASURE DIFFERENT SETS ON PURPOSE (c40's law: when two careful counts
disagree by a factor, the first hypothesis is that they measure different sets)
  A  CODE-DECLARED.  Output paths extracted BY MACHINE from the code that writes them: open(...,'w'),
     json.dump/np.save/savefig/write_text/to_csv, and argparse --*-out defaults.  A LOWER BOUND: a
     file produced by shell redirection (`python s.py > data/s.out`) is invisible to it, and that is
     how most of our .out files were made.
  B  EXTENSION-CLASS.  Every tracked our-side file with an output-ish extension.  An UPPER BOUND on
     "instrument output" and a lower bound on nothing: a hand-written .json fixture counts here.
  Neither is "the" answer.  A and B are printed side by side with A\\B and B\\A enumerated.

SELF-EXCLUSION, per BEAST-AGI's c41 ruling, and it applies to THIS FILE FIRST
  This scan DECLARES its own output paths in SELF_OUTPUTS and EXCLUDES them from every set it
  reports, and it PRINTS the excluded count on every run.  A silent exclusion is a second way to
  look at nothing and feel fine.  If the excluded count is 0 the tool says so loudly, because 0 is
  also what a broken exclusion prints.

FAIL-CLOSED: the known-answer test runs first and the scan refuses to report if any control fails.
"""
import os, re, sys, json, subprocess, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m2_corpus_scope

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- self-declaration: this instrument's OWN outputs -------------------------------
# Declared, not inferred.  Every path this file can write must appear here.
SELF_OUTPUTS = (
    "data/m2_c41_selfoutput_sweep.json",
    "data/m2_c41_selfoutput_sweep.out",
    "data/m2_c41_selfoutput_sweep.tsv",
)
# One mechanism, not two: this scan goes through the same m2_corpus_scope every other scan uses, so
# the scope gate can SEE it.  A bespoke inline exclusion here would have been invisible to the gate
# -- an exclusion nobody can audit is the same shape as no exclusion.
SCOPE = m2_corpus_scope.declare(
    "m2_c41_selfoutput_sweep (circular-carrier sweep)",
    entitled="every tracked file (pdf excluded); our-side subset by the committed is_ours predicate",
    outputs=SELF_OUTPUTS,
    sources=("data/code/m2_c41_selfoutput_sweep.py", "data/code/m2_corpus_scope.py"))

OURS_PREFIX = ("machine2", "m2_", "machine2_", "c3")          # transcribed from m2_c39_knob_column.py
THEIRS_PREFIX = ("machine1", "machine3", "m3_", "m1_", "letter", "BEAST", "SAPIENS")

OUTPUT_EXT = (".out", ".json", ".tsv", ".csv", ".log", ".txt", ".stdout")


def is_ours(path):
    b = os.path.basename(path)
    if b.startswith(THEIRS_PREFIX):
        return False
    return b.startswith(OURS_PREFIX)


def tracked():
    out = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True, text=True).stdout
    return [f for f in out.split("\n") if f and not f.lower().endswith(".pdf")]


def read(p):
    try:
        return open(os.path.join(REPO, p), encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


# --- DETERMINATION A: code-declared output paths -----------------------------------
# Each pattern captures a quoted path-ish literal in a WRITING position.  Deliberately narrow:
# a false positive here inflates TIER 2, and this determination is published as a LOWER BOUND.
WRITE_PATTERNS = [
    re.compile(r"""open\(\s*(?:os\.path\.join\([^)]*\)|["'][^"']+["'])\s*,\s*["'][wa]b?["']"""),
    re.compile(r"""\.write_text\(""" ),
    re.compile(r"""to_csv\(\s*["'][^"']+["']"""),
    re.compile(r"""savefig\(\s*["'][^"']+["']"""),
    re.compile(r"""np\.save[a-z_]*\(\s*["'][^"']+["']"""),
]
# path-ish quoted literals, and os.path.join(R, "data", "x.json") triples
QUOTED = re.compile(r"""["']([^"'\s]{3,120})["']""")
JOIN = re.compile(r"""os\.path\.join\(\s*[A-Za-z_][A-Za-z_0-9]*\s*,\s*((?:["'][^"']+["']\s*,\s*)*["'][^"']+["'])\s*\)""")
ARG_OUT = re.compile(r"""add_argument\(\s*["']--[a-z0-9-]*out[a-z0-9-]*["'][^)]*default\s*=\s*["']([^"']+)["']""")


def _norm(p):
    p = p.strip().lstrip("./")
    return p


# A path expression in ARGUMENT POSITION of a writing call.  PROXIMITY IS NOT ENOUGH and that is a
# measured fact, not a preference: `json.load(open(<read>))` on one line and `json.dump(..)` on the
# next sit inside any window wide enough to be useful.  The discriminator has to be the ARGUMENT
# SLOT, so these regexes capture the expression itself.
W_OPEN = re.compile(r"""open\(\s*([^,()]*(?:\([^()]*\))?[^,()]*)\s*,\s*["'][wa]b?\+?["']""")
W_CALL = re.compile(r"""(?:\.write_text|\.to_csv|savefig|np\.save[a-z_]*)\(\s*([^,()]*(?:\([^()]*\))?[^,()]*)\s*[,)]""")
EXPR_JOIN = re.compile(r"""os\.path\.join\(\s*[A-Za-z_][A-Za-z_0-9]*\s*,\s*((?:["'][^"']+["']\s*,\s*)*["'][^"']+["'])\s*\)""")
EXPR_STR = re.compile(r"""^\s*["']([^"']+)["']\s*$""")
IDENT = re.compile(r"""^\s*([A-Za-z_][A-Za-z_0-9.]*)\s*$""")


def _resolve(expr, txt, depth=0):
    """Resolve a path EXPRESSION to a repo-relative path, or None.

    Handles: a quoted literal; os.path.join(ROOT, "a", "b"); and ONE level of variable indirection
    (`out = os.path.join(R,"data","x.json") ... open(out,"w")`), which is the dominant idiom in our
    own scripts and would otherwise make this determination near-empty."""
    e = expr.strip()
    m = EXPR_STR.match(e)
    if m:
        return _norm(m.group(1))
    m = EXPR_JOIN.search(e)
    if m:
        parts = re.findall(r"""["']([^"']+)["']""", m.group(1))
        return _norm("/".join(parts))
    m = IDENT.match(e)
    if m and depth < 2:
        var = re.escape(m.group(1))
        asg = re.findall(r"""(?m)^\s*%s\s*=\s*(.+)$""" % var, txt)
        for rhs in reversed(asg):                      # last assignment wins
            r = _resolve(rhs, txt, depth + 1)
            if r:
                return r
    return None


def code_declared_outputs(files):
    """-> {repo-relative path: set(producing script)}.  LOWER BOUND (shell redirection invisible)."""
    prod = collections.defaultdict(set)
    scripts = [f for f in files if f.endswith((".py", ".sh", ".gp")) and is_ours(f)]
    for s in scripts:
        txt = read(s)
        cands = set()
        for rx in (W_OPEN, W_CALL):
            for m in rx.finditer(txt):
                r = _resolve(m.group(1), txt)
                if r and not r.startswith("/") and "{" not in r and "%" not in r:
                    cands.add(r)
        for m in ARG_OUT.finditer(txt):
            cands.add(_norm(m.group(1)))
        for c in cands:
            prod[c].add(s)
            if not c.startswith("data/"):
                prod["data/" + c].add(s)
    return prod


# --- INPUT PREDICATES of every corpus scan we own ----------------------------------
# Transcribed from the committed source of each scan.  If a predicate here disagrees with the
# committed scan, THIS FILE is wrong -- the scan is the authority and the transcription is the claim.
def pred_lint_targets(f):
    """m2_c39_width_lint.py --letters/--code: repo-root machine2*.md, data/code/{m2_,machine2}*.py"""
    b = os.path.basename(f)
    if "/" not in f and b.startswith("machine2") and b.endswith(".md"):
        return True
    return f.startswith("data/code/") and b.endswith(".py") and b.startswith(("m2_", "machine2"))


def pred_lint_exemption(f):
    """m2_c39_width_lint.py build_artefact_index(subdirs=('data',)): EVERY file under data/**.

    Note it walks the WORKING TREE, not git ls-files, so an untracked scratch file also exempts."""
    return f.startswith("data/")


def pred_knob_carrier(f):
    """m2_c39_knob_column.py / m2_c40_rule_k_impl_{A,B}.py: tracked, ours, non-.md."""
    return (not f.endswith(".md")) and is_ours(f)


def pred_knob_index_md(f):
    """m2_c39_knob_column.py also reads .md for the appearance index."""
    return f.endswith(".md")


SCANS = [
    ("lint-TARGETS      (m2_c39_width_lint --letters --code)", pred_lint_targets),
    ("lint-EXEMPTION    (m2_c39_width_lint build_artefact_index)", pred_lint_exemption),
    ("knob-CARRIER      (m2_c39_knob_column / m2_c40_rule_k_impl_A,B)", pred_knob_carrier),
    ("knob-APPEARANCE   (m2_c39_knob_column .md side)", pred_knob_index_md),
]

# Which scan OWNS which output path (for TIER 1).  Declared, not inferred.
SCAN_OWN_OUTPUTS = {
    "lint-TARGETS      (m2_c39_width_lint --letters --code)": (),
    "lint-EXEMPTION    (m2_c39_width_lint build_artefact_index)": (),
    "knob-CARRIER      (m2_c39_knob_column / m2_c40_rule_k_impl_A,B)":
        ("data/m2_c39_split_column.json", "data/m2_c39_split_column.tsv",
         "data/m2_c39_published_constants_census_split.tsv",
         "data/m2_c40_rule_k_A.json", "data/m2_c40_rule_k_B.json"),
    "knob-APPEARANCE   (m2_c39_knob_column .md side)": (),
}

# --- C3: does any committed file under data/ contain LINT OUTPUT? ------------------
LINT_OUTPUT_MARK = re.compile(
    r"RULE A untraceable literal|RULE B claims|SCANNED \d+ objects \| RULE A hits|"
    r"known-answer test: \d+/\d+ controls PASS|artefact index: \d+ exponent buckets")


def selftest(verbose=True):
    """KNOWN-ANSWER TEST.  Fail-closed: the sweep refuses to report if any control fails."""
    ok, n = True, 0
    def chk(name, cond):
        nonlocal ok, n
        n += 1
        if not cond:
            ok = False
            print("  CONTROL FAIL: %s" % name)
        elif verbose:
            print("  ok: %s" % name)

    # POS-1: a file this scan writes MUST be recognised as its own output.
    chk("POS-1 SELF_OUTPUTS is non-empty and every entry is repo-relative",
        len(SELF_OUTPUTS) > 0 and all(not p.startswith("/") for p in SELF_OUTPUTS))
    # POS-2: the c40 instance MUST be detected as TIER 1 by the declared predicates.
    chk("POS-2 the c40 circular carrier is TIER 1 under the transcribed predicates",
        pred_knob_carrier("data/m2_c39_split_column.json") and
        "data/m2_c39_split_column.json" in SCAN_OWN_OUTPUTS[SCANS[2][0]])
    # NEG-1: a .md letter must NOT be a carrier (the knob predicate excludes .md).
    chk("NEG-1 a machine2 .md letter is not in the carrier set",
        not pred_knob_carrier("machine2-c40-RECONCILED.md"))
    # NEG-2: machine1's output must not be attributed to us.
    chk("NEG-2 machine1 output is not ours", not is_ours("data/machine1_cycle16_zeros234_partial.out"))
    # POS-3: the lint exemption predicate must be TRUE for a data/ output (that is the whole point).
    chk("POS-3 lint EXEMPTION ingests data/ outputs", pred_lint_exemption("data/m2_c38_runs.out"))
    # NEG-3: the lint exemption predicate must be FALSE for a repo-root letter.
    chk("NEG-3 lint EXEMPTION does not ingest repo-root letters",
        not pred_lint_exemption("machine2-c40-RECONCILED.md"))
    # POS-4: the lint-output marker must fire on a real lint stdout line.
    chk("POS-4 lint-output marker fires on genuine lint stdout",
        bool(LINT_OUTPUT_MARK.search("    RULE A untraceable literal (13 s.f.): 1.234567890123")))
    # NEG-4: the marker must NOT fire on ordinary prose that merely mentions RULE A.
    chk("NEG-4 lint-output marker does not fire on prose mentioning RULE A",
        not LINT_OUTPUT_MARK.search("RULE A was amended in c39 and its counts were inflated."))
    # POS-5: code-declared extraction must find an output in a file that plainly writes one.
    probe = 'import json\nout = os.path.join(R, "data", "probe_x.json")\njson.dump(d, open(out, "w"))\n'
    tmp = os.path.join(REPO, "data", "code", "m2_c41__selftest_probe.py")
    try:
        open(tmp, "w").write(probe)
        got = code_declared_outputs(["data/code/m2_c41__selftest_probe.py"])
        chk("POS-5 code-declared extraction finds data/probe_x.json", "data/probe_x.json" in got)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    # NEG-6: a path that is only READ must not be reported as an output, even when the same file
    # writes something else.  This is the A-vs-B false positive, promoted to a control.
    tmp3 = os.path.join(REPO, "data", "code", "m2_c41__selftest_probe3.py")
    try:
        open(tmp3, "w").write(
            'm3 = json.load(open(os.path.join(R, "data/code/m3_read_only.json")))\n'
            'json.dump(x, open(os.path.join(R, "data", "m2_written.json"), "w"))\n')
        got3 = code_declared_outputs(["data/code/m2_c41__selftest_probe3.py"])
        chk("NEG-6 a read-only path is not reported as an output",
            "data/code/m3_read_only.json" not in got3 and "data/m2_written.json" in got3)
    finally:
        if os.path.exists(tmp3):
            os.remove(tmp3)
    # NEG-5: a file with no writing construct contributes nothing.
    tmp2 = os.path.join(REPO, "data", "code", "m2_c41__selftest_probe2.py")
    try:
        open(tmp2, "w").write('p = "data/never_written.json"\nprint(p)\n')
        got2 = code_declared_outputs(["data/code/m2_c41__selftest_probe2.py"])
        chk("NEG-5 a non-writing file declares no outputs", len(got2) == 0)
    finally:
        if os.path.exists(tmp2):
            os.remove(tmp2)
    globals()["_N_CONTROLS"] = n
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", default="")
    ap.add_argument("--quiet-selftest", action="store_true")
    a = ap.parse_args()

    print("=== KNOWN-ANSWER TEST (runs first; fail-closed) ===")
    if not selftest(verbose=not a.quiet_selftest):
        print("REFUSING TO REPORT: a control failed.")
        sys.exit(2)
    print("known-answer test: %d/%d controls PASS\n" % (_N_CONTROLS, _N_CONTROLS))

    files = tracked()

    # ---- SELF-EXCLUSION, printed, per the c41 ruling -----------------------------
    files = SCOPE.apply(files)
    SCOPE.report()
    excluded = SCOPE._removed_self

    ours = [f for f in files if is_ours(f)]
    print("CORPUS: %d tracked files (pdf excluded), %d ours by the committed is_ours predicate\n"
          % (len(files), len(ours)))

    # ---- DETERMINATION A ---------------------------------------------------------
    prodA = code_declared_outputs(files)
    A = sorted(p for p in prodA if p in set(files))
    # ---- DETERMINATION B ---------------------------------------------------------
    B = sorted(f for f in ours if f.endswith(OUTPUT_EXT))
    print("DETERMINATION A (code-declared, LOWER BOUND -- shell redirection is invisible to it): "
          "%d tracked files" % len(A))
    print("DETERMINATION B (extension-class over our-side tracked files, UPPER BOUND on "
          "'instrument output'): %d tracked files" % len(B))
    sA, sB = set(A), set(B)
    print("  A and B agree on %d; A\\B = %d; B\\A = %d" % (len(sA & sB), len(sA - sB), len(sB - sA)))
    if sA - sB:
        print("  A\\B (code-declared but not our-side output-extension):")
        for f in sorted(sA - sB)[:20]:
            print("    %s   <- %s" % (f, ",".join(sorted(prodA[f]))))
    print()

    # ---- TIER 2: instrument output inside some scan's input predicate ------------
    print("=== TIER 2 -- instrument artefact inside a scan's input set ===")
    tier2 = {}
    for name, pred in SCANS:
        inA = [f for f in A if pred(f)]
        inB = [f for f in B if pred(f)]
        tier2[name] = (len(inA), len(inB))
        print("  %-58s ingests A:%4d  B:%4d" % (name, len(inA), len(inB)))
    print()

    # ---- TIER 1 (MACHINE-DERIVED SCAN POPULATION) --------------------------------
    # 🔴 The hand-picked four-scan table below gave a DIFFERENT ANSWER from this one, and this
    # cycle is about exactly that: I chose the scan population by hand, in the cycle whose subject
    # is undeclared scope.  A hand classification is a detector too (c39).  The machine-derived
    # population is every our-side .py that calls ls-files / os.walk / rglob / glob.glob; the input
    # region is COARSE -- ls-files means the whole tracked tree, os.walk(X) means the X subtree --
    # and it ignores each scan's type filters, so this arm OVER-reports and is an UPPER BOUND.
    print("=== TIER 1 (machine-derived population, COARSE input region -> UPPER BOUND) ===")
    scan_files = [f for f in files
                  if f.startswith("data/code/") and f.endswith(".py")
                  and os.path.basename(f).startswith(("m2_", "machine2"))
                  and re.search(r"ls-files|os\.walk|rglob|glob\.glob", read(f))]
    prod_all = code_declared_outputs(files)
    by_script = collections.defaultdict(set)
    for path, scripts in prod_all.items():
        for s in scripts:
            by_script[s].add(path)
    n_circ = 0
    for s in sorted(scan_files):
        txt = read(s)
        whole_tree = bool(re.search(r"ls-files", txt))
        roots = re.findall(r"os\.walk\(\s*([^)]*)\)", txt)
        walks_repo = any(("REPO" in r or r.strip() in ("R", "R,")) and '"' not in r for r in roots)
        outs = sorted(o for o in by_script.get(s, ()) if o in set(files))
        circ = outs if (whole_tree or walks_repo) else []
        if circ:
            n_circ += 1
        print("  %-46s tracked outputs %d  region %-12s %s"
              % (s.replace("data/code/", ""), len(outs),
                 "whole-tree" if (whole_tree or walks_repo) else "sub-tree",
                 "CIRCULAR" if circ else "clean"))
        for o in circ:
            print("      -> %s" % o)
    print("  scans in the machine-derived population: %d; TIER 1 (coarse): %d\n"
          % (len(scan_files), n_circ))

    # ---- TIER 1: strict self-ingestion -------------------------------------------
    print("=== TIER 1 -- STRICT self-ingestion (a scan's OWN output inside its OWN input set) ===")
    tier1 = {}
    for name, pred in SCANS:
        own = [p for p in SCAN_OWN_OUTPUTS.get(name, ()) if p in set(files)]
        circ = [p for p in own if pred(p)]
        tier1[name] = circ
        flag = "CIRCULAR" if circ else "clean"
        print("  %-58s own outputs tracked:%2d  self-ingested:%2d  %s"
              % (name, len(own), len(circ), flag))
        for p in circ:
            print("      -> %s" % p)
    n_tier1_scans = sum(1 for v in tier1.values() if v)
    print("  TIER 1 scans: %d of %d" % (n_tier1_scans, len(SCANS)))
    print()

    # ---- C3: is LINT OUTPUT sitting inside the LINT'S OWN EXEMPTION INDEX? -------
    print("=== C3 -- does the width lint's EXEMPTION index contain lint OUTPUT? ===")
    hits = []
    for f in files:
        if not pred_lint_exemption(f):
            continue
        t = read(f)
        if LINT_OUTPUT_MARK.search(t):
            hits.append(f)
    print("  tracked files under data/ containing a lint-output signature: %d" % len(hits))
    for f in hits:
        print("    %s" % f)
    # working-tree (untracked) arm: the exemption index walks the tree, not the index
    wt = []
    for dp, _, fns in os.walk(os.path.join(REPO, "data")):
        for fn in fns:
            p = os.path.relpath(os.path.join(dp, fn), REPO)
            if p in set(files) or p in SELF_OUTPUTS:
                continue
            if os.path.getsize(os.path.join(REPO, p)) > 40_000_000:
                continue
            if LINT_OUTPUT_MARK.search(read(p)):
                wt.append(p)
    print("  UNTRACKED files under data/ containing a lint-output signature: %d "
          "(the exemption index walks the working tree, not git ls-files)" % len(wt))
    for f in wt:
        print("    %s" % f)
    print()

    result = {
        "self_declared_outputs": list(SELF_OUTPUTS),
        "self_excluded_tracked": excluded,
        "n_tracked": len(files), "n_ours": len(ours),
        "A_code_declared": A, "B_extension_class": B,
        "tier2": {k: {"A": v[0], "B": v[1]} for k, v in tier2.items()},
        "tier1": {k: v for k, v in tier1.items()},
        "c3_lint_output_in_exemption_index_tracked": hits,
        "c3_lint_output_in_exemption_index_untracked": wt,
    }
    if a.json_out:
        json.dump(result, open(a.json_out, "w"), indent=1)
        print("written: %s" % a.json_out)


if __name__ == "__main__":
    main()
