"""machine2 CYCLE 34 -- scoring: P-A / P-B / P-C, and the DOMINANCE test.

Reads c34_refit.json (produced by the frozen m2_c34_refit.py) and answers, in order:

  P-A  does the shift land where c33's sensitivity said?
       measured  raw(A, refined centre) - raw(Alit, literal centre)
       predicted S_k * (D*_refined - D*_literal),  S from c33's three-pipeline-run FD
       (and, independently, from this run's free series-shift route).
       Pass: every coefficient within a factor 2.

  P-B  what is the floor AFTER the substitution?
       raw floor  = max_config spread of the RAW coefficients at the refined centre
       rec floor  = max_config spread of the RECENTRED coefficients
       Pass (P-B as filed): the limiting error lands at 1e-45 or COARSER.

  P-C  does G(0,0) stop being config-invariant?
       In c33 it printed -1.41253e-35 in all four configs.  Here: does it move, and with
       WHICH knob?  A term that moves with no knob is the instrument printing its own floor.

  DOMINANCE  for each pair of configs, the implied centre shift delta_k = Delta_k / S_k.
       Five numbers that must agree iff the difference is entirely a centre-channel effect.
       Calibration from the synthetic dry-run (T5): a pure centre shift gives spread 1.000,
       a purely instrumental error (g[1][0] perturbed) gives spread 4.79.
"""
import json
import os
import sys

import mpmath as mp

mp.mp.dps = 120

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["a", "b", "a3", "a4", "a5"]
REFINED = mp.mpf("0.14173323966388719139541568508418502362314456195501665594286660394665904218970743")
LITERAL = mp.mpf("0.141733239663887191395415685084185024")
# c33's sensitivity, measured there by three full pipeline runs at D* and D* +- 1e-25
S_C33 = {"a": mp.mpf("-42.6418612841"), "b": mp.mpf("452.708172669"),
         "a3": mp.mpf("-2123.16726697"), "a4": mp.mpf("6698.97547725"),
         "a5": mp.mpf("-16819.9239728")}

R = {d["label"]: d for d in json.load(open(os.path.join(HERE, "c34_refit.json")))}
have = list(R)
print("configs present:", have)
S = {nm: mp.mpf(R["A"]["sens"][nm]) for nm in NAMES}

print("\n" + "=" * 92)
print("P-C  G(0,0) across configs -- in c33 this printed -1.41253e-35 in ALL FOUR configs")
print("=" * 92)
print(f"  {'cfg':6s} {'N_w':>4s} {'r_w':>6s} {'npts':>5s} {'h_e':>5s} {'dps':>4s}   "
      f"{'G(0,0)':>26s}   {'(2 r_w)^N_w':>12s}  ratio")
for lab in have:
    c, g00 = R[lab]["cfg"], mp.mpf(R[lab]["g00"])
    law = (2 * mp.mpf(c["r_w"])) ** c["N_w"]
    print(f"  {lab:6s} {c['N_w']:4d} {c['r_w']:>6s} {c['npts']:5d} "
          f"1e-{c['he']:<3d} {c['dps']:4d}   {mp.nstr(g00, 12):>26s}   "
          f"{mp.nstr(law, 6):>12s}  {mp.nstr(g00 / law, 6)}")

print("\n" + "=" * 92)
print("P-A  the shift, measured on ONE code path (cfg A knobs, refined vs literal centre)")
print("=" * 92)
dD = REFINED - LITERAL
print(f"  D*_refined - D*_literal = {mp.nstr(dD, 10)}")
if "Alit" in R:
    print(f"  {'':4s} {'measured shift':>22s} {'predicted (c33 S)':>22s} {'ratio':>10s}   "
          f"{'predicted (c34 free S)':>24s} {'ratio':>10s}")
    for nm in NAMES:
        meas = mp.mpf(R["A"]["raw"][nm]) - mp.mpf(R["Alit"]["raw"][nm])
        p33 = S_C33[nm] * dD
        p34 = S[nm] * dD
        print(f"  {nm:>4s} {mp.nstr(meas, 10):>22s} {mp.nstr(p33, 10):>22s} "
              f"{mp.nstr(meas / p33, 8):>10s}   {mp.nstr(p34, 10):>24s} "
              f"{mp.nstr(meas / p34, 8):>10s}")
    print("\n  and the SAME comparison on the RECENTRED coefficients (must be ~0: the")
    print("  self-centring is supposed to make the answer independent of the centre used):")
    for nm in NAMES:
        d = mp.mpf(R["A"]["rec"][nm]) - mp.mpf(R["Alit"]["rec"][nm])
        print(f"  {nm:>4s} rec(refined) - rec(literal) = {mp.nstr(d, 8)}")

print("\n" + "=" * 92)
print("P-B / DOMINANCE  cross-config spreads, RAW vs RECENTRED, at the refined centre")
print("=" * 92)
ref = sys.argv[1] if len(sys.argv) > 1 else "A"
others = [l for l in have if l not in (ref, "Alit")]
for kind in ("raw", "rec"):
    print(f"\n  --- {kind.upper()} coefficients, differences against cfg {ref} ---")
    print(f"  {'cfg':6s} " + " ".join(f"{nm:>13s}" for nm in NAMES)
          + "   | implied centre shift delta_k = Delta_k/S_k, and its spread")
    for lab in others:
        D_ = [mp.mpf(R[lab][kind][nm]) - mp.mpf(R[ref][kind][nm]) for nm in NAMES]
        dk = [D_[i] / S[NAMES[i]] for i in range(5)]
        nz = [abs(v) for v in dk if v != 0]
        spread = (max(nz) / min(nz)) if len(nz) == 5 else mp.inf
        print(f"  {lab:6s} " + " ".join(f"{mp.nstr(v, 4):>13s}" for v in D_)
              + f"   | dk ~ {mp.nstr(sum(dk) / 5, 5)}  spread {mp.nstr(spread, 5)}")
    mx = mp.mpf(0)
    for i, nm in enumerate(NAMES):
        vals = [mp.mpf(R[l][kind][nm]) for l in have if l != "Alit"]
        mx = max(mx, max(vals) - min(vals))
    print(f"  => max spread over all configs, all five coefficients: {mp.nstr(mx, 6)}")

print("\n" + "=" * 92)
print("The centre channel, isolated: each config's OWN determination of D*")
print("=" * 92)
for lab in have:
    if lab == "Alit":
        c = LITERAL
    else:
        c = REFINED
    impl = c - mp.mpf(R[lab]["et"])
    print(f"  {lab:6s} implied D* - D*_refined = {mp.nstr(impl - REFINED, 8):>16s}   "
          f"(x S_a = {mp.nstr((impl - REFINED) * S['a'], 6)} in `a`)")

print("\n" + "=" * 92)
print("PAIRWISE among the configs whose aliasing is dead (the floor of the BEST answers)")
print("=" * 92)
good = [l for l in have if l not in ("A", "Alit", "P17", "H6", "H8", "Q125")]
for kind in ("raw", "rec"):
    print(f"  --- {kind.upper()} ---")
    for i, x in enumerate(good):
        for y in good[i + 1:]:
            d = [mp.mpf(R[x][kind][nm]) - mp.mpf(R[y][kind][nm]) for nm in NAMES]
            dk = [d[j] / S[NAMES[j]] for j in range(5)]
            nz = [abs(v) for v in dk if v != 0]
            sp = (max(nz) / min(nz)) if len(nz) == 5 else mp.inf
            print(f"  {x:5s} - {y:5s}  " + " ".join(f"{mp.nstr(v,4):>13s}" for v in d)
                  + f"   | dk ~ {mp.nstr(sum(dk)/5,4)} spread {mp.nstr(sp,4)}")
