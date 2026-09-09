#!/usr/bin/env python3
"""m2_c57_path_census.py -- ONE INSTRUMENT, THREE CENSUSES, ALL BY AST.

Answers three questions BEAST-AGI's c57 brief asks with a NAMED, COUNTED DENOMINATOR:

  C2  How many code paths can compute a value at a protected window, and how many are GATED?
      (the c56 erratum generalised: a mechanism binds only the path that goes through it, and the
      refusal-to-compute was installed in the SCORER while the SPECTRUM GENERATOR -- a different
      program, same cycle -- computed and committed an index at the protected window anyway.)

  C4  Does any code path read the CYCLE TOKEN out of a FILENAME?  (files WRITTEN in c56 CLAIM c53
      in their names, because c53's gpred() hardcodes its own basename.)

  C5  Trap #177 generalised: does any live test choose its object by DIRECTORY ORDER?

WHY AST AND NOT GREP.  c56's C4 audit needed FOUR passes, and pass 4's law was: a negative operator
inside a quoted string is not an operator, it is a QUOTATION of one.  A regex cannot tell those
apart; `ast` cannot confuse them, because a string literal is a different node type from a Call.
The NEGATIVE CONTROL below plants exactly that confusion and requires the census not to fire.

DENOMINATOR RULE.  The corpus is DECLARED (every *.py under the repo, minus .git and __pycache__,
minus the planted control files themselves) and each census then derives its own sub-population BY
CONTENT -- never by directory name and never by filename pattern, because a name-shaped rule hides
members (c56).  Both numbers are reported: population and denominator.

usage:  m2_c57_path_census.py            -> m2_c57_path_census.json  (+ stdout table)
"""
import ast, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

# ---------------------------------------------------------------- corpus (DECLARED)
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
CONTROL_MARK = "M2_C57_PLANTED_CONTROL"


def corpus(extra_root=None):
    """every *.py reachable under the repo root.  Declared, not name-filtered."""
    out = []
    roots = [REPO] + ([extra_root] if extra_root else [])
    for R in roots:
        for root, dirs, fs in os.walk(R):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in fs:
                if f.endswith(".py"):
                    out.append(os.path.join(root, f))
    return sorted(set(out))


# ---------------------------------------------------------------- C2 vocabulary
# A "protected-quantity producer" is a callable that, given a window x, yields a number ABOUT that
# window.  Three layers, because the c56 finding was precisely that the gate sat on layer 3 only.
PRODUCERS = {
    "spectral": {"spectrum", "pooled_ladder", "gpred", "run_spectrum"},
    "nodal":    {"nodes", "count_all_knobs", "refine", "sturm", "n_control_depth"},
    "index":    {"pooled_table", "_first_leave", "plateaus", "plateaus_holeaware", "score",
                 "score_window", "pool_rows"},
}
ALL_PRODUCERS = set().union(*PRODUCERS.values())
GATE_SYMBOLS = {"RETIRED_WINDOWS", "gate_first", "TRUST_FLOOR_LIVE", "TRUST_FLOOR_Z",
                "trust_gate", "gate_passed", "PROTECTED_WINDOWS", "open_protected"}

DIRORDER = {("os", "listdir"), ("os", "scandir"), ("os", "walk"),
            ("glob", "glob"), ("glob", "iglob")}
DIRORDER_METHODS = {"iterdir", "rglob"}          # pathlib; .glob() handled below


def _callee_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id, None
    if isinstance(f, ast.Attribute):
        base = f.value.id if isinstance(f.value, ast.Name) else None
        return f.attr, base
    return None, None


def _parents(tree):
    p = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            p[c] = n
    return p


def _names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)} | \
           {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}


def analyse(path, src):
    """returns (c2_record, c4_hits, c5_hits) for one file, or None if it does not parse."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    par = _parents(tree)

    # ---- C2: producer calls, and whether each is dominated by a gate test
    prod_calls, gated_calls = [], []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        name, base = _callee_name(n)
        if name not in ALL_PRODUCERS:
            continue
        layer = next(k for k, v in PRODUCERS.items() if name in v)
        # DOMINANCE: walk up; guarded iff some ancestor is an If/While whose TEST mentions a gate
        # symbol, or an except/try body of one.  Stated criterion, deliberately generous to the
        # code -- it can only make the "gated" count too HIGH, never too low.
        guarded, q = False, par.get(n)
        while q is not None:
            if isinstance(q, (ast.If, ast.While, ast.IfExp)) and (_names_in(q.test) & GATE_SYMBOLS):
                guarded = True
                break
            if isinstance(q, ast.FunctionDef):
                # early-refusal pattern: `if <gate...>: raise/return` before this call
                for st in q.body:
                    if isinstance(st, ast.If) and (_names_in(st.test) & GATE_SYMBOLS) and \
                       any(isinstance(s, (ast.Raise, ast.Return)) for s in ast.walk(st)):
                        guarded = True
                        break
                if guarded:
                    break
            q = par.get(q)
        rec = dict(line=n.lineno, callee=name, base=base, layer=layer, gated=guarded)
        prod_calls.append(rec)
        if guarded:
            gated_calls.append(rec)

    # ---- C4: cycle token inside a STRING LITERAL that is used to build a path
    c4 = []
    import re
    tok = re.compile(r"(?:^|[^a-zA-Z0-9])c(\d{2})(?:[^0-9]|$)|m2_c(\d{2})_|c(\d{2})_")
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            m = tok.search(n.value)
            if not m:
                continue
            cyc = next(g for g in m.groups() if g)
            # is this literal used to name a FILE?  parent chain reaching os.path.join / open /
            # a %-format or f-string that itself lands in one of those.
            q, used_as_path, depth = par.get(n), False, 0
            while q is not None and depth < 6:
                if isinstance(q, ast.Call):
                    nm, base = _callee_name(q)
                    if nm in {"join", "open", "exists", "glob", "iglob", "basename", "dump",
                              "load", "specname", "nodename"}:
                        used_as_path = True
                        break
                q, depth = par.get(q), depth + 1
            if used_as_path:
                c4.append(dict(line=n.lineno, cycle_token="c" + cyc, literal=n.value[:70]))

    # ---- C5: object chosen by directory order without sorting
    c5 = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        name, base = _callee_name(n)
        hit = ((base, name) in DIRORDER) or (name in DIRORDER_METHODS) or \
              (name == "glob" and base not in (None, "glob")) or \
              (name == "glob" and base == "glob")
        if not hit:
            continue
        q, sorted_ = par.get(n), False
        depth = 0
        while q is not None and depth < 4:
            if isinstance(q, ast.Call):
                nm, _b = _callee_name(q)
                if nm in {"sorted", "min", "max", "sort"}:
                    sorted_ = True
                    break
            q, depth = par.get(q), depth + 1
        c5.append(dict(line=n.lineno, callee=("%s.%s" % (base, name) if base else name),
                       pinned=sorted_))
    return dict(producers=prod_calls, c4=c4, c5=c5)


# ---------------------------------------------------------------- controls
CTRL_POS_UNGATED = '''"""%s -- POSITIVE CONTROL 1: an UNGATED path that computes at a window."""
import m2_c53_spectrum as S
def go(x):
    return S.nodes("even", x, 100, 300, 15)
''' % CONTROL_MARK

CTRL_POS_GATED = '''"""%s -- POSITIVE CONTROL 2: a GATED path."""
import m2_c56_score_gated as GG
def go(x, files100, files180):
    g = GG.gate_first(files100, files180)
    if g["passed"]:
        return pooled_table(files100)
    return None
def pooled_table(f):
    return []
''' % CONTROL_MARK

CTRL_NEG_QUOTE = '''"""%s -- NEGATIVE CONTROL: the producer names appear ONLY inside quotations."""
NOTE = "this file mentions nodes( and pooled_table( and _first_leave( but never calls them"
DOC  = """it also names os.listdir and glob.glob in prose, and the filename m2_c53_gpred_x42.json"""
def go():
    return NOTE + DOC
''' % CONTROL_MARK

CTRL_POS_C4 = '''"""%s -- POSITIVE CONTROL 3: reads a cycle token out of a filename."""
import os
def find(here, x):
    return os.path.join(here, "m2_c54_gpred_x%%d_N100_dps300.json" %% x)
''' % CONTROL_MARK

CTRL_POS_C5 = '''"""%s -- POSITIVE CONTROL 4: object chosen by directory order."""
import os
def pick(d):
    return [f for f in os.listdir(d) if "ERRATUM-28" in f][0]
def pick_pinned(d):
    return sorted(os.listdir(d))[0]
''' % CONTROL_MARK


def run_controls(tmp):
    files = {"pos_ungated_producer": CTRL_POS_UNGATED, "pos_gated_producer": CTRL_POS_GATED,
             "neg_quotation_only": CTRL_NEG_QUOTE, "pos_c4_filename_token": CTRL_POS_C4,
             "pos_c5_dirorder": CTRL_POS_C5}
    res = {}
    for k, src in files.items():
        p = os.path.join(tmp, k + ".py")
        open(p, "w").write(src)
        a = analyse(p, src)
        res[k] = a
    verdicts = {}
    a = res["pos_ungated_producer"]
    verdicts["C2 positive (ungated producer is FOUND and marked ungated)"] = bool(
        a["producers"] and not any(c["gated"] for c in a["producers"]))
    a = res["pos_gated_producer"]
    verdicts["C2 positive (gated producer is FOUND and marked gated)"] = bool(
        any(c["gated"] for c in a["producers"]))
    a = res["neg_quotation_only"]
    verdicts["C2/C4/C5 negative (a QUOTATION of an operator does not fire)"] = bool(
        not a["producers"] and not a["c4"] and not a["c5"])
    a = res["pos_c4_filename_token"]
    verdicts["C4 positive (cycle token in a path literal is FOUND)"] = bool(a["c4"])
    a = res["pos_c5_dirorder"]
    verdicts["C5 positive (unsorted listdir FOUND, sorted one marked pinned)"] = bool(
        len(a["c5"]) == 2 and sum(1 for h in a["c5"] if not h["pinned"]) == 1)
    return verdicts, res


def main():
    import tempfile
    tmp = tempfile.mkdtemp()
    verdicts, _ = run_controls(tmp)
    files = [f for f in corpus() if CONTROL_MARK not in open(f, errors="ignore").read()]
    per, unparsed = {}, []
    for f in files:
        src = open(f, errors="ignore").read()
        a = analyse(f, src)
        if a is None:
            unparsed.append(os.path.relpath(f, REPO))
            continue
        if a["producers"] or a["c4"] or a["c5"]:
            per[os.path.relpath(f, REPO)] = a

    c2_files = {k: v for k, v in per.items() if v["producers"]}
    c2_calls = sum(len(v["producers"]) for v in c2_files.values())
    c2_gated = sum(sum(1 for c in v["producers"] if c["gated"]) for v in c2_files.values())
    c2_gated_files = sum(1 for v in c2_files.values() if all(c["gated"] for c in v["producers"]))
    by_layer = {}
    for v in c2_files.values():
        for c in v["producers"]:
            d = by_layer.setdefault(c["layer"], dict(calls=0, gated=0))
            d["calls"] += 1
            d["gated"] += 1 if c["gated"] else 0

    c4_files = {k: v["c4"] for k, v in per.items() if v["c4"]}
    c5_all = [(k, h) for k, v in per.items() for h in v["c5"]]
    c5_unpinned = [(k, h) for k, h in c5_all if not h["pinned"]]

    out = dict(
        corpus_rule="DECLARED: every *.py under the repo root minus .git/__pycache__; planted "
                    "control files excluded by CONTENT (they carry a marker string)",
        search_roots=[REPO],
        denominator_python_files=len(files),
        files_that_failed_to_parse=unparsed,
        controls=verdicts,
        C2=dict(question="how many code paths can compute a value at a protected window, and how "
                         "many of those are gated?",
                producer_vocabulary={k: sorted(v) for k, v in PRODUCERS.items()},
                gate_vocabulary=sorted(GATE_SYMBOLS),
                dominance_criterion="a producer call is GATED iff an ancestor If/While test names a "
                                    "gate symbol, or its enclosing function opens with a gate-tested "
                                    "raise/return. Generous to the code: it can only overcount gated.",
                files_with_a_producer_call=len(c2_files),
                producer_calls_total=c2_calls,
                producer_calls_gated=c2_gated,
                files_in_which_EVERY_producer_call_is_gated=c2_gated_files,
                by_layer=by_layer,
                detail=c2_files),
        C4=dict(question="does any code path read the cycle token out of a filename?",
                files_building_a_path_from_a_cycle_token=len(c4_files),
                sites=sum(len(v) for v in c4_files.values()),
                detail=c4_files),
        C5=dict(question="does any live test choose its object by directory order?",
                directory_order_call_sites=len(c5_all),
                unpinned=len(c5_unpinned),
                pinned=len(c5_all) - len(c5_unpinned),
                detail=[dict(file=k, **h) for k, h in c5_all]),
    )
    json.dump(out, open(os.path.join(HERE, "m2_c57_path_census.json"), "w"), indent=1)

    print("CONTROLS")
    for k, v in verdicts.items():
        print("  %-62s %s" % (k, "FIRES" if v else "DEAD"))
    print("\nDENOMINATOR: %d python files parsed (%d failed to parse)" % (len(files), len(unparsed)))
    print("\nC2  files with >=1 producer call : %d" % len(c2_files))
    print("C2  producer CALLS               : %d   of which GATED: %d" % (c2_calls, c2_gated))
    print("C2  files fully gated            : %d" % c2_gated_files)
    for k, d in sorted(by_layer.items()):
        print("      layer %-9s calls=%-4d gated=%d" % (k, d["calls"], d["gated"]))
    print("\nC4  files naming a cycle token in a path literal: %d  (sites %d)"
          % (len(c4_files), sum(len(v) for v in c4_files.values())))
    print("\nC5  directory-order call sites: %d   UNPINNED: %d   pinned: %d"
          % (len(c5_all), len(c5_unpinned), len(c5_all) - len(c5_unpinned)))
    for k, h in c5_unpinned:
        print("      UNPINNED %s:%d  %s" % (k, h["line"], h["callee"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
