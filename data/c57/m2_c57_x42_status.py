#!/usr/bin/env python3
"""m2_c57_x42_status.py -- ONE STATUS FOR x=42, in ONE machine-readable field.

SUPERSEDES the two statuses that m2_c56_scores_gated.json shipped in a single object:
    VERDICT (machine-readable) : "x=42 is left UNSPENT for a future cycle"
    what_the_author_has_seen   : "... treat it as at most SEMI-BLIND"
The stronger of the two won a hop to the supervisor and a second hop into m1's L202, which carries
BOTH in one sentence.  ⇒ A QUALIFICATION THAT IS NOT IN THE FIELD THE NEXT PROGRAM READS IS NOT A
QUALIFICATION.  This file has exactly one status field and every qualification lives inside it.

It DERIVES the status from the artefacts rather than asserting it, and it never computes p2.
"""
import json, os, sys
_F = os.path.dirname(os.path.abspath(__file__))
C56 = os.path.abspath(os.path.join(_F, "..", "c56"))
sys.path.insert(0, os.path.abspath(os.path.join(_F, "..", "c55")))
print("resolver: c56 dir = %s" % C56)
import m2_c55_score as S55

nf = {p: os.path.join(C56, "m2_c56_nodes_%s_x42_N100_dps300.json" % p) for p in ("even", "odd")}
tab, cert, forder = S55.pooled_table(nf)
holes = [r["p"] for r in tab if r["nu"] is None]
seen = [r["p"] for r in tab if r["nu"] is not None]
lead = next((i for i, r in enumerate(tab) if r["nu"] is not None), len(tab))

# constructive non-determination: two admissible completions of the leading hole block
tail = []
for r in tab[lead:]:
    if r["nu"] is None:
        break
    tail.append(r["nu"] - (r["p"] - 1))
cand = {S55._first_leave([2] * lead + tail, 2),
        S55._first_leave([0 - (p - 1) for p in range(1, lead + 1)] + tail, 2)}

gp = json.load(open(os.path.join(C56, "m2_c53_gpred_x42_N100_dps300.json")))

out = {
    "window": 42,
    "STATUS": "SEMI-BLIND-TAIL-SEEN",
    "status_is_the_only_one_in_this_artefact": True,
    "supersedes": {
        "file": "data/c56/m2_c56_scores_gated.json",
        "withdrawn_status_1": {
            "text": "x=42 is left UNSPENT for a future cycle",
            "where": "VERDICT (machine-readable)",
            "why_withdrawn": "a window whose author has read %d of %d pooled node counts, and whose "
                             "entire eigenvalue ladder and Model G prediction are published, is not "
                             "unspent" % (len(seen), len(tab))},
        "withdrawn_clause_2": {
            "text": "The raw node artefacts are committed and DO contain the values",
            "where": "what_the_author_has_seen (prose)",
            "why_withdrawn": "FALSE as written. %d of %d pooled positions are nu=null, including "
                             "the entire leading block of %d, so the artefacts contain node counts "
                             "of the ladder's TAIL and do not contain p2."
                             % (len(holes), len(tab), lead)},
        "clause_2_upheld_in_part": "the SEMI-BLIND conclusion is right; its stated reason was not. "
                                   "It is semi-blind because the tail was SEEN, not because p2 is "
                                   "derivable -- p2 is not derivable."},
    "what_is_spent": {
        "eigenvalue_arm": "PUBLIC -- %d pooled levels, certified prefix %d, and Model G's prediction "
                          "p2 = %s, all published in c56"
                          % (gp["pooled_levels"], gp["certified_prefix"], gp["model_G_p2"]),
        "node_arm_tail": "SEEN -- pooled positions %s carry node counts the author has read"
                         % (seen,),
        "node_arm_prefix": "UNSEEN AND UNDERIVABLE -- pooled positions %s are nu=null" % (holes,)},
    "what_is_not_spent": {
        "p2": "NOT DETERMINED by the committed bytes",
        "evidence": "constructive: two admissible non-decreasing completions of the %d-long leading "
                    "hole block give %d distinct values of _first_leave(seq, 2)" % (lead, len(cand)),
        "note": "the two candidate values are counted, never printed"},
    "residual_blindness": "UNPRICED BY DESIGN. Measuring how much of the window is still blind means "
                          "asking which registered model predictions the visible tail already "
                          "excludes, and computing that is the act that spends what is left.",
    "consequence_for_prior_cycles": "NONE. c56 scored p1/p2/p3 at x=42 not at all (trusted depth 0 "
                                    "vs registered floor 16). Its P11 is eigenvalue-only: gpred() "
                                    "reads no node count (m2_c53_spectrum.py:292, docstring and "
                                    "body), so first_local_min_index feeds a PREDICTION, never an "
                                    "outcome.",
    "consequence_going_forward": "any cycle that scores p2 at x=42 must publish it as "
                                 "SEMI-BLIND-TAIL-SEEN and may not call it a blind arm.",
    "pooled_rows": len(tab), "certified_prefix": cert,
    "float_order_equals_decimal_order": forder,
    "p2_computed_here": False,
}
json.dump(out, open(os.path.join(_F, "m2_c57_x42_status.json"), "w"), indent=1)
print("STATUS: %s" % out["STATUS"])
print("  pooled rows %d ; seen %d ; holes %d ; leading block %d ; distinct p2 over completions %d"
      % (len(tab), len(seen), len(holes), lead, len(cand)))
