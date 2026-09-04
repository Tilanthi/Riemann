"""Referee R, part 2: WHY the wrong kernel nearly closed on my first test function,
and a second test function that is kernel-SENSITIVE.  Plus the exact -log(pi)*phi(0) receipt."""
import mpmath as mp
import m2_c21_identity_referee as R

mp.mp.dps = 30

def run(c, sig, label):
    R.C = mp.mpf(c); R.SIG = mp.mpf(sig)
    out = {}
    for name, kern, contr in [("correct", R.K_sum, "complex"),
                              ("m3-diff", R.K_diff, "complex"),
                              ("ReRe",    R.K_sum, "rere")]:
        A,B,U1,Z,Arch = R.legs(kernel=kern, contraction=contr)
        out[name] = (A+B) - (U1 - Z + Arch)
        out[name+"_arch"] = Arch
    phi0 = R.phi(0)
    dArch = out["correct_arch"] - out["m3-diff_arch"]
    print("%s   phi(0)=%s" % (label, mp.nstr(phi0, 8)))
    print("   closure correct = %s" % mp.nstr(abs(out["correct"]), 6))
    print("   closure m3-diff = %s      closure Re*Re = %s"
          % (mp.nstr(abs(out["m3-diff"]), 6), mp.nstr(abs(out["ReRe"]), 6)))
    print("   Arch_correct - Arch_diff = %s" % mp.nstr(dArch, 10))
    print("   -log(pi)*phi(0)          = %s   (the delta-function part of the missing kernel)"
          % mp.nstr(-mp.log(mp.pi)*phi0, 10))
    print("   residual (= the psi((1-s)/2) part) = %s"
          % mp.nstr(dArch + mp.log(mp.pi)*phi0, 6))
    print()

run(2,    "0.35", "TF1 Gaussian c=2.00 sig=0.35 (my first choice -- support far from x=0)")
run(0,    "0.35", "TF2 Gaussian c=0.00 sig=0.35 (kernel-SENSITIVE: phi(0)=1)")
run("0.6","0.35", "TF3 Gaussian c=0.60 sig=0.35 (intermediate)")
