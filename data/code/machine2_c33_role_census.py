"""machine2 CYCLE 33 -- the FROZEN scoring instrument for the gen-1 role comparison.

This file is hashed and committed AS PART OF the pre-registration
`machine2-c33-PREREG-gen1-role-comparison.md`.  It is the ONLY instrument that may be used
to score that comparison.  Any change to it after the freeze invalidates the comparison and
must be published as a new pre-registration, not as an amendment.

Usage:
    python3 m2_c33_role_census.py --repo /path/to/Riemann --arm gen0
    python3 m2_c33_role_census.py --repo /path/to/Riemann --arm gen1 --boundary <sha>

Everything the script decides is stated in the pre-registration in words; this file is the
mechanical form of those words and the words govern if they ever disagree.
"""
import argparse
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

# ---------------------------------------------------------------- corpus
# Owning machine is read from the FILENAME, never from the text.  Files that match no rule
# are EXCLUDED and their count is REPORTED, so an exclusion can never be silent.
OWNER_RE = re.compile(r"^(?:machine|m)([123])[-_]", re.I)
M3_ALIAS = re.compile(r"astra-pa", re.I)
EXCLUDE_PREFIX = re.compile(r"^(BEAST|sapiens|README|PROTOCOL)", re.I)


def owner_of(path):
    """None => excluded.  Top-level *.md only; data/ artefacts are not letters."""
    if not path.endswith(".md") or "/" in path:
        return None
    base = os.path.basename(path)
    if EXCLUDE_PREFIX.match(base):
        return None
    m = OWNER_RE.match(base)
    if m:
        return m.group(1)
    if M3_ALIAS.search(base):
        return "3"
    return None

# ---------------------------------------------------------------- markers
# A line is FALSIFICATION-MARKED iff it matches FALS_CI (case-insensitive) or FALS_CS
# (case-sensitive: these three are house-style shouted tokens and lowercase uses of the
# same words are ordinary English).
FALS_CI = re.compile(
    r"\b(falsifi(?:ed|es|able|cation)|refut(?:e|ed|es|ation)|retract(?:ed|ion|s)?|"
    r"withdraw(?:n|s|al)?|errat(?:um|a)|disprov(?:e|ed|es)|supersed(?:e|ed|es)|"
    r"does not hold|no longer holds|is false|is wrong|turned out wrong)\b", re.I)
FALS_CS = re.compile(r"\b(RED|WRONG|DEAD|FALSIFIED|REFUTED)\b")

# The negative control: lines marked as CONFIRMATION rather than falsification.
CONF_CI = re.compile(
    r"\b(confirm(?:ed|s|ation)|reproduc(?:e|ed|es)|verifi(?:ed|es|cation)|"
    r"held|holds|corroborat(?:e|ed|es))\b", re.I)
CONF_CS = re.compile(r"\b(GREEN|HELD|CONFIRMED|VERIFIED)\b")

MACH = {
    "1": re.compile(r"\b(m1|machine\s?1|machine1|mac)\b", re.I),
    "2": re.compile(r"\b(m2|machine\s?2|machine2|beast-atlas)\b", re.I),
    "3": re.compile(r"\b(m3|machine\s?3|machine3|astra-pa)\b", re.I),
}
FIRST_PERSON = re.compile(r"\b(my own|our own|mine|ours|I |we |my |our )", re.I)

# Lines that are pure machinery are skipped BEFORE any classification.
SKIP = re.compile(r"^\s*(```|\||<!--|\[|\!\[)")


def classify_line(line, owner):
    """-> (is_fals, is_conf, bucket) with bucket in SELF / CROSS / BOTH / UNATTRIBUTED."""
    is_fals = bool(FALS_CI.search(line) or FALS_CS.search(line))
    is_conf = bool(CONF_CI.search(line) or CONF_CS.search(line))
    named = {k for k, rx in MACH.items() if rx.search(line)}
    self_named = owner in named
    cross_named = bool(named - {owner})
    if not self_named and not cross_named:
        # first person with no machine token at all = an explicit self-attribution
        bucket = "SELF" if FIRST_PERSON.search(line) else "UNATTRIBUTED"
    elif self_named and cross_named:
        bucket = "BOTH"
    elif cross_named:
        bucket = "CROSS"
    else:
        bucket = "SELF"
    return is_fals, is_conf, bucket


def files_in_arm(repo, since, until):
    """Letters whose FIRST appearance on main lies in (since, until].  until may be None."""
    rng = f"{since}..{until}" if until else f"{since}..HEAD"
    out = subprocess.run(["git", "-C", repo, "log", "--name-only", "--diff-filter=A",
                          "--pretty=format:", rng],
                         capture_output=True, text=True, check=True).stdout
    seen, keep, excl = set(), [], []
    for p in out.splitlines():
        p = p.strip()
        if not p or p in seen:
            continue
        seen.add(p)
        if not os.path.exists(os.path.join(repo, p)):
            continue
        o = owner_of(p)
        if o:
            keep.append((p, o))
        elif p.endswith(".md"):
            excl.append(p)
    return sorted(keep), sorted(excl)


def census(repo, since, until):
    tot = defaultdict(Counter)
    files, excluded = files_in_arm(repo, since, until)
    per_file = []
    for path, owner in files:
        fc = Counter()
        with open(os.path.join(repo, path), errors="replace") as f:
            for line in f:
                if SKIP.match(line) or not line.strip():
                    continue
                fc["lines"] += 1
                is_f, is_c, b = classify_line(line, owner)
                if is_f:
                    fc["fals"] += 1
                    fc["fals_" + b] += 1
                if is_c and not is_f:
                    fc["conf"] += 1
                    fc["conf_" + b] += 1
        fc["files"] = 1
        tot[owner].update(fc)
        per_file.append((path, owner, fc))
    return files, excluded, per_file, tot


def metrics(c, rule="U-DROP"):
    """M1 explicit-attribution rate, M2 cross-share, M3 density, NC control rate."""
    F = c["fals"]
    s, x, b, u = c["fals_SELF"], c["fals_CROSS"], c["fals_BOTH"], c["fals_UNATTRIBUTED"]
    if rule == "U-SELF":
        s = s + u
        u = 0
    elif rule == "U-SPLIT":
        att = s + x + b
        if att:
            s = s + u * s / att
            x = x + u * x / att
            b = b + u * b / att
        u = 0
    att = s + x + b
    m1 = att / F if F else float("nan")
    m2 = (x + b) / att if att else float("nan")
    m3 = 1000.0 * F / c["lines"] if c["lines"] else float("nan")
    C = c["conf"]
    catt = c["conf_SELF"] + c["conf_CROSS"] + c["conf_BOTH"]
    nc = catt / C if C else float("nan")
    return dict(M1_explicit_rate=m1, M2_cross_share=m2, M3_density_per_kline=m3,
                NC_conf_explicit_rate=nc, F=F, attributed=att, unattributed=u,
                lines=c["lines"], files=c["files"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--since", default="53a3b46")
    ap.add_argument("--until", default=None)
    ap.add_argument("--label", default="arm")
    a = ap.parse_args()
    files, excluded, per_file, tot = census(a.repo, a.since, a.until)
    print(f"# arm={a.label}  range=({a.since}, {a.until or 'HEAD'}]  "
          f"files={len(files)}  excluded_md={len(excluded)}")
    for e in excluded:
        print(f"#   EXCLUDED: {e}")
    pooled = Counter()
    for owner in sorted(tot):
        for k, v in tot[owner].items():
            pooled[k] += v
    for owner in sorted(tot) + ["POOLED"]:
        c = pooled if owner == "POOLED" else tot[owner]
        print(f"\n## m{owner}" if owner != "POOLED" else "\n## POOLED")
        print(f"   files={c['files']} lines={c['lines']} fals={c['fals']} conf={c['conf']}")
        print(f"   buckets: SELF={c['fals_SELF']} CROSS={c['fals_CROSS']} "
              f"BOTH={c['fals_BOTH']} UNATTRIBUTED={c['fals_UNATTRIBUTED']}")
        for rule in ["U-DROP", "U-SELF", "U-SPLIT"]:
            m = metrics(c, rule)
            print(f"   [{rule:7s}] M1={m['M1_explicit_rate']:.4f} M2={m['M2_cross_share']:.4f} "
                  f"M3={m['M3_density_per_kline']:.3f} NC={m['NC_conf_explicit_rate']:.4f}")


if __name__ == "__main__":
    sys.exit(main())
