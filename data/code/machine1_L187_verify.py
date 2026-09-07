#!/usr/bin/env python3
"""m1-L187 primary verification of m3-L185 (parity N->inf extrapolation).

Inputs are the FULL printed ladders from m3's committed SUMMARY.md
(data/code/m3_L184_build/results/SUMMARY.md) and m2's committed 60-s.f. JSON
literals (data/c46/c46_odd_x13_N100_dps150_g9_it16.json, ..._N140_...).
Every number below is READ from those artifacts (trap #151), not recalled.

Checks:
  G1  gate N=100: m3 value vs m2 JSON literal -> exact relative difference
  G2  gate N=140: digit agreement m3 vs m2 printed value
  G3  finite-N gaps log10(odd/even) at N=100/140/180/220
  G4  odd decay ratios N140/N100, N180/N140, N220/N180
  G5  Aitken (Delta^2) per triple, ratio-to-N100, both blocks
  G6  Richardson (1/N, two-point) on all 6 matched pairs: gap in dex
"""
import json
from decimal import Decimal, getcontext

getcontext().prec = 80

# --- ladders, read from SUMMARY.md (m3, commit 59b515a) ---
odd = {
    100: Decimal("3.34107742032073965658213712601992236254413410378763387206214e-55"),
    140: Decimal("2.8475156913393636771563703939938140057126090742267e-55"),
    180: Decimal("2.698009778782749686608210255746078258440609181395e-55"),
    220: Decimal("2.5322446138126329379067665416656277722374006147654e-55"),
}
even = {
    100: Decimal("3.720899741667123935791434766094540694091e-59"),
    140: Decimal("3.191618722904299187775878951533394940265e-59"),
    180: Decimal("2.959706807240060045108126519806894301792e-59"),
    220: Decimal("2.833656431009356898926062340578180078197e-59"),
}
# m3's N=100 gate print (39 s.f., identical text to m2's ritz[0] print in c46_runs.out)
m3_gate100 = Decimal("3.341077420320739656582137126019922362544e-55")
# m2's committed 30-s.f. N=140 print (c46_runs.out r2_odd_13_N140.log)
m2_print140 = "2.84751569133936367715637039399e-55"

def log10d(x):
    # Decimal log10 via ln: use Python float for the log of a Decimal Mantissa
    return Decimal(str(float(x.log10()))) if hasattr(x, "log10") else None

print("=== G1: gate N=100 vs m2 60-s.f. JSON literal ===")
with open("data/c46/c46_odd_x13_N100_dps150_g9_it16.json") as f:
    j = json.load(f)
m2_lit = j["lambda_min"]  # the 60-s.f. stored literal (NOT the _30 print)
print(f"  json field 'lambda_min'  : {m2_lit}")
print(f"  json field 'lambda_min_30': {j.get('lambda_min_30')}")
m2_val = Decimal(m2_lit)
reld = abs(m3_gate100 - m2_val) / m2_val
print(f"  m3 gate value  : {m3_gate100}")
print(f"  m2 json literal: {m2_lit}")
print(f"  |gate39 diff|/val = {reld:.6e}   (vs the 30-s.f. print; claimed 1.34e-60 is vs the 60-s.f. literal)")
# the real check: m3's committed ladder value vs m2's 60-s.f. stored literal, as strings
ladder_str = "3.34107742032073965658213712601992236254413410378763387206214e-55"
print(f"  ladder N100 string == m2 lambda_min string: {ladder_str == m2_lit}")
m2_full = Decimal(m2_lit)
print(f"  ladder N100 vs m2 60sf literal: rel diff = {abs(odd[100] - m2_full)/m2_full:.6e}")
print("  -> the 1.34e-60 claim measures m3's INTERNAL dps-150 tail vs m2's rounded")
print("     59-s.f. literal (a digit-60 difference); cross-machine agreement depth")
print("     from committed prints = 59 s.f. exactly (string identity), per c43 law.")

print("=== G2: gate N=140 digit agreement ===")
s140 = format(odd[100 + 40], "e")  # placeholder, real check below
s140 = "2.8475156913393636771563703939938140057126090742267e-55"
print(f"  m3 N140 starts: {s140[:34]}")
print(f"  m2 print (30sf): {m2_print140}")
agree = s140.startswith(m2_print140[:len(m2_print140) - 4])  # strip 'e-55'
print(f"  m2's 30 printed digits are a prefix of m3's value: {agree}")

print("=== G3: finite-N gaps log10(odd/even) ===")
import math
gaps = {}
for n in (100, 140, 180, 220):
    r = float(odd[n] / even[n])
    g = math.log10(r)
    gaps[n] = g
    print(f"  N={n}: {g:.9f}")

print("=== G4: odd decay ratios ===")
for a, b in ((100, 140), (140, 180), (180, 220)):
    print(f"  N{b}/N{a} = {float(odd[b]/odd[a]):.6f}")

print("=== G5: Aitken per triple (ratio of extrapolate to N=100) ===")
def aitken(t):
    a, b, c = t
    return c - (c - b) ** 2 / (c - 2 * b + a)
for name, d in (("even", even), ("odd", odd)):
    for trip in ((100, 140, 180), (140, 180, 220)):
        ext = aitken(tuple(d[n] for n in trip))
        print(f"  {name} {trip}: extrap = {ext:.6e}  ratio-to-N100 = {float(ext/d[100]):.6f}")

print("=== G6: Richardson 1/N two-point, 6 matched pairs ===")
g100 = gaps[100]
res = []
for na, nb in ((180, 220), (140, 220), (100, 220), (140, 180), (100, 180), (100, 140)):
    eo = (nb * odd[nb] - na * odd[na]) / (nb - na)
    ee = (nb * even[nb] - na * even[na]) / (nb - na)
    ro = float(eo / odd[100]); re_ = float(ee / even[100])
    gap_inf = g100 + math.log10(ro / re_)
    res.append(gap_inf)
    print(f"  ({na},{nb}): odd_ratio={ro:.4f} even_ratio={re_:.4f} gap_inf={gap_inf:.4f}")
print(f"  exact range over 6 pairs: {min(res):.4f} .. {max(res):.4f}")
print("  m3 SUMMARY table gaps: 3.897 3.953 3.951 4.014 3.965 3.938; letter range 3.90-4.01")

print("=== G7: Aitken cross-gap (one usable odd triple vs even triples) ===")
oa = float(aitken(tuple(odd[n] for n in (100, 140, 180))))
for trip in ((100, 140, 180), (140, 180, 220)):
    ea = float(aitken(tuple(even[n] for n in trip)))
    print(f"  odd(100,140,180) vs even{trip}: gap = {math.log10(oa/ea):.4f}")
