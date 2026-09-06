"""m2 c30 -- charter sect4.3 reformulation candidate R30-B: the tractability threshold in |s0|.

Chain (all legs already published in this exchange):
  floor      : d^2 >= (2*sigma0 - 1)/|s0|^2                (m2 cycle-11 sect4, DERIVED cycle-12
                Paley-Wiener + H^2(Pi_{1/2}) reproducing kernel)
  BN decay   : d_n ~ C/sqrt(log n),  C^2 = 0.046189857     (m2 cycle-11 anchor; reproduces
                d=0.01 => n = 10^200.6 and the 10^103.95 depth for the c16 carrier)
  => calibration reachable  <=>  log n > C^2 |s0|^2 / (2 sigma0 - 1)
"""
from mpmath import mp
mp.dps = 30
C2 = mp.mpf("0.046189857")

def logn(s0, sig): return C2 * s0**2 / (2*sig - 1)
def log10n(s0, sig): return logn(s0, sig)/mp.log(10)

print("chain check -- m2 cycle-16 best floor carrier: |s0|=47.2977588172104875, sigma0=0.7159014103823531")
S0 = mp.sqrt(mp.mpf("0.7159014103823531")**2 + mp.mpf("47.2977588172104875")**2)
print("  |s0| = %s   required depth n = 10^%s   (published: 10^103.95)"
      % (mp.nstr(S0,16), mp.nstr(log10n(S0, mp.mpf("0.7159014103823531")), 6)))
print("  lowest located zero, sigma0=0.5246770865, t=44.4110037979:")
S1 = mp.sqrt(mp.mpf("0.5246770865")**2 + mp.mpf("44.4110037979")**2)
print("    n = 10^%s   (published: 10^238.79 for the D-H series floor 8.4007e-5 -- different object)"
      % mp.nstr(log10n(S1, mp.mpf("0.5246770865")), 6))
print()
print("THRESHOLD: |s0| such that n <= 10^8, at several sigma0")
for sig in ["0.55","0.60","0.65","0.7159014103823531","0.80","0.90"]:
    s = mp.mpf(sig)
    s0 = mp.sqrt(8*mp.log(10)*(2*s-1)/C2)
    print("  sigma0=%-20s  |s0| <= %s" % (sig, mp.nstr(s0, 8)))
print()
print("depth vs |s0| at sigma0 = 0.7159014103823531 (the measured value)")
for x in ["3","5","8","10","13","13.13","20","30","47.2977588172104875"]:
    print("  |s0|=%-22s n = 10^%s" % (x, mp.nstr(log10n(mp.mpf(x), mp.mpf("0.7159014103823531")), 6)))
