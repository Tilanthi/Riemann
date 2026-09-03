# Significance test: GUE (Letter 80, M=100, W=8/k=7) vs zeta primary arm (Mac's heat67, 12 windows, W=8/k=7)
from scipy import stats
import json
import numpy as np

zeta_primary_R = [0.12009, 0.12654, 0.25961, 0.18644, 0.13479, 0.12363,
                  0.13579, 0.14288, 0.25988, 0.37186, 0.13274, 0.10034]  # heat67 table, primary arm

if __name__ == '__main__':
    gue = json.load(open('../gue_leg.json'))
    gue_R = [r['R'] for r in gue['results'] if 'R' in r]

    print('zeta n=', len(zeta_primary_R), ' median=', sorted(zeta_primary_R)[len(zeta_primary_R)//2])
    print('GUE n=', len(gue_R), ' median=', sorted(gue_R)[len(gue_R)//2])

    u_stat, p_mw = stats.mannwhitneyu(zeta_primary_R, gue_R, alternative='two-sided')
    print('Mann-Whitney U:', u_stat, ' p=', p_mw)

    rng = np.random.default_rng(2026)
    combined = np.array(zeta_primary_R + gue_R)
    n1 = len(zeta_primary_R)
    obs_diff = np.median(zeta_primary_R) - np.median(gue_R)
    n_perm = 100000
    count = 0
    for _ in range(n_perm):
        perm = rng.permutation(combined)
        diff = np.median(perm[:n1]) - np.median(perm[n1:])
        if abs(diff) >= abs(obs_diff):
            count += 1
    print('permutation test on median difference: observed diff=', obs_diff, ' p=', count/n_perm)
