"""
m3-L177 build, part 1: the basis Fourier transform phihat_k(r) and correlation g_jk(t), closed forms
derived from scratch (see derivation_notes.md), validated against direct numerical quadrature before
being trusted for anything -- own KAT-2/KAT-3-equivalent gate, built independently (no BEAST code read).
"""
import mpmath as mp


def w(k, L):
    return 2 * mp.pi * k / L


def phi_val(k, s, L):
    """phi_k(s), zero outside [-L/2, L/2]."""
    if abs(s) > L / 2:
        return mp.mpf(0)
    if k == 0:
        return 1 / mp.sqrt(L)
    return mp.sqrt(2 / L) * mp.cos(w(k, L) * s)


def phihat(k, r, L):
    """Closed form for INT phi_k(s) e^{i r s} ds, valid for any complex r."""
    if k == 0:
        # limit-safe form using sinc; mpmath handles r->0 fine via direct formula except literal r=0
        if r == 0:
            return 2 / (mp.sqrt(L)) * (L / 2)  # lim sin(rL/2)/r -> L/2
        return 2 * mp.sin(r * L / 2) / (r * mp.sqrt(L))
    wk = w(k, L)
    if r == wk or r == -wk:
        # removable singularity; evaluate by the limit sin(rL/2)*2r/(r^2-wk^2) -> use L'Hopital
        # d/dr[2r]=2, d/dr[r^2-wk^2]=2r, and sin(rL/2) -> 0 there too (both vanish), so use a tiny
        # perturbation in high precision instead of a hand-coded limit (kept simple & safe)
        eps = mp.mpf('1e-30')
        r = r + eps
    return mp.sqrt(2 / L) * ((-1) ** k) * mp.sin(r * L / 2) * 2 * r / (r ** 2 - wk ** 2)


def g_closed(j, k, t, L):
    """Closed form for g_jk(t) = INT phi_j(s) phi_k(s+t) ds, using evenness (valid for all real t)."""
    at = abs(t)
    if at >= L:
        return mp.mpf(0)
    if j == 0 and k == 0:
        return 1 - at / L
    if j == 0 or k == 0:
        kk = k if j == 0 else j
        wk = w(kk, L)
        return mp.sqrt(2) * ((-1) ** (kk + 1)) * mp.sin(wk * at) / (L * wk)
    if j == k:
        wk = w(k, L)
        return (mp.cos(wk * at) * (L - at) - mp.sin(wk * at) / wk) / L
    # j != k, both >= 1
    wj, wk = w(j, L), w(k, L)
    A, B = wj - wk, wj + wk
    sign = (-1) ** (j + k)
    return (sign / L) * ((mp.sin(wk * at) - mp.sin(wj * at)) / A - (mp.sin(wj * at) + mp.sin(wk * at)) / B)


def g_direct_quadrature(j, k, t, L):
    """Brute-force direct numerical quadrature of the SAME integral, for validation only."""
    lo = max(-L / 2, -L / 2 - t)
    hi = min(L / 2, L / 2 - t)
    if lo >= hi:
        return mp.mpf(0)
    return mp.quad(lambda s: phi_val(j, s, L) * phi_val(k, s + t, L), [lo, hi])


def phihat_direct_quadrature(k, r, L):
    return mp.quad(lambda s: phi_val(k, s, L) * mp.e ** (mp.mpc(0, 1) * r * s), [-L / 2, L / 2])


if __name__ == '__main__':
    mp.mp.dps = 40
    L = mp.mpf('5.0')  # arbitrary test L, not tied to any real x

    print("=== validating phihat closed form vs direct quadrature ===")
    import random
    random.seed(1)
    maxerr = mp.mpf(0)
    for _ in range(8):
        k = random.randint(0, 6)
        r = mp.mpf(random.uniform(-3, 3))
        closed = phihat(k, r, L)
        direct = phihat_direct_quadrature(k, r, L)
        err = abs(closed - direct)
        maxerr = max(maxerr, err)
        print(f"k={k} r={mp.nstr(r,6)}: closed={mp.nstr(closed,15)} direct={mp.nstr(direct,15)} "
              f"err={mp.nstr(err,5)}")
    print(f"max abs error: {mp.nstr(maxerr, 5)}")
    assert maxerr < mp.mpf('1e-30'), "phihat closed form FAILED validation"
    print("PASS\n")

    # also check complex r (needed for r=i/2 evaluation later)
    print("=== validating phihat at complex r (i/2-like values) vs direct quadrature ===")
    maxerr2 = mp.mpf(0)
    for k in range(0, 6):
        r = mp.mpc(0, mp.mpf('0.5'))
        closed = phihat(k, r, L)
        direct = phihat_direct_quadrature(k, r, L)
        err = abs(closed - direct)
        maxerr2 = max(maxerr2, err)
        print(f"k={k} r=i/2: closed={mp.nstr(closed,15)} direct={mp.nstr(direct,15)} err={mp.nstr(err,5)}")
    assert maxerr2 < mp.mpf('1e-30'), "phihat complex-r validation FAILED"
    print("PASS\n")

    print("=== validating g_jk closed form vs direct quadrature ===")
    maxerr3 = mp.mpf(0)
    for _ in range(12):
        j = random.randint(0, 6)
        k = random.randint(0, 6)
        t = mp.mpf(random.uniform(0, float(L) - 0.01))
        closed = g_closed(j, k, t, L)
        direct = g_direct_quadrature(j, k, t, L)
        err = abs(closed - direct)
        maxerr3 = max(maxerr3, err)
        print(f"j={j} k={k} t={mp.nstr(t,6)}: closed={mp.nstr(closed,15)} direct={mp.nstr(direct,15)} "
              f"err={mp.nstr(err,5)}")
    print(f"max abs error: {mp.nstr(maxerr3, 5)}")
    assert maxerr3 < mp.mpf('1e-30'), "g_jk closed form FAILED validation"
    print("PASS\n")

    print("=== orthonormality check: g_jk(0) == delta_jk ===")
    maxerr4 = mp.mpf(0)
    for j in range(0, 8):
        for k in range(0, 8):
            val = g_closed(j, k, mp.mpf(0), L)
            expected = mp.mpf(1) if j == k else mp.mpf(0)
            maxerr4 = max(maxerr4, abs(val - expected))
    print(f"max abs error vs delta_jk: {mp.nstr(maxerr4, 5)}")
    assert maxerr4 < mp.mpf('1e-35')
    print("PASS\n")

    print("=== symmetry check: g_jk(t) == g_kj(t) (evenness consequence) ===")
    maxerr5 = mp.mpf(0)
    for _ in range(10):
        j = random.randint(0, 6)
        k = random.randint(0, 6)
        t = mp.mpf(random.uniform(0, float(L) - 0.01))
        maxerr5 = max(maxerr5, abs(g_closed(j, k, t, L) - g_closed(k, j, t, L)))
    print(f"max abs error: {mp.nstr(maxerr5, 5)}")
    assert maxerr5 < mp.mpf('1e-35')
    print("PASS -- all basis-level closed forms validated independently.")
