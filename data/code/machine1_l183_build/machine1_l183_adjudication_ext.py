"""
m1-L183 adjudication extensions for m3-L181 (why-1/2 RESULTS). Read-only against the sealed
census JSON and m3's committed build. Three objects, all preregistered (2e2178f) before this
script existed:

  1. the M=64 Hessian finite-difference RECEIPT m3-L181 sec.2 describes but did not commit;
  2. the eigengap/two-level diagnostic for the unexplained monotone k-trend in M=64 rel_errs
     (d4_mix = sum_j (v_j^T A2 v0)^2/(lam0-lam_j)  vs  d4_eff = (sealed - quadratic)/delta^4;
      plus the two-branch lambda_-(delta) built from (lam0,lam1,A2) alone, no A4);
  3. m3's honest gap: k=22/23/24 at M=64, delta=0.05.

Imports m3's why_half.py for definitions only (their own seal checks re-run on build).
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'm3_L180_build'))
from mpmath import mp, mpf, sqrt as msqrt
import why_half as wh

DELTAS = ['0.05', '0.1', '0.2', '0.3', '0.45']
D05 = mpf('0.05')


def bil(v, Mx, w, n):
    return sum(v[i] * Mx[i, j] * w[j] for i in range(n) for j in range(n))


def cell_data(inst, M, zeros, k):
    """lam0, lam1, c, A2, v0, v1, and the full mixing decomposition."""
    g = wh.g_of(zeros, k, 4)
    KS0 = inst.K - inst.gram(zeros[k]) - inst.gram(zeros[k + 1]) + inst.quad_ex(g, mpf(0))
    vals, vecs = inst.eig(KS0)
    lam0, lam1 = vals[0], vals[1]
    v0, v1 = vecs[0], vecs[1]
    A2 = inst.A2_hessian(g)
    b00 = bil(v0, A2, v0, M)
    b11 = bil(v1, A2, v1, M)
    b01 = bil(v0, A2, v1, M)
    c = -b00 / 2
    # mixing quartic: sum_{j>=1} (v_j^T A2 v0)^2 / (lam0 - lam_j)
    d4_mix = mpf(0)
    n_terms = 0
    for j in range(1, M):
        bj0 = bil(vecs[j], A2, v0, M)
        if bj0 != 0:
            d4_mix += bj0 * bj0 / (lam0 - vals[j])
            n_terms += 1
    return dict(k=k, g=g, lam0=lam0, lam1=lam1, v0=v0, v1=v1, A2=A2,
                b00=b00, b11=b11, b01=b01, c=c, d4_mix=d4_mix, vals=vals, vecs=vecs)


def two_level(cd, d):
    lam0, lam1, b00, b11, b01 = cd['lam0'], cd['lam1'], cd['b00'], cd['b11'], cd['b01']
    t = d * d
    root = msqrt(((lam0 - lam1) / 2 + t * (b00 - b11) / 2) ** 2 + t * t * b01 * b01)
    return (lam0 + lam1) / 2 + t * (b00 + b11) / 2 - root


if __name__ == '__main__':
    t0 = time.time()
    print('m1-L183 adjudication extensions -- prereg 2e2178f -- read-only', flush=True)
    insts = wh.build_instruments()
    zeros = wh.get_zeros(26)
    census = json.load(open(wh.CENSUS_JSON))
    results = census['results']
    print(f"[{time.time()-t0:.1f}s] setup done\n", flush=True)

    # --- 0. survivor list, my own read of the sealed JSON (not via m3's script) ---
    m64_ks = [k for k in range(25)
              if results.get(f"64/{k}/4/0.05") and not results[f"64/{k}/4/0.05"]['fires']]
    m8_ks = [k for k in range(25)
             if all(results.get(f"8/{k}/4/{d}") and not results[f"8/{k}/4/{d}"]['fires']
                    for d in DELTAS)]
    print(f"sealed-JSON survivor lists: M64@0.05 = {len(m64_ks)} of 25 -> {m64_ks}", flush=True)
    print(f"                          M8 full-ladder = {len(m8_ks)} of 25\n", flush=True)

    # --- 1. the M=64 Hessian FD receipt (k=16) ---
    inst64 = insts[64]
    g16 = wh.g_of(zeros, 16, 4)
    h = mpf('1e-8')
    Q0 = inst64.quad_ex(g16, mpf(0))
    Qp = inst64.quad_ex(g16, h)
    Qm = inst64.quad_ex(g16, -h)
    D1 = (Qp - Qm) / (2 * h)
    D2 = (Qp - 2 * Q0 + Qm) / (h * h)
    A2a = inst64.A2_hessian(g16)
    maxd1 = max(abs(D1[i, j]) for i in range(64) for j in range(64))
    maxdiff = max(abs(D2[i, j] - A2a[i, j]) for i in range(64) for j in range(64))
    maxval = max(abs(A2a[i, j]) for i in range(64) for j in range(64))
    print("== M=64 Hessian FD receipt (k=16, h=1e-8) ==", flush=True)
    print(f"  max |D1| (evenness): {mp.nstr(maxd1, 6)}", flush=True)
    print(f"  max |A2|:            {mp.nstr(maxval, 8)}", flush=True)
    print(f"  max |D2 - A2|:       {mp.nstr(maxdiff, 6)}   relative: {mp.nstr(maxdiff/maxval, 6)}",
          flush=True)
    print(f"  prereg bound: relative <= 1e-12 -> {'PASS' if maxdiff/maxval <= mpf('1e-12') else 'FAIL'}\n",
          flush=True)

    # --- 2. M=64 cells: the k-trend diagnostic + k=22/23/24 ---
    print("== M=64 @ delta=0.05: quadratic vs sealed vs two-level; d4 decomposition ==", flush=True)
    hdr = ("k      lam0            c          gap=lam1-lam0   quad_relerr   2lvl_relerr   "
           "d4_eff      d4_mix       mix/effective")
    print(hdr, flush=True)
    for k in m64_ks:  # ALL EIGHT, including m3's not-run k=22/23/24
        cd = cell_data(inst64, 64, zeros, k)
        quad = cd['lam0'] - cd['c'] * D05 * D05
        two = two_level(cd, D05)
        sealed = mpf(results[f"64/{k}/4/0.05"]['lam_min'])
        req = (quad - sealed) / abs(sealed)
        rer = (two - sealed) / abs(sealed)
        d4_eff = (sealed - quad) / (D05 ** 4)
        gap = cd['lam1'] - cd['lam0']
        ratio = cd['d4_mix'] / d4_eff if d4_eff != 0 else mpf(0)
        print(f"{k:<3d} {mp.nstr(cd['lam0'],8):>14s} {mp.nstr(cd['c'],6):>12s} {mp.nstr(gap,6):>14s} "
              f"{mp.nstr(req,4):>12s} {mp.nstr(rer,4):>12s} {mp.nstr(d4_eff,4):>11s} "
              f"{mp.nstr(cd['d4_mix'],4):>12s} {mp.nstr(ratio,3):>13s}", flush=True)
    print(flush=True)

    # --- 3. M=8 contrast cells: branch isolation across the whole ladder ---
    print("== M=8 cells: gap vs |c|*delta^2 (isolation ratio at delta=0.45; prereg: >= 1e3) ==",
          flush=True)
    inst8 = insts[8]
    for k in [5, 10, 15, 20, 24]:
        cd = cell_data(inst8, 8, zeros, k)
        gap = cd['lam1'] - cd['lam0']
        iso = gap / (abs(cd['c']) * mpf('0.45') ** 2)
        print(f"k={k:<3d} lam0={mp.nstr(cd['lam0'],10)}  gap={mp.nstr(gap,8)}  "
              f"|c|*0.45^2={mp.nstr(abs(cd['c'])*mpf('0.2025'),6)}  isolation={mp.nstr(iso,4)}",
              flush=True)
    print(f"\n[{time.time()-t0:.1f}s] all done", flush=True)
