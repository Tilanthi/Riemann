import mpmath as mp
import json, time, sys

def my_bisect(f, a, b, tol, max_iter=60):
    fa = f(a)
    for _ in range(max_iter):
        mid = (a+b)/2
        fm = f(mid)
        if abs(b-a) < tol:
            return mid
        if (fa > 0) == (fm > 0):
            a, fa = mid, fm
        else:
            b = mid
    return (a+b)/2

def scan_window(T_center, n_spacings, dps=25, tol=mp.mpf('1e-8')):
    """Reproduces exactly the scan used in manual_zerofinder4.py / neff_1e12_population.py."""
    old = mp.mp.dps
    mp.mp.dps = dps
    spacing = 2*mp.pi/mp.log(T_center/(2*mp.pi))
    step = spacing/4
    T_lo = T_center - n_spacings*spacing/2
    n_pts = int(n_spacings*spacing/step) + 1
    T_hi = T_lo + n_pts*step   # the ACTUAL right edge the original loop reaches

    t_prev = T_lo
    z_prev = mp.siegelz(t_prev)
    zeros = []
    for i in range(1, n_pts+1):
        t = T_lo + i*step
        z = mp.siegelz(t)
        if (z_prev > 0) != (z > 0) and z_prev != 0 and z != 0:
            root = my_bisect(mp.siegelz, t_prev, t, tol)
            zeros.append(root)
        t_prev, z_prev = t, z
    mp.mp.dps = old
    return zeros, T_lo, T_hi, spacing

def turing_certify(T_center, n_spacings, dps=25, label=""):
    t0 = time.time()
    zeros, T_lo, T_hi, spacing = scan_window(T_center, n_spacings, dps=dps)
    n_scan = len(zeros)
    t1 = time.time()

    # Rigorous count via mpmath's Turing/Rosser-block machinery, fully independent of the scan.
    old = mp.mp.dps
    mp.mp.dps = 25
    N_lo = mp.nzeros(T_lo)
    N_hi = mp.nzeros(T_hi)
    mp.mp.dps = old
    n_rigorous = int(N_hi - N_lo)
    t2 = time.time()

    certified = (n_scan == n_rigorous)
    print(f"[{label}] T_center={T_center}  window=[{float(T_lo):.4f},{float(T_hi):.4f}]  "
          f"spacing={float(spacing):.6f}  n_scan={n_scan}  n_rigorous={n_rigorous}  "
          f"CERTIFIED={certified}  scan_time={t1-t0:.1f}s  nzeros_time={t2-t1:.1f}s", flush=True)
    return dict(label=label, T_center=str(T_center), T_lo=str(T_lo), T_hi=str(T_hi),
                spacing=str(spacing), n_scan=n_scan, n_rigorous=n_rigorous,
                certified=certified, zeros=[str(z) for z in zeros],
                scan_time=t1-t0, nzeros_time=t2-t1)

if __name__ == '__main__':
    windows = [
        (mp.mpf('1000000000000.0'), 40, "letter40-site-1e12"),
        (mp.mpf('1000000005000.0'), 16, "neffpop-site-A"),
        (mp.mpf('999999995000.0'), 16, "neffpop-site-B"),
    ]
    results = []
    for T_center, n_sp, label in windows:
        r = turing_certify(T_center, n_sp, dps=25, label=label)
        results.append(r)
    json.dump(results, open('/data/Riemann/results/turing_certify_1e12_windows.json', 'w'), indent=1)
    print("ALL DONE. Summary:", [(r['label'], r['certified']) for r in results])
