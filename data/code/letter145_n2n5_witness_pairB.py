import sys, time
sys.path.insert(0, '/tmp')
from n2n5_witness_instrument import (load_genome_mp, load_K_T200, K_pair_matrix,
                                       S_quadruple_matrix, lambda_min_gen_eig)
import mpmath as mp

mp.mp.dps = 45

if __name__ == '__main__':
    M = 8
    seed = 's1'
    fns = load_genome_mp(f"{seed}/M{M}", M)
    K200, G = load_K_T200(seed, M)

    print("Finding zeros 71, 72 (k=70 pair, smallest gap)...")
    # zetazero indices: k=70 means the 71st and 72nd zeros (BEAST's k is 0-indexed presumably)
    z70 = mp.zetazero(71)
    z71 = mp.zetazero(72)
    gamma_a, gamma_b = mp.im(z70), mp.im(z71)
    print(f"gamma (zero 71) = {gamma_a}")
    print(f"gamma (zero 72) = {gamma_b}")
    print("expected (Mac's): 184.874468, 185.598784")
    gamma0 = (gamma_a + gamma_b) / 2
    print(f"gamma0 (midpoint) = {gamma0}")

    rho_a = mp.mpc('0.5', gamma_a)
    rho_b = mp.mpc('0.5', gamma_b)

    t0 = time.time()
    K_a = K_pair_matrix(fns, rho_a)
    K_b = K_pair_matrix(fns, rho_b)
    print(f"removed-pair matrices done in {time.time()-t0:.1f}s")

    K_base = K200 - K_a - K_b
    lmin_base, _ = lambda_min_gen_eig(K_base, G)
    print(f"\nBaseline (PAIR-B both removed): lambda_min = {lmin_base}")
    print("  (compare to Mac's launch point 1.176119142e-5)")

    delta_ladder = [mp.mpf(x) for x in ['0', '0.001', '0.01', '0.05', '0.1', '0.2', '0.3', '0.45']]
    print("\nDelta ladder (PAIR-B):")
    for delta in delta_ladder:
        t0 = time.time()
        S = S_quadruple_matrix(fns, delta, gamma0)
        S_Z = K_base + S
        lmin, _ = lambda_min_gen_eig(S_Z, G)
        print(f"  delta={float(delta):.3f}: lambda_min = {lmin}  [{time.time()-t0:.1f}s]")

    print("\nCompare to BEAST's PAIR-B: pinned at 1.17612e-5 for every rung (does not fire)")
