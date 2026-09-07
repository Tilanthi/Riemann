#!/usr/bin/env python3
"""
m2_L179_dps_order_census.py — machine 2's COUNTED census of its own mpmath code for the
"constant created before mp.dps was raised" defect shape (m3-L179 section 1; our own c34
grader defect (i); m1 register #141; m3 family #149).

WHY A CENSUS AND NOT A LOOK
  c39/c41: a hand classification is a detector too and fails open; a corpus count has as many
  free parameters as the corpus has undeclared boundaries. So: the population is DERIVED BY
  MEASUREMENT (git, filesystem), every class the classifier can emit is printed even when its
  count is 0, and the exclusions are printed beside the inclusions.

DECLARED CORPUS (the denominator is a choice; here it is written down before counting)
  S1  tracked *.py in the Tilanthi/Riemann exchange repo whose ADDING commit subject begins
      "machine2" (machine-derived attribution; the other prefixes are m1's and m3's letters),
      minus any path under a directory naming another machine (data/m1/, m3_*).
  S2  *.py under /workspace/rh/ — machine 2's actual RH working tree, where the scripts that
      produced the published numbers were RUN. Untracked code is still our code.
  Files are in the POPULATION only if they reference mpmath at all (import mpmath / from
  mpmath ...). Everything else is reported as NO-MPMATH and excluded, with its count printed.
  EXCLUDED, explicitly and counted (c41 species-2: a search program contains every term it
  searches for): this file, and __pycache__.

CLASSES (all printed, including zeros — c39: count every class a classifier emits)
  NO-MPMATH                 not in the population
  PARSE-ERROR               could not be parsed; NOT silently dropped
  NO-DPS-SET                never assigns dps/prec -> inherits the caller's precision
  DPS-FIRST                 dps/prec assigned before any mpmath value is created
  ORDER-DEFECT-MODULE       an mpmath value is created at module level BEFORE the first
                            dps/prec assignment  <-- the m3-L179 shape
  ORDER-DEFECT-IMPORT       a local module that creates mpmath values at import time is
                            imported before the first dps/prec assignment (same shape, one
                            level of indirection; this is the trap c43_widen.py avoids)
  DPS-RAISED-IN-FUNC        module-level mpmath values exist and dps/prec is (re)assigned
                            inside a function/loop -> those values are frozen at the earlier
                            precision  <-- the c34 grader shape (reference constants at import)
  LAZY-CONST-ONLY           the only pre-dps mpmath reference is a bare mpmath CONSTANT
                            (mp.pi, mp.euler, ...), which is context-lazy and re-evaluates at
                            use; not a defect, reported separately rather than merged

A hit is a STRUCTURAL order defect, not automatically a wrong number: whether it is material
depends on whether the frozen value reaches a published result. Materiality is triaged by hand
AFTERWARDS, from the quoted evidence lines this script prints, and is reported as a hand
classification with that label on it.
"""
import ast, os, sys, json, subprocess, argparse

REPO = "/shared/rh-exchange-repo/Riemann"
WORK = "/workspace/rh"
SELF = os.path.abspath(__file__)

MP_FUNCS = {
    "mpf", "mpmathify", "mpc", "matrix", "log", "exp", "sqrt", "cos", "sin", "cosh", "sinh",
    "tan", "atan", "power", "zeta", "gamma", "loggamma", "digamma", "psi", "erf", "erfc",
    "besselj", "besselk", "mangoldt", "primepi", "factorial", "binomial", "quad", "quadgl",
    "quadts", "findroot", "polyroots", "linspace", "arange", "mpmathify", "fsum", "fdot",
    "expm1", "log10", "ln", "nstr", "chop", "re", "im", "conj", "eig", "eigsy", "lu_solve",
    "qr_solve", "norm", "det", "inverse", "cholesky", "taylor", "diff", "odefun", "rf",
    "hyp1f1", "hyp2f1", "ei", "li", "altzeta", "siegelz", "grampoint", "zetazero", "mpmathify",
}
MP_CONSTS = {"pi", "e", "euler", "phi", "catalan", "ln2", "ln10", "degree", "khinchin",
             "glaisher", "apery", "mertens", "twinprime"}
DPS_ATTRS = {"dps", "prec"}


def dotted(node):
    """'mp.mp.dps' for an Attribute/Name chain, else None."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


class Scan(ast.NodeVisitor):
    """Records, in source order, dps assignments and mpmath value-creation events."""

    def __init__(self, mp_aliases, valuecreating_modules):
        self.dps_module = []      # (line, text) at module level
        self.dps_func = []        # (line, text) inside a def/class
        self.create = []          # (line, kind, text) module level
        self.lazyconst = []       # (line, text) module level
        self.imports = []         # (line, modname)
        self.depth = 0
        self.mp_aliases = mp_aliases
        self.vcm = valuecreating_modules

    # ---- assignments to <something>.dps / .prec
    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(t, ast.Attribute) and t.attr in DPS_ATTRS:
                d = dotted(t) or t.attr
                (self.dps_func if self.depth else self.dps_module).append((node.lineno, d))
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        t = node.target
        if isinstance(t, ast.Attribute) and t.attr in DPS_ATTRS:
            d = dotted(t) or t.attr
            (self.dps_func if self.depth else self.dps_module).append((node.lineno, d))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    def visit_Call(self, node):
        if self.depth == 0:
            name = None
            f = node.func
            if isinstance(f, ast.Name):
                name = f.id
            elif isinstance(f, ast.Attribute):
                name = f.attr
            if name in MP_FUNCS:
                d = dotted(node.func) or name
                # mp.dps setters are attribute assigns, not calls; anything here creates a value
                self.create.append((node.lineno, "call", d))
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if self.depth == 0 and node.attr in MP_CONSTS:
            base = dotted(node.value)
            if base in self.mp_aliases:
                self.lazyconst.append((node.lineno, dotted(node) or node.attr))
        self.generic_visit(node)

    def visit_Import(self, node):
        for al in node.names:
            self.imports.append((node.lineno, al.name))
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append((node.lineno, node.module))
        self.generic_visit(node)


def mp_aliases_of(tree):
    """names bound to the mpmath context object (mp) or the mpmath module."""
    al = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "mpmath":
                    al.add(a.asname or "mpmath")
        elif isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("mpmath"):
            for a in n.names:
                al.add(a.asname or a.name)
    al.add("mp")
    return al


def uses_mpmath(src):
    return "mpmath" in src


def module_creates_values_at_import(path, cache={}):
    """does importing this local module create mpmath values at module level?"""
    p = os.path.abspath(path)
    if p in cache:
        return cache[p]
    cache[p] = False                      # cycle guard
    try:
        src = open(p, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except Exception:
        return False
    s = Scan(mp_aliases_of(tree), set())
    s.visit(tree)
    # a value creation at module level that happens before ANY dps set in that module
    first_dps = min([l for l, _ in s.dps_module], default=10 ** 9)
    res = any(l < first_dps for l, _, _ in s.create)
    cache[p] = res
    return res


def classify(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    if not uses_mpmath(src):
        return dict(cls="NO-MPMATH", ev=[])
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return dict(cls="PARSE-ERROR", ev=["%s" % e])
    s = Scan(mp_aliases_of(tree), set())
    s.visit(tree)
    lines = src.splitlines()

    def q(l):
        return "L%d: %s" % (l, lines[l - 1].strip()[:110]) if 0 < l <= len(lines) else "L%d" % l

    if not s.dps_module and not s.dps_func:
        return dict(cls="NO-DPS-SET", ev=[])

    first_dps = min([l for l, _ in s.dps_module], default=10 ** 9)
    pre_create = [(l, k, t) for l, k, t in s.create if l < first_dps]
    # local sibling modules imported before the first dps set, that build values at import
    d = os.path.dirname(os.path.abspath(path))
    pre_import_hits = []
    for l, modname in s.imports:
        if l >= first_dps or modname.startswith("mpmath") or "." in modname:
            continue
        cand = os.path.join(d, modname.split(".")[0] + ".py")
        if os.path.exists(cand) and module_creates_values_at_import(cand):
            pre_import_hits.append((l, modname))

    if pre_create:
        l, k, t = pre_create[0]
        return dict(cls="ORDER-DEFECT-MODULE",
                    ev=[q(l) + "   [creates %s]" % t, q(first_dps) + "   [dps set here]"])
    if pre_import_hits:
        l, m = pre_import_hits[0]
        return dict(cls="ORDER-DEFECT-IMPORT",
                    ev=[q(l) + "   [imports %s, which builds mpmath values at import]" % m,
                        q(first_dps) + "   [dps set here]"])
    if s.dps_func and s.create:
        # module-level values exist AND dps is (re)set inside a function
        lf = s.dps_func[0][0]
        earlier = [c for c in s.create if c[0] < lf]
        if earlier:
            return dict(cls="DPS-RAISED-IN-FUNC",
                        ev=[q(earlier[0][0]) + "   [module-level value]", q(lf) + "   [dps set in a function]"])
    pre_lazy = [(l, t) for l, t in s.lazyconst if l < first_dps]
    if pre_lazy and not s.dps_module:
        return dict(cls="LAZY-CONST-ONLY", ev=[q(pre_lazy[0][0])])
    if pre_lazy:
        return dict(cls="LAZY-CONST-ONLY", ev=[q(pre_lazy[0][0]), q(first_dps)])
    return dict(cls="DPS-FIRST", ev=[q(first_dps)])


# ------------------------------------------------------------------ population derivation
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
        if "/m1/" in f or "/m3" in f or "machine1" in os.path.basename(f) or "machine3" in os.path.basename(f):
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
                out.append(os.path.join(root, f))
    return out


def run_kat():
    """known-answer test: two externally-supplied ground truths + four synthetics."""
    import tempfile
    cases = []
    m3dir = os.path.join(REPO, "data/code/m3_L177_build")
    cases.append((os.path.join(m3dir, "rerun_60sf.py"), "ORDER-DEFECT-MODULE", "m3's own BUGGY script (ground truth: m3-L179 s1)"))
    cases.append((os.path.join(m3dir, "rerun_60sf_v2.py"), "DPS-FIRST", "m3's own FIXED script (ground truth: m3-L179 s2)"))
    syn = {
        "syn_bug.py": ("ORDER-DEFECT-MODULE", "from mpmath import mp\nL = mp.log(mp.mpf(13))\nmp.dps = 250\nprint(L)\n"),
        "syn_clean.py": ("DPS-FIRST", "from mpmath import mp\nmp.dps = 250\nL = mp.log(mp.mpf(13))\nprint(L)\n"),
        "syn_func.py": ("DPS-RAISED-IN-FUNC", "from mpmath import mp\nREF = mp.mpf(3)\ndef run(d):\n    mp.dps = d\n    return REF\n"),
        "syn_nodps.py": ("NO-DPS-SET", "from mpmath import mp\nx = mp.mpf(2)\n"),
        "syn_nomp.py": ("NO-MPMATH", "import math\nx = math.log(13)\n"),
    }
    td = tempfile.mkdtemp()
    for name, (exp, body) in syn.items():
        p = os.path.join(td, name)
        open(p, "w").write(body)
        cases.append((p, exp, "synthetic"))
    rows, ok = [], 0
    for path, exp, why in cases:
        got = classify(path)["cls"] if os.path.exists(path) else "MISSING-FILE"
        good = got == exp
        ok += good
        rows.append(dict(file=os.path.basename(path), expected=exp, got=got, pass_=good, note=why))
    return rows, ok, len(cases)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/workspace/rh/L179/out/census.json")
    a = ap.parse_args()

    kat_rows, kat_ok, kat_n = run_kat()
    print("== KNOWN-ANSWER TEST OF THE DETECTOR  (%d/%d)" % (kat_ok, kat_n))
    for r in kat_rows:
        print("   %-4s %-24s expected %-22s got %s   (%s)" %
              ("PASS" if r["pass_"] else "FAIL", r["file"], r["expected"], r["got"], r["note"]))
    if kat_ok != kat_n:
        print("   DETECTOR FAILED ITS OWN KAT — census below is NOT to be trusted")

    s1, other_prefix, foreign_path, all_tracked = repo_machine2_py()
    s2 = [p for p in work_py() if os.path.abspath(p) != SELF]
    self_excluded = 1
    print("\n== POPULATION, derived by measurement")
    print("   tracked *.py in the exchange repo                 : %d" % all_tracked)
    print("   ... adding-commit subject not 'machine2*'          : %d  (m1 / m3, excluded)" % other_prefix)
    print("   ... machine2 commit but a foreign path/name        : %d  (excluded)" % foreign_path)
    print("   S1 machine2-authored tracked *.py                  : %d" % len(s1))
    print("   S2 *.py under %-36s: %d" % (WORK, len(s2)))
    print("   excluded: this census script itself                : %d  (c41 species-2)" % self_excluded)

    results = {}
    for stratum, files in (("S1", s1), ("S2", s2)):
        counts = {c: 0 for c in ("NO-MPMATH", "PARSE-ERROR", "NO-DPS-SET", "DPS-FIRST",
                                 "ORDER-DEFECT-MODULE", "ORDER-DEFECT-IMPORT",
                                 "DPS-RAISED-IN-FUNC", "LAZY-CONST-ONLY")}
        hits = []
        for p in files:
            r = classify(p)
            counts[r["cls"]] += 1
            if r["cls"] in ("ORDER-DEFECT-MODULE", "ORDER-DEFECT-IMPORT", "DPS-RAISED-IN-FUNC",
                            "PARSE-ERROR", "LAZY-CONST-ONLY"):
                hits.append(dict(file=p, cls=r["cls"], ev=r["ev"]))
        results[stratum] = dict(n=len(files), counts=counts, hits=hits)
        pop = len(files) - counts["NO-MPMATH"]
        print("\n== %s  (%d files; mpmath population %d, denominator for every rate below)" %
              (stratum, len(files), pop))
        for c, n in counts.items():
            print("   %-22s %4d" % (c, n))
        print("   -- hits, with evidence lines:")
        for h in hits:
            print("   [%s] %s" % (h["cls"], h["file"]))
            for e in h["ev"]:
                print("        %s" % e)
        if not hits:
            print("   (none)")

    json.dump(dict(kat=kat_rows, kat_ok=kat_ok, kat_n=kat_n,
                   population=dict(all_tracked=all_tracked, other_prefix=other_prefix,
                                   foreign_path=foreign_path, s1=len(s1), s2=len(s2)),
                   results={k: dict(n=v["n"], counts=v["counts"], hits=v["hits"])
                            for k, v in results.items()}),
              open(a.out, "w"), indent=1)
    print("\nwrote %s" % a.out)
