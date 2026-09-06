"""machine2 CYCLE 31 -- DRAFT RANKING RULE for charter mechanism 1 (condition C's missing object).

THE RULE.  For a gen-0 candidate cell c = (k, delta) with published lam_min(c) = lam:

    F(c)  =  log10(delta)  -  asinh( (lam - theta) / u ) / S

F is an ESTIMATE OF log10(delta_c), the displacement at which this site's smallest eigenvalue
would cross the published FIRES threshold.  It is not a balance of two incommensurable scores:
both terms are in the SAME UNIT (decades of displacement), because S is the measured number of
asinh-units per decade of delta on the sealed census.  Higher F = the positivity certificate
survives further out in displacement.  A survivor scores above log10(delta); a firer below it.

CONSTANTS, each DERIVED from artefacts gen-0 already reads:
    theta = -1e-12   the published FIRES threshold (m1-L168 sect1) -- the decision scale
    u     = |theta| = 1e-12   below which a sign is not resolved, so the transform is linear there
    S     = the site's own slope d(asinh term)/d(log10 delta), least-squares-fitted on the SEALED
            census data/heat78c_census_result.json at M=64 (sha256 published in m1-L168 sect5),
            IF that site carries >= 2 census deltas; otherwise the MEDIAN of all such site slopes.
            The fallback is what makes the rule total: a genuinely new site (gen-0's k=25) has no
            census slope, and a rule that cannot score a new site cannot rank a breeding round.

TIES.  Strictly decreasing F; ties broken by (larger delta, then larger k, then string order of
the cell key).  Real-valued + deterministic tiebreak => a TOTAL ORDER, hence a total preorder.

INPUTS.  Exactly what gen-0 already publishes:
    cells["{k}/{delta}"]["lam_min"]  (25 s.f. decimal string)
    cells["{k}/{delta}"]["fires"]    (bool; used only for reporting, NOT in F)
    the cell key, which carries k and delta
plus, for the three constants only, the sealed census JSON gen-0 already reads as its gate anchor.
No quantity is required that gen-0 does not already write.
"""
import json
import sys

import mpmath as mp

mp.mp.dps = 40
CENSUS = "/shared/rh-exchange-repo/Riemann/data/heat78c_census_result.json"
THETA = mp.mpf("-1e-12")
U = mp.mpf("1e-12")


def A(lam):
    return mp.asinh((lam - THETA) / U)


def load_census(path=CENSUS):
    d = json.load(open(path))
    m64 = {}
    for key, v in d["results"].items():
        p = key.split("/")
        if p[0] != "64":
            continue
        m64[(int(p[1]), int(p[2]), p[3])] = (mp.mpf(v["lam_min"]), bool(v["fires"]))
    return d, m64


def slope_S(m64):
    """median over sites (k, phi8) of the least-squares slope of A(lam) against log10(delta)."""
    sites = {}
    for (k, phi8, dd), (lam, _) in m64.items():
        sites.setdefault((k, phi8), []).append((mp.log(mp.mpf(dd), 10), A(lam)))
    slopes = []
    for key, pts in sites.items():
        if len(pts) < 2:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        xm = mp.fsum(xs) / len(xs)
        ym = mp.fsum(ys) / len(ys)
        num = mp.fsum([(x - xm) * (y - ym) for x, y in zip(xs, ys)])
        den = mp.fsum([(x - xm) ** 2 for x in xs])
        slopes.append(num / den)
    slopes.sort()
    n = len(slopes)
    med = slopes[n // 2] if n % 2 else (slopes[n // 2 - 1] + slopes[n // 2]) / 2
    return med, slopes


def site_slopes(m64):
    """least-squares slope of A(lam) against log10(delta) at each (k, phi8) with >= 2 deltas."""
    sites = {}
    for (k, phi8, dd), (lam, _) in m64.items():
        sites.setdefault((k, phi8), []).append((mp.log(mp.mpf(dd), 10), A(lam)))
    Sk = {}
    for key, pts in sites.items():
        if len(pts) < 2:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        xm = mp.fsum(xs) / len(xs)
        ym = mp.fsum(ys) / len(ys)
        Sk[key] = (mp.fsum([(x - xm) * (y - ym) for x, y in zip(xs, ys)])
                   / mp.fsum([(x - xm) ** 2 for x in xs]))
    return Sk


def S_of(k, phi8, Sk, Sbar):
    """THE FROZEN SLOPE RULE: the site's own census slope if it has one, else the median."""
    return Sk.get((k, phi8), Sbar)


def F(lam, delta, k, Sk, Sbar, phi8=4):
    return mp.log(delta, 10) - A(lam) / S_of(k, phi8, Sk, Sbar)


def rank(cells, Sk, Sbar, phi8=4):
    keyed = [(F(lam, delta, k, Sk, Sbar, phi8), delta, k, key, lam, fires)
             for (key, k, delta, lam, fires) in cells]
    keyed.sort(key=lambda t: (-t[0], -t[1], -t[2], t[3]))
    return keyed


def main():
    d, m64 = load_census()
    Sbar, slopes = slope_S(m64)
    Sk = site_slopes(m64)
    print("=== CONSTANTS ===")
    print("  theta (published FIRES threshold) : %s" % mp.nstr(THETA, 4))
    print("  u = |theta|                       : %s" % mp.nstr(U, 4))
    print("  census M=64 cells                 : %d  (survivors %d)"
          % (len(m64), sum(1 for v in m64.values() if not v[1])))
    print("  per-site slopes available         : %d sites" % len(Sk))
    print("  slope range   [%s , %s]" % (mp.nstr(slopes[0], 8), mp.nstr(slopes[-1], 8)))
    print("  S_bar = MEDIAN slope (fallback)   : %s" % mp.nstr(Sbar, 12))

    cells = [("%d/%s" % (k, dd), k, mp.mpf(dd), lam, fires)
             for (k, phi8, dd), (lam, fires) in m64.items() if phi8 == 4]
    order = rank(cells, Sk, Sbar)
    print("\n=== APPLIED TO THE SEALED CENSUS, phi8=4 SLICE (%d cells) ===" % len(cells))
    print("  rank  cell        fires  lam_min                 F = est. log10 delta_c")
    for i, t in enumerate(order[:10], 1):
        print("  %4d  %-10s  %-5s  %-23s %s" % (i, t[3], t[5], mp.nstr(t[4], 12), mp.nstr(t[0], 8)))
    print("  ...")
    for i, t in enumerate(order[-3:], start=len(order) - 2):
        print("  %4d  %-10s  %-5s  %-23s %s" % (i, t[3], t[5], mp.nstr(t[4], 12), mp.nstr(t[0], 8)))

    surv = [t for t in order if not t[5]]
    fire = [t for t in order if t[5]]
    print("\n=== CONDITION (c): the rule must not be the FIRES bit with extra steps ===")
    print("  survivors %d, distinct F %d ; firers %d, distinct F %d"
          % (len(surv), len({mp.nstr(t[0], 30) for t in surv}),
             len(fire), len({mp.nstr(t[0], 30) for t in fire})))
    worst_s = min(t[0] for t in surv)
    print("  firers scoring ABOVE the worst survivor : %d   (0 would mean F IS the bit)"
          % sum(1 for t in fire if t[0] > worst_s))
    print("  best firer F = %s   worst survivor F = %s"
          % (mp.nstr(max(t[0] for t in fire), 8), mp.nstr(worst_s, 8)))

    print("\n=== SELF-CONSISTENCY (the rule's own named defect #1) ===")
    for label, getS in (("per-site S_k (+ fallback)", lambda k: S_of(k, 4, Sk, Sbar)),
                        ("global median S_bar only", lambda k: Sbar)):
        per = {}
        for (k, phi8, dd), (lam, _) in m64.items():
            if phi8 != 4:
                continue
            per.setdefault(k, []).append(mp.log(mp.mpf(dd), 10) - A(lam) / getS(k))
        sp = sorted([max(v) - min(v) for v in per.values() if len(v) > 1])
        print("  %-26s within-site F spread: median %s  max %s"
              % (label, mp.nstr(sp[len(sp) // 2], 6), mp.nstr(sp[-1], 6)))
    print("  reference: the census delta grid itself spans %s decades"
          % mp.nstr(mp.log(mp.mpf("0.45") / mp.mpf("0.05"), 10), 6))

    print("\n=== gen-0 SCOPE ===")
    print("  gen-0 site k=25 has no census slope -> falls back to S_bar = %s" % mp.nstr(Sbar, 8))
    g0d = [mp.mpf(x) for x in ["0.04", "0.05", "0.06", "0.07", "0.09", "0.1", "0.11", "0.12"]]
    print("  gen-0's delta term spans only %s decades (named defect #3)"
          % mp.nstr(mp.log(max(g0d) / min(g0d), 10), 6))

    json.dump({"formula": "F = log10(delta) - asinh((lam_min - theta)/u) / S(k,phi8)",
               "theta": "-1e-12", "u": "1e-12",
               "S_rule": ("least-squares slope of asinh((lam-theta)/u) against log10(delta) over the "
                          "sealed census M=64 cells at that (k,phi8) if it carries >=2 deltas; "
                          "else the median of all such site slopes"),
               "S_median_fallback": mp.nstr(Sbar, 25),
               "n_site_slopes": len(Sk),
               "S_per_site": {("%d/%d" % kk): mp.nstr(v, 25) for kk, v in sorted(Sk.items())},
               "tiebreak": "larger delta, then larger k, then string order of the cell key",
               "census_source": "data/heat78c_census_result.json, sha256 sealed in m1-L168 sect5",
               "status": "DRAFT for amendment by m1 and m3 before any freeze; trigger is generation 1"},
              open("m2_c31_fitness_constants.json", "w"), indent=1)
    print("\nwrote m2_c31_fitness_constants.json")


if __name__ == "__main__":
    sys.exit(main())
