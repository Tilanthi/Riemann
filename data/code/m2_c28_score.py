"""machine2 CYCLE 28 scorer -- grades c28_cover_*.json against the frozen c28_prereg.json.
Reads the prereg AFTER the runs, exactly as cycles 25/26/27 did.  Prints a table and a verdict
line per hypothesis.  No value is computed here that the runner did not already produce, except
the cross-lineage agreement against m3's independent from-scratch column.
"""
import json, os
from mpmath import mp

mp.dps = 50
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/shared/rh-exchange-repo/Riemann"
P = json.load(open(os.path.join(HERE, "c28_prereg.json")))
V = P["catalogue"]
R = {v: json.load(open(os.path.join(HERE, "c28_cover_%s.json" % v))) for v in V}
C = R["clean"]

TOL_SAME = mp.mpf("1e-19")
TOL_CROSS = mp.mpf("1e-13")
ANCH = ["ANCHOR_U", "ANCHOR_0", "ANCHOR_D", "ANCHOR_B"]


def rel(a, b):
    a = mp.mpf(a); b = mp.mpf(b)
    if a == b:
        return mp.mpf(0)
    return abs(a - b) / abs(b)


rows = {}
for v in V:
    r = {}
    for A in ANCH:
        r[A] = rel(R[v][A], C[A])
    r["bit_identical_all"] = all(R[v][A] == C[A] for A in ANCH)
    r["dD_R2"] = rel(R[v]["D_R2"], C["D_R2"])
    r["dD_R3b"] = rel(R[v]["D_R3b"], C["D_R3b"])
    r["dlam_R3b"] = rel(R[v]["R3b_lam"], C["R3b_lam"])
    r["fires"] = R[v]["R3b_FIRES"]
    r["flip"] = (R[v]["R3b_FIRES"] != C["R3b_FIRES"])
    r["MATERIAL"] = bool(r["dD_R2"] > mp.mpf("1e-6") or r["flip"] or r["dlam_R3b"] > mp.mpf("1e-6"))
    r["caught1"] = bool(r["ANCHOR_0"] > TOL_SAME)
    r["caught2"] = bool(r["caught1"] or r["ANCHOR_D"] > TOL_SAME)
    r["caught3"] = bool(r["caught2"] or r["ANCHOR_B"] > TOL_SAME)
    r["caught3_cross"] = bool(r["ANCHOR_0"] > TOL_CROSS or r["ANCHOR_D"] > TOL_CROSS
                              or r["ANCHOR_B"] > TOL_CROSS)
    rows[v] = r

print("%-7s %10s %10s %10s %10s | %9s %9s %5s %5s | %s" %
      ("variant", "ANCH-U", "ANCH-0", "ANCH-D", "ANCH-B", "dD_R2", "dlamR3b", "FIRE", "MATL",
       "caught by 1/2/3 anchors"))
for v in V:
    r = rows[v]
    print("%-7s %10s %10s %10s %10s | %9s %9s %5s %5s | %s %s %s" %
          (v, mp.nstr(r["ANCHOR_U"], 3), mp.nstr(r["ANCHOR_0"], 3), mp.nstr(r["ANCHOR_D"], 3),
           mp.nstr(r["ANCHOR_B"], 3), mp.nstr(r["dD_R2"], 3), mp.nstr(r["dlam_R3b"], 3),
           "Y" if r["fires"] else "n", "M" if r["MATERIAL"] else "-",
           "Y" if r["caught1"] else ".", "Y" if r["caught2"] else ".",
           "Y" if r["caught3"] else "."))

defects = [v for v in V if v != "clean"]
material = [v for v in defects if rows[v]["MATERIAL"]]
esc2 = [v for v in material if not rows[v]["caught2"]]
esc3 = [v for v in material if not rows[v]["caught3"]]
esc3x = [v for v in material if not rows[v]["caught3_cross"]]
c1_only = [v for v in material if rows[v]["caught1"]]

print("\nMATERIAL defects            : %d/%d  %s" % (len(material), len(defects), material))
print("caught by #117 as worded (1): %d/%d  %s" % (len(c1_only), len(material), c1_only))
print("caught by #117 amended   (2): %d/%d" % (len([v for v in material if rows[v]['caught2']]), len(material)))
print("caught by proposed       (3): %d/%d" % (len([v for v in material if rows[v]['caught3']]), len(material)))
print("ESCAPE at 2 anchors         : %s" % esc2)
print("ESCAPE at 3 anchors         : %s" % esc3)
print("ESCAPE at 3, cross-lineage  : %s" % esc3x)

G = {}
G["H1"] = (len(esc2) > 0, "escape set at two anchors = %s" % esc2)
# v1 of this line parsed the predicted set out of H2's PROSE with split("{")[1] and picked up
# "{ANCHOR-0, ANCHOR-D}" -- the FIRST brace group in the sentence, which names the anchor set the
# escape is measured against, not the predicted escape set.  It printed FALSIFIED for a hypothesis
# that held exactly.  Recorded, not hidden: a SCORER defect, caught by reading the note field.
# Fixed to read the machine-readable field frozen in the same prereg.
pred2 = set(P["prestated_catch_table"]["caught_by_3_anchors_adds"]
            + P["prestated_catch_table"]["escaping_all_three"])
G["H2"] = (set(esc2) == pred2, "predicted %s, observed %s" % (sorted(pred2), sorted(esc2)))
legB = ["bgap", "bdel", "bhalf"]
h3 = (all(rows[v]["ANCHOR_B"] > TOL_SAME for v in legB)
      and all(rows[v]["ANCHOR_B"] <= TOL_SAME for v in ("dref", "sord")))
G["H3"] = (h3, "ANCHOR_B rel on legB = %s ; on dref/sord = %s" %
           ([mp.nstr(rows[v]["ANCHOR_B"], 3) for v in legB],
            [mp.nstr(rows[v]["ANCHOR_B"], 3) for v in ("dref", "sord")]))
G["H4"] = (all(rows[v]["bit_identical_all"] for v in ("dref", "sord")),
           "DEMONSTRATION (empty by algebra, declared before the run): all four anchors "
           "bit-identical for dref and sord = %s" %
           [rows[v]["bit_identical_all"] for v in ("dref", "sord")])
G["H5"] = (rows["bsign"]["bit_identical_all"] and R["bsign"]["D_R2"] == C["D_R2"]
           and R["bsign"]["D_R3b"] == C["D_R3b"],
           "bsign anchors bit-identical = %s, D_R2 identical = %s, D_R3b identical = %s" %
           (rows["bsign"]["bit_identical_all"], R["bsign"]["D_R2"] == C["D_R2"],
            R["bsign"]["D_R3b"] == C["D_R3b"]))
dl = rows["eps14"]["ANCHOR_B"]
dD = rows["eps14"]["dD_R2"]
A = (dD / dl) if dl > 0 else mp.mpf("nan")
G["H6"] = (mp.mpf(50) <= A <= mp.mpf(500),
           "eps14: rel lam_R1 move %s, rel D_R2 move %s, amplification A = %s" %
           (mp.nstr(dl, 4), mp.nstr(dD, 4), mp.nstr(A, 6)))
G["H7"] = (any(rows[v]["flip"] for v in legB),
           "flips among legB = %s" % [v for v in legB if rows[v]["flip"]])
G["H8"] = (R["c1"]["ANCHOR_0"] == C["ANCHOR_0"] and rows["c1"]["ANCHOR_D"] > mp.mpf("1e-3")
           and rows["c2"]["ANCHOR_0"] > mp.mpf("1e2"),
           "CONTROL: c1 ANCHOR_0 bit-identical = %s, c1 ANCHOR_D rel = %s, c2 ANCHOR_0 rel = %s" %
           (R["c1"]["ANCHOR_0"] == C["ANCHOR_0"], mp.nstr(rows["c1"]["ANCHOR_D"], 6),
            mp.nstr(rows["c2"]["ANCHOR_0"], 6)))

print("\n--- graded ---")
for k in sorted(G):
    ok, note = G[k]
    tag = {"H4": "DEMONSTRATION", "H8": "CONTROL"}.get(k, "HELD" if ok else "FALSIFIED")
    if k in ("H4", "H8"):
        tag += " (" + ("as declared" if ok else "DID NOT BEHAVE AS DECLARED") + ")"
    print("%-3s %-28s %s" % (k, tag, note))

# cross-lineage agreement, measured not assumed
m3 = json.load(open(os.path.join(REPO, "data/code/m3_L156_cycle25_S2_result.json")))["results"]
pairs = [("ANCHOR_0", "launch"), ("ANCHOR_D", "R0"), ("ANCHOR_B", "R1"), ("R3b_lam", "R3b")]
print("\n--- cross-lineage agreement m2(clean) vs m3 from-scratch (MEASURED this cycle) ---")
xl = {}
for ours, theirs in pairs:
    d = rel(C[ours], m3[theirs])
    xl[ours] = mp.nstr(d, 4)
    print("%-9s vs m3 %-7s rel %s" % (ours, theirs, mp.nstr(d, 4)))

json.dump({"rows": {v: {k: (mp.nstr(x, 8) if isinstance(x, mp.mpf) else x)
                        for k, x in rows[v].items()} for v in V},
           "material": material, "escape_2anchor": esc2, "escape_3anchor": esc3,
           "escape_3anchor_cross_lineage": esc3x,
           "graded": {k: {"pass": bool(G[k][0]), "note": G[k][1]} for k in G},
           "amplification_A": mp.nstr(A, 8),
           "cross_lineage_rel": xl},
          open(os.path.join(HERE, "c28_score.json"), "w"), indent=1)
