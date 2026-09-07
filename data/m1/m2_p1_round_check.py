from mpmath import mp, mpmathify
mp.dps = 200   # first executable line (the adopted habit), well above the 130-digit literal
m2_130 = mpmathify("3.720899741667123935791434766094540694091385619140619522831293472355645252511338501707715701126959943461337701579966383375965519379e-59")
m3_65  = "3.7208997416671239357914347660945406940913856191406195228312934724"
# round m2's value to 65 s.f. the way nstr would
rounded = mp.nstr(m2_130, 65)
print("m2 rounded to 65 :", rounded)
print("m3 literal       :", m3_65 + "e-59")
print("EXACT MATCH      :", rounded == m3_65 + "e-59")
# raw prefix (truncation semantics) - the near-false-headline they flagged
raw = mp.nstr(m2_130, 130)
print("raw 65-digit truncation of m2_130:", raw[:66], " (differs from m3 at final digit: 3 vs 4)")
