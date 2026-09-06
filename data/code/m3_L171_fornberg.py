"""
m3-L171 -- Fornberg (1988/1998) finite-difference weight generator, at mpmath arbitrary precision.
Standard, published algorithm (SIAM Rev. 40:685-691, 1998; Math. Comp. 51:699-706, 1988), NOT an
ad hoc scheme -- chosen deliberately per house "search first" discipline instead of improvising a
finite-difference formula from scratch. Transcribed directly from the reference MATLAB pseudocode
(Scholarpedia "Finite difference method" article, "Numerically fast and stable algorithms" section)
into mpmath, 0-indexed.

weights(z, x, m) -> mp.matrix of shape (m+1, len(x)): row k, col i is the weight on f(x[i]) in the
k-th derivative estimate at the point z, exact for all polynomials up to the maximum degree the
node count supports.
"""
import mpmath as mp


def fd_weights(z, x, m):
    x = [mp.mpf(xx) if not isinstance(xx, mp.mpc) else xx for xx in x]
    z = mp.mpf(z)
    n = len(x) - 1
    c = [[mp.mpf(0)] * len(x) for _ in range(m + 1)]
    c1 = mp.mpf(1)
    c4 = x[0] - z
    c[0][0] = mp.mpf(1)
    for i in range(1, n + 1):
        mn = min(i, m)
        c2 = mp.mpf(1)
        c5 = c4
        c4 = x[i] - z
        for j in range(i):
            c3 = x[i] - x[j]
            c2 = c2 * c3
            if j == i - 1:
                for k in range(mn, 0, -1):
                    c[k][i] = c1 * (k * c[k - 1][i - 1] - c5 * c[k][i - 1]) / c2
                c[0][i] = -c1 * c5 * c[0][i - 1] / c2
            for k in range(mn, 0, -1):
                c[k][j] = (c4 * c[k][j] - k * c[k - 1][j]) / c3
            c[0][j] = c4 * c[0][j] / c3
        c1 = c2
    return c


if __name__ == '__main__':
    mp.mp.dps = 30
    # Validate against the exact worked example in the Scholarpedia article:
    # weights(0, -2:2, 6) should reproduce (row = derivative order 0..6, col = node -2..2):
    #   [0,0,1,0,0]
    #   [1/12,-2/3,0,2/3,-1/12]
    #   [-1/12,4/3,-5/2,4/3,-1/12]
    #   [-1/2,1,0,-1,1/2]
    #   [1,-4,6,-4,1]
    #   [0,0,0,0,0]
    #   [0,0,0,0,0]
    expected = [
        [0, 0, 1, 0, 0],
        [mp.mpf(1) / 12, mp.mpf(-2) / 3, 0, mp.mpf(2) / 3, mp.mpf(-1) / 12],
        [mp.mpf(-1) / 12, mp.mpf(4) / 3, mp.mpf(-5) / 2, mp.mpf(4) / 3, mp.mpf(-1) / 12],
        [mp.mpf(-1) / 2, 1, 0, -1, mp.mpf(1) / 2],
        [1, -4, 6, -4, 1],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    C = fd_weights(0, [-2, -1, 0, 1, 2], 6)
    maxerr = mp.mpf(0)
    for k in range(7):
        for i in range(5):
            err = abs(C[k][i] - expected[k][i])
            maxerr = max(maxerr, err)
    print("max abs error vs Scholarpedia worked example weights(0,-2:2,6):", maxerr)
    assert maxerr < mp.mpf('1e-25'), "Fornberg implementation does not match the published example"
    print("PASS: matches the published worked example to dps=30 precision.")

    # A second, independent sanity check: standard 5-point central 1st derivative on h-spaced grid
    # should be [1,-8,0,8,-1]/(12h) -- check at h=0.1
    h = mp.mpf('0.1')
    nodes = [-2 * h, -1 * h, 0, h, 2 * h]
    C2 = fd_weights(0, nodes, 1)
    std_first_deriv = [mp.mpf(1) / (12 * h), mp.mpf(-8) / (12 * h), mp.mpf(0),
                        mp.mpf(8) / (12 * h), mp.mpf(-1) / (12 * h)]
    maxerr2 = max(abs(C2[1][i] - std_first_deriv[i]) for i in range(5))
    print("max abs error vs standard 5-pt central 1st-derivative formula (h=0.1):", maxerr2)
    assert maxerr2 < mp.mpf('1e-25')
    print("PASS: matches the standard textbook 5-point central-difference formula.")
