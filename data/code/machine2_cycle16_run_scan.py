import json, time, math, sys
from multiprocessing import Pool
import certify

SIGMAJ = 1.1842563361   # gate 1
BOX = (0.52, SIGMAJ, 20.0, 43.0)

if __name__ == "__main__":
    t0 = time.time()
    out = {}
    with Pool(8, initializer=certify._init, initargs=(20,)) as pool:
        # --- Lipschitz bound for method B: sampled sup |F'| over the residual box + margin
        import numpy as np
        xs = np.linspace(BOX[0], BOX[1], 15); ys = np.linspace(BOX[2], BOX[3], 60)
        pts = [(float(x), float(y)) for x in xs for y in ys]
        d = pool.map(certify._Fp, pts, chunksize=8)
        Lsamp = max(d); L = 1.6 * Lsamp
        out['lipschitz'] = dict(n_samples=len(pts), sup_sampled=Lsamp, safety=1.6, L=L)
        print("METHOD B Lipschitz: sampled sup|F'| = %.5f over %d pts; L = 1.6*sup = %.5f  (%.0fs)"
              % (Lsamp, len(pts), L, time.time() - t0))

        # --- METHOD B
        t1 = time.time()
        B = certify.modulus_exclusion(pool, *BOX, L=L, h0=0.20, maxdepth=7)
        B['seconds'] = time.time() - t1
        out['methodB'] = B
        area = (BOX[1] - BOX[0]) * (BOX[3] - BOX[2])
        print("\nMETHOD B  modulus exclusion on Re[%.4f,%.4f] x Im[%g,%g], area %.5f" % (BOX + (area,)))
        for r in B['per_depth']:
            print("   depth %d  cell %.5f  cells=%-6d certified-empty=%-6d survive=%-5d area_certified=%.5f"
                  % (r['depth'], r['cell_w'], r['n_cells'], r['n_certified_empty'], r['n_survive'], r['area_certified']))
        tot = sum(r['area_certified'] for r in B['per_depth'])
        print("   TOTAL certified-empty area = %.5f of %.5f (%.4f%%);  UNCERTIFIED = %.6f  [%d evals, %.0fs]"
              % (tot, area, 100 * tot / area, B['area_uncertified'], B['n_evals'], B['seconds']))
        out['methodB_area_certified'] = tot; out['methodB_area_total'] = area

        # --- METHOD A: whole box, then a 23-way partition, then additivity
        t1 = time.time()
        W = certify.winding_certified(pool, *BOX, n0=900, maxdepth=10)
        W['seconds'] = time.time() - t1
        out['methodA_whole'] = W
        print("\nMETHOD A  whole box: zeros=%s verdict=%s  max|dArg|=%.5f (cap %.5f)  max step ratio=%.5f (cap %.2f)"
              % (W['zeros'], W['verdict'], W['max_step_arg'], math.pi/4, W['max_step_ratio'], 0.5))
        print("          min|F| on contour=%.6f  contour pts=%d  evals=%d  refine depth=%d  uncertified steps=%d  raw=%.9f  [%.0fs]"
              % (W['min_mod_on_contour'], W['n_contour_pts'], W['n_evals'], W['refine_depth'],
                 W['n_uncertified_steps'], W['raw_winding'], W['seconds']))

        subs = []
        t1 = time.time()
        for j in range(23):
            y0, y1 = 20.0 + j, 21.0 + j
            r = certify.winding_certified(pool, BOX[0], BOX[1], y0, y1, n0=200, maxdepth=10)
            subs.append(r)
            print("   sub Im[%g,%g]: zeros=%-5s %-10s max|dArg|=%.4f ratio=%.4f min|F|=%.5f pts=%d"
                  % (y0, y1, r['zeros'], r['verdict'], r['max_step_arg'], r['max_step_ratio'],
                     r['min_mod_on_contour'], r['n_contour_pts']))
        out['methodA_subs'] = subs
        ssum = sum(r['zeros'] for r in subs if r['zeros'] is not None)
        nvoid = sum(1 for r in subs if r['zeros'] is None)
        out['additivity'] = dict(sum_subs=ssum, whole=W['zeros'], n_void_subs=nvoid,
                                 agree=(nvoid == 0 and ssum == W['zeros']))
        print("   (c3) ADDITIVITY: sum of %d sub-boxes = %d ; whole box = %s ; VOID subs = %d ; agree = %s  [%.0fs]"
              % (len(subs), ssum, W['zeros'], nvoid, out['additivity']['agree'], time.time() - t1))

    out['total_seconds'] = time.time() - t0
    json.dump(out, open("scan_results.json", "w"), indent=1, default=str)
    print("\nwrote scan_results.json  total %.0fs" % out['total_seconds'])
