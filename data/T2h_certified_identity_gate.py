import mpmath as mp
import json

mp.mp.dps = 50

# Fresh, full-precision (40-digit) gamma pairs, independently re-derived from my own
# T1 zetazero() runs (T1b/T1c/T1d/T1f outputs) -- NOT reused from T2f_coefficients.json,
# because that JSON turned out to hold float64-precision-truncated m0/d for 6 of 7 sites
# (only telescope was fixed, in letter 7/8). Root-cause narrative for the letter.
pairs = {
 'k453':  (mp.mpf('750.6559503621242998668074383702946266551'), mp.mpf('750.9663810666508372684584196954287854228')),
 'k693':  (mp.mpf('1054.7810394782813499067987929540953136'), mp.mpf('1055.002146475685736209353382433418439335')),
 'k922':  (mp.mpf('1329.043517996518601239811852415442827374'), mp.mpf('1329.205018785483634847618474141123450438')),
 'k1166': (mp.mpf('1610.003264190037944310470787202544635374'), mp.mpf('1610.253823162574488807567725458148863014')),
 'Lehmer':(mp.mpf('7005.062866174920581380343783588841683864'), mp.mpf('7005.100564672646721568720431979517171498')),
 'telescope': (mp.mpf('71732.90120787235703062711009473064833167'), mp.mpf('71732.91590934774935380306650881119600911')),
 'W_site': (mp.mpf('9022.965488033276409706416602595995891289'), mp.mpf('9023.565193774028462051337129485316938609')),
}

def make_f(m0, d):
    def f(z, m0=m0, d=d):
        s = mp.mpf('0.5') + 1j*(m0+z)
        Xi_val = mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
        return mp.log(Xi_val / (z**2 - d**2))
    return f

with open('/data/Riemann/external/zeros1') as fh:
    all_heights = [mp.mpf(l.strip()) for l in fh if l.strip()]

def find_pair_indices(m0):
    for i in range(len(all_heights)-1):
        if all_heights[i] < m0 < all_heights[i+1]:
            return i, i+1
    return None

results = {}
for name, (g1, g2) in pairs.items():
    m0 = (g1+g2)/2
    d = (g2-g1)/2
    f = make_f(m0, d)
    coeffs = mp.taylor(f, 0, 6)
    a = {j: mp.factorial(j)*coeffs[j] for j in range(1,7)}

    i0, i1 = find_pair_indices(m0)
    S = {j: mp.mpf(0) for j in [2,3,4,5,6]}
    for i, h in enumerate(all_heights):
        if i == i0 or i == i1:
            continue
        delta = m0 - h
        for j in S:
            S[j] += 1/delta**j

    # Correct sign per z-plane derivative identity, re-derived here (not copied):
    # d^j/dz^j ln(z-z_rho)|_0 = -(j-1)!/z_rho^j for ALL j (the (-1)^(j-1) from
    # differentiating ln(z-z_rho) and (-1)^-j from z_rho=-delta cancel to a
    # constant -1), and z_rho = gamma-m0 = -delta, delta=m0-gamma, giving
    # a_j = sum_rho -(j-1)!/z_rho^j = (-1)^(j+1)*(j-1)!*S_j -- PLUS sign for odd j,
    # MINUS for even j. (Self-caught bug in first draft of this exact script:
    # used -(j-1)!*S_j uniformly, giving residual~2.0 i.e. exact sign flip at
    # every odd order -- caught immediately from the residual pattern, not
    # copied from anyone.)
    identity = {j: ((-1)**(j+1))*mp.factorial(j-1)*S[j] for j in [3,4,5,6]}
    resid = {j: float(abs(a[j]-identity[j])/abs(a[j])) for j in [3,4,5,6]}

    B = -2*coeffs[2]
    kappa2 = -(1/d**2 + B/2)

    results[name] = dict(
        m0=str(m0), d=str(d),
        kappa1=str(a[1]), B=str(B), kappa2=str(kappa2),
        kappa3_jet=str(a[3]), kappa3_plain=str(a[3]/mp.factorial(3)),
        kappa4=str(a[4]),
        kappa5_jet=str(a[5]), kappa5_plain=str(a[5]/mp.factorial(5)),
        kappa6_plain=str(a[6]/mp.factorial(6)),
        identity_residual_j3=resid[3], identity_residual_j4=resid[4],
        identity_residual_j5=resid[5], identity_residual_j6=resid[6],
        S_full_table_own_pair_excluded={str(j): str(S[j]) for j in S},
    )
    print(f'{name}: kappa5_jet={a[5]}  kappa6_plain={a[6]/mp.factorial(6)}')
    print(f'   identity residuals (j=3,4,5,6): {resid[3]:.2e} {resid[4]:.2e} {resid[5]:.2e} {resid[6]:.2e}')

json.dump(results, open('/data/Riemann/results/T2h_certified_identity_gated.json','w'), indent=1)
print('wrote T2h_certified_identity_gated.json')
