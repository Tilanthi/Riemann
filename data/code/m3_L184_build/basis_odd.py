"""
m3-L184 build: odd-parity basis functions, closed forms derived from scratch (derivation_notes.md),
validated against direct numerical quadrature before being trusted for anything. No code imported
from BEAST's c46_parity.py -- only their docstring's basis DEFINITION was read as a specification.
"""
import mpmath as mp


def w(k, L):
    return 2 * mp.pi * k / L


def psi_val(k, s, L):
    if abs(s) > L / 2:
        return mp.mpf(0)
    return mp.sqrt(2 / L) * mp.sin(w(k, L) * s)


def psihat(k, r, L):
    """Closed form for INT psi_k(s) e^{i r s} ds, valid for any complex r."""
    wk = w(k, L)
    if r == wk or r == -wk:
        eps = mp.mpf('1e-30')
        r = r + eps
    return mp.sqrt(2 / L) * mp.mpc(0, 1) * ((-1) ** k) * mp.sin(r * L / 2) * 2 * wk / (r ** 2 - wk ** 2)


def g_odd_closed(j, k, t, L):
    """Closed form for g_jk^odd(t) = INT psi_j(s) psi_k(s+t) ds, using evenness (valid for all real t)."""
    at = abs(t)
    if at >= L:
        return mp.mpf(0)
    wj, wk = w(j, L), w(k, L)
    if j == k:
        return (mp.cos(wk * at) * (L - at) + mp.sin(wk * at) / wk) / L
    A, B = wj - wk, wj + wk
    sign = (-1) ** (j + k)
    return (sign / L) * ((mp.sin(wk * at) - mp.sin(wj * at)) / A + (mp.sin(wj * at) + mp.sin(wk * at)) / B)


def g_odd_direct_quadrature(j, k, t, L):
    lo = max(-L / 2, -L / 2 - t)
    hi = min(L / 2, L / 2 - t)
    if lo >= hi:
        return mp.mpf(0)
    return mp.quad(lambda s: psi_val(j, s, L) * psi_val(k, s + t, L), [lo, hi])


def psihat_direct_quadrature(k, r, L):
    return mp.quad(lambda s: psi_val(k, s, L) * mp.e ** (mp.mpc(0, 1) * r * s), [-L / 2, L / 2])


if __name__ == '__main__':
    mp.mp.dps = 40
    L = mp.mpf('5.0')
    import random
    random.seed(2)

    print("=== validating psihat closed form vs direct quadrature ===")
    maxerr = mp.mpf(0)
    for _ in range(8):
        k = random.randint(1, 6)
        r = mp.mpf(random.uniform(-3, 3))
        closed = psihat(k, r, L)
        direct = psihat_direct_quadrature(k, r, L)
        err = abs(closed - direct)
        maxerr = max(maxerr, err)
        print(f"k={k} r={mp.nstr(r,6)}: closed={mp.nstr(closed,15)} direct={mp.nstr(direct,15)} "
              f"err={mp.nstr(err,5)}")
    assert maxerr < mp.mpf('1e-30')
    print(f"PASS, max err {mp.nstr(maxerr,5)}\n")

    print("=== validating psihat at r=i/2 (complex) vs direct quadrature ===")
    maxerr2 = mp.mpf(0)
    for k in range(1, 6):
        r = mp.mpc(0, mp.mpf('0.5'))
        closed = psihat(k, r, L)
        direct = psihat_direct_quadrature(k, r, L)
        err = abs(closed - direct)
        maxerr2 = max(maxerr2, err)
        print(f"k={k}: closed={mp.nstr(closed,15)} direct={mp.nstr(direct,15)} err={mp.nstr(err,5)}")
    assert maxerr2 < mp.mpf('1e-30')
    print(f"PASS, max err {mp.nstr(maxerr2,5)}\n")

    print("=== validating g_odd closed form vs direct quadrature ===")
    maxerr3 = mp.mpf(0)
    for _ in range(12):
        j = random.randint(1, 6)
        k = random.randint(1, 6)
        t = mp.mpf(random.uniform(0, float(L) - 0.01))
        closed = g_odd_closed(j, k, t, L)
        direct = g_odd_direct_quadrature(j, k, t, L)
        err = abs(closed - direct)
        maxerr3 = max(maxerr3, err)
        print(f"j={j} k={k} t={mp.nstr(t,6)}: closed={mp.nstr(closed,15)} direct={mp.nstr(direct,15)} "
              f"err={mp.nstr(err,5)}")
    assert maxerr3 < mp.mpf('1e-30')
    print(f"PASS, max err {mp.nstr(maxerr3,5)}\n")

    print("=== orthonormality: g_odd(j,k,0) == delta_jk ===")
    maxerr4 = mp.mpf(0)
    for j in range(1, 8):
        for k in range(1, 8):
            val = g_odd_closed(j, k, mp.mpf(0), L)
            expected = mp.mpf(1) if j == k else mp.mpf(0)
            maxerr4 = max(maxerr4, abs(val - expected))
    print(f"max err vs delta_jk: {mp.nstr(maxerr4,5)}")
    assert maxerr4 < mp.mpf('1e-35')
    print("PASS\n")

    print("=== symmetry: g_odd(j,k,t) == g_odd(k,j,t) ===")
    maxerr5 = mp.mpf(0)
    for _ in range(10):
        j = random.randint(1, 6)
        k = random.randint(1, 6)
        t = mp.mpf(random.uniform(0, float(L) - 0.01))
        maxerr5 = max(maxerr5, abs(g_odd_closed(j, k, t, L) - g_odd_closed(k, j, t, L)))
    print(f"max err: {mp.nstr(maxerr5,5)}")
    assert maxerr5 < mp.mpf('1e-35')
    print("PASS -- all odd-basis closed forms validated independently.")
