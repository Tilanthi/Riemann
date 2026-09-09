#!/usr/bin/env python3
"""m2_c57_path_census_fix.py -- SIBLING REPAIR of two defects in THIS CYCLE'S OWN SEALED CENSUS,
both found by its own planted controls.  The sealed file is imported, never edited.

DEFECT 1 (found by a DEAD control).  `m2_c57_path_census.py`'s planted control
"C2 positive (gated producer is FOUND and marked gated)" came back **DEAD**.  Cause: the dominance
test collected `ast.Name` ids and `ast.Attribute` attrs from an `If` test, so it saw `g` in
`if g["passed"]:` and never saw the string key `"passed"` -- and `g["passed"]` is the ONE idiom the
real gated sibling uses.  ⇒ the sealed census UNDER-counts "gated", which falsifies its own stated
claim that the criterion "can only overcount gated, never undercount".

DIRECTION CHECK.  This repair can only INCREASE the gated count, and B1 predicted that FEWER than
10 % of producer calls are gated.  The repair therefore runs AGAINST my own registered prediction.
That is the only direction in which a post-hoc repair may be made.

DEFECT 2 (found by my own census firing on my own new file).  The C5 rule flagged
`m2_c57_aligned_ncontrol.py:34 os.walk` as UNPINNED, but that walk sorts its filenames inside the
loop and sorts the corpus on return.  The syntactic rule tests the CALL; pinning happens at the
SELECTION.  ⇒ three classes instead of two: PINNED_AT_CALL / PINNED_IN_SCOPE / UNPINNED, counted
separately, so nobody has to hand-classify anything (a hand classification is a detector too).

usage: m2_c57_path_census_fix.py  -> m2_c57_path_census_fix.json
"""
import ast, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m2_c57_path_census as C                       # SEALED, imported, never edited

_orig_names_in = C._names_in


def _names_in(node):
    """REPAIR 1: a subscript key is a name to a reader; it must be one to the detector too."""
    return _orig_names_in(node) | {n.value for n in ast.walk(node)
                                   if isinstance(n, ast.Constant) and isinstance(n.value, str)}


C._names_in = _names_in
C.GATE_SYMBOLS = C.GATE_SYMBOLS | {"passed"}


def pin_class(path, src, hit_line):
    """REPAIR 2: PINNED_AT_CALL (sorted wraps the call) / PINNED_IN_SCOPE (the enclosing function or
    module sorts something after it) / UNPINNED."""
    tree = ast.parse(src)
    par = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            par[c] = n
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and getattr(n, "lineno", None) == hit_line):
            continue
        q, d = par.get(n), 0
        while q is not None and d < 4:
            if isinstance(q, ast.Call):
                nm, _ = C._callee_name(q)
                if nm in {"sorted", "min", "max", "sort"}:
                    return "PINNED_AT_CALL"
            q, d = par.get(q), d + 1
        scope, q = None, par.get(n)
        while q is not None:
            if isinstance(q, (ast.FunctionDef, ast.Module)):
                scope = q
                break
            q = par.get(q)
        if scope is not None:
            for m in ast.walk(scope):
                if isinstance(m, ast.Call):
                    nm, _ = C._callee_name(m)
                    if nm in {"sorted", "sort"} and getattr(m, "lineno", 0) >= hit_line:
                        return "PINNED_IN_SCOPE"
    return "UNPINNED"


def main():
    import tempfile
    tmp = tempfile.mkdtemp()
    verdicts, _ = C.run_controls(tmp)
    # extra planted control for repair 2
    ctrl = ('"""%s -- planted: a walk whose selection is sorted downstream."""\n'
            'import os\n'
            'def go(d):\n'
            '    out = []\n'
            '    for root, ds, fs in os.walk(d):\n'
            '        out += fs\n'
            '    return sorted(out)[0]\n' % C.CONTROL_MARK)
    p = os.path.join(tmp, "ctrl_pin_in_scope.py")
    open(p, "w").write(ctrl)
    a = C.analyse(p, ctrl)
    verdicts["C5 repair (a walk sorted downstream is PINNED_IN_SCOPE, not UNPINNED)"] = (
        len(a["c5"]) == 1 and pin_class(p, ctrl, a["c5"][0]["line"]) == "PINNED_IN_SCOPE")

    files = [f for f in C.corpus() if C.CONTROL_MARK not in open(f, errors="ignore").read()]
    calls = gated = 0
    by_layer, gated_sites = {}, []
    pins = {"PINNED_AT_CALL": 0, "PINNED_IN_SCOPE": 0, "UNPINNED": 0}
    unpinned_sites = []
    for f in files:
        src = open(f, errors="ignore").read()
        a = C.analyse(f, src)
        if a is None:
            continue
        rel = os.path.relpath(f, C.REPO)
        for c in a["producers"]:
            calls += 1
            d = by_layer.setdefault(c["layer"], dict(calls=0, gated=0))
            d["calls"] += 1
            if c["gated"]:
                gated += 1
                d["gated"] += 1
                gated_sites.append(dict(file=rel, **c))
        for h in a["c5"]:
            k = pin_class(f, src, h["line"])
            pins[k] += 1
            if k == "UNPINNED":
                unpinned_sites.append(dict(file=rel, line=h["line"], callee=h["callee"]))
    out = dict(cycle=57, repairs=["subscript keys count as names in a gate test",
                                  "three pin classes instead of two"],
               direction_check="both repairs can only move the numbers AGAINST prediction B1",
               controls=verdicts, denominator_python_files=len(files),
               C2=dict(producer_calls=calls, gated=gated,
                       gated_fraction=round(gated / calls, 4) if calls else None,
                       by_layer=by_layer, gated_sites=gated_sites),
               C5=dict(classes=pins, unpinned_sites=unpinned_sites))
    json.dump(out, open(os.path.join(HERE, "m2_c57_path_census_fix.json"), "w"), indent=1)
    print("CONTROLS (sealed five + one new)")
    for k, v in verdicts.items():
        print("  %-64s %s" % (k, "FIRES" if v else "DEAD"))
    print("\nDENOMINATOR: %d python files" % len(files))
    print("C2 producer calls %d   GATED %d   (%.2f %%)" % (calls, gated, 100.0 * gated / calls))
    for k, d in sorted(by_layer.items()):
        print("     layer %-9s calls=%-4d gated=%d" % (k, d["calls"], d["gated"]))
    print("   gated sites:")
    for g in gated_sites:
        print("     %s:%d  %s (%s)" % (g["file"], g["line"], g["callee"], g["layer"]))
    print("\nC5 pin classes: %s" % pins)
    print("   UNPINNED sites: %d" % len(unpinned_sites))
    return 0


if __name__ == "__main__":
    sys.exit(main())
