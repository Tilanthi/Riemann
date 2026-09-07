#!/usr/bin/env python3
"""
machine2 cycle 39 -- the producing script for ERRATUM 19's reading-form numbers.

FILED BECAUSE OUR OWN LINT CAUGHT US.  m2_c39_lint_widths.py, on its first run over the real
corpus, classified `1.48742188420142330184348e-152` and `4.8742188420142330184348e-153` --
published in machine2-ERRATUM-19-* and in commit 6181e51 -- as UNBACKED: 24 and 23 significant
figures with no committed artefact behind them.  They were computed in an interactive session and
typed into the letter, which is exactly the B1/B2 defect the boundary register describes.  This
script is the artefact; running it converts both literals from UNBACKED to EXEMPT.

Inputs are two strings already committed in this repository:
  * the 175 s.f. serialisation of D*      -- data/machine2_c36_dstar_175.txt
  * the certified accuracy 2.3209072e-152 -- same file (|eps(R6)| / |f'(D*)|)
No evaluator is called and no run is performed; this is exact decimal arithmetic on committed text.
"""
import os
import re
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

getcontext().prec = 400
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(R, "data", "machine2_c36_dstar_175.txt")

txt = open(SRC).read()
m = re.search(r"D\* = (0\.\d+)", txt)
full = Decimal(m.group(1))
acc = Decimal(re.search(r"CERTIFIED ACCURACY\s*:\s*([0-9.eE+-]+)", txt).group(1))

sf_full = len(m.group(1).split(".")[1].lstrip("0"))
rel = acc / full
print(f"source                : {os.path.relpath(SRC, R)}")
print(f"serialised width      : {sf_full} s.f.")
print(f"certified accuracy    : {acc} absolute")
print(f"  relative            : {rel:.7e}")
print(f"  supported s.f.      : {-rel.log10():.3f}   <-- '~151' is this, rounded UP")
print()
print(f"{'width':>6} {'departure from the 175 s.f. string':>42} {'half-ulp':>12} {'total vs true D*':>26}")
for k in (151, 152):
    r = full.quantize(Decimal(1).scaleb(-k), rounding=ROUND_HALF_EVEN)
    dep = abs(full - r)
    half = Decimal(5).scaleb(-(k + 1))
    print(f"{k:>6} {str(dep.normalize()):>42} {str(half):>12} {str((acc+dep).normalize()):>26}")
    print(f"       {r}")
print()
print("VERDICT: a reading form printed AT the certified width (151) has a half-ulp 2.2x LARGER than")
print("the accuracy it carries; at 152 the print is no longer the binding term.  LAW: print the")
print("reading form at least one digit WIDER than the certified width.")
