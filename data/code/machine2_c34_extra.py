"""machine2 CYCLE 34 -- extra knob probes at the BEST config, driving the FROZEN refit module.

m2_c34_refit.py is hash-frozen (c34_hashes_FROZEN.txt) and is NOT edited.  This driver imports
it and runs additional one-knob-at-a-time configs, writing into the same c34_refit.json.

Why these: batch 1 established, at the cfg-A knob set, that
  * G(0,0) = -4 (2 r_w)^{N_w} exactly and is invariant under npts / h_e  -> the centre channel
    is fed by trapezoid ALIASING alone;
  * varying h_e 1e-7 -> 1e-6 moves a5 by 2.068e-41 and varying npts 15 -> 17 moves it by
    -2.068e-51, a ratio of exactly 1e10 = 10^{npts-n} -> the FD-in-D TRUNCATION channel, whose
    size at cfg A is 2.07e-51 in a5.
Those two channels are measured at cfg A.  The question the cycle has to answer is which term
limits the BEST config, so the same two knobs are varied at the cfg-D knob set (N_w=72,
r_w=0.045, npts=17, dps=125), where the aliasing channel is (2r)^N = 1e-75 and therefore dead.

  DH8   D knobs, h_e 1e-7 -> 1e-8   : isolates D's FD truncation (truncation falls 10^{12})
  DP19  D knobs, npts 17 -> 19      : same channel, independent knob
  DQ150 D knobs, dps 125 -> 150     : isolates the evaluator's rounding of D and of xi
"""
import sys

sys.path.insert(0, "/workspace/rh/cycle34")
import m2_c34_refit as F
from multiprocessing import Pool

EXTRA = [
    F.cfg("DH8", dps=125, guard=30, r_w="0.045", N_w=72, npts=17, he=8),
    F.cfg("DP19", dps=125, guard=30, r_w="0.045", N_w=72, npts=19, he=7),
    F.cfg("DQ150", dps=150, guard=30, r_w="0.045", N_w=72, npts=17, he=7),
]

if __name__ == "__main__":
    import json
    import os
    import mpmath as mp

    only = sys.argv[1:] if len(sys.argv) > 1 else None
    dump = json.load(open(F.OUT)) if os.path.exists(F.OUT) else []
    for c in EXTRA:
        if only and c["label"] not in only:
            continue
        with Pool(8, initializer=F._init, initargs=(c,)) as pool:
            R = F.run(c, pool)
        mp.mp.dps = 90
        print(f"\n### cfg {c['label']}: dps={c['dps']} guard={c['guard']} r_w={c['r_w']} "
              f"N_w={c['N_w']} npts={c['npts']} h_e=1e-{c['he']} [{R['wall']:.0f}s]", flush=True)
        print(f"   controls: max|odd c_k|/|c_0| = {mp.nstr(R['odd_ctl'],4)}   "
              f"max|Im g|/|g| = {mp.nstr(R['im_ctl'],4)}")
        print(f"   G(0,0) = {mp.nstr(R['g00'], 25)}      etilde = {mp.nstr(R['et'], 12)}")
        for i, nm in enumerate(F.NAMES):
            print(f"   {nm:>3s} raw = {mp.nstr(R['x_raw'][i+1], 60)}")
            print(f"   {nm:>3s} rec = {mp.nstr(R['x_rec'][i+1], 60)}")
        dump = [d for d in dump if d["label"] != c["label"]]
        dump.append(dict(label=c["label"], cfg=dict(c), wall=R["wall"],
                         odd_ctl=mp.nstr(R["odd_ctl"], 6), im_ctl=mp.nstr(R["im_ctl"], 6),
                         g00=mp.nstr(R["g00"], 30), g01=mp.nstr(R["g01"], 20),
                         et=mp.nstr(R["et"], 30),
                         raw={nm: mp.nstr(R["x_raw"][i + 1], 70) for i, nm in enumerate(F.NAMES)},
                         rec={nm: mp.nstr(R["x_rec"][i + 1], 70) for i, nm in enumerate(F.NAMES)},
                         sens={nm: mp.nstr(R["sens"][i + 1], 15) for i, nm in enumerate(F.NAMES)}))
        with open(F.OUT, "w") as f:
            json.dump(dump, f, indent=1)
