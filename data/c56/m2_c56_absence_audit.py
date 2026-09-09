#!/usr/bin/env python3
"""m2_c56_absence_audit.py -- C4: audit every NEGATIVE / ABSENCE check in this cycle's gate set
against the possibility that a CORRECTLY MARKED correction makes it fire falsely.

WHY (BEAST-AGI, c55 ruling).  Our ERRATUM-28 repair PRESERVED the superseded hedge and marked it,
which is the right way to correct a record.  The consequence is that `grep "not quite right"` now
returns TWO hits at origin, so a naive absence check reports the erratum as STILL hedged.  In the
same hour a fleet prompt-edit guard asserted the absence of a string its own approved replacement
contained.  ⇒ A CORRECTION DONE PROPERLY MAKES EVERY NEGATIVE-SUBSTRING CHECK ON THE CORRECTED
WORDING RETURN A FALSE POSITIVE -- the better the correction hygiene, the more reliably the cheap
check is wrong.

CORPUS, DECLARED BEFORE IT IS FILTERED (c41).  "This cycle's gate set" is made explicit: every .py
and .sh under the cycle lineage data/c53..c56 (c56 imports c53 and inherits c55's gates), plus the
fleet tools this cycle actually invoked.  Every file is listed in the artefact whether or not it
contains an absence check, so the denominator is visible and not chosen after the fact.

CLASSIFICATION is by MEASUREMENT of the matched line, not by the author's sense of what the file
does; and the classification is itself KATed on planted lines whose answers are known.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(DATA, ".."))

# --- the detector: a line whose PASS condition is that something is NOT found -------------------
PATTERNS = [
    (r"\bnot\s+in\b", "python `not in`"),
    (r"\.count\([^)]*\)\s*==\s*0", "python .count(...) == 0"),
    (r"\bnot\s+re\.(search|match|findall)", "python not re.search"),
    (r"if\s+not\s+.*\.(find|index)\(", "python not .find("),
    (r"grep\s+-[a-zA-Z]*v", "shell grep -v"),
    (r"!\s*grep", "shell ! grep"),
    (r"grep\s+-[a-zA-Z]*q[^|]*\|\|", "shell grep -q ||"),
    (r"-eq\s+0\s*\]", "shell count -eq 0"),
    (r"\[\s*!\s*-e", "shell [ ! -e ]"),
    (r"\[\s*-e\b", "shell [ -e ] (file existence)"),
    (r"\babsen(t|ce)\b", "self-declared absence check"),
]
# a matched line is WORDING-absence (the C4-vulnerable class) only if the thing it looks for is a
# quoted natural-language string of >= 3 words.  Everything else is structural.
WORDS = re.compile(r"""['"]([^'"]{6,})['"]""")


# 🔴 PASS 2, ADDED AFTER PASS 1 WAS RUN AND ITS RESULT KEPT.  Pass 1 flagged 30 lines "vulnerable"
# and most were this tool's OWN regex table and its own print statements -- prose sitting next to a
# negative token, with no control flow.  The planted KAT passed 8/8 and the detector was still wrong
# on the real corpus, because the planted set contained no `print("... absence ...")` line: a KAT
# tests the ANTECEDENT, never the POPULATION.  Both counts are reported; pass 1 is not deleted.
CONTROL_FLOW = re.compile(r"(\bif\b|\bassert\b|\bwhile\b|\belif\b|\breturn\b|\bexit\b|"
                          r"==|!=|\bnot in\b|-eq|-ne|\|\||&&|\[\s|\btest\b)")
OUTPUT_ONLY = re.compile(r"^\s*(print|echo|#|\"|')")


# 🔴 PASS 3.  Pass 2's KAT went 10/11: a bare `grep -v "..." file` in a pipeline IS an absence
# check and has no control flow on its own line, so requiring control flow of EVERY match threw a
# genuine class away.  Strong negatives (an explicitly negative operator) are checks on sight; weak
# indicators (a file test, a zero comparison, the word "absence") need control flow to count.
# The KAT caught this -- which is the whole argument for KATing a hand classification.
STRONG = ("python `not in`", "python .count(...) == 0", "python not re.search",
          "python not .find(", "shell grep -v", "shell ! grep", "shell grep -q ||")
# content rule, not a filename rule: a line that IS a planted (literal, expected) KAT row is data.
KAT_ROW = re.compile(r"""^\s*\(\s*(r?['"]).*\1\s*,\s*(True|False|None)\s*\),?\s*$""")


def is_a_check(line):
    """a CHECK participates in control flow or an assertion; a line that only PRINTS the word
    'absence', or a regex in a data table, is not a check no matter what words it contains."""
    st = line.strip()
    if st.startswith("#") or st.startswith("//"):
        return False
    if KAT_ROW.match(st):
        return False
    if OUTPUT_ONLY.match(st) and not re.search(r"(\bif\b|&&|\|\||==|!=|-eq)", st):
        return False
    if re.match(r"^\s*\(r[\"']", st):          # a regex row in a PATTERNS-style data table
        return False
    return bool(CONTROL_FLOW.search(line))


QUOTED = re.compile(r"""(['"]).*?\1""")


def classify(line, strict=True):
    kinds = [name for pat, name in PATTERNS if re.search(pat, line)]
    if not kinds:
        return None
    # 🔴 PASS 4.  A negative operator that appears ONLY INSIDE A QUOTED STRING is not an operator,
    # it is a QUOTATION of one -- which is the very confusion this whole condition is about (a
    # wording being USED versus a wording being CITED).  Strip the literals and re-test.
    if strict:
        bare = QUOTED.sub("", line)
        if not any(re.search(pat, bare) for pat, _ in PATTERNS):
            return None
    if strict and not any(k in STRONG for k in kinds) and not is_a_check(line):
        return None
    if strict and KAT_ROW.match(line.strip()):
        return None
    lits = [s for s in WORDS.findall(line) if len(s.split()) >= 3 and re.search(r"[a-z]{3} [a-z]{3}", s)]
    # 🔴 PASS 4 (b).  Only a check whose OPERAND is a WORDING can be broken by correction hygiene.
    # A file-existence test or a zero-count test cannot be: no amount of good marking reintroduces
    # a FILE.  So vulnerability requires an explicitly negative operator AND a prose operand.
    strong = [k for k in kinds if k in STRONG]
    vuln = bool(lits and strong)
    return dict(kinds=kinds, strong_kinds=strong, prose_literals=lits,
                vulnerable=vuln,
                why=("asserts the ABSENCE of a natural-language wording -> a preserved-and-marked "
                     "superseded wording makes it fire falsely"
                     if vuln else
                     "structural absence (file, key, flag, count) -- correction hygiene cannot "
                     "reintroduce the thing it looks for"))


def kat():
    """A HAND CLASSIFICATION IS A DETECTOR TOO -- KAT it on planted lines with known answers."""
    planted = [
        ('if "not quite right" not in open(f).read(): ok()', True),
        ('assert text.count("the framing is not quite right") == 0', True),
        ('grep -v "this wording is now superseded" file', True),
        ('[ -e "the file we must not have yet" ] && fail', False),
        ('if key not in d: raise', False),
        ('[ -e "$f" ] || continue', False),
        ('if x not in (1, 2, 3): fail()', False),
        ('miss=$((miss+1)); [ "$present" -eq 0 ]', False),
        ('nothing negative here at all', None),
        # planted for PASS 2 -- the class the pass-1 KAT could not see:
        ('    print("PRE-LAUNCH ABSENCE: nothing of the run exists yet")', None),
        ('    (r"\\babsen(t|ce)\\b", "self-declared absence check"),', None),
        ('# c55 asserted the absence of "the framing is not quite right"', None),
    ]
    rows = []
    for line, expect in planted:
        got = classify(line)
        got_v = None if got is None else got["vulnerable"]
        rows.append(dict(line=line, expected=expect, got=got_v, agree=bool(got_v == expect)))
    return dict(rows=rows, passed=all(r["agree"] for r in rows),
                note="planted inputs, not real ones: a KAT built from your own data would have "
                     "passed under the defect (c54)")


def main():
    corpus = []
    for sub in ("c53", "c54", "c55", "c56"):
        d = os.path.join(DATA, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith((".py", ".sh")):
                corpus.append(os.path.join(d, f))
    for f in ("/shared/bin/stampnow.sh", "/shared/bin/stampwrite.sh", "/shared/bin/memfile-audit.py",
              "/shared/bin/memfile-alarm.sh", "/shared/bin/absence-claim.sh"):
        if os.path.exists(f):
            corpus.append(f)

    files, hits, loose_only = [], [], []
    for p in corpus:
        try:
            txt = open(p, errors="replace").read().splitlines()
        except Exception:
            continue
        n = 0
        for i, line in enumerate(txt, 1):
            c = classify(line, strict=True)
            c_loose = classify(line, strict=False)
            if c_loose and not c:
                loose_only.append(dict(file=os.path.relpath(p, REPO) if p.startswith(REPO) else p,
                                       line_no=i, line=line.strip()[:160]))
            if c:
                n += 1
                hits.append(dict(file=os.path.relpath(p, REPO) if p.startswith(REPO) else p,
                                 line_no=i, line=line.strip()[:200], **c))
        files.append(dict(file=os.path.relpath(p, REPO) if p.startswith(REPO) else p,
                          lines=len(txt), absence_checks=n))

    vulnerable = [h for h in hits if h["vulnerable"]]

    # --- THE LIVE TEST: does the ruling's own example actually fire on our corrected record? -----
    def grep_count(pat, path):
        try:
            r = subprocess.run(["grep", "-c", "-F", pat, path], capture_output=True, text=True)
            return int(r.stdout.strip() or 0)
        except Exception:
            return -1
    erratum = None
    for f in os.listdir(REPO):
        if "ERRATUM-28" in f:
            erratum = os.path.join(REPO, f)
    live = dict(file=(os.path.basename(erratum) if erratum else None),
                hits_of_the_superseded_wording=(grep_count("not quite right", erratum) if erratum else None),
                hits_of_the_corrected_wording=(grep_count("false under the grader", erratum) if erratum else None))
    live["naive_absence_check_would_say"] = (
        "STILL HEDGED (false positive)" if (live["hits_of_the_superseded_wording"] or 0) > 0
        else "repaired")
    live["reading"] = ("The superseded wording is PRESENT because the repair preserved and marked "
                       "it, which is correct practice. Any check of the form 'the hedge is gone' "
                       "reports failure on a correctly repaired file. The check that works asks "
                       "whether every occurrence is MARKED, which is a positive claim about the "
                       "matched line -- not an absence claim about the file.")

    out = dict(condition="BEAST-AGI c55 ruling C4",
               corpus_rule="every .py/.sh in data/c53..c56 (the c56 gate lineage) + the fleet tools "
                           "this cycle invoked; every file listed, hit or not",
               denominator_files=len(files),
               denominator_lines=sum(f["lines"] for f in files),
               files_containing_an_absence_check=sum(1 for f in files if f["absence_checks"]),
               absence_checks_audited=len(hits),
               pass1_loose_matches_rejected_in_pass2=len(loose_only),
               pass1_rejected_detail=loose_only,
               pass1_note=("PASS 1 of this tool counted 101 matches and called 30 of them "
                           "vulnerable; most were its own regex table and its own print "
                           "statements. The planted KAT passed 8/8 while the detector was wrong on "
                           "the real corpus. Recorded, not deleted: a KAT tests the ANTECEDENT, "
                           "the population must be derived by MEASUREMENT."),
               vulnerable_to_correction_hygiene=len(vulnerable),
               vulnerable_detail=vulnerable,
               classifier_kat=kat(),
               live_test_on_our_own_corrected_erratum=live,
               files=files)
    json.dump(out, open(os.path.join(HERE, "m2_c56_absence_audit.json"), "w"), indent=1)
    print("CLASSIFIER KAT on planted lines: %s (%d/%d agree)"
          % ("PASS" if out["classifier_kat"]["passed"] else "FAIL",
             sum(1 for r in out["classifier_kat"]["rows"] if r["agree"]),
             len(out["classifier_kat"]["rows"])))
    print("DENOMINATOR: %d files, %d lines; %d files carry at least one absence check"
          % (out["denominator_files"], out["denominator_lines"], out["files_containing_an_absence_check"]))
    print("AUDITED: %d absence/negative checks; VULNERABLE to correction hygiene: %d"
          % (out["absence_checks_audited"], out["vulnerable_to_correction_hygiene"]))
    for h in vulnerable:
        print("   %s:%d  %s" % (h["file"], h["line_no"], h["line"][:120]))
    print("LIVE TEST on %s: superseded wording x%s, corrected wording x%s -> a naive check says: %s"
          % (live["file"], live["hits_of_the_superseded_wording"],
             live["hits_of_the_corrected_wording"], live["naive_absence_check_would_say"]))
    return 0 if out["classifier_kat"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
