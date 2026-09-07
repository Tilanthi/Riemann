"""c38 DERIVATION (declared as such, before the prereg is filed): can the N_w=40 residual
1.378304e-74 be explained WITHOUT any new run, as the round-off of the JSON's own 30-s.f.
serialisation of g00?  Every constant is READ from a committed/frozen artefact, none typed."""
import json, re, mpmath as mp
mp.mp.dps = 220
R = "/shared/rh-exchange-repo/Riemann/"
c36 = open(R+"machine2-c36-the-two-unanchored-checks-are-real-and-neither-touches-the-evaluator.md").read()
D175 = mp.mpf(max(re.findall(r"0\.14173323966388719139541568508418502362314456[0-9]*", c36), key=len))
FP = mp.mpf(re.search(r"f'\(D\*\) = (-37\.4819713608[0-9]*)",
                      open("/workspace/rh/cycle37/c37_fprime.out").read()).group(1))
d = json.load(open('/workspace/rh/cycle34/c34_refit.json'))
C80 = mp.mpf(d[0]['cfg']['centre'])
delta = C80 - D175
print("print floor  f'(D*)*delta = %s" % mp.nstr(FP*delta, 12))
print()
print("%-5s %-6s %-4s %-24s %-24s %-24s %s" % ("cfg","r_w","N_w","eps from stored string","predicted round-off","eps - roundoff","alias 4(2r)^N"))
for e in d:
    c = e['cfg']
    if len(c['centre']) < 50:   # skip the old-literal-centre control
        continue
    rw = mp.mpf(c['r_w']); Nw = c['N_w']
    alias = -4*(2*rw)**Nw
    g00_stored = mp.mpf(e['g00'])
    eps_stored = g00_stored - alias
    # model of the TRUE g00: alias + print floor.  Round THAT to the same 30 s.f. the JSON used.
    g00_model = alias + FP*delta
    roundoff = mp.mpf(mp.nstr(g00_model, 30, strip_zeros=False)) - g00_model
    print("%-5s %-6s %-4d %-24s %-24s %-24s %s" % (e['label'], c['r_w'], Nw,
          mp.nstr(eps_stored, 8), mp.nstr(roundoff, 8), mp.nstr(eps_stored-roundoff, 8),
          mp.nstr(-alias, 6)))
    if Nw == 40 and e['label'] == 'A':
        print("      stored string : %s" % e['g00'])
        print("      model  at 30sf: %s" % mp.nstr(g00_model, 30, strip_zeros=False))
