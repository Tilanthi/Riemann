#!/usr/bin/env python3
"""m2_c58_population_audit.py -- m1's REGISTER #188 TURNED ON MY OWN CODE.

m1-L203 sec 5 filed a defect of its own: its first check of our C4 sort-key claim scanned
`sorted(keys, reverse=True)[:40]`, which under `key = 9999999999 - epoch` is the OLDEST forty.  The
scan returned zero anomalies, and its own agreeing-quantity control passed through a different
selection path, so the green was real and the population was wrong.  The filed law:

    #188  A SCAN'S GREEN IS CONDITIONED ON AN UNASSERTED POPULATION.
          ASSERT THE POPULATION (it contains the known-extreme member) BEFORE READING THE RESULT.

A law filed against the other machine's code is worth exactly nothing until it is run against mine.
This file is that run.  Nothing here is a claim about m1.

THE DETECTOR, declared before the run.  AST, never grep -- a quotation of an idiom is not the idiom
(#189: a claim about what dominates a call is a claim about a parse tree).  A SCAN SITE is a
`Subscript` whose slice is a `Slice` (`X[:k]`, `X[-k:]`, `X[a:b]`) and whose sliced value is
POPULATION-DERIVED, meaning it is
    (a) a direct call to one of sorted / os.listdir / glob.glob / glob.iglob / list / dict.keys /
        os.walk / json.load(...)[...] indexing a list, or
    (b) a Name bound, anywhere in the enclosing function or module body, to such a call.
A scan site is GUARDED if the enclosing function (or module, for module-level sites) contains an
`assert`, or an `if ...: raise`, whose test mentions either the sliced Name or the population Name.
Otherwise it is UNGUARDED and is reported.

GENEROUS-TO-CODE BY CONSTRUCTION: any mention of the name inside any assert counts as a guard, so
the detector can only UNDER-report.  It is therefore a LOWER BOUND on #188 exposure.

DECLARED UNMEASURED: Python only; dynamically built slices; scans expressed with itertools.islice,
heapq.nsmallest, or an explicit loop with a counter.  Those are outside the detector, not absent.

CONTROLS, planted, firing worlds named here before the run:
  P1 planted POSITIVE : source with `sorted(names, reverse=True)[:40]` and no assert -> MUST FIRE.
  P2 planted NEGATIVE : the same source with an assert naming the population -> MUST NOT fire.
  P3 planted QUOTATION: the identical idiom inside a string literal only -> MUST NOT fire.
  P4 planted NEGATIVE : a slice of a literal list (not population-derived) -> MUST NOT fire.
If any control fails the run ABORTS and no census is reported.
"""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
POP_CALLS = {"sorted", "listdir", "glob", "iglob", "walk", "keys", "values", "items", "readlines",
             "split", "splitlines"}


def _callname(node):
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute):
            return f.attr
    return None


def _population_names(scope):
    """Names bound in this scope to a population-producing call."""
    out = set()
    for n in ast.walk(scope):
        if isinstance(n, ast.Assign):
            cn = _callname(n.value)
            if cn in POP_CALLS:
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        out.add(t.id)
    return out


def _guard_names(scope):
    """Names mentioned inside an assert test, or inside the test of an `if` that raises."""
    out = set()
    for n in ast.walk(scope):
        test = None
        if isinstance(n, ast.Assert):
            test = n.test
        elif isinstance(n, ast.If) and any(isinstance(s, ast.Raise) for s in n.body):
            test = n.test
        if test is not None:
            for m in ast.walk(test):
                if isinstance(m, ast.Name):
                    out.add(m.id)
                if isinstance(m, ast.Attribute):
                    out.add(m.attr)
    return out


def scan_sites(tree):
    """Yield (lineno, sliced_repr, population_kind) for every scan site in this tree."""
    scopes = [tree] + [n for n in ast.walk(tree)
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    seen = {}
    for scope in scopes:
        popnames = _population_names(scope) | _population_names(tree)
        guards = _guard_names(scope) | (_guard_names(tree) if scope is tree else set())
        for n in ast.walk(scope):
            if not (isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Slice)):
                continue
            v = n.value
            kind, key = None, None
            cn = _callname(v)
            if cn in POP_CALLS:
                kind, key = "call:%s" % cn, cn
            elif isinstance(v, ast.Name) and v.id in popnames:
                kind, key = "name:%s" % v.id, v.id
            if kind is None:
                continue
            guarded = key in guards
            prev = seen.get(n.lineno)
            if prev is None or (prev["guarded"] and not guarded):
                seen[n.lineno] = dict(lineno=n.lineno, population=kind, guarded=bool(guarded))
    return sorted(seen.values(), key=lambda r: r["lineno"])


P1 = """
import os
def check(d):
    names = sorted(os.listdir(d), reverse=True)
    newest = names[:40]
    return [n for n in newest if n.endswith('.md')]
"""
P2 = """
import os
def check(d):
    names = sorted(os.listdir(d), reverse=True)
    assert 'KNOWN.md' in names[:40], 'population does not contain the known-extreme member'
    newest = names[:40]
    return [n for n in newest if n.endswith('.md')]
"""
P3 = '''
def check(d):
    """documentation only: names = sorted(os.listdir(d), reverse=True); newest = names[:40]"""
    return "names = sorted(os.listdir(d), reverse=True)[:40]"
'''
P4 = """
def check():
    lit = [1, 2, 3, 4, 5]
    return lit[:2]
"""


def controls():
    def fires(src):
        return any(not s["guarded"] for s in scan_sites(ast.parse(src)))
    out = [("P1_planted_positive", fires(P1) is True, "must FIRE"),
           ("P2_planted_guarded", fires(P2) is False, "must NOT fire"),
           ("P3_planted_quotation", fires(P3) is False, "must NOT fire"),
           ("P4_planted_literal", fires(P4) is False, "must NOT fire")]
    return out


def main():
    ctrl = controls()
    print("CONTROLS")
    for name, ok, note in ctrl:
        print("  %-24s %s   (%s)" % (name, "PASS" if ok else "FAIL", note))
    if not all(ok for _, ok, _ in ctrl):
        print("\nABORT: a planted control failed.  No census is reported.")
        return 2

    files, unparseable = [], []
    for root, dirs, fs in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in sorted(fs):
            if f.endswith(".py"):
                files.append(os.path.join(root, f))
    files.sort()

    hits, total_sites = [], 0
    for p in files:
        try:
            tree = ast.parse(open(p, encoding="utf-8", errors="replace").read())
        except Exception as e:
            unparseable.append(dict(file=os.path.relpath(p, REPO), error=type(e).__name__))
            continue
        for s in scan_sites(tree):
            total_sites += 1
            if not s["guarded"]:
                hits.append(dict(file=os.path.relpath(p, REPO), **s))

    mine = [h for h in hits if os.path.basename(h["file"]).startswith("m2_")]
    out = dict(cycle=58, arm="D1", law="#188",
               denominator=dict(py_files=len(files), unparseable=len(unparseable),
                                unparseable_detail=unparseable),
               scan_sites_total=total_sites,
               unguarded_sites=len(hits), unguarded_in_m2_files=len(mine),
               hits=hits,
               controls=[dict(name=n, passed=bool(ok), note=note) for n, ok, note in ctrl],
               detector=("AST slice-of-a-population with no assert/if-raise naming the sliced or "
                         "population name in the enclosing scope; GENEROUS-TO-CODE, so a LOWER "
                         "BOUND"),
               unmeasured=("Python only; islice/heapq/explicit-counter scans; dynamically built "
                           "slices. Outside the detector, not absent."),
               D1_verdict=("FOUND" if mine else "NONE FOUND"))
    json.dump(out, open(os.path.join(HERE, "m2_c58_population_audit.json"), "w"), indent=1)
    print("\nDENOMINATOR: %d python files (%d unparseable); %d scan sites"
          % (len(files), len(unparseable), total_sites))
    print("UNGUARDED: %d total, %d in m2_* files" % (len(hits), len(mine)))
    for h in hits:
        print("  %-58s :%-5d %s" % (h["file"], h["lineno"], h["population"]))
    print("D1: %s" % out["D1_verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
