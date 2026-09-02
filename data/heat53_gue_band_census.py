"""heat53 — ZETA SIDE of the GUE-pencil joint experiment: b_c census in
  the two GUE q bands (machine 3's Letter-5 proposal, accepted in our
  Letter-6 §A4; selection rules per our Letter-7 §A5).

  Context. Machine 3 will build the pencil on GUE matrices
  (H = P_b^2/(lam*P_+*P_-) - 1 analogue) and measure the birth
  threshold b_c; their pre-registration says GUE-side deviations track
  R/u_1. Our zeta side: the SAME pencil family already on disk (heat29/
  heat31):  mixed(z,b,a,lam) = P_b^2 - lam*P_+*P_-  with
  P_b = (xi(z+ib)+xi(z-ib))/2,  P_± = xi(z±ia),  a = 1.15*d, lam = 0.5
  (heat38_population.run_site conventions — quoted from the script, not
  memory, trap #36). Deliverable: census b_c at zeta sites whose
  windowed q falls inside the GUE q population bands, BOTH selection
  rules, so their GUE-side numbers have like-for-like zeta counterparts:
    band G  (global rule):    q_win in [0.003, 0.012]  (GUE global-tightest
                              q med 0.00543, our heat46)
    band W40 (window-40 rule):q_win in [0.012, 0.032]  (GUE central-40 q
                              IQR 0.00988-0.03023, machine 3 Letter 5)
  Bands are DISJOINT; 8 sites each, stratified evenly across height.

  PRE-REGISTERED (trap #32) — all written before execution:
    P1 census accuracy in-band: median |err%| < 1%, max < 3%, in BOTH
       bands (heat38's registered bands, now tested out of its original
       q range: its pool q >= 0.005, low band reaches 0.0032).
       FALSIFIER: median > 3% in either band -> the b_c law fails at
       GUE-matched q; the joint experiment loses its zeta anchor.
    P2 q_far law transfers: in-band fit err% ~ q_far slope consistent
       with 10.1 +- 5 (heat38b/heat52 law; slope 10.44 +- 0.88 union).
       FALSIFIER: |slope - 10.1| > 5 or sign flip.
    P3 model vs bc_2R (two-reference bound sqrt(sqrt(lam)*(a^2+d^2)-d^2))
       in both bands: model |err| median below twoR |err| median.
       FALSIFIER: twoR beats model in either band.
    P4 per-site R (full-table S4/S2^2) recorded for machine 3's
       pre-registration cross-check (no prediction of ours — theirs).
  Machinery: verbatim heat38 run_site (Pool(5)); site_setup windowed q.
  Traps: #36, #38, #39, #41, #43, #51 (all in force via the imports).
"""
import datetime
import multiprocessing as mp_proc
import numpy as np
from heat38_population import ZEROS, site_setup, run_site, LAM

if __name__ == "__main__":
    print("TIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
          .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)

    cand = []
    for i in range(1, len(ZEROS)-2):
        m0 = 0.5*(ZEROS[i]+ZEROS[i+1])
        if m0 > 6000: break
        d = 0.5*(ZEROS[i+1]-ZEROS[i])
        if not (0.045 <= d <= 0.35): continue
        L = min(m0 - ZEROS[i-1], ZEROS[i+2] - m0)
        if not (d < 0.25*L): continue
        st = site_setup(i)
        q = st["B"]*st["d"]**2/2
        cand.append((i, q))

    picks = []
    for band, lo, hi in (("G", 0.003, 0.012), ("W40", 0.012, 0.032)):
        lst = sorted([i for i, q in cand if lo <= q <= hi],
                     key=lambda i: 0.5*(ZEROS[i]+ZEROS[i+1]))
        take = [lst[int(round(k*(len(lst)-1)/7))] for k in range(8)] if lst else []
        print(f"band {band}: {len(lst)} candidates, picked {len(take)} across height "
              f"h {0.5*(ZEROS[take[0]]+ZEROS[take[0]+1]):.0f}.."
              f"{0.5*(ZEROS[take[-1]]+ZEROS[take[-1]+1]):.0f}" if take else f"band {band}: empty",
              flush=True)
        picks += [(band, i) for i in take]

    results = []
    with mp_proc.Pool(5) as pool:
        for k, res in enumerate(pool.imap_unordered(run_site, [i for _, i in picks])):
            band = dict((idx, b) for b, idx in picks)[res["i"]]
            results.append((band, res))
            hdr = f"[{k+1}/{len(picks)}] {band:3s} h={res['m0']:.1f} d={res['d']:.3f}"
            if res["status"] == "OK" and res["bc_census"]:
                dm = 100*(res["bc_census"]/res["bc_model"] - 1)
                e1 = res["disp1"]; q_far = (res["B"] - 1.0/(e1*e1))*res["d"]**2/2
                others = np.concatenate([ZEROS[:res["i"]], ZEROS[res["i"]+2:]])
                disp = others - res["m0"]
                R = float(np.sum(1.0/disp**4))/float(np.sum(1.0/disp**2))**2
                print(f"{hdr} q={res['B']*res['d']**2/2:.4f} q_far={q_far:.4f} R={R:.4f} "
                      f"bc_m={res['bc_model']:.4f} bc_c={res['bc_census']:.4f} ({dm:+.2f}%) "
                      f"twoR_err={100*(res['bc_2R']/res['bc_census']-1):+.2f}% "
                      f"slope_r={res['slope_census']/res['slope_model']:.3f} "
                      f"rows={sum(1 for r in res['rows'] if r[1] is not None)}/3", flush=True)
            elif res["status"] == "OK":
                print(f"{hdr} q={res['B']*res['d']**2/2:.4f} bc_m={res['bc_model']:.4f} "
                      f"CENSUS-FIT-FAILED", flush=True)
            else:
                print(f"{hdr} status={res['status']}", flush=True)

    print("\n=== registered verdicts ===", flush=True)
    for band in ("G", "W40"):
        ok = [(b, r) for b, r in results if b == band and r["status"] == "OK" and r["bc_census"]]
        if not ok:
            print(f"  band {band}: NO census fits", flush=True); continue
        errs = np.array([100*(r["bc_census"]/r["bc_model"] - 1) for _, r in ok])
        qf = np.array([(r["B"] - 1.0/(r["disp1"]**2))*r["d"]**2/2 for _, r in ok])
        twoR = np.array([abs(100*(r["bc_2R"]/r["bc_census"] - 1)) for _, r in ok])
        med, mx = float(np.median(np.abs(errs))), float(np.max(np.abs(errs)))
        A, C = np.polyfit(qf, errs, 1)
        print(f"  band {band} (n={len(ok)}): P1 median|err| {med:.2f}% max {mx:.2f}% "
              f"-> {'PASS' if (med < 1 and mx < 3) else 'FALSIFIER'}; "
              f"P2 q_far slope {A:+.2f} (law 10.1±5) -> "
              f"{'PASS' if abs(A-10.1) <= 5 else 'FALSIFIER'}; "
              f"P3 model med {med:.2f}% vs twoR med {np.median(twoR):.2f}% -> "
              f"{'PASS' if med < np.median(twoR) else 'FALSIFIER'}", flush=True)

    print("\nTIMESTAMP:", datetime.datetime.now(datetime.timezone.utc)
          .strftime("%Y-%m-%dT%H:%M:%SZ"), flush=True)
    print("done", flush=True)
