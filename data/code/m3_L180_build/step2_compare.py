"""
Assemble c = -(1/2) v0^T A2 v0 (v0 = G-normalized minimal eigenvector of K_S(0)) for a spread of
survivor cells, and compare lambda_min(0) - c*delta^2 against the sealed delta-ladder.
"""
import sys, json, time
sys.path.insert(0, '.')
from mpmath import mp, mpf
from why_half import build_instruments, get_zeros, g_of, CENSUS_JSON

DELTAS = ['0.05', '0.1', '0.2', '0.3', '0.45']


def bilinear(v, Mx, w, n):
    return sum(v[i] * Mx[i, j] * w[j] for i in range(n) for j in range(n))


if __name__ == '__main__':
    t0 = time.time()
    insts = build_instruments()
    zeros = get_zeros(26)
    census = json.load(open(CENSUS_JSON))
    results = census['results']
    print(f"[{time.time()-t0:.1f}s] setup done", flush=True)

    # M=8 full-ladder survivors (phi=4/8): k=5..24 all survive at every delta. Pick a spread of 5.
    cell_ks = [5, 10, 15, 20, 24]
    M = 8
    inst = insts[M]

    print("=== M=8 cells: analytic c, then compare lambda_min(0)-c*delta^2 vs sealed ===\n",
          flush=True)

    summary_rows = []
    for k in cell_ks:
        g = g_of(zeros, k, 4)
        KS0 = inst.K - inst.gram(zeros[k]) - inst.gram(zeros[k + 1]) + inst.quad_ex(g, mpf(0))
        vals, vecs = inst.eig(KS0)
        lam0 = vals[0]
        v0 = vecs[0]
        # confirm G-normalization v0^T G v0 = 1 (sanity check on the eig() convention)
        gnorm = bilinear(v0, inst.G, v0, M)

        A2 = inst.A2_hessian(g)
        v0Tv0 = bilinear(v0, A2, v0, M)
        c = -v0Tv0 / 2

        print(f"k={k}: lambda_min(0)={mp.nstr(lam0,15)}  v0^T G v0={mp.nstr(gnorm,10)}  "
              f"c={mp.nstr(c,15)}", flush=True)

        row = {'k': k, 'lam0': lam0, 'c': c, 'deltas': {}}
        for dstr in DELTAS:
            d = mpf(dstr)
            predicted = lam0 - c * d * d
            key = f"{M}/{k}/4/{dstr}"
            sealed = mpf(results[key]['lam_min'])
            abs_err = predicted - sealed
            rel_err = abs_err / abs(sealed) if sealed != 0 else abs_err
            row['deltas'][dstr] = (predicted, sealed, abs_err, rel_err)
            print(f"    delta={dstr}: predicted={mp.nstr(predicted,12)}  sealed={mp.nstr(sealed,12)}  "
                  f"abs_err={mp.nstr(abs_err,5)}  rel_err={mp.nstr(rel_err,5)}", flush=True)
        summary_rows.append(row)
        print(flush=True)

    print(f"[{time.time()-t0:.1f}s] M=8 done\n", flush=True)

    print("=== M=64 cells at the smallest delta only (0.05) -- most survive there ===\n", flush=True)
    inst64 = insts[64]
    m64_ks = []
    for k in range(25):
        key = f"64/{k}/4/0.05"
        r = results.get(key)
        if r and not r['fires']:
            m64_ks.append(k)
    print(f"M=64 survivors at delta=0.05: {len(m64_ks)} of 25 -> {m64_ks}", flush=True)

    for k in m64_ks[:5]:
        g = g_of(zeros, k, 4)
        KS0 = inst64.K - inst64.gram(zeros[k]) - inst64.gram(zeros[k + 1]) + inst64.quad_ex(g, mpf(0))
        vals, vecs = inst64.eig(KS0)
        lam0 = vals[0]
        v0 = vecs[0]
        A2 = inst64.A2_hessian(g)
        v0Tv0 = bilinear(v0, A2, v0, 64)
        c = -v0Tv0 / 2
        d = mpf('0.05')
        predicted = lam0 - c * d * d
        sealed = mpf(results[f"64/{k}/4/0.05"]['lam_min'])
        rel_err = (predicted - sealed) / abs(sealed) if sealed != 0 else predicted - sealed
        print(f"k={k}: lambda_min(0)={mp.nstr(lam0,12)}  c={mp.nstr(c,12)}  "
              f"predicted(0.05)={mp.nstr(predicted,12)}  sealed={mp.nstr(sealed,12)}  "
              f"rel_err={mp.nstr(rel_err,5)}", flush=True)

    print(f"\n[{time.time()-t0:.1f}s] all done", flush=True)
