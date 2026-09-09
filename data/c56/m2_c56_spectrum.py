#!/usr/bin/env python3
"""m2_c56_spectrum.py -- cycle 56's instrument for the SIXTH window, x = 42.

WHY x = 42, AND WHY IT IS NOT x = 22 OR x = 25
----------------------------------------------
c55 opened c54's sealed x = 25 column, and BEAST-AGI's c55 ruling states the consequence: an
opened seal cannot be re-sealed.  Worse than the ruling knew: c55 also PUBLISHED the untrusted
raw readings at both windows (`p2 = 11`, `p3 = 16`).  So at x = 22 and x = 25 the author has
seen both the predictions AND the outcome-up-to-trust.  Those two windows are RETIRED as
evidential arms.  x = 42 is the FIRST window at which all four live models give four DISTINCT
predictions (I 16, X 13, A 12, S 15) -- chosen by outcome-space search over published zero
counts BEFORE anything was computed, which is the check c55 found nobody had run before sealing.

WHAT IS NEW HERE, AND WHAT IS NOT
---------------------------------
Nothing computational is new and nothing is copied.  Matrix builder = c46's, node detector =
c51's, stage A/B = c53's `spec`/`nodes`, all IMPORTED.  This file rebinds exactly FOUR module
attributes of the imported c53 module: `HERE`, `specname`, `nodename` (redirection, as c55 did)
and `STORE_SF` 40 -> 120 (the instrument repair, the configuration already validated in c55's
storage test: H1' 10302/10302 values identical after rounding, H0 control held, H2 held).

🔴 THE REPAIR IS A KNOB MOVE AND IS GATED AS ONE.  `repro` re-runs a PUBLISHED c53 cell through
this wrapper at the SEALED width 40 and demands the banked artefact back field-for-field: a dry
run on a KNOWN ANSWER is the only thing that tests the test.  `reprosf` then re-runs the same
cell at 120 and demands every value identical AFTER ROUNDING TO 40 s.f. (c55's H1' discipline --
never a raw string comparison, because STORE_SF *is* a print width and comparing printed values
would test the print, which is the c55 defect this file exists not to repeat).

usage:
  m2_c56_spectrum.py spec  PARITY X N DPS GL     stage A  -> m2_c56_spec_PARITY_xX_NN_dpsD.json
  m2_c56_spectrum.py nodes PARITY X N DPS R      stage B  -> m2_c56_nodes_PARITY_xX_NN_dpsD.json
  m2_c56_spectrum.py gpred X N DPS               Model G on the pooled ladder (no nodes)
  m2_c56_spectrum.py repro                       KAT: published c53 cell at SF=40, must match
  m2_c56_spectrum.py reprosf                     KAT: same cell at SF=120, equal after rounding
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_SF_REPAIRED = 120
STORE_SF_SEALED = 40


def _find_dir(name):
    """resolve relative to THIS file; no absolute clone path.  c52's law: PRINT THE PATH THE
    RESOLVER USED, so a portability pass cannot silently read the author's own tree."""
    for cand in (os.path.join(HERE, "data", name), os.path.join(HERE, "..", name)):
        if os.path.isdir(cand):
            return os.path.abspath(cand)
    raise SystemExit("cannot locate %s from %s" % (name, HERE))


C53 = _find_dir("c53")
sys.path.insert(0, C53)
import m2_c53_spectrum as S53          # the WHOLE stage-A/stage-B implementation, imported

_ORIG = dict(HERE=S53.HERE, specname=S53.specname, nodename=S53.nodename, STORE_SF=S53.STORE_SF)


def specname(par, X, N, DPS):
    return os.path.join(HERE, "m2_c56_spec_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))


def nodename(par, X, N, DPS):
    return os.path.join(HERE, "m2_c56_nodes_%s_x%d_N%d_dps%d.json" % (par, X, N, DPS))


def redirect(sf=STORE_SF_REPAIRED, names=True):
    """THE ONLY MUTATIONS THIS FILE PERFORMS.  Printed, reversible, and gated by `repro`."""
    if names:
        S53.HERE, S53.specname, S53.nodename = HERE, specname, nodename
    S53.STORE_SF = sf
    print("REBINDING: out_dir -> %s ; STORE_SF %d -> %d" % (HERE, _ORIG["STORE_SF"], sf), flush=True)


def report(sf):
    return dict(wrapper=os.path.abspath(__file__), c53_module=os.path.abspath(S53.__file__),
                c53_dir=C53, out_dir=HERE, redirected=(S53.HERE == HERE),
                store_sf_sealed=_ORIG["STORE_SF"], store_sf_used=sf,
                inner_resolver=S53.resolver_report())


# ------------------------------------------------------------------ the KAT gate (known answer)
KAT_CELL = dict(par="even", X=13, N=100, DPS=150, GL=9, R=5)
SKIP = {"build_seconds", "eigsy_seconds", "seconds", "label", "resolver", "reference",
        "selftest_depths_sf", "selftest_ceiling_sf", "source", "detector"}


def _round_sf(s, sf):
    """round a decimal string to `sf` significant figures, via mpmath, NEVER by string slicing."""
    from mpmath import mp, mpf
    old = mp.dps
    try:
        mp.dps = max(sf + 25, 60)
        return mp.nstr(mpf(s), sf, strip_zeros=True)
    finally:
        mp.dps = old


def _diff(a, b, sf=None, path="", out=None):
    out = [] if out is None else out
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k in SKIP:
                continue
            _diff(a.get(k), b.get(k), sf, path + "/" + k, out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append((path, "len %s" % len(a), "len %s" % len(b)))
        else:
            for i, (u, v) in enumerate(zip(a, b)):
                _diff(u, v, sf, path + "[%d]" % i, out)
    else:
        u, v = a, b
        if sf is not None and isinstance(a, str) and isinstance(b, str) and a and b:
            try:
                u, v = _round_sf(a, sf), _round_sf(b, sf)
            except Exception:
                pass
        if u != v:
            out.append((path, a, b))
    return out


def _kat(sf, tag):
    c = KAT_CELL
    banked = os.path.join(C53, "m2_c53_spec_%s_x%d_N%d_dps%d.json" % (c["par"], c["X"], c["N"], c["DPS"]))
    if not os.path.exists(banked):
        raise SystemExit("KAT: no banked c53 cell at %s" % banked)
    tmp = os.path.join(HERE, "m2_c56_kat_%s_spec.json" % tag)
    S53.HERE = HERE
    S53.specname = lambda *a, **k: tmp
    S53.nodename = lambda *a, **k: os.path.join(HERE, "m2_c56_kat_%s_nodes.json" % tag)
    S53.STORE_SF = sf
    print("KAT %s: re-running published c53 cell %s x=%d N=%d dps=%d gl=%d at STORE_SF=%d"
          % (tag, c["par"], c["X"], c["N"], c["DPS"], c["GL"], sf), flush=True)
    S53.spec(c["par"], c["X"], c["N"], c["DPS"], c["GL"])
    a, b = json.load(open(banked)), json.load(open(tmp))
    cmp_sf = None if sf == STORE_SF_SEALED else STORE_SF_SEALED
    diffs = _diff(a, b, cmp_sf)
    # MUTATION CONTROL: a planted change must make this gate FAIL, or the gate measures nothing.
    mut = json.loads(json.dumps(b))
    mut["rungs"][2]["coef"][7] = _round_sf(mut["rungs"][2]["coef"][7], 6) + "1"
    mdiffs = _diff(a, mut, cmp_sf)
    res = dict(tag=tag, store_sf=sf, compare_after_rounding_to_sf=cmp_sf,
               banked=os.path.relpath(banked, HERE), rerun=os.path.basename(tmp),
               fields_skipped=sorted(SKIP), n_diffs=len(diffs), diffs=diffs[:20],
               n_values_compared=sum(len(r["coef"]) + 4 for r in a["rungs"]),
               mutation_control_diffs=len(mdiffs),
               mutation_control=("FIRES" if len(mdiffs) > len(diffs) else "DEAD -- GATE MEANS NOTHING"),
               verdict=("PASS" if not diffs and len(mdiffs) > 0 else "FAIL"))
    json.dump(res, open(os.path.join(HERE, "m2_c56_kat_%s.json" % tag), "w"), indent=1)
    print("KAT %s: %d diffs over %d values (skipped %s); mutation control %s -> %s"
          % (tag, len(diffs), res["n_values_compared"], sorted(SKIP), res["mutation_control"],
             res["verdict"]), flush=True)
    for d in diffs[:10]:
        print("   DIFF %s: %r != %r" % d)
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    c = sys.argv[1]
    if c == "repro":
        sys.exit(_kat(STORE_SF_SEALED, "sf40"))
    elif c == "reprosf":
        sys.exit(_kat(STORE_SF_REPAIRED, "sf120"))
    redirect()
    if c == "spec":
        sys.exit(S53.spec(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])))
    elif c == "nodes":
        sys.exit(S53.nodes(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])))
    elif c == "gpred":
        sys.exit(S53.gpred(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])))
    else:
        raise SystemExit(__doc__)
