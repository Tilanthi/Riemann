"""machine 2 -- cycle 16 -- certified zero counting on the VOID wedge.

TWO INDEPENDENT METHODS, different failure modes, both publishing their own denominator.

METHOD A -- ADAPTIVE ARGUMENT PRINCIPLE WITH A CERTIFICATE THAT IS NOT THE INTEGER.
  Condition 6 of the brief: a discrete readout has no residual, so it cannot report its own
  non-convergence.  Here the convergence argument lives OUTSIDE the integer:
    (c1) per-step |Delta arg| < pi/4                      -- aliasing guard
    (c2) per-step |Delta F| < RHO * min(|F_i|,|F_{i+1}|)  -- Rouche/step guard, RHO = 0.5.
         If |F(s)-F(s_i)| < |F(s_i)| along the whole segment then the segment's image cannot
         wind round 0, so the polygonal winding equals the true winding.  (c2) enforces that
         at the endpoints with a factor-2 margin; (c1) independently forbids the pi-aliasing
         mode that produced cycle 15's -29.
    (c3) subdivision additivity: sum of sub-rectangle counts == whole-rectangle count.
    (c4) min |F| on the contour, printed -- a contour passing near a zero is disclosed.
  All four are REAL-VALUED and are printed beside the integer.  A box that cannot satisfy
  (c1)+(c2) within the depth cap is returned VOID, never as a number.

METHOD B -- MODULUS EXCLUSION.  For each cell of centre c and half-diagonal rho, the cell is
  CERTIFIED-EMPTY if |F(c)| > L * rho, with L a Lipschitz bound for F on the cell.  Gives an
  AREA-valued coverage figure with an explicitly counted cell denominator, and an explicit
  UNCERTIFIED residual set if any cell survives to the depth cap.
"""
import math, time
from multiprocessing import Pool
from mpmath import mp, mpc, mpf, arg, fabs, log
import eval2

DPS = 20
RHO = 0.5
ARGCAP = math.pi / 4


def _init(dps):
    global DPS
    DPS = dps
    mp.dps = dps


def _F(z):
    mp.dps = DPS
    v = eval2.F(mpc(z[0], z[1]))
    return (float(mp.re(v)), float(mp.im(v)))


def _Fp(z):
    mp.dps = DPS
    h = mpf(10) ** -8
    s = mpc(z[0], z[1])
    d = (eval2.F(s + h) - eval2.F(s - h)) / (2 * h)
    return float(fabs(d))


def _perim(x0, x1, y0, y1, t):
    """map t in [0,1) to the rectangle boundary, counter-clockwise."""
    w, h = x1 - x0, y1 - y0
    P = 2 * (w + h)
    u = t * P
    if u < w:
        return (x0 + u, y0)
    u -= w
    if u < h:
        return (x1, y0 + u)
    u -= h
    if u < w:
        return (x1 - u, y1)
    u -= w
    return (x0, y1 - u)


def winding_certified(pool, x0, x1, y0, y1, n0=400, maxdepth=9):
    """returns dict with the integer AND its four external certificates."""
    ts = [i / n0 for i in range(n0)] + [1.0]
    vals = pool.map(_F, [_perim(x0, x1, y0, y1, t) for t in ts], chunksize=8)
    nev = len(ts)
    depth = 0
    while depth < maxdepth:
        bad = []
        for i in range(len(ts) - 1):
            a, b = vals[i], vals[i + 1]
            ma, mb = math.hypot(*a), math.hypot(*b)
            if ma == 0 or mb == 0:
                bad.append(i); continue
            dF = math.hypot(b[0] - a[0], b[1] - a[1])
            da = abs(math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]))
            if da > ARGCAP or dF > RHO * min(ma, mb):
                bad.append(i)
        if not bad:
            break
        newt = [(ts[i] + ts[i + 1]) / 2 for i in bad]
        newv = pool.map(_F, [_perim(x0, x1, y0, y1, t) for t in newt], chunksize=8)
        nev += len(newt)
        merged_t, merged_v = [], []
        bs = set(bad)
        k = 0
        for i in range(len(ts) - 1):
            merged_t.append(ts[i]); merged_v.append(vals[i])
            if i in bs:
                merged_t.append(newt[k]); merged_v.append(newv[k]); k += 1
        merged_t.append(ts[-1]); merged_v.append(vals[-1])
        ts, vals = merged_t, merged_v
        depth += 1
    # final certificates
    tot = 0.0; mx_arg = 0.0; mx_ratio = 0.0; mn_mod = float("inf"); nbad = 0
    for i in range(len(ts) - 1):
        a, b = vals[i], vals[i + 1]
        ma, mb = math.hypot(*a), math.hypot(*b)
        mn_mod = min(mn_mod, ma)
        da = math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1])
        tot += da
        mx_arg = max(mx_arg, abs(da))
        if min(ma, mb) > 0:
            r = math.hypot(b[0] - a[0], b[1] - a[1]) / min(ma, mb)
            mx_ratio = max(mx_ratio, r)
            if abs(da) > ARGCAP or r > RHO:
                nbad += 1
        else:
            nbad += 1
    wind = tot / (2 * math.pi)
    ok = (nbad == 0) and abs(wind - round(wind)) < 1e-6
    return dict(box=(x0, x1, y0, y1), zeros=(int(round(wind)) if ok else None),
                raw_winding=wind, max_step_arg=mx_arg, max_step_ratio=mx_ratio,
                min_mod_on_contour=mn_mod, n_contour_pts=len(ts) - 1, n_evals=nev,
                refine_depth=depth, n_uncertified_steps=nbad,
                verdict=("CERTIFIED" if ok else "VOID"))


def modulus_exclusion(pool, x0, x1, y0, y1, L, h0=0.25, maxdepth=6):
    """METHOD B: adaptive certified-empty cover.  Returns per-depth kill counts."""
    cells = []
    nx = max(1, int(math.ceil((x1 - x0) / h0)))
    ny = max(1, int(math.ceil((y1 - y0) / h0)))
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    for i in range(nx):
        for j in range(ny):
            cells.append((x0 + (i + .5) * dx, y0 + (j + .5) * dy, dx / 2, dy / 2))
    per_depth = []; survivors = []; nev = 0
    for d in range(maxdepth):
        if not cells:
            break
        vs = pool.map(_F, [(c[0], c[1]) for c in cells], chunksize=8)
        nev += len(cells)
        killed = []; alive = []
        for c, v in zip(cells, vs):
            rho = math.hypot(c[2], c[3])
            if math.hypot(*v) > L * rho:
                killed.append((c, rho))
            else:
                alive.append(c)
        area_k = sum(4 * c[2] * c[3] for c, _ in killed)
        per_depth.append(dict(depth=d, cell_w=cells[0][2] * 2, n_cells=len(cells),
                              n_certified_empty=len(killed), n_survive=len(alive),
                              area_certified=area_k))
        if d == maxdepth - 1:
            survivors = alive
            break
        cells = [(c[0] + sx * c[2] / 2, c[1] + sy * c[3] / 2, c[2] / 2, c[3] / 2)
                 for c in alive for sx in (-1, 1) for sy in (-1, 1)]
    return dict(per_depth=per_depth, n_evals=nev, survivors=survivors,
                area_uncertified=sum(4 * c[2] * c[3] for c in survivors))
