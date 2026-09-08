#!/usr/bin/env python3
"""machine1_c52_verify.py — m1's adjudication verifier for machine2 cycle 52 (q_1 x-drift).

Run from any checkout of Tilanthi/Riemann:  python3 data/code/machine1_c52_verify.py
Receipts print to stdout; every tier ends PASS/FAIL; TALLY at the end.

Tiers:
  T0  seals + inventory + the post-seal v1->v2 edit (path-only, per prereg §7 + c50 rule)
  T1  launch discipline (prereg commit vs first-cell stamp)
  T2  grader regen from a FOREIGN copy of the tree (resolver cannot reach the author's tree
      from this Mac: /shared/... does not exist here, so HERE/../.. must resolve -- §11's cure)
  T3  my own q_1 recompute from the 70 committed cells (independent code path, mpmath dps 60
      on lam_full strings) + P0-equivalent vs c50's PUBLISHED values from c50's own cells
  T4  P1 order/cert-prefix; worst relative Ritz residual; rejected-rung census
  T5  the headline: 12-window N=100 series, P2a/P2b violations, N=60 reproduction,
      x=13 four-basis ladder (incl. c50's published N=180 cell), spreads, medians, R
  T6  P3a/P3b paired+conservative bands; P3b vs MY witness-re-derived sealed families
  T7  P4 isoresolution-vs-fixed-N sign table, spans, the tie census
  T8  P5 per-x verdicts at R/3
  T9  P6 three families (MY constants) x 9 blind points: bands, sign structure, sums
  T10 arm D (dps150/k5 vs dps300/k3 from committed cells, both sides mine) + cross-cycle
      x=19 determinism (lam_full string identity vs c50's committed pair)
  T11 P7 permutation null (my own RNG implementation, same seed) + the exact P2 nulls
No proof claim. Standing sentence unchanged: we have no route to a proof.
"""
import glob, hashlib, json, math, os, random, re, shutil, subprocess, sys, time
from mpmath import mp, mpf

mp.dps = 60
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
C52 = os.path.join(REPO, "data", "c52")
T0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
FAILS = []

def ck(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(name)

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

print(f"machine1_c52_verify.py  started {T0}  repo={REPO}")

# ---------------------------------------------------------------- T0 seals + inventory
print(f"\nTIER T0  seals, inventory, post-seal edit  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
seal = dict(reversed(l.split()) for l in open(os.path.join(C52, "m2_c52_seal.txt")).read().splitlines() if l.strip())
ck("seal: SEALED_v1 hash retained (seal certifies what was registered)",
   sha256(os.path.join(C52, "m2_c52_qdrift.SEALED_v1.py")) == seal["m2_c52_qdrift.py"],
   seal["m2_c52_qdrift.py"][:16])
ck("seal: grid.py", sha256(os.path.join(C52, "m2_c52_grid.py")) == seal["m2_c52_grid.py"])
ck("seal: prereg.md", sha256(os.path.join(C52, "m2_c52_prereg.md")) == seal["m2_c52_prereg.md"])
for rel, key in ((os.path.join("data", "c46", "c46_parity.py"), None),
                 (os.path.join("data", "c50", "m2_c50_ladder.py"), None)):
    h = sha256(os.path.join(REPO, rel))
    match = any(h == v for v in seal.values())
    ck(f"seal: local {rel.replace(os.sep, '/').split('/')[-1]} content-hash present in seal (import identity)", match)

v1 = open(os.path.join(C52, "m2_c52_qdrift.SEALED_v1.py")).read().splitlines()
v2 = open(os.path.join(C52, "m2_c52_qdrift.py")).read().splitlines()
diff_lines = [l for l in open(os.path.join(C52, "m2_c52_qdrift.v1_to_v2.diff")).read().splitlines()]
committed_body = [l for l in diff_lines[2:] if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
import difflib
mydiff = [l for l in difflib.unified_diff(v1, v2, lineterm="", n=2)
          if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
ck("post-seal edit: committed diff body == difflib(SEALED_v1, current)", committed_body == mydiff,
   f"{len(committed_body)} +/- lines")
def _fn_span(lines, name):
    start = next(i for i, l in enumerate(lines) if l.startswith(f"def {name}("))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("def ")), len(lines))
    return start, end

sp_v1, sp_v2 = _fn_span(v1, "_repo"), _fn_span(v2, "_repo")
body_v1 = set(l.rstrip() for l in v1[sp_v1[0]:sp_v1[1]])
body_v2 = set(l.rstrip() for l in v2[sp_v2[0]:sp_v2[1]])
removed_in_repo = all(l[1:].rstrip() in body_v1 for l in committed_body if l.startswith("-"))
added_in_repo = all(l[1:].rstrip() in body_v2 for l in committed_body if l.startswith("+"))
no_other_def = all("def " not in l[1:] for l in committed_body)
ck("post-seal edit: every changed line lives inside _repo() in its file; no def line touched",
   removed_in_repo and added_in_repo and no_other_def,
   f"removed->v1 span {removed_in_repo}, added->v2 span {added_in_repo}")

grid = [l.split("\t") for l in open(os.path.join(C52, "m2_c52_grid_cmds.tsv")).read().splitlines() if l.strip()]
cellnames = sorted(os.path.basename(p) for p in glob.glob(os.path.join(C52, "cells", "*.json")))
ck("grid: 70 registered cmds == 70 cells on disk, identical name sets",
   len(grid) == 70 and len(cellnames) == 70 and sorted(r[1] for r in grid) == cellnames)
XS = [4, 4.82, 4.86, 5, 5.23, 7, 9, 11, 13, 16, 19, 23]
NISO = {x: round(100 * math.log(x) / math.log(5)) for x in XS}
pairs = sorted({(float(r[2].split()[2]), int(r[2].split()[3])) for r in grid})
expect_pairs = sorted({(x, n) for x in XS for n in {60, 100, NISO[x]}})
ck("grid: 12 x {60,100,N_iso} dedup == 35 pairs == committed cmds; N_iso = round(100 log x/log 5)",
   pairs == expect_pairs and len(pairs) == 35, f"N_iso range {min(NISO.values())}-{max(NISO.values())}")

# ---------------------------------------------------------------- T1 launch discipline
print(f"\nTIER T1  launch discipline  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
commit_ts = subprocess.run(["git", "-C", REPO, "show", "-s", "--format=%cI", "ac8df53"],
                           capture_output=True, text=True).stdout.strip()
launch = open(os.path.join(C52, "logs", "LAUNCH.txt")).read().strip()
ck("prereg commit ac8df53 precedes first registered cell launch",
   commit_ts < launch.split()[1].replace("Z", ""), f"commit {commit_ts} < launch {launch.split()[1]}")
ck("prelaunch absence receipt: 70 names checked, ALREADY PRESENT: 2 (the disclosed c50 x19 pair)",
   "ALREADY PRESENT: 2" in open(os.path.join(C52, "m2_c52_prelaunch_absence.out")).read())

# ---------------------------------------------------------------- T2 grader regen, foreign copy
print(f"\nTIER T2  grader regen from a FOREIGN copy (this Mac has no /shared; resolver must use the copy)  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
TMP = "/tmp/c52_adj"
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(os.path.join(TMP, "data"), exist_ok=True)
for d in ("c46", "c50", "c52"):
    shutil.copytree(os.path.join(REPO, "data", d), os.path.join(TMP, "data", d))
ck("foreign copy built without the author's tree reachable", not os.path.exists("/shared/rh-exchange-repo"),
   "/shared absent on this Mac -> HERE/../.. = the copy, by structure")
for args, target in ((["--kat"], "m2_c52_kat.out"),
                     (["--score", "--cells", "cells"], "m2_c52_scores.out")):
    r = subprocess.run([sys.executable, "m2_c52_qdrift.py"] + args, cwd=os.path.join(TMP, "data", "c52"),
                       capture_output=True, text=True)
    mine = r.stdout
    theirs = open(os.path.join(C52, target)).read()
    ck(f"regen byte-identical: {target}", r.returncode == 0 and mine == theirs,
       f"rc={r.returncode} stderr_lines={len(r.stderr.splitlines())}")

# ---------------------------------------------------------------- T3 my own q_1 recompute
print(f"\nTIER T3  my own q_1 recompute from the 70 cells (independent path)  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")

RESID_RULE = mpf(10) ** (-20)

def _rungs(p):
    """per rung: (log10 float field, log10_full, admitted?, full-precision relative residual)"""
    return [(mpf(r["log10"]), mpf(r["log10_full"]),
             abs(mpf(r["residual"]) / mpf(r["lam"])) < RESID_RULE,
             abs(mpf(r["residual_full"]) / mpf(r["lam_full"])))
            for r in json.load(open(p))["ritz"]]

def pool52(even_p, odd_p, full=False):
    """MY transcription of the c50 pooling convention (m2_c50_ladder.pool/load_block):
    admission |res/lam| < 1e-20 per sector, pool on the log10 coordinate, q_1 = gap_2/gap_1,
    certified = #{merged <= min(last admitted of each side)}.  Every scored c52 number is a
    ratio/order/count in this coordinate, so a uniform scale on the field cannot move it."""
    ev = [r for r in _rungs(even_p) if r[2]]
    od = [r for r in _rungs(odd_p) if r[2]]
    ix = 1 if full else 0
    merged = sorted([(r[ix], "e") for r in ev] + [(r[ix], "o") for r in od])
    gaps = [merged[i + 1][0] - merged[i][0] for i in range(len(merged) - 1)]
    q1 = (gaps[1] / gaps[0]) if gaps[0] != 0 else None
    order = "".join(p for _, p in merged)
    cert = sum(1 for v, _ in merged if v <= min(ev[-1][ix], od[-1][ix]))
    return q1, order, cert

CP = {}
for p in glob.glob(os.path.join(C52, "cells", "*.json")):
    d = json.load(open(p))
    CP[(d["parity"], float(d["x"]), int(d["N"]))] = p
C50P = {}
for p in glob.glob(os.path.join(REPO, "data", "c50", "c46_block_*.json")):
    d = json.load(open(p))
    C50P[(d["parity"], float(d["x"]), int(d["N"]))] = p

def q13(x, N):
    return pool52(CP[("even", x, N)], CP[("odd", x, N)])

def fnum(m, nd=12):
    return float(mp.nstr(m, nd + 3))

score_rows = {}
for line in open(os.path.join(C52, "m2_c52_scores.out")):
    m = re.match(r"^(\d+(?:\.\d+)?)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+(0\.[\d]+)\s+(\w+)\s+(\d+)", line)
    if m:
        score_rows[(float(m.group(1)), int(m.group(2)))] = dict(n=int(m.group(3)), q1=float(m.group(5)),
                                                                order=m.group(6), cert=int(m.group(7)))
bad, worst_scale_dev = [], mpf(0)
for (x, N), ref in score_rows.items():
    q1, order, cert = q13(x, N)
    for lg, lgf, ok, _ in _rungs(CP[("even", x, N)]) + _rungs(CP[("odd", x, N)]):
        worst_scale_dev = max(worst_scale_dev, abs(lg / lgf - 10))
    if q1 is None or abs(float(q1) - ref["q1"]) > 1e-11 or order != ref["order"] or cert != ref["cert"]:
        bad.append((x, N))
ck("my transcription of the pooling rule reproduces all 35 rows exactly: q_1, order, cert",
   not bad, str(bad[:4]))
diffs = []
for (x, N) in score_rows:
    qf = pool52(CP[("even", x, N)], CP[("odd", x, N)], full=True)[0]
    diffs.append(abs(float(qf) - float(q13(x, N)[0])))
ck("float-field pooling == log10_full pooling to 1e-12 (float64 storage costs nothing at the 6th d.p.)",
   max(diffs) < 1e-12,
   f"worst {max(diffs):.2e}; float log10 field = 10x log10_full on every rung "
   f"(max deviation {mp.nstr(worst_scale_dev, 3)} -- uniform scale, inert for ratios/orders/cert)")

# P0-equivalent: c50's own committed cells -> the three published values (their P0 dps/k mapping)
pub = {5.0: ("0.889256615305", 150, 5), 13.0: ("0.9206571015", 150, 5), 19.0: ("0.931062954", 300, 3)}
p0bad = []
for x, (want, dps, k) in pub.items():
    pe, po = C50P[("even", x, 100)], C50P[("odd", x, 100)]
    de = json.load(open(pe))
    if de["dps"] != dps or de["k"] != k:
        p0bad.append((x, "cell dps/k", de["dps"], de["k"]))
        continue
    q1, order, cert = pool52(pe, po)
    got = float(mp.nstr(q1, 15))
    tol = 0.5 * 10 ** (-(len(want.split(".")[1]) - 1))
    if abs(got - float(want)) > tol or cert < 3:
        p0bad.append((x, got, want))
ck("P0-equivalent: my transcription on c50's committed cells reproduces the 3 PUBLISHED q_1",
   not p0bad, str(p0bad))
# and identity of c50's cells with the c52 re-run pair is checked in T10

# ---------------------------------------------------------------- T4 P1 + residual floor
print(f"\nTIER T4  P1 order/cert; residual floor; rejected rungs  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
p1bad = [k for k, ref in score_rows.items() if not ref["order"].startswith("eoe") or ref["cert"] < 3]
ck("P1: pooled order starts 'eoe' and certified prefix >= 3 at all 35", not p1bad, str(p1bad))
certs = {k: ref["cert"] for k, ref in score_rows.items()}
ck("cert column: 5 everywhere except x=4 (residual rule drops one; printed as 4)",
   all(v == (4 if k[0] == 4.0 else 5) for k, v in certs.items()), f"{sorted(set(certs.values()))}")
adm = rej = 0; worst_adm = worst_rej = mpf(0)
for p in glob.glob(os.path.join(C52, "cells", "*.json")):
    for _, _, ok, relf in _rungs(p):
        if ok:
            adm += 1; worst_adm = max(worst_adm, relf)
        else:
            rej += 1; worst_rej = max(worst_rej, relf)
ck("numerical floor: worst relative Ritz residual over ADMITTED rungs <= 4.78e-36; exactly 3 rejected",
   worst_adm <= mpf("4.78e-36") and rej == 3,
   f"admitted {adm} (letter says 195), rejected {rej}, worst admitted {mp.nstr(worst_adm, 3)}, "
   f"worst rejected {mp.nstr(worst_rej, 3)}")

# ---------------------------------------------------------------- T5 the headline
print(f"\nTIER T5  headline series, P2a/P2b, N=60, x=13 ladder, spreads  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
qN = {x: score_rows[(x, 100)]["q1"] for x in XS}
letter_tab = [0.875226, 0.881370, 0.867591, 0.889257, 0.897548, 0.913980, 0.927164, 0.931024,
              0.920657, 0.928296, 0.931063, 0.942862]
ck("letter table: my 12 N=100 q_1 values match to 6 d.p.", all(abs(qN[x] - t) <= 5e-7 for x, t in zip(XS, letter_tab)))
def steps(xs):
    return [(xs[i], xs[i + 1], qN[xs[i + 1]] - qN[xs[i]]) for i in range(len(xs) - 1)]
viol = [(a, b, d) for a, b, d in steps(XS) if d <= 0]
ck("P2a: exactly 2 violating pairs, 4.82->4.86 (-0.013779) and 11->13 (-0.010367)",
   len(viol) == 2 and abs(viol[0][2] + 0.013779) < 2e-6 and abs(viol[1][2] + 0.010367) < 2e-6,
   str([(a, b, round(d, 6)) for a, b, d in viol]))
COARSE = [4, 5, 7, 9, 11, 13, 16, 19, 23]
violc = [(a, b, d) for a, b, d in steps(COARSE) if d <= 0]
ck("P2b coarse-9: exactly 1 violating pair (11->13)", len(violc) == 1 and violc[0][:2] == (11, 13))
q60 = {x: score_rows[(x, 60)]["q1"] for x in XS}
v60 = {(XS[i], XS[i + 1]): q60[XS[i + 1]] - q60[XS[i]] for i in range(11)}
v60v = [(a, b, d) for (a, b), d in v60.items() if d <= 0]
ck("both N=100 violations REPRODUCE at N=60 with the stated magnitudes (letter claims reproduction, not exclusivity)",
   abs(v60[(4.82, 4.86)] + 0.016270) < 2e-6 and abs(v60[(11, 13)] + 0.010775) < 2e-6,
   f"all N=60 violating pairs in their own committed data: {[(a, b, round(d, 6)) for a, b, d in v60v]}")
def SN(x, na=100, nb=60):
    return score_rows[(x, na)]["q1"] - score_rows[(x, nb)]["q1"]
ck("|Delta S_N| at the two violating pairs ~ 0.0025 / 0.00041 (not truncation flutter at one basis)",
   abs(abs(SN(4.82) - SN(4.86)) - 0.0025) < 1e-3 and abs(abs(SN(11) - SN(13)) - 0.00041) < 2e-4,
   f"{abs(SN(4.82)-SN(4.86)):.5f} {abs(SN(11)-SN(13)):.5f}")
lad = [score_rows[(13.0, n)]["q1"] for n in (60, 100, 159)]
lad.append(float(pool52(C50P[("even", 13.0, 180)], C50P[("odd", 13.0, 180)])[0]))
want_lad = [0.926250, 0.920657, 0.925005, 0.916933]
ck("x=13 four-basis ladder 0.926250/0.920657/0.925005/0.916933 (180 = c50's published cell, mine)",
   all(abs(a - b) <= 5e-7 for a, b in zip(lad, want_lad)) and lad[0] > lad[1] < lad[2] > lad[3],
   str([round(v, 6) for v in lad]))
R = max(qN.values()) - min(qN.values())
ck("total N=100 range R = 0.075271", abs(R - 0.075271) < 2e-6, f"{R:.7f}")
sn_abs = [abs(SN(x)) for x in XS]
med_SN = sorted(sn_abs)[5] + sorted(sn_abs)[6] / 2  # placeholder replaced below
med_SN = (sorted(sn_abs)[5] + sorted(sn_abs)[6]) / 2
lsteps = sorted(abs(d) for _, _, d in steps(XS))
med_step = lsteps[5]
ck("median local step to next x = 0.010367 (the |11->13| magnitude)", abs(med_step - 0.010367) < 2e-6,
   f"{med_step:.6f}")
nsp = {}
for x in XS:
    qs = [score_rows[(x, n)]["q1"] for n in sorted({60, 100, NISO[x]})]
    if x == 13.0:   # their S3 ladder: x=13 carries the 4th basis (c50's N=180 cell)
        qs.append(float(pool52(C50P[("even", 13.0, 180)], C50P[("odd", 13.0, 180)])[0]))
    nsp[x] = max(qs) - min(qs)
nsl = {}
for line in open(os.path.join(C52, "m2_c52_nspread.out")):
    m = re.match(r"^(\d+(?:\.\d+)?)\s+N=([\d,]+)\s+([\d.]+)", line)
    if m:
        nsl[float(m.group(1))] = (float(m.group(3)), m.group(2))
srt = sorted(nsp.values())
ck("S3 per-x N-ladder spreads: all 12 match nspread.out (x=13 4-point incl N=180); "
   "median 0.019101 (upper-median convention), max 0.028078 at x=5",
   all(abs(nsp[x] - nsl[x][0]) < 2e-6 for x in XS) and "180" in nsl[13.0][1]
   and abs(srt[6] - 0.019101) < 2e-6 and abs(nsp[5.0] - 0.028078) < 2e-6,
   f"upper-median {srt[6]:.6f} (low-median {(srt[5]+srt[6])/2:.6f}) max {nsp[5.0]:.6f}")

# ---------------------------------------------------------------- T6 P3a/P3b
print(f"\nTIER T6  P3a/P3b bands; sealed families (MY witness constants)  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
def paired_band(xa, xb):
    return 3 * abs(SN(xa) - SN(xb))
def conservative_band(xa, xb):
    return 3 * max(abs(SN(xa)), abs(SN(xb)))
p3 = {("4.86", "5.23"): 0.029957459, ("4.82", "4.86"): -0.013779285}
for (a, b), want in (("4.86", "5.23"), 0.029957459), (("4.82", "4.86"), -0.013779285):
    dq = qN[float(b)] - qN[float(a)]
    pb, cb = paired_band(float(a), float(b)), conservative_band(float(a), float(b))
    ck(f"P3 pair {a}->{b}: dq={dq:+.6f} paired {pb:.6f} conservative {cb:.6f}",
       abs(dq - want) < 2e-6 and (abs(dq) > pb if (a, b) == ("4.86", "5.23") else True))
sub = [(qN[5.0] - qN[4.86], paired_band(4.86, 5.0)), (qN[5.23] - qN[5.0], paired_band(5.0, 5.23))]
ck("sub-pairs 4.86->5 (+0.021666/0.026931) and 5->5.23 (+0.008292/0.028251) each INSIDE; sum pair 22.7x OUTSIDE",
   abs(sub[0][0] - 0.021666) < 2e-6 and abs(sub[0][1] - 0.026931) < 2e-6
   and abs(sub[1][0] - 0.008292) < 2e-6 and abs(sub[1][1] - 0.028251) < 2e-6
   and sub[0][0] < sub[0][1] and sub[1][0] < sub[1][1]
   and abs(0.029957459 / paired_band(4.86, 5.23) - 22.7) < 0.1,
   f"ratio {0.029957459/paired_band(4.86, 5.23):.1f}x")
# MY families, re-derived in the witness note from the 3 published points (log-log LS)
NX = {4: 3, 4.82: 3, 4.86: 4, 5: 4, 5.23: 4, 7: 8, 9: 12, 11: 16, 13: 21, 16: 29, 19: 38, 23: 50}
FAM = {"F_x": (0.195941845, -0.353887747, lambda x: x),
       "F_L": (0.160254056, -0.767130019, lambda x: math.log(x)),
       "F_n": (0.148240440, -0.208506978, lambda x: NX[x])}
def fam_pred(f, x):
    A, beta, u = FAM[f]      # beta stored WITH its sign (witness-note convention: q1 = 1 - A*u^beta)
    return 1 - A * u(x) ** beta
d_p3b = qN[4.86] - qN[4.82]
preds = {f: fam_pred(f, 4.86) - fam_pred(f, 4.82) for f in FAM}
ck("P3b: measured -0.013779 vs MY sealed-family deltas F_n +0.006864 / F_x +0.000328 / F_L +0.000454",
   all(abs(preds[f] - w) < 2e-6 for f, w in (("F_n", 0.006864), ("F_x", 0.000328), ("F_L", 0.000454)))
   and d_p3b < 0,
   " ".join(f"{f}:{preds[f]:+.6f}" for f in FAM))
fac = {f: abs(d_p3b) / preds[f] for f in FAM}
ck("all three wrong in SIGN; the SMOOTH families (F_x, F_L) off by 30-42x (letter's exact scope; F_n is 2x)",
   all(preds[f] > 0 for f in FAM) and d_p3b < 0
   and 29 <= fac["F_x"] <= 43 and 29 <= fac["F_L"] <= 43,
   f"F_x {fac['F_x']:.1f}x, F_L {fac['F_L']:.1f}x, F_n {fac['F_n']:.1f}x")

# ---------------------------------------------------------------- T7 P4
print(f"\nTIER T7  P4 isoresolution vs fixed-N  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
iso = {x: score_rows[(x, NISO[x])]["q1"] for x in XS}
disagree, ties, minabs = [], 0, (None, 1e9)
for i in range(11):
    a, b = XS[i], XS[i + 1]
    d1, d2 = qN[b] - qN[a], iso[b] - iso[a]
    for d, s in ((d1, "fixedN"), (d2, "iso")):
        if d == 0:
            ties += 1
        elif abs(d) < minabs[1]:
            minabs = ((s, a, b), abs(d))
    if (d1 > 0) != (d2 > 0):
        disagree.append((a, b))
span_iso, span_fix = iso[23] - iso[4], qN[23] - qN[4]   # their print convention: last - first
ck("P4: 9 of 11 sign agreements; disagreements exactly at 7->9 and 16->19",
   len(disagree) == 2 and disagree == [(7, 9), (16, 19)], str(disagree))
ck("P4 spans (endpoint drift q1(23)-q1(4), their convention): iso 0.068032 vs fixed-N 0.067636",
   abs(span_iso - 0.068032) < 2e-6 and abs(span_fix - 0.067636) < 2e-6, f"{span_iso:.6f} {span_fix:.6f}")
ck("tie census: zero exact ties; min |dq_1| = 0.0027668 at fixedN 16->19 (addendum's measurement)",
   ties == 0 and minabs[0] == ("fixedN", 16, 19) and abs(minabs[1] - 0.0027668) < 2e-7,
   f"{minabs[0]} {minabs[1]:.7f}")

# ---------------------------------------------------------------- T8 P5
print(f"\nTIER T8  P5 per-x confound verdicts  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
verdicts = {x: ("CONFOUNDED" if abs(SN(x)) > R / 3 else "CLEAN") for x in XS}
conf = [x for x, v in verdicts.items() if v == "CONFOUNDED"]
ck("P5: 11 CLEAN + exactly x=5 CONFOUNDED at R/3 (no UNMEASURED: all tiers complete)",
   conf == [5.0] and abs(R / 3 - 0.0250902) < 2e-6, f"R/3={R/3:.7f} conf={conf}")

# ---------------------------------------------------------------- T9 P6
print(f"\nTIER T9  P6 three families x 9 blind points (MY constants)  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
CAL = {5.0, 13.0, 19.0}
blind = [x for x in XS if x not in CAL]
sums, allin, signstrings = {}, True, {}
for f in FAM:
    resid = []
    for x in XS:
        r = qN[x] - fam_pred(f, x)
        resid.append((x, r))
        if x not in CAL and abs(r) > 3 * abs(SN(x)):
            allin = False
    blindres = [r for x, r in resid if x not in CAL]
    sums[f] = sum(abs(r) for r in blindres)
    signstrings[f] = "".join("-" if r < 0 else "+" for r in blindres)
ck("all three families: 9 of 9 blind points inside 3|S_N| (the unanimous pass = broken band)",
   allin, str({f: round(sums[f], 6) for f in FAM}))
ck("sums |resid| (blind): 0.091914 / 0.080556 / 0.087477; best = F_L",
   abs(sums["F_x"] - 0.091914) < 2e-5 and abs(sums["F_L"] - 0.080556) < 2e-5 and abs(sums["F_n"] - 0.087477) < 2e-5)
ck("blind residual signs: all three '---++++++' — ONE sign change through calibration (c50's refutation shape)",
   all(s == "---++++++" for s in signstrings.values()), str(signstrings))
maxband = max(3 * abs(SN(x)) for x in blind)
ck("the registered band cannot fail: widest blind 3|S_N| = 0.0648 (calibration x=5: 0.0842) vs total range 0.0753",
   abs(maxband - 0.0648) < 2e-4 and abs(3 * abs(SN(5.0)) - 0.0842) < 2e-4 and maxband > 0.85 * R,
   f"widest blind {maxband:.4f}, x=5 band {3*abs(SN(5.0)):.4f}, R {R:.4f}")

# ---------------------------------------------------------------- T10 arm D + cross-cycle x19
print(f"\nTIER T10  arm D + cross-cycle determinism  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
q_dps150 = pool52(C50P[("even", 13.0, 100)], C50P[("odd", 13.0, 100)])[0]
q_dps300 = q13(13.0, 100)[0]
ck("arm D from committed cells, both sides MY pooling: k5@dps150 == k3@dps300 == published "
   "0.9206571014709472604304785 (exact mpf equality, 25 s.f.)",
   q_dps150 == q_dps300 and mp.nstr(q_dps300, 25) == "0.9206571014709472604304785",
   f"mine {mp.nstr(q_dps150, 26)}")
x19_same = []
for par in ("even", "odd"):
    a = json.load(open(CP[(par, 19.0, 100)]))
    b = json.load(open(C50P[(par, 19.0, 100)]))
    x19_same.append([r1["lam_full"] == r2["lam_full"] for r1, r2 in zip(a["ritz"], b["ritz"])])
ck("cross-cycle x=19: lam_full literals identical to c50's committed pair, every rung, both parities",
   all(all(row) for row in x19_same), f"{sum(map(len, x19_same))} literals compared")

# ---------------------------------------------------------------- T11 P7 nulls
print(f"\nTIER T11  P7 permutation null (my implementation, same seed) + exact P2 nulls  [{time.strftime('%H:%M:%SZ', time.gmtime())}]")
predL = [fam_pred("F_L", x) for x in XS if x not in CAL]      # their null: shuffle the NINE blind values only
meas = [qN[x] for x in XS if x not in CAL]
obs = sum(abs(m - p) for m, p in zip(meas, predL))
rng = random.Random(20260908)
cnt = 0
for _ in range(20000):
    perm = meas[:]
    rng.shuffle(perm)
    if sum(abs(m - p) for m, p in zip(perm, predL)) <= obs:
        cnt += 1
ck("P7 my null (blind-9 shuffle, their construction, my constants): 2 of 20000 -> p = 1.0e-4",
   cnt == 2, f"mine {cnt}/20000 obs {obs:.6f}")
ck("exact nulls printed at 4 s.f.: 1/12! = 2.088e-9 and 1/9! = 2.756e-6 (P2a/P2b permutation p)",
   abs(1 / math.factorial(12) - 2.088e-9) < 1e-12 and abs(1 / math.factorial(9) - 2.756e-6) < 5e-10)

print(f"\nTALLY: {len(FAILS)} FAIL(s)" + (": " + "; ".join(FAILS) if FAILS else ""))
print(f"machine1_c52_verify.py  finished {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
sys.exit(1 if FAILS else 0)
