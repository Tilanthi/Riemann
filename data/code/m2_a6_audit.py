"""machine2 cycle22 — a6 independence audit (BEAST-AGI verification condition 4).

m1-L141 sect1: "Two different moment functionals of my two anchor values and your (a3,a4,a5)
return the same a6."  Question: two functionals, or two readings of one input?
"""
from mpmath import mp
mp.dps = 30

Dstar = mp.mpf("0.14173323966388719139541530708686641")
e1 = mp.mpf(1) / 7 - Dstar
e2 = mp.mpf("0.15") - Dstar
r1 = mp.mpf("11.7237530179")      # m1's anchor r(eps1)
r2 = mp.mpf("11.8712683846")      # m1's anchor r(eps2)
a3 = mp.mpf("11.7007174")         # m2 cycle-21
a4 = mp.mpf("20.4755")            # m2 cycle-21
a5 = mp.mpf("18.3")               # m2 cycle-21 ("~18.3")

print(f"eps1 = {mp.nstr(e1,10)}  eps2 = {mp.nstr(e2,10)}  eps2-eps1 = {mp.nstr(e2-e1,10)} (1/140 = {mp.nstr(mp.mpf(1)/140,10)})")
print(f"eps1+eps2 = {mp.nstr(e1+e2,10)}   (m1's '0.0093907')")
chord = (r2 - r1) / (e2 - e1)
print(f"chord slope = {mp.nstr(chord,10)}   (m1's 20.652)")
print(f"anchor mean = {mp.nstr((r1+r2)/2,12)}   (m1's published 11.7975107)")


def a6_diff(a3_, a4_, a5_, r1_, r2_):
    R1 = r1_ - a3_ - a4_ * e1 - a5_ * e1**2
    R2 = r2_ - a3_ - a4_ * e2 - a5_ * e2**2
    return (R2 - R1) / (e2**3 - e1**3)


def a6_mean(a3_, a4_, a5_, r1_, r2_):
    R1 = r1_ - a3_ - a4_ * e1 - a5_ * e1**2
    R2 = r2_ - a3_ - a4_ * e2 - a5_ * e2**2
    return (R1 + R2) / (e1**3 + e2**3)


d0 = a6_diff(a3, a4, a5, r1, r2)
m0 = a6_mean(a3, a4, a5, r1, r2)
print(f"\na6 (difference/chord route) = {mp.nstr(d0,8)}   [m1: 63.7]")
print(f"a6 (mean/identity route)    = {mp.nstr(m0,8)}   [m1: 63.6]")
print(f"observed spread             = {mp.nstr(abs(d0-m0),4)}")
print(f"\nNote a3 does NOT enter the difference route: "
      f"{mp.nstr(a6_diff(a3+1,a4,a5,r1,r2)-d0,4)} (exactly 0 by construction)")

print("\n--- propagated sensitivity of each route (per unit input shift) ---")
for name, da3, da4, da5, dr in [("a3", mp.mpf("1e-6"), 0, 0, 0),
                                ("a4", 0, mp.mpf("5e-5"), 0, 0),
                                ("a5", 0, 0, mp.mpf("0.05"), 0),
                                ("r1,r2 (1e-6, opposite)", 0, 0, 0, mp.mpf("1e-6"))]:
    dd = a6_diff(a3 + da3, a4 + da4, a5 + da5, r1 - dr, r2 + dr) - d0
    dm = a6_mean(a3 + da3, a4 + da4, a5 + da5, r1 - dr, r2 + dr) - m0
    print(f"shift {name:>24}: d(a6_diff) = {mp.nstr(dd,4):>12}   d(a6_mean) = {mp.nstr(dm,4):>12}"
          f"   d(spread) = {mp.nstr(dd-dm,4):>12}")

print("\n--- the agreement condition in closed form ---")
R1 = r1 - a3 - a4 * e1 - a5 * e1**2
R2 = r2 - a3 - a4 * e2 - a5 * e2**2
print(f"R1/eps1^3 = {mp.nstr(R1/e1**3,8)}    R2/eps2^3 = {mp.nstr(R2/e2**3,8)}")
print("a6_diff == a6_mean  <=>  R1/eps1^3 == R2/eps2^3  (a single 1-dof shape test on two residuals)")
print(f"weights: mean route puts {mp.nstr(e2**3/(e1**3+e2**3)*100,4)}% of its weight on the eps2 anchor;")
print(f"         diff route puts {mp.nstr(e2**3/(e2**3-e1**3)*100,4)}% on eps2 (and -{mp.nstr(e1**3/(e2**3-e1**3)*100,3)}% on eps1)")
