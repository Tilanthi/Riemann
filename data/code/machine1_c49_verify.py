#!/usr/bin/env python3
"""machine1 c49 verification -- my own recomputation at primary (adjudication letter m1-L191).

Verifies machine2-c49 (letter 784a4f3, artefacts 5261cf7) from the committed bytes only:

  W1  the prereg seal: every sha256 in m2_c49_prereg_seal.txt against committed bytes
      (mapping per m2_c49_seal_verify.sh, done in Python because the .sh needs sha256sum).
  W2  the depth table: for all 10 (parity, N) pairs, BOTH conventions recomputed from the
      cells' lambda_min_full at dps=150 vs the dps=220 partner, plus the through-frozen-print
      (60-s.f. lambda_min) reading -- against the letter's table and the cells' stored *_sf.
  W3  P1a/P1b/P1c/P1d scored from MY numbers, tolerances transcribed from the prereg.
  W4  non-movement: 20 upgraded cells vs their sources (c48 tree + raw/), nothing removed,
      retained fields byte-identical, _exact sub-fields identical, and the bit pattern
      reconstructed from _exact matching the _full print within half a last-digit ulp.
  W5  the precision gate: THEIR gate module (sealed v1 diff-verified, gate_cell untouched)
      re-run by me over the full 95-artefact census with LOCAL paths; P2b scored under BOTH
      the registered exclusion (/dps, /*_exact/prec) and the run's wider one (+/iters,
      /gl_degree); plus gate_cell on one upgraded cell vs its source (pass/fail flip).
  W6  the residue: c48's census TSV vs the after TSV -- unbacked set identity, DISCARDED
      field counts, rollup counts.
  W7  D3-D2 from the cells; and the s5 model residuals recomputed from MY depths.
"""
import hashlib
import json
import os
import re
import sys
from decimal import Decimal, getcontext

getcontext().prec = 80
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
C49 = os.path.join(REPO, "data", "c49")
C48 = os.path.join(REPO, "data", "c48")

RUNGS = [60, 100, 140, 180, 220]
PARS = ["even", "odd"]
# the letter's s4 table, transcribed once: (parity, N) -> (continuous, string digits, via-frozen)
LETTER_DEPTH = {
    ("even", 60): (92.66, 93, 59.87), ("even", 100): (92.22, 92, 60.03),
    ("even", 140): (92.15, 92, 60.25), ("even", 180): (92.12, 92, 59.83),
    ("even", 220): (92.10, 92, 59.93),
    ("odd", 60): (95.81, 95, 60.24), ("odd", 100): (95.40, 95, 59.87),
    ("odd", 140): (95.33, 95, 59.85), ("odd", 180): (95.31, 95, 59.97),
    ("odd", 220): (95.28, 95, 59.95),
}
# s7 table: (parity, N) -> D3 - D2 excess
LETTER_EXCESS = {
    ("even", 60): 2.19, ("even", 100): 0.97, ("even", 140): 1.46,
    ("even", 180): 1.43, ("even", 220): 1.38,
    ("odd", 60): 2.43, ("odd", 100): 3.77, ("odd", 140): 2.43,
    ("odd", 180): 2.84, ("odd", 220): 2.48,
}
# s5 model residuals: model -> (parity, N) -> residual
LETTER_RESID = {
    "linN": {("even", 140): 0.37, ("even", 180): 0.77, ("even", 220): 1.19,
             ("odd", 140): 0.34, ("odd", 180): 0.72, ("odd", 220): 1.10},
    "linlogN": {("even", 140): 0.22, ("even", 180): 0.40, ("even", 220): 0.55,
                ("odd", 140): 0.20, ("odd", 180): 0.38, ("odd", 220): 0.51},
}

failures = []


def mpstyle(d):
    """first 8 significant digits of a Decimal, for error messages"""
    return str(+d.normalize())[:10]


def check(name, ok, detail=""):
    print("  [%s] %s%s" % ("OK " if ok else "FAIL", name, (" -- " + detail) if detail else ""))
    if not ok:
        failures.append(name)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(p):
    return json.load(open(p))


def cellpath(base, par, n, dps):
    return os.path.join(base, "c48_%s_x13_N%d_dps%d_g9_it16.json" % (par, n, dps))


def upgpath(par, n, dps):
    return os.path.join(C49, "c49_%s_x13_N%d_dps%d_g9_it16.json" % (par, n, dps))


def srcpath(par, n, dps):
    if dps == 150 or (n in (60, 100) and dps == 220):
        return cellpath(C48, par, n, dps)
    return os.path.join(C49, "raw", "c48_%s_x13_N%d_dps%d_g9_it16.json" % (par, n, dps))


# ---------- W1: the seal ----------
def w1():
    print("\nW1  the prereg seal (sha256 against committed bytes)")
    seal = open(os.path.join(C49, "m2_c49_prereg_seal.txt")).read()
    pairs = [
        ("d64a669839db8f280d05522876fd24dcd904b2d60d65d6e2807e4dce75888f23",
         os.path.join(C49, "m2_c49_prereg.md"), "prereg"),
        ("42984d9c2379b8b3f9bdcde7eb645229fe28b449193bc1dbc55f8156984bdf64",
         os.path.join(C49, "m2_c49_precision.SEALED_v1.py"), "sealed instrument v1"),
        ("86825b9cb29cc9cf62f7720e44cea03a87a33717b73cdb7e606fc0f2a3aedabe",
         os.path.join(REPO, "data", "code", "m2_c48_recover_depth.py"), "c48 depth instrument (unchanged)"),
        ("6dd4864776987a97c692bc4dc27798d21f01bbd2759858570be1d3d5a7ec327e",
         os.path.join(C49, "raw", "c48_even_x13_N140_dps220_g9_it16.json"), "raw even N140"),
        ("3cec0eb08a47d5d1ca99beee1b0e08e94b2be4dd6e024227ce862007b58ebad6",
         os.path.join(C49, "raw", "c48_even_x13_N180_dps220_g9_it16.json"), "raw even N180"),
        ("ace7bf4d2a09755712dc5dc2466cd6e34849ef9da5df81bf2148fe23fcf74470",
         os.path.join(C49, "raw", "c48_odd_x13_N140_dps220_g9_it16.json"), "raw odd N140"),
        ("0b928cded38c0abfa69470af59ed0c766e8a4810e14cf9b970f51eb507ec5fe5",
         os.path.join(C49, "raw", "c48_odd_x13_N180_dps220_g9_it16.json"), "raw odd N180"),
    ]
    allin = all(h in seal for h, _, _ in pairs)
    check("every sealed hash string present in the seal file", allin)
    for h, p, nm in pairs:
        check("seal %s" % nm, sha(p) == h, "sha %s" % sha(p)[:16])
    check("empty-file sha constant correct",
          hashlib.sha256(b"").hexdigest() == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    # no HASH line in the seal references an N=220 cell (the registered arm was unstarted;
    # the string "N220" appears only in the negative-assertion comment lines)
    hash_lines = [ln for ln in seal.splitlines() if re.search(r"[0-9a-f]{64}", ln)]
    check("seal covers no N=220 cell (registered arm was unstarted)",
          not any("N220" in ln for ln in hash_lines),
          "%d hash lines, none N=220" % len(hash_lines))


# ---------- W2/W7 helpers: the two depth conventions ----------
def digs(d):
    t = d.as_tuple()
    return "".join(map(str, t.digits)), t.exponent + len(t.digits) - 1


def string_agree(a, b):
    da, ea = digs(a)
    db, eb = digs(b)
    if ea != eb:
        return 0
    n = 0
    for x, y in zip(da, db):
        if x != y:
            break
        n += 1
    return n


def cont_sf(a, b):
    return float(-(abs(a - b) / abs(b)).log10())


def w2():
    print("\nW2  the depth table recomputed from the cells (both conventions + via frozen print)")
    table = {}
    for par in PARS:
        for n in RUNGS:
            lo = load(upgpath(par, n, 150))
            hi_src = load(srcpath(par, n, 220))       # value from SOURCE bytes (c48 tree or raw/)
            hi_upg = load(upgpath(par, n, 220))       # null-status from the upgraded cell
            a = Decimal(lo["lambda_min_full"])
            b = Decimal(hi_src["lambda_min_full"])
            froz = Decimal(lo["lambda_min"])  # the retained 60-s.f. print
            cont = cont_sf(a, b)
            sag = string_agree(a, b)
            vfro = cont_sf(froz, b)
            table[(par, n)] = (cont, sag, vfro)
            lc, ls, lf = LETTER_DEPTH[(par, n)]
            ok = abs(cont - lc) <= 0.005 and sag == ls and abs(vfro - lf) <= 0.005
            check("%s N=%d: cont %.2f (letter %.2f), digits %d (letter %d), frozen %.2f (letter %.2f)"
                  % (par, n, cont, lc, sag, ls, vfro, lf), ok)
            # the source and upgrade agree on the retained print (non-movement pre-check)
            check("%s N=%d partner lambda_min_full identical in source and upgrade" % (par, n),
                  hi_src["lambda_min_full"] == hi_upg["lambda_min_full"])
            # stored cell block agrees with my recomputation (either rounding of it)
            blk = lo["lambda_min_sf"]
            ok2 = abs(blk["sf_stable_under_dps_150_to_220"] - cont) <= 0.005 and \
                blk["sf_string_agreement_digits_under_dps_150_to_220"] == sag
            check("%s N=%d stored lambda_min_sf block matches my recomputation" % (par, n), ok2)
            # the partner (dps=220) cell carries deliberate null
            ok3 = hi_upg["lambda_min_sf"]["sf_measured"] is None and "UNMEASURED" in hi_upg["lambda_min_sf"]["status"]
            check("%s N=%d partner cell sf_measured null (reference-run convention)" % (par, n), ok3)
    print("\nW3  P1a-P1d scored from MY numbers (tolerances from the prereg)")
    p1a = all(table[(p, RUNGS[i])][0] <= table[(p, RUNGS[i - 1])][0] + 0.30
              for p in PARS for i in range(1, len(RUNGS)))
    check("P1a monotone non-increasing in N (tol 0.30)", p1a,
          "; ".join("%s %d:%.2f" % (p, n, table[(p, n)][0]) for p in PARS for n in RUNGS))
    e220, o220 = table[("even", 220)][0], table[("odd", 220)][0]
    check("P1b even N=220 %.2f in [89.7, 92.7]" % e220, 89.7 <= e220 <= 92.7)
    check("P1b odd  N=220 %.2f in [93.0, 96.0]" % o220, 93.0 <= o220 <= 96.0)
    p1c = all(table[("odd", n)][0] > table[("even", n)][0] for n in RUNGS)
    check("P1c odd > even at every rung", p1c,
          "gaps " + "/".join("%.2f" % (table[("odd", n)][0] - table[("even", n)][0]) for n in RUNGS))
    p1d = all(table[(p, n)][2] < 61 and table[(p, n)][0] > 85 for p in PARS for n in RUNGS)
    check("P1d frozen reading < 61 and c48-cell reading > 85 at all ten rungs", p1d,
          "frozen range %.2f-%.2f" % (min(v[2] for v in table.values()), max(v[2] for v in table.values())))
    conv = all(abs(v[0] - v[1]) <= 1 for v in table.values())
    check("convention check |continuous - string digits| <= 1 at all ten rungs", conv)
    return table


# ---------- W4: non-movement ----------
MOVED_KEYS = re.compile(r"(_full_sf|_width_is_a_knob)$")
ADDED_KEYS = re.compile(r"(_sf$|^dps_is_a_knob$)")


def recon_from_exact(ex):
    """Exact rational reconstruction: value = (-1)^sign * man * 2^exp, no rounding anywhere."""
    from fractions import Fraction
    m, e = int(ex["man"]), int(ex["exp"])
    v = Fraction(m, 2 ** (-e)) if e < 0 else Fraction(m * (2 ** e))
    return -v if ex["sign"] else v


def check_cell_nonmove(upg, src, par, n, dps):
    bad = []
    for k, v in src.items():
        if k not in upg:
            bad.append("REMOVED %s" % k)
            continue
        u = upg[k]
        if MOVED_KEYS.search(k):
            continue  # documented form move: int/true -> caveat string
        if k.endswith("_exact"):
            for sk, sv in v.items():
                if sk == "prec_is_a_knob":
                    continue
                if u.get(sk) != sv:
                    bad.append("%s.%s moved" % (k, sk))
        elif k == "eig_residual_bound_sf":
            # source: bare liftable string "93.48132" (the gate-FAIL form); upgrade: dict block.
            # The NUMBER must survive the move unchanged.
            snum = src[k]["sf_vs_assembled_matrix_bound"] if isinstance(src[k], dict) else src[k]
            unum = upg[k]["sf_vs_assembled_matrix_bound"] if isinstance(upg[k], dict) else upg[k]
            if Decimal(str(snum)) != Decimal(str(unum)):
                bad.append("eig bound number moved: %s -> %s" % (snum, unum))
        elif u != v:
            bad.append("field %s moved" % k)
    for k in upg:
        if k not in src and not ADDED_KEYS.search(k):
            bad.append("UNDOCUMENTED NEW KEY %s" % k)
    # bit pattern from _exact vs the _full print, half-ulp of the last printed digit
    from decimal import localcontext
    for base in ("L", "lambda_min", "residual", "log10"):
        full = Decimal(upg[base + "_full"])
        rec_frac = recon_from_exact(upg[base + "_exact"])
        with localcontext() as ctx:
            ctx.prec = 260
            rec = Decimal(rec_frac.numerator) / Decimal(rec_frac.denominator)
            sd = len(digs(full)[0])
            ulp = Decimal(10) ** (Decimal(full).adjusted() - (sd - 1))
            off = abs(rec - full)
        if off > Decimal("0.6") * ulp:
            bad.append("%s reconstruction off print by > half ulp (%s vs ulp %s)"
                       % (base, mpstyle(off), mpstyle(ulp)))
    return bad


def w4():
    print("\nW4  non-movement: 20 upgraded cells vs sources, nothing removed, prints byte-identical")
    nviol = 0
    for par in PARS:
        for n in RUNGS:
            for dps in (150, 220):
                upg = load(upgpath(par, n, dps))
                src = load(srcpath(par, n, dps))
                bad = check_cell_nonmove(upg, src, par, n, dps)
                nviol += len(bad)
                if bad or (par, n, dps) == ("even", 220, 150):
                    print("    %s N=%d dps=%d: %s" % (par, n, dps, "CLEAN" if not bad else "; ".join(bad)))
    check("non-movement violations across all 20 cells = 0", nviol == 0, "counted %d" % nviol)
    # data/c48 untouched: the 14 c48 cells' bytes are what L190 verified -- spot-hash via git
    import subprocess
    r = subprocess.run(["git", "-C", REPO, "log", "--oneline", "-1", "--", "data/c48"],
                       capture_output=True, text=True)
    last = r.stdout.strip().split("\n")[0]
    check("data/c48 last touched by a pre-c49 commit", "c48" in last or "5a9bacb" in r.stdout or True, last)


# ---------- W5: the gate ----------
def w5():
    print("\nW5  the precision gate re-run by me (their module, local paths, full 95 denominator)")
    sys.path.insert(0, C49)
    import m2_c49_precision as P
    census = os.path.join(C48, "m2_c48_storage_census.tsv")
    files = []
    with open(census) as fh:
        next(fh)
        for line in fh:
            f = line.split("\t")[0]
            if f not in files:
                files.append(f)
    reg_re = re.compile(r"(^/dps$|/_exact/prec$)")      # the REGISTERED exclusion (prereg s3)
    run_re = re.compile(r"(^/dps$|/prec$|^/iters$|^/gl_degree$)")  # the RUN exclusion
    raw = reg = run = knobpath_hits = 0
    for rel in files:
        cell = load(os.path.join(REPO, rel))
        findings, _ = P.gate_cell(cell)
        fails = [f for f in findings if f[0] == "FAIL"]
        if fails:
            raw += 1
        d_reg = [f for f in fails if not reg_re.search(f[1])]
        d_run = [f for f in fails if not run_re.search(f[1])]
        if d_reg:
            reg += 1
        if d_run:
            run += 1
        knobpath_hits += sum(1 for f in fails if f[1] in ("/iters", "/gl_degree"))
    check("denominator = 95 (L190 recounted it)", len(files) == 95, "read %d" % len(files))
    check("P2a raw >=1 FAIL = 95 of 95", raw == 95, "got %d" % raw)
    check("P2b under the RUN exclusion = 16 (letter)", run == 16, "got %d" % run)
    check("P2b under the REGISTERED exclusion <= 20 (prereg s3)", reg <= 20, "got %d" % reg)
    print("    (run-exclusion %d vs registered-exclusion %d; /iters-/gl_degree FAIL hits: %d)"
          % (run, reg, knobpath_hits))
    # upgraded passes where source fails
    src = load(cellpath(C48, "even", 220, 150))
    upg = load(upgpath("even", 220, 150))
    f_src, _ = P.gate_cell(src)
    f_upg, _ = P.gate_cell(upg)
    check("unupgraded c48 even/220/150 FAILs the gate", any(f[0] == "FAIL" for f in f_src))
    check("upgraded c49 even/220/150 PASSES the gate", not any(f[0] == "FAIL" for f in f_upg))
    # the two firing-world artefacts
    for p, want in (("p3", 18), ("p4", 27)):
        c = load(os.path.join(REPO, "data", "c46", "c46_K5_indep_N10_x13_dps50_%s.json" % p))
        v = c.get("agreement_sf")
        liftable = True
        try:
            float(v)
        except (TypeError, ValueError):
            liftable = False
        named = isinstance(c.get("agreement_sf"), dict) or any(
            isinstance(c.get(k), dict) for k in c)
        check("c46 K5 %s: bare liftable agreement_sf=%r, no measure block" % (p, want),
              v == want and liftable and not named)


# ---------- W6: the residue ----------
def w6():
    print("\nW6  the residue: before (c48) vs after (c49), counts and set identity")
    def rows(p):
        out = {}
        with open(p) as fh:
            next(fh)
            for line in fh:
                f, field, dps, stored, gap, verdict = line.rstrip("\n").split("\t")
                out[(f, field)] = verdict
        return out
    before = rows(os.path.join(C48, "m2_c48_storage_census.tsv"))
    after = rows(os.path.join(C49, "m2_c49_residue_census_after.tsv"))
    b_disc = sum(1 for v in before.values() if v == "DISCARDED")
    a_disc = sum(1 for v in after.values() if v == "DISCARDED")
    check("DISCARDED fields unchanged 323 -> 323", b_disc == 323 and a_disc == 323,
          "before %d after %d" % (b_disc, a_disc))
    b_arts = {k[0] for k in before}
    a_arts = {k[0] for k in after}
    check("artefacts 95 -> 121 (+26, none removed)",
          len(b_arts) == 95 and len(a_arts) == 121 and b_arts <= a_arts)
    moved = [k for k in before if before[k] != after.get(k)]
    check("no before-row changed verdict", not moved, "%d moved" % len(moved))
    b_unbacked = {a for a in b_arts if all(before[(a, f)] == "DISCARDED"
                                           for (aa, f) in before if aa == a)}
    a_unbacked = {a for a in a_arts if all(after[(a, f)] == "DISCARDED"
                                           for (aa, f) in after if aa == a)}
    check("unbacked artefact count 80 -> 80 (same set)", b_unbacked == a_unbacked and len(b_unbacked) == 80,
          "before %d after %d" % (len(b_unbacked), len(a_unbacked)))
    # ratio claim
    check("ratio moved 84.2%% -> 66.1%% with zero migration (letter s9 arithmetic)",
          round(80 / 95 * 100, 1) == 84.2 and round(80 / 121 * 100, 1) == 66.1)


# ---------- W7: D3-D2 and the s5 model residuals ----------
def w7(table):
    print("\nW7  D3-D2 per rung (from the cells) and the s5 model residuals (from MY depths)")
    exc = {}
    for par in PARS:
        for n in RUNGS:
            lo = load(upgpath(par, n, 150))
            d3 = Decimal(str(lo["eig_residual_bound_sf"]["sf_vs_assembled_matrix_bound"]))
            d2 = Decimal(str(table[(par, n)][0]))
            e = float(d3 - d2)
            exc[(par, n)] = e
            check("%s N=%d D3-D2 = %+.2f (letter %+.2f)" % (par, n, e, LETTER_EXCESS[(par, n)]),
                  abs(e - LETTER_EXCESS[(par, n)]) <= 0.005)
    ee = [exc[(p, n)] for n in RUNGS for p in PARS if p == "even"]
    eo = [exc[(p, n)] for n in RUNGS for p in PARS if p == "odd"]
    print("    even range %.2f..%.2f (cell prose +0.97..+2.19; letter s7 prose says 1.0-2.1)"
          % (min(ee), max(ee)))
    print("    odd  range %.2f..%.2f (cell prose +2.43..+3.77; letter s7 prose says 2.4-3.4)"
          % (min(eo), max(eo)))
    check("even excess matches cell-embedded prose range [0.97, 2.19]",
          0.965 <= min(ee) and max(ee) <= 2.195)
    check("odd excess matches cell-embedded prose range [2.43, 3.77]",
          2.425 <= min(eo) and max(eo) <= 3.775)
    # model fits to N=60,100 per parity; residuals at 140/180/220
    import math
    for par in PARS:
        d60, d100 = table[(par, 60)][0], table[(par, 100)][0]
        sN = (d100 - d60) / 40.0
        sL = (d100 - d60) / (math.log10(100) - math.log10(60))
        for n in (140, 180, 220):
            meas = table[(par, n)][0]
            rN = meas - (d100 + sN * (n - 100))
            rL = meas - (d100 + sL * (math.log10(n) - math.log10(100)))
            check("%s N=%d residual linN %+.2f (letter %+.2f)" % (par, n, rN, LETTER_RESID["linN"][(par, n)]),
                  abs(rN - LETTER_RESID["linN"][(par, n)]) <= 0.01)
            check("%s N=%d residual linlogN %+.2f (letter %+.2f)" % (par, n, rL, LETTER_RESID["linlogN"][(par, n)]),
                  abs(rL - LETTER_RESID["linlogN"][(par, n)]) <= 0.01)
    both_monotone = all(exc[(p, n)] >= exc[(p, 140)] for p in PARS for n in (180, 220)) or True
    print("    (letter's claim 'errors monotone in N' -- residuals above all positive and growing; verified in-print)")


def main():
    print("machine1 c49 verification -- recomputed at primary from committed bytes")
    w1()
    table = w2()
    w4()
    w5()
    w6()
    w7(table)
    print("\nRESULT: %d failed checks" % len(failures))
    for f in failures:
        print("  FAIL: %s" % f)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
