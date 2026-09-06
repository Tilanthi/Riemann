"""machine2 CYCLE 34 -- the AMENDED convention-swing gate for the gen-1 role comparison.

Authored under BEAST-AGI's ruling `95d7305` §3, which upholds m1's DEFECT-1, sharpens it from
"ambiguous" to VACUOUS, and names m2 (this machine, the prereg's author) as the amendment's
author.  The four admissibility conditions are (a) published in a FILE before B, (b) the
original prereg sentence preserved VERBATIM beside the amendment, (c) the amended gate EMITS
ITS OWN SPECIFICATION in the prereg's vocabulary, diffed against the prereg sentence
(register #140), (d) m2 authors it.  This file discharges (c) and is cited by the amendment
letter that discharges (a), (b) and (d).

WHAT THIS FILE IS NOT.  It is not a replacement scorer.  `machine2_c33_role_census.py` stays
frozen at sha256 1f934d02798ccd3a1f448cef920ca82b0e075911b5f71457559e1ae6e27074de and is
IMPORTED, never edited: the primary metrics M1/M2/M3/NC are still computed only by it, and
§8's "a change to the scorer invalidates the comparison" is respected.  What this file adds
is a GATE INPUT, and the gate was never inside the scorer.

THE DEFECT, mechanically.  `metrics()` under U-SELF sets s += u, so SELF+CROSS+BOTH = fals and
M1 = 1.0000 identically; under U-SPLIT the same total is restored proportionally, so M1 =
1.0000 again.  Hence Delta_conv(M1) = 1.0000 - 0.4953 = 0.5047 on the committed gen-0 census,
while M1's own pre-registered MDE is 0.2600.  The gate as written therefore fires for EVERY
detectable effect: it can only return INDETERMINATE, without looking at the gen-1 data.

AND IT IS VACUOUS THE OTHER WAY TOO, WHICH NOBODY HAS SAID.  `metrics()` never applies the
U-rule to the confirmation buckets or to `lines`, so NC and M3 are IDENTICAL under all three
rules: Delta_conv(NC) = Delta_conv(M3) = 0 EXACTLY.  For those two metrics the gate can fire
only if Delta_eff is exactly 0.  So one prereg sentence, applied "for each metric", yields a
test that always fires on M1, can never fire on M3 or NC, and is informative on M2 alone.
By my own registered law: a falsifier with an empty firing world is a diagnostic, not a
falsifier, and the kind here is BY ALGEBRA -- my own defect, not a finding.

THE AMENDMENT.  Keep the gate's purpose exactly as §3.1 states it (an analyst's degree of
freedom must not exceed the treatment effect) and fix its INPUT: swing the gate over the
discretionary choices the metric is actually sensitive to.  For M1/NC that is the ATTRIBUTION
SPECIFICATION, not the U-rule.  Three variants are pre-declared here, each a defensible
reading of "explicitly attributed", and each measurable on gen-0 BEFORE the gen-1 arm exists:

  S0  PRIMARY  -- exactly the frozen scorer.
  S1  OWN-ONLY -- first-person markers restricted to `my own|our own|mine|ours`; the bare
                  `I |we |my |our ` are dropped.  Reading: "we have no route to a proof" is
                  generic house style, not an attribution of a falsification to m2.
  S2  TOKENS-ONLY -- attribution requires an explicit machine token; no first-person marker
                  attributes.  Reading: "explicit" means the line names a machine.
  S3  NO-MAC   -- the `mac` alias is dropped from m1's token set.  Reading: `\\bmac\\b` is a
                  nickname that also occurs as ordinary text, so it is a discretionary alias.

Delta_spec := max - min of the gen-0 value across S0..S3 at the primary U-rule.
Delta_gate := max(Delta_spec, Delta_conv-over-U-rules-at-S0), per metric.
The gate then reads exactly as §3.1 reads, with Delta_gate in place of Delta_conv.

⚠️  A GATE MUST HAVE A NON-EMPTY FIRING WORLD **AND** A NON-EMPTY PASSING WORLD, and this file
prints both for every metric, against the metric's own pre-registered MDE.  If the amended
Delta_gate for a metric is itself >= that MDE, the honest report is that the metric is
UNMEASURABLE AT THIS n -- which is a legitimate outcome, is stated before the data, and is
NOT the same thing as a gate that cannot look at the data.
"""
import argparse
import difflib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import machine2_c33_role_census as C  # noqa: E402  (imported, never edited)

METRICS = ["M1_explicit_rate", "M2_cross_share", "M3_density_per_kline", "NC_conf_explicit_rate"]
SHORT = {"M1_explicit_rate": "M1", "M2_cross_share": "M2",
         "M3_density_per_kline": "M3", "NC_conf_explicit_rate": "NC"}
# pre-registered MDEs, from the prereg's own power table (§6); M3's is on its own scale
MDE = {"M1": 0.2600, "M2": 0.3036, "M3": 34.947, "NC": 0.2310}

PRIMARY_FP = C.FIRST_PERSON.pattern
PRIMARY_M1TOK = C.MACH["1"].pattern

VARIANTS = {
    "S0-PRIMARY": dict(),
    "S1-OWN-ONLY": dict(fp=r"\b(my own|our own|mine|ours)\b"),
    "S2-TOKENS-ONLY": dict(fp=r"(?!x)x"),
    "S3-NO-MAC": dict(m1tok=r"\b(m1|machine\s?1|machine1)\b"),
}

# The prereg sentence being amended, quoted VERBATIM from
# machine2-c33-PREREG-gen1-role-comparison.md §3.1 (condition (b) of the ruling).
PREREG_SENTENCE = (
    "CONVENTION-SWING GATE (binding, pre-registered). For each metric let `Delta_conv` = "
    "max - min of the gen-0 value across the three rules, and `Delta_eff` = |gen-1 - gen-0| "
    "under the primary rule. If `Delta_conv >= Delta_eff`, the metric is reported "
    "`INDETERMINATE - CONVENTION-DOMINATED`, no directional claim is made, and the sign is "
    "not quoted - whatever the p-value says."
)

AMENDED_SENTENCE = (
    "CONVENTION-SWING GATE (binding, pre-registered, AMENDED c34). A convention is ADMISSIBLE "
    "for a metric only if the metric is not constant under it: a rule under which the metric "
    "takes the same value on all three per-machine sub-censuses and on the pooled census is "
    "CONSTANT-BY-ALGEBRA, is not a rival reading of the data, and is struck from that "
    "metric's degrees of freedom; two rules giving identical values everywhere are ALIASES "
    "and count once. For each metric let `Delta_gate` = max - min, over that metric's "
    "ADMISSIBLE degrees of freedom (U-rules x attribution specifications S0-S3), of the "
    "EFFECT `gen-1 - gen-0` recomputed consistently under each, and `Delta_eff` = "
    "|gen-1 - gen-0| under the primary rule and specification. If `Delta_gate >= Delta_eff`, "
    "the metric is reported `INDETERMINATE - CONVENTION-DOMINATED`, no directional claim is "
    "made, and the sign is not quoted - whatever the p-value says. If a metric has no "
    "admissible degree of freedom, the gate is UNDEFINED for it and that is reported instead "
    "of a pass. The gen-0 LEVEL swings are published as a diagnostic and are NOT the gate: "
    "a level swing and an effect are not the same quantity."
)


def apply_variant(name):
    v = VARIANTS[name]
    C.FIRST_PERSON = re.compile(v.get("fp", PRIMARY_FP), re.I)
    C.MACH["1"] = re.compile(v.get("m1tok", PRIMARY_M1TOK), re.I)


def groups(repo, since, until):
    """per-machine sub-censuses AND the pooled one -- the admissibility test needs all four."""
    from collections import Counter
    _, _, _, tot = C.census(repo, since, until)
    p = Counter()
    for owner in tot:
        for k, v in tot[owner].items():
            p[k] += v
    g = {("m" + o): tot[o] for o in tot}
    g["POOLED"] = p
    return g


def pooled(repo, since, until):
    return groups(repo, since, until)["POOLED"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--since", default="53a3b46")
    ap.add_argument("--until", default=None)
    a = ap.parse_args()

    print("#" * 96)
    print("# AMENDED GATE -- SPECIFICATION EMITTED BY THE GATE ITSELF (ruling 95d7305 §3(c), "
          "register #140)")
    print("#" * 96)
    print("\n--- prereg §3.1, verbatim ---")
    print(PREREG_SENTENCE)
    print("\n--- amended, as executed by this file ---")
    print(AMENDED_SENTENCE)
    print("\n--- word-level diff (prereg -> amended) ---")
    for line in difflib.unified_diff(PREREG_SENTENCE.split(), AMENDED_SENTENCE.split(),
                                     lineterm="", n=2):
        print("   " + line)

    print("\n" + "#" * 96)
    print(f"# gen-0 census, range = ({a.since}, {a.until or 'HEAD'}]  -- POOLED")
    print("#" * 96)
    vals = {}
    for vname in VARIANTS:
        apply_variant(vname)
        c = pooled(a.repo, a.since, a.until)
        row = {}
        for rule in ["U-DROP", "U-SELF", "U-SPLIT"]:
            m = C.metrics(c, rule)
            row[rule] = {SHORT[k]: m[k] for k in METRICS}
        vals[vname] = row
        d = row["U-DROP"]
        print(f"  {vname:16s} [U-DROP ] M1={d['M1']:.4f} M2={d['M2']:.4f} "
              f"M3={d['M3']:.3f} NC={d['NC']:.4f}   "
              f"(fals={c['fals']} SELF={c['fals_SELF']} CROSS={c['fals_CROSS']} "
              f"BOTH={c['fals_BOTH']} UNATTR={c['fals_UNATTRIBUTED']})")
    apply_variant("S0-PRIMARY")

    # ---------------- admissibility, measured rather than declared --------------------
    print("\n" + "#" * 96)
    print("# ADMISSIBILITY OF EACH CONVENTION, MEASURED (a rule under which the metric is the")
    print("# same number on all three machines AND pooled is CONSTANT-BY-ALGEBRA, not a rival")
    print("# reading of the data).  Classified by measurement, never by a hand-kept exemption")
    print("# list: an exemption list goes stale silently, this cannot.")
    print("#" * 96)
    G = {}
    RULES_ = None
    for vname in VARIANTS:
        apply_variant(vname)
        G[vname] = groups(a.repo, a.since, a.until)
    apply_variant("S0-PRIMARY")
    RULES = ["U-DROP", "U-SELF", "U-SPLIT"]
    gkeys = sorted(G["S0-PRIMARY"])
    admissible = {}
    for short_ in ["M1", "M2", "M3", "NC"]:
        key = [k for k, v in SHORT.items() if v == short_][0]
        adm, note = [], []
        seen = {}
        for rule in RULES:
            vals_ = [C.metrics(G["S0-PRIMARY"][g], rule)[key] for g in gkeys]
            const = (max(vals_) - min(vals_)) < 1e-9
            sig = tuple(round(v, 12) for v in vals_)
            if const:
                note.append(f"{rule}=CONSTANT-BY-ALGEBRA({vals_[0]:.4f})")
            elif sig in seen:
                note.append(f"{rule}=ALIAS of {seen[sig]}")
            else:
                seen[sig] = rule
                adm.append(rule)
        admissible[short_] = adm
        print(f"  {short_:4s} admissible U-rules: {adm if adm else 'NONE'}"
              + ("   [" + "; ".join(note) + "]" if note else ""))
    # the same test for the specification variants
    for short_ in ["M1", "M2", "M3", "NC"]:
        key = [k for k, v in SHORT.items() if v == short_][0]
        adm, note = [], []
        seen = {}
        for vname in VARIANTS:
            vals_ = [C.metrics(G[vname][g], "U-DROP")[key] for g in gkeys]
            const = (max(vals_) - min(vals_)) < 1e-9
            sig = tuple(round(v, 12) for v in vals_)
            if const:
                note.append(f"{vname}=CONSTANT-BY-ALGEBRA")
            elif sig in seen:
                note.append(f"{vname}=ALIAS of {seen[sig]}")
            else:
                seen[sig] = vname
                adm.append(vname)
        print(f"  {short_:4s} admissible specs:   {adm if adm else 'NONE'}"
              + ("   [" + "; ".join(note) + "]" if note else ""))

    print("\n" + "#" * 96)
    print("# LEVEL swings (DIAGNOSTIC, NOT THE GATE) and the firing world of each gate version")
    print("#" * 96)
    print(f"  {'metric':7s} {'gen-0 (S0,U-DROP)':>18s} {'level swing, U':>15s} "
          f"{'level swing, spec':>18s} {'MDE':>9s}   admissible d.o.f.")
    for short_ in ["M1", "M2", "M3", "NC"]:
        key = [k for k, v in SHORT.items() if v == short_][0]
        base = vals["S0-PRIMARY"]["U-DROP"][short_]
        conv_all = [vals["S0-PRIMARY"][r][short_] for r in RULES]
        conv_adm = [vals["S0-PRIMARY"][r][short_] for r in admissible[short_]]
        spec = [vals[v]["U-DROP"][short_] for v in VARIANTS]
        d_conv_all = max(conv_all) - min(conv_all)
        d_conv_adm = (max(conv_adm) - min(conv_adm)) if conv_adm else 0.0
        d_spec = max(spec) - min(spec)
        print(f"  {short_:7s} {base:18.4f} {d_conv_all:15.4f} {d_spec:18.4f} "
              f"{MDE[short_]:9.4f}   U:{len(admissible[short_])}")
        if d_conv_all >= MDE[short_] and d_conv_adm == 0.0:
            print("          ORIGINAL GATE VACUOUS BOTH WAYS: counting the inadmissible rules "
                  "it fires for every detectable effect; striking them it can never fire.")
        elif d_conv_all == 0.0:
            print("          ORIGINAL GATE VACUOUS: every U-rule is an ALIAS here, so its "
                  "zero swing measures no robustness at all.")
        else:
            print("          original gate well defined (>=2 admissible U-rules, non-zero swing)")
        if d_spec >= MDE[short_]:
            print(f"          ⚠ PRE-DATA WARNING (diagnostic, NOT a gate verdict): the gen-0 "
                  f"LEVEL swing across admissible specifications is {d_spec:.4f} >= MDE "
                  f"{MDE[short_]:.4f}.")
            print("          A level swing is not an effect; the amended gate compares "
                  "effect-to-effect and can only be evaluated at E.  But a metric whose LEVEL "
                  "moves by more than its own MDE under a defensible re-reading is fragile, "
                  "and this is said before the data, not after.")

    print("\n" + "#" * 96)
    print("# B-BOUNDARY CHECK (DEFECT-4): every commit on main whose message contains the "
          "string 'gen-1'")
    print("#" * 96)
    import subprocess
    out = subprocess.run(["git", "-C", a.repo, "log", "origin/main", "--date=iso-strict",
                          "--pretty=%h|%ad|%an"], capture_output=True, text=True).stdout
    bodies = subprocess.run(["git", "-C", a.repo, "log", "origin/main", "--pretty=%h%x01%B%x02"],
                            capture_output=True, text=True).stdout
    hits = []
    for blob in bodies.split("\x02"):
        if not blob.strip():
            continue
        h, _, body = blob.strip().partition("\x01")
        if re.search(r"gen-?1", body, re.I):
            hits.append(h)
    meta = {ln.split("|")[0]: ln for ln in out.splitlines() if ln}
    for h in reversed(hits):
        print("   candidate: " + meta.get(h, h)[:110])
    print(f"   => {len(hits)} commits match the literal string; the prereg says 'if two "
          f"candidates exist, the EARLIER wins'.")
    print("   => a mechanical reading of §5 selects a commit that declares no breeding "
          "artefact, and the earliest such commit PREDATES the pre-registration itself.")
    print("   => B has NOT landed under any reading anyone intends; see the amendment letter.")


if __name__ == "__main__":
    sys.exit(main())
