import mpmath as mp

mp.mp.dps = 60

m0 = mp.mpf('7005.081715423783651474532107784179427681')
d_true = mp.mpf('0.018849248863070093562566142963987658731639385223389')

def make_f(m0, d):
    def f(z, m0=m0, d=d):
        s = mp.mpf('0.5') + 1j*(m0+z)
        Xi_val = mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
        return mp.log(Xi_val / (z**2 - d**2))
    return f

f0 = make_f(m0, d_true)
c0 = mp.taylor(f0, 0, 6)
a2_0, a5_0, a6_0 = mp.factorial(2)*c0[2], mp.factorial(5)*c0[5], mp.factorial(6)*c0[6]

print("Testing Mac's d-law: Delta kappa_j = -2*delta/d^(j+1) for EVEN j, ~0 for odd j")
for delta in [mp.mpf('1e-18'), mp.mpf('-1e-18'), mp.mpf('5e-19')]:
    f = make_f(m0, d_true+delta)
    c = mp.taylor(f, 0, 6)
    a2 = mp.factorial(2)*c[2]
    a5 = mp.factorial(5)*c[5]
    a6 = mp.factorial(6)*c[6]
    pred2 = -2*delta/d_true**3
    pred6 = -2*delta/d_true**7
    print(f'delta={delta}:')
    print(f'  a2: obs Delta={a2-a2_0}  pred={pred2}  ratio={(a2-a2_0)/pred2}')
    print(f'  a5: obs Delta={a5-a5_0}  (should be ~0)')
    print(f'  a6: obs Delta={a6-a6_0}  pred={pred6}  ratio={(a6-a6_0)/pred6}')
