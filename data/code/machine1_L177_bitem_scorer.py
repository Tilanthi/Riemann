#!/usr/bin/env python3
"""m1-L177 deferred-B-item scorer — scores B2/B4/B5/B6(+B1 echo) against the
COMPLETED v2 self-centring artefacts, exactly as the bands were filed at the
launch note a7e04cb (pre-compute) and re-posed by the v2 erratum a7e8675.

Reads (committed artefacts, read-only):
  data/machine1_L176_selfcentring_v2_r.json      (cfg R,  N_w=16)
  data/machine1_L176_selfcentring_v2_n64.json    (cfg N64, N_w=64)
  data/machine1_L176_selfcentring_v2_ab.json     (cfg A N_w=40, cfg B N_w=24, in order)

No band is edited here; every threshold is transcribed once and printed beside
its verdict (#123).  Parsing: mpmath complex strings "(-x + yj)" -> real part.
"""
import json
import os
from decimal import Decimal as D, getcontext

getcontext().prec = 80
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, ".."))


def creal(s):
    """Real part of an mpmath complex string (separator is space-padded, so an
    exponent's minus can never be mistaken for it)."""
    s = s.strip().strip("()").strip()
    if s.endswith("j"):
        i, j = s.rfind(" + "), s.rfind(" - ")
        s = s[:max(i, j)]
    return D(s)


def load(name, i=0):
    return json.load(open(os.path.join(DATA, name)))[i]


R = load("machine1_L176_selfcentring_v2_r.json")
N64 = load("machine1_L176_selfcentring_v2_n64.json")
AB = json.load(open(os.path.join(DATA, "machine1_L176_selfcentring_v2_ab.json")))
A, B = AB[0], AB[1]
assert (A["N_w"], B["N_w"]) == (40, 24), "A/B order changed"

# ---- the echo strings (published, ECHOED per the a7e04cb filing) -------------
M2_G10 = D("-14.16808467075497560605419228419387228304")
M2_ET = D("1.41852517093e-45")
B5_A4, B5_A5 = D("20.4755387553904"), D("18.2712")   # band centres (INFORMED, declared)

print("configs: R N_w=%d | A N_w=%d | B N_w=%d | N64 N_w=%d"
      % (R["N_w"], A["N_w"], B["N_w"], N64["N_w"]))

# ---- B6 clause-1 (registered FREE): c6(N64)/c6(R) within 1e-13 ----------------
cR, cN = creal(R["c6"]), creal(N64["c6"])
ratio = cN / cR
d = abs(ratio - 1)
print("\nB6-1  c6(R)   = %s" % cR)
print("      c6(N64) = %s" % cN)
print("      c6(N64)/c6(R) - 1 = %s  (band 1e-13) -> %s"
      % (d, "PASS" if d < D("1e-13") else "FAIL"))
print("      |c6(R)-c6(N64)|/|c6| = %s   [R-side alias scale (2*.05)^16 = 1e-16]"
      % (abs(cR - cN) / abs(cN)))
cA = creal(A["c6"])
print("      cross-check A: |c6(A)-c6(N64)|/|c6| = %s" % (abs(cA - cN) / abs(cN)))

# ---- B2: g-table head-to-head at cfg A ----------------------------------------
g10A, g01A = creal(A["g10"]), creal(A["g01"])
M2_G01 = D("-37.48197136084288173875936")
phi1 = abs(g10A) / abs(M2_G10)     # := |g10(m1)|/|g10(m2)|
phi2 = abs(g01A) / abs(M2_G01)     # := |g01(m1)|/|g01(m2)|
print("\nB2    raw g10(A) = %s" % g10A)
print("      raw g01(A) = %s" % g01A)
print("      phi1 := |g10(A)|/|g10(m2)| = %s" % phi1)
print("      phi2 := |g01(A)|/|g01(m2)| = %s" % phi2)
print("      phi entry gap = %s" % abs(phi1 - phi2))
print("      RAW band (rel<=1e-25): g10 rel = %s ; g01 rel = %s -> both FAIL at the SAME factor"
      % (abs(g10A - M2_G10) / abs(M2_G10), abs(g01A - M2_G01) / abs(M2_G01)))
# non-circular normalization: each entry divided by the OTHER entry's phi
cross10 = abs(g10A / phi2 - M2_G10) / abs(M2_G10)
cross01 = abs(g01A / phi1 - M2_G01) / abs(M2_G01)
print("      cross-normalized (g10 by phi2): rel = %s" % cross10)
print("      cross-normalized (g01 by phi1): rel = %s" % cross01)
PI = D("3.14159265358979323846264338327950288419716939937510582097494459")
et_ratio = abs(creal(A["etilde"])) / M2_ET
print("      B4 mechanistic cross-read: |et(A)|/|et(m2)| = %s" % et_ratio)
print("           vs pi*phi = %s  (rel %s)" % (PI * phi1, abs(et_ratio - PI * phi1) / (PI * phi1)))
print("           closure: (prefactor ratio pi*phi^2)/(g01 ratio phi) = pi*phi -> B4 miss = B1/B2 jointly")

# ---- B4: |etilde| clauses ------------------------------------------------------
etA, etB = abs(creal(A["etilde"])), abs(creal(B["etilde"]))
dA, dB = abs(creal(A["delta"])), abs(creal(B["delta"]))
print("\nB4    |et(A)| = %s   vs m2 %s  -> ratio %s (band [0.8,1.2])"
      % (etA, M2_ET, etA / M2_ET))
print("      free clause |et(B)|/|et(A)| = %s vs delta(B)/delta(A) = %s"
      % (etB / etA, dB / dA))
print("             ratio-of-ratios - 1 = %s  (band 5%%) -> %s"
      % ((etB / etA) / (dB / dA) - 1,
         "PASS" if abs((etB / etA) / (dB / dA) - 1) < D("0.05") else "FAIL"))

# ---- B5: a4/a5 at A, B, N64 (INFORMED bands, declared at filing) ---------------
print("\nB5    band a4 within 1e-3 of +20.4755387553904 ; a5 within 5e-3 of +18.2712")
for tag, c in (("A", A), ("B", B), ("N64", N64)):
    a4, a5 = creal(c["a4"]), creal(c["a5"])
    print("      %3s: a4 = %s  (rel %s)  %s ; a5 = %s  (rel %s)  %s"
          % (tag, a4, abs(a4 - B5_A4) / B5_A4,
             "PASS" if abs(a4 - B5_A4) / B5_A4 < D("1e-3") else "FAIL",
             a5, abs(a5 - B5_A5) / B5_A5,
             "PASS" if abs(a5 - B5_A5) / B5_A5 < D("5e-3") else "FAIL"))

# ---- even ladder (informational): rows j>=1 of g_table[.][0] := c_{2j}; row 0
# is the RAW g00 stencil entry, NOT delta (they coincide only where the alias
# term dominates: at N64 g00 = -1.876e-35 while delta = -2.2166e-63) -----------
print("\nladder (real parts, c_{2j} := g_table[j][0] for j>=1):")
for tag, c in (("R", R), ("A", A), ("B", B), ("N64", N64)):
    col = []
    for row in c["g_table"][1:]:
        col.append(creal(row[0]) if isinstance(row, list) else creal(row))
    print("      %-3s (%d harmonics): %s" % (tag, len(col), ", ".join(str(x) for x in col)))
print("      deltas: R %s | A %s | B %s | N64 %s"
      % (creal(R["delta"]), creal(A["delta"]), creal(B["delta"]), creal(N64["delta"])))


# ---- THIRD ROUTE: m2's closed forms (machine2-c35-extraction-spec-for-m3.md §3,
# from machine2_c35_signgroup.py::closed_forms) evaluated at MY g-table.
# My g[m][n] is differenced in eps=D-D* (spec: "difference in D directly"), so the
# spec-convention entry is (-1)^n * mine.  Every form is homogeneous of degree 0
# in the g's, so the phi normalization cancels identically -- no rescaling.
def closed_forms(g):
    """g: dict {(m,n): Decimal} in the SPEC convention. Returns (a,b,a3,a4,a5)."""
    G = lambda m, n: g.get((m, n), D(0))
    a = -G(0, 1) / G(1, 0)
    b = (-G(0, 1)**2 * G(2, 0) + G(0, 1) * G(1, 0) * G(1, 1) - G(0, 2) * G(1, 0)**2) / G(1, 0)**3
    a3 = (-2*G(0,1)**3*G(2,0)**2
          + G(0,1)**2*G(1,0)*(G(0,1)*G(3,0) + 3*G(1,1)*G(2,0))
          - G(0,1)*G(1,0)**2*(G(0,1)*G(2,1) + 2*G(0,2)*G(2,0) + G(1,1)**2)
          - G(0,3)*G(1,0)**4
          + G(1,0)**3*(G(0,1)*G(1,2) + G(0,2)*G(1,1))) / G(1,0)**5
    a4 = (-5*G(0,1)**4*G(2,0)**3
          + 5*G(0,1)**3*G(1,0)*G(2,0)*(G(0,1)*G(3,0) + 2*G(1,1)*G(2,0))
          - G(0,1)**2*G(1,0)**2*(G(0,1)**2*G(4,0) + 4*G(0,1)*G(1,1)*G(3,0)
                                 + 4*G(0,1)*G(2,0)*G(2,1) + 6*G(0,2)*G(2,0)**2
                                 + 6*G(1,1)**2*G(2,0))
          + G(0,1)*G(1,0)**3*(G(0,1)**2*G(3,1) + 3*G(0,1)*G(0,2)*G(3,0)
                              + 3*G(0,1)*G(1,1)*G(2,1) + 3*G(0,1)*G(1,2)*G(2,0)
                              + 6*G(0,2)*G(1,1)*G(2,0) + G(1,1)**3)
          - G(0,4)*G(1,0)**6
          + G(1,0)**5*(G(0,1)*G(1,3) + G(0,2)*G(1,2) + G(0,3)*G(1,1))
          - G(1,0)**4*(G(0,1)**2*G(2,2) + 2*G(0,1)*G(0,2)*G(2,1)
                       + 2*G(0,1)*G(0,3)*G(2,0) + 2*G(0,1)*G(1,1)*G(1,2)
                       + G(0,2)**2*G(2,0) + G(0,2)*G(1,1)**2)) / G(1,0)**7
    a5 = (-14*G(0,1)**5*G(2,0)**4
          + 7*G(0,1)**4*G(1,0)*G(2,0)**2*(3*G(0,1)*G(3,0) + 5*G(1,1)*G(2,0))
          - G(0,1)**3*G(1,0)**2*(6*G(0,1)**2*G(2,0)*G(4,0) + 3*G(0,1)**2*G(3,0)**2
                                 + 30*G(0,1)*G(1,1)*G(2,0)*G(3,0)
                                 + 15*G(0,1)*G(2,0)**2*G(2,1) + 20*G(0,2)*G(2,0)**3
                                 + 30*G(1,1)**2*G(2,0)**2)
          + G(0,1)**2*G(1,0)**3*(G(0,1)**3*G(5,0) + 5*G(0,1)**2*G(1,1)*G(4,0)
                                 + 5*G(0,1)**2*G(2,0)*G(3,1) + 5*G(0,1)**2*G(2,1)*G(3,0)
                                 + 20*G(0,1)*G(0,2)*G(2,0)*G(3,0)
                                 + 10*G(0,1)*G(1,1)**2*G(3,0)
                                 + 20*G(0,1)*G(1,1)*G(2,0)*G(2,1)
                                 + 10*G(0,1)*G(1,2)*G(2,0)**2
                                 + 30*G(0,2)*G(1,1)*G(2,0)**2 + 10*G(1,1)**3*G(2,0))
          - G(0,1)*G(1,0)**4*(G(0,1)**3*G(4,1) + 4*G(0,1)**2*G(0,2)*G(4,0)
                              + 4*G(0,1)**2*G(1,1)*G(3,1) + 4*G(0,1)**2*G(1,2)*G(3,0)
                              + 4*G(0,1)**2*G(2,0)*G(2,2) + 2*G(0,1)**2*G(2,1)**2
                              + 12*G(0,1)*G(0,2)*G(1,1)*G(3,0)
                              + 12*G(0,1)*G(0,2)*G(2,0)*G(2,1)
                              + 6*G(0,1)*G(0,3)*G(2,0)**2 + 6*G(0,1)*G(1,1)**2*G(2,1)
                              + 12*G(0,1)*G(1,1)*G(1,2)*G(2,0) + 6*G(0,2)**2*G(2,0)**2
                              + 12*G(0,2)*G(1,1)**2*G(2,0) + G(1,1)**4)
          - G(0,5)*G(1,0)**8
          + G(1,0)**7*(G(0,1)*G(1,4) + G(0,2)*G(1,3) + G(0,3)*G(1,2) + G(0,4)*G(1,1))
          - G(1,0)**6*(G(0,1)**2*G(2,3) + 2*G(0,1)*G(0,2)*G(2,2)
                       + 2*G(0,1)*G(0,3)*G(2,1) + 2*G(0,1)*G(0,4)*G(2,0)
                       + 2*G(0,1)*G(1,1)*G(1,3) + G(0,1)*G(1,2)**2
                       + G(0,2)**2*G(2,1) + 2*G(0,2)*G(0,3)*G(2,0)
                       + 2*G(0,2)*G(1,1)*G(1,2) + G(0,3)*G(1,1)**2)
          + G(1,0)**5*(G(0,1)**3*G(3,2) + 3*G(0,1)**2*G(0,2)*G(3,1)
                       + 3*G(0,1)**2*G(0,3)*G(3,0) + 3*G(0,1)**2*G(1,1)*G(2,2)
                       + 3*G(0,1)**2*G(1,2)*G(2,1) + 3*G(0,1)**2*G(1,3)*G(2,0)
                       + 3*G(0,1)*G(0,2)**2*G(3,0) + 6*G(0,1)*G(0,2)*G(1,1)*G(2,1)
                       + 6*G(0,1)*G(0,2)*G(1,2)*G(2,0) + 6*G(0,1)*G(0,3)*G(1,1)*G(2,0)
                       + 3*G(0,1)*G(1,1)**2*G(1,2) + 3*G(0,2)**2*G(1,1)*G(2,0)
                       + G(0,2)*G(1,1)**3)) / G(1,0)**9
    return a, b, a3, a4, a5


print("\nTHIRD ROUTE -- m2's closed forms at my g-table ((-1)^n-flipped to spec conv):")
for tag, c in (("A", A), ("B", B), ("N64", N64), ("R", R)):
    g = {}
    for m, row in enumerate(c["g_table"]):
        for n, cell in enumerate(row):
            if cell is None:
                continue  # truncation-cut entry: absent support, stays 0
            g[(m, n)] = creal(cell) * (D(-1) ** n)
    try:
        va, vb, v3, v4, v5 = closed_forms(g)
        stored = [c.get(k) for k in ("a", "b", "a3", "a4", "a5")]
        print("      %s: cf a=%s" % (tag, va))
        print("              b=%s" % vb)
        print("              a3=%s" % v3)
        print("              a4=%s" % v4)
        print("              a5=%s" % v5)
        for name, cf, st in zip(("a", "b", "a3", "a4", "a5"),
                                (va, vb, v3, v4, v5), stored):
            if st is None:
                print("         %s: stored slot EMPTY at this truncation (cf value above)"
                      % name)
                continue
            s = creal(st)
            print("         %s: vs stored rel %s | vs negated rel %s"
                  % (name, abs(cf - s) / abs(s), abs(cf + s) / abs(s)))
    except Exception as e:
        print("      %s: closed-form eval failed: %r" % (tag, e))


# ---- B1 quantitative + implied-vs-root D* (appended for the committed .out to be one-run) ----
print("")
print("B1 quantitative + implied-vs-root D*")
_cfgs = {}
for _p, _tag in (("v2_r", "R"), ("v2_n64", "N64")):
    _d = json.load(open("data/machine1_L176_selfcentring_%s.json" % _p))
    _cfgs[_tag] = _d[0] if isinstance(_d, list) else _d
for _blk in json.load(open("data/machine1_L176_selfcentring_v2_ab.json")):
    _cfgs[_blk["cfg"]] = _blk
_phi = abs(creal(_cfgs["A"]["g10"])) / abs(D("-14.16808467075497560605419228419387228304"))
_pref = -4 * PI * _phi * _phi
print("  prefactor(m1) = -4*pi*phi^2 = %s" % +_pref)
for _nm in ("R", "A", "B", "N64"):
    _c = _cfgs[_nm]
    _rw = D(str(_c["r_w"])); _nw = int(_c["N_w"])
    _d = creal(_c["delta"]); _pred = _pref * (2 * _rw) ** _nw
    print("  %-3s r_w=%s N_w=%3d  |delta/pred - 1| = %s"
          % (_nm, _rw.normalize(), _nw, abs((_d - _pred) / _d)))
    if _c.get("implied_Dstar"):
        _ids = creal(_c["implied_Dstar"]); _root = creal(_c["root_Dstar"])
        _rel = abs((_ids - _root) / _root)
        print("        implied_D* vs root_D* rel = %s   [pi*(2r_w)^N_w = %s]  dps=%s centre=%s"
              % (+_rel, +(PI * (2 * _rw) ** _nw), _c.get("dps"), _c.get("centre")))
