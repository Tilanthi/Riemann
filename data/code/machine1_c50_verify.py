#!/usr/bin/env python3
"""machine1 verifier for m2 cycle-50 (commits 3ea026b + 4ad47d3 + correction ddf0172).

Independent re-derivation at primary of every scored figure in the c50 results letter,
from the committed cell bytes only. Where the letter quotes a figure, this script
recomputes it from data/c50/c46_block_*.json (and the published data/c46 cells) with
exact-arithmetic comparisons (trap #156: comparisons of wide artefacts are exact).
Exit code = number of failed checks.
"""
import json, glob, os, subprocess, sys
from decimal import Decimal, getcontext

getcontext().prec = 250
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
C50 = os.path.join(REPO, "data", "c50")
C46 = os.path.join(REPO, "data", "c46")

fails = []
def check(name, ok, detail=""):
    print("%-72s %s%s" % (name, "PASS" if ok else "FAIL", ("  " + detail) if detail else ""))
    if not ok:
        fails.append(name)

def ritz(fp):
    return json.load(open(fp))["ritz"]

def lam_of(r):
    """lam_full where the cell has it (c48-storage cells), else the 60-s.f. print field
    (published c46 cells predate the storage fix; agreement then caps at print width)."""
    return Decimal(r["lam_full"] if "lam_full" in r else r["lam"])

def kept_log10(fp):
    """log10_full of rungs passing the registered admission rule (rel resid < 1e-20),
    where rel = residual / lam (the scorer's normalization, scores.out max_rel_resid)."""
    out = []
    for r in ritz(fp):
        lam, res = Decimal(r["lam_full"]), Decimal(r["residual_full"] if "residual_full" in r else r["residual"])
        if lam != 0 and abs(res / lam) < Decimal("1e-20"):
            out.append(Decimal(r["log10_full"]))
    return out

QA = Decimal("0.9206571015")

# ---------- P0: new-cell lambda_1 vs published k3 lambda_1, >= 30 s.f. ----------
def agreeing_sf(a, b):
    sa, sb = f"{a:e}", f"{b:e}"
    da, db = sa.split("e"), sb.split("e")
    if da[1] != db[1]:
        return 0
    da, db = da[0].replace("-", "").replace(".", ""), db[0].replace("-", "").replace(".", "")
    n = 0
    for x, y in zip(da, db):
        if x != y:
            break
        n += 1
    return n

pairs = [
    ("x13_N100_dps150_g9_it16_k5",  "x13_N100_dps150_g9_it16_k3"),
    ("x5_N100_dps150_g9_it16_k5",   None),   # published run_cell cells, different name
    ("x19_N100_dps300_g9_it16_k3",  None),
    ("x13_N180_dps150_g9_it16_k3",  None),
]
pub_run = {"x5":  ("c46_even_x5_N100_dps150_g9_it16.json",  "c46_odd_x5_N100_dps150_g9_it16.json"),
           "x19": ("c46_even_x19_N100_dps300_g9_it16.json", "c46_odd_x19_N100_dps300_g9_it16.json"),
           "x13_180": ("c46_even_x13_N180_dps150_g9_it16.json", "c46_odd_x13_N180_dps150_g9_it16.json")}
depths = []
for par in ("even", "odd"):
    for stem, k3 in pairs:
        fp = os.path.join(C50, f"c46_block_{par}_{stem}.json")
        new1 = lam_of(ritz(fp)[0])
        if k3:
            pub = lam_of(ritz(os.path.join(C46, f"c46_block_{par}_{k3}.json"))[0])
        else:
            key = "x13_180" if "N180" in stem else ("x19" if "x19" in stem else "x5")
            pub = Decimal(json.load(open(os.path.join(C46, pub_run[key][0 if par == "even" else 1])))["lambda_min"])
        sf = agreeing_sf(new1, pub)
        depths.append(sf)
        check(f"P0  {par:>4} {stem[:24]:>24} lam1 vs published  >=30 s.f.", sf >= 30, f"({sf} s.f.)")

# k=5 ladder vs published k=3 ladder (6 values)
ev5 = [lam_of(r) for r in ritz(os.path.join(C50, "c46_block_even_x13_N100_dps150_g9_it16_k5.json"))][:3]
od5 = [lam_of(r) for r in ritz(os.path.join(C50, "c46_block_odd_x13_N100_dps150_g9_it16_k5.json"))][:3]
ev3 = [lam_of(r) for r in ritz(os.path.join(C46, "c46_block_even_x13_N100_dps150_g9_it16_k3.json"))]
od3 = [lam_of(r) for r in ritz(os.path.join(C46, "c46_block_odd_x13_N100_dps150_g9_it16_k3.json"))]
worst = min(agreeing_sf(a, b) for a, b in zip(ev5 + od5, ev3 + od3))
check("P0  k=5 calibration ladder vs published k=3 (6 values)", worst >= 30, f"(worst {worst} s.f.)")

# ---------- P1: alternation + riders + certificate ----------
certs, orders = {}, {}
for stem in ("x13_N100_dps150_g9_it16_k5", "x13_N180_dps150_g9_it16_k3",
             "x19_N100_dps300_g9_it16_k3", "x5_N100_dps150_g9_it16_k5"):
    le = kept_log10(os.path.join(C50, f"c46_block_even_{stem}.json"))
    lo = kept_log10(os.path.join(C50, f"c46_block_odd_{stem}.json"))
    pooled = sorted(le + lo)
    order = ("e" if len(le) else "")  # placeholder, rebuild below
    seq = []
    for v in pooled:
        seq.append("e" if v in le else "o")
    # careful: equal values across sectors impossible here (gaps > 1 dex)
    T = min(le[-1], lo[-1]) if False else min(max(le), max(lo))
    # T must be in log10 space too
    Tlog = min(le[-1], lo[-1])
    prefix = sum(1 for v in pooled if v <= Tlog)
    certs[stem] = prefix
    orders[stem] = "".join(seq)
    gaps = [pooled[i + 1] - pooled[i] for i in range(len(pooled) - 1)]
    check(f"P1  {stem[:26]:>26} alternates", seq == ["e", "o"] * (len(seq) // 2) + (["e"] if len(seq) % 2 else []), f"({''.join(seq)})")
    check(f"P1  {stem[:26]:>26} min pooled gap > 1 dex", min(gaps) > 1, f"({min(gaps):.4f})")

check("P1  certificate prefixes 9/5/5/6 (x13k5/x13N180/x19/x5)",
      [certs[s] for s in ("x13_N100_dps150_g9_it16_k5", "x13_N180_dps150_g9_it16_k3",
                          "x19_N100_dps300_g9_it16_k3", "x5_N100_dps150_g9_it16_k5")] == [9, 5, 5, 6],
      str([certs[s] for s in certs]))

# x=5 drop rule: 3 of 10, max rel resid 3.6e-3, lam ~0.606
dropped, maxrel, lam06 = 0, Decimal(0), Decimal(0)
for par in ("even", "odd"):
    for r in ritz(os.path.join(C50, f"c46_block_{par}_x5_N100_dps150_g9_it16_k5.json")):
        lam, res = Decimal(r["lam_full"]), Decimal(r["residual"])
        rel = abs(res / lam)
        if rel >= Decimal("1e-20"):
            dropped += 1
            if rel > maxrel:
                maxrel, lam06 = rel, lam
check("P1  x=5 drop rule: 3 dropped", dropped == 3, f"({dropped})")
check("P1  x=5 max dropped rel residual = 3.6e-3", abs(maxrel - Decimal("0.0036395")) < Decimal("2e-6"), f"({maxrel:.4e})")
lamdropped = [Decimal(r["lam_full"]) for par in ("even", "odd")
              for r in ritz(os.path.join(C50, f"c46_block_{par}_x5_N100_dps150_g9_it16_k5.json"))
              if abs(Decimal(r["residual"]) / Decimal(r["lam_full"])) >= Decimal("1e-20")]
near06 = any(Decimal("0.60") < v < Decimal("0.61") for v in lamdropped)
check("P1  x=5 an off-ladder rung at lam ~0.606 (even[5])", near06, f"({[f'{v:.4f}' for v in lamdropped]})")

# ---------- P2/P3: q1 at 4 points, A residuals, B's x=5 sign ----------
def q1_of(stem):
    le = kept_log10(os.path.join(C50, f"c46_block_even_{stem}.json"))
    lo = kept_log10(os.path.join(C50, f"c46_block_odd_{stem}.json"))
    pooled = sorted(le + lo)
    return (pooled[2] - pooled[1]) / (pooled[1] - pooled[0])

q5, q13 = q1_of("x5_N100_dps150_g9_it16_k5"), q1_of("x13_N100_dps150_g9_it16_k5")
q13N, q19 = q1_of("x13_N180_dps150_g9_it16_k3"), q1_of("x19_N100_dps300_g9_it16_k3")
check("P2  q1 x=5   = 0.889256615305", abs(q5 - Decimal("0.889256615305")) < Decimal("5e-12"), f"({q5:.12f})")
check("P2  q1 x=13  = 0.920657101471", abs(q13 - Decimal("0.920657101471")) < Decimal("5e-12"), f"({q13:.12f})")
check("P2  q1 x=13N180 = 0.916933080206", abs(q13N - Decimal("0.916933080206")) < Decimal("5e-12"), f"({q13N:.12f})")
check("P2  q1 x=19  = 0.931062954397", abs(q19 - Decimal("0.931062954397")) < Decimal("5e-12"), f"({q19:.12f})")
check("P2  A residuals -0.031400 / -2.9e-11 / -0.003724 / +0.010406",
      abs((q5 - QA) + Decimal("0.031400")) < Decimal("5e-7") and abs((q13N - QA) + Decimal("0.003724")) < Decimal("5e-7")
      and abs((q19 - QA) - Decimal("0.010406")) < Decimal("5e-7"),
      f"({q5-QA:+.6f} / {q13N-QA:+.6f} / {q19-QA:+.6f})")
check("P2  A residual sign change through calibration (x5<0, x19>0)", (q5 - QA) < 0 < (q19 - QA))

# B's x=5 prediction from F(n) = 2 pi^2 n / ln n
import math
F = lambda n: 2 * math.pi ** 2 * n / math.log(n)
g1b, g2b = (F(6) - F(4)) / math.log(10), (F(8) - F(6)) / math.log(10)
qB = g2b / g1b
check("P3  model B q1(x=5) predicted > 1 (recomputed from F)", qB > 1, f"({qB:.5f})")
check("P3  measured q1(x=5) < 1 -> B dead by sign", q5 < 1, f"({q5:.6f})")
check("P3  |q1-1| = 0.1107 (the knife-edge distance, letter 8b)", abs(abs(q5 - 1) - Decimal("0.1107")) < Decimal("1e-4"), f"({abs(q5-1):.4f})")

# ---------- P4: N-stability ----------
s1 = lambda stem: (lambda le: le[1] - le[0])(kept_log10(os.path.join(C50, f"c46_block_even_{stem}.json")))
ds1 = s1("x13_N180_dps150_g9_it16_k3") - s1("x13_N100_dps150_g9_it16_k5")
check("P4  |ds1| = 0.00215 <= 0.15 (interval held)", abs(ds1) <= Decimal("0.15"), f"({ds1:+.6f})")
check("P4  ds1 sign NEGATIVE (predicted positive -> consequence applied)", ds1 < 0, f"({ds1:+.6f})")

# ---------- P5 ----------
for stem, want in (("x5_N100_dps150_g9_it16_k5", "5.11e5"), ("x13_N100_dps150_g9_it16_k5", "3.92e7"),
                   ("x13_N180_dps150_g9_it16_k3", "3.90e7"), ("x19_N100_dps300_g9_it16_k3", "1.60e8")):
    le = kept_log10(os.path.join(C50, f"c46_block_even_{stem}.json"))
    ratio = Decimal(10) ** (le[1] - le[0])
    w = Decimal(want.replace("e", "E"))
    check(f"P5  lam2/lam1 {stem[:22]:>22} ~ {want}", abs(ratio / w - 1) < Decimal("0.005"), f"({ratio:.3e})")

# ---------- P6 ----------
le = kept_log10(os.path.join(C50, "c46_block_even_x13_N100_dps150_g9_it16_k5.json"))
lo = kept_log10(os.path.join(C50, "c46_block_odd_x13_N100_dps150_g9_it16_k5.json"))
pooled = sorted(le + lo)
gaps = [pooled[i + 1] - pooled[i] for i in range(len(pooled) - 1)]
q7 = gaps[7] / gaps[6]
check("P6  gaps stop decreasing at j=8 (REFUTED as letter says)",
      gaps[7] > gaps[6], f"(gap7={gaps[6]:.5f} gap8={gaps[7]:.5f})")
check("P6  q7 = 1.02526", abs(q7 - Decimal("1.02526")) < Decimal("5e-6"), f"({q7:.5f})")
Tlog = min(le[-1], lo[-1])
check("P6  rungs 7-9 inside certified prefix 9", all(pooled[i] <= Tlog for i in (6, 7, 8)))

# ---------- the exact identity ----------
for stem in ("x13_N100_dps150_g9_it16_k5", "x13_N180_dps150_g9_it16_k3",
             "x19_N100_dps300_g9_it16_k3", "x5_N100_dps150_g9_it16_k5"):
    le = kept_log10(os.path.join(C50, f"c46_block_even_{stem}.json"))
    lo = kept_log10(os.path.join(C50, f"c46_block_odd_{stem}.json"))
    pooled = sorted(le + lo)
    lhs = (pooled[1] - pooled[0]) + (pooled[2] - pooled[1])
    check(f"ID  gap1+gap2 == s1 EXACT  {stem[:24]:>24}", lhs == le[1] - le[0])

# ---------- x-drift vs N-drift ----------
nmove = abs(q13N - q13)
check("x-drift = 2.8-8.4x the N-drift",
      Decimal("2.7") < abs(q5 - q13) / nmove < Decimal("8.5") and Decimal("2.7") < abs(q19 - q13) / nmove < Decimal("8.5"),
      f"({abs(q5-q13)/nmove:.2f}x, {abs(q19-q13)/nmove:.2f}x)")

# ---------- nodal arm (unregistered; inspection level) ----------
nodal = {"even": json.load(open(os.path.join(C50, "m2_c50_nodes_even_x13_N100.json"))),
         "odd":  json.load(open(os.path.join(C50, "m2_c50_nodes_odd_x13_N100.json")))}
allstable = all(r["stable"] for par in nodal for r in nodal[par]["rungs"])
counts = {par: [r["counts"]["1201_0.0"] for r in nodal[par]["rungs"]] for par in ("even", "odd")}
seq = [counts["even" if i % 2 == 0 else "odd"][i // 2] for i in range(10)]
disl = [seq[i] - i for i in range(10)]
check("NODAL  10/10 rungs stable across all 9 knob settings", allstable)
check("NODAL  exact for rungs 1-5 (nodes = rung-1)", disl[:5] == [0, 0, 0, 0, 0], str(seq[:5]))
check("NODAL  +2 dislocation from rung 6, +6 at rung 10 (15 nodes)", disl[5:] == [2, 2, 2, 2, 6], str(seq[5:]))
check("NODAL  every dislocation even (why alternation survives)", all(d % 2 == 0 for d in disl))
check("NODAL  node parity matches sector at every rung",
      all(seq[i] % 2 == (0 if i % 2 == 0 else 1) for i in range(10)))

# ---------- artefact hygiene ----------
out = subprocess.run(["git", "-C", REPO, "diff", "--stat", "995ecf7..ddf0172", "--", "data/c46", "data/c48"],
                     capture_output=True, text=True).stdout
check("HYG  data/c46 + data/c48 untouched 995ecf7..ddf0172", out.strip() == "")

import hashlib
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
check("HYG  sealed predict.out sha == seal entry 997f8066...",
      sha(os.path.join(C50, "m2_c50_predict.out")).startswith("997f80665c3b910a"))
erratum = open(os.path.join(REPO, "8211147020_2026-09-08T0736Z_machine2-c49-the-width-row-CLOSED-by-"
      "measurement-c48-ladder-depth-at-ALL-FIVE-rungs-not-two-a-band-that-passed-while-its-model-was-"
      "refuted-and-the-residue-published-as-a-COUNT.md")).read()
check("HYG  ERRATUM 26 marked on-the-line in c49 letter 7 (original preserved)",
      "ERRATUM 26" in erratum and "~~1.0–2.1" in erratum)

# ---------- the one slip ----------
p0out = open(os.path.join(C50, "m2_c50_p0_gate.out")).read()
gate40 = "40.0" in p0out.splitlines()[6] if len(p0out.splitlines()) > 6 else False
check("SLIP  committed gate .out says even x13 N180 = 40.0 (letter 2 table says 39.90)",
      gate40, "(finding: letter-vs-artefact transcription slip, immaterial)")

print()
print("RESULT: %d failed checks" % len(fails))
sys.exit(len(fails))
