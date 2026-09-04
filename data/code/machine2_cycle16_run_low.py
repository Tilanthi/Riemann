"""Close the chain from t = 0: re-run cycle 15's C15-R1 region on the stable evaluator with the
four certificates.  C15-R1 (Re[0.52,4] x Im[-20,20], winding -1, pole inside) was reported with
max step arg 2.5279 -- inside pi but far outside this cycle's pi/4 cap, and taken on E1, whose
error at t=20 is 3.0e-9 (fine) but which is the same instrument that failed at t=43.
GATE 1 already kills sigma >= 1.1842563361 for free, so only Re[0.52,1.1842563361] is scanned."""
import json, time, math
from multiprocessing import Pool
import certify

X0, X1 = 0.52, 1.1842563361
if __name__ == "__main__":
    rows = []; t0 = time.time()
    with Pool(8, initializer=certify._init, initargs=(25,)) as pool:
        # box containing the pole s=1 (Im in [-0.5,0.5]): winding = Z - 1
        rp = certify.winding_certified(pool, X0, X1, -0.5, 0.5, n0=300, maxdepth=11)
        print("pole box Re[%.4f,%.7f] x Im[-0.5,0.5]: raw winding=%.9f -> zeros = winding+1 = %s  %s"
              % (X0, X1, rp['raw_winding'], (rp['zeros'] + 1) if rp['zeros'] is not None else None, rp['verdict']))
        print("   max|dArg|=%.5f ratio=%.5f min|F|=%.6f pts=%d" % (rp['max_step_arg'], rp['max_step_ratio'],
                                                                   rp['min_mod_on_contour'], rp['n_contour_pts']))
        rp['note'] = 'contains the simple pole s=1; zeros = winding + 1'
        rows.append(rp)
        for y in range(0, 20):
            y0 = max(0.5, float(y)); y1 = float(y + 1)
            if y1 <= 0.5: continue
            r = certify.winding_certified(pool, X0, X1, y0, y1, n0=220, maxdepth=11)
            r.pop('box'); r['t_lo'] = y0; r['t_hi'] = y1
            rows.append(r)
            print("t[%5.1f,%5.1f] zeros=%-5s %-10s max|dArg|=%.4f ratio=%.4f min|F|=%.6f pts=%d"
                  % (y0, y1, r['zeros'], r['verdict'], r['max_step_arg'], r['max_step_ratio'],
                     r['min_mod_on_contour'], r['n_contour_pts']), flush=True)
    json.dump(rows, open("low_results.json", "w"), indent=1, default=str)
    zz = [r for r in rows[1:] if r['zeros']]
    print("\nLOW-t TOTAL Re[%.4f,%.7f] x Im[0,20] (upper half): %d unit boxes, zeros in %s"
          % (X0, X1, len(rows) - 1, [(r['t_lo'], r['zeros']) for r in zz] or "NONE"))
    print("  VOID boxes: %d ; wall %.0fs" % (sum(1 for r in rows if r['zeros'] is None), time.time() - t0))
