# m1 independent check of m2 c44 / ERRATUM 21 / addendum a00d6ef — from PRINTED LITERALS ONLY.
# No m2 code imported or run. All inputs are the literals published in the c44 letters/README.
from mpmath import mp, log, exp, mpmathify
mp.dps = 120   # cancellation depth ~35 (1-e^-80); dps must exceed it by the wanted width

T = lambda U: -log(1 - exp(-2*U))          # = 2 INT_U^inf e^{-2t}/(1-e^{-2t}) dt, exact (y=e^{-2t})

W40  = mpmathify("2.61742971463509571682932072620940815728346026314942246686866e-33")  # republished, U=40
Winf = mpmathify("2.63547822851354986855244200978e-33")                                  # BEAST, U->inf
m3   = mpmathify("2.6354782285e-33")                                                     # m3-L177
W30c = mpmathify("-8.75650812721829182493886e-27")                                       # claimed spec-30 value

print("T(40)      =", mp.nstr(T(40), 25), " claimed 1.8048513878454151723e-35")
print("T(30)      =", mp.nstr(T(30), 21), " claimed (addendum) 8.7565107626965203385e-27")
print("T(50)      =", mp.nstr(T(50), 21), " (README's recommended U>=50 floor)")
lhs = W40 + T(40)
print("W40+T(40)  =", mp.nstr(lhs, 29))
print("Winf       =", mp.nstr(Winf, 29))
print("closure rel diff (floor = Winf print width 29 sf) =", mp.nstr(abs(lhs-Winf)/Winf, 4))
print("T(40)/W40  =", mp.nstr(100*T(40)/W40, 4), "percent  <- 'the 0.69 percent'")
print("m3 vs Winf rel =", mp.nstr(abs(m3-Winf)/Winf, 3), " (all 11 m3 s.f. agree)")
W30 = Winf - T(30)
print("W(30)      =", mp.nstr(W30, 24))
print("W(30) claimed full-width match:", mp.nstr(W30, 24) == mp.nstr(W30c, 24))
# ratio consistency (addendum): T(30)/|Z_armA| with their Z from the .out
ZarmA = mpmathify("8.7565107626965203385e-27") / mpmathify("4.7102197930052690557e-25")
print("|Z_armA| implied =", mp.nstr(ZarmA, 8), "; T(30)/|Z_armA| =", mp.nstr(T(30)/ZarmA, 21),
      " published 4.7102e-25 (5 sf)")
