#!/usr/bin/env python3
"""
machine2 cycle 39 -- THE SECTION-6 WIDTH LINT, with the known-answer test BEAST-AGI required.

What it checks
--------------
A decimal literal that a human TYPED is a claim with no artefact behind it.  For every literal of
>= THRESHOLD significant figures appearing in one of our prose surfaces (letters, preregs, errata,
commit messages), the lint asks whether that exact string exists in a committed non-prose artefact:

  EXEMPT   the literal appears VERBATIM in a committed data/code artefact
           -> it was read from a file and re-printed.  Ruling amendment (b).
  NARROWED the literal is a strict PREFIX of a wider literal in a committed artefact
           -> a truncated quote: the c35 defect (a 20 s.f. literal under a 45 s.f. warrant).
              This is the case an exemption keyed on "appears in a file" would wrongly forgive,
              so it is separated out rather than folded into EXEMPT.
  UNBACKED the literal appears in no committed artefact at all
           -> hand-typed.  c37's own worst instances live here, and a route-keyed search
              (data/code/** only) is structurally blind to them.  Ruling amendment (a).

Scope: our prose surfaces AND our commit messages.  Ruling amendment (a) again -- c37 P2 measured
that the commit-message route is the one a file census cannot see.

Known-answer test
-----------------
`selftest()` runs the same classifier over a synthetic corpus with the answers written down:
two positive controls it MUST catch and three negative controls it MUST NOT flag.  It is asserted,
it fails loudly, and the lint refuses to run if it fails -- because a guard that has never fired is
indistinguishable from a guard that cannot fire.
"""
import collections
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
THRESHOLD = 12

NUM = re.compile(r"(?<![\w.])[-+]?(?:\d+\.\d+)(?:[eEdD][-+]?\d+)?(?![\w.])")


def digits(tok):
    t = tok.lstrip("+-")
    t = re.split(r"[eEdD]", t)[0]
    return t.replace(".", "").lstrip("0")


def classify(tok, ours, theirs=(frozenset(), frozenset())):
    """ours/theirs = (exact digit-strings, all prefixes thereof) for committed non-prose artefacts.

    THEIRS is a separate class, not a silent exemption: quoting another machine's artefact is
    legitimate, but it is a DIFFERENT warrant from quoting our own and the lint must say which.
    Found by running v1 over the real corpus: its widest 'UNBACKED' hit was a 40 s.f. literal we had
    correctly quoted out of an m1 file -- a false positive produced by an index that only knew our
    own artefacts."""
    oe, op = ours
    te, tp = theirs
    d = digits(tok)
    if len(d) < THRESHOLD:
        return None
    if d in oe:
        return "EXEMPT"
    if d in te:
        return "EXEMPT-THEIRS"
    if d in op:
        return "NARROWED"
    if d in tp:
        return "NARROWED-THEIRS"
    return "UNBACKED"


def build_artefact_index(texts):
    exact, pref = set(), set()
    for txt in texts:
        for m in NUM.finditer(txt):
            d = digits(m.group(0))
            if len(d) >= THRESHOLD:
                exact.add(d)
                for i in range(THRESHOLD, len(d)):
                    pref.add(d[:i])
    return exact, pref


def selftest():
    """KNOWN-ANSWER TEST.  Answers written down before the classifier is called."""
    artefact = (
        'a = 0.104051654913127452341094763510384719236412236\n'
        '"g00": "-5.31691198313966349161522824112e-44"\n'
    )
    theirs_artefact = 'z[1] = 71732.90783055708304445059087085997984896\n'
    ours = build_artefact_index([artefact])
    theirs = build_artefact_index([theirs_artefact])

    cases = [
        # (name, literal, expected verdict)
        ("POSITIVE 1 -- hand-typed literal in no artefact",
         "0.14173323966388719139541568508418502362", "UNBACKED"),
        ("POSITIVE 2 -- 20 s.f. truncation of a committed 45 s.f. value (the c35 defect)",
         "0.10405165491312745234", "NARROWED"),
        ("NEGATIVE 1 -- exact re-print of a committed 45 s.f. literal",
         "0.104051654913127452341094763510384719236412236", "EXEMPT"),
        ("NEGATIVE 2 -- exact re-print of a committed 30 s.f. JSON serialisation",
         "-5.31691198313966349161522824112e-44", "EXEMPT"),
        ("NEGATIVE 3 -- 11 s.f. literal, one digit below threshold",
         "-37.481971360", None),
        ("NEGATIVE 4 -- ISO date, not a decimal literal", "2026-09-07", None),
        ("NEGATIVE 5 -- commit sha", "6181e51df47549dabb6a88280b0fbdce7fbec2c1", None),
        ("NEGATIVE 6 -- exact quote of ANOTHER MACHINE'S committed literal (v1 false positive)",
         "71732.90783055708304445059087085997984896", "EXEMPT-THEIRS"),
    ]
    ok = True
    for name, text, expect in cases:
        toks = NUM.findall(text)
        got = classify(toks[0], ours, theirs) if toks else None
        flag = "OK " if got == expect else "FAIL"
        if got != expect:
            ok = False
        print(f"  [{flag}] {name}\n         expected {expect!r}, got {got!r}")
    return ok


def is_ours(path):
    b = os.path.basename(path)
    if b.startswith(("machine1", "machine3", "m3_", "m1_", "letter", "BEAST", "SAPIENS")):
        return False
    return b.startswith(("machine2", "m2_", "c3"))


def main():
    print("== KNOWN-ANSWER TEST ==")
    ok = selftest()
    print(f"== selftest {'PASSED' if ok else 'FAILED'} ==\n")
    if not ok:
        print("LINT REFUSES TO RUN: its own known-answer test failed.")
        sys.exit(2)

    tracked = [f for f in subprocess.run(["git", "-C", R, "ls-files"], capture_output=True,
                                         text=True).stdout.split("\n")
               if f and not f.lower().endswith(".pdf")]
    ours = [f for f in tracked if is_ours(f)]
    prose = [f for f in ours if f.endswith(".md")]
    artefacts = [f for f in ours if not f.endswith(".md")]

    def read(p):
        try:
            return open(os.path.join(R, p), encoding="utf-8", errors="replace").read()
        except OSError:
            return ""

    # THEIRS includes their prose: quoting an m1/m3 letter is still quoting a committed artefact.
    theirs_files = [f for f in tracked if f not in set(ours)]
    ours_idx = build_artefact_index([read(f) for f in artefacts])
    theirs_idx = build_artefact_index([read(f) for f in theirs_files])
    print(f"artefact index: {len(ours_idx[0])} distinct >= {THRESHOLD} s.f. literals from "
          f"{len(artefacts)} of our committed data/code files; "
          f"{len(theirs_idx[0])} from {len(theirs_files)} of theirs (prose included)")

    findings = collections.Counter()
    worst = collections.defaultdict(list)

    surfaces = [(f, read(f), "prose") for f in prose]
    raw = subprocess.run(["git", "-C", R, "log", "--format=%H%x00%B%x01"],
                         capture_output=True, text=True).stdout
    for rec in raw.split("\x01"):
        if "\x00" not in rec:
            continue
        sha, body = rec.split("\x00", 1)
        if body.lstrip().lower().startswith("machine2"):
            surfaces.append((sha.strip()[:7] + " (commit message)", body, "commit"))

    for name, txt, kind in surfaces:
        for m in NUM.finditer(txt):
            v = classify(m.group(0), ours_idx, theirs_idx)
            if v is None:
                continue
            # count EVERY class.  v1 counted EXEMPT but not EXEMPT-THEIRS, so a whole class
            # vanished from the totals silently -- the same family of defect this lint hunts.
            findings[(kind, v)] += 1
            if v in ("UNBACKED", "NARROWED", "NARROWED-THEIRS"):
                worst[v].append((len(digits(m.group(0))), m.group(0), name))

    print(f"surfaces linted: {len(prose)} prose files + "
          f"{len(surfaces)-len(prose)} m2 commit messages\n")
    for kind in ("prose", "commit"):
        for v in ("EXEMPT", "EXEMPT-THEIRS", "NARROWED", "NARROWED-THEIRS", "UNBACKED"):
            print(f"  {kind:<7} {v:<9} {findings[(kind, v)]:>6}")
    tot_flag = sum(n for (k, v), n in findings.items()
                   if v in ("UNBACKED", "NARROWED", "NARROWED-THEIRS"))
    tot = sum(findings.values())
    print(f"\n  FLAGGED {tot_flag} of {tot} literals "
          f"({100*tot_flag/tot:.1f}%) at threshold {THRESHOLD} s.f.")

    for v in ("NARROWED", "NARROWED-THEIRS", "UNBACKED"):
        print(f"\n-- widest {v} (top 8) --")
        for w, tok, name in sorted(worst[v], reverse=True)[:8]:
            print(f"   {w:>4} s.f.  {tok[:46]:<46} {name[:64]}")


if __name__ == "__main__":
    main()
