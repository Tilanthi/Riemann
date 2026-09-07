"""
m3-L177 build, part 2: the Weil functional W(g) and the matrix M_jk = W(g_jk), built from the
validated closed forms in basis.py. Own KAT-1-equivalent gate: the explicit formula (poles +
archimedean + primes, applied to an actual test function g via its OWN autocorrelation) checked
against a direct sum over the zeros themselves -- built independently, not copied from BEAST's
KAT-1 numbers (though the target magnitudes are a useful sanity cross-check since both instruments
must be computing the same classical Weil explicit formula).
"""
import sys, time
sys.path.insert(0, '.')
import mpmath as mp
from basis import phihat, g_closed, w


def gl_nodes_weights(a, b, degree):
    """Robust GL nodes/weights on [a,b] using numpy.polynomial.legendre at machine precision,
    then refined... simplest robust route: use mpmath's own tanh-sinh/GL via mp.quad with a
    'maxdegree' won't give us reusable nodes directly, so instead build GL nodes via the
    standard Newton iteration on Legendre polynomials at full working precision."""
    n = degree
    nodes = []
    weights = []
    for i in range(1, n + 1):
        # initial guess (Chebyshev-ish), refine via Newton on Legendre polynomial P_n
        x0 = mp.cos(mp.pi * (i - mp.mpf('0.25')) / (n + mp.mpf('0.5')))
        x = x0
        for _ in range(100):
            p0, p1 = mp.mpf(1), mp.mpf(0)
            pm1 = mp.mpf(1)
            p_prev, p_cur = mp.mpf(1), x
            if n == 0:
                break
            a0, a1 = mp.mpf(1), x
            for k in range(2, n + 1):
                a0, a1 = a1, ((2 * k - 1) * x * a1 - (k - 1) * a0) / k
            pn = a1 if n >= 1 else mp.mpf(1)
            # derivative via recurrence: P_n'(x) = n/(x^2-1) * (x P_n(x) - P_{n-1}(x))
            if n == 1:
                pnm1 = mp.mpf(1)
            else:
                b0, b1 = mp.mpf(1), x
                for k in range(2, n):
                    b0, b1 = b1, ((2 * k - 1) * x * b1 - (k - 1) * b0) / k
                pnm1 = b1 if n >= 2 else mp.mpf(1)
            dpn = n * (x * pn - pnm1) / (x * x - 1)
            dx = pn / dpn
            x = x - dx
            if abs(dx) < mp.mpf(10) ** (-mp.mp.dps - 5):
                break
        nodes.append(x)
        # weight: 2 / ((1-x^2) [P_n'(x)]^2)
        b0, b1 = mp.mpf(1), x
        for k in range(2, n):
            b0, b1 = b1, ((2 * k - 1) * x * b1 - (k - 1) * b0) / k
        pnm1 = b1 if n >= 2 else mp.mpf(1)
        a0, a1 = mp.mpf(1), x
        for k in range(2, n + 1):
            a0, a1 = a1, ((2 * k - 1) * x * a1 - (k - 1) * a0) / k
        pn = a1
        dpn = n * (x * pn - pnm1) / (x * x - 1)
        wt = 2 / ((1 - x * x) * dpn * dpn)
        weights.append(wt)
    # map from [-1,1] to [a,b]
    mid, half = (a + b) / 2, (b - a) / 2
    mapped_nodes = [mid + half * xi for xi in nodes]
    mapped_weights = [half * wi for wi in weights]
    return mapped_nodes, mapped_weights


class GLQuad:
    """Panelled fixed Gauss-Legendre quadrature over [0, L], reusable node/weight set."""
    def __init__(self, L, degree, npanels):
        self.L = L
        self.degree = degree
        self.npanels = npanels
        panel_edges = [L * i / npanels for i in range(npanels + 1)]
        self.nodes = []
        self.weights = []
        for i in range(npanels):
            nodes, weights = gl_nodes_weights(panel_edges[i], panel_edges[i + 1], degree)
            self.nodes.extend(nodes)
            self.weights.extend(weights)

    def integrate_vals(self, vals):
        return sum(w_ * v for w_, v in zip(self.weights, vals))


GAMMA_E = None  # set at runtime once dps is fixed


def mangoldt(n):
    """Von Mangoldt Lambda(n): ln(p) if n = p^m, else 0."""
    if n < 2:
        return mp.mpf(0)
    m = n
    p = None
    d = 2
    while d * d <= m:
        if m % d == 0:
            p = d
            while m % d == 0:
                m //= d
            break
        d += 1
    if p is None:
        p = m  # n itself is prime
        m = 1
    if m == 1:
        return mp.log(p)
    return mp.mpf(0)  # n has more than one distinct prime factor -> not a prime power


def prime_powers_upto(x):
    return [n for n in range(2, int(mp.floor(x)) + 1) if mangoldt(n) != 0]


def build_matrix(x, N, L, glq, dps, log=True):
    """Build the (N+1)x(N+1) symmetric matrix M_jk = W(g_jk)."""
    mp.mp.dps = dps
    gamma_e = mp.euler
    log_pi = mp.log(mp.pi)
    half_i = mp.mpc(0, mp.mpf('0.5'))

    # precompute phihat_k(i/2) for k=0..N (real numbers)
    phihat_half = [phihat(k, half_i, L).real for k in range(N + 1)]

    # precompute prime powers and their weights
    pps = prime_powers_upto(x)
    prime_terms = [(mp.log(mp.mpf(n)), mangoldt(n) / mp.sqrt(mp.mpf(n))) for n in pps]

    t0 = time.time()
    M = [[mp.mpf(0)] * (N + 1) for _ in range(N + 1)]
    for j in range(N + 1):
        for k in range(j, N + 1):
            delta = 1 if j == k else 0
            # pole term
            pole = 2 * phihat_half[j] * phihat_half[k] - delta * log_pi
            # archimedean term via fixed GL quadrature
            vals = []
            for t in glq.nodes:
                gjk = g_closed(j, k, t, L)
                num = mp.e ** (-2 * t) * delta - mp.e ** (-t / 2) * gjk
                den = 1 - mp.e ** (-2 * t)
                vals.append(num / den if den != 0 else mp.mpf(0))
            # BUG FOUND+FIXED (self-caught via a comparison-script inconsistency, not a silent
            # guess): the archimedean integral is over [0, infinity), but g_jk(t)=0 for t>=L, so
            # for diagonal entries (delta=1) there is a nonzero ANALYTIC TAIL from t=L to infinity
            # of e^{-2t}/(1-e^{-2t}), which the finite-panel GL quadrature on [0,L] alone omits.
            # Closed form: INT_L^inf e^{-2t}/(1-e^{-2t}) dt = -(1/2) ln(1-e^{-2L}) (substitution
            # u=e^{-2t}), verified against a finely-broken adaptive mpmath.quad to 3.3e-52 before
            # trusting it here.
            tail = -delta * mp.log(1 - mp.e ** (-2 * L))
            arch = -gamma_e * delta + 2 * glq.integrate_vals(vals) + tail
            # prime term
            prime = mp.mpf(0)
            for logn, wgt in prime_terms:
                prime += wgt * g_closed(j, k, logn, L)
            prime = -2 * prime

            val = pole + arch + prime
            M[j][k] = val
            M[k][j] = val
        if log and (j % 10 == 0):
            print(f"  row {j}/{N} done [{time.time()-t0:.1f}s]", flush=True)
    return M
