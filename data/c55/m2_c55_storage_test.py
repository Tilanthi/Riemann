#!/usr/bin/env python3
"""m2_c55_storage_test.py -- the DISCRIMINATING TEST of why the node detector failed at x = 22 and
x = 25: is it the STORED COEFFICIENT WIDTH, or the computation?

THE HYPOTHESIS, registered in m2_c55_prereg_addendum_1.md and PUSHED BEFORE THIS FILE RAN.
c53's sealed instrument stores eigenvector coefficients at `STORE_SF = 40` significant figures
("c51's published coefficient width").  The node detector reads THOSE stored coefficients.  Fourteen
of this cycle's fifteen unstable rungs have `lobe_min_ratio` between 2.8e-43 and 5.6e-41 -- i.e. a
smallest lobe BELOW the stored resolution -- so the sign of that lobe is not in the artefact at all
and the detector, correctly, refuses to answer.  Every stable rung ever measured (367 of them, five
windows) sits at lobe ratio >= 3.4e-3.

WHAT THIS FILE CHANGES, AND ONLY THIS.  It imports c53's sealed module and rebinds ONE attribute,
`STORE_SF`, from 40 to 120.  The matrix, the eigensolver, dps, gl, the detector and every other line
are the sealed ones, imported and unmodified.  The rebinding is printed into the artefact.

GATE (H1): the eigenvalue strings must come back BIT-IDENTICAL to the sealed 40-s.f. run for all
101 rungs.  If they do not, the rebinding changed the computation and the test is void -- that is the
whole reason H1 is registered as a gate and not as a hope.

usage:  m2_c55_storage_test.py spec     one cell at STORE_SF=120  (even, x=22, N=100, dps 300, gl 9)
        m2_c55_storage_test.py nodes    rungs 1..3 of that cell
        m2_c55_storage_test.py score    H1..H3 scored against the sealed 40-s.f. artefacts
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_dir(name):
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


C53 = _find_dir("c53")
sys.path.insert(0, C53)
import m2_c53_spectrum as S53

PAR, X, N, DPS, GL, R = "even", 22, 100, 300, 9, 3
SF = 120


def specname(par, x, n, dps):
    return os.path.join(HERE, "m2_c55_hp_spec_%s_x%d_N%d_dps%d_sf%d.json" % (par, x, n, dps, SF))


def nodename(par, x, n, dps):
    return os.path.join(HERE, "m2_c55_hp_nodes_%s_x%d_N%d_dps%d_sf%d.json" % (par, x, n, dps, SF))


def redirect():
    S53.HERE, S53.specname, S53.nodename = HERE, specname, nodename
    S53.STORE_SF = SF
    print("REBINDING: HERE/specname/nodename -> data/c55 hp names ; STORE_SF 40 -> %d" % SF,
          flush=True)


def score():
    sealed_spec = os.path.join(HERE, "m2_c55_spec_%s_x%d_N%d_dps%d.json" % (PAR, X, N, DPS))
    sealed_nodes = os.path.join(HERE, "m2_c55_nodes_%s_x%d_N%d_dps%d.json" % (PAR, X, N, DPS))
    a, b = json.load(open(sealed_spec)), json.load(open(specname(PAR, X, N, DPS)))
    lam_a = [r["lam"] for r in a["rungs"]]
    lam_b = [r["lam"] for r in b["rungs"]]
    h1 = dict(compared=len(lam_a), identical=sum(1 for u, v in zip(lam_a, lam_b) if u == v),
              all_identical=bool(lam_a == lam_b),
              coef_sf_sealed=len(a["rungs"][0]["coef"][0].split("e")[0].replace("-", "")
                                 .replace(".", "")),
              coef_sf_hp=len(b["rungs"][0]["coef"][0].split("e")[0].replace("-", "")
                             .replace(".", "")))
    na, nb = json.load(open(sealed_nodes)), json.load(open(nodename(PAR, X, N, DPS)))
    rows = []
    for r_new in nb["rungs"]:
        r_old = next(r for r in na["rungs"] if r["rung"] == r_new["rung"])
        rows.append(dict(rung=r_new["rung"],
                         nu_at_sf40=r_old["nu"], stable_at_sf40=r_old.get("stable"),
                         nu_at_sf120=r_new["nu"], stable_at_sf120=r_new.get("stable"),
                         lobe_min_ratio=r_old.get("lobe_min_ratio"),
                         counts_sf40=r_old.get("counts"), counts_sf120=r_new.get("counts"),
                         zero_tol_count_sf40=(r_old.get("counts") or {}).get("12001_0.0"),
                         refine_sf40=r_old.get("nu_refine_48001")))
    unstable40 = [r for r in rows if r["nu_at_sf40"] is None]
    h2 = dict(unstable_at_sf40=[r["rung"] for r in unstable40],
              now_stable=[r["rung"] for r in unstable40 if r["nu_at_sf120"] is not None],
              still_unstable=[r["rung"] for r in unstable40 if r["nu_at_sf120"] is None],
              verdict=("HELD" if unstable40 and all(r["nu_at_sf120"] is not None for r in unstable40)
                       else ("REFUTED" if unstable40 else "VACUOUS -- no unstable rung in range")))
    h3 = dict(rows=[dict(rung=r["rung"], predicted=r["zero_tol_count_sf40"], measured=r["nu_at_sf120"],
                         agree=bool(r["zero_tol_count_sf40"] == r["nu_at_sf120"]))
                    for r in unstable40],
              verdict=("HELD" if unstable40 and all(r["zero_tol_count_sf40"] == r["nu_at_sf120"]
                                                    for r in unstable40)
                       else ("REFUTED" if unstable40 else "VACUOUS")))
    stable_before = [r for r in rows if r["nu_at_sf40"] is not None]
    h0 = dict(rows=[dict(rung=r["rung"], sf40=r["nu_at_sf40"], sf120=r["nu_at_sf120"],
                         agree=bool(r["nu_at_sf40"] == r["nu_at_sf120"])) for r in stable_before],
              verdict=("HELD" if all(r["nu_at_sf40"] == r["nu_at_sf120"] for r in stable_before)
                       else "REFUTED"),
              why="CONTROL: a rung that was already stable must not move. If widening storage moved "
                  "a settled count, the storage width was load-bearing where we thought it was not "
                  "and every published node count would be in question.")
    out = dict(cell=dict(parity=PAR, x=X, N=N, dps=DPS, gl=GL, R=R, store_sf=SF),
               H1_eigenvalues_bit_identical=dict(**h1, verdict=("HELD" if h1["all_identical"]
                                                                else "REFUTED")),
               H2_unstable_rungs_become_stable=h2,
               H3_stabilised_counts_equal_the_zero_tolerance_counts=h3,
               H0_control_already_stable_rungs_unmoved=h0,
               rows=rows,
               verdict=("PASS" if (h1["all_identical"] and h2["verdict"] == "HELD"
                                   and h3["verdict"] == "HELD" and h0["verdict"] == "HELD")
                        else "MIXED -- read the individual hypotheses"))
    json.dump(out, open(os.path.join(HERE, "m2_c55_storage_test.json"), "w"), indent=1)
    print("H1 eigenvalues bit-identical: %d/%d -> %s"
          % (h1["identical"], h1["compared"], out["H1_eigenvalues_bit_identical"]["verdict"]))
    print("H0 control (already-stable rungs unmoved): %s" % h0["verdict"])
    print("H2 unstable %s -> now stable %s, still unstable %s : %s"
          % (h2["unstable_at_sf40"], h2["now_stable"], h2["still_unstable"], h2["verdict"]))
    print("H3 stabilised counts equal zero-tolerance counts: %s  %s"
          % (h3["verdict"], [(r["rung"], r["predicted"], r["measured"]) for r in h3["rows"]]))
    print("STORAGE TEST: %s" % out["verdict"])
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "spec":
        redirect()
        return S53.spec(PAR, X, N, DPS, GL)
    if cmd == "nodes":
        redirect()
        return S53.nodes(PAR, X, N, DPS, R)
    if cmd == "score":
        return score()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
