"""CYCLE 38 -- the four authorized runs.  The c34 producing script is IMPORTED, NEVER EDITED:
the only things that change are `centre`, `r_w`, `N_w` and the SERIALISATION WIDTH of g00.

Every constant is READ from a committed artefact (c37's law: in an audit of transcription, read
every constant from a file; never type one).
"""
import json, os, re, sys, time
from multiprocessing import Pool
import mpmath as mp

sys.path.insert(0, "/workspace/rh/cycle34")
import m2_c34_refit as C34                      # frozen producing script, imported not edited

R = "/shared/rh-exchange-repo/Riemann/"
_c36 = open(R + "machine2-c36-the-two-unanchored-checks-are-real-and-neither-touches-the-evaluator.md").read()
D175 = max(re.findall(r"0\.14173323966388719139541568508418502362314456[0-9]*", _c36), key=len)
_c34json = json.load(open('/workspace/rh/cycle34/c34_refit.json'))
C80 = _c34json[0]['cfg']['centre']
assert len(D175) - 2 == 175, len(D175)
assert C80 == C34.DSTAR_REFINED and len(C80) - 2 == 80

BASE = dict(C34.BASE)

def cfg(label, **kw):
    c = dict(BASE); c.update(kw); c["label"] = label
    c.setdefault("centre", D175)
    return c

RUNS = {
    # object 1 -- separate coefficient from channel at N_w = 40
    "R1": cfg("R1", r_w="0.045", N_w=40, centre=C80),        # print floor, other r_w
    "R2": cfg("R2", r_w="0.04",  N_w=40),                    # refined centre, c34 cfg A knobs
    "R3": cfg("R3", r_w="0.045", N_w=40),                    # refined centre, other r_w
    # object 2 -- the c34 re-run at the 175-digit centre, on the config c34 PUBLISHED from
    "R4": cfg("R4", dps=125, guard=30, r_w="0.045", N_w=72, npts=19),   # = DP19 knobs
    # ADDENDUM 1 -- dps is the ONLY knob changed in each case
    "R5": cfg("R5", dps=125, r_w="0.04", N_w=40),                       # = R2 with dps 90 -> 125
    "R6": cfg("R6", dps=150, guard=30, r_w="0.045", N_w=72, npts=19),   # = R4 with dps 125 -> 150
    # ADDENDUM 2 -- R2 with r_w the ONLY change; the model predicts a SIGN FLIP here
    "R7": cfg("R7", r_w="0.035", N_w=40),
}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c38_runs.json")

if __name__ == "__main__":
    dump = json.load(open(OUT)) if os.path.exists(OUT) else []
    for lab in sys.argv[1:]:
        c = RUNS[lab]
        t0 = time.time()
        with Pool(8, initializer=C34._init, initargs=(c,)) as pool:
            Rr = C34.run(c, pool)
        mp.mp.dps = 200
        print(f"\n### {lab}: dps={c['dps']} guard={c['guard']} r_w={c['r_w']} N_w={c['N_w']} "
              f"npts={c['npts']} h_e=1e-{c['he']} centre={len(c['centre'])-2}-digit "
              f"[{Rr['wall']:.0f}s]", flush=True)
        print(f"   controls: max|odd|/|c0| = {mp.nstr(Rr['odd_ctl'],4)}   max|Im g|/|g| = {mp.nstr(Rr['im_ctl'],4)}")
        alias = -4 * (2 * mp.mpf(c['r_w'])) ** c['N_w']
        eps = Rr['g00'] - alias
        print(f"   g00 (30 s.f., c34's own width) = {mp.nstr(Rr['g00'], 30, strip_zeros=False)}")
        print(f"   g00 (90 s.f., FULL)            = {mp.nstr(Rr['g00'], 90, strip_zeros=False)}")
        print(f"   eps = g00 + 4(2 r_w)^N_w       = {mp.nstr(eps, 30)}")
        print(f"   implied D* = {mp.nstr(mp.mpf(c['centre']) - Rr['et'], 80)}")
        for i, nm in enumerate(C34.NAMES):
            print(f"   {nm:>3s} raw = {mp.nstr(Rr['x_raw'][i+1], 70)}")
            print(f"   {nm:>3s} rec = {mp.nstr(Rr['x_rec'][i+1], 70)}   S = {mp.nstr(Rr['sens'][i+1], 15)}")
        dump = [d for d in dump if d["label"] != lab]
        dump.append(dict(label=lab, cfg=c, wall=Rr["wall"],
                         odd_ctl=mp.nstr(Rr["odd_ctl"], 6), im_ctl=mp.nstr(Rr["im_ctl"], 6),
                         g00=mp.nstr(Rr["g00"], 90, strip_zeros=False),
                         g00_30=mp.nstr(Rr["g00"], 30, strip_zeros=False),
                         eps=mp.nstr(eps, 30), g01=mp.nstr(Rr["g01"], 40),
                         et=mp.nstr(Rr["et"], 90),
                         raw={nm: mp.nstr(Rr["x_raw"][i+1], 70) for i, nm in enumerate(C34.NAMES)},
                         rec={nm: mp.nstr(Rr["x_rec"][i+1], 70) for i, nm in enumerate(C34.NAMES)},
                         sens={nm: mp.nstr(Rr["sens"][i+1], 15) for i, nm in enumerate(C34.NAMES)}))
        json.dump(dump, open(OUT, "w"), indent=1)
        print(f"   [wrote {OUT}, {time.time()-t0:.0f}s total]", flush=True)
