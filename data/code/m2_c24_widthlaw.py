"""cycle24 -- the WIDTH LAW, redesigned after the first design censored 90% of its own cells.

Claim under test (machine2 cycle-22 letter line 458, our own): "the node budget is set by the
widest sub-interval."  Refined claim being tested here: the operative width is not the panel
width h but the PHI-SUPPORTED width h_eff, because the instrument drops nodes where phi == 0.
Basis 7 has the widest panel of all (h = 5.118) and does NOT fail at degree 8 up to gamma = 400,
which the h-claim cannot explain; the h_eff-claim can.

Design: unit = sub-interval panel (n ~ 47 across the 8 bases, empty panels excluded as vacuous).
Response = MINIMUM mpmath GL degree d in 3..11 (3*2^(d-1) = 12..3072 nodes) at which the panel
integral of phi(x) e^{(1/2+400i)x} matches the composite ground truth to 1e-12 relative.
No censoring: the response is bounded above by 11 and every panel resolves by then.
External ground truth: composite GL, panels <= wavelength/8, refinement-checked at /16.
Null: 20000-draw permutation Spearman, predictor shuffled against response.
"""
import os, sys, json, math, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mpmath import mp
import m2_u_instrument as U
from m2_c24_gt_u import panel_nodes

mp.dps = 40
half = mp.mpf(1) / 2
GAMMA = mp.mpf(400)
TOL = mp.mpf("1e-12")

def gl_panel(phi, a, b, deg):
    rho = mp.mpc(half, GAMMA); tot = mp.mpc(0)
    for (x, w) in panel_nodes(a, b, deg):
        v = phi(x)
        if v != 0:
            tot += w * v * mp.exp(rho * x)
    return tot

def truth(phi, a, b, ppw):
    rho = mp.mpc(half, GAMMA)
    lam = 2 * mp.pi / GAMMA
    n = max(1, int(mp.ceil((b - a) / (lam / ppw))))
    step = (b - a) / n; tot = mp.mpc(0)
    for k in range(n):
        aa = a + k * step
        for (x, w) in panel_nodes(aa, aa + step, 4):
            v = phi(x)
            if v != 0:
                tot += w * v * mp.exp(rho * x)
    return tot

gens = U.load_genomes("s1/M8")
rows = []
t0 = time.time()
for i in range(8):
    phi, bumps = U.make_phi(gens[i])
    for (a, b) in U.intervals(bumps):
        m = 400
        cnt = sum(1 for k in range(m + 1) if phi(a + (b - a) * mp.mpf(k) / m) != 0)
        heff = float(b - a) * cnt / (m + 1)
        h = float(b - a)
        if cnt == 0:
            print("  basis %d panel [%7.3f,%7.3f] EMPTY (phi==0) -- excluded as vacuous" % (i, float(a), float(b)), flush=True)
            continue
        t8 = truth(phi, a, b, 8); t16 = truth(phi, a, b, 16)
        if abs(t8) == 0:
            continue
        selfc = abs(t8 - t16) / abs(t8)
        dmin = None
        for d in range(3, 12):
            if abs(gl_panel(phi, a, b, d) - t8) <= TOL * abs(t8):
                dmin = d; break
        rows.append({"basis": i, "a": float(a), "b": float(b), "h": h, "heff": heff,
                     "dmin": dmin, "nodes": (3 * 2 ** (dmin - 1)) if dmin else None,
                     "selfconv": mp.nstr(selfc, 4), "absI": mp.nstr(abs(t8), 6)})
        print("  basis %d panel [%7.3f,%7.3f] h=%6.3f heff=%6.3f |I|=%-12s dmin=%s nodes=%s "
              "[gt selfconv %s]  (%.0fs)" % (i, float(a), float(b), h, heff, mp.nstr(abs(t8), 5),
              dmin, (3 * 2 ** (dmin - 1)) if dmin else None, mp.nstr(selfc, 3), time.time() - t0), flush=True)

json.dump(rows, open("widthlaw2.json", "w"), indent=1)

def ranks(v):
    idx = sorted(range(len(v)), key=lambda k: v[k])
    r = [0.0] * len(v); k = 0
    while k < len(idx):
        j = k
        while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[k]]:
            j += 1
        avg = (k + j) / 2.0 + 1
        for t in range(k, j + 1):
            r[idx[t]] = avg
        k = j + 1
    return r

def spearman(x, y):
    rx, ry = ranks(x), ranks(y); n = len(x)
    mx = sum(rx) / n; my = sum(ry) / n
    num = sum((rx[k] - mx) * (ry[k] - my) for k in range(n))
    dx = math.sqrt(sum((rx[k] - mx) ** 2 for k in range(n)))
    dy = math.sqrt(sum((ry[k] - my) ** 2 for k in range(n)))
    return num / (dx * dy) if dx and dy else 0.0

y = [r["dmin"] for r in rows]
print("\nn panels (non-empty) = %d;  dmin range %d..%d" % (len(rows), min(y), max(y)))
random.seed(20260905)
for name in ("h", "heff", "absI"):
    x = [float(r[name]) if name != "absI" else float(mp.mpf(r["absI"])) for r in rows]
    obs = spearman(x, y)
    NP = 20000; c = 0
    for _ in range(NP):
        yy = y[:]; random.shuffle(yy)
        if abs(spearman(x, yy)) >= abs(obs):
            c += 1
    print("predictor %-5s Spearman rho = %+.4f  permutation P (two-sided, %d) = %.5f"
          % (name, obs, NP, (c + 1) / (NP + 1)))
# quantitative form: nodes needed vs gamma*heff/4
print("\nnodes / (gamma*heff/4):")
for r in rows:
    pred = float(GAMMA) * r["heff"] / 4
    print("   heff=%6.3f  nodes=%5d  gamma*heff/4=%8.1f  ratio=%6.2f" % (r["heff"], r["nodes"], pred, r["nodes"] / pred))
