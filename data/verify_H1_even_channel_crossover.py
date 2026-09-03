import mpmath as mp
mp.mp.dps = 100
m0_true = mp.mpf('7005.081715423783651474532107784179427681')
d = mp.mpf('0.018849248863070094188324195337743816999999999996969')
def make_f(m0, d):
    def f(z, m0=m0, d=d):
        s = mp.mpf('0.5') + 1j*(m0+z)
        Xi_val = mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
        return mp.log(Xi_val / (z**2 - d**2))
    return f
f0 = make_f(m0_true, d)
c0 = mp.taylor(f0, 0, 12)
# BEAST's stated crossovers at Lehmer: n=2: 3.234e-8, n=4: 6.879e-12, n=6: 1.694e-15
for eps in [mp.mpf('1e-16'), mp.mpf('1e-17'), mp.mpf('1e-14')]:
    f = make_f(m0_true+eps, d)
    c = mp.taylor(f, 0, 12)
    dk4, dk6 = c[4]-c0[4], c[6]-c0[6]
    pred4 = 5*c0[5]*eps
    pred6 = 7*c0[7]*eps
    print(f'eps={eps}:  Dk4 ratio={dk4/pred4}   Dk6 ratio={dk6/pred6}')
