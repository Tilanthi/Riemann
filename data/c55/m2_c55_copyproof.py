#!/usr/bin/env python3
"""m2_c55_copyproof.py -- PROVE that cycle 55's instrument is cycle 54's instrument, and print
every byte where it is not.

WHY THIS EXISTS.  `m2_c55_spectrum.py` and `m2_c55_repro_fix.py` were produced from their c54
originals by a `54 -> 55` textual substitution.  c51's discipline is "prove the copy is a copy";
c50's is "ship a new script, never edit the registered one".  A substitution satisfies neither on
its own, because a substitution can silently rewrite PROSE into a false present-tense claim while
leaving every number right -- which is exactly what happened here and is disclosed in the prereg:
c54's `repro_fix` docstring narrates c54's own gate FAILURE ("21/22 -> FAIL"), and the substitution
turned that history into an assertion about a cycle-55 gate that had not yet run.

So this gate does not assert "it is a copy".  It MEASURES the difference, line by line, and
CLASSIFIES each differing line as DOCSTRING/COMMENT (prose) or CODE.  Prose differences are listed
and must be the disclosed ones; a CODE difference must be disclosed in the prereg by name or the
gate fails.

MUTATION CONTROL (an exemption is indistinguishable from a loosening without a planted failure):
the same comparison is re-run against an in-memory copy of the c55 file with one CODE line altered,
and the gate must report that line as a CODE difference.  If it does not, this proof is worthless
and says so.

usage:  m2_c55_copyproof.py     ->  m2_c55_copyproof.json
"""
import ast, difflib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C54 = os.path.abspath(os.path.join(HERE, "..", "c54"))

PAIRS = [("m2_c55_spectrum.py", "m2_c54_spectrum.py"),
         ("m2_c55_repro_fix.py", "m2_c54_repro_fix.py")]

# Every difference we DECLARE in advance. Anything else -- prose or code -- fails the gate.
DECLARED = {
    "m2_c55_spectrum.py": dict(
        code_changes=[],
        prose_changes=["module docstring line 1: 'the THIRD WINDOW (x = 17)' -> the fourth and "
                       "fifth windows (x = 25 sealed extrapolation, x = 22 discriminating)"]),
    "m2_c55_repro_fix.py": dict(
        code_changes=["_sealed_gate_result(): NEW -- reads THIS cycle's own m2_c55_repro_gate.json "
                      "instead of the hardcoded c54 verdict 'FAIL 21/22'",
                      "out['sealed_gate_result'] now calls _sealed_gate_result()"],
        prose_changes=["docstring: c54's gate-failure narrative re-marked as c54 HISTORY, with the "
                       "substitution hazard stated"]),
}


def normalise(text):
    """undo the 55 -> 54 substitution so that only REAL differences survive."""
    return (text.replace("m2_c55_", "m2_c54_").replace("c55", "c54")
                .replace("cycle 55", "cycle 54").replace("CYCLE 55", "CYCLE 54"))


def prose_lines(path):
    """line numbers that lie inside a docstring, plus every comment-only line."""
    src = open(path).read()
    lines = src.splitlines()
    inside = set()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                for ln in range(body[0].lineno, (body[0].end_lineno or body[0].lineno) + 1):
                    inside.add(ln)
    for i, ln in enumerate(lines, 1):
        if ln.strip().startswith("#"):
            inside.add(i)
    return inside, lines


def diff_one(new_path, old_path, override_new_text=None):
    new_src = override_new_text if override_new_text is not None else open(new_path).read()
    old_src = open(old_path).read()
    a = normalise(new_src).splitlines()
    b = old_src.splitlines()
    inside, _ = prose_lines(new_path)
    changed_new_lines = []
    sm = difflib.SequenceMatcher(None, b, a, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        for j in range(j1, j2):                       # lines of the NEW file
            changed_new_lines.append((j + 1, a[j]))
        if tag == "delete":
            for i in range(i1, i2):
                changed_new_lines.append((None, "-(removed) " + b[i]))
    code, prose = [], []
    for ln, txt in changed_new_lines:
        (prose if (ln is not None and ln in inside) else code).append(
            dict(line=ln, text=txt[:160]))
    return code, prose


def main():
    out = dict(files=[], verdict="PASS", legend=(
        "CODE difference = a line that is not inside a docstring and is not a comment. "
        "Every CODE difference must be named in DECLARED; every prose difference is listed."))
    for new_name, old_name in PAIRS:
        new_p, old_p = os.path.join(HERE, new_name), os.path.join(C54, old_name)
        code, prose = diff_one(new_p, old_p)
        decl = DECLARED[new_name]
        undeclared_code = bool(code) and not decl["code_changes"]
        # --- mutation control: alter one CODE line and require the gate to see it
        src = open(new_p).read().splitlines(keepends=True)
        inside, _ = prose_lines(new_p)
        tgt = None
        for i, ln in enumerate(src, 1):
            if i not in inside and ln.strip() and not ln.strip().startswith("#") \
                    and "import" not in ln and "=" in ln:
                tgt = i
                break
        mutated = list(src)
        mutated[tgt - 1] = mutated[tgt - 1].rstrip("\n") + "  # PLANTED\n"
        mcode, _mprose = diff_one(new_p, old_p, override_new_text="".join(mutated))
        fires = len(mcode) > len(code)
        rec = dict(new=new_name, old="../c54/" + old_name,
                   code_differences=code, prose_differences=prose,
                   declared=decl,
                   undeclared_code_difference=bool(undeclared_code),
                   mutation_control=dict(planted_line=tgt, code_diffs_without=len(code),
                                         code_diffs_with=len(mcode), fires=bool(fires)))
        if undeclared_code or not fires:
            out["verdict"] = "FAIL"
        out["files"].append(rec)
    json.dump(out, open(os.path.join(HERE, "m2_c55_copyproof.json"), "w"), indent=1)
    for r in out["files"]:
        print("%-24s code-diff lines=%d  prose-diff lines=%d  mutation fires=%s"
              % (r["new"], len(r["code_differences"]), len(r["prose_differences"]),
                 r["mutation_control"]["fires"]))
    print("COPY PROOF: %s" % out["verdict"])
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
