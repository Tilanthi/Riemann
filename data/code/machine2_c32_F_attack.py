"""machine2 CYCLE 32 -- MY OWN RECORDED ATTACK ON F (condition C's fitness object).

m1-L171 sect 2.1 already attacked F on four fronts (u-instability, the k=25 fallback
discontinuity, the empty near-threshold regime, cliff-vs-chord at survivor-bearing sites) and
offered a bracket-interpolation replacement.  This file does NOT repeat any of those.  It runs
the two tests my OWN condition A(b) demanded of any scalar fitness -- an external ground truth
and a null -- neither of which has been run by anyone, including me.

A1. EXTERNAL GROUND TRUTH.  F claims to estimate log10(delta_c).  At every census site whose five
    deltas contain BOTH a survivor and a firer, delta_c is BRACKETED by the data itself.  F is
    therefore falsifiable there with no new computation: 10^F must land inside the bracket.
    Firing world non-empty by construction (a wrong S puts it outside).

A2. THE NULL F HAS NEVER BEEN RUN AGAINST.  The c31 evidence ("not the bit with extra steps")
    tested F against the FIRES BIT.  It never tested F against the far stronger trivial rival
    "rank by lam_min alone", nor against "rank by delta alone".  If F's order is a monotone
    relabelling of lam_min's order, F is lam_min with extra steps -- a different and much more
    embarrassing charge than being the bit with extra steps.

A3. THE DISCARDED RESIDUAL.  F is a per-CELL number estimating a per-SITE quantity, so the five
    cells of a site give five estimates of one number.  Their spread is a free internal falsifier
    that the rule as written throws away.  Measured, and proposed as a hard gate.
"""
import json
import itertools

import mpmath as mp

mp.mp.dps = 40
CENSUS = "/shared/rh-exchange-repo/Riemann/data/heat78c_census_result.json"
CONST = "/workspace/rh/cycle31/m2_c31_fitness_constants.json"
THETA = mp.mpf("-1e-12")
U = mp.mpf("1e-12")

C = json.load(open(CONST))
S_PER = {k: mp.mpf(v) for k, v in C["S_per_site"].items()}
S_FALLBACK = mp.mpf(C["S_median_fallback"])


def A(lam):
    return mp.asinh((lam - THETA) / U)


d = json.load(open(CENSUS))
cells = []          # (k, phi8, delta, lam, fires)
for key, v in d["results"].items():
    p = key.split("/")
    if p[0] != "64":
        continue
    cells.append((int(p[1]), int(p[2]), mp.mpf(p[3]), mp.mpf(v["lam_min"]), bool(v["fires"])))

print(f"census M=64 cells: {len(cells)}")
slice4 = [c for c in cells if c[1] == 4]
print(f"phi8=4 slice     : {len(slice4)}")


def S_of(k, phi8):
    return S_PER.get(f"{k}/{phi8}", S_FALLBACK)


def F_of(k, phi8, delta, lam):
    return mp.log10(delta) - A(lam) / S_of(k, phi8)


# ------------------------------------------------------------------ A1
print("\n" + "=" * 78)
print("A1  EXTERNAL GROUND TRUTH: does 10^F land inside the site's own bracket?")
print("=" * 78)
sites = {}
for k, p8, delta, lam, fires in cells:
    sites.setdefault((k, p8), []).append((delta, lam, fires))
brack = []
for (k, p8), rows in sorted(sites.items()):
    rows.sort()
    surv = [r for r in rows if not r[2]]
    fire = [r for r in rows if r[2]]
    if surv and fire:
        lo = max(r[0] for r in surv)          # largest delta that survives
        hi = min(r[0] for r in fire)          # smallest delta that fires
        if lo < hi:
            brack.append((k, p8, lo, hi, rows))
print(f"bracketed sites (both a survivor and a firer among the five deltas): {len(brack)}")
n_in = n_tot = 0
for k, p8, lo, hi, rows in brack:
    print(f"\n  site {k}/{p8}   delta_c in ({mp.nstr(lo,4)}, {mp.nstr(hi,4)})   "
          f"log10 bracket = ({mp.nstr(mp.log10(lo),6)}, {mp.nstr(mp.log10(hi),6)})   "
          f"S = {mp.nstr(S_of(k,p8),8)}")
    for delta, lam, fires in rows:
        F = F_of(k, p8, delta, lam)
        inside = mp.log10(lo) <= F <= mp.log10(hi)
        n_in += int(inside)
        n_tot += 1
        print(f"     d={mp.nstr(delta,4):>6s} {'FIRE' if fires else 'surv'}  "
              f"F = {mp.nstr(F,8):>12s}  10^F = {mp.nstr(10**F,6):>10s}  "
              f"{'INSIDE ' if inside else 'OUTSIDE'}")
print(f"\n  VERDICT A1: {n_in}/{n_tot} cell-level estimates land inside their own site's bracket "
      f"({100.0*n_in/max(n_tot,1):.1f}%)")

# ------------------------------------------------------------------ A2
print("\n" + "=" * 78)
print("A2  THE NULL: is F a monotone relabelling of lam_min?")
print("=" * 78)


def discordance(pairs_a, pairs_b):
    n = len(pairs_a)
    conc = disc = tie = 0
    for i, j in itertools.combinations(range(n), 2):
        da = pairs_a[i] - pairs_a[j]
        db = pairs_b[i] - pairs_b[j]
        if da == 0 or db == 0:
            tie += 1
        elif (da > 0) == (db > 0):
            conc += 1
        else:
            disc += 1
    tot = conc + disc + tie
    return conc, disc, tie, (conc - disc) / tot   # Kendall tau-a


for label, rows in [("phi8=4 slice (125)", slice4), ("full M=64 (205)", cells)]:
    Fv = [F_of(k, p8, dl, lam) for k, p8, dl, lam in [(c[0], c[1], c[2], c[3]) for c in rows]]
    lamv = [c[3] for c in rows]
    delv = [c[2] for c in rows]
    asv = [A(c[3]) for c in rows]
    firev = [mp.mpf(0) if c[4] else mp.mpf(1) for c in rows]
    print(f"\n  {label}: n={len(rows)}")
    for nm, rival in [("lam_min alone     ", lamv),
                      ("delta alone       ", delv),
                      ("asinh term alone  ", asv),
                      ("fires bit alone   ", firev)]:
        c_, d_, t_, tau = discordance(Fv, rival)
        print(f"    F vs {nm}: Kendall tau-a = {float(tau):+.6f}   "
              f"concordant {c_}  DISCORDANT {d_}  tied {t_}")

# ------------------------------------------------------------------ A3
print("\n" + "=" * 78)
print("A3  THE DISCARDED RESIDUAL: within-site spread of F, and it as a GATE")
print("=" * 78)
spreads = []
for (k, p8), rows in sorted(sites.items()):
    Fs = [F_of(k, p8, dl, lam) for dl, lam, _ in rows]
    sp = max(Fs) - min(Fs)
    has_surv = any(not r[2] for r in rows)
    spreads.append((sp, k, p8, len(rows), has_surv))
spreads.sort(reverse=True)
allsp = [s[0] for s in spreads]
allsp_sorted = sorted(allsp)
med = allsp_sorted[len(allsp_sorted) // 2]
print(f"  sites: {len(spreads)}   median spread = {mp.nstr(med,8)} dec   "
      f"max = {mp.nstr(allsp[0] if False else max(allsp),8)} dec")
print("  WORST 8 sites by within-site F spread (decades):")
for sp, k, p8, n, hs in spreads[:8]:
    print(f"    {k}/{p8}  spread {mp.nstr(sp,8):>12s}  n={n}  survivor-bearing={hs}")
print("  BEST 5:")
for sp, k, p8, n, hs in spreads[-5:]:
    print(f"    {k}/{p8}  spread {mp.nstr(sp,8):>12s}  n={n}  survivor-bearing={hs}")
sb = [s for s in spreads if s[4]]
nsb = [s for s in spreads if not s[4]]
if sb:
    print(f"\n  survivor-bearing sites  n={len(sb)}  median spread "
          f"{mp.nstr(sorted(x[0] for x in sb)[len(sb)//2],8)}")
if nsb:
    print(f"  all-fire sites          n={len(nsb)}  median spread "
          f"{mp.nstr(sorted(x[0] for x in nsb)[len(nsb)//2],8)}")
