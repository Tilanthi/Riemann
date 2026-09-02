import mpmath as mp

mp.mp.dps = 60

# True Lehmer midpoint/half-gap (from my own T1 zetazero pair, dps=40 originally, refreshed to
# dps=60 string precision by just reusing the T1 value which had 40 correct digits)
m0_true = mp.mpf('7005.081715423783651474532107784179427681')
d = mp.mpf('0.018849248863070093562566142963987658731639385223389')

def make_f(m0, d):
    def f(z, m0=m0, d=d):
        s = mp.mpf('0.5') + 1j*(m0+z)
        Xi_val = mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
        return mp.log(Xi_val / (z**2 - d**2))
    return f

f0 = make_f(m0_true, d)
c0 = mp.taylor(f0, 0, 6)
a5_0 = mp.factorial(5)*c0[5]
a3_0 = mp.factorial(3)*c0[3]
a4_0 = mp.factorial(4)*c0[4]
print('exact-site a3,a4,a5 =', a3_0, a4_0, a5_0)

print()
print("Testing Mac's closed-form law: Delta a_j = -2*j!*eps/d^(j+1) for odd j, ~0 for even j")
for eps in [mp.mpf('1e-13'), mp.mpf('-1e-13'), mp.mpf('5e-13'), mp.mpf('1e-12')]:
    f = make_f(m0_true+eps, d)
    c = mp.taylor(f, 0, 6)
    a3 = mp.factorial(3)*c[3]
    a4 = mp.factorial(4)*c[4]
    a5 = mp.factorial(5)*c[5]
    pred_d3 = -2*mp.factorial(3)*eps/d**4
    pred_d5 = -2*mp.factorial(5)*eps/d**6
    print(f'eps={eps}:')
    print(f'  a3: observed Delta={a3-a3_0}  predicted={pred_d3}  ratio={(a3-a3_0)/pred_d3}')
    print(f'  a4: observed Delta={a4-a4_0}  (should be ~0 at O(eps))')
    print(f'  a5: observed Delta={a5-a5_0}  predicted={pred_d5}  ratio={(a5-a5_0)/pred_d5}')
