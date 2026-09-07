from mpmath import mp, mpf, mpmathify
mp.dps=80
ours_s = "3.72089974166712393579143476609e-59"
m3_s   = "3.720899741667123935791434766094540694091e-59"
ours=mpmathify(ours_s); m3=mpmathify(m3_s)
rel=(m3-ours)/m3
print("P1 rel diff recomputed :", mp.nstr(rel,12))
print("m3/m1 quoted           : 1.220321537e-30 / 1.2203e-30")
# significant-figure width of our published literal
dig_ours=len(ours_s.split('e')[0].replace('.','').replace('-',''))
dig_m3 =len(m3_s.split('e')[0].replace('.','').replace('-',''))
print("our published width    :",dig_ours,"s.f.   m3 published width:",dig_m3,"s.f.")
# CENSORING: what is the FULL RANGE of rel-diff consistent with 'first 30 digits identical'?
# m3's value must lie in [ours, ours+1ulp) for a truncated print, or +-0.5ulp for a rounded print.
ulp = mpmathify("1e-29")*mpmathify("1e-59")   # last printed digit is the 29th decimal of the mantissa
print("1 ulp of our print     :", mp.nstr(ulp,6), " (as rel):", mp.nstr(ulp/ours,6))
print("half-ulp (rounded print) as rel:", mp.nstr(ulp/2/ours,6))
print("observed rel / ulp-rel :", mp.nstr(rel/(ulp/ours),6))
# N=140 pair (m1's extension)
o140="3.19161872290429918777587895153e-59"; m140="3.191618722904299187775878951533394940265e-59"
r140=(mpmathify(m140)-mpmathify(o140))/mpmathify(m140)
print("N=140 rel diff recomputed:", mp.nstr(r140,12), " (m1 quoted 1.06e-30)")
print("N=140 observed rel / ulp-rel:", mp.nstr(r140/(mpmathify('1e-29')*mpmathify('1e-59')/mpmathify(o140)),6))
