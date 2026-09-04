"""machine 2 cycle 15 -- measurement stages for the Epstein fold letter.
Each stage is the file that produced the corresponding fold_results*.json; they import the
evaluator module machine2_cycle15_epstein_fold.py (renamed imports below).
Run a stage with:  python3 machine2_cycle15_fold_runs.py <1|2|3|4|5|6|7|8>
"""
import sys

def stage1():
    """cycle 15 -- the fold: where the real pair goes for Delta > Delta*, and what the floor does."""
    from mpmath import mp, mpf, mpc, pi, log, sqrt, findroot, im, re, arg, fabs, exp, euler, matrix, lu_solve, mpmathify
    from machine2_cycle15_epstein_fold import zeta2, Lam, digits
    import json
    
    mp.dps = 40
    
    DSTAR = exp(euler) / (4 * pi)          # m1's analytic collision point, recomputed here
    K_M1 = mpf('3.25301161631896')          # m1's analytic branch coefficient (L103 receipt)
    C2_M1 = mpf('-7.41840343632')           # m1's analytic c2
    
    def rho_plus(D, guess=None):
        """real zero of zeta2 in (1/2,1)."""
        f = lambda x: re(zeta2(mpf(x), D))
        if guess is None:
            guess = mpf('0.56')
        return findroot(f, mpf(guess))
    
    def y_zero(D, guess):
        """zero of Lambda(1/2+iy) on the critical line (Lambda is real there)."""
        f = lambda y: re(Lam(mpf(1) / 2 + 1j * mpf(y), D))
        return findroot(f, mpf(guess))
    
    def winding(D, cx, cy, rx, ry, n=400):
        """number of zeros of zeta2 inside the rectangle centred (cx,cy), half-widths rx,ry,
        by continuous argument tracking of zeta2 along the boundary (pole of zeta2 is at s=1,
        keep it outside the box)."""
        pts = []
        for i in range(n):
            u = mpf(i) / n
            # parametrise the rectangle
            t = 4 * u
            if t < 1:
                s = mpc(cx - rx + 2 * rx * t, cy - ry)
            elif t < 2:
                s = mpc(cx + rx, cy - ry + 2 * ry * (t - 1))
            elif t < 3:
                s = mpc(cx + rx - 2 * rx * (t - 2), cy + ry)
            else:
                s = mpc(cx - rx, cy + ry - 2 * ry * (t - 3))
            pts.append(zeta2(s, D))
        tot = mp.zero
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            d = arg(b / a)
            tot += d
        return tot / (2 * pi)
    
    out = {}
    print("Delta* =", mp.nstr(DSTAR, 20))
    
    # ---------- 1. real side: reproduce m1's certified rho+(0.14), then approach Delta* ----------
    print("\n== real side (Delta < Delta*) ==")
    real_rows = []
    for D in ['0.14', '0.1416', '0.14170', '0.141733', '0.14142135623730950488']:
        Dm = mpf(D)
        r = rho_plus(Dm)
        w = Dm  # placeholder
        u = r - mpf(1) / 2
        floor = (2 * r - 1) / (r * r)
        real_rows.append(dict(D=D, rho_plus=mp.nstr(r, 25), u=mp.nstr(u, 20),
                              u2=mp.nstr(u * u, 20), floor=mp.nstr(floor, 12),
                              Dstar_minus_D=mp.nstr(DSTAR - Dm, 12)))
        print("D=%-24s rho+=%s  u^2=%s  floor=%s" % (D, mp.nstr(r, 20), mp.nstr(u * u, 12), mp.nstr(floor, 10)))
    out['real'] = real_rows
    
    # ---------- 2. complex side: the pair past the fold ----------
    print("\n== critical-line side (Delta > Delta*) ==  predicted y = (k/2)sqrt(D-D*)(1+c2*w^2), w=(k/2)sqrt(D-D*)")
    cx_rows = []
    for D in ['0.1417335', '0.141740', '0.14180', '0.14200', '0.142857142857142857142857', '0.1450', '0.1500', '0.2000']:
        Dm = mpf(D)
        wpred = (K_M1 / 2) * sqrt(Dm - DSTAR)
        ypred = wpred * (1 + C2_M1 * wpred**2)
        try:
            y = y_zero(Dm, ypred if ypred > 0 else mpf('0.01'))
        except Exception as e:
            print("D=%s  root failed: %s" % (D, e))
            continue
        u2 = -(y * y)
        cx_rows.append(dict(D=D, y=mp.nstr(y, 25), y_pred_zeroparam=mp.nstr(ypred, 12),
                            rel_err=mp.nstr((y - ypred) / y, 8), u2=mp.nstr(u2, 20),
                            D_minus_Dstar=mp.nstr(Dm - DSTAR, 12)))
        print("D=%-26s y=%-24s ypred=%-18s relerr=%s" % (D, mp.nstr(y, 20), mp.nstr(ypred, 10), mp.nstr((y - ypred) / y, 6)))
    out['line'] = cx_rows
    
    # ---------- 3. is the pair EXACTLY on the line?  argument principle ----------
    print("\n== zero count in a box around s=1/2 ==")
    for D, rx, ry in [('0.14', mpf('0.15'), mpf('0.15')), ('0.1425', mpf('0.15'), mpf('0.15')),
                      ('0.15', mpf('0.2'), mpf('0.2'))]:
        n = winding(mpf(D), mpf(1) / 2, mp.zero, rx, ry, n=600)
        print("D=%-8s box half-widths (%s,%s):  N = %s" % (D, rx, ry, mp.nstr(n, 12)))
        out.setdefault('winding', []).append(dict(D=D, rx=str(rx), ry=str(ry), N=mp.nstr(n, 12)))
    
    # ---------- 4. off-line search on the complex side: is Re = 1/2 exactly? ----------
    print("\n== 2-D root polish off the line (does it move off Re=1/2?) ==")
    for D in ['0.1425', '0.15']:
        Dm = mpf(D)
        y0 = mpf([r['y'] for r in cx_rows if r['D'].startswith(D[:6])][0]) if any(r['D'].startswith(D[:6]) for r in cx_rows) else None
        # full 2-D complex root find from a perturbed start
        s0 = mpc(mpf('0.53'), y0 if y0 else mpf('0.05'))
        root = findroot(lambda s: zeta2(s, Dm), s0)
        print("D=%-8s  start Re=0.53 -> root = %s   (Re-1/2 = %s)" % (D, mp.nstr(root, 22), mp.nstr(re(root) - mpf(1) / 2, 8)))
        out.setdefault('polish', []).append(dict(D=D, root=mp.nstr(root, 22), re_minus_half=mp.nstr(re(root) - mpf(1) / 2, 8)))
    
    with open('fold_results.json', 'w') as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote fold_results.json")
    

def stage2():
    """cycle 15 part 2 -- class membership (H1)-(H4)/a1 gate, blind zone, off-line census at 1/7."""
    from mpmath import mp, mpf, mpc, pi, log, sqrt, exp, euler, re, im, arg, findroot
    from machine2_cycle15_epstein_fold import zeta2, Lam, digits, set_cut
    import json, math
    
    mp.dps = 25
    set_cut(25)
    
    DSTAR = exp(euler) / (4 * pi)
    K_M1 = mpf('3.25301161631896')
    C2_M1 = mpf('-7.41840343632')
    C_VIS = 2 + euler - log(4 * pi)     # m1's visibility constant
    
    out = {}
    print("C_vis =", mp.nstr(C_VIS, 12))
    
    # ---- 1. Delta -> 1/Delta invariance of the zero set:  zeta2(s,1/D) = D^{2s} zeta2(s,D)
    print("\n== Delta <-> 1/Delta ==")
    rows = []
    for (s, D) in [(mpc('0.7', '1.3'), mpf('0.1417')), (mpc('1.6', '0'), mpf('0.3'))]:
        a = zeta2(s, 1 / D)
        b = D**(2 * s) * zeta2(s, D)
        rows.append(dict(s=str(s), D=str(D), digits=mp.nstr(digits(a, b), 6)))
        print("s=%-16s D=%-8s agreement %s digits" % (s, D, mp.nstr(digits(a, b), 6)))
    out['duality_D'] = rows
    
    # ---- 2. blind zone: floor(D) = (2rho-1)/rho^2 ~ 4k sqrt(D*-D);  when is it < C/log N ?
    print("\n== visibility blind zone below Delta* ==")
    bz = []
    for N in [6, 9, 12, 15]:
        thr = C_VIS / (mpf(N) * log(10))
        # leading order: floor = 8u + O(u^2), u = (k/2)sqrt(D*-D)  => floor = 4k sqrt(w)
        w = (thr / (4 * K_M1))**2
        bz.append(dict(N='1e%d' % N, threshold=mp.nstr(thr, 8), Dstar_minus_D=mp.nstr(w, 8)))
        print("N=1e%-3d threshold=%-14s  blind for Delta*-Delta < %s" % (N, mp.nstr(thr, 8), mp.nstr(w, 6)))
    out['blind_zone'] = bz
    
    # ---- 3. the two readings of the local law, checked against measured roots
    print("\n== local-law reading: m1's gap-coefficient vs L105's offset restatement ==")
    law = []
    for D in ['0.141733', '0.14170', '0.1416']:
        Dm = mpf(D)
        r = findroot(lambda x: re(zeta2(mpf(x), Dm)), mpf('0.51'))
        u = r - mpf(1) / 2
        w = (K_M1 / 2) * sqrt(DSTAR - Dm)
        m1_read = w * (1 + C2_M1 * w**2)                       # rho+ - 1/2  (gap/2)
        m3_read = K_M1 * sqrt(DSTAR - Dm) * (1 + C2_M1 * (DSTAR - Dm))
        law.append(dict(D=D, measured_u=mp.nstr(u, 15),
                        m1_halfgap=mp.nstr(m1_read, 15), m1_relerr=mp.nstr((m1_read - u) / u, 6),
                        L105_restatement=mp.nstr(m3_read, 15), L105_ratio=mp.nstr(m3_read / u, 10)))
        print("D=%-10s u=%-20s m1 %-20s (rel %s)   L105 %-20s (ratio %s)"
              % (D, mp.nstr(u, 12), mp.nstr(m1_read, 12), mp.nstr((m1_read - u) / u, 4),
                 mp.nstr(m3_read, 12), mp.nstr(m3_read / u, 8)))
    out['local_law'] = law
    
    # ---- 4. class numbers of the two in-class sites: k^2 + q j^2, disc -4q
    def class_number(disc):
        """count reduced primitive positive forms (a,b,c), b^2-4ac=disc<0, |b|<=a<=c, b>=0 if |b|==a or a==c."""
        h = 0
        forms = []
        a = 1
        while 3 * a * a <= -disc:
            for b in range(-a + 1, a + 1):
                num = b * b - disc
                if num % (4 * a):
                    continue
                c = num // (4 * a)
                if c < a:
                    continue
                if math.gcd(math.gcd(a, abs(b)), c) != 1:
                    continue
                if (a == c or abs(b) == a) and b < 0:
                    continue
                h += 1
                forms.append((a, b, c))
            a += 1
        return h, forms
    
    print("\n== class numbers ==")
    cn = []
    for q in [49, 50, 100, 400, 1600]:
        h, forms = class_number(-4 * q)
        cn.append(dict(disc=-4 * q, h=h, forms=str(forms)))
        print("q=%-5d disc=%-7d h=%d   %s" % (q, -4 * q, h, forms if h <= 8 else '(%d forms)' % h))
    out['class_numbers'] = cn
    
    with open('fold_results2.json', 'w') as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote fold_results2.json")
    

def stage3():
    """cycle 15 part 3 -- Delta* a third way, the analytic law across the fold, and the b-coefficient."""
    from mpmath import mp, mpf, mpc, pi, log, sqrt, exp, euler, re, im, findroot, diff, matrix, lu_solve, nstr
    from machine2_cycle15_epstein_fold import zeta2, Lam, digits, set_cut
    import json
    
    mp.dps = 40
    set_cut(40)
    
    K_M1 = mpf('3.25301161631896')
    C2_M1 = mpf('-7.41840343632')
    out = {}
    
    # ---------- 1. Delta* as the root of  D -> zeta2(1/2, D).  (At the fold the double zero sits at
    #             s=1/2 by the s<->1-s symmetry, so the fold point is exactly where zeta2(1/2,.) vanishes.)
    f = lambda D: re(zeta2(mpf(1) / 2, mpf(D)))
    DSTAR_NUM = findroot(f, mpf('0.1417332396638872'))
    DSTAR_CF = exp(euler) / (4 * pi)
    print("Delta* (root of zeta2(1/2,.)) = %s" % nstr(DSTAR_NUM, 35))
    print("Delta* = e^gamma/(4pi)        = %s" % nstr(DSTAR_CF, 35))
    print("agreement: %s digits" % nstr(digits(DSTAR_NUM, DSTAR_CF), 6))
    out['Dstar'] = dict(numeric=nstr(DSTAR_NUM, 35), closed_form=nstr(DSTAR_CF, 35),
                        digits=nstr(digits(DSTAR_NUM, DSTAR_CF), 6))
    DS = DSTAR_NUM
    
    # ---------- 2. u^2 across the fold ----------
    vs = [mpf('1e-4'), mpf('3e-5'), mpf('1e-5'), mpf('3e-6'), mpf('1e-6'), mpf('3e-7'), mpf('1e-7')]
    rows = []
    for v in vs + [-x for x in vs]:
        D = DS - v
        if v > 0:
            r = findroot(lambda x: re(zeta2(mpf(x), D)), mpf(1) / 2 + (K_M1 / 2) * sqrt(v))
            u2 = (r - mpf(1) / 2)**2
            kind = 'real'
        else:
            y = findroot(lambda t: re(Lam(mpf(1) / 2 + 1j * mpf(t), D)), (K_M1 / 2) * sqrt(-v))
            u2 = -(y * y)
            kind = 'line'
        rows.append((v, u2, kind))
        print("v=%-12s %-5s u^2=%-28s u^2/v=%s" % (nstr(v, 6), kind, nstr(u2, 20), nstr(u2 / v, 18)))
    out['u2'] = [dict(v=nstr(v, 12), kind=k, u2=nstr(u2, 22), u2_over_v=nstr(u2 / v, 18)) for v, u2, k in rows]
    
    # least-squares fit u^2/v = a + b v  (both sides pooled)
    def fit(sub):
        n = len(sub)
        A = matrix(n, 2)
        y = matrix(n, 1)
        for i, (v, u2, k) in enumerate(sub):
            A[i, 0] = 1
            A[i, 1] = v
            y[i] = u2 / v
        N = A.T * A
        rhs = A.T * y
        return lu_solve(N, rhs)
    
    for name, sub in [('pooled', rows), ('real side', [r for r in rows if r[2] == 'real']),
                      ('line side', [r for r in rows if r[2] == 'line'])]:
        sol = fit(sub)
        a, b = sol[0], sol[1]
        print("fit %-10s a = %-24s b = %-20s   k_implied = 2*sqrt(a) = %s   c2_eff = b/(2a^2) = %s"
              % (name, nstr(a, 18), nstr(b, 12), nstr(2 * sqrt(a), 15), nstr(b / (2 * a * a), 8)))
        out.setdefault('fits', {})[name] = dict(a=nstr(a, 18), b=nstr(b, 12),
                                                k_implied=nstr(2 * sqrt(a), 15), c2_eff=nstr(b / (2 * a * a), 8))
    print("k (m1 analytic) = %s ;  a_pred = k^2/4 = %s" % (nstr(K_M1, 15), nstr(K_M1**2 / 4, 15)))
    out['a_pred_from_m1_k'] = nstr(K_M1**2 / 4, 15)
    
    # ---------- 3. the analytic coefficients, computed for BOTH normalisations ----------
    print("\n== fold derivatives at (1/2, Delta*) ==")
    mp.dps = 30
    set_cut(30)
    for label, F in [('Lambda', lambda s, D: Lam(s, D)), ('zeta2', lambda s, D: zeta2(s, D))]:
        A_ss = diff(lambda x: re(F(mpf(1) / 2 + x, DS)), mpf(0), 2)
        A_ssss = diff(lambda x: re(F(mpf(1) / 2 + x, DS)), mpf(0), 4)
        A_D = diff(lambda d: re(F(mpf(1) / 2, DS + d)), mpf(0), 1)
        A_DD = diff(lambda d: re(F(mpf(1) / 2, DS + d)), mpf(0), 2)
        A_ssD = diff(lambda d: diff(lambda x: re(F(mpf(1) / 2 + x, DS + d)), mpf(0), 2), mpf(0), 1)
        a = 2 * A_D / A_ss
        b_m1only = -A_ssss * a * a / (12 * A_ss)
        b_full = b_m1only - A_DD / A_ss + A_ssD * a / A_ss
        print("%-7s A_ss=%-16s A_ssss=%-16s A_D=%-14s A_DD=%-14s A_ssD=%-14s"
              % (label, nstr(A_ss, 10), nstr(A_ssss, 10), nstr(A_D, 10), nstr(A_DD, 10), nstr(A_ssD, 10)))
        print("        a=%-20s  b(m1's c2 term only)=%-16s  b(full)=%-16s  c2_full=%s"
              % (nstr(a, 15), nstr(b_m1only, 10), nstr(b_full, 10), nstr(b_full / (2 * a * a), 10)))
        out.setdefault('derivs', {})[label] = dict(
            A_ss=nstr(A_ss, 12), A_ssss=nstr(A_ssss, 12), A_D=nstr(A_D, 12), A_DD=nstr(A_DD, 12),
            A_ssD=nstr(A_ssD, 12), a=nstr(a, 15), b_m1_term_only=nstr(b_m1only, 10),
            b_full=nstr(b_full, 10), c2_full=nstr(b_full / (2 * a * a), 10),
            c2_m1_formula=nstr(-A_ssss / (24 * A_ss), 10))
        print("        m1's c2 = -A_ssss/(24 A_ss) = %s" % nstr(-A_ssss / (24 * A_ss), 10))
    
    with open('fold_results3.json', 'w') as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote fold_results3.json")
    

def stage4():
    """cycle 15 part 4 -- SECOND, structurally different evaluator (Bessel/Poisson line identity,
    derived here, and it independently reproduces m1's AMENDMENT-2-corrected (m/k)^{s-1/2} form),
    used to test whether the fold point Delta* really equals the published closed form e^gamma/(4pi)."""
    from mpmath import mp, mpf, mpc, pi, sqrt, gamma, zeta, besselk, exp, euler, log, findroot, re, nstr
    from machine2_cycle15_epstein_fold import zeta2 as zeta2_theta, digits, set_cut
    import json
    
    mp.dps = 50
    set_cut(50)
    
    def zeta2_bessel(s, D, nmax=None):
        """zeta2(s,D) = zeta(2s) + sqrt(pi)Gamma(s-1/2)D^{1-2s}zeta(2s-1)/Gamma(s)
                        + (4 pi^s/Gamma(s)) D^{1/2-s} sum_{k,m>=1} (m/k)^{s-1/2} K_{s-1/2}(2 pi D k m)
        (my own Poisson/line-identity derivation; singular termwise at s=1/2 -- evaluate slightly off)."""
        s = mpc(s); D = mpf(D)
        nu = s - mpf(1) / 2
        if nmax is None:
            nmax = int((mp.dps + 12) * log(mpf(10)) / (2 * pi * D)) + 2
        tot = mp.zero
        for k in range(1, nmax + 1):
            for m in range(1, nmax // k + 1):
                tot += (mpf(m) / k)**nu * besselk(nu, 2 * pi * D * k * m)
        return (zeta(2 * s) + sqrt(pi) * gamma(nu) * D**(1 - 2 * s) * zeta(2 * s - 1) / gamma(s)
                + 4 * pi**s * D**(-nu) * tot / gamma(s))
    
    out = {}
    DSTAR_CF = exp(euler) / (4 * pi)
    EPS = mpf('1e-12')          # zeta2(1/2+eps,D) = zeta2(1/2,D) + (A_ss/2)eps^2, |A_ss|/2 ~ 19 => 1.9e-23
    s0 = mpf(1) / 2 + EPS
    
    print("== evaluator cross-check (theta-Mellin vs Bessel), dps=%d ==" % mp.dps)
    xs = []
    for (s, D) in [(mpf('1.3'), mpf('0.1417')), (mpf('0.75'), mpf('0.5')), (s0, DSTAR_CF)]:
        a = zeta2_theta(s, D); b = zeta2_bessel(s, D)
        xs.append(dict(s=nstr(s, 15), D=nstr(D, 12), theta=nstr(a, 15), bessel=nstr(b, 15),
                       digits=nstr(digits(a, b), 6)))
        print("s=%-22s D=%-20s  theta=%-24s bessel=%-24s  agree %s dig"
              % (nstr(s, 14), nstr(D, 12), nstr(a, 12), nstr(b, 12), nstr(digits(a, b), 6)))
    out['evaluator_crosscheck'] = xs
    
    print("\n== is e^gamma/(4pi) the fold point? ==")
    vals = {}
    for name, f in [('theta', zeta2_theta), ('bessel', zeta2_bessel)]:
        v = f(s0, DSTAR_CF)
        vals[name] = nstr(v, 15)
        print("zeta2(1/2+1e-12, e^gamma/4pi) via %-7s = %s" % (name, nstr(v, 15)))
    out['value_at_closed_form'] = vals
    
    # root of D -> zeta2(1/2+eps, D), both evaluators, tight tolerance
    roots = {}
    for name, f in [('theta', zeta2_theta), ('bessel', zeta2_bessel)]:
        r = findroot(lambda D: re(f(s0, mpf(D))), DSTAR_CF, tol=mpf(10)**(-80))
        roots[name] = nstr(r, 40)
        print("Delta* root via %-7s = %s   (minus closed form: %s)"
              % (name, nstr(r, 36), nstr(r - DSTAR_CF, 8)))
    out['Dstar_roots'] = roots
    out['closed_form'] = nstr(DSTAR_CF, 40)
    print("closed form            = %s" % nstr(DSTAR_CF, 36))
    
    with open('fold_results4.json', 'w') as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote fold_results4.json")
    

def stage5():
    """cycle 15 part 5 -- (H4) lattice counts at the two in-class sites, class-number table,
    off-line census past the fold at Delta=1/7, and a precision re-check of a=k^2/4."""
    from mpmath import mp, mpf, mpc, pi, sqrt, log, exp, euler, re, im, arg, findroot, diff, nstr
    from machine2_cycle15_epstein_fold import zeta2, Lam, digits, set_cut
    import json, math
    import numpy as np
    
    out = {}
    
    # ---------- A. class-number table for the in-class sites Delta = 1/sqrt(q) ----------
    def class_number(disc):
        h, forms = 0, []
        a = 1
        while 3 * a * a <= -disc:
            for b in range(-a + 1, a + 1):
                num = b * b - disc
                if num % (4 * a):
                    continue
                c = num // (4 * a)
                if c < a:
                    continue
                if math.gcd(math.gcd(a, abs(b)), c) != 1:
                    continue
                if (a == c or abs(b) == a) and b < 0:
                    continue
                h += 1
                forms.append((a, b, c))
            a += 1
        return h, forms
    
    tab = []
    for q in range(1, 31):
        h, _ = class_number(-4 * q)
        tab.append((q, h))
    print("q:h  " + "  ".join("%d:%d" % t for t in tab))
    out['class_numbers_1_to_30'] = {str(q): h for q, h in tab}
    
    # ---------- B. (H4): summatory-function error exponent at the two straddling sites ----------
    print("\n== (H4) lattice-count error, A(y) = (pi/(2 Delta)) y + E(y) ==")
    h4 = []
    for q in [50, 49]:
        # Delta = 1/sqrt(q):  lambda = j^2 + k^2/q,  q*lambda = q j^2 + k^2 =: n  (integral form, disc -4q)
        Y = 2 * 10**6                     # y-range in lambda
        NMAX = q * Y
        jmax = int(math.isqrt(NMAX // q))
        counts = np.zeros(NMAX + 1, dtype=np.int64)
        for j in range(-jmax, jmax + 1):
            rem = NMAX - q * j * j
            if rem < 0:
                continue
            kmax = int(math.isqrt(rem))
            ks = np.arange(-kmax, kmax + 1, dtype=np.int64)
            n = q * j * j + ks * ks
            n = n[n > 0]
            np.add.at(counts, n, 1)
        cum = np.cumsum(counts) / 2.0        # the 1/2 in zeta2 = (1/2) sum'
        ys = np.unique(np.geomspace(1000, Y, 4000).astype(np.int64))
        A = cum[(ys * q).astype(np.int64)]
        main = math.pi * math.sqrt(q) / 2.0 * ys      # pi/(2*Delta) * y with Delta = 1/sqrt(q)
        E = A - main
        r13 = np.max(np.abs(E) / ys**(1.0 / 3.0))
        r12 = np.max(np.abs(E) / ys**(0.5))
        ratio = A[-1] / main[-1]
        h4.append(dict(q=q, Delta='1/sqrt(%d)' % q, count_ratio=float(ratio),
                       sup_E_over_y13=float(r13), sup_E_over_y12=float(r12)))
        print("q=%-4d Delta=1/sqrt(q)  A(Y)/main = %.10f   sup|E|/y^(1/3) = %.4f   sup|E|/y^(1/2) = %.5f"
              % (q, ratio, r13, r12))
    out['H4'] = h4
    
    # ---------- C. precision re-check of a = k^2/4 at dps 50 ----------
    mp.dps = 50
    set_cut(50)
    EPS = mpf('1e-12')
    DS = findroot(lambda D: re(zeta2(mpf(1) / 2 + EPS, mpf(D))), mpf('0.1417332396638871914'), tol=mpf(10)**(-80))
    print("\nDelta* (dps50) = %s" % nstr(DS, 36))
    mp.dps = 40
    set_cut(40)
    res = {}
    for label, F in [('zeta2', zeta2), ('Lambda', Lam)]:
        A_ss = diff(lambda x: re(F(mpf(1) / 2 + x, DS)), mpf(0), 2)
        A_ssss = diff(lambda x: re(F(mpf(1) / 2 + x, DS)), mpf(0), 4)
        A_D = diff(lambda d: re(F(mpf(1) / 2, DS + d)), mpf(0), 1)
        A_DD = diff(lambda d: re(F(mpf(1) / 2, DS + d)), mpf(0), 2)
        A_ssD = diff(lambda d: diff(lambda x: re(F(mpf(1) / 2 + x, DS + d)), mpf(0), 2), mpf(0), 1)
        a = 2 * A_D / A_ss
        b = -A_ssss * a * a / (12 * A_ss) - A_DD / A_ss + A_ssD * a / A_ss
        res[label] = dict(a=nstr(a, 18), k=nstr(2 * sqrt(a), 18), b=nstr(b, 14),
                          c2_full=nstr(b / (2 * a * a), 12), c2_m1=nstr(-A_ssss / (24 * A_ss), 12))
        print("%-7s dps40  a=%-22s k=2sqrt(a)=%-20s b=%-16s c2_full=%s"
              % (label, nstr(a, 16), nstr(2 * sqrt(a), 16), nstr(b, 12), nstr(b / (2 * a * a), 10)))
    out['coeffs_dps40'] = res
    out['Dstar_dps50'] = nstr(DS, 36)
    
    # ---------- D. off-line census past the fold at Delta = 1/7 ----------
    mp.dps = 25
    set_cut(25)
    D7 = mpf(1) / 7
    
    def winding_rect(D, x0, x1, y0, y1, n):
        pts = []
        per = 2 * ((x1 - x0) + (y1 - y0))
        for i in range(n):
            t = mpf(i) / n * per
            if t < (x1 - x0):
                s = mpc(x0 + t, y0)
            elif t < (x1 - x0) + (y1 - y0):
                s = mpc(x1, y0 + (t - (x1 - x0)))
            elif t < 2 * (x1 - x0) + (y1 - y0):
                s = mpc(x1 - (t - (x1 - x0) - (y1 - y0)), y1)
            else:
                s = mpc(x0, y1 - (t - 2 * (x1 - x0) - (y1 - y0)))
            pts.append(zeta2(s, D))
        tot = mp.zero
        mx = mp.zero
        for i in range(n):
            d = arg(pts[(i + 1) % n] / pts[i])
            mx = max(mx, abs(d))
            tot += d
        return tot / (2 * pi), mx
    
    print("\n== off-line census at Delta = 1/7 (past the fold): argument principle ==")
    cen = []
    for (x0, x1, y0, y1, n) in [(mpf('0.52'), mpf('4.0'), mpf('-20'), mpf('20'), 1200),
                                (mpf('0.5001'), mpf('0.52'), mpf('-5'), mpf('5'), 600)]:
        N, mx = winding_rect(D7, x0, x1, y0, y1, n)
        pole = 1 if (x0 < 1 < x1 and y0 < 0 < y1) else 0
        cen.append(dict(box='Re[%s,%s] Im[%s,%s]' % (x0, x1, y0, y1), n=n, winding=nstr(N, 10),
                        pole_inside=pole, zeros=nstr(N + pole, 10), max_step_arg=nstr(mx, 6)))
        print("box Re[%s,%s] x Im[%s,%s], n=%d : winding=%s  (pole inside: %d) => zeros = %s   max step arg = %s"
              % (x0, x1, y0, y1, n, nstr(N, 8), pole, nstr(N + pole, 8), nstr(mx, 5)))
    out['census_1_over_7'] = cen
    
    with open('fold_results5.json', 'w') as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote fold_results5.json")
    

def stage6():
    """cycle 15 part 6 -- resolve the low-height off-line census at Delta = 1/7 properly.
    run5's thin box [0.5001,0.52] x [-5,5] returned 6 with max-step-arg 3.13 rad (~pi) => aliasing
    suspected (the on-line fold zero sits 1e-4 from that contour). Redo symmetrically + locate."""
    from mpmath import mp, mpf, mpc, pi, arg, re, im, findroot, nstr, sqrt
    from machine2_cycle15_epstein_fold import zeta2, Lam, set_cut
    import json
    
    mp.dps = 20
    set_cut(20)
    D7 = mpf(1) / 7
    out = {}
    
    # --- A. on-line zeros with |t| <= 5: Lambda(1/2+iy) is real, so just scan for sign changes
    print("== on-line zeros of Lambda(1/2+iy), Delta=1/7, 0 < y <= 5 ==")
    prev = None
    onl = []
    N = 500
    for i in range(N + 1):
        y = mpf(5) * i / N
        v = re(Lam(mpf(1) / 2 + 1j * y, D7))
        if prev is not None and (v > 0) != (prev[1] > 0):
            r = findroot(lambda t: re(Lam(mpf(1) / 2 + 1j * mpf(t), D7)), (prev[0] + y) / 2)
            onl.append(r)
            print("   on-line zero at y = %s" % nstr(r, 18))
        prev = (y, v)
    print("on-line zeros with 0 < y <= 5 : %d  (plus mirror images, plus none at y=0)" % len(onl))
    out['online_zeros_1_over_7'] = [nstr(r, 18) for r in onl]
    
    # --- B. symmetric box count around the critical line
    def winding_rect(D, x0, x1, y0, y1, n):
        pts = []
        per = 2 * ((x1 - x0) + (y1 - y0))
        for i in range(n):
            t = mpf(i) / n * per
            if t < (x1 - x0):
                s = mpc(x0 + t, y0)
            elif t < (x1 - x0) + (y1 - y0):
                s = mpc(x1, y0 + (t - (x1 - x0)))
            elif t < 2 * (x1 - x0) + (y1 - y0):
                s = mpc(x1 - (t - (x1 - x0) - (y1 - y0)), y1)
            else:
                s = mpc(x0, y1 - (t - 2 * (x1 - x0) - (y1 - y0)))
            pts.append(zeta2(s, D))
        tot = mp.zero
        mx = mp.zero
        for i in range(n):
            d = arg(pts[(i + 1) % n] / pts[i])
            mx = max(mx, abs(d))
            tot += d
        return tot / (2 * pi), mx
    
    print("\n== symmetric box counts (Delta = 1/7) ==")
    box = []
    for (x0, x1, y0, y1, n) in [(mpf('0.46'), mpf('0.54'), mpf('-5'), mpf('5'), 2400),
                                (mpf('0.30'), mpf('0.70'), mpf('-5'), mpf('5'), 2400),
                                (mpf('0.52'), mpf('4.0'), mpf('-20'), mpf('20'), 2400)]:
        Nw, mx = winding_rect(D7, x0, x1, y0, y1, n)
        pole = 1 if (x0 < 1 < x1 and y0 < 0 < y1) else 0
        print("Re[%s,%s] x Im[%s,%s] n=%d : winding=%s  pole=%d => zeros=%s  max step arg=%s"
              % (x0, x1, y0, y1, n, nstr(Nw, 10), pole, nstr(Nw + pole, 10), nstr(mx, 5)))
        box.append(dict(box='Re[%s,%s] Im[%s,%s]' % (x0, x1, y0, y1), n=n, winding=nstr(Nw, 10),
                        zeros=nstr(Nw + pole, 10), max_step_arg=nstr(mx, 5)))
    out['boxes_1_over_7'] = box
    
    with open('fold_results6.json', 'w') as fh:
        json.dump(out, fh, indent=1)
    print("\nwrote fold_results6.json")
    

def stage7():
    """cycle 15 part 7 -- (i) close the visibility-relevant census window at Delta=1/7,
    (ii) rigorous-enough no-zeros-for-sigma>=2 bound, (iii) the zero-parameter continuation
    prediction past the fold at the two sites of record."""
    from mpmath import mp, mpf, mpc, pi, arg, re, im, sqrt, findroot, nstr, log, exp, euler
    from machine2_cycle15_epstein_fold import zeta2, Lam, set_cut
    import json, math
    
    out = {}
    D7 = mpf(1) / 7
    
    # ---- (iii) first, it is cheap: continuation law past the fold, zero fitted parameters
    mp.dps = 30
    set_cut(30)
    DS = mpf('0.14173323966388719139541530708686641')      # our root of zeta2(1/2,.), dps50, both evaluators
    A = mpf('2.645521411811663')                            # a = 2 A_D / A_ss   (=k^2/4)
    B = mpf('-7.46245287679')                               # full second coefficient
    pred = []
    for Dstr, guess in [('0.142857142857142857142857142857', '0.0546'), ('0.145', '0.0934'), ('0.15', '0.1496')]:
        D = mpf(Dstr)
        d = D - DS
        y2 = A * d - B * d * d
        ypred = sqrt(y2)
        ymeas = findroot(lambda t: re(Lam(mpf(1) / 2 + 1j * mpf(t), D)), mpf(guess))
        pred.append(dict(D=Dstr[:12], delta=nstr(d, 12), y_pred=nstr(ypred, 15),
                         y_meas=nstr(ymeas, 15), rel=nstr((ypred - ymeas) / ymeas, 6)))
        print("D=%-14s D-D*=%-14s y_pred=%-20s y_meas=%-20s rel=%s"
              % (Dstr[:12], nstr(d, 8), nstr(ypred, 15), nstr(ymeas, 15), nstr((ypred - ymeas) / ymeas, 5)))
    out['continuation_prediction'] = pred
    
    # ---- (ii) no zeros with sigma >= 2 at Delta = 1/7:  zeta2(s,1/7) = 49^s F(s),
    #      F(s) = sum a_n n^{-s}, a_1 = 1;  |F-1| <= sum_{n>=2} a_n n^{-sigma}
    q = 49
    NMAX = 2 * 10**6
    import numpy as np
    counts = np.zeros(NMAX + 1, dtype=np.int64)
    jmax = int(math.isqrt(NMAX // q))
    for j in range(-jmax, jmax + 1):
        rem = NMAX - q * j * j
        kmax = int(math.isqrt(rem))
        ks = np.arange(-kmax, kmax + 1, dtype=np.int64)
        n = q * j * j + ks * ks
        n = n[n > 0]
        np.add.at(counts, n, 1)
    a_n = counts / 2.0
    for sig in [1.5, 1.75, 2.0]:
        ns = np.arange(2, NMAX + 1)
        tail_sum = float(np.sum(a_n[2:] * ns**(-sig)))
        tail_bound = (math.pi * 7 / 2) / ((sig - 1) * NMAX**(sig - 1))   # A(x) ~ (pi/(2 Delta)) x /49-scaled
        print("sigma=%.2f : sum_{2<=n<=2e6} a_n n^-s = %.6f   + tail bound %.3g" % (sig, tail_sum, tail_bound))
        out.setdefault('no_zero_bound', []).append(dict(sigma=sig, partial=tail_sum, tail_bound=tail_bound))
    
    # ---- (i) the remaining visibility window: sigma in [0.52,2], 20 < t <= 43
    mp.dps = 20
    set_cut(20)
    
    def winding_rect(D, x0, x1, y0, y1, n):
        pts = []
        per = 2 * ((x1 - x0) + (y1 - y0))
        for i in range(n):
            t = mpf(i) / n * per
            if t < (x1 - x0):
                s = mpc(x0 + t, y0)
            elif t < (x1 - x0) + (y1 - y0):
                s = mpc(x1, y0 + (t - (x1 - x0)))
            elif t < 2 * (x1 - x0) + (y1 - y0):
                s = mpc(x1 - (t - (x1 - x0) - (y1 - y0)), y1)
            else:
                s = mpc(x0, y1 - (t - 2 * (x1 - x0) - (y1 - y0)))
            pts.append(zeta2(s, D))
        tot = mp.zero
        mx = mp.zero
        for i in range(n):
            d = arg(pts[(i + 1) % n] / pts[i])
            mx = max(mx, abs(d))
            tot += d
        return tot / (2 * pi), mx
    
    for (x0, x1, y0, y1, n) in [(mpf('0.52'), mpf('2.0'), mpf('20'), mpf('43'), 2000)]:
        N, mx = winding_rect(D7, x0, x1, y0, y1, n)
        print("Re[%s,%s] x Im[%s,%s] n=%d : winding=%s max step arg=%s" % (x0, x1, y0, y1, n, nstr(N, 10), nstr(mx, 5)))
        out['census_upper_window'] = dict(box='Re[%s,%s] Im[%s,%s]' % (x0, x1, y0, y1), n=n,
                                          zeros=nstr(N, 10), max_step_arg=nstr(mx, 5))
    
    with open('fold_results7.json', 'w') as fh:
        json.dump(out, fh, indent=1)
    print("wrote fold_results7.json")
    

def stage8():
    """cycle 15 part 8 -- widen the TIGHT symmetric census window at Delta=1/7 to |t|<=12."""
    from mpmath import mp, mpf, mpc, pi, arg, re, findroot, nstr
    from machine2_cycle15_epstein_fold import zeta2, Lam, set_cut
    import json
    mp.dps = 15; set_cut(15)
    D7 = mpf(1)/7
    out = {}
    # on-line zeros to |t| <= 12
    prev=None; onl=[]
    N=1200
    for i in range(N+1):
        y = mpf(12)*i/N
        v = re(Lam(mpf(1)/2 + 1j*y, D7))
        if prev is not None and (v>0)!=(prev[1]>0):
            r = findroot(lambda t: re(Lam(mpf(1)/2+1j*mpf(t), D7)), (prev[0]+y)/2)
            onl.append(nstr(r,15))
        prev=(y,v)
    print("on-line zeros 0<y<=12 : %d -> %s" % (len(onl), onl))
    out['online_zeros_t12'] = onl
    def winding_rect(D,x0,x1,y0,y1,n):
        pts=[]; per=2*((x1-x0)+(y1-y0))
        for i in range(n):
            t=mpf(i)/n*per
            if t<(x1-x0): s=mpc(x0+t,y0)
            elif t<(x1-x0)+(y1-y0): s=mpc(x1,y0+(t-(x1-x0)))
            elif t<2*(x1-x0)+(y1-y0): s=mpc(x1-(t-(x1-x0)-(y1-y0)),y1)
            else: s=mpc(x0,y1-(t-2*(x1-x0)-(y1-y0)))
            pts.append(zeta2(s,D))
        tot=mp.zero; mx=mp.zero
        for i in range(n):
            d=arg(pts[(i+1)%n]/pts[i]); mx=max(mx,abs(d)); tot+=d
        return tot/(2*pi), mx
    for (x0,x1,y0,y1,n) in [(mpf('0.46'),mpf('0.54'),mpf('-12'),mpf('12'),5000)]:
        Nw,mx = winding_rect(D7,x0,x1,y0,y1,n)
        print("Re[%s,%s] x Im[%s,%s] n=%d : zeros=%s max step arg=%s"%(x0,x1,y0,y1,n,nstr(Nw,10),nstr(mx,5)))
        out['box_t12']=dict(box='Re[0.46,0.54] Im[-12,12]',n=n,zeros=nstr(Nw,10),max_step_arg=nstr(mx,5))
    json.dump(out, open('fold_results8.json','w'), indent=1)
    print("done")
    

if __name__ == '__main__':
    {'1':stage1,'2':stage2,'3':stage3,'4':stage4,'5':stage5,'6':stage6,'7':stage7,'8':stage8}[sys.argv[1]]()
