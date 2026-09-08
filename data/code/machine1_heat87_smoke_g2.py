#!/usr/bin/env python3
"""heat87 gen-2 smoke — pre-prereg instrument check. NO mutant cell is computed.

Stage 1 (#143): import the sealed census runner byte-identical, seals 3/3.
Stage 2: build the M64 instrument; re-solve TWO public cells only — the G1
control k=0 @ delta=0 and the founder 18/0.05 — and check both against the
committed census values.  Every gen-2 mutant cell (0.0540 ... 0.0580) stays
untouched until after the prereg push.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import machine1_heat78c_survivor_census as census  # noqa: E402
from mpmath import mp, mpf, zetazero  # noqa: E402

mp.dps = 45
THRESH = mpf("-1e-12")
CENSUS_RUNNER_SHA = "88ab08f82fc8d14453dc064ba292dd35dc57541a5acc45f0d0bf10cd2721cd53"
CENSUS_JSON = os.path.join(HERE, "..", "heat78c_census_result.json")
CENSUS_JSON_SHA = "3d2f1d7a771a689d460f8e6994b98a8458c5ca8825f06f6f805c7a14393cc920"
T0 = time.time()


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    print("stage 1: seals")
    got = sha(os.path.join(HERE, "machine1_heat78c_survivor_census.py"))
    print("  census runner: %s" % ("OK" if got == CENSUS_RUNNER_SHA else "FAIL %s" % got))
    assert got == CENSUS_RUNNER_SHA
    got = sha(os.path.normpath(CENSUS_JSON))
    print("  census json:   %s" % ("OK" if got == CENSUS_JSON_SHA else "FAIL %s" % got))
    assert got == CENSUS_JSON_SHA
    census.check_seals()
    print("  check_seals:   3/3 OK")
    cj = json.load(open(os.path.normpath(CENSUS_JSON)))["results"]

    print("stage 2: instrument + two public cells")
    gdata = json.load(open(census.GEN))["genomes"]
    k64 = json.load(open(census.K64))
    M = 64
    genomes = gdata["s1/M64"]
    phis, edges = zip(*[census.make_phi(g) for g in genomes])
    K = mp.matrix(M, M)
    G = mp.matrix(M, M)
    for i in range(M):
        for j in range(M):
            K[i, j] = mpf(k64["K_T200"][i][j])
            G[i, j] = mpf(k64["G_raw"][i][j])
    inst = census.Instrument(M, K, G, phis, edges)
    print("  instrument built %.1fs" % (time.time() - T0))
    zeros = [mpf(str(zetazero(n).imag)) for n in range(1, 28)]

    def g_of(k, phi8=4):
        return zeros[k] + (zeros[k + 1] - zeros[k]) * mpf(phi8) / 8

    def solve(k, dstr):
        KS = inst.K - inst.gram(zeros[k]) - inst.gram(zeros[k + 1]) + inst.quad_ex(g_of(k), mpf(dstr))
        vals, _ = inst.eig(KS)
        return vals[0]

    lam0 = solve(0, "0")
    ok0 = not (lam0 < THRESH)
    print("  control k=0 d=0: lam %s fires=%r (expect False) -> %s"
          % (mp.nstr(lam0, 12), bool(lam0 < THRESH), "OK" if ok0 else "FAIL"))
    lamf = solve(18, "0.05")
    ref = mpf(cj["64/18/4/0.05"]["lam_min"])
    rel = abs(lamf - ref) / abs(ref)
    okf = rel <= mpf("1e-9")
    print("  founder 18/0.05: lam %s rel %s -> %s"
          % (mp.nstr(lamf, 12), mp.nstr(rel, 3), "OK" if okf else "FAIL"))
    print("SMOKE %s  (%.1fs)" % ("PASS" if (ok0 and okf) else "FAIL", time.time() - T0))
    return 0 if (ok0 and okf) else 1


if __name__ == "__main__":
    sys.exit(main())
