"""CYCLE 37 -- G(0,0) derivation, v2.

ERRATUM AGAINST MYSELF, v1 of this script: I TYPED the 175-digit D* from memory instead of reading
the committed artefact, and invented digits from position 84 on.  That single act is an instance of
the very class under audit, and it produced a spurious factor 3.53.  v2 reads EVERY constant out of a
file; nothing here is typed.
"""
import json, re, mpmath as mp
mp.mp.dps = 200
R="/shared/rh-exchange-repo/Riemann/"
# --- every constant below is READ, not typed ---
c36 = open(R+"machine2-c36-the-two-unanchored-checks-are-real-and-neither-touches-the-evaluator.md").read()
D175 = mp.mpf(max(re.findall(r"0\.14173323966388719139541568508418502362314456[0-9]*", c36), key=len))
FP  = mp.mpf(re.search(r"f'\(D\*\) = (-37\.4819713608[0-9]*)", open("c37_fprime.out").read()).group(1))
d   = json.load(open('/workspace/rh/cycle34/c34_refit.json'))
C80 = mp.mpf(d[0]['cfg']['centre'])          # the string the c34 pipeline actually consumed
CLIT= mp.mpf([e for e in d if e['label']=='Alit'][0]['cfg']['centre'])
print("digits read: D*=%d s.f.   f'=%d s.f.   centre_80=%d s.f.   centre_lit=%d s.f."
      % (len(str(D175).replace('.','').lstrip('0')), len(str(FP).replace('.','').replace('-','').lstrip('0')),
         len(d[0]['cfg']['centre'])-2, len(CLIT.__str__())))

fam = {}
for e in d:
    c=e['cfg']; g00=mp.mpf(e['g00']); rw=mp.mpf(c['r_w']); Nw=c['N_w']
    eps = g00 + 4*(2*rw)**Nw
    fam.setdefault((Nw if len(c['centre'])>50 else 'LIT'), []).append((e['label'], c['dps'], c['r_w'], eps))
print("\n%-8s %-28s %s" % ("N_w","eps = G(0,0) + 4(2 r_w)^N_w","configs (label/dps/r_w)"))
for k in sorted(fam, key=lambda x: (str(x))):
    vals=[v[3] for v in fam[k]]
    sp = max(vals)/min(vals) if min(vals)!=0 else float('nan')
    print("%-8s %-28s %s   [spread max/min = %s]" % (k, mp.nstr(vals[0],10),
          ", ".join("%s/%d/%s"%(a,b,c) for a,b,c,_ in fam[k]), mp.nstr(sp,6)))

delta = C80 - D175
print("\n## MECHANISM: is the N_w>=56 floor our own 80-digit PRINT of D*?")
print("   delta = (80-digit centre string) - (175-digit value) =", mp.nstr(delta,10))
print("   [c36 published this same rounding error as -8.75933e-82]")
pred = FP*delta
meas = fam[56][0][3]
print("   PREDICTED floor  f'(D*) x delta =", mp.nstr(pred,10))
print("   MEASURED  floor  (N_w=56,64,72; dps 90/110/125; r_w 0.04 and 0.045) =", mp.nstr(meas,10))
print("   predicted / measured =", mp.nstr(pred/meas,8))

print("\n## POSITIVE CONTROL (known answer, already committed): the Alit config, 36-digit centre")
alit=[e for e in d if e['label']=='Alit'][0]
dl = CLIT - D175
print("   delta_lit                    =", mp.nstr(dl,10))
print("   predicted g00 = f'*delta_lit =", mp.nstr(FP*dl,12))
print("   committed    g00             =", mp.nstr(mp.mpf(alit['g00']),12))
print("   predicted / committed        =", mp.nstr(FP*dl/mp.mpf(alit['g00']),8))

print("\n## what the N_w=40 family's larger floor is: UNMEASURED (one (r_w,N_w) point only)")
print("   eps(N_w=40) =", mp.nstr(fam[40][0][3],10), " = %s x the print floor" % mp.nstr(fam[40][0][3]/meas,6))
print("   it is dps-independent (90 and 125 agree to all printed digits) so it is an INPUT error,")
print("   but ONE (r_w,N_w) point cannot separate a coefficient from a channel (c34's own law).")
print("   client: one pipeline run at N_w=40, r_w=0.045.")
