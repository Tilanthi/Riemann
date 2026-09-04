"""EXTENSION (separate denominator, METHOD A only): push the certified census UPWARD in t.
h(-196)=4>1 => Davenport-Heilbronn 1936 gives infinitely many zeros with sigma>1; GATE 1
confines them to 1 < sigma < 1.1842563361.  This lane turns a qualitative existence theorem
into a MEASURED height lower bound, with the four external certificates printed per unit box.

NOTE ON A FAILED FIRST ATTEMPT (recorded, not hidden): the first version of this script ran
METHOD B (modulus exclusion, maxdepth 8) here.  It did not finish one 10-unit chunk in 5 min:
|F'| grows with t, so more cells survive each depth and the quadtree grows x4 per level.
Method B is an AREA-coverage instrument and is affordable on the primary wedge; on a long
strip Method A is ~70x cheaper for the same verdict.  Killed and replaced.
"""
import json, time, math, sys
from multiprocessing import Pool
import certify

SIGMAJ = 1.1842563361
X0, X1 = 0.52, SIGMAJ

if __name__ == "__main__":
    t_start = int(sys.argv[1]); t_stop = int(sys.argv[2])
    rows = []
    t00 = time.time()
    with Pool(8, initializer=certify._init, initargs=(20,)) as pool:
        for y in range(t_start, t_stop):
            r = certify.winding_certified(pool, X0, X1, float(y), float(y + 1), n0=220, maxdepth=11)
            r.pop('box')
            r['t_lo'] = y; r['t_hi'] = y + 1
            rows.append(r)
            if r['zeros'] != 0 or (y - t_start) % 10 == 0:
                print("t[%4d,%4d] zeros=%-5s %-10s max|dArg|=%.4f ratio=%.4f min|F|=%.6f pts=%-6d evals=%-6d depth=%d  [%.0fs]"
                      % (y, y + 1, r['zeros'], r['verdict'], r['max_step_arg'], r['max_step_ratio'],
                         r['min_mod_on_contour'], r['n_contour_pts'], r['n_evals'], r['refine_depth'],
                         time.time() - t00), flush=True)
            json.dump(rows, open("ext_results.json", "w"), indent=1, default=str)
    nz = [r for r in rows if r['zeros'] not in (0, None)]
    nv = [r for r in rows if r['zeros'] is None]
    print("\nEXTENSION TOTAL  Re[%.4f,%.6f] x Im[%d,%d]: %d unit boxes, %d CERTIFIED, %d VOID, %d with zeros"
          % (X0, X1, t_start, t_stop, len(rows), len(rows) - len(nv), len(nv), len(nz)))
    print("  total zeros found = %d ; total contour evaluations = %d ; wall %.0fs"
          % (sum(r['zeros'] for r in rows if r['zeros']), sum(r['n_evals'] for r in rows), time.time() - t00))
    print("  min over boxes of min|F| on contour = %.6f ; max over boxes of max|dArg| = %.5f (cap %.5f)"
          % (min(r['min_mod_on_contour'] for r in rows), max(r['max_step_arg'] for r in rows), math.pi / 4))
    for r in nz + nv:
        print("  NONZERO/VOID BOX: t[%d,%d] zeros=%s verdict=%s" % (r['t_lo'], r['t_hi'], r['zeros'], r['verdict']))
