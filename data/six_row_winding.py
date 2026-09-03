import mpmath as mp
import json

mp.mp.dps = 30

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

def winding_number(C, center, radius, n_steps=400):
    """Count zeros inside |z-center|<radius via argument principle (numerical contour integral of C'/C, done via phase accumulation)."""
    total_phase = mp.mpf('0')
    prev = None
    pts = []
    for k in range(n_steps+1):
        theta = 2*mp.pi*k/n_steps
        z = center + radius*mp.exp(1j*theta)
        val = C(z)
        pts.append(val)
    # accumulate phase change around the loop
    phase_accum = mp.mpf('0')
    for k in range(1, len(pts)):
        v0, v1 = pts[k-1], pts[k]
        dphase = mp.arg(v1/v0)
        phase_accum += dphase
    winding = phase_accum/(2*mp.pi)
    return winding

lam = mp.mpf('0.5')
rows = [
    ('k922', mp.mpf('0.30'), mp.mpf('0.2490'), mp.mpf('-0.0312901'), mp.mpf('0.0262607')),
    ('k922', mp.mpf('0.30'), mp.mpf('0.25130'), mp.mpf('-0.0318'),   mp.mpf('0.0044484')),
    ('telescope', mp.mpf('0.10'), mp.mpf('0.0840'), mp.mpf('-0.00184353'), mp.mpf('0.0051639')),
    ('telescope', mp.mpf('0.10'), mp.mpf('0.0842'), mp.mpf('-0.00185202'), mp.mpf('0.0027084')),
]

results = []
for site, a, b, x0, y0 in rows:
    m0, d = sites[site]
    C = make_C(m0, a, b, lam)
    center = x0 + 1j*y0
    # radius: half the distance from guess to origin-ish, keep box local and away from d (the removed pair, but pencil has no explicit pair removal here -- it's the raw C_{b,a})
    radius = max(abs(x0), abs(y0)) * mp.mpf('1.5') + d*mp.mpf('0.1')
    print(f'{site} a={a} b={b}: center={complex(center)} radius={float(radius)}')
    w = winding_number(C, center, radius, n_steps=150)
    print(f'  winding number (zero count inside) = {w}')
    results.append(dict(site=site, a=str(a), b=str(b), center=str(center), radius=str(radius), winding=str(w)))

json.dump(results, open('/data/Riemann/results/six_row_winding.json','w'), indent=1)
print('done')
