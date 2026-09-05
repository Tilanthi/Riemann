"""machine2 CYCLE 26 -- part 2 of the scored unit (declared as an EXTENSION, run after the sealed
runner, and labelled as such).

Two jobs the prereg's sealed runner left open:

 (A) pin the failure boundary delta_b* where r = 1/2 (the sealed runner bracketed it to [0.55,0.60]).

 (B) THE REMEDY.  r = |ty6-exact|/|ty4-exact| needs the exact value, so it cannot certify a band in
     the situation the band exists for.  Test the OBSERVABLE surrogate
         q = |ty6 - ty4| / |ty4 - ty2|
     which uses only the ladder itself.  If q tracks r, then "band trustworthy" becomes a check the
     practitioner can run BEFORE the exact eigensolve: for a geometric ladder r = q/(1-q) exactly,
     so the band rule holds iff q < 1/3.
"""
import json, os, sys, time
from mpmath import mp

C26 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, C26)
import importlib.util
spec = importlib.util.spec_from_file_location("bl", os.path.join(C26, "m2_c26_bandlaw.py"))

# reuse the sealed runner's instrument by importing its module-level setup
sys.argv = [sys.argv[0]]
import io, contextlib
bl = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(bl)          # re-runs the sealed legs silently; output already committed
mp.dps = 40
t0 = time.time()
OUT = {}

# ---------- (A) boundary ----------
lo, hi = mp.mpf("0.55"), mp.mpf("0.60")


def r_of(db):
    ex, tys = bl.config(mp.mpf("0.1"), db, "b", orders=(2, 4, 6))
    e4 = abs(tys[4] - ex); e6 = abs(tys[6] - ex)
    q = abs(tys[6] - tys[4]) / abs(tys[4] - tys[2])
    return e6 / e4, q, ex, tys


print("(A) bisecting r = 1/2 on delta_b in [0.55, 0.60]")
rlo, _, _, _ = r_of(lo); rhi, _, _, _ = r_of(hi)
print("   bracket  r(%s) = %s   r(%s) = %s" % (mp.nstr(lo, 4), mp.nstr(rlo, 8), mp.nstr(hi, 4), mp.nstr(rhi, 8)))
for it in range(22):
    mid = (lo + hi) / 2
    rm, _, _, _ = r_of(mid)
    if rm < mp.mpf("0.5"):
        lo = mid
    else:
        hi = mid
    if it % 5 == 0 or it == 21:
        print("   it %2d  delta_b* in [%s, %s]" % (it, mp.nstr(lo, 12), mp.nstr(hi, 12)), flush=True)
dstar = (lo + hi) / 2
OUT["delta_b_star"] = mp.nstr(dstar, 14)
OUT["bracket"] = [mp.nstr(lo, 16), mp.nstr(hi, 16)]
print("   delta_b* = %s   (band rule fails for delta_b > this)" % mp.nstr(dstar, 12))

# ---------- (B) observable surrogate ----------
print("\n(B) observable surrogate q = |ty6-ty4|/|ty4-ty2| vs the unobservable r")
print("%-8s | %12s %12s %14s %12s %s" % ("d_b", "r", "q", "q/(1-q)", "rel.dev", "band"))
rows = {}
for ds in ["0.10", "0.16499045761728792745744", "0.20", "0.30", "0.35", "0.40", "0.45",
           "0.50", "0.55", "0.60", "0.70", "0.80"]:
    db = mp.mpf(ds)
    r, q, ex, tys = r_of(db)
    pred = q / (1 - q)
    dev = abs(pred - r) / r
    holds = bool(abs(tys[4] - ex) <= 2 * abs(tys[6] - tys[4]))
    rows[ds] = {"r": mp.nstr(r, 12), "q": mp.nstr(q, 12), "q_over_1mq": mp.nstr(pred, 12),
                "rel_dev": mp.nstr(dev, 6), "in_band": holds,
                "surrogate_verdict": bool(q < mp.mpf(1) / 3), "agree": holds == bool(q < mp.mpf(1) / 3)}
    print("%-8s | %12s %12s %14s %12s %s  surrogate says %s %s"
          % (ds[:8], mp.nstr(r, 8), mp.nstr(q, 8), mp.nstr(pred, 8), mp.nstr(dev, 4),
             "IN " if holds else "OUT", "IN " if q < mp.mpf(1) / 3 else "OUT",
             "AGREE" if holds == bool(q < mp.mpf(1) / 3) else "**DISAGREE**"), flush=True)
OUT["surrogate"] = rows
OUT["surrogate_agreement"] = "%d/%d" % (sum(1 for v in rows.values() if v["agree"]), len(rows))
json.dump(OUT, open(os.path.join(C26, "c26_boundary.json"), "w"), indent=1)
print("\nagreement %s      done %.1fs" % (OUT["surrogate_agreement"], time.time() - t0))
