#!/usr/bin/env python3
"""
m2_L179_dps_order_census_v2.py — machine 2's COUNTED census of its OWN mpmath code for the
"value created before mp.dps was raised" defect shape (m3-L179 s1; our c34 grader defect (i);
m1 register #141; m3 family #149).

v1 (kept unedited beside this file as m2_L179_dps_order_census_v1_KEPT.py) FAILED ITS OWN
KNOWN-ANSWER TEST, 5/7, and the failure is worth more than the census:
  * it classified m3's KNOWN-BUGGY rerun_60sf.py as NO-DPS-SET — i.e. CLEAN — because that
    script never assigns dps at all: it builds L = mp.log(mp.mpf(13)) and then passes dps into
    build_matrix_fast(), a CALLEE in another module, which raises it. A single-file, single-
    module scanner is structurally blind to the very instance that motivated the census.
  * it merged "module-level value then dps raised inside a function" into ORDER-DEFECT-MODULE
    because of a precedence slip (first_dps defaulted to +inf).
  * it counted np.linspace(...) as an mpmath value creation: a bare-name match with no
    resolution of where the name came from (c38: a regex is a detector excerpt too).
v2 fixes all three. The KAT is run FIRST, every run, and the census refuses to be believed if
the KAT does not pass.

DECLARED CORPUS (written down before counting; c41 — a count over a corpus has as many free
parameters as the corpus has undeclared boundaries):
  S1  tracked *.py in Tilanthi/Riemann whose ADDING commit subject begins "machine2"
      (machine-derived attribution via git log --diff-filter=A; the remaining prefixes are
      m1's and m3's, checked by inspection of all 214 of them).
  S2  *.py anywhere under /workspace/rh — machine 2's actual RH working tree, where the
      scripts that produced the published numbers were RUN. Untracked code is still our code.
  POPULATION = files in S1 or S2 that reference mpmath at all. NO-MPMATH files are counted and
  excluded. EXCLUDED and counted separately: this file and its own v1 (c41 species 2: a search
  program contains every term it searches for), and __pycache__.

CLASSES (all printed every run, including zeros — c39):
  NO-MPMATH  PARSE-ERROR  NO-DPS-ANYWHERE  DPS-FIRST  LAZY-CONST-ONLY
  ORDER-DEFECT-MODULE     value created at module level before the first module-level dps set
  ORDER-DEFECT-CALLEE     value created at module level before a module-level CALL to a local
                          function that raises dps  <-- m3-L179's own shape
  DPS-RAISED-IN-FUNC      module-level value exists and dps is (re)set inside a function
LIMITATION, declared: execution order is approximated by SOURCE-LINE order at module level.
A call inside `if __name__ == "__main__":` is module level; a value created inside a function
that runs before a dps raise elsewhere is NOT seen. This makes the count a LOWER BOUND.
A hit is a STRUCTURAL order defect, not automatically a wrong published number; materiality is
triaged by hand afterwards from the evidence lines printed here, and is labelled as such.
"""
import ast, os, sys, json, subprocess, argparse

REPO = "/shared/rh-exchange-repo/Riemann"
WORK = "/workspace/rh"
SELF = os.path.abspath(__file__)
SELF_V1 = os.path.join(os.path.dirname(SELF), "m2_L179_dps_order_census_v1_KEPT.py")

# names that CREATE an mpmath value; only counted when the name resolves to mpmath
MP_FUNCS = {
    "mpf", "mpmathify", "mpc", "matrix", "log", "exp", "sqrt", "cos", "sin", "cosh", "sinh",
    "tan", "atan", "power", "zeta", "gamma", "loggamma", "digamma", "psi", "erf", "erfc",
    "besselj", "besselk", "mangoldt", "primepi", "factorial", "binomial", "quad", "quadgl",
    "quadts", "findroot", "polyroots", "linspace", "arange", "fsum", "fdot", "expm1", "log10",
    "ln", "eig", "eigsy", "eighe", "lu_solve", "qr_solve", "norm", "det", "inverse", "cholesky",
    "taylor", "diff", "odefun", "rf", "hyp1f1", "hyp2f1", "ei", "li", "altzeta", "siegelz",
    "grampoint", "zetazero", "atan2", "cot", "sec", "acos", "asin", "mpmathify",
}
MP_CONSTS = {"pi", "e", "euler", "phi", "catalan", "ln2", "ln10", "degree", "khinchin",
             "glaisher", "apery", "mertens", "twinprime"}
DPS_ATTRS = {"dps", "prec"}


def dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def mpmath_names(tree):
    """(aliases of the mpmath module / mp context, bare names imported FROM mpmath)"""
    mods, bare = {"mp"}, set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "mpmath" or a.name.startswith("mpmath."):
                    mods.add(a.asname or a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("mpmath"):
            for a in n.names:
                (mods if a.name in ("mp", "fp", "iv") else bare).add(a.asname or a.name)
    return mods, bare


class Scan(ast.NodeVisitor):
    def __init__(self, mods, bare):
        self.mods, self.bare = mods, bare
        self.dps_module, self.dps_func = [], []
        self.create, self.lazyconst, self.imports, self.calls = [], [], [], []
        self.depth = 0
        self.func_sets_dps = set()      # names of functions in THIS file that set dps
        self._curfunc = None

    def _dps_target(self, t):
        return isinstance(t, ast.Attribute) and t.attr in DPS_ATTRS and (
            (dotted(t) or "").split(".")[0] in self.mods or (dotted(t) or "") in ("mp.dps", "mp.prec"))

    def visit_Assign(self, node):
        for t in node.targets:
            if self._dps_target(t):
                d = dotted(t)
                if self.depth:
                    self.dps_func.append((node.lineno, d))
                    if self._curfunc:
                        self.func_sets_dps.add(self._curfunc)
                else:
                    self.dps_module.append((node.lineno, d))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        prev, self._curfunc = self._curfunc, node.name
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1
        self._curfunc = prev

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    def visit_Call(self, node):
        if self.depth == 0:
            f = node.func
            if isinstance(f, ast.Attribute):
                base = dotted(f.value)
                if base in self.mods and f.attr in MP_FUNCS:
                    self.create.append((node.lineno, dotted(f) or f.attr))
                self.calls.append((node.lineno, f.attr, dotted(f)))
            elif isinstance(f, ast.Name):
                if f.id in self.bare and f.id in MP_FUNCS:
                    self.create.append((node.lineno, f.id))
                self.calls.append((node.lineno, f.id, f.id))
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if self.depth == 0 and node.attr in MP_CONSTS and dotted(node.value) in self.mods:
            self.lazyconst.append((node.lineno, dotted(node)))
        self.generic_visit(node)

    def visit_Import(self, node):
        for a in node.names:
            self.imports.append((node.lineno, a.name, a.asname or a.name.split(".")[0]))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for a in node.names:
                self.imports.append((node.lineno, node.module, a.asname or a.name))
        self.generic_visit(node)


def parse(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    tree = ast.parse(src)
    mods, bare = mpmath_names(tree)
    s = Scan(mods, bare)
    s.visit(tree)
    return src, s


_mod_cache = {}


def module_profile(path):
    """(creates_values_at_import, {functions that set dps}, sets_dps_at_module_level)."""
    p = os.path.abspath(path)
    if p in _mod_cache:
        return _mod_cache[p]
    _mod_cache[p] = (False, set(), False)
    try:
        src, s = parse(p)
    except Exception:
        return _mod_cache[p]
    first_dps = min([l for l, _ in s.dps_module], default=10 ** 9)
    res = (any(l < first_dps for l, _ in s.create), set(s.func_sets_dps), bool(s.dps_module))
    _mod_cache[p] = res
    return res


def classify(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    if "mpmath" not in src:
        return dict(cls="NO-MPMATH", advisory=False, ev=[])
    try:
        src, s = parse(path)
    except SyntaxError as e:
        return dict(cls="PARSE-ERROR", advisory=False, ev=[str(e)])
    lines = src.splitlines()

    def q(l, tag=""):
        t = lines[l - 1].strip()[:110] if 0 < l <= len(lines) else ""
        return "L%-5d %s%s" % (l, t, ("   <-- " + tag if tag else ""))

    if not s.dps_module and not s.dps_func:
        dps_free = True
    else:
        dps_free = False

    # --- where does dps get raised, in module-level execution order?
    first_dps_mod = min([l for l, _ in s.dps_module], default=10 ** 9)

    # calls at module level to LOCAL functions/modules that raise dps
    d = os.path.dirname(os.path.abspath(path))
    imported_from = {}                       # local name -> module file
    for l, mod, asname in s.imports:
        cand = os.path.join(d, mod.split(".")[0] + ".py")
        if os.path.exists(cand):
            imported_from[asname] = cand
    # a local module that raises dps at IMPORT time is a precision-setting event at its import
    # line — an unstated side effect, but a real one (measured: machine2_cycle15_epstein_fold
    # line 22 sets mp.dps = 40, which is why one flagged file's published .out is NOT garbage)
    import_dps = []
    for l, mod, asname in s.imports:
        cand = os.path.join(d, mod.split(".")[0] + ".py")
        if os.path.exists(cand) and os.path.abspath(cand) != os.path.abspath(path):
            if module_profile(cand)[2]:
                import_dps.append((l, os.path.basename(cand)))
    first_dps_import = min([l for l, _ in import_dps], default=10 ** 9)

    callee_dps = []
    for l, fname, dot in s.calls:
        if fname in s.func_sets_dps:                       # local function in this file
            callee_dps.append((l, fname, os.path.basename(path)))
            continue
        base = (dot or "").split(".")[0]
        for local, f in imported_from.items():
            if local == fname or (base == local and base != fname):
                creates, fset, _ = module_profile(f)
                if fname in fset:
                    callee_dps.append((l, fname, os.path.basename(f)))
                break
    first_dps_callee = min([l for l, _, _ in callee_dps], default=10 ** 9)

    # THE RULE, and it is exactly the habit m3 proposed: a value created before the FIRST
    # precision-setting event is born at whatever precision happened to be in force.
    # Events, in module-level source order: (a) this file assigns mp.dps/prec; (b) this file
    # calls a local function/module that assigns it; (c) this file imports a local module that
    # assigns it AT IMPORT TIME — a real event, but an unstated side effect.
    first_event = min(first_dps_mod, first_dps_callee, first_dps_import)
    first_create = min([l for l, _ in s.create], default=10 ** 9)
    advisory = bool([1 for l, _ in s.create if first_event <= l] and
                    ([1 for l, _ in s.dps_module if l > first_event] or
                     [1 for l, _, _ in callee_dps if l > first_event] or s.dps_func))

    if first_create < first_event < 10 ** 9:
        l, t = [(l, t) for l, t in s.create if l == first_create][0]
        if first_dps_mod <= min(first_dps_callee, first_dps_import):
            return dict(cls="ORDER-DEFECT-MODULE", advisory=advisory,
                        ev=[q(l, "creates %s" % t), q(first_dps_mod, "dps set here")])
        if first_dps_callee <= first_dps_import:
            lc, fn, where = min(callee_dps)
            return dict(cls="ORDER-DEFECT-CALLEE", advisory=advisory,
                        ev=[q(l, "creates %s" % t),
                            q(lc, "calls %s() in %s, which raises dps" % (fn, where))])
        li, mi = min(import_dps)
        return dict(cls="ORDER-DEFECT-MODULE", advisory=advisory,
                    ev=[q(l, "creates %s" % t), q(li, "precision only arrives with import %s" % mi)])
    if first_dps_mod < 10 ** 9 and first_dps_mod <= first_create:
        return dict(cls="DPS-FIRST", advisory=advisory,
                    ev=[q(first_dps_mod, "this file sets its own precision, before any value")])
    if first_dps_callee < 10 ** 9 and first_dps_callee <= first_create:
        return dict(cls="DPS-FIRST", advisory=advisory,
                    ev=[q(first_dps_callee, "precision raised by a local callee, before any value")])
    if first_dps_import < 10 ** 9 and first_dps_import <= first_create:
        li, mi = min(import_dps)
        cls = "DPS-VIA-IMPORT-BEFORE-VALUES" if first_create < 10 ** 9 else "DPS-VIA-IMPORT-NO-VALUES"
        return dict(cls=cls, advisory=advisory,
                    ev=[q(li, "importing %s raises dps at module level: this file's working "
                              "precision is set by a side effect it never states" % mi)])
    if s.dps_func and s.create:
        lf = s.dps_func[0][0]
        if [c for c in s.create if c[0] < lf]:
            return dict(cls="DPS-RAISED-IN-FUNC", advisory=advisory,
                        ev=[q(first_create, "module-level value"), q(lf, "dps set inside a function")])
    if first_event >= 10 ** 9 and not s.dps_func:
        return dict(cls="NO-DPS-ANYWHERE", advisory=False, ev=[])
    pre_lazy = [(l, t) for l, t in s.lazyconst if l < first_event]
    if pre_lazy:
        return dict(cls="LAZY-CONST-ONLY", advisory=advisory,
                    ev=[q(pre_lazy[0][0], "lazy mpmath constant, re-evaluated at use")])
    return dict(cls="DPS-FIRST", advisory=advisory,
                ev=[q(min(first_event, 10 ** 9), "first precision-setting event")])


# ---------------------------------------------------------------- known-answer test
def run_kat():
    import tempfile
    DEFECTS = {"ORDER-DEFECT-MODULE", "ORDER-DEFECT-CALLEE", "DPS-RAISED-IN-FUNC"}
    m3dir = os.path.join(REPO, "data/code/m3_L177_build")
    cases = [
        (os.path.join(m3dir, "rerun_60sf.py"), {"ORDER-DEFECT-CALLEE"},
         "EXTERNAL ground truth: m3's own script, m3-L179 s1 says it is buggy"),
        (os.path.join(m3dir, "rerun_60sf_v2.py"), {"DPS-FIRST"},
         "EXTERNAL ground truth: m3's own fixed script, m3-L179 s2"),
    ]
    syn = {
        "syn_bug.py": ({"ORDER-DEFECT-MODULE"},
                       "from mpmath import mp\nL = mp.log(mp.mpf(13))\nmp.dps = 250\nprint(L)\n"),
        "syn_clean.py": ({"DPS-FIRST"},
                         "from mpmath import mp\nmp.dps = 250\nL = mp.log(mp.mpf(13))\nprint(L)\n"),
        "syn_func.py": ({"DPS-RAISED-IN-FUNC"},
                        "from mpmath import mp\nREF = mp.mpf(3)\ndef run(d):\n    mp.dps = d\n    return REF\n"),
        "syn_nodps.py": ({"NO-DPS-ANYWHERE"}, "from mpmath import mp\nx = mp.mpf(2)\n"),
        "syn_nomp.py": ({"NO-MPMATH"}, "import math\nx = math.log(13)\n"),
        # NEGATIVE CONTROL: numpy names must not be mistaken for mpmath ones (v1 did exactly this)
        "syn_numpy.py": ({"DPS-FIRST"},
                         "import numpy as np\nfrom mpmath import mp\nxs = np.linspace(0, 1, 5)\n"
                         "mp.dps = 50\ny = mp.mpf(2)\n"),
        # local-callee shape, the one v1 was blind to, in a form I control
        "syn_import_lib.py": (None, "from mpmath import mp\nmp.dps = 40\n"),
        "syn_import_use.py": ({"DPS-VIA-IMPORT-BEFORE-VALUES"},
                              "from mpmath import mp\nimport syn_import_lib\nC = mp.mpf('0.1')\n"),
        "syn_callee_lib.py": (None,
                              "from mpmath import mp\ndef build(dps):\n    mp.dps = dps\n    return mp.mpf(1)\n"),
        "syn_callee_use.py": ({"ORDER-DEFECT-CALLEE"},
                              "from mpmath import mp\nfrom syn_callee_lib import build\n"
                              "L = mp.log(mp.mpf(13))\nM = build(250)\n"),
    }
    td = tempfile.mkdtemp()
    for name, (exp, body) in syn.items():
        open(os.path.join(td, name), "w").write(body)
    for name, (exp, body) in syn.items():
        if exp is not None:
            cases.append((os.path.join(td, name), exp, "synthetic"))
    rows, ok = [], 0
    for path, exp, why in cases:
        got = classify(path)["cls"] if os.path.exists(path) else "MISSING-FILE"
        good = got in exp
        ok += good
        rows.append(dict(file=os.path.basename(path), expected="|".join(sorted(exp)), got=got,
                         pass_=good, note=why))
    return rows, ok, len(cases)


def repo_machine2_py():
    out = subprocess.run(["git", "-C", REPO, "ls-files", "*.py"],
                         capture_output=True, text=True, check=True).stdout.split()
    keep, other, foreign = [], 0, 0
    for f in out:
        sub = subprocess.run(["git", "-C", REPO, "log", "--diff-filter=A", "--format=%s", "-1", "--", f],
                             capture_output=True, text=True).stdout.splitlines()
        sub = sub[0] if sub else ""
        if not sub.startswith("machine2"):
            other += 1
            continue
        b = os.path.basename(f)
        if "/m1/" in f or "/m3" in f or b.startswith("machine1") or b.startswith("machine3") or b.startswith("m1_") or b.startswith("m3_"):
            foreign += 1
            continue
        keep.append(os.path.join(REPO, f))
    return keep, other, foreign, len(out)


def work_py():
    out = []
    for root, dirs, files in os.walk(WORK):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                p = os.path.join(root, f)
                if os.path.abspath(p) not in (SELF, SELF_V1):
                    out.append(p)
    return out


ALL_CLASSES = ("NO-MPMATH", "PARSE-ERROR", "NO-DPS-ANYWHERE", "DPS-FIRST",
               "DPS-VIA-IMPORT-BEFORE-VALUES", "DPS-VIA-IMPORT-NO-VALUES", "LAZY-CONST-ONLY",
               "ORDER-DEFECT-MODULE", "ORDER-DEFECT-CALLEE", "DPS-RAISED-IN-FUNC")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/workspace/rh/L179/out/census_v2.json")
    a = ap.parse_args()

    rows, ok, n = run_kat()
    print("== KNOWN-ANSWER TEST OF THE DETECTOR (runs first, every run)   %d/%d" % (ok, n))
    for r in rows:
        print("   %-4s %-22s expected %-24s got %-22s (%s)" %
              ("PASS" if r["pass_"] else "FAIL", r["file"], r["expected"], r["got"], r["note"]))
    if ok != n:
        print("   ⛔ DETECTOR FAILED ITS OWN KAT — the census below is NOT to be believed")

    s1, other_prefix, foreign_path, all_tracked = repo_machine2_py()
    s2 = work_py()
    print("\n== POPULATION, derived by measurement (git + filesystem), not by memory")
    print("   tracked *.py in the exchange repo                  : %d" % all_tracked)
    print("   ... adding commit not 'machine2*' (m1/m3)          : %d  excluded" % other_prefix)
    print("   ... machine2 commit but foreign path/name          : %d  excluded" % foreign_path)
    print("   S1 machine2-authored tracked *.py                  : %d" % len(s1))
    print("   S2 *.py under %-37s: %d" % (WORK, len(s2)))
    print("   this census script + its kept v1                   : 2  excluded (c41 species 2)")

    results = {}
    for stratum, files in (("S1", s1), ("S2", s2)):
        counts = {c: 0 for c in ALL_CLASSES}
        n_adv = 0
        hits = []
        for p in files:
            r = classify(p)
            counts[r["cls"]] += 1
            n_adv += bool(r.get("advisory"))
            if r["cls"] in ("ORDER-DEFECT-MODULE", "ORDER-DEFECT-CALLEE", "DPS-RAISED-IN-FUNC",
                            "PARSE-ERROR", "LAZY-CONST-ONLY", "DPS-VIA-IMPORT-BEFORE-VALUES"):
                hits.append(dict(file=p, cls=r["cls"], ev=r["ev"]))
        pop = len(files) - counts["NO-MPMATH"]
        defects = counts["ORDER-DEFECT-MODULE"] + counts["ORDER-DEFECT-CALLEE"] + counts["DPS-RAISED-IN-FUNC"]
        results[stratum] = dict(n=len(files), pop=pop, counts=counts, defects=defects,
                                advisory_multi_raise=n_adv, hits=hits)
        print("\n== %s   files %d   mpmath POPULATION %d  <- the denominator" % (stratum, len(files), pop))
        for c in ALL_CLASSES:
            print("   %-22s %4d" % (c, counts[c]))
        print("   STRUCTURAL ORDER DEFECTS: %d / %d" % (defects, pop))
        print("   advisory (precision set again after values exist; NOT counted as a defect,")
        print("             static analysis cannot tell a raise from a lower): %d / %d" % (n_adv, pop))
        for h in hits:
            print("   [%s] %s" % (h["cls"], h["file"]))
            for e in h["ev"]:
                print("        %s" % e)
        if not hits:
            print("   (no hits)")

    json.dump(dict(kat=rows, kat_ok=ok, kat_n=n,
                   population=dict(all_tracked=all_tracked, other_prefix=other_prefix,
                                   foreign_path=foreign_path, s1=len(s1), s2=len(s2)),
                   results={k: dict(n=v["n"], pop=v["pop"], counts=v["counts"],
                                    defects=v["defects"],
                                    advisory_multi_raise=v["advisory_multi_raise"], hits=v["hits"])
                            for k, v in results.items()}),
              open(a.out, "w"), indent=1)
    print("\nwrote %s" % a.out)
