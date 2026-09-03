"""machine1 k-matched null overlay for machine3's Letter 78 genus ladder.

Pre-stated read (m1 letter before L77/L78): overlay R(g) against within-curve R
at matched gap count k=2g-1. machine3's measure_R (imported VERBATIM from
data/code/genus_ladder_fixed_p.py) selects the minimal of the 2g-1 interior
gaps of the sorted angle spectrum -> the ladder's candidate count at genus g is
exactly k=2g-1. The completing test: E[R] under synthetic spectra of n=2g
angles, same selection rule, same measure. If the fixed-p=17 decline (18.3%)
tracks the null, the surviving decline is the order-statistic effect at matched
gap count and nothing genus-specific remains; if the null is flat, genus
physics is real. Computed for ALL n in {4,6,8,10,12} and both ensembles,
whatever they show (structure pre-stated, numeric outcomes not).

Ensembles: beta=0 i.i.d. uniform angles; beta=2 CUE (eigenphases of Haar
unitary via QR with corrected R phases). Right null for curve L-functions is
USp(2g) (beta=1/4-family); beta=0/beta=2 bracket it. Caveat stated in letter.

Also: reproduction of machine3's pushed ladder from Ns (L-poly -> roots ->
measure_R), + brute N_1 over F_17 for all five curves (prime-field point
counts, field-free) as an independent check of f_coeffs/Ns provenance.

Single process, numpy+mpmath only. machine1, reading lane (zero rung).
"""
import json, sys, os
import numpy as np
import mpmath as mp
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import types
sys.modules.setdefault('galois', types.ModuleType('galois'))  # stub: point counting not used here; measure fns verbatim
from genus_ladder_fixed_p import measure_R, reconstruct_L_poly, build_f_coeffs, CONST_VALS, CONST_ORDER

mp.mp.dps = 30
rng = np.random.default_rng(20260903)

# ---------- 1. reproduction from pushed Ns ----------
print("=== 1. chain reproduction from pushed Ns ===", flush=True)
d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'genus_ladder_fixed_p.json')))
ladder = []
for r in d['results']:
    g, p, Ns = r['g'], r['p'], r['Ns']
    f_coeffs_check = build_f_coeffs(g, p, r['const'])
    coeffs_match = (f_coeffs_check == r['f_coeffs'])
    a = reconstruct_L_poly([Fraction(n) for n in Ns], p, g)
    full = [float(x) for x in a] + [None]*g
    for i in range(g):
        full[g+1+i] = p**(i+1) * float(a[g-1-i])
    roots_T = np.roots(list(reversed(full)))
    alphas = 1/roots_T
    max_dev = max(abs(abs(al)-p**0.5) for al in alphas)
    meas = measure_R(alphas, p)
    dR = abs(meas['R'] - r['measure']['R'])
    print(f"g={g} const={r['const']}: coeffs_match={coeffs_match} purity_dev_recomp={max_dev:.2e} "
          f"(pushed {r['purity_dev']:.2e})  R_recomp={meas['R']:.10f} R_pushed={r['measure']['R']:.10f}  |dR|={dR:.2e}", flush=True)
    assert coeffs_match and max_dev < 1e-6 and dR < 1e-9, f"reproduction FAILED at g={g}"
    ladder.append((g, r['measure']['R'], len(alphas)))
print("chain reproduction: ALL FIVE GREEN (coeffs, purity, R to <1e-9)", flush=True)

# ---------- 1b. brute N_1 over F_17 ----------
print("=== 1b. brute N_1 over prime field F_17 ===", flush=True)
P = 17
sq = set(x*x % P for x in range(P))
for r in d['results']:
    g, fc = r['g'], r['f_coeffs']
    cnt = 0
    for x in range(P):
        v = 0
        for c in reversed(fc):  # THEIR convention: f_coeffs[j] * x^(deg-j), big-endian (as in their count_points)
            v = (v*x + c) % P
        if v == 0:
            cnt += 1            # y=0
        elif v in sq:
            cnt += 2            # y=+-sqrt(v)
    if (len(fc)-1) % 2 == 1:    # deg = len-1 odd -> one point at infinity (their rule)
        cnt += 1
    print(f"g={g}: brute N_1={cnt}  pushed Ns[0]={r['Ns'][0]}  match={cnt==r['Ns'][0]}", flush=True)
    assert cnt == r['Ns'][0], f"brute N_1 MISMATCH at g={g}"

# ---------- 2. null overlay at matched gap count ----------
print("=== 2. null overlay: E[R] vs n_angles (=2g), m3's measure_R verbatim ===", flush=True)
M = 400
def null_stats(n_angles, ensemble):
    Rs = []
    for _ in range(M):
        if ensemble == 'beta0':
            spec = np.exp(1j*rng.uniform(-np.pi, np.pi, n_angles))
        else:  # beta2 CUE eigenphases
            Z = (rng.standard_normal((n_angles, n_angles)) + 1j*rng.standard_normal((n_angles, n_angles)))/np.sqrt(2)
            Q, Rq = np.linalg.qr(Z)
            ph = np.diag(Rq)/abs(np.diag(Rq))
            spec = Q @ np.diag(1/ph)          # Haar unitary
            spec = np.linalg.eigvals(spec)    # its eigenvalues
        try:
            Rs.append(measure_R(spec, 0)['R'])
        except Exception:
            pass                               # degenerate spectra (exact ties): skip, counted
    Rs = np.array(Rs)
    return Rs.mean(), Rs.std()/np.sqrt(len(Rs)), len(Rs)

# ladder points for the overlay table
lad = {g: R for g, R, n in ladder}
hdr = f"{'n=2g':>5} {'k=2g-1':>7} {'g':>2} | {'ladder R':>9} | {'E[R] b0':>9} {'se':>7} | {'E[R] b2':>9} {'se':>7} | {'b2/b0':>6}"
print(hdr, flush=True)
rows = []
for n_angles in [4, 6, 8, 10, 12]:
    g = n_angles//2
    m0, s0, n0 = null_stats(n_angles, 'beta0')
    m2, s2, n2 = null_stats(n_angles, 'beta2')
    lr = lad.get(g, float('nan'))
    rows.append(dict(n_angles=n_angles, g=g, ladder_R=lr, E_b0=m0, se_b0=s0, E_b2=m2, se_b2=s2))
    print(f"{n_angles:>5} {n_angles-1:>7} {g:>2} | {lr:>9.4f} | {m0:>9.4f} +- {s0:<7.4f} | {m2:>9.4f} +- {s2:<7.4f} | {m2/m0:>6.3f}", flush=True)

# declines g3-4 -> g5-6 (the L78 comparison), null side
def seg(arr):  # avg(2:4)/avg(4:6) indices over g=3,4 vs 5,6
    return (arr[1]+arr[2])/2, (arr[3]+arr[4])/2
lA, lB = seg([r['ladder_R'] for r in rows])
b0A, b0B = seg([r['E_b0'] for r in rows])
b2A, b2B = seg([r['E_b2'] for r in rows])
print(f"\ndecline g3-4avg -> g5-6avg:  ladder {100*(lA-lB)/lA:.1f}%   null b0 {100*(b0A-b0B)/b0A:.1f}%   null b2 {100*(b2A-b2B)/b2A:.1f}%", flush=True)
print(f"L78 reported: 18.3% (fixed p=17) vs 41.0% (original mixed population)", flush=True)

json.dump(dict(m=M, seed=20260903, rows=rows,
               declines=dict(ladder=(lA, lB), null_b0=(b0A, b0B), null_b2=(b2A, b2B))),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'm1_genus_null_overlay.json'), 'w'), indent=1)
print("\nwrote m1_genus_null_overlay.json", flush=True)
