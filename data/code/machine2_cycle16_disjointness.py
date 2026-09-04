"""CONDITION 1 -- disjointness stated as a TEST, not asserted.

Enumerate every REGION-VALUED search (a subset of the complex plane searched for zeros of a
named carrier) performed by machine 2 in cycles 1-15, mechanically, with file:line provenance,
then print the pairwise intersection of each against the cycle-16 target regions.
A prose claim of novelty does not satisfy the condition; an intersection area does.
"""
import subprocess, os, json, glob, re, sys

REPO = "/shared/rh-exchange-repo/Riemann"
PROG = "/shared/progress"

# ---------- 1. MECHANICAL SWEEP: which cycles contain a region-valued search at all? ----------
PAT = r"winding|argument principle|argument-principle|contour|zero count|zero-count|census|sign scan|sign-scan|root scan"
def sweep(paths):
    hits = {}
    for p in paths:
        try: txt = open(p, encoding="utf-8", errors="replace").read()
        except Exception: continue
        n = len(re.findall(PAT, txt, re.I))
        if n: hits[p] = n
    return hits

m2_letters = sorted(glob.glob(f"{REPO}/machine2-*.md"))
m2_code    = sorted(glob.glob(f"{REPO}/data/code/machine2*.py"))
m2_out     = sorted(glob.glob(f"{REPO}/data/machine2*.out"))
m2_prog    = sorted(glob.glob(f"{PROG}/rh-*.md"))
allpaths = m2_letters + m2_code + m2_out + m2_prog
hits = sweep(allpaths)
print("== SWEEP: machine-2 artefacts containing region-search vocabulary ==")
print("   denominator: %d machine-2 artefacts scanned (%d letters, %d code, %d out, %d progress)"
      % (len(allpaths), len(m2_letters), len(m2_code), len(m2_out), len(m2_prog)))
print("   pattern: /%s/i" % PAT)
for p, n in sorted(hits.items()):
    print("   HIT  %-70s %d" % (os.path.relpath(p, "/shared"), n))
print("   -> %d artefacts hit, %d clean" % (len(hits), len(allpaths) - len(hits)))

# ---------- 2. THE REGISTRY: every prior region, with the line that printed it ----------
# Each row: (label, carrier, sig_lo, sig_hi, t_lo, t_hi, converged?, provenance)
PRIOR = [
 ("C15-R1", "zeta2(s,1/7)", 0.52,   4.0,  -20.0, 20.0, True,
  "data/machine2_cycle15_stage5.out:'box Re[0.52,4.0] x Im[-20.0,20.0] n=1200 winding=-1 pole=1 => zeros~0, max step arg=2.5279'"),
 ("C15-R2", "zeta2(s,1/7)", 0.5001, 0.52,  -5.0,  5.0, False,
  "data/machine2_cycle15_stage5.out:'box Re[0.5001,0.52] x Im[-5.0,5.0] n=600 winding=6.0 max step arg=3.1313' -- VOID (aliased)"),
 ("C15-R3", "zeta2(s,1/7)", 0.46,   0.54,  -5.0,  5.0, True,
  "data/machine2_cycle15_stage6.out:'Re[0.46,0.54] x Im[-5.0,5.0] n=2400 winding=6.0 max step arg=0.27809'"),
 ("C15-R4", "zeta2(s,1/7)", 0.52,   2.0,   20.0, 43.0, False,
  "data/machine2_cycle15_stage7.out:'Re[0.52,2.0] x Im[20.0,43.0] n=2000 winding=-29.0 max step arg=3.1411' -- VOID (impossible)"),
 ("C15-R5", "zeta2(s,1/7)", 0.46,   0.54, -12.0, 12.0, True,
  "data/machine2_cycle15_stage8.out:'Re[0.46,0.54] x Im[-12,12] n=5000 zeros=20.0 max step arg=0.31835'"),
 ("C15-R6", "zeta2(s,1/7)", 1.5,    1e9,  -1e9,  1e9,  True,
  "data/machine2_cycle15_stage7.out: Dirichlet majorant, sum_{n>=2} a_n n^-1.5 = 0.2689 + 0.0156 < 1 => half-plane sigma>=1.5 zero-free"),
]
TARGET = [
 ("C16-V2", "zeta2(s,1/7)", 0.52,   2.0,   20.0, 43.0, "PRIMARY: the disclosed VOID wedge"),
 ("C16-V1", "zeta2(s,1/7)", 0.5001, 0.52,  -5.0,  5.0, "SECONDARY: the aliased thin box"),
]

def inter(a, b):
    x = max(0.0, min(a[3], b[3]) - max(a[2], b[2]))
    y = max(0.0, min(a[5], b[5]) - max(a[4], b[4]))
    return x * y, x, y

print("\n== TEST: pairwise intersection of each cycle-16 target with every prior machine-2 region ==")
verdict = {}
for tg in TARGET:
    ta = (tg[3] - tg[2]) * (tg[5] - tg[4])
    print("\n  TARGET %s  Re[%g,%g] x Im[%g,%g]  area=%.4f   (%s)" % (tg[0], tg[2], tg[3], tg[4], tg[5], ta, tg[6]))
    tot_overlap = 0.0; worst = None
    for pr in PRIOR:
        A, dx, dy = inter(tg, pr)
        contained = (pr[2] <= tg[2] and pr[3] >= tg[3] and pr[4] <= tg[4] and pr[5] >= tg[5])
        flag = "CONTAINS TARGET" if contained else ("overlap" if A > 0 else ("touches" if (dx > 0) != (dy > 0) or (dx == 0 and dy > 0) or (dy == 0 and dx > 0) else "disjoint"))
        print("    vs %-8s Re[%-7g,%-7g] Im[%-7g,%-7g] conv=%-5s : |intersection| = %.6f  (dRe=%.4f dIm=%.4f)  %s"
              % (pr[0], pr[2], pr[3], pr[4], pr[5], pr[6], A, dx, dy, flag))
        tot_overlap += A
        if contained: worst = pr[0]
    frac = tot_overlap / ta
    if worst:
        v = "FAIL-AS-NEW-SPACE (contained in %s) -> RE-EXAMINATION, not new territory" % worst
    elif tot_overlap == 0.0:
        v = "PASS (interior-disjoint from all %d prior regions; total intersection area 0.000000)" % len(PRIOR)
    else:
        v = "PARTIAL (%.4f%% of target already covered)" % (100 * frac)
    verdict[tg[0]] = v
    print("    VERDICT %s: %s" % (tg[0], v))

json.dump(dict(prior=[list(p) for p in PRIOR], target=[list(t) for t in TARGET], verdict=verdict,
               n_artefacts=len(allpaths), n_hits=len(hits)), open("disjointness.json", "w"), indent=1)
