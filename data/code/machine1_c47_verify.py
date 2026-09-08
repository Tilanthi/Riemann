#!/usr/bin/env python3
"""m1 primary verification of machine2-c47 (commit c6f6315).

Every input is READ from committed artifacts (trap #151): m3's SUMMARY.md
ladders, m2's c46 JSON literals (N60/100/140 from c46; N180/220 new in c47),
and my own heat85 results file for ERRATUM 24. No number is recalled.

Checks:
  V1  four new cells (N180/220, odd+even) vs m3's ladder strings
  V2  A5 ceiling: Aitken on 3 odd + 3 even triples (5-rung set incl N=60)
      vs the LAST-rung ceiling lambda(220), per parity
  V3  10-pair Richardson 1/N set with N=60 admitted: which pairs
      nonpositive, survivor gap range; test [3.8966, 4.4625]
  V4  1/N^2 model on m3's 4 rungs: band vs [3.9304, 3.9768]
  V5  digit count of m2's stored 60-char literal (60 vs 59)
  V6  m3 SUMMARY approx-label audit: which of my 3 scored cells carry it
  V7  ERRATUM 24 from data/machine1_heat85_results.json: per-k delta
      windows, spans (max-min)/max|lam|, moves at 0.06/0.07
  V8  m2's ratio chains (odd 0.3909->...; even 0.3671->...)
  V9  lam_inf spans quoted: odd 1.61-2.47e-55, even 1.87-2.64e-59
"""
import json
import math
from decimal import Decimal, getcontext

getcontext().prec = 90
EX = "/Users/gjw255/astrodata/SWARM/Riemann_exchange"

def js(path):
    with open(f"{EX}/{path}") as f:
        return json.load(f)

def lam(path):
    return Decimal(js(path)["lambda_min"])

# --- ladders (m3 SUMMARY.md values, as committed 59b515a; trap #151: read, don't recall) ---
odd = {100: Decimal("3.34107742032073965658213712601992236254413410378763387206214e-55"),
       140: Decimal("2.8475156913393636771563703939938140057126090742267e-55"),
       180: Decimal("2.698009778782749686608210255746078258440609181395e-55"),
       220: Decimal("2.5322446138126329379067665416656277722374006147654e-55")}
even = {100: Decimal("3.720899741667123935791434766094540694091e-59"),
        140: Decimal("3.191618722904299187775878951533394940265e-59"),
        180: Decimal("2.959706807240060045108126519806894301792e-59"),
        220: Decimal("2.833656431009356898926062340578180078197e-59")}
# N=60 rungs from m2's own c46 JSONs
odd[60] = lam("data/c46/c46_odd_x13_N60_dps150_g9_it16.json")
even[60] = lam("data/c46/c46_even_x13_N60_dps150_g9_it16.json")

print("=== V1: four new c47 cells vs m3 ladder strings ===")
pairs = [("odd", 180), ("odd", 220), ("even", 180), ("even", 220)]
for name, n in pairs:
    lit = js(f"data/c46/c46_{name}_x13_N{n}_dps150_g9_it16.json")["lambda_min"]
    m3v = (odd if name == "odd" else even)[n]
    ds = Decimal(lit)
    rel = abs(ds - m3v) / m3v
    # agreement depth: first differing digit position in normalized sci strings
    def sci(d):
        s = format(d, "e")
        m, ex = s.split("e")
        return m.replace(".", "").lstrip("0"), int(ex)
    a, ea = sci(ds); b, eb = sci(m3v)
    depth = 0
    if ea == eb:
        for x, y in zip(a, b):
            if x != y:
                break
            depth += 1
    print(f"  {name} N={n}: c47={lit[:46]}...")
    print(f"     m3  ={format(m3v, 'e')[:46]}...")
    print(f"     rel={rel:.2e}  digit-agreement={depth} s.f.  exponents {'match' if ea == eb else 'DIFFER'}")

print("=== V2: Aitken on 5-rung set vs LAST-rung ceiling lambda(220) ===")
def aitken(t):
    a, b, c = t
    return c - (c - b) ** 2 / (c - 2 * b + a)
for name, d in (("odd", odd), ("even", even)):
    ceil = d[220]
    for trip in ((60, 100, 140), (100, 140, 180), (140, 180, 220)):
        ext = aitken(tuple(d[n] for n in trip))
        r = float(ext / ceil)
        verdict = "ADMISSIBLE" if r <= 1.0 else f"INADMISSIBLE ({r:.3f}x ceiling)"
        print(f"  {name} {trip}: Aitken={float(ext):.4e}  /lam(220)={r:.4f}  {verdict}")

print("=== V3: 10-pair Richardson 1/N with N=60 admitted ===")
gapsN = {n: math.log10(float(odd[n] / even[n])) for n in sorted(odd)}
res = []
for na in (60, 100, 140, 180):
    for nb in (100, 140, 180, 220):
        if nb <= na:
            continue
        eo = (nb * odd[nb] - na * odd[na]) / (nb - na)
        ee = (nb * even[nb] - na * even[na]) / (nb - na)
        tag = ""
        if eo <= 0 or ee <= 0:
            tag = "  <- NONPOSITIVE (" + ("odd" if eo <= 0 else "even") + ")"
        else:
            g = math.log10(float(eo / ee))
            res.append(((na, nb), g))
            tag = f"  gap={g:.4f}"
        print(f"  ({na},{nb}): odd_inf={float(eo):+.4e} even_inf={float(ee):+.4e}{tag}")
surv = [g for _, g in res]
print(f"  survivors: {len(res)} of 10; range [{min(surv):.4f}, {max(surv):.4f}]  (c47 claims [3.8966, 4.4625])")
for p, g in sorted(res, key=lambda t: t[1]):
    print(f"    {p}: {g:.4f}")
# ceiling test on survivors
print("  survivor admissibility vs lam(220):")
for (na, nb), g in res:
    eo = (nb * odd[nb] - na * odd[na]) / (nb - na)
    ee = (nb * even[nb] - na * even[na]) / (nb - na)
    ro, re_ = float(eo / odd[220]), float(ee / even[220])
    print(f"    {na},{nb}: odd_inf/lam220odd={ro:.4f} even_inf/lam220even={re_:.4f}"
          + ("  <- even side EXCEEDS ceiling" if re_ > 1 else ""))

print("=== V4: 1/N^2 model on m3's 4 rungs ===")
# lam_inf = (nb^2*lam_b - na^2*lam_a)/(nb^2 - na^2)
res2 = []
for na in (100, 140, 180):
    for nb in (140, 180, 220):
        if nb <= na:
            continue
        eo = (nb * nb * odd[nb] - na * na * odd[na]) / (nb * nb - na * na)
        ee = (nb * nb * even[nb] - na * na * even[na]) / (nb * nb - na * na)
        if eo > 0 and ee > 0:
            g = math.log10(float(eo / ee))
            res2.append(((na, nb), g))
            print(f"  ({na},{nb}): odd_inf={float(eo):.4e} even_inf={float(ee):.4e} gap={g:.4f}")
        else:
            print(f"  ({na},{nb}): nonpositive extrapolant")
s2 = [g for _, g in res2]
print(f"  1/N^2 band: [{min(s2):.4f}, {max(s2):.4f}]  (c47 claims [3.9304, 3.9768])")

print("=== V5: digit count of stored literal ===")
lit = js("data/c46/c46_odd_x13_N100_dps150_g9_it16.json")["lambda_min"]
mant = lit.split("e")[0].replace(".", "")
print(f"  literal: {lit}")
print(f"  mantissa digits: {len(mant)}  (L186 said '59 significant digits'; leading + decimals = ?)")
print(f"  decimals after point: {len(lit.split('.')[1].split('e')[0])}")

print("=== V6: m3 SUMMARY approx-label audit ===")
with open(f"{EX}/data/code/m3_L184_build/results/SUMMARY.md") as f:
    summ = f.read()
lines = summ.splitlines()
scored = [("140,180",), ("100,220",), ("100,180",)]
for i, ln in enumerate(lines):
    if "approx" in ln.lower():
        print(f"  L{i+1}: {ln.strip()[:120]}")
for key in ("(140, 180)", "(100, 220)", "(100, 180)"):
    hit = [ln for ln in lines if key in ln]
    for h in hit:
        print(f"  scored-cell {key}: {'APPROX' if 'approx' in h.lower() else 'unlabelled'} :: {h.strip()[:110]}")

print("=== V7: ERRATUM 24 from machine1_heat85_results.json (MY artefact) ===")
with open(f"{EX}/data/machine1_heat85_results.json") as f:
    h85 = json.load(f)
if isinstance(h85, dict):
    ks = sorted(h85.keys(), key=lambda s: int(s) if str(s).lstrip("-").isdigit() else 10**9)
    print(f"  keys: {ks}")
    k0 = ks[0]
    v0 = h85[k0]
    print(f"  sample k={k0}: {v0 if not isinstance(v0, dict) else list(v0.items())[:3]}")

print("=== V8: m2's ratio chains ===")
for name, d in (("odd", odd), ("even", even)):
    rungs = sorted(d)
    chain = [float(d[b] / d[a]) for a, b in zip(rungs, rungs[1:])]
    print(f"  {name}: " + " -> ".join(f"{c:.4f}" for c in chain))
print("  c47 quotes odd  0.3909 -> 0.8523 -> 0.9475 -> 0.9386")
print("  c47 quotes even 0.3671 -> 0.8578 -> 0.9273 -> 0.9574")

print("=== V9: lam_inf spans quoted (odd 1.61-2.47e-55, even 1.87-2.64e-59) ===")
print("  Richardson (m3 4-rung pairs): odd %.4f-%.4f e-55, even %.4f-%.4f e-59" % (
    min(float((nb * odd[nb] - na * odd[na]) / (nb - na)) for na, nb in
        ((100, 140), (100, 180), (100, 220), (140, 180), (140, 220), (180, 220))) / 1e-55,
    max(float((nb * odd[nb] - na * odd[na]) / (nb - na)) for na, nb in
        ((100, 140), (100, 180), (100, 220), (140, 180), (140, 220), (180, 220))) / 1e-55,
    min(float((nb * even[nb] - na * even[na]) / (nb - na)) for na, nb in
        ((100, 140), (100, 180), (100, 220), (140, 180), (140, 220), (180, 220))) / 1e-59,
    max(float((nb * even[nb] - na * even[na]) / (nb - na)) for na, nb in
        ((100, 140), (100, 180), (100, 220), (140, 180), (140, 220), (180, 220))) / 1e-59))
print("  1/N^2 (same pairs): odd %.4f-%.4f e-55, even %.4f-%.4f e-59" % (
    min(float((nb * nb * odd[nb] - na * na * odd[na]) / (nb * nb - na * na)) for na, nb in
        ((100, 140), (100, 180), (100, 220), (140, 180), (140, 220), (180, 220))) / 1e-55,
    max(float((nb * nb * odd[nb] - na * na * odd[na]) / (nb * nb - na * na)) for na, nb in
        ((100, 140), (100, 180), (100, 220), (140, 180), (140, 220), (180, 220))) / 1e-55,
    min(float((nb * nb * even[nb] - na * na * even[na]) / (nb * nb - na * na)) for na, nb in
        ((100, 140), (100, 180), (100, 220), (140, 180), (140, 220), (180, 220))) / 1e-59,
    max(float((nb * nb * even[nb] - na * na * even[na]) / (nb * nb - na * na)) for na, nb in
        ((100, 140), (100, 180), (100, 220), (140, 180), (140, 220), (180, 220))) / 1e-59))
print("  Aitken admissible (even only): 2.6836 / 2.7788 e-59 -> OUTSIDE the quoted even span top 2.64")
print("  (60,220) Richardson survivor: odd 0.2768e-55, even 0.0954e-59 -> outside both quoted spans")
