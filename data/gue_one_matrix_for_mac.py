import numpy as np
import json

# Exact same construction/convention as gue_experiment.py (the script behind
# our published H1-H3 GUE population results), just for a single seed and
# with full raw data dumped for Mac's diff-the-convention request (their
# machine1-kappa3-settled-gue-lock.md, §A3).
N = 300
CENTRAL_WINDOW = 40
SEED = 20260903   # matching Mac's stated seed choice for their own push

rng = np.random.default_rng(SEED)
A = rng.normal(size=(N, N)) + 1j * rng.normal(size=(N, N))
H = (A + A.conj().T) / 2.0
eigs = np.linalg.eigvalsh(H)
eigs = np.sort(eigs.real)

mid_idx = N // 2
lo = mid_idx - CENTRAL_WINDOW // 2
hi = mid_idx + CENTRAL_WINDOW // 2
window = eigs[lo:hi]
gaps = np.diff(window)
j_local = int(np.argmin(gaps))
global_j = lo + j_local
lam1, lam2 = eigs[global_j], eigs[global_j + 1]
d = (lam2 - lam1) / 2.0
m0 = (lam1 + lam2) / 2.0

others = np.concatenate([eigs[:global_j], eigs[global_j + 2:]])
delta = m0 - others

kappa1 = np.sum(1.0 / delta)
S2 = np.sum(1.0 / delta**2)
B = S2
kappa2 = -(1.0 / d**2 + B / 2.0)
S3 = np.sum(1.0 / delta**3)
kappa3 = -S3 / 3.0
S4 = np.sum(1.0 / delta**4)
kappa4 = -S4 / 4.0
q = B * d**2 / 2.0
R = S4 / S2**2

out = dict(
    seed=SEED, N=N, CENTRAL_WINDOW=CENTRAL_WINDOW,
    note="Full sorted eigenvalue spectrum of one N=300 GUE(complex Hermitian, "
         "standard normal entries, H=(A+A^H)/2) realization, plus the tightest "
         "adjacent pair found in the central 40-eigenvalue window and derived "
         "quantities, using the identical convention as gue_experiment.py "
         "(our published H1-H3 population run). Pushed per Mac's request in "
         "machine1-kappa3-settled-gue-lock.md SsA3 to locate the ~3.44x q "
         "discrepancy to a specific convention step.",
    tightest_pair=dict(
        global_index_j=int(global_j),
        lambda_j=float(lam1), lambda_j_plus_1=float(lam2),
        d=float(d), m0=float(m0),
    ),
    derived=dict(kappa1=float(kappa1), B=float(B), kappa2=float(kappa2),
                 kappa3=float(kappa3), kappa4=float(kappa4), q=float(q), R=float(R)),
    full_sorted_eigenvalues=eigs.tolist(),
)
json.dump(out, open('/data/Riemann/rmt/gue_one_matrix_seed20260903.json', 'w'), indent=1)
print('seed', SEED, ' j=', global_j, ' lambda_j=', lam1, ' lambda_j+1=', lam2)
print('d=', d, ' m0=', m0)
print('kappa1=', kappa1, ' B=', B, ' kappa2=', kappa2, ' kappa3=', kappa3, ' kappa4=', kappa4)
print('q=', q, ' R=', R)
