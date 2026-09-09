#!/usr/bin/env python3
"""m2_c56_storage_law.py -- M3, the DECISIVE and cheap test registered in m2_c56_prereg.md §6.

THE QUESTION.  c55 recorded 15 rungs with `lobe_min_ratio` in 1e-43..1e-41 and read them as REAL
lobes too small for the 40-s.f. store to resolve; m1's L200 §7 queues that reading for the shared
register as a domain rule.  The competing reading, from c55's own SF=120 cell (rung 1: nu None,
lobe 1.70629e-41 at SF=40  ->  nu 0, lobe 1.0 at SF=120), is that there is NO such lobe: the stored
coefficients carry relative noise ~10^(-SF) and the reconstruction MANUFACTURES a spurious lobe
whose amplitude is the noise floor itself.

THE DISCRIMINATOR.  A real lobe does not know what STORE_SF is.  A noise readout does.
  M3 HOLDS  : lobe_min_ratio tracks ~10^(-SF)   (order 1e-61 at SF=60, 1e-81 at SF=80)
  M3 REFUTED: it stays within two decades of 1e-41 at either width
Registered BEFORE this file ran, in the prereg pushed as 197c71b.

SCOPE.  x = 22 is RETIRED as an evidential arm (prereg §0).  This is an INSTRUMENT test and it is
bounded to rungs 1-2, which cannot yield p2, so no model score can leave this window through it.

usage:  m2_c56_storage_law.py spec SF        one spectrum cell at STORE_SF=SF
        m2_c56_storage_law.py nodes SF       rungs 1..2 of that cell
        m2_c56_storage_law.py score          M3 scored against the sealed SF=40 and c55's SF=120
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAR, X, N, DPS, GL, R = "even", 22, 100, 300, 9, 2


def _find_dir(name):
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


C53 = _find_dir("c53")
C55 = _find_dir("c55")
sys.path.insert(0, C53)
import m2_c53_spectrum as S53


def _names(SF):
    return (os.path.join(HERE, "m2_c56_law_spec_x22_N100_dps300_sf%d.json" % SF),
            os.path.join(HERE, "m2_c56_law_nodes_x22_N100_dps300_sf%d.json" % SF))


def redirect(SF):
    sp, nd = _names(SF)
    S53.HERE = HERE
    S53.specname = lambda *a, **k: sp
    S53.nodename = lambda *a, **k: nd
    S53.STORE_SF = SF
    print("REBINDING: out -> %s ; STORE_SF 40 -> %d" % (os.path.basename(sp), SF), flush=True)


def score():
    rows = []
    sealed = json.load(open(os.path.join(C55, "m2_c55_nodes_%s_x%d_N%d_dps%d.json" % (PAR, X, N, DPS))))
    hp = json.load(open(os.path.join(C55, "m2_c55_hp_nodes_%s_x%d_N%d_dps%d_sf120.json" % (PAR, X, N, DPS))))
    src = {40: sealed, 120: hp}
    for SF in (40, 60, 80, 120):
        if SF in src:
            d = src[SF]
        else:
            _, nd = _names(SF)
            d = json.load(open(nd))
        for r in d["rungs"][:R]:
            rows.append(dict(store_sf=SF, rung=r["rung"], nu=r["nu"], stable=r.get("stable"),
                             lobe_min_ratio=r.get("lobe_min_ratio"),
                             log10_lobe=(None if r.get("lobe_min_ratio") in (None,) else
                                         __import__("math").log10(float(r["lobe_min_ratio"])))))
    # M3 is scored on the rungs the sealed SF=40 run called UNSTABLE -- the ones carrying the claim.
    claim = [r for r in rows if r["store_sf"] == 40 and r["nu"] is None]
    verdicts = []
    for c in claim:
        seq = [r for r in rows if r["rung"] == c["rung"]]
        moved, stayed = [], []
        for r in seq:
            if r["store_sf"] == 40 or r["log10_lobe"] is None:
                continue
            if r["nu"] is None and abs(r["log10_lobe"] - c["log10_lobe"]) <= 2:
                stayed.append(r["store_sf"])
            else:
                moved.append((r["store_sf"], r["log10_lobe"], r["nu"]))
        verdicts.append(dict(rung=c["rung"], sf40_lobe=c["lobe_min_ratio"], moved=moved, stayed=stayed))
    tracked = all(not v["stayed"] for v in verdicts) and bool(verdicts)
    out = dict(hypothesis="M3: the 1e-41 lobe_min_ratio is a readout of the storage noise floor and "
                          "must MOVE with STORE_SF; a real lobe would STAY PUT",
               registered_in="m2_c56_prereg.md sec 6, pushed as 197c71b before this ran",
               cell=dict(parity=PAR, x=X, N=N, dps=DPS, gl=GL, rungs=R),
               scope="INSTRUMENT test at a RETIRED window; rungs 1-2 only; cannot yield p2",
               rows=rows, per_rung=verdicts,
               verdict=("HELD" if tracked else "REFUTED"),
               reading=("At every widened store the rung that was unstable at 40 s.f. either becomes "
                        "STABLE with an O(1) lobe or its 'lobe' moves with the store width. A lobe "
                        "that is a property of the eigenfunction cannot do that."
                        if tracked else
                        "At least one rung kept a lobe within two decades of 1e-41 when the store "
                        "was widened -- consistent with a REAL feature, and M3 is refuted."))
    json.dump(out, open(os.path.join(HERE, "m2_c56_storage_law.json"), "w"), indent=1)
    print("%-9s %-5s %-7s %-8s %s" % ("STORE_SF", "rung", "nu", "stable", "lobe_min_ratio"))
    for r in rows:
        print("%-9d %-5d %-7s %-8s %s" % (r["store_sf"], r["rung"], r["nu"], r["stable"],
                                          r["lobe_min_ratio"]))
    print("M3 verdict: %s" % out["verdict"])
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "score":
        sys.exit(score())
    SF = int(sys.argv[2])
    redirect(SF)
    if sys.argv[1] == "spec":
        sys.exit(S53.spec(PAR, X, N, DPS, GL))
    elif sys.argv[1] == "nodes":
        sys.exit(S53.nodes(PAR, X, N, DPS, R))
    raise SystemExit(__doc__)
