"""machine2 cycle22 — answers to m1-L144 (counterparty attack) and m3-L144."""
import json
from mpmath import mp
from m2_u_instrument import Basis, load_genomes, load_target
from m2_witness_analysis import gram, lam, mat, zero_pair_K, N
mp.dps = 40
gens = load_genomes("s1/M8"); tgt = load_target("s1/M8")
gam = [mp.mpf(g) for g in json.load(open("zeros210.json"))]
bases = [Basis(g, degree=8) for g in gens]
half = mp.mpf(1)/2
G = gram(); K200 = mat(tgt["K_T200"])
up200 = [g for g in gam if g <= 200]

def Q_analytic(delta, g0):
    p = mp.mpc(half+delta, g0); q = mp.mpc(half-delta, g0)
    up=[b.u(p) for b in bases]; uq=[b.u(q) for b in bases]
    M = mp.matrix(N,N)
    for i in range(N):
        for j in range(N):
            M[i,j] = 2*mp.re(up[i]*mp.conj(uq[j]) + up[j]*mp.conj(uq[i]))
    return M

g1,g2 = up200[0], up200[1]; g0=(g1+g2)/2
base = K200 - zero_pair_K(mp.mpc(half,g1)) - zero_pair_K(mp.mpc(half,g2))
print("=== m1-L144 sect4B: launch points (removal only), G-metric ===")
print(f"PAIR-A removal-only lam_min = {mp.nstr(lam(base,G)[0],10)}   (m1: 3.3758e-7)")
b1,b2 = up200[70], up200[71]
baseB = K200 - zero_pair_K(mp.mpc(half,b1)) - zero_pair_K(mp.mpc(half,b2))
print(f"PAIR-B removal-only lam_min = {mp.nstr(lam(baseB,G)[0],10)}   (m1: 1.176119e-5)")

print("\n=== m1-L144 sect4C: diagnostic 3' at LAMBDA level ===")
for nm,(x1,x2,bs) in {"PAIR-A":(g1,g2,base),"PAIR-B":(b1,b2,baseB)}.items():
    es=(x2-x1)/2; m0=(x1+x2)/2
    A = zero_pair_K(mp.mpc(half,m0+es))+zero_pair_K(mp.mpc(half,m0-es))
    l = lam(bs+A,G)[0]
    print(f"  {nm}: lam_min(S_Z(eta*),G) = {mp.nstr(l,20)}  vs anchor {mp.nstr(lam(K200,G)[0],20)}"
          f"  |diff| = {mp.nstr(abs(l-lam(K200,G)[0]),4)}")

print("\n=== m1-L144 sect1: his analytic/Gram entry ratios at (0,0), gamma_0=17.578382 ===")
for d in ["0.1","0.45","0.2"]:
    dd=mp.mpf(d); p=mp.mpc(half+dd,g0); q=mp.mpc(half-dd,g0)
    a=bases[0].u(p); b=bases[0].u(q)
    S00 = 2*mp.re(a*mp.conj(b)+a*mp.conj(b))
    K00 = 2*mp.re(a*mp.conj(a)) + 2*mp.re(b*mp.conj(b))
    print(f"  delta={d:>5}  analytic/Gram = {mp.nstr(S00/K00,6)}   (m1: 0.651 at 0.1, 0.0282 at 0.45)")

print("\n=== transport analysis: c2 of the SCORED object vs the difference form ===")
l0 = lam(base+Q_analytic(mp.mpf(0),g0),G)[0]
for d in ["0.001","0.01","0.05"]:
    dd=mp.mpf(d)
    l = lam(base+Q_analytic(dd,g0),G)[0]
    print(f"  delta={d:>6}  (lam(0)-lam(d))/d^2 = {mp.nstr((l0-l)/dd**2,6)}")
print("  difference-form coefficient measured pre-run: 0.266")

print("\n=== m1-L144 sect4A generalisation: ordinate sweep at delta=0.1 across the PAIR-A gap ===")
print(f"{'gamma_0':>12} {'lam_min(S_Z(0.1))':>24} {'launch (removal only)':>24}")
lo, hi = g1, g2
for k in range(9):
    gg = lo + (hi-lo)*mp.mpf(k)/8
    l = lam(base+Q_analytic(mp.mpf("0.1"), gg),G)[0]
    print(f"{mp.nstr(gg,8):>12} {mp.nstr(l,10):>24} {mp.nstr(lam(base,G)[0],10):>24}")
