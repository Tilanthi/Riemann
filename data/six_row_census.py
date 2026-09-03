import mpmath as mp
import json

mp.mp.dps = 50

sites = {
 'k922':      (mp.mpf('1329.124268391001118043715163278283138906'), mp.mpf('0.080750394482516803903310862840311531999999999999602')),
 'Lehmer':    (mp.mpf('7005.081715423783651474532107784179427681'), mp.mpf('0.018849248863070094188324195337743816999999999996969')),
 'telescope': (mp.mpf('71732.90855861005319221508830177092217039'), mp.mpf('0.0073507376961615879782070402738387200000000000085966')),
}

def make_Xi(m0):
    def Xi(z):
        s = mp.mpf('0.5') + 1j*(m0+z)
        return mp.mpf('0.5')*s*(s-1)*mp.power(mp.pi, -s/2)*mp.gamma(s/2)*mp.zeta(s)
    return Xi

def make_C(m0, a, b, lam):
    Xi = make_Xi(m0)
    ia = 1j*a
    ib = 1j*b
    def C(z):
        Xi_b = (Xi(z+ib) + Xi(z-ib)) / 2
        return Xi_b**2 - lam*Xi(z+ia)*Xi(z-ia)
    return C

# The six opposite-verdict rows (site, a, b, x0_guess, y0_guess, BEAST's predicted |y|)
rows = [
    ('k922', mp.mpf('0.30'), mp.mpf('0.2490'), mp.mpf('-0.0312901'), mp.mpf('0.0262607')),
    ('k922', mp.mpf('0.30'), mp.mpf('0.25130'), mp.mpf('-0.0318'),   mp.mpf('0.0044484')),
    ('Lehmer', mp.mpf('0.02'), mp.mpf('0.013373'), mp.mpf('0.00000028'), mp.mpf('0.0002831')),
    ('Lehmer', mp.mpf('0.05'), mp.mpf('0.04080'),  mp.mpf('0.00000157'), mp.mpf('0.0008520')),
    ('telescope', mp.mpf('0.10'), mp.mpf('0.0840'), mp.mpf('-0.00184353'), mp.mpf('0.0051639')),
    ('telescope', mp.mpf('0.10'), mp.mpf('0.0842'), mp.mpf('-0.00185202'), mp.mpf('0.0027084')),
]

lam = mp.mpf('0.5')
results = []
for site, a, b, x0, y0 in rows:
    m0, d = sites[site]
    C = make_C(m0, a, b, lam)
    z0 = x0 + 1j*y0
    print(f'=== {site} a={a} b={b}  guess z0={complex(z0)} ===')
    try:
        root = mp.findroot(C, z0, solver='muller', tol=mp.mpf('1e-40'))
        resid = abs(C(root))
        print(f'  converged root = {complex(root)}   |C(root)| = {resid}')
        found_birth = abs(mp.im(root)) > mp.mpf('1e-6') and resid < mp.mpf('1e-30')
        results.append(dict(site=site, a=str(a), b=str(b), guess=str(z0), root=str(root),
                             residual=str(resid), verdict='BIRTH' if found_birth else 'UNCLEAR'))
    except Exception as e:
        print(f'  findroot FAILED: {e}')
        results.append(dict(site=site, a=str(a), b=str(b), guess=str(z0), error=str(e), verdict='NO-CONVERGENCE(->clean?)'))
    print()

json.dump(results, open('/data/Riemann/results/six_row_census.json','w'), indent=1)
print('done')
