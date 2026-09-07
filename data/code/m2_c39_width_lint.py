#!/usr/bin/env python3
"""machine2 -- cycle 39 -- WIDTH LINT for the serialisation boundaries.

WHAT IT CHECKS
  RULE A  UNWARRANTED WIDTH.  A decimal literal of >= THRESH significant figures that appears in a
          letter, a commit message or a source file, and CANNOT be traced to any committed data
          artefact, was hand-typed.  Exemption (b), required by BEAST-AGI's c38 ruling: a literal
          that is read from a file and re-printed is exempt -- implemented as "prefix-consistent
          with, OR a correct ROUNDING of, some literal in data/**", which is the read-and-reprint
          relation and also permits the legitimate narrower quotation of a wider stored value.
          The ROUNDING half was added after the prefix-only version flagged our own c34 letter's
          correct 12-s.f. rounding -5.31691198314e-44 of a stored ...13966...e-44 as untraceable:
          prefix matching punishes correct rounding and rewards truncation, which is the defect the
          lint exists to prevent.  A superseded version of this file, committed at c5cbdb6, is
          prefix-only and its RULE A counts are INFLATED by that artefact.
  RULE B  WIDTH ASSERTION vs LITERAL.  A stated PRINT width ("N s.f.", "N significant figures",
          "N digits", "N-digit", "N decimal places") next to a decimal literal whose counted
          significant figures differ from N.  Working-precision vocabulary (dps, working precision,
          prec, guard) is deliberately NOT a print-width claim and is ignored by RULE B.

WHY IT FAILS CLOSED
  Every run executes the known-answer test FIRST.  The control count is COUNTED and printed at run
  time, never typed here: an earlier line in this file said "8/8" while ten controls ran, and this
  docstring said "six" while ten ran.  If any control fails the lint prints the failure and exits
  2 WITHOUT emitting findings, because a guard that has never fired is indistinguishable from a
  guard that cannot fire, and findings from an untested detector are worse than no findings.

SCOPE, per the same ruling: letters and commit messages are in scope, not only data/code/**, because
the worst measured instances were hand-typed literals in letters and are invisible to a route-keyed
search.
"""
import re, os, sys, subprocess, argparse, collections

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
THRESH = 12

# --- tokeniser -------------------------------------------------------------------
# Boundary discipline in BOTH directions, and it is a tested requirement, not a taste:
#   (?<![\w.]) stops a match from STARTING inside a longer literal  -- without it, "2.9078"
#              matches inside "71732.90783055708304445059087085997984896" and invents a carrier
#              (measured defect, machine2, this cycle);
#   (?![\w.])  stops a match from ENDING early -- the mirror defect (c38 v1's width token required
#              the unit to follow the integer immediately and missed a line the brief had quoted).
NUM = re.compile(r'(?<![\w.])[+-]?(?:\d+\.\d+|\.\d+|\d+)(?:[eE][+-]?\d+)?(?![\w.])')

def sigfigs(tok):
    t = tok.strip().lstrip('+-')
    t = re.split(r'[eE]', t)[0]
    if '.' in t:
        ip, fp = t.split('.', 1)
    else:
        ip, fp = t, ''
    d = (ip + fp)
    s = d.lstrip('0')
    if not s:
        return 0
    return len(s.rstrip()) if ip.lstrip('0') == '' else len(d)

def mant(tok):
    """(significant-digit string, decimal exponent) -- the key literals are compared on."""
    t = tok.strip().lstrip('+-'); e = 0
    if 'e' in t or 'E' in t:
        parts = re.split(r'[eE]', t)
        t = parts[0]
        try: e = int(parts[1])
        except Exception: return None
    if '.' in t: ip, fp = t.split('.', 1)
    else:        ip, fp = t, ''
    alld = ip + fp
    d = alld.lstrip('0')
    if not d: return None
    lead = len(alld) - len(d)
    return d.rstrip('\n'), len(ip) - lead + e

# --- width-assertion extractor ---------------------------------------------------
# NOTE the ".{0,24}?" gap: c38's v1 required the unit to follow the integer immediately and
# therefore missed "32 printed digits".  The gap is what makes POS-C pass.
PRINT_WIDTH = re.compile(
    r'(?<![\w.])(\d{1,4})\s*(?:-|\s)?[^\d]{0,24}?\b(s\.?f\.?|significant figures?|significant digits?|'
    r'printed digits?|digits?|decimal places?)\b', re.I)
# The gap is [^\d]{0,24}? and not .{0,24}? because a permissive gap binds the unit to the FIRST
# number in the window rather than the nearest: on the real m3 line it read "150, 83 s.f" as a claim
# of 150, and on the real m1 line it read "105 vs their 32 printed digits" as a claim of 105.
# Both were caught by the known-answer test, not by inspection.
# The vocabulary must be bound to the number it labels.  A 24-character lookbehind window is NOT
# that binding: on the real m3 line "published D* (dps-150, 83 s.f.)" it let "dps" 20 characters away
# suppress the "83 s.f." claim, and the known-answer test caught it.  Anchored to the digit instead.
PRECISION_VOCAB = re.compile(r'\b(dps|working precision|prec|guard)\b\s*[-=:]?\s*$', re.I)

def width_statements(text):
    """[(stated_width, matched_span_text, start, end)] -- PRINT widths only."""
    out = []
    for m in PRINT_WIDTH.finditer(text):
        pre = text[max(0, m.start() - 24):m.start()]
        if PRECISION_VOCAB.search(pre):
            continue                     # dps-150 is a knob, not a print-width claim
        out.append((int(m.group(1)), m.group(0), m.start(), m.end()))
    return out

# --- artefact index (the exemption set) -------------------------------------------
def build_artefact_index(root=None, subdirs=("data",)):
    root = root or REPO
    idx = collections.defaultdict(set)
    for sub in subdirs:
        for dp, _, fns in os.walk(os.path.join(root, sub)):
            for fn in fns:
                p = os.path.join(dp, fn)
                if os.path.getsize(p) > 40_000_000: continue
                try: t = open(p, errors='replace').read()
                except Exception: continue
                for m in NUM.finditer(t):
                    mm = mant(m.group(0))
                    if mm and len(mm[0]) >= THRESH:
                        idx[mm[1]].add(mm[0])
    return idx

def _round_digits(D, n):
    """Round the significant-digit string D to n digits. Returns (digits, exponent_carry)."""
    if n >= len(D): return D, 0
    head, nxt = D[:n], D[n]
    if nxt < '5': return head, 0
    carried = str(int(head) + 1)
    if len(carried) > n:                 # 999... -> 1000..., the exponent moves
        return carried[:n], 1
    return carried.rjust(n, '0'), 0

def traceable(tok, idx):
    """Exempt iff the literal is prefix-consistent with, OR a correct ROUNDING of, a stored literal.

    Prefix matching alone is wrong and the c39 sample proved it: our c34 letter prints
    -5.31691198314e-44 for a stored -5.31691198313966349161522824112e-44.  That is a CORRECT
    12-s.f. rounding and prefix matching calls it untraceable, because the last digit went 3 -> 4.
    A width discipline that punishes correct rounding would push every letter toward truncation,
    which is the defect it exists to prevent.
    """
    mm = mant(tok)
    if not mm: return True
    d, e = mm
    for E in (e, e - 1, e + 1):
        for D in idx.get(E, ()):
            if E == e and (D.startswith(d) or d.startswith(D)):
                return True
            r, carry = _round_digits(D, len(d))
            if r == d and E + carry == e:
                return True
    return False

# --- rules -------------------------------------------------------------------------
def rule_a(text, idx):
    hits = []
    for m in NUM.finditer(text):
        tok = m.group(0)
        if sigfigs(tok) >= THRESH and not traceable(tok, idx):
            hits.append((tok, m.start()))
    return hits

ORDINAL = re.compile(r'\d+\s*(st|nd|rd|th)\b', re.I)
CODEY   = re.compile(r'[(),\[\]{}=]')

def rule_b(text):
    """Pair a PRINT-width claim with the literal it labels.

    Deliberately conservative, and its residual false-positive rate is MEASURED and published rather
    than assumed: see the c39 letter.  Three suppressions, each added because it fired on a real line:
      - ordinals ("the 13th s.f. is wrong") state a POSITION, not a width;
      - a claim whose own span carries code punctuation ("nstr(digits", "12),") is a tokenisation
        artefact of scanning source, not a sentence;
      - the literal must be the NEAREST one to the claim inside a +-80 character window, because a
        wider window pairs a claim with whatever number happens to be nearby.
    """
    hits = []
    for W, span, s, e in width_statements(text):
        if ORDINAL.search(span) or CODEY.search(span):
            continue
        # Scan the WHOLE text and filter by distance -- never slice a window and then count digits
        # inside it.  A +-80 character window cut an 80-s.f. literal in half and the lint reported
        # its own truncation as the author's error: a print-width defect inside the width lint,
        # caught by its own known-answer test.
        best = None
        for m in NUM.finditer(text):
            d = min(abs(m.start() - s), abs(m.start() - e))
            if d > 80:
                continue
            tok = m.group(0)
            n = sigfigs(tok)
            if n < THRESH:
                continue
            if best is None or d < best[0]:
                best = (d, tok, n)
        if best and best[2] != W and abs(best[2] - W) <= 60:
            hits.append((W, span.strip(), best[1][:40] + ('…' if len(best[1]) > 40 else ''), best[2]))
    return hits

# --- KNOWN-ANSWER TEST --------------------------------------------------------------
POSB_FIXTURE = ("BEAST's published D* (dps-150, 83 s.f.) = "
                "0.14173323966388719139541568508418502362314456195501665594286660394665904218970743")
POSC_FIXTURE = "working dps 105 vs their 32 printed digits). Direction-carrying: my g[0][1] predicted"
NEGB_FIXTURE = "z[1] = 71732.90783055708304445059087085997984896"

def selftest(verbose=True):
    fails = []; ran = []
    def chk(name, cond, detail=""):
        ran.append(name)
        if not cond: fails.append("%s :: %s" % (name, detail))
        if verbose: print("   %-46s %s" % (name, "PASS" if cond else "*** FAIL *** " + detail))

    # POS-A: a hand-typed literal present in no artefact must be caught by RULE A.
    fake = "0.31415926535897932384626433832795028841971693993751"
    idx  = {}                                    # empty artefact index
    chk("POS-A rule A catches an untraceable literal", len(rule_a("value = " + fake, idx)) == 1,
        "expected exactly 1 hit")

    # NEG-A: the same literal, once it IS in the artefact index, must NOT be flagged (exemption b).
    mm = mant(fake); idx2 = {mm[1]: {mm[0]}}
    chk("NEG-A rule A exempts a re-printed literal", len(rule_a("value = " + fake, idx2)) == 0,
        "read-and-reprinted literal was flagged")

    # NEG-A2: a narrower correct quotation of a wider stored value must NOT be flagged.
    chk("NEG-A2 rule A exempts a narrower quotation",
        len(rule_a("value = 0.3141592653589793238462643383", idx2)) == 0,
        "legitimate narrower quotation was flagged")

    # --- controls for the ROUNDING half of the exemption.  The rounding fix shipped in
    # /shared/progress/c39-atlas-unpushed/ with NO control of its own; an exemption without a
    # known-answer test is exactly the untested-detector defect this file was written to refuse.
    # Fixture is the real c34 case: stored 30 s.f., letter printed a correct 12-s.f. rounding.
    stored = "-5.31691198313966349161522824112e-44"
    ms = mant(stored); idx3 = {ms[1]: {ms[0]}}
    # NEG-A3: a CORRECT rounding of a stored literal must NOT be flagged (last digit 3 -> 4).
    chk("NEG-A3 rule A exempts a correct rounding",
        len(rule_a("value = -5.31691198314e-44", idx3)) == 0,
        "a correct 12-s.f. rounding of a stored value was flagged")
    # POS-A2: a WRONG last digit is NOT a rounding and must still be caught.  Without this control
    # the exemption could be widened to "any prefix of the same length" and NEG-A3 would still pass.
    chk("POS-A2 rule A still catches a wrong rounding",
        len(rule_a("value = -5.31691198317e-44", idx3)) == 1,
        "a non-rounding near-miss was exempted")
    # NEG-A4: the exponent-carry branch (999... -> 100..., exponent moves) must also be exempt.
    ms4 = mant("9.999999999996e-44"); idx4 = {ms4[1]: {ms4[0]}}
    chk("NEG-A4 rule A exempts a rounding that carries the exponent",
        len(rule_a("value = 1.00000000000e-43", idx4)) == 0,
        "carry-rounded literal was flagged")

    # POS-B: the real m3 line -- "83 s.f." beside a literal counting 80.
    hb = rule_b(POSB_FIXTURE)
    chk("POS-B rule B catches 83 s.f. vs an 80-s.f. literal",
        any(h[0] == 83 and h[3] == 80 for h in hb), "got %r" % (hb,))

    # NEG-D: the SAME line's "dps-150" is a knob, not a print width, and must be ignored.
    chk("NEG-D rule B ignores dps-150 on that same line",
        all(h[0] != 150 for h in hb), "dps-150 was read as a print-width claim: %r" % (hb,))
    # NEG-D2 keeps the working-precision suppressor ITSELF under test: on the line above, 150 is now
    # rejected by the nearest-number rule, so it would pass even if the suppressor were deleted.
    # A control that passes for a reason other than the one it names is not a control.
    chk("NEG-D2 vocab suppressor still live (dps 150 digits)",
        all(w[0] != 150 for w in width_statements("ran at working dps 150 digits of headroom")),
        "got %r" % (width_statements("ran at working dps 150 digits of headroom"),))

    # NEG-C: a correct width claim must not fire.
    # Fixture READ from the committed artefact, never typed: typing it produced a 79-digit string
    # under an "80 s.f." label on the first attempt, and this control caught it.  Read, then count,
    # then label from the count.
    src = os.path.join(REPO, "data", "machine2_c36_dstar_175.txt")
    full = re.search(r"0\.\d{170,}", open(src, errors="replace").read()).group(0)
    lit80 = "0." + full.split(".")[1][:80]
    assert sigfigs(lit80) == 80, "fixture construction is wrong: %d" % sigfigs(lit80)
    good = "D* printed at 80 s.f. = " + lit80
    chk("NEG-C rule B silent on a correct width claim", len(rule_b(good)) == 0, "got %r" % (rule_b(good),))

    # POS-C: the exemplar c38's v1 detector missed -- a word between the integer and the unit.
    ws = width_statements(POSC_FIXTURE)
    chk("POS-C extractor sees '32 printed digits'", any(w[0] == 32 for w in ws), "got %r" % (ws,))
    chk("POS-C extractor ignores 'working dps 105'", all(w[0] != 105 for w in ws), "got %r" % (ws,))

    # NEG-B: tokeniser boundary -- no sub-literal may be produced from a longer one.
    toks = [m.group(0) for m in NUM.finditer(NEGB_FIXTURE)]
    chk("NEG-B tokeniser emits no sub-literal",
        toks == ["1", "71732.90783055708304445059087085997984896"], "got %r" % (toks,))

    if fails:
        print("\nKNOWN-ANSWER TEST FAILED -- %d control(s):" % len(fails))
        for f in fails: print("  " + f)
        print("REFUSING TO EMIT FINDINGS. An untested detector's silence is not evidence.")
        return False
    globals()["_N_CONTROLS"] = len(ran)
    return True

# --- driver -------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest-only", action="store_true")
    ap.add_argument("--letters", action="store_true", help="scan machine2-*.md letters")
    ap.add_argument("--commits", action="store_true", help="scan our own commit messages")
    ap.add_argument("--code",    action="store_true", help="scan data/code/**.py")
    ap.add_argument("--quiet-selftest", action="store_true")
    a = ap.parse_args()

    print("=== KNOWN-ANSWER TEST (runs before every scan; fail-closed) ===")
    if not selftest(verbose=not a.quiet_selftest):
        sys.exit(2)
    n = globals().get("_N_CONTROLS", 0)
    # counted, not typed: an earlier version of this line said "8/8" while 10 controls ran.
    print("known-answer test: %d/%d controls PASS\n" % (n, n))
    if a.selftest_only: return

    idx = build_artefact_index()
    print("artefact index: %d exponent buckets, %d literals >= %d s.f.\n"
          % (len(idx), sum(len(v) for v in idx.values()), THRESH))

    targets = []
    if a.letters:
        for fn in sorted(os.listdir(REPO)):
            if fn.startswith("machine2") and fn.endswith(".md"):
                targets.append(("letter", fn, open(os.path.join(REPO, fn), errors='replace').read()))
    if a.code:
        d = os.path.join(REPO, "data", "code")
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".py") and fn.startswith(("m2_", "machine2")):
                targets.append(("code", "data/code/" + fn, open(os.path.join(d, fn), errors='replace').read()))
    if a.commits:
        OURS = {"thebeastagi","machine2","machine2 (BEAST)","BEAST-AGI","beast-scout","beast-atlas","The Beast"}
        out = subprocess.run(["git","log","origin/main","--format=%x01%an%x02%H%x02%B"],
                             cwd=REPO, capture_output=True, text=True).stdout
        for chunk in out.split("\x01"):
            if not chunk.strip(): continue
            an, _, rest = chunk.partition("\x02")
            sha, _, body = rest.partition("\x02")
            if an in OURS:
                targets.append(("commit", sha[:7], body))

    nA = nB = 0
    for kind, name, text in targets:
        ha, hb = rule_a(text, idx), rule_b(text)
        if ha or hb:
            print("--- %s %s" % (kind, name))
            for tok, _ in ha[:6]:
                print("    RULE A untraceable literal (%d s.f.): %s" % (sigfigs(tok), tok[:60]))
            if len(ha) > 6: print("    ... +%d more" % (len(ha) - 6))
            for W, span, tok, n in hb[:6]:
                print("    RULE B claims %r but the literal counts %d s.f.: %s" % (span, n, tok))
            nA += len(ha); nB += len(hb)
    print("\nSCANNED %d objects | RULE A hits %d | RULE B hits %d" % (len(targets), nA, nB))

if __name__ == "__main__":
    main()
