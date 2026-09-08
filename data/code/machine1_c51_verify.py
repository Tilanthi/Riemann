#!/usr/bin/env python3
"""machine1_c51_verify.py -- m1's independent adjudication verifier for machine2 cycle 51.

The witness note (3c994bb) named what adjudication owed beyond reading: (1) re-derive SCALING's
n = NZERO = {5:4, 13:21, 19:38} from first principles, (2) re-derive THRESHOLD's interval and
reproduce the disclosed exclusion defect, (3) RE-RUN the REFINE counts from the committed
coefficients rather than reading them, (4) reproduce P0's 90/90, (5) reproduce P6's one-integer
refutation, (6) verify the ERRATUM-27 marker is on the line in the c50 letter. This file does
all six, plus the structural checks (seals, grader byte-reproduction, census re-derivation).

INDEPENDENCE LAYERS (deliberate):
  * the census/P-verdict re-derivation (T2) is m1's own code from the prereg text, not the grader's;
  * the 9-knob + REFINE recount (T6) is numpy float64 with m1's own sampling/counting code and the
    basis built from the closed form (w_j = 2 pi j / L, norms 1/sqrt(L), sqrt(2/L)) -- a different
    arithmetic path from mpmath at dps 50, agreeing only if the integers are real;
  * the exact-instrument recount (T7) imports machine2's OWN committed functions (count_all_knobs,
    refine) and runs them on the committed coefficients -- the registered instrument path itself;
  * P0 (T8) runs machine2's committed recount gate in a copy, never in place.

usage:
  machine1_c51_verify.py fast      # T0 seals/timing, T1 grader bytes, T2 census, T3 NZERO,
                                   # T4 THRESHOLD, T5 SCALING, T9 ERRATUM marker
  machine1_c51_verify.py numpy     # T6 independent recount, all rungs, all cells
  machine1_c51_verify.py mpmath    # T7 exact-instrument recount, 6 critical rungs
  machine1_c51_verify.py p0        # T8 their P0 gate re-run in a temp tree
Receipt appends to machine1_c51_verify.out beside this file. Exit 0 iff every check PASS.
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))          # .../Riemann_exchange/data/code
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))     # .../Riemann_exchange
C51 = os.path.join(REPO, "data", "c51")
RECEIPT = os.path.join(HERE, "machine1_c51_verify.out")

CELLS = [("even", 5, 100, 5), ("odd", 5, 100, 5),
         ("even", 19, 100, 5), ("odd", 19, 100, 5),
         ("even", 13, 180, 5), ("odd", 13, 180, 5),
         ("even", 13, 100, 7), ("odd", 13, 100, 7)]
NEW_WINDOWS = [(5, 100), (19, 100), (13, 180)]
DELTA_N = {"even": [0, 0, 0, 2, 2], "odd": [0, 0, 2, 2, 6]}   # Model N, from the prereg text
ONSET_N = {"even": 4, "odd": 3}
P1_PREFIX = {"even": (1, 2, 3), "odd": (1, 2)}                 # prereg P1: Sturm prefix, new windows
KAT_FRONTIER = "5.0e-3"

FAILS = []


def sec(title):
    with open(RECEIPT, "a") as f:
        f.write("\n===== %s  [%s] =====\n" % (title, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))


def say(msg):
    print(msg, flush=True)
    with open(RECEIPT, "a") as f:
        f.write(msg + "\n")


def check(name, ok, detail=""):
    line = "%-4s %s%s" % ("PASS" if ok else "FAIL", name, ("  -- " + detail) if detail else "")
    say(line)
    if not ok:
        FAILS.append(name)
    return ok


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def cell_path(par, X, N, K):
    return os.path.join(C51, "m2_c51_nodes_%s_x%d_N%d_k%d.json" % (par, X, N, K))


def load_cells():
    return {(p, x, n): json.load(open(cell_path(p, x, n, k))) for (p, x, n, k) in CELLS}


def admitted(cell):
    """the rungs this cycle may speak about (prereg: c50 residual rule AND knob-stable)."""
    return [r for r in cell["rungs"] if r["admitted"] and r["stable"]]


# ---------------------------------------------------------------- T0 seals, inventory, timing
def t0():
    sec("T0 seals / inventory / launch timing")
    pre = open(os.path.join(C51, "m2_c51_prereg.md")).read()
    block = pre.split("INSTRUMENT_SHA256_BEGIN")[1].split("INSTRUMENT_SHA256_END")[0]
    sealed = {}
    for ln in block.strip().splitlines():
        h, fn = ln.split()
        sealed[fn.strip()] = h.strip()
    for fn, h in sorted(sealed.items()):
        mine = sha256(os.path.join(C51, fn))
        check("seal %s" % fn, mine == h, "%s" % ("matches" if mine == h else "mine %s" % mine))
    need = (["m2_c51_prereg.md", "m2_c51_kat.json", "m2_c51_p0_recount.json",
             "m2_c51_pooled.py", "m2_c51_pooled.out", "m2_c51_scores.json", "m2_c51_scores.out",
             "m2_c51_prelaunch_absence.out", "m2_c51_freshclone_verify.out", "m2_c51_seal_verify.sh"]
            + ["m2_c51_nodes_%s_x%d_N%d_k%d.json" % c for c in CELLS])
    missing = [f for f in need if not os.path.exists(os.path.join(C51, f))]
    check("inventory %d artefacts" % len(need), not missing, "missing: %s" % missing or "none")
    launch = open(os.path.join(C51, "logs", "LAUNCH.txt")).read()
    say("LAUNCH.txt: %s" % " ".join(launch.split()))
    ts = subprocess.run(["git", "-C", REPO, "show", "-s", "--format=%cI", "2723194"],
                        capture_output=True, text=True).stdout.strip()
    check("prereg push precedes first cell", ts <= "2026-09-08T12:26:18+00:00",
          "2723194 committer date %s vs first cell 12:26:18Z" % ts)


# ---------------------------------------------------------------- T1 grader + pooled byte reproduction
def t1():
    sec("T1 grader and pooled byte-reproduction (in a copy, never in place)")
    tmp = tempfile.mkdtemp(prefix="c51_t1_")
    shutil.copytree(C51, os.path.join(tmp, "c51"))
    for script, outs in (("m2_c51_score.py", ["m2_c51_scores.out", "m2_c51_scores.json"]),
                         ("m2_c51_pooled.py", ["m2_c51_pooled.out"])):
        r = subprocess.run([sys.executable, os.path.join(tmp, "c51", script)],
                           capture_output=True, text=True, cwd=os.path.join(tmp, "c51"))
        check("%s exit 0" % script, r.returncode == 0, r.stderr.strip()[-200:] or "")
        check("%s stderr empty" % script, r.stderr == "", "streams never merged (c51 §8)")
        for out in outs:
            a = sha256(os.path.join(C51, out))
            b = sha256(os.path.join(tmp, "c51", out))
            check("%s byte-identical: %s" % (script, out), a == b, "%s" % b[:16])
    shutil.rmtree(tmp)


# ---------------------------------------------------------------- T2 census + P-verdicts, m1's own code
def t2():
    sec("T2 census and P1-P8 re-derivation from the cell JSONs (m1's own code, prereg rules)")
    cells = load_cells()
    sj = json.load(open(os.path.join(C51, "m2_c51_scores.json")))

    # census
    my_census = {}
    for (p, x, n), cell in cells.items():
        adm = admitted(cell)
        my_census["%s_x%d_N%d" % (p, x, n)] = dict(
            computed=len(cell["rungs"]), admitted=len(adm),
            dropped_residual=sum(1 for r in cell["rungs"] if not r["admitted"]),
            dropped_unstable=sum(1 for r in cell["rungs"] if r["admitted"] and not r["stable"]),
            delta=[r["delta"] for r in adm])
    for k, v in sorted(my_census.items()):
        p = sj["census"][k]
        same = all(v[f] == p[f] for f in ("computed", "admitted", "dropped_residual",
                                          "dropped_unstable", "delta"))
        check("census %s" % k, same, "delta %s" % v["delta"])

    # onsets
    onsets = {}
    for (p, x, n), cell in cells.items():
        adm = admitted(cell)
        on = next((r["rung"] for r in adm if r["delta"] != 0), None)
        onsets["%s_x%d_N%d" % (p, x, n)] = (on, next(
            (r["delta"] for r in adm if r["rung"] == on), None) if on else None)
    say("my onsets: %s" % {k: v[0] for k, v in sorted(onsets.items())})

    # P1 Sturm prefix at new windows
    p1_tested = [r for (x, n) in NEW_WINDOWS for p in ("even", "odd")
                 for r in admitted(cells[(p, x, n)]) if r["rung"] in P1_PREFIX[p]]
    check("P1: %d prefix integers, 0 nonzero -> HELD" % len(p1_tested),
          len(p1_tested) == 15 and all(r["delta"] == 0 for r in p1_tested))

    # P2 onset universality (and P4 = its N180 conjunct, P3 first delta)
    p2ok = all(onsets["%s_x%d_N%d" % (p, x, n)][0] == ONSET_N[p]
               for (p, x, n, k) in CELLS)
    check("P2: onset (%d,%d) at all 8 cells -> HELD" % (ONSET_N["even"], ONSET_N["odd"]), p2ok)
    check("P4: N180 conjunct of P2 -> HELD",
          onsets["even_x13_N180"][0] == 4 and onsets["odd_x13_N180"][0] == 3)
    check("P3: first defect == +2 at all 8 cells",
          all(v[1] == 2 for v in onsets.values()))

    # P5 monotone on the k=7 arm
    for p in ("even", "odd"):
        d = [r["delta"] for r in admitted(cells[(p, 13, 100)])]
        check("P5 %s k=7 non-decreasing" % p, all(d[i] >= d[i - 1] for i in range(1, len(d))),
              str(d))

    # P6 ABSOLUTE full-vector, tolerance 0, new windows only
    p6 = []
    for (x, n) in NEW_WINDOWS:
        for p in ("even", "odd"):
            for r in admitted(cells[(p, x, n)]):
                if r["rung"] <= 5 and r["delta"] != DELTA_N[p][r["rung"] - 1]:
                    p6.append("%s x%d N%d rung %d: delta %d, Model N says %d"
                              % (p, x, n, r["rung"], r["delta"], DELTA_N[p][r["rung"] - 1]))
    n6 = sum(1 for (x, n) in NEW_WINDOWS for p in ("even", "odd")
             for r in admitted(cells[(p, x, n)]) if r["rung"] <= 5)
    check("P6: %d integers tested, %d mismatch(es) -> %s"
          % (n6, len(p6), "REFUTED" if p6 else "HELD"), "; ".join(p6) or "none")
    check("P6 mismatch is exactly the registered one (odd x19 N100 rung 5, 2 vs 6)",
          p6 == ["odd x19 N100 rung 5: delta 2, Model N says 6"])

    # P7 instrument, from the published fields (T6/T7 re-run them independently)
    ref = sum(1 for c in cells.values() for r in admitted(c) if r["nu_refine_48001"] != r["nu"])
    lob = sum(1 for c in cells.values() for r in admitted(c)
              if float(r["lobe_min_ratio"]) <= float(KAT_FRONTIER))
    check("P7 (field-level): refine mismatches 0, lobes at/below frontier 0", ref == 0 and lob == 0)

    # Theorem T over every computed rung
    tf = sum(1 for c in cells.values() for r in c["rungs"] if r["parity_T_ok"] is False)
    check("Theorem T: 0 parity violations over every computed rung", tf == 0)

    # P8 tallies re-derivation comes in T4/T5 (THRESHOLD, SCALING) after their inputs are re-derived


# ---------------------------------------------------------------- T3 NZERO from first principles
def t3():
    sec("T3 NZERO re-derived from the zeta zeros themselves (mpmath, independent of c46's table)")
    from mpmath import mp, zetazero, mpf, pi
    mp.dps = 30
    zeros = [zetazero(k).imag for k in range(1, 45)]
    mono = all(zeros[i] < zeros[i + 1] for i in range(len(zeros) - 1))
    check("mpmath ordinates strictly increasing", mono)
    for x, want in ((5, 4), (13, 21), (19, 38)):
        lim = 2 * pi * mpf(x)
        n = sum(1 for g in zeros if g <= lim)
        g_n, g_n1 = zeros[want - 1], zeros[want]
        check("NZERO[%d] = %d" % (x, want), n == want,
              "gamma_%d = %.6f <= 2pi*%d = %.6f < gamma_%d = %.6f"
              % (want, float(g_n), x, float(lim), want + 1, float(g_n1)))


# ---------------------------------------------------------------- T4 THRESHOLD interval + exclusion defect
def t4():
    from decimal import Decimal as D
    sec("T4 THRESHOLD interval re-derivation + the disclosed exclusion defect")
    cells = load_cells()
    # calibration window x=13 N=100, pooled by lambda across sectors, admitted rungs
    rows = []
    for p in ("even", "odd"):
        for r in admitted(cells[(p, 13, 100)]):
            rows.append((D(r["log10"]), p, r["rung"], r["delta"]))
    rows.sort()
    last_exact = max(r for r in rows if r[3] == 0)
    first_def = min(r for r in rows if r[3] != 0)
    check("calibration: last exact pooled rung is even rung 3 @ %s" % last_exact[0],
          last_exact[1:] == ("even", 3, 0))
    check("calibration: first defective pooled rung is odd rung 3 @ %s" % first_def[0],
          first_def[1:] == ("odd", 3, 2))
    lo, hi = D("-43.9259"), D("-40.6436")
    check("sealed LO = 6-decimal round of the last-exact rung", abs(lo - last_exact[0]) < D("1e-4"),
          "%s vs %s" % (lo, last_exact[0]))
    check("sealed HI = 6-decimal round of the first-defective rung",
          abs(hi - first_def[0]) < D("1e-4"), "%s vs %s" % (hi, first_def[0]))
    # the disclosed defect: the first-defective rung falls INSIDE the sealed ambiguous band
    inside = lo < first_def[0] <= hi
    check("EXCLUSION DEFECT reproduced: first-defective %s is strictly inside (%s, %s]"
          % (first_def[0], lo, hi), inside,
          "gap = %s" % (hi - first_def[0]))
    say("     FINDING (prose slip in m2's letter sec 3): the gap is %.4e, the letter says \"2.1e-8\""
        % float(hi - first_def[0]))
    say("     -- the mechanism (strictly inside the sealed band) is unaffected; the number is off")
    # the rounding DIRECTION is what did it: toward zero raised HI above the rung's own value
    # (excluding it); an away-from-zero 6-decimal round (-40.6437) would have classified it
    # defective and given the odd onset 3 at calibration
    check("rounding direction isolated: HI(6dp toward zero) > rung > HI(6dp away from zero)",
          D("-40.6436") > first_def[0] > D("-40.6437"),
          "only the away-from-zero round includes its own calibration point")
    # THRESHOLD per-sector predictions recomputed under the sealed rule, vs the grader's P8
    sj = json.load(open(os.path.join(C51, "m2_c51_scores.json")))
    ok = True
    for (p, x, n, k) in CELLS:
        key = "%s_x%d_N%d" % (p, x, n)
        pred, ambig = None, False
        for r in admitted(cells[(p, x, n)]):
            lg = D(r["log10"])
            if lg > hi:
                pred = r["rung"]
                break
            if lo < lg <= hi:
                ambig = True
        theirs = sj["P8"]["per_cell"][key]["THRESHOLD"]["pred"]
        if (str(pred) if pred is not None else None) != (
                theirs if not theirs.startswith(("onset", "no-defect")) else None):
            ok = False
            say("     THRESHOLD pred divergence at %s: mine %s theirs %s" % (key, pred, theirs))
    check("THRESHOLD per-cell predictions match the grader under the sealed rule", ok)
    # the calibration-window odd miss is the defect's own consequence (onset 4 predicted vs 3 true)
    check("calibration-window odd cell mis-scored by the sealed literal (m2's disclosure)",
          sj["P8"]["per_cell"]["odd_x13_N100"]["THRESHOLD"]["pred"] == "4"
          and sj["P8"]["per_cell"]["odd_x13_N100"]["measured"] == 3)


# ---------------------------------------------------------------- T5 SCALING re-derivation
def t5():
    from decimal import Decimal as D
    sec("T5 SCALING re-derivation: onset = max(1, round_half_up(onset_13 * n_x / 21))")
    sj = json.load(open(os.path.join(C51, "m2_c51_scores.json")))
    NZERO = {5: D(4), 13: D(21), 19: D(38)}

    def half_up(v):
        return max(1, int(v + D("0.5")))

    for x in (5, 13, 19):
        for p in ("even", "odd"):
            pred = half_up(D(ONSET_N[p]) * NZERO[x] / NZERO[13])
            say("     SCALING %s x=%d: onset %d" % (p, x, pred))
    ok = True
    for (p, x, n, k) in CELLS:
        key = "%s_x%d_N%d" % (p, x, n)
        pred = half_up(D(ONSET_N[p]) * NZERO[x] / NZERO[13])
        cell = json.load(open(cell_path(p, x, n, k)))
        n_adm = len([r for r in cell["rungs"] if r["admitted"] and r["stable"]])
        # the grader renders a prediction beyond the computed rungs as "onset>N (beyond computed)"
        mine = str(pred) if pred <= n_adm else "onset>%d (beyond computed)" % n_adm
        theirs = sj["P8"]["per_cell"][key]["SCALING"]["pred"]
        if mine != theirs:
            ok = False
            say("     SCALING divergence at %s: mine %s theirs %s" % (key, mine, theirs))
    check("SCALING per-cell predictions match the grader (1,1 / 4,3 / 7,5)", ok)


# ---------------------------------------------------------------- T6 hybrid independent recount
def t6():
    import numpy as np
    from mpmath import mp, mpf, pi as mpi, cos as mcos, sin as msin
    mp.dps = 50
    sec("T6 independent recount: float64 everywhere + mpmath arbitration of near-noise samples")
    say("     basis: w_j = 2 pi j / L (even j=0..N, odd j=1..N); nr = 1/sqrt(L), sqrt(2/L)")
    say("     m1's own sampling/counting code; only samples with |v| < 1e-9*max are re-evaluated")
    say("     at dps 50 (their instrument's working precision), spliced back before counting.")
    # -- demonstrate why pure float64 cannot referee tol=0 here (measured, one example)
    cell = json.load(open(cell_path("even", 19, 100, 5)))
    Lm = mpf(cell["L"]); L = float(Lm); N = 100
    jj = np.arange(0, N + 1, dtype=float)
    omf = 2 * np.pi * jj / L
    nrf = np.array([1 / np.sqrt(L)] + [np.sqrt(2 / L)] * N)
    amps = np.array([float(s) for s in cell["rungs"][0]["coef"]]) * nrf
    t0f = -L / 2 + L * 1 / 1202
    v_f = float(amps @ np.cos(omf * t0f))
    omm = [2 * mpi * j / Lm for j in range(N + 1)]
    nrm = [1 / mp.sqrt(Lm)] + [mp.sqrt(2 / Lm)] * N
    cm = [mpf(s) for s in cell["rungs"][0]["coef"]]
    v_m = sum(cm[a] * nrm[a] * mcos(omm[a] * (-Lm / 2 + Lm * mpf(1) / 1202)) for a in range(N + 1))
    say("     float64 limitation, measured: even x19 rung 1, first grid point of the 1201 grid --")
    say("     float64 value %.3e vs dps-50 value %.3e: the deep-window eigenfunctions carry" % (v_f, float(v_m)))
    say("     single-signed plateaus at the 1e-38 level, 22 orders below the float64 noise floor;")
    say("     pure float64 fragments them into spurious tol=0 sign changes (28 vs 2 at rung 2).")
    say("     The tol!=0 knobs are immune (cut 1e-8*max sits far above the noise floor).")

    TOLKEY = {0.0: "0.0", 1e-8: "1.0e-8", 1e-4: "0.0001"}
    THRESH = 1e-9
    bad = 0
    worst_lobe = (None, float("inf"))

    def spliced(amps, omf, M, L, Lm, par, N, cm, omm, nrm, F, npts):
        i = np.arange(npts)
        t = -L / 2 + L * (i + 1) / (npts + 1)
        v = amps @ M(np.outer(omf, t))
        mx = float(np.max(np.abs(v)))
        amb = np.abs(v) < THRESH * mx
        for k in np.flatnonzero(amb):
            tk = -Lm / 2 + Lm * mpf(int(k) + 1) / (npts + 1)
            v[k] = float(sum(cm[a] * nrm[a] * F(omm[a] * tk) for a in range(len(omm))))
        return v, int(amb.sum())

    for (p, x, n, k) in CELLS:
        cell = json.load(open(cell_path(p, x, n, k)))
        Lm = mpf(cell["L"]); L = float(Lm)
        jj = np.arange(0 if p == "even" else 1, n + 1, dtype=float)
        omf = 2 * np.pi * jj / L
        nrf = (np.array([1 / np.sqrt(L)] + [np.sqrt(2 / L)] * (len(jj) - 1)) if p == "even"
               else np.full(n, np.sqrt(2 / L)))
        if p == "even":
            omm = [2 * mpi * j / Lm for j in range(n + 1)]
            nrm = [1 / mp.sqrt(Lm)] + [mp.sqrt(2 / Lm)] * n
        else:
            omm = [2 * mpi * j / Lm for j in range(1, n + 1)]
            nrm = [mp.sqrt(2 / Lm)] * n
        Mn = np.cos if p == "even" else np.sin
        Fm = mcos if p == "even" else msin
        for r in cell["rungs"]:
            amps = np.array([float(s) for s in r["coef"]]) * nrf
            cm = [mpf(s) for s in r["coef"]]
            counts, n_amb = {}, 0
            for g in (1201, 4001, 12001):
                vg, na = spliced(amps, omf, Mn, L, Lm, p, n, cm, omm, nrm, Fm, g)
                n_amb += na
                mx = float(np.max(np.abs(vg)))
                for tol in (0.0, 1e-8, 1e-4):
                    cut = tol * mx
                    s = np.sign(vg)
                    s[np.abs(vg) <= cut] = 0
                    s = s[s != 0]
                    counts["%d_%s" % (g, TOLKEY[tol])] = int(np.sum(s[1:] != s[:-1]))
            vr, na = spliced(amps, omf, Mn, L, Lm, p, n, cm, omm, nrm, Fm, 48001)
            n_amb += na
            mx = float(np.max(np.abs(vr)))
            keep = vr != 0
            s = np.sign(vr[keep])
            ch = s[1:] != s[:-1]
            nu_ref = int(np.sum(ch))
            starts = np.concatenate(([0], np.flatnonzero(ch) + 1))
            lobes = np.maximum.reduceat(np.abs(vr[keep]), starts)
            lobe = float(lobes.min() / mx)
            nu_cons = counts["1201_0.0"] if len(set(counts.values())) == 1 else None
            ok = (counts == r["counts"] and nu_cons == r["nu"] and nu_ref == r["nu_refine_48001"]
                  and abs(lobe - float(r["lobe_min_ratio"])) <= 1e-3 * float(r["lobe_min_ratio"]))
            if not ok:
                bad += 1
                say("     MISMATCH %s x%d N%d rung %d: counts %s vs %s, nu %s/%s, refine %s/%s, "
                    "lobe %.6f/%s" % (p, x, n, r["rung"], counts, r["counts"], nu_cons, r["nu"],
                                      nu_ref, r["nu_refine_48001"], lobe, r["lobe_min_ratio"]))
            if r["admitted"] and r["stable"]:
                ratio = lobe / float(KAT_FRONTIER)
                if ratio < worst_lobe[1]:
                    worst_lobe = ("%s_x%d_N%d_r%d" % (p, x, n, r["rung"]), ratio)
    n_rungs = sum(len(json.load(open(cell_path(*c)))["rungs"]) for c in CELLS)
    check("T6: all %d rungs reproduce (9-knob dict, consensus nu, refine48001, lobe to 1e-3)"
          % n_rungs, bad == 0, "%d mismatches" % bad)
    say("     thinnest admitted lobe margin over the frontier: %s at %.3fx" % worst_lobe)
    say("     (m2's letter: odd x13 rung 5 at 1.139x N=100 / 1.096x N=180)")


# ---------------------------------------------------------------- T7 exact-instrument recount
T7_RUNGS = [("odd", 19, 100, 5, 5, "the P6 refutation carrier (delta 2 vs Model N's 6)"),
            ("odd", 13, 100, 7, 5, "the +6 carrier, thinnest lobe margin (0.005694)"),
            ("odd", 13, 180, 5, 5, "the +6 N-control (0.005481)"),
            ("even", 13, 100, 7, 1, "a clean Sturm-prefix rung"),
            ("even", 5, 100, 5, 4, "first defect +2 at x=5"),
            ("odd", 5, 100, 5, 3, "odd first defect +2 at x=5")]


def t7():
    import importlib.util
    from mpmath import mp, mpf
    sec("T7 exact-instrument recount (machine2's committed count_all_knobs + refine, mpmath dps 50)")
    spec = importlib.util.spec_from_file_location(
        "m2_c51_nodes", os.path.join(C51, "m2_c51_nodes.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mp.dps = 50
    bad = 0
    for (p, x, n, k, rung, why) in T7_RUNGS:
        cell = json.load(open(cell_path(p, x, n, k)))
        r = next(q for q in cell["rungs"] if q["rung"] == rung)
        L = mpf(cell["L"])
        om, nr, _ = mod.P.make_basis_parity(n, L, p)
        coef = [mpf(c) for c in r["coef"]]
        t0 = time.time()
        counts, stable, nu = mod.count_all_knobs(coef, om, nr, L, p)
        nu_ref, lobe = mod.refine(coef, om, nr, L, p)
        ok = (counts == r["counts"] and stable == r["stable"] and nu == r["nu"]
              and nu_ref == r["nu_refine_48001"]
              and abs(float(lobe) - float(r["lobe_min_ratio"])) <= 1e-4 * float(r["lobe_min_ratio"]))
        if not ok:
            bad += 1
        say("     %-4s x%-2d N%-3d rung %d  nu=%s refine=%s lobe=%.6f vs %s  %s  (%.0fs)  [%s]"
            % (p, x, n, rung, nu, nu_ref, float(lobe), r["lobe_min_ratio"],
               "PASS" if ok else "FAIL", time.time() - t0, why))
    check("T7: %d critical rungs reproduce under the registered instrument itself"
          % len(T7_RUNGS), bad == 0)


# ---------------------------------------------------------------- T8 their P0 gate, in a copy
def t8():
    sec("T8 P0 gate re-run (their recount, in a temp tree with c42/c46/c50/code beside it)")
    tmp = tempfile.mkdtemp(prefix="c51_t8_")
    os.makedirs(os.path.join(tmp, "data"))
    for d in ("c42", "code", "c46", "c50", "c51"):  # code: _find_dir puts it on sys.path (layout, not import)
        shutil.copytree(os.path.join(REPO, "data", d), os.path.join(tmp, "data", d),
                        ignore=shutil.ignore_patterns("__pycache__"))
    r = subprocess.run([sys.executable, os.path.join(tmp, "data", "c51", "m2_c51_nodes.py"),
                        "recount"], capture_output=True, text=True)
    tail = [ln for ln in r.stdout.strip().splitlines() if ln][-1]
    check("P0 gate: %s" % tail, r.returncode == 0 and "90/90" in tail and "PASS" in tail,
          "exit %d, stderr %s" % (r.returncode, r.stderr.strip()[-200:]))
    shutil.rmtree(tmp)


# ---------------------------------------------------------------- T9 ERRATUM 27 on the line
def t9():
    sec("T9 ERRATUM 27 marker on the line in the c50 letter")
    c50 = [f for f in os.listdir(REPO)
           if f.startswith("8211142501_")][0]
    txt = open(os.path.join(REPO, c50)).read()
    check("c50 letter carries the on-the-line withdrawal",
          "WITHDRAWN AS A MECHANISM BY ERRATUM 27" in txt)
    struck = "~~**The dislocation is EVEN" in txt and "the one the data actually supports.~~" in txt
    check("the strike delimiters wrap the mechanism sentence itself", struck)
    er = [f for f in os.listdir(REPO) if "machine2-ERRATUM-27" in f]
    check("ERRATUM 27 sibling file present (standalone, not the c51 letter)",
          len(er) == 1, str(er))
    gl = subprocess.run(["git", "-C", REPO, "log", "--format=%h", "-S",
                         "WITHDRAWN AS A MECHANISM BY ERRATUM 27", "--", c50],
                        capture_output=True, text=True).stdout.split()
    check("marker entered the c50 letter in the c51 letter push (fdee199)",
          gl == ["fdee199"], str(gl))


def main():
    modes = sys.argv[1:] or ["fast"]
    if "fast" in modes:
        t0(); t1(); t2(); t3(); t4(); t5(); t9()
    if "numpy" in modes:
        t6()
    if "mpmath" in modes:
        t7()
    if "p0" in modes:
        t8()
    with open(RECEIPT, "a") as f:
        f.write("\nTALLY: %d FAIL(s)%s\n" % (len(FAILS), (" -- " + ", ".join(FAILS)) if FAILS else ""))
    print("TALLY: %d FAIL(s)%s" % (len(FAILS), (" -- " + ", ".join(FAILS)) if FAILS else ""),
          flush=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
