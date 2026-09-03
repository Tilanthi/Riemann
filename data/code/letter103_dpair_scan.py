from mpmath import mp, mpf, mpc, pi as mp_pi, sqrt as mp_sqrt, gamma as mp_gamma, zeta, besselk, findroot
import time, json

mp.dps = 35

def zeta2_adaptive(s, D, zcut=160, kshell_reltol=mpf('1e-42'), kmax=100000, mmax=100000):
    D = mpf(D); s = mpc(s)
    t1 = zeta(2*s)
    t2 = mp_sqrt(mp_pi)*mp_gamma(s - mpf('0.5'))*D**(1 - 2*s)*zeta(2*s - 1)/mp_gamma(s)
    tot = t1 + t2
    nu = s - mpf('0.5')
    ssum = mpc(0)
    running_abs_scale = mpf(0)
    for k in range(1, kmax+1):
        z = 2*mp_pi*D*k
        inner = mpc(0)
        m = 1
        while m <= mmax:
            arg = z*m
            term = (mpf(m)/k)**nu * besselk(nu, arg)
            inner += term
            if arg > zcut:
                break
            m += 1
        ssum += inner
        running_abs_scale = max(running_abs_scale, abs(inner))
        if abs(inner) < kshell_reltol * running_abs_scale and k > 5:
            break
    return tot + (4*mp_pi**s/mp_gamma(s))*D**(mpf('0.5') - s)*ssum

def zeta2_real(sigma, D):
    return zeta2_adaptive(mpc(sigma, 0), D).real

def find_root_plus(D, guess):
    f = lambda s: zeta2_real(s, D)
    root = findroot(f, guess)
    return root

if __name__ == '__main__':
    Ds = [mpf('0.14'), mpf('0.141'), mpf('0.1415'), mpf('0.1417'),
          mpf('0.14172'), mpf('0.141730'), mpf('0.1417332')]
    guess = mpf('0.5675497245010190350')
    results = []
    for D in Ds:
        t0 = time.time()
        try:
            root = find_root_plus(D, guess)
            gap = root - (1-root)  # rho_+ - rho_- = 2*rho_+ - 1
            dt = time.time()-t0
            print(f"D={float(D):.7f}: rho_+={root}  gap(rho+-rho-)={float(gap):.6e}  [{dt:.1f}s]", flush=True)
            results.append(dict(D=str(D), rho_plus=str(root), gap=float(gap), elapsed_s=dt))
            guess = root  # continuation
        except Exception as e:
            print(f"D={float(D):.7f}: FAILED ({e})")
            break
    json.dump(results, open('/tmp/lambda_lane/dpair_scan_results.json','w'), indent=1)

# push one more point even closer, continue from last root
D_extra = mpf('0.14173323')
t0=time.time()
try:
    root = find_root_plus(D_extra, guess)
    gap = root - (1-root)
    print(f"D={float(D_extra):.8f}: rho_+={root}  gap={float(gap):.6e}  [{time.time()-t0:.1f}s]")
    results.append(dict(D=str(D_extra), rho_plus=str(root), gap=float(gap), elapsed_s=time.time()-t0))
except Exception as e:
    print("FAILED:", e)
json.dump(results, open('/tmp/lambda_lane/dpair_scan_results.json','w'), indent=1)
