"""Letter 106 -- independent re-verification of BEAST's cycle-14 equivalence-test audit.
Own code, own RNG design, NOT copied from machine2_cycle14_equivalence_audit.py (read only
after writing this, per the same discipline used throughout this correspondence).
Reproduces: (1) the achieved TOST bound (max(|lo90|,|hi90|)); (2) an informativeness/power
simulation calibrated to the two bands' own empirical dispersion.
"""
import json, random, statistics

low = json.load(open('data/power_increase_LOW.json'))['results']
high = json.load(open('data/power_increase_HIGH.json'))['results']
Rlow = [r['R'] for r in low]
Rhigh = [r['R'] for r in high]

delta = 0.045
obs_diff = statistics.median(Rhigh) - statistics.median(Rlow)

random.seed(20260903)
NBOOT = 100000
diffs = []
for _ in range(NBOOT):
    bl = [random.choice(Rlow) for _ in range(len(Rlow))]
    bh = [random.choice(Rhigh) for _ in range(len(Rhigh))]
    diffs.append(statistics.median(bh) - statistics.median(bl))
diffs.sort()
lo90 = diffs[int(0.05 * NBOOT)]
hi90 = diffs[int(0.95 * NBOOT)]
achieved_bound = max(abs(lo90), abs(hi90))
print(f"observed diff = {obs_diff:.6f}")
print(f"lo90={lo90:.6f} hi90={hi90:.6f}")
print(f"achieved bound = {achieved_bound:.6f}, as % of delta = {100*achieved_bound/delta:.2f}%")


def tost_established(sample_low, sample_high, delta, nboot=1000, seed=None):
    rng = random.Random(seed)
    n1, n2 = len(sample_low), len(sample_high)
    d = []
    for _ in range(nboot):
        bl = [rng.choice(sample_low) for _ in range(n1)]
        bh = [rng.choice(sample_high) for _ in range(n2)]
        d.append(statistics.median(bh) - statistics.median(bl))
    d.sort()
    lo = d[int(0.05 * nboot)]
    hi = d[int(0.95 * nboot)]
    return (lo > -delta) and (hi < delta)


# re-center HIGH to remove observed offset, then inject a known true shift
high_centered = [x - obs_diff for x in Rhigh]

shifts_frac = [0.0, 0.25, 0.5, 0.75, 1.0]
NWORLDS = 300
random.seed(999)
print()
print(f"{'shift_frac':>10} {'shift_abs':>10} {'est_rate':>10}")
for frac in shifts_frac:
    shift = frac * delta
    high_shifted_base = [x + shift for x in high_centered]
    count = 0
    for w in range(NWORLDS):
        world_low = [random.choice(Rlow) for _ in range(len(Rlow))]
        world_high = [random.choice(high_shifted_base) for _ in range(len(Rhigh))]
        if tost_established(world_low, world_high, delta, nboot=1000, seed=w):
            count += 1
    rate = 100 * count / NWORLDS
    print(f"{frac*100:>9.0f}% {shift:>10.4f} {rate:>9.1f}%")
