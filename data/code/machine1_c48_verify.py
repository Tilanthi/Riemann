#!/usr/bin/env python3
"""m1 primary verification of machine2-c48 + ERRATUM 25 (commit 1fb3a8c).

All inputs read from committed artefacts (trap #151). Checks:
  W1  sha256 of data/c47/c47_prereg.md  -> d48f6008...
  W2  three truncation reconstructions  -> 5b87557d / caa485f4 / 09a61958
  W3  corpus scan: does 6709efed appear as a file hash anywhere?
  W4  D2 recovery depth, MY OWN count: dps150 _full vs dps220 _full
  W5  non-movement: c48 print fields byte-equal to frozen c46 cells
  W6  _full digit count (claimed 154) + _exact->{man,2^exp} sanity
  W7  the 1.34e-60 reproduction from print width alone
  W8  census denominators from the committed .tsv
"""
import hashlib
import json
import re
import subprocess
from decimal import Decimal, getcontext

getcontext().prec = 400
EX = "/Users/gjw255/astrodata/SWARM/Riemann_exchange"

print("=== W1/W2: ERRATUM 25 hashes ===")
raw = open(f"{EX}/data/c47/c47_prereg.md", "rb").read()
h = lambda b: hashlib.sha256(b).hexdigest()
print(f"  file as committed : {h(raw)[:16]}...  (claimed d48f6008...)")
cut = raw.split(b"## ADDENDUM 1")[0]
print(f"  trunc @ ADDENDUM 1: {h(cut)[:16]}...  (claimed 5b87557d...)")
stripped = cut.rstrip()
print(f"  trunc rstrip      : {h(stripped)[:16]}...  (claimed 09a61958...)")
print(f"  trunc rstrip + \\n : {h(stripped + b'\\n')[:16]}...  (claimed caa485f4...)")

print("=== W3: 6709efed in the corpus ===")
r = subprocess.run(["grep", "-rl", "6709efed", f"{EX}", "--exclude-dir=.git"],
                   capture_output=True, text=True)
files = [l.split("/")[-1][:60] for l in r.stdout.strip().splitlines() if l]
print(f"  {len(files)} files: {files}")

print("=== W4: D2 recovery depth (MY count, dps150 _full vs dps220 _full) ===")
def agree(a: str, b: str):
    # count agreeing significant digits of two decimal sci strings
    def sci(s):
        m, e = s.split("e")
        return m.replace(".", "").lstrip("0"), int(e)
    ma, ea = sci(a); mb, eb = sci(b)
    if ea != eb:
        return 0, abs(int(ea) - int(eb))
    n = 0
    for x, y in zip(ma, mb):
        if x != y:
            break
        n += 1
    return n, 0

for name, n in (("odd", 60), ("odd", 100), ("even", 60), ("even", 100)):
    lo = json.load(open(f"{EX}/data/c48/c48_{name}_x13_N{n}_dps150_g9_it16.json"))
    hi = json.load(open(f"{EX}/data/c48/c48_{name}_x13_N{n}_dps220_g9_it16.json"))
    d, _ = agree(lo["lambda_min_full"], hi["lambda_min_full"])
    print(f"  {name} N={n}: my count = {d} s.f.   (c48 claims "
          f"{ {'even60':92.66,'even100':92.22,'odd60':95.81,'odd100':95.40}[f'{name}{n}'] })")

print("=== W5: non-movement, c48 print fields vs frozen c46 cells ===")
for name in ("odd", "even"):
    for n in (60, 100, 140, 180, 220):
        c48 = json.load(open(f"{EX}/data/c48/c48_{name}_x13_N{n}_dps150_g9_it16.json"))
        c46 = json.load(open(f"{EX}/data/c46/c46_{name}_x13_N{n}_dps150_g9_it16.json"))
        same = all(c48.get(k) == c46.get(k) for k in ("lambda_min", "lambda_min_30"))
        new = [k for k in c48 if k not in c46]
        print(f"  {name} N={n}: print fields byte-identical: {same}; new fields: {new}")

print("=== W6: _full width + _exact sanity ===")
j = json.load(open(f"{EX}/data/c48/c48_odd_x13_N100_dps150_g9_it16.json"))
full = j["lambda_min_full"]
print(f"  _full: {full[:40]}...e{full.split('e')[1]}")
print(f"  _full sig digits: {len(full.split('e')[0].replace('.', ''))}  (claimed 154)")
ex = j["lambda_min_exact"]
man, ep = int(ex["man"]), int(ex["exp"])
val = Decimal(man) * Decimal(2) ** ep
ratio = val / Decimal(full)
print(f"  _exact man bits: {man.bit_length()} (claimed 502); prec={ex['prec']}")
print(f"  _exact/_full = {ratio}  (== 1 within stored precision?)")

print("=== W7: 1.34e-60 from print width alone ===")
lo60 = Decimal(j["lambda_min"])                      # frozen 60-s.f. print
hi = json.load(open(f"{EX}/data/c48/c48_odd_x13_N100_dps220_g9_it16.json"))
hi_full = Decimal(hi["lambda_min_full"])
rel = abs(lo60 - hi_full) / hi_full
print(f"  |60sf - dps220|/dps220 = {float(rel):.4e}   (m3 published 1.34e-60)")
print(f"  ratio to 1.34e-60      = {float(rel)/1.34e-60:.6f}  (c48 claims 0.996744)")
lo_full = Decimal(full)
rel2 = abs(lo_full - hi_full) / hi_full
print(f"  |c48full - dps220|/    = {float(rel2):.4e}   (c48 claims 3.99e-96)")

print("=== W8: census denominators ===")
tsv = open(f"{EX}/data/c48/m2_c48_storage_census.tsv").read().splitlines()
hdr = tsv[0].split("\t")
print(f"  header: {hdr}")
rows = [l.split("\t") for l in tsv[1:] if l.strip()]
print(f"  artefact rows: {len(rows)}")
col = {k: i for i, k in enumerate(hdr)}
if "retains_full" in col:
    ret = sum(1 for r in rows if r[col["retains_full"]] in ("True", "true", "1"))
    print(f"  retaining full precision: {ret}  (census claims 15)")
