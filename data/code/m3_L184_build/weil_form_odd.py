"""
m3-L184 build: matrix assembly for the odd-parity block, reusing the O(N) J_sin precomputation
architecture from data/code/m3_L177_build/weil_form2.py (validated there; the only things that
change are the closed-form g_jk/psihat functions themselves, per derivation_notes.md).
"""
import sys, time
sys.path.insert(0, '.')
import mpmath as mp
from basis_odd import psihat, g_odd_closed, w


def mangoldt(n):
    if n < 2:
        return mp.mpf(0)
    m, p, d = n, None, 2
    while d * d <= m:
        if m % d == 0:
            p = d
            while m % d == 0:
                m //= d
            break
        d += 1
    if p is None:
        p, m = m, 1
    return mp.log(p) if m == 1 else mp.mpf(0)


def prime_powers_upto(x):
    return [n for n in range(2, int(mp.floor(x)) + 1) if mangoldt(n) != 0]


def precompute_Jsin(N, L, log=True):
    """J_sin(w_m) = INT_0^L e^{-t/2} sin(w_m t) / (1-e^{-2t}) dt, m=1..N (no m=0 term for odd)."""
    t0 = time.time()
    Jsin = {}
    for m in range(1, N + 1):
        wm = w(m, L)

        def integrand(t, wm=wm):
            return mp.e ** (-t / 2) * mp.sin(wm * t) / (1 - mp.e ** (-2 * t))

        val = mp.quad(integrand, [0, L])
        Jsin[m] = val
        if log and m % 20 == 0:
            print(f"  J_sin: m={m}/{N} done [{time.time()-t0:.1f}s]", flush=True)
    return Jsin


def precompute_diag_arch(N, L, log=True):
    """Full finite diagonal archimedean-integral-over-[0,L] piece for the odd block, m=1..N."""
    t0 = time.time()
    out = {}
    for m in range(1, N + 1):
        def integrand(t, m=m):
            gmm = g_odd_closed(m, m, t, L)
            num = mp.e ** (-2 * t) - mp.e ** (-t / 2) * gmm
            den = 1 - mp.e ** (-2 * t)
            return num / den

        val = mp.quad(integrand, [0, L])
        out[m] = val
        if log and m % 20 == 0:
            print(f"  diag_arch: m={m}/{N} done [{time.time()-t0:.1f}s]", flush=True)
    return out


def build_matrix_odd(x, N, L, dps, log=True):
    """(N x N) symmetric matrix, indices 1..N (no k=0 term). Returned as 0-indexed NxN python list."""
    mp.mp.dps = dps
    gamma_e = mp.euler
    log_pi = mp.log(mp.pi)
    half_i = mp.mpc(0, mp.mpf('0.5'))

    t0 = time.time()
    psihat_half = {k: psihat(k, half_i, L).real for k in range(1, N + 1)}
    if log:
        print(f"[{time.time()-t0:.1f}s] psihat(i/2) table done", flush=True)

    Jsin = precompute_Jsin(N, L, log=log)
    if log:
        print(f"[{time.time()-t0:.1f}s] J_sin table done", flush=True)

    diag_arch_full = precompute_diag_arch(N, L, log=log)
    if log:
        print(f"[{time.time()-t0:.1f}s] diagonal archimedean table done", flush=True)

    pps = prime_powers_upto(x)
    prime_terms = [(mp.log(mp.mpf(n)), mangoldt(n) / mp.sqrt(mp.mpf(n))) for n in pps]

    # matrix indices 1..N -> python list 0..N-1
    M = [[mp.mpf(0)] * N for _ in range(N)]
    for j in range(1, N + 1):
        wj = w(j, L)
        for k in range(j, N + 1):
            wk = w(k, L)
            delta = 1 if j == k else 0

            # ODD block: pole term has an extra minus sign relative to the even block
            pole = -2 * psihat_half[j] * psihat_half[k] - delta * log_pi

            if delta:
                arch = -gamma_e + 2 * diag_arch_full[j] - mp.log(1 - mp.e ** (-2 * L))
            else:
                A, B = wj - wk, wj + wk
                sign = (-1) ** (j + k)
                # ODD block off-diagonal: PLUS instead of MINUS on the B term (derivation_notes.md)
                off_int = (sign / L) * ((Jsin[k] - Jsin[j]) / A + (Jsin[j] + Jsin[k]) / B)
                arch = -2 * off_int

            prime = mp.mpf(0)
            for logn, wgt in prime_terms:
                prime += wgt * g_odd_closed(j, k, logn, L)
            prime = -2 * prime

            val = pole + arch + prime
            M[j - 1][k - 1] = val
            M[k - 1][j - 1] = val
        if log and j % 20 == 0:
            print(f"  matrix row {j}/{N} assembled [{time.time()-t0:.1f}s]", flush=True)
    return M
