"""
m3-L177 build, part 2 REWRITE: efficient O(N) archimedean-integral precomputation instead of the
O(N^2) fixed-panel-GL approach in weil_form.py, which turned out to have TWO real problems, both
self-caught before being trusted:
  (1) fixed-panel GL quadrature does not resolve the archimedean integral's oscillatory content once
      the basis frequency w_k grows with k (checked: lambda_min at N=30 changed by orders of
      magnitude, even sign, between 8/16/24 panels -- not converged at all, an honest failure caught
      by a convergence check before trusting any number);
  (2) naively splitting the (always-finite) combined integrand into separate J_sin/J_cos "moment"
      pieces is UNSAFE for the diagonal (j=k) case: the individual cos-type piece is log-DIVERGENT at
      t=0 even though the full combination [e^{-2t}delta - e^{-t/2}g_jk(t)]/(1-e^{-2t}) is finite --
      caught by direct reasoning about the t->0 limit before ever running a quadrature call that would
      have silently returned nonsense.

FIX, exploiting the closed forms in basis.py:
  - g_jk(t) for j != k decomposes into a linear combination of sin(w_j t) and sin(w_k t) ONLY (no
    cos terms, no cross-frequency sin(w_j+-w_k) terms) -- so off-diagonal archimedean contributions
    need only J_sin(w_m) := INT_0^L e^{-t/2} sin(w_m t) / (1-e^{-2t}) dt for m=0..N, EACH of which is
    individually finite at t=0 (sin(w_m*0)=0 kills the 1/t pole) -- N+1 quadratures total, reused
    across all O(N^2) off-diagonal pairs via the same coefficient algebra as the closed form.
  - Diagonal (j=k=m) contributions are computed as ONE finite quadrature per m directly on the whole
    combined (always-finite) integrand -- another N+1 quadratures, none of them individually unsafe.
  - Total: O(N) adaptive quadratures (not O(N^2)), each on a genuinely convergent integrand, checked
    against the fixed-panel version on a small case before being trusted for the real run.
"""
import sys, time
sys.path.insert(0, '.')
import mpmath as mp
from basis import phihat, g_closed, w


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
    """J_sin(w_m) for m=0..N. J_sin(0)=0 exactly (sin(0)=0 for all t)."""
    t0 = time.time()
    Jsin = [mp.mpf(0)]  # m=0
    for m in range(1, N + 1):
        wm = w(m, L)

        def integrand(t, wm=wm):
            return mp.e ** (-t / 2) * mp.sin(wm * t) / (1 - mp.e ** (-2 * t))

        val = mp.quad(integrand, [0, L])
        Jsin.append(val)
        if log and m % 20 == 0:
            print(f"  J_sin: m={m}/{N} done [{time.time()-t0:.1f}s]", flush=True)
    return Jsin


def precompute_diag_arch(N, L, log=True):
    """The full finite diagonal archimedean-integral-over-[0,L] piece,
    INT_0^L [e^{-2t} - e^{-t/2} g_mm(t)] / (1-e^{-2t}) dt, for m=0..N, computed as ONE combined
    (always-finite) integrand per m -- never split into individually-divergent pieces."""
    t0 = time.time()
    out = []
    for m in range(0, N + 1):
        def integrand(t, m=m):
            gmm = g_closed(m, m, t, L)
            num = mp.e ** (-2 * t) - mp.e ** (-t / 2) * gmm
            den = 1 - mp.e ** (-2 * t)
            return num / den

        val = mp.quad(integrand, [0, L])
        out.append(val)
        if log and m % 20 == 0:
            print(f"  diag_arch: m={m}/{N} done [{time.time()-t0:.1f}s]", flush=True)
    return out


def build_matrix_fast(x, N, L, dps, log=True):
    mp.mp.dps = dps
    gamma_e = mp.euler
    log_pi = mp.log(mp.pi)
    half_i = mp.mpc(0, mp.mpf('0.5'))
    tail_ln = mp.log(1 - mp.e ** (-2 * L))  # for the analytic t>L tail on diagonal entries

    t0 = time.time()
    phihat_half = [phihat(k, half_i, L).real for k in range(N + 1)]
    if log:
        print(f"[{time.time()-t0:.1f}s] phihat(i/2) table done", flush=True)

    Jsin = precompute_Jsin(N, L, log=log)
    if log:
        print(f"[{time.time()-t0:.1f}s] J_sin table done", flush=True)

    diag_arch_full = precompute_diag_arch(N, L, log=log)
    if log:
        print(f"[{time.time()-t0:.1f}s] diagonal archimedean table done", flush=True)

    pps = prime_powers_upto(x)
    prime_terms = [(mp.log(mp.mpf(n)), mangoldt(n) / mp.sqrt(mp.mpf(n))) for n in pps]

    M = [[mp.mpf(0)] * (N + 1) for _ in range(N + 1)]
    for j in range(N + 1):
        wj = w(j, L)
        for k in range(j, N + 1):
            wk = w(k, L)
            delta = 1 if j == k else 0

            pole = 2 * phihat_half[j] * phihat_half[k] - delta * log_pi

            if delta:
                arch = -gamma_e + 2 * diag_arch_full[j] - mp.log(1 - mp.e ** (-2 * L))
            else:
                if j == 0 or k == 0:
                    m = k if j == 0 else j
                    coeff = mp.sqrt(2) * ((-1) ** (m + 1)) / (L * w(m, L))
                    off_int = coeff * Jsin[m]
                else:
                    A, B = wj - wk, wj + wk
                    sign = (-1) ** (j + k)
                    off_int = (sign / L) * ((Jsin[k] - Jsin[j]) / A - (Jsin[j] + Jsin[k]) / B)
                arch = -2 * off_int  # (the "-e^{-t/2}g_jk" part only; no e^{-2t}delta, no tail off-diag)

            prime = mp.mpf(0)
            for logn, wgt in prime_terms:
                prime += wgt * g_closed(j, k, logn, L)
            prime = -2 * prime

            val = pole + arch + prime
            M[j][k] = val
            M[k][j] = val
        if log and j % 20 == 0:
            print(f"  matrix row {j}/{N} assembled [{time.time()-t0:.1f}s]", flush=True)
    return M
