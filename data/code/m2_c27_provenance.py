"""machine2 cycle27 LEG C -- automated sweep for RECURRENCE of the cycle-26 provenance defect class.

THE CLASS (founded by my own defect, cycle-26 scored letter ffc9873 / addendum 2f045f5):
    data/code/m2_c25_bandaudit.py's DOCSTRING claimed R1d missed the band at 10.05x; its own
    committed .out said 0.5023 IN.  Two independent verifications (m1 de9ab99, m3 718aa6f) missed
    it BECAUSE THE DEFECT LIVES IN PROSE AND VERIFICATION BATTERIES READ NUMBERS.

THE INSTRUMENT (deliberately crude, and its crudeness is disclosed):
    For every committed .py under data/code/ that has a paired committed .out under data/,
    extract every numeric token with >= 4 significant digits from the file's PROSE ONLY
    (module docstring + full-line comments + trailing comments), and ask whether that token is
    BACKED -- i.e. whether a numerically-equal value (to the prose token's own precision) occurs
    anywhere in the paired .out, or anywhere in the script's executable code.

    An UNBACKED prose number is a CANDIDATE, not a defect: it may be a quotation of another
    machine's letter, a design constant, or a historical value.  Every candidate is triaged by
    hand and the triage is published.  The instrument's job is to shrink 206 files to a list a
    human can read, not to render a verdict.

FALSIFIER, NAMED AT BIRTH (per my own standing law -- a falsifier with an empty firing world is
a diagnostic, not a falsifier):
    The world in which this fires is: a committed script whose prose asserts a number that its own
    committed output contradicts.  That world is KNOWN NON-EMPTY -- it contains exactly one member
    already (m2_c25_bandaudit.py, found by hand in cycle 26).  So the instrument has a positive
    control: IT MUST REDISCOVER MY OWN DEFECT.  If it does not, the sweep is void and reports
    nothing about the other 205 files.
"""
import os, re, json, sys
from decimal import Decimal, InvalidOperation

REPO = "/shared/rh-exchange-repo/Riemann"
CODE = os.path.join(REPO, "data", "code")
DATA = os.path.join(REPO, "data")

# v3: the trailing lookahead was (?![\w.]), which made "10.05x" -- the natural prose form of a
# MULTIPLIER, and the exact form of my own cycle-26 defect -- invisible to the sweep. v1 also
# paired on raw stems and missed the file entirely. Both misses are reported, not hidden.
NUM = re.compile(r"(?<![\w.])[-+]?\d+\.\d+(?:[eE][-+]?\d+)?(?![0-9.])|(?<![\w.])[-+]?\d+(?:\.\d*)?[eE][-+]?\d+(?![0-9.])")


def sigdigits(tok):
    s = tok.lstrip("+-")
    s = s.split("e")[0].split("E")[0]
    s = s.replace(".", "").lstrip("0")
    return len(s.rstrip("0")) if s.rstrip("0") else 0


def prose_spans(src):
    """module docstring + all comments. Deliberately excludes string literals used as data."""
    out = []
    m = re.match(r'\s*(?:#[^\n]*\n\s*)*("""|\'\'\')', src)
    if m:
        q = m.group(1)
        end = src.find(q, m.end())
        if end > 0:
            out.append(src[m.end():end])
    for line in src.split("\n"):
        i = line.find("#")
        if i >= 0:
            out.append(line[i:])
    return "\n".join(out)


def code_span(src):
    m = re.match(r'\s*(?:#[^\n]*\n\s*)*("""|\'\'\')', src)
    if m:
        q = m.group(1)
        end = src.find(q, m.end())
        if end > 0:
            return src[end + 3:]
    return src


def numeric_backed(tok, haystack_nums):
    """tok is backed if some number in the haystack agrees with it to tok's OWN precision."""
    try:
        v = Decimal(tok)
    except InvalidOperation:
        return True
    sd = sigdigits(tok)
    for w in haystack_nums:
        try:
            u = Decimal(w)
        except InvalidOperation:
            continue
        if u == v:
            return True
        if u == 0 or v == 0:
            continue
        try:
            rel = abs((u - v) / v)
        except Exception:
            continue
        if rel < Decimal(10) ** (-(sd - 1)):
            return True
    return False


def norm(s):
    s = s.lower()
    s = s.replace("machine", "m").replace("cycle", "c")
    return re.sub(r"[^a-z0-9]", "", s)


def pair_out(pyname):
    """Committed outputs are named after the script but the naming convention is NOT stable
    across machines or cycles (m2_c25_bandaudit.py <-> machine2_cycle25_bandaudit.out).  The
    first version of this sweep paired on raw stems and MISSED ITS OWN POSITIVE CONTROL; the
    normalisation below is the fix, and the miss is reported rather than hidden."""
    stem = norm(os.path.splitext(os.path.basename(pyname))[0])
    cands = []
    for f in os.listdir(DATA):
        if not f.endswith((".out", ".log", ".json")):
            continue
        fs = norm(os.path.splitext(f)[0])
        if fs == stem or fs.startswith(stem) or stem.startswith(fs):
            cands.append(os.path.join(DATA, f))
    return cands


def main():
    rows = []
    npaired = 0
    for py in sorted(os.listdir(CODE)):
        if not py.endswith(".py"):
            continue
        p = os.path.join(CODE, py)
        outs = pair_out(py)
        if not outs:
            continue
        npaired += 1
        src = open(p, errors="replace").read()
        prose = prose_spans(src)
        code = code_span(src)
        hay = set(NUM.findall(code))
        for o in outs:
            hay |= set(NUM.findall(open(o, errors="replace").read()))
        unbacked = []
        for tok in NUM.findall(prose):
            if sigdigits(tok) < 4:
                continue
            if not numeric_backed(tok, hay):
                ctx = ""
                i = prose.find(tok)
                if i >= 0:
                    ctx = " ".join(prose[max(0, i - 110):i + len(tok) + 60].split())
                unbacked.append({"token": tok, "context": ctx})
        if unbacked:
            rows.append({"script": py, "outs": [os.path.basename(x) for x in outs],
                         "n_unbacked": len(unbacked), "unbacked": unbacked})
    res = {"n_py_total": len([f for f in os.listdir(CODE) if f.endswith(".py")]),
           "n_py_with_committed_output": npaired,
           "n_scripts_with_unbacked_prose_numbers": len(rows),
           "n_unbacked_tokens": sum(r["n_unbacked"] for r in rows),
           "rows": rows}
    json.dump(res, open("/workspace/rh/cycle27/c27_provenance.json", "w"), indent=1)
    print("py total %d | with committed output %d | scripts with unbacked prose numbers %d | tokens %d"
          % (res["n_py_total"], npaired, len(rows), res["n_unbacked_tokens"]))
    for r in rows:
        print("\n--- %s  (%d)" % (r["script"], r["n_unbacked"]))
        for u in r["unbacked"][:6]:
            print("    %-24s | %s" % (u["token"], u["context"][:150]))


main()
