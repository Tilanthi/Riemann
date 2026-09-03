import mpmath as mp
import time, sys

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

def find_zeros_near(T_center, n_spacings=40, dps=25, tol=mp.mpf('1e-8')):
    old_dps = mp.mp.dps
    mp.mp.dps = dps
    spacing = 2*mp.pi/mp.log(T_center/(2*mp.pi))
    step = spacing/4
    T_lo = T_center - n_spacings*spacing/2
    n_pts = int(n_spacings*spacing/step) + 1

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
    mp.mp.dps = old_dps
    return zeros, spacing

if __name__ == '__main__':
    T_center = mp.mpf(sys.argv[1]) if len(sys.argv) > 1 else mp.mpf('1e12')
    n_sp = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    mp.mp.dps = 25
    t0 = time.time()
    zeros, spacing = find_zeros_near(T_center, n_spacings=n_sp, dps=25, tol=mp.mpf('1e-8'))
    dt = time.time()-t0
    print(f"T_center={T_center}  mean spacing={float(spacing):.6f}  found {len(zeros)} zeros  [{dt:.1f}s]", flush=True)
    gaps = [float(zeros[i+1]-zeros[i]) for i in range(len(zeros)-1)]
    if gaps:
        print("gaps:", [round(g,6) for g in gaps])
        min_gap = min(gaps)
        idx = gaps.index(min_gap)
        print("tightest gap:", min_gap, " between zeros at", zeros[idx], "and", zeros[idx+1])
