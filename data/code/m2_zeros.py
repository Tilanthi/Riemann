"""machine2 cycle22 — cache zeta zeros with 0 < Im rho <= 210 at high precision."""
import json, time
from mpmath import mp

mp.dps = 50
out = []
n = 1
t0 = time.time()
while True:
    z = mp.zetazero(n)
    g = mp.im(z)
    if g > 210:
        break
    out.append(mp.nstr(g, 45))
    n += 1
print(len(out), "zeros, last", out[-1], f"{time.time()-t0:.1f}s")
json.dump(out, open("/workspace/rh/cycle22/zeros210.json", "w"))
