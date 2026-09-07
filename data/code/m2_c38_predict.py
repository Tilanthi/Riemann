"""c38 PREDICTIONS, computed from committed artefacts only, BEFORE the runs they predict."""
import json, re, mpmath as mp
mp.mp.dps = 240
R = "/shared/rh-exchange-repo/Riemann/"
c36 = open(R+"machine2-c36-the-two-unanchored-checks-are-real-and-neither-touches-the-evaluator.md").read()
D175s = max(re.findall(r"0\.14173323966388719139541568508418502362314456[0-9]*", c36), key=len)
D175 = mp.mpf(D175s)
FP = mp.mpf(re.search(r"f'\(D\*\) = (-37\.4819713608[0-9]*)",
                      open("/workspace/rh/cycle37/c37_fprime.out").read()).group(1))
d = json.load(open('/workspace/rh/cycle34/c34_refit.json'))
C80 = mp.mpf(d[0]['cfg']['centre'])
delta = C80 - D175                      # error of the string the c34 pipeline consumed
print("D* read at %d s.f.;  f' read at %d s.f." % (len(D175s)-2, 12))
print("delta = C80 - D175            =", mp.nstr(delta, 12))
print("print floor  f'*delta         =", mp.nstr(FP*delta, 14))
print()
def alias(rw, N, order=1): return -4*(2*mp.mpf(rw))**(order*N)
for lab, rw, N, centre in [("R1", "0.045", 40, "C80"), ("R2", "0.04", 40, "C175"),
                           ("R3", "0.045", 40, "C175"), ("R4", "0.045", 72, "C175")]:
    a1 = alias(rw, N, 1); a2 = alias(rw, N, 2)
    cen = FP*delta if centre == "C80" else mp.mpf(0)
    eps = cen + a2
    print("%-3s r_w=%-6s N_w=%-3d centre=%-5s  1st alias %-12s 2nd alias %-14s  PREDICTED eps = g00+4(2r)^N = %s"
          % (lab, rw, N, centre, mp.nstr(-a1, 6), mp.nstr(a2, 6), mp.nstr(eps, 12)))
    print("      predicted g00 = %s" % mp.nstr(a1 + eps, 32))
print()
print("R3/R2 second-alias ratio (1.125)^80 =", mp.nstr((mp.mpf("0.09")/mp.mpf("0.08"))**80, 10))
print()
dp = [e for e in d if e['label'] == 'DP19'][0]
print("DP19 sensitivities d(coeff)/d(centre) read from c34_refit.json, and the predicted RAW shift")
print("  raw(C175) - raw(C80) = S_k * (C175 - C80) = S_k * %s" % mp.nstr(-delta, 12))
for nm in ["a", "b", "a3", "a4", "a5"]:
    S = mp.mpf(dp['sens'][nm])
    print("   %-3s S = %-22s  predicted raw shift = %s      published(45sf) ulp = 1e-%d"
          % (nm, mp.nstr(S, 12), mp.nstr(S*(-delta), 8), 45 - len(str(int(abs(mp.mpf(dp['rec'][nm])))))))
