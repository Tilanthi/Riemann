#!/usr/bin/env python3
"""m2_c55_spectrum.py -- cycle 55's instrument for the FOURTH and FIFTH windows:
x = 25 (the extrapolation SEALED UNRUN in c54's prereg) and x = 22 (the window that
DISCRIMINATES models I and X, which x = 25 does not).

WHAT IS NEW HERE, AND WHAT IS NOT
---------------------------------
NOTHING computational is new and nothing is copied.  The matrix builder is c46's
`c46_parity.build_matrix_parity` (unmodified, imported), the node detector is c51's
`m2_c51_nodes` (unmodified, imported), and the stage-A/stage-B routines are **cycle 53's own
`m2_c53_spectrum.spec` and `.nodes`**, imported and called -- not reimplemented.

The ONLY thing this file adds is REDIRECTION: c53's module writes `m2_c53_*` artefacts next to
itself, and cycle 55's artefacts must live in `data/c55` under c55 names.  So this file rebinds
exactly three module attributes of the imported module -- `HERE`, `specname`, `nodename` -- and
prints the rebinding in every artefact it writes.

🔴 WHY THAT NEEDS A GATE.  A rebinding is a two-line change that cannot be seen in any number it
produces, which is the same shape as the c53 defect this cycle exists to remedy (a field that was
arithmetically right and named wrong).  So `repro` re-runs a PUBLISHED c53 cell THROUGH THIS
WRAPPER and compares the result to c53's banked artefact field-for-field.  A dry run on a known
answer is the only thing that tests the test.

usage:
  m2_c55_spectrum.py spec  PARITY X N DPS GL     one stage-A cell -> m2_c55_spec_PARITY_xX_NN_dpsD.json
  m2_c55_spectrum.py nodes PARITY X N DPS R      rungs 1..R      -> m2_c55_nodes_PARITY_xX_NN_dpsD.json
  m2_c55_spectrum.py repro PARITY X N DPS GL R   re-run a c53 cell through this wrapper and diff
  m2_c55_spectrum.py gpred X N DPS               Model G on the pooled eigenvalue ladder (no nodes)
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_dir(name):
    """resolve relative to THIS file (c50 addendum 2 / m1-L191 finding (c)); no absolute clone path.
    c52's law: PRINT THE PATH THE RESOLVER USED, so a portability pass cannot silently read the
    author's own tree."""
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


C53 = _find_dir("c53")
sys.path.insert(0, C53)
import m2_c53_spectrum as S53          # the WHOLE stage-A/stage-B implementation, imported


def specname(par, X, N, DPS):
    return os.path.join(HERE, "m2_c55_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))


def nodename(par, X, N, DPS):
    return os.path.join(HERE, "m2_c55_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))


_ORIG = dict(HERE=S53.HERE, specname=S53.specname, nodename=S53.nodename)


def redirect(to_c55=True):
    """THE ONLY MUTATION THIS FILE PERFORMS.  Printed, reversible, and gated by `repro`."""
    if to_c55:
        S53.HERE, S53.specname, S53.nodename = HERE, specname, nodename
    else:
        S53.HERE, S53.specname, S53.nodename = _ORIG["HERE"], _ORIG["specname"], _ORIG["nodename"]


def report():
    return dict(wrapper=os.path.abspath(__file__), c53_module=os.path.abspath(S53.__file__),
                c53_dir=C53, out_dir=HERE, redirected=(S53.HERE == HERE),
                inner_resolver=S53.resolver_report())


# ------------------------------------------------------------------ the G0-REPRO gate
def repro(par, X, N, DPS, GL, R):
    """Re-run a PUBLISHED c53 cell through this wrapper and diff it against c53's banked artefact.

    Compared field-for-field EXCEPT the fields that are expected to differ and are named here:
    timing (`build_seconds`, `eigsy_seconds`, `seconds`), provenance (`label`, `resolver`,
    `source`) and the output filename.  Everything else -- every eigenvalue string, every
    coefficient, every node count, every delta -- must be IDENTICAL.  Any difference fails.
    """
    IGN = {"build_seconds", "eigsy_seconds", "seconds", "label", "resolver", "source"}
    redirect(True)
    S53.spec(par, X, N, DPS, GL)
    S53.nodes(par, X, N, DPS, R)
    rows, fails, compared = [], 0, 0
    for kind, mine_fn, theirs_fn in (
            ("spec", specname(par, X, N, DPS),
             os.path.join(C53, "m2_c53_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))),
            ("nodes", nodename(par, X, N, DPS),
             os.path.join(C53, "m2_c53_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS)))):
        a, b = json.load(open(mine_fn)), json.load(open(theirs_fn))
        if kind == "nodes":
            b = dict(b, rungs=b["rungs"][:R])
        for k in sorted(set(a) | set(b)):
            if k in IGN:
                continue
            compared += 1
            same = (json.dumps(a.get(k), sort_keys=True) == json.dumps(b.get(k), sort_keys=True))
            fails += 0 if same else 1
            rows.append(dict(kind=kind, field=k, identical=bool(same)))
            if not same:
                print("  DIFF %s.%s" % (kind, k))
    out = dict(cell=dict(parity=par, x=X, N=N, dps=DPS, gl=GL, R=R),
               compared_fields=compared, fails=fails,
               verdict=("PASS" if fails == 0 else "FAIL"), ignored_fields=sorted(IGN),
               rows=rows, report=report(),
               note="the redirection is the ONLY difference between this wrapper and c53's "
                    "registered instrument; this gate is what turns that sentence into a measurement.")
    json.dump(out, open(os.path.join(HERE, "m2_c55_repro_gate.json"), "w"), indent=1)
    print("G0-REPRO: %d/%d fields identical -> %s" % (compared - fails, compared, out["verdict"]))
    return 0 if fails == 0 else 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    redirect(True)
    print("REDIRECTION: %s" % json.dumps(report(), indent=1), flush=True)
    if cmd == "spec":
        par, X, N, DPS, GL = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
        return S53.spec(par, X, N, DPS, GL)
    if cmd == "nodes":
        par, X, N, DPS, R = sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
        return S53.nodes(par, X, N, DPS, R)
    if cmd == "gpred":
        X, N, DPS = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        rc = S53.gpred(X, N, DPS)
        # c53's gpred hardcodes its own BASENAME; the redirection only moves the DIRECTORY.
        # Rename so that no c55 artefact wears a c53 name -- the exact collision class this
        # cycle exists to remedy, one layer down in the filesystem.
        src = os.path.join(HERE, "m2_c53_gpred_x%d_N%d_dps%d.json" % (X, N, DPS))
        dst = os.path.join(HERE, "m2_c55_gpred_x%d_N%d_dps%d.json" % (X, N, DPS))
        if os.path.exists(src):
            os.replace(src, dst)
            print("renamed %s -> %s" % (os.path.basename(src), os.path.basename(dst)))
        return rc
    if cmd == "repro":
        par, X, N, DPS, GL, R = (sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
                                 int(sys.argv[6]), int(sys.argv[7]))
        return repro(par, X, N, DPS, GL, R)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
