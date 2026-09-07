"""
Gate: reproduce the SEALED lambda_min(delta) values at a handful of cells, independently, before
trusting anything downstream. Read-only against data/heat78c_census_result.json.
"""
import sys, json, time
sys.path.insert(0, '.')
from mpmath import mp, mpf
from why_half import build_instruments, get_zeros, g_of, CENSUS_JSON

if __name__ == '__main__':
    t0 = time.time()
    insts = build_instruments()
    print(f"[{time.time()-t0:.1f}s] instruments built", flush=True)
    zeros = get_zeros(26)
    print(f"[{time.time()-t0:.1f}s] zeros computed", flush=True)

    census = json.load(open(CENSUS_JSON))
    results = census['results']

    # gate cells: a spread across M and k, at phi=4/8, several deltas
    gate_cells = [(8, 5, 4, '0.05'), (8, 10, 4, '0.1'), (8, 20, 4, '0.2'),
                  (8, 24, 4, '0.45'), (64, 5, 4, '0.05')]

    maxerr = mpf(0)
    for (M, k, phi8, dstr) in gate_cells:
        inst = insts[M]
        g = g_of(zeros, k, phi8)
        KS = inst.K - inst.gram(zeros[k]) - inst.gram(zeros[k + 1]) + inst.quad_ex(g, mpf(dstr))
        vals, vecs = inst.eig(KS)
        mine = vals[0]
        key = f"{M}/{k}/{phi8}/{dstr}"
        sealed = mpf(results[key]['lam_min'])
        err = abs(mine - sealed) / abs(sealed) if sealed != 0 else abs(mine - sealed)
        maxerr = max(maxerr, err)
        print(f"{key}: mine={mp.nstr(mine,20)}  sealed={mp.nstr(sealed,20)}  rel_err={mp.nstr(err,5)}",
              flush=True)

    print(f"\nMAX relative error across gate cells: {mp.nstr(maxerr, 5)}", flush=True)
    assert maxerr < mpf('1e-20'), "GATE FAILED -- own construction does not reproduce sealed values"
    print("GATE PASSED -- own Instrument construction reproduces sealed lambda_min exactly.",
          flush=True)
    print(f"[{time.time()-t0:.1f}s] done", flush=True)
