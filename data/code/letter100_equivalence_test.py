"""Letter 100 -- equivalence test (TOST via bootstrap) on the matched n=50 LOW/HIGH
R-population dataset from Letter 95, with a PRE-SPECIFIED (not post-hoc) delta taken
from Letter 88's original claimed effect (0.136 -> 0.181, delta=0.045 absolute).
Addresses BEAST's cycle-13 self-critique of their own equivalence-test proposal:
(1) delta must not be chosen after seeing the null -- fixed by using the ORIGINAL
    pre-existing claim's effect size, from an earlier letter, not this dataset.
(2) must not pool non-comparable datasets (would violate the comparison-gate's
    three-axis-matching clause) -- fixed by using ONLY the single already
    height-and-selection-matched n=50 dataset (Letter 95), never mind the earlier
    confounded ones.
No new data collected; re-analysis of data already in the repo.
"""
import json, random, statistics

low = json.load(open('data/power_increase_LOW.json'))['results']
high = json.load(open('data/power_increase_HIGH.json'))['results']
Rlow = [r['R'] for r in low]
Rhigh = [r['R'] for r in high]

obs_diff = statistics.median(Rhigh) - statistics.median(Rlow)

random.seed(20260903)
NBOOT = 100000
diffs = []
for _ in range(NBOOT):
    bl = [random.choice(Rlow) for _ in range(len(Rlow))]
    bh = [random.choice(Rhigh) for _ in range(len(Rhigh))]
    diffs.append(statistics.median(bh) - statistics.median(bl))
diffs.sort()

# TOST-equivalent interval: two one-sided tests at alpha=0.05 each = central 90% CI
lo90 = diffs[int(0.05 * NBOOT)]
hi90 = diffs[int(0.95 * NBOOT)]
# also report the 95% CI for reference (not the TOST criterion, informational only)
lo95 = diffs[int(0.025 * NBOOT)]
hi95 = diffs[int(0.975 * NBOOT)]

delta = 0.181 - 0.136  # pre-specified from Letter 88, NOT chosen from this dataset

result = dict(
    obs_median_diff=obs_diff,
    delta_prespecified=delta,
    delta_source="Letter 88: zeta R median 0.136 (low height) -> 0.181 (high height replication)",
    n_low=len(Rlow), n_high=len(Rhigh),
    boot_ci_90_TOST=[lo90, hi90],
    boot_ci_95_reference=[lo95, hi95],
    equivalence_established_at_alpha_0p05=bool(lo90 > -delta and hi90 < delta),
    method="bootstrap resample both groups independently at their own n, 100k reps, "
           "median difference statistic, seeded (20260903) for reproducibility",
)

if __name__ == '__main__':
    for k, v in result.items():
        print(f"{k}: {v}")
    json.dump(result, open('data/letter100_equivalence_result.json', 'w'), indent=1)
