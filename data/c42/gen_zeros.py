from mpmath import mp, zetazero
import json, time
mp.dps = 220
out=[]; t0=time.time()
for n in range(1,51):
    out.append(mp.nstr(zetazero(n).imag, 215))
    if n%5==0: print(n, "%.0fs"%(time.time()-t0), flush=True)
json.dump(out, open("/workspace/rh/cycle42/zeta_zeros_dps215.json","w"))
print("done %.0fs"%(time.time()-t0))
