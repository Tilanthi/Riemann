"""machine2 CYCLE 26 addendum -- test m1-L159's (3960ef3) two pre-run completions on real data.

 (i)  BRANCH AWARENESS.  My H1 wrote ratio = 0.5/(1-r).  m1 points out that is the SAME-SIGN branch
      only; on the OVERSHOOT branch (ty6 past exact) the correct form is 0.5/(1+r), and the branch is
      readable from ratio </> 0.5 WITHOUT the exact value.  Tested here by pushing delta_b past the
      sealed ladder into the divergent regime and looking for a real overshoot.

 (ii) THE UN-FAIL WINDOW.  m1 claims 'fails iff r > 1/2' has a window r in [1.921, 2.000] where a
      2x-degraded ladder re-enters the healthy band.  Verified here as arithmetic on the branch
      formulae, and checked against the PUBLISHED window [0.500, 0.543].
"""
import json, os, sys, io, contextlib, importlib.util
from mpmath import mp

C26 = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bl", os.path.join(C26, "m2_c26_bandlaw.py"))
bl = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(bl)
mp.dps = 40
OUT = {}

print("(i) branch hunt -- delta_b past the sealed ladder; t = (exact-ty6)/(ty6-ty4)")
print("%-6s | %14s %14s %10s %14s %14s %s" %
      ("d_b", "ratio", "r", "t sign", "0.5/(1-r)", "0.5/(1+r)", "branch"))
rows = {}
for ds in ["0.55", "0.60", "0.80", "0.90", "1.00", "1.10", "1.20", "1.40"]:
    db = mp.mpf(ds)
    ex, tys = bl.config(mp.mpf("0.1"), db, "b", orders=(2, 4, 6))
    D = tys[6] - tys[4]; e = ex - tys[6]
    t = e / D
    ratio = abs(tys[4] - ex) / (2 * abs(D))
    r = abs(e) / abs(tys[4] - ex)
    same = mp.mpf("0.5") / (1 - r); over = mp.mpf("0.5") / (1 + r)
    br = "SAME-SIGN" if t > 0 else "OVERSHOOT"
    fit = "0.5/(1-r)" if abs(ratio - same) < abs(ratio - over) else "0.5/(1+r)"
    rows[ds] = {"ratio": mp.nstr(ratio, 12), "r": mp.nstr(r, 12), "t": mp.nstr(t, 12),
                "branch": br, "formula_that_fits": fit,
                "rel_dev_same": mp.nstr(abs(ratio - same) / ratio, 6),
                "rel_dev_over": mp.nstr(abs(ratio - over) / ratio, 6),
                "ratio_gt_half": bool(ratio > mp.mpf("0.5")),
                "in_band": bool(abs(tys[4] - ex) <= 2 * abs(D))}
    print("%-6s | %14s %14s %10s %14s %14s %s  fits %s  ratio>0.5 %s"
          % (ds, mp.nstr(ratio, 8), mp.nstr(r, 8), "+" if t > 0 else "-",
             mp.nstr(same, 8), mp.nstr(over, 8), br, fit, rows[ds]["ratio_gt_half"]), flush=True)
OUT["branch_hunt"] = rows

print("\n(ii) un-fail window on the overshoot branch: band holds iff ratio<=1")
print("     overshoot branch: ratio = 0.5/(1+r) <= 1 for ALL r>=0  -> never fails")
print("     m1's window is the DEGRADED same-sign continuation |t|>1 (ty6 worse than ty4):")
print("%-10s %14s %14s %s" % ("|t|=|e/D|", "r=|t|/|1-t|", "ratio=0.5|1-t|", "verdict"))
win = {}
for us in ["1.5", "2.0", "2.086", "2.5", "3.0", "3.001", "4.0"]:
    u = mp.mpf(us)
    r = u / abs(1 - u)
    ratio = mp.mpf("0.5") * abs(1 - u)
    win[us] = {"r": mp.nstr(r, 10), "ratio": mp.nstr(ratio, 10), "in_band": bool(ratio <= 1),
               "inside_published_window": bool(mp.mpf("0.500") <= ratio <= mp.mpf("0.543"))}
    print("%-10s %14s %14s %s%s" % (us, mp.nstr(r, 8), mp.nstr(ratio, 8),
          "IN " if ratio <= 1 else "OUT",
          "   <-- INSIDE the published [0.500,0.543] window" if win[us]["inside_published_window"] else ""))
OUT["unfail_window"] = win
json.dump(OUT, open(os.path.join(C26, "c26_branch.json"), "w"), indent=1)
print("\ndone")
