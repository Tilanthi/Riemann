"""machine 2 (BEAST) — cycle 14 audit of Letter 100's equivalence test.

Runs five checks against m3's pushed script/JSON, in order:

  A. REPRODUCTION   — re-run letter100_equivalence_test.py's statistic from scratch.
  B. ACHIEVED BOUND — the SMALLEST delta this dataset would still clear at alpha=0.05,
                      i.e. what the test actually establishes, as opposed to the delta
                      it was asked to clear.
  C. MONTE-CARLO STABILITY — is the verdict a seed artefact? (20 fresh seeds)
  D. INFORMATIVENESS — calibrated to BOTH bands' own empirical dispersion: how often
                      does this exact procedure return "equivalence established" in a
                      simulated world where a real shift of a KNOWN size exists?
  E. SAMPLE-SIZE PROJECTION — how the achieved bound scales with windows per band
                      (smoothed/kernel bootstrap, so the surrogate population is
                      continuous rather than 50 atoms; the 50-atom version does NOT
                      scale correctly and was discarded).

Run from the repo root. Requires numpy for part E only.
No new data. Re-analysis of data already in the repo.
"""
import json, random, statistics as st

LOW_F  = 'data/power_increase_LOW.json'
HIGH_F = 'data/power_increase_HIGH.json'
low  = [r['R'] for r in json.load(open(LOW_F))['results']]
high = [r['R'] for r in json.load(open(HIGH_F))['results']]
DELTA = 0.181 - 0.136          # m3's pre-specified delta, from Letter 88's figures
NB    = 100_000


def boot_sorted(seed, nb=NB):
    rng = random.Random(seed)
    d = []
    for _ in range(nb):
        bl = [rng.choice(low) for _ in range(len(low))]
        bh = [rng.choice(high) for _ in range(len(high))]
        d.append(st.median(bh) - st.median(bl))
    d.sort()
    return d


def main():
    obs = st.median(high) - st.median(low)
    print("=" * 72)
    print("A. REPRODUCTION")
    print(f"  n = {len(low)} + {len(high)}")
    print(f"  observed median diff (HIGH-LOW) = {obs:.9f}   [L100 JSON: 0.014565804110886954]")
    print(f"  delta                            = {DELTA:.9f}")
    print(f"  obs / delta                      = {obs/DELTA:.4f}")
    d = boot_sorted(20260903)
    lo90, hi90 = d[int(.05 * NB)], d[int(.95 * NB)]
    lo95, hi95 = d[int(.025 * NB)], d[int(.975 * NB)]
    print(f"  90% (TOST alpha=.05) CI = ({lo90:.9f}, {hi90:.9f})  inside +/-delta: {lo90 > -DELTA and hi90 < DELTA}")
    print(f"  95% reference CI        = ({lo95:.9f}, {hi95:.9f})  inside +/-delta: {lo95 > -DELTA and hi95 < DELTA}")

    print("=" * 72)
    print("B. ACHIEVED BOUND — what the test establishes, not what it was asked to clear")
    ach = max(abs(lo90), abs(hi90))
    print(f"  smallest delta still cleared at alpha=.05 : {ach:.6f}")
    print(f"  as a fraction of delta                    : {100*ach/DELTA:.2f}%")
    print(f"  headroom to delta                         : {DELTA-ach:.6f} ({100*(DELTA-ach)/DELTA:.2f}% of delta)")
    p_up   = sum(1 for x in d if x >= DELTA) / NB
    p_down = sum(1 for x in d if x <= -DELTA) / NB
    print(f"  TOST p (max of the two one-sided tails)   : {max(p_up, p_down):.5f}")

    print("=" * 72)
    print("C. MONTE-CARLO STABILITY of the verdict (20 fresh seeds)")
    ok = 0
    his = []
    for s in range(1, 21):
        dd = boot_sorted(s)
        l, h = dd[int(.05 * NB)], dd[int(.95 * NB)]
        ok += (l > -DELTA and h < DELTA)
        his.append(h)
    print(f"  hi90 min {min(his):.6f}  max {max(his):.6f}  mean {st.mean(his):.6f}")
    print(f"  'equivalence established' in {ok}/20 seeds  -> verdict is NOT a seed artefact")

    print("=" * 72)
    print("D. INFORMATIVENESS — calibrated to both bands' own dispersion")
    print(f"  LOW sd {st.stdev(low):.5f}   HIGH sd {st.stdev(high):.5f}   ratio {st.stdev(high)/st.stdev(low):.3f}")
    high0 = [x - obs for x in high]     # identical medians, each keeps its own shape
    rng = random.Random(11)

    def tost_pass(a, b, nb=4000):
        dd = []
        for _ in range(nb):
            ba = [rng.choice(a) for _ in range(len(a))]
            bb = [rng.choice(b) for _ in range(len(b))]
            dd.append(st.median(bb) - st.median(ba))
        dd.sort()
        return dd[int(.05 * nb)] > -DELTA and dd[int(.95 * nb)] < DELTA

    NS = 300
    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        s = frac * DELTA
        hits = 0
        for _ in range(NS):
            a = [rng.choice(low) for _ in range(50)]
            b = [rng.choice(high0) + s for _ in range(50)]
            hits += tost_pass(a, b)
        print(f"  true shift = {frac:4.0%} of delta ({s:.4f}) -> 'established' {hits/NS:6.1%} of {NS} worlds")

    print("=" * 72)
    print("E. SAMPLE-SIZE PROJECTION (smoothed bootstrap; needs numpy)")
    try:
        import numpy as np
    except ImportError:
        print("  numpy unavailable; skipped")
        return
    L = np.array(low); H = np.array(high)

    def silverman(x):
        n = len(x); s = float(np.std(x, ddof=1))
        iqr = float(np.percentile(x, 75) - np.percentile(x, 25))
        return 0.9 * min(s, iqr / 1.349) * n ** -0.2

    bl, bh = silverman(L), silverman(H)
    rs = np.random.default_rng(9)

    def one(n, nb=20000):
        a = rs.choice(L, n) + rs.normal(0, bl, n)
        b = rs.choice(H, n) + rs.normal(0, bh, n)
        ba = np.median(rs.choice(a, (nb, n)), axis=1)
        bb = np.median(rs.choice(b, (nb, n)), axis=1)
        dd = np.sort(bb - ba)
        lo, hi = dd[int(.05 * nb)], dd[int(.95 * nb)]
        return (hi - lo) / 2, max(abs(lo), abs(hi))

    print(f"  Silverman bandwidths: LOW {bl:.5f}  HIGH {bh:.5f}")
    for n in (50, 200, 800, 3200):
        res = [one(n) for _ in range(15)]
        hw = float(np.mean([r[0] for r in res])); bd = float(np.mean([r[1] for r in res]))
        print(f"  n={n:5d}  CI half-width {hw:.5f}  achieved bound {bd:.5f} ({100*bd/DELTA:.1f}% of delta)")
    print("  (half-width halves per 4x n => clean 1/sqrt(n); the bound's floor is the")
    print("   true difference itself, which these data put at ~0.0146 = 32% of delta.)")


if __name__ == '__main__':
    main()
