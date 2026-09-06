"""machine2 CYCLE 35 -- the SIGN GROUP of the fold constants, and the a4/a5 extraction spec.

NEW SCRIPT, NEW HASH.  c33 and c34 artefacts are frozen and untouched.  Machinery IMPORTED,
never edited, from the frozen `machine2_c34_refit.py` (Zeta2 evaluator, circle extraction,
fd_weights, series_solve, shift_e, solve_etilde).  The ONE addition is a `dsign` knob:

    D = centre - dsign * p * h_e          (dsign = +1 reproduces c34 exactly)

so that `dsign = -1` reflects the finite-difference grid onto the other side of D*, which is
the physical realisation of the convention change  e -> -e.

WHY.  m1 publishes a4 = +20.47556(13); I publish a4 = -20.4755387553904125...  m3 (`82547c4`)
declines to compute a4/a5 for want of the extraction formula and asks for it.  Handing over a
spec whose sign degrees of freedom are implicit would make m3's "independent" a4 inherit the
spec author's convention -- exactly the c33 law (a shared sign convention is invisible to
cross-instrument agreement).  So: enumerate the sign group, measure which element the record
needs, and publish a convention-CLOSED extraction spec.

Four pre-registered predictions (`machine2-c35-PREREG-...md`, commit c6ea857, pushed BEFORE
this file was written):
  P1  m1's b is POSITIVE and m1's a3 POSITIVE (blind search of m1-authored files only)
  P2  reflected grid gives a_n -> (-1)^n a_n to >= 55 s.f. (falsified below 40)
  P3  a4's closed form REQUIRES g[m][n] with m >= 2
  P4  my g[1][0] is NEGATIVE and matches m3's to >= 25 s.f. (no third sign d.o.f.)
"""
import json
import os
import sys
import time
from multiprocessing import Pool

import mpmath as mp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import machine2_c34_refit as C34  # noqa: E402  -- IMPORTED, NEVER EDITED

MMAX, NMAX, NAMES = C34.MMAX, C34.NMAX, C34.NAMES
DSTAR_REFINED = C34.DSTAR_REFINED

# m3's published values (letter170, commit 82547c4) -- quoted, not recomputed
M3_G10 = "-14.1680846707549756060541923597517360089"
M3_G01 = "-37.4819713608428817387593623904468580249"
M3_DSTAR = "0.141733239663887191395415685084185023623144561955016655942867"

_CFG = {}


def _init(cfg):
    _CFG.update(cfg)
    mp.mp.dps = cfg["dps"] + 15


def _node(p):
    """c34's _node, verbatim except for the single `dsign` factor on the D offset."""
    dps, guard = _CFG["dps"], _CFG["guard"]
    r = mp.mpf(_CFG["r_w"])
    N = _CFG["N_w"]
    he = mp.mpf(10) ** (-_CFG["he"])
    ds = _CFG.get("dsign", 1)
    mp.mp.dps = dps + 15
    D = mp.mpf(_CFG["centre"]) - ds * p * he
    Z = C34.Zeta2(D, dps=dps, guard=guard)
    half = mp.mpf(1) / 2
    quarter = N // 4
    base = [Z.xi(half + r * mp.expjpi(mp.mpf(2 * j) / N)) for j in range(quarter + 1)]

    def hval(j):
        j %= N
        if j >= N // 2:
            j -= N // 2
        if j <= quarter:
            return base[j]
        return mp.conj(base[N // 2 - j])

    vals = [hval(j) for j in range(N)]
    out = []
    for k in range(2 * MMAX + 2):
        s = mp.mpc(0)
        for j in range(N):
            s += vals[j] * mp.expjpi(mp.mpf(-2 * k * j) / N)
        out.append((s / N) / r ** k)
    return p, [mp.nstr(v, dps + 5, strip_zeros=False) for v in out]


def run(cfg, pool):
    dps, npts = cfg["dps"], cfg["npts"]
    mp.mp.dps = dps + 15
    ps = list(range(-(npts // 2), npts // 2 + 1))
    t0 = time.time()
    res = {}
    for p, strs in pool.imap_unordered(_node, ps):
        res[p] = [mp.mpmathify(s) for s in strs]
    wall = time.time() - t0
    he = mp.mpf(10) ** (-cfg["he"])
    g = [[None] * (NMAX + 1) for _ in range(MMAX + 1)]
    for m in range(MMAX + 1):
        for n in range(NMAX + 1):
            nodes, wts = C34.fd_weights(n, npts)
            s = mp.mpc(0)
            for idx, p in enumerate(nodes):
                s += wts[idx] * res[p][2 * m]
            g[m][n] = mp.re((s / he ** n) / mp.factorial(n))
    x_raw = C34.series_solve(g, 5)
    et = C34.solve_etilde(g)
    x_rec = C34.series_solve(C34.shift_e(g, et), 5)
    return dict(cfg=cfg, wall=wall, g=g, x_raw=x_raw, x_rec=x_rec, et=et)


# ------------------------------------------------------- closed-form extraction (P3)
def closed_forms():
    """Solve  sum_{m,n} g[m][n] x^m e^n = 0,  x(0)=0,  order by order in e, symbolically.

    Returns sympy expressions for a1..a5 in the symbols g_m_n.  This IS the spec m3 asked
    for; the support of each expression answers P3 by inspection.
    """
    import sympy as sp
    G = {(m, n): sp.Symbol(f"g_{m}_{n}") for m in range(6) for n in range(6)}
    e = sp.Symbol("e")
    A = sp.symbols("a1:6")
    x = sum(A[i] * e ** (i + 1) for i in range(5))
    # g[0][0] is the residual G(0,0); the fold condition is g_0_0 = 0 and the solver
    # enforces x(0)=0, so the constant term is dropped exactly as series_solve does.
    expr = sum(G[(m, n)] * x ** m * e ** n
               for m in range(6) for n in range(6) if not (m == 0 and n == 0))
    ser = sp.Poly(sp.expand(expr), e)
    sol = {}
    for k in range(1, 6):
        c = sp.expand(ser.as_expr().coeff(e, k).subs(sol))
        s = sp.solve(sp.Eq(c, 0), A[k - 1])[0]
        sol[A[k - 1]] = sp.simplify(sp.together(s))
    return [sp.simplify(sol[A[i]].subs(sol)) for i in range(5)], G, A


def support(expr, G):
    return sorted([mn for mn, sym in G.items() if expr.has(sym)])


BASE_A = dict(C34.BASE)
BASE_A["centre"] = DSTAR_REFINED
BASE_A["label"] = "A"

CFGS = [
    dict(BASE_A, label="A_fwd", dsign=1),    # must reproduce c34 cfg A exactly
    dict(BASE_A, label="A_ref", dsign=-1),   # reflected grid  <=>  e -> -e
]

OUT = os.path.join(HERE, "../machine2_c35_signgroup.json")

if __name__ == "__main__":
    mp.mp.dps = 120
    dump = {}
    for c in CFGS:
        with Pool(8, initializer=_init, initargs=(c,)) as pool:
            R = run(c, pool)
        mp.mp.dps = 90
        print(f"\n### {c['label']}  dsign={c['dsign']}  dps={c['dps']} N_w={c['N_w']} "
              f"npts={c['npts']} h_e=1e-{c['he']}  [{R['wall']:.0f}s]", flush=True)
        print(f"   g[0][0] = {mp.nstr(R['g'][0][0], 25)}")
        print(f"   g[1][0] = {mp.nstr(R['g'][1][0], 40)}")
        print(f"   g[0][1] = {mp.nstr(R['g'][0][1], 40)}")
        print(f"   etilde  = {mp.nstr(R['et'], 12)}")
        for i, nm in enumerate(NAMES):
            print(f"   {nm:>3s} rec = {mp.nstr(R['x_rec'][i + 1], 70)}")
        dump[c["label"]] = dict(
            cfg={k: v for k, v in c.items()}, wall=R["wall"],
            g=[[mp.nstr(R["g"][m][n], 60) for n in range(NMAX + 1)] for m in range(MMAX + 1)],
            et=mp.nstr(R["et"], 40),
            raw={nm: mp.nstr(R["x_raw"][i + 1], 70) for i, nm in enumerate(NAMES)},
            rec={nm: mp.nstr(R["x_rec"][i + 1], 70) for i, nm in enumerate(NAMES)})
    with open(OUT, "w") as f:
        json.dump(dump, f, indent=1)

    # ---------------------------------------------------------------- P2 scoring
    print("\n=== P2: reflected grid vs forward grid, predicted a_n -> (-1)^n a_n ===")
    mp.mp.dps = 90
    for i, nm in enumerate(NAMES):
        n = i + 1
        f_ = mp.mpf(dump["A_fwd"]["rec"][nm])
        r_ = mp.mpf(dump["A_ref"]["rec"][nm])
        pred = (-1) ** n * f_
        rel = abs(r_ - pred) / abs(pred)
        sf = -mp.log10(rel) if rel > 0 else mp.inf
        print(f"   {nm:>3s}: fwd={mp.nstr(f_,20)}  ref={mp.nstr(r_,20)}  "
              f"sign_ok={(mp.sign(r_) == mp.sign(pred))}  agree={mp.nstr(sf,4)} s.f.")

    # ---------------------------------------------------------------- P4 scoring
    print("\n=== P4: my g[1][0] vs m3's published g[1][0] (letter170, 82547c4) ===")
    mine = mp.mpf(dump["A_fwd"]["g"][1][0])
    m3 = mp.mpf(M3_G10)
    print(f"   mine = {mp.nstr(mine, 40)}")
    print(f"   m3   = {mp.nstr(m3, 40)}")
    print(f"   sign(mine) = {mp.sign(mine)}   rel diff = {mp.nstr(abs(mine-m3)/abs(m3), 6)}"
          f"   => {mp.nstr(-mp.log10(abs(mine-m3)/abs(m3)), 4)} s.f.")
    mine01 = mp.mpf(dump["A_fwd"]["g"][0][1])
    m301 = mp.mpf(M3_G01)
    print(f"   g[0][1]: mine = {mp.nstr(mine01,25)}   m3 = {mp.nstr(m301,25)}   "
          f"sum (should be ~0 if pure e-flip) = {mp.nstr(mine01+m301,6)}   "
          f"rel = {mp.nstr(abs(mine01+m301)/abs(m301),6)}")

    # ------------------------------------------------- D* cross-evaluator resolution
    print("\n=== cross-evaluator D* resolution actually delivered by 82547c4 ===")
    mp.mp.dps = 120
    mine_ds = mp.mpf(DSTAR_REFINED) - mp.mpf(dump["A_fwd"]["et"])
    m3_ds = mp.mpf(M3_DSTAR)
    d = mine_ds - m3_ds
    print(f"   m2 implied D* (cfg A, own recentring) = {mp.nstr(mine_ds, 60)}")
    print(f"   m3 root-find D* (dps 60)              = {mp.nstr(m3_ds, 60)}")
    print(f"   difference = {mp.nstr(d, 8)}  (ABSOLUTE, in D)")
    print(f"   c34 ask threshold = 1e-77 ABSOLUTE  =>  ratio {mp.nstr(abs(d)/mp.mpf('1e-77'), 6)}")

    # ---------------------------------------------------------------- P3 scoring
    print("\n=== P3: closed forms and their support ===")
    forms, G, A = closed_forms()
    import sympy as sp
    for i, f in enumerate(forms):
        sup = support(f, G)
        mmax_used = max(m for m, n in sup)
        print(f"\n   {NAMES[i]} (order e^{i+1}): support m<= {mmax_used}, terms {sup}")
        print(f"      {sp.simplify(f)}")

    # numerical verification of the closed forms against the measured g table
    print("\n=== closed forms verified against the measured g table (cfg A_fwd) ===")
    mp.mp.dps = 90
    gA = dump["A_fwd"]["g"]
    subs = {G[(m, n)]: sp.Float(gA[m][n], 85) for m in range(6) for n in range(6)
            if m <= MMAX and n <= NMAX}
    for i, f in enumerate(forms):
        v = mp.mpf(str(sp.N(f.subs(subs), 80)))
        ref = mp.mpf(dump["A_fwd"]["raw"][NAMES[i]])
        rel = abs(v - ref) / abs(ref)
        print(f"   {NAMES[i]:>3s}: closed form = {mp.nstr(v, 30)}   pipeline raw = "
              f"{mp.nstr(ref,30)}   rel = {mp.nstr(rel,6)}")

    # P3 second instrument: numerical sensitivity of a4 to g[2][0]
    print("\n=== P3 second instrument: perturb g[2][0] by 1e-30 relative ===")
    mp.mp.dps = 90
    g0 = [[mp.mpf(gA[m][n]) for n in range(NMAX + 1)] for m in range(MMAX + 1)]
    base = C34.series_solve(g0, 5)
    g1 = [row[:] for row in g0]
    g1[2][0] = g1[2][0] * (1 + mp.mpf(10) ** -30)
    pert = C34.series_solve(g1, 5)
    for i, nm in enumerate(NAMES):
        dv = abs(pert[i + 1] - base[i + 1]) / abs(base[i + 1])
        print(f"   {nm:>3s}: |d/rel| = {mp.nstr(dv, 6)}   moves = {dv > 0}")
