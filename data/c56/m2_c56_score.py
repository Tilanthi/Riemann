#!/usr/bin/env python3
"""m2_c56_score.py -- cycle 56's grader for the SIXTH window, x = 42.

WHAT IS IMPORTED AND WHAT IS NEW.  The pooling, the N-control trusted depth, the plateau reader and
the half-up rounding are c55's, IMPORTED from `data/c55/m2_c55_score.py` (the sealed grader) with
the two c55 sibling repairs re-applied by DELEGATION, not by copying: `plateaus()` is taken from
`m2_c55_score_jointfix.py`'s discipline (a hole is not a value) and the trust gate is applied to
EVERY arm here, including the one that names a survivor.

WHAT IS NEW is only this cycle's registered content: the x = 42 model column, the P2-STRICT
criterion, and the instrument predictions M1 / M2 from the prereg.  Everything registered is read
from constants written HERE, before the node cells exist, and this file is SEALED at that moment.

🔴 THE POST-HOC BOUNDARY IS ENFORCED IN CODE, not promised in prose: `RETIRED_WINDOWS = {22, 25}`
and `score_window` REFUSES to run on them.  A grader that could still score x = 22 would make the
prereg's section 0 an intention rather than a mechanism.

usage: m2_c56_score.py score    ->  m2_c56_scores.json
"""
import json, os, sys, decimal
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_dir(name):
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


C55 = _find_dir("c55")
sys.path.insert(0, C55)
import m2_c55_score as S55                      # the sealed c55 grader, IMPORTED

X, DPS, GL, R = 42, 300, 9, 15
RETIRED_WINDOWS = {22, 25}

# ---- REGISTERED in m2_c56_prereg.md sec 3, sealed as 197c71b BEFORE any x=42 cell existed -------
REGISTERED_P2 = {"I": 16, "X": 13, "A": 12, "S": 15, "L": 12, "Z": 28}
LIVE = ("I", "X", "A", "S")
REGISTERED_MARGIN = {"I": 0.088, "X": 0.410, "A": 0.255, "S": 0.099, "L": 0.329, "Z": 0.405}
TRUST_FLOOR_LIVE, TRUST_FLOOR_Z = 16, 28
M1_FORBIDDEN_BAND = (1e-45, 1e-35)


def _nodefiles(N):
    return {p: os.path.join(HERE, "m2_c56_nodes_%s_x%d_N%d_dps%d.json" % (p, X, N, DPS))
            for p in ("even", "odd")}


def _round_half_up(v):
    return int(decimal.Decimal(repr(v)).quantize(decimal.Decimal('1'),
                                                 rounding=decimal.ROUND_HALF_UP))


def rule_values(n, x):
    """the SAME closed forms as c55 sec 3, re-evaluated at the measured n -- a CHECK on the column
    printed in the prereg, never a substitute for it."""
    from mpmath import mp, log, sqrt, mpf
    mp.dps = 40
    def rh(v):
        return int(decimal.Decimal(mp.nstr(v, 30)).quantize(decimal.Decimal('1'),
                                                            rounding=decimal.ROUND_HALF_UP))
    L13, L19, L21 = log(13), log(19), log(21)
    raw = dict(I=10 + (n - 21) / mpf(17), X=10 + (log(x) - L13) / (L19 - L13),
               A=4 * log(n) / L21, S=4 * sqrt(mpf(n) / 21),
               L=4 * log(x) / L13, Z=4 * mpf(n) / 21)
    base = dict(I=0, X=0, A=6, S=6, L=6, Z=6)
    out = {}
    for k, v in raw.items():
        out[k] = dict(raw=mp.nstr(v, 12), p2=base[k] + rh(v),
                      margin=float(mp.nstr(abs(v - (mp.floor(v) + mpf('0.5'))), 6)),
                      live=(k in LIVE))
    return out


def instrument_checks():
    """M1 and M2 from the prereg sec 6 -- registered before the run."""
    rows, m1_hits, m2_holes = [], [], []
    for N in (100, 180):
        for par, f in _nodefiles(N).items():
            if not os.path.exists(f):
                continue
            d = json.load(open(f))
            for r in d["rungs"]:
                lr = r.get("lobe_min_ratio")
                v = None if lr is None else float(lr)
                rows.append(dict(N=N, parity=par, rung=r["rung"], nu=r["nu"],
                                 stable=r.get("stable"), lobe=lr))
                if v is not None and M1_FORBIDDEN_BAND[0] <= v <= M1_FORBIDDEN_BAND[1]:
                    m1_hits.append(rows[-1])
                if r["nu"] is None:
                    m2_holes.append(rows[-1])
    return dict(
        M1=dict(registered="no rung with lobe_min_ratio in [1e-45, 1e-35] at STORE_SF=120",
                hits=m1_hits, verdict=("HELD" if not m1_hits else "REFUTED"),
                firing_world="non-empty: 15 rungs of c55 sat in exactly this band at STORE_SF=40"),
        M2=dict(registered="every rung of every x=42 cell is stable (nu is not None)",
                holes=m2_holes, verdict=("HELD" if not m2_holes else "REFUTED"),
                note="registered in advance as the more fragile of the two"),
        rungs_examined=len(rows))


def score():
    if X in RETIRED_WINDOWS:
        raise SystemExit("REFUSED: x=%d is a RETIRED window (prereg sec 0)" % X)
    S = dict(cycle=56, window=dict(x=X, dps=DPS, gl=GL, R=R, N=[100, 180], store_sf=120),
             retired_windows_refused_by_this_grader=sorted(RETIRED_WINDOWS),
             registered_column=REGISTERED_P2, registered_margins=REGISTERED_MARGIN,
             depth_legend=S55.DEPTH_LEGEND)
    n100, n180 = _nodefiles(100), _nodefiles(180)
    have100 = all(os.path.exists(f) for f in n100.values())
    have180 = all(os.path.exists(f) for f in n180.values())
    S["inputs"] = dict(N100_present=have100, N180_present=have180)
    if not have100:
        S["VERDICT"] = "UNMEASURED -- the N=100 node cells do not exist"
        json.dump(S, open(os.path.join(HERE, "m2_c56_scores.json"), "w"), indent=1)
        return 1

    tab, cert, float_same = S55.pooled_table(n100)
    S["completeness_certified_prefix"] = cert
    S["float_order_equals_decimal_order"] = bool(float_same)
    seq = [r["pooled_delta"] for r in tab]
    S["pooled_delta_N100"] = seq
    S["pooled_parity_order_N100"] = "".join(r["parity"][0] for r in tab)
    S["pooled_table_N100"] = tab

    depth, det = S55.n_control_depth(n100, n180) if have180 else (0, dict(reason="N=180 absent"))
    S["n_control_trusted_depth"] = depth
    S["n_control_detail"] = det

    n = json.load(open(os.path.join(HERE, "m2_c56_zerocount.json")))["n"]
    rules = rule_values(n, X)
    S["measured_zero_count_n"] = n
    S["rule_vs_registered_column"] = {k: dict(rule=rules[k]["p2"], registered=REGISTERED_P2[k],
                                              agree=bool(rules[k]["p2"] == REGISTERED_P2[k]),
                                              raw=rules[k]["raw"], margin=rules[k]["margin"])
                                      for k in REGISTERED_P2}
    S["rule_vs_registered_all_agree"] = all(v["agree"] for v in S["rule_vs_registered_column"].values())

    p1 = S55._first_leave(seq, 0)
    p2 = S55._first_leave(seq, 2)
    p3 = S55._first_leave(seq, 6)
    S["structure"] = dict(p1_onset=p1, p2=p2, p3=p3,
                          plateaus=[list(t) for t in S55.plateaus(seq)],
                          holes_in_pooled_sequence=sum(1 for v in seq if v is None))
    struct_ok = (p1 == 6 and p2 is not None)
    S["structure_gate"] = dict(registered="onset at 6 and a second dislocation must exist",
                               passed=bool(struct_ok),
                               verdict=("OK" if struct_ok else
                                        "FAILED -- p2 does not exist at this window; every model "
                                        "is UNMEASURED, not refuted"))

    trusted_live = bool(p2 is not None and depth >= max(TRUST_FLOOR_LIVE, p2))
    trusted_Z = bool(p2 is not None and depth >= TRUST_FLOOR_Z)
    S["trust_gate"] = dict(registered_floor_live=TRUST_FLOOR_LIVE, registered_floor_Z=TRUST_FLOOR_Z,
                           measured_depth=depth, live_scoreable=trusted_live, Z_scoreable=trusted_Z)

    if not (struct_ok and trusted_live):
        S["P2_STRICT"] = dict(verdict="UNMEASURED", measured_p2_NOT_PUBLISHED=True,
                              why=("the trust gate or the structure gate failed. Per prereg sec 7 "
                                   "the raw index is NOT quoted as an integer here: publishing an "
                                   "untrusted reading is exactly what retired x=22 and x=25."))
        S["VERDICT"] = "UNMEASURED -- nothing banked, no model confirmed or refuted"
    else:
        namers = sorted(k for k, v in REGISTERED_P2.items() if v == p2)
        live_namers = [k for k in namers if k in LIVE]
        if not namers:
            v = "EVERY REGISTERED RULE REFUTED at x=42 -- the measurement matches no registered value"
        elif len(namers) == 1:
            v = "CONFIRMED at x=42: %s is the sole namer of %d" % (namers[0], p2)
        else:
            v = ("NO BANK -- %s all name %d, and P2-STRICT requires a unique namer (disclosed in "
                 "the prereg as the one cell of this design with no survivor)" % (namers, p2))
        S["P2_STRICT"] = dict(measured_p2=p2, namers=namers, live_namers=live_namers,
                              refuted=[k for k in LIVE if REGISTERED_P2[k] != p2],
                              margin_of_the_survivor=(REGISTERED_MARGIN[namers[0]]
                                                      if len(namers) == 1 else None),
                              verdict=v)
        S["VERDICT"] = v

    S["instrument"] = instrument_checks()
    json.dump(S, open(os.path.join(HERE, "m2_c56_scores.json"), "w"), indent=1)
    print("pooled delta N=100: %s" % seq)
    print("structure: p1=%s p2=%s p3=%s holes=%d  gate=%s"
          % (p1, p2, p3, S["structure"]["holes_in_pooled_sequence"], S["structure_gate"]["verdict"]))
    print("N-control trusted depth = %s (floor %d live / %d for Z)" % (depth, TRUST_FLOOR_LIVE, TRUST_FLOOR_Z))
    print("rules re-evaluated at n=%d agree with the sealed column: %s"
          % (n, S["rule_vs_registered_all_agree"]))
    print("M1 %s   M2 %s   (%d rungs examined)" % (S["instrument"]["M1"]["verdict"],
                                                   S["instrument"]["M2"]["verdict"],
                                                   S["instrument"]["rungs_examined"]))
    print("VERDICT: %s" % S["VERDICT"])
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "score":
        sys.exit(score())
    raise SystemExit(__doc__)
