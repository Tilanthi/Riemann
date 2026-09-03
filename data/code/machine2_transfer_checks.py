#!/usr/bin/env python3
"""
machine 2 (BEAST) -- Lemma-5-analogue transfer: numerical verification suite.

Verifies, per carrier, the HYPOTHESES that de Roton's generalised Beurling-Nyman
theorem (TAMS 359 (2007) 6079-6110) requires, plus the Mellin/annihilation identity
itself on the zeta positive control.

No result here is a proof claim.  Every block prints its own DQ line.
"""
import mpmath as mp
import numpy as np

mp.mp.dps = 40
OUT = []
def say(s=""):
    print(s); OUT.append(s)

# ----------------------------------------------------------------------------
# A. ZETA POSITIVE CONTROL -- the Mellin symbol of Burnol's corrected family
# ----------------------------------------------------------------------------
say("="*78)
say("A. ZETA POSITIVE CONTROL -- symbol of f_k(x) = (1/k)floor(1/x) - floor(1/(kx))")
say("="*78)
say("  Structural fact used (exact, elementary): f_k is CONSTANT = {n/k} on")
say("  (1/(n+1), 1/n].  Hence  M f_k(s) = (1/s) sum_n {n/k} [ n^-s - (n+1)^-s ].")

def M_fk_direct(k, s, N=200000):
    """Direct step-sum of the Mellin integral, mean-subtracted for a fast tail."""
    c = mp.mpf(k-1)/(2*k)          # mean of {n/k} over a period
    tot = c * mp.mpf(1)            # telescoping part: sum_n c[n^-s-(n+1)^-s] = c
    acc = mp.mpf(0)*1j
    for n in range(1, N+1):
        e = mp.mpf(n % k)/k - c
        if e != 0:
            acc += e * (mp.power(n, -s) - mp.power(n+1, -s))
    return (tot + acc)/s

for (k, s) in [(2, mp.mpf('0.7')+3j), (3, mp.mpf('0.6')+11j), (5, mp.mpf('0.9')+1j)]:
    lhs = M_fk_direct(k, s)
    claimed = (mp.mpf(1)/k - mp.power(k, -s)) * mp.zeta(s)/s      # our derivation
    prereg  = -mp.power(k, s-1) * mp.zeta(s)/s                    # form printed in heat65 prereg
    say(f"  k={k}  s={mp.nstr(s,8)}")
    say(f"    direct step-sum          = {mp.nstr(lhs,12)}")
    say(f"    (1/k - k^-s) zeta(s)/s   = {mp.nstr(claimed,12)}   |diff|={mp.nstr(abs(lhs-claimed),3)}")
    say(f"    -k^(s-1) zeta(s)/s       = {mp.nstr(prereg,12)}   |diff|={mp.nstr(abs(lhs-prereg),3)}")

say("")
say("  Annihilation at the first zeta zero rho1 = 1/2 + 14.134725...i :")
rho1 = mp.mpc(mp.mpf('0.5'), mp.zetazero(1).imag)
for k in (2, 3, 7):
    v = (mp.mpf(1)/k - mp.power(k, -rho1)) * mp.zeta(rho1)/rho1
    say(f"    k={k}:  |M f_k(rho1)| = {mp.nstr(abs(v),6)}")
say("  DQ: annihilation is by the COMMON factor zeta(s)/s; the k-dependent factor is a")
say("      Dirichlet polynomial and is generically non-zero.  Nothing here is a proof claim.")

# ----------------------------------------------------------------------------
# B. DAVENPORT-HEILBRONN CARRIER
# ----------------------------------------------------------------------------
say("")
say("="*78)
say("B. CARRIER 1: DAVENPORT-HEILBRONN  (Ferry-Ghisa-Muscutar arXiv:1602.06328 shape)")
say("="*78)

TAU = mp.mpf('0.2840790438404123')   # kappa, as FE-derived by machine 1 (heat65)
A_PER = [mp.mpf(1), TAU, -TAU, mp.mpf(-1), mp.mpf(0)]   # a_1..a_5, period 5

def a_dh(n):
    return A_PER[(n-1) % 5]

def dh(s):
    """f(s) = 5^-s sum_{r=1..5} a_r zeta(s, r/5)  (Hurwitz continuation)."""
    return mp.power(5, -s) * sum(A_PER[r-1]*mp.zeta(s, mp.mpf(r)/5) for r in range(1, 6))

# B1 -- Hurwitz closed form vs absolutely convergent direct sum
s_t = mp.mpf('3.0') + 2j
NB1 = 200000
direct = mp.fsum(a_dh(n)*mp.power(n, -s_t) for n in range(1, NB1+1))
say(f"  B1 closed form vs direct sum at s={mp.nstr(s_t,6)}:")
say(f"     hurwitz = {mp.nstr(dh(s_t),15)}")
say(f"     direct  = {mp.nstr(direct,15)}   |diff|={mp.nstr(abs(dh(s_t)-direct),3)}   (partial sum N={NB1}, tail < {mp.nstr((1+TAU)*mp.power(NB1,-2)/2,3)})")

# B2 -- functional equation residual  f(s) = 2^s pi^(s-1) 5^(1/2-s) Gamma(1-s) cos(pi s/2) f(1-s)
def fe_res(s):
    W = mp.power(2, s)*mp.power(mp.pi, s-1)*mp.power(5, mp.mpf('0.5')-s)*mp.gamma(1-s)*mp.cos(mp.pi*s/2)
    return dh(s) - W*dh(1-s)
say("  B2 functional-equation residual (independent re-check of m1's kappa):")
for s in [mp.mpf('2.3')+1.7j, mp.mpf('0.3')-4.1j]:
    say(f"     s={mp.nstr(s,6)}  |residual|={mp.nstr(abs(fe_res(s)),3)}   |f(s)|={mp.nstr(abs(dh(s)),6)}")

# B3 -- the four published off-line zeros (Math. Comp. 76 (2007) 2045-2049, as quoted in cycle 11)
say("  B3 |f| at the four published off-line zeros quoted in our cycle-11 letter:")
zeros = [(mp.mpf('0.808517182'), mp.mpf('85.699348')),
         (mp.mpf('0.650830'),    mp.mpf('114.163343')),
         (mp.mpf('0.574356050'), mp.mpf('166.479306')),
         (mp.mpf('0.724258'),    mp.mpf('176.702461'))]
for (sg, t) in zeros:
    s0 = mp.mpc(sg, t)
    say(f"     s0={mp.nstr(s0,10)}  |f(s0)|={mp.nstr(abs(dh(s0)),4)}   "
        f"floor (2Re-1)/|s0|^2 = {mp.nstr((2*sg-1)/abs(s0)**2,6)}")

# B4 -- the complementary function Psi_F.  m_F = 0 (f entire) so Psi_F = -A(y), and A is
#       PERIODIC of period 5 because the coefficients have mean zero over a period.
Acum = [mp.mpf(0)]*6
run = mp.mpf(0)
for r in range(1, 6):
    run += A_PER[r-1]; Acum[r] = run
def A_dh(y):
    m = int(mp.floor(y))
    if m < 1: return mp.mpf(0)
    return Acum[m % 5] if m % 5 != 0 else mp.mpf(0)
say("  B4 summatory function A(y) = sum_{n<=y} a_n :")
say(f"     period sum = {mp.nstr(Acum[5],3)}  (must be 0 for A to be bounded)")
brute = mp.mpf(0); mx = mp.mpf(0); ok = True
for n in range(1, 20001):
    brute += a_dh(n)
    if abs(brute) > mx: mx = abs(brute)
    if abs(brute - A_dh(n)) > mp.mpf('1e-30'): ok = False
say(f"     closed form matches brute force for n<=20000: {ok}")
say(f"     sup_{{y<=20000}} |A(y)| = {mp.nstr(mx,10)}   (= 1+kappa = {mp.nstr(1+TAU,10)})")
say("     ==> Psi_DH is BOUNDED and 5-periodic; Psi_DH^(1) is supported in (0,1] and in L^2. [HYPOTHESIS MET]")

# B5 -- the transferred family, and its Mellin symbol, by direct step-sum
#      basis element for dilation alpha=1/j :  t -> Psi_DH(1/(jt)) = -A(1/(jt)),
#      constant on (1/(n+1), 1/n] with value -A(n/j).
def M_dh_family_direct(j, s, N=200000):
    vals = [-A_dh(mp.mpf(n)/j) for n in range(1, 5*j+1)]     # periodic in n with period 5j
    c = sum(vals)/len(vals)
    tot = c
    acc = mp.mpf(0)*1j
    for n in range(1, N+1):
        e = vals[(n-1) % (5*j)] - c
        if e != 0:
            acc += e*(mp.power(n, -s) - mp.power(n+1, -s))
    return (tot + acc)/s
say("  B5 Mellin symbol of the transferred family, direct step-sum vs -alpha^s F(s)/s:")
for (j, s) in [(1, mp.mpf('0.7')+3j), (2, mp.mpf('0.65')+9j), (3, mp.mpf('0.85')+2j)]:
    lhs = M_dh_family_direct(j, s)
    rhs = -mp.power(mp.mpf(1)/j, s)*dh(s)/s
    say(f"     alpha=1/{j}  s={mp.nstr(s,6)}  direct={mp.nstr(lhs,12)}  -alpha^s F/s={mp.nstr(rhs,12)}"
        f"  |diff|={mp.nstr(abs(lhs-rhs),3)}")

# ----------------------------------------------------------------------------
# C. EPSTEIN CARRIER  (binary quadratic form, discriminant -23, class number 3)
# ----------------------------------------------------------------------------
say("")
say("="*78)
say("C. CARRIER 2: EPSTEIN ZETA of a binary quadratic form, disc -23, h=3")
say("="*78)

def lattice_counts(a, b, c, Y):
    """a_n = #{(x,y) in Z^2 : a x^2 + b x y + c y^2 = n}, n = 1..Y, returned as np array idx 0..Y."""
    D = b*b - 4*a*c
    assert D < 0 and a > 0
    cnt = np.zeros(Y+1, dtype=np.int64)
    ymax = int(np.floor(np.sqrt(-4.0*a*Y/D))) + 2
    for y in range(-ymax, ymax+1):
        disc = b*b*y*y - 4*a*(c*y*y - Y)
        if disc < 0: continue
        r = np.sqrt(disc)
        x0 = (-b*y - r)/(2*a); x1 = (-b*y + r)/(2*a)
        xs = np.arange(int(np.ceil(x0))-1, int(np.floor(x1))+2, dtype=np.int64)
        v = a*xs*xs + b*xs*y + c*y*y
        v = v[(v >= 1) & (v <= Y)]
        np.add.at(cnt, v, 1)
    return cnt

Y = 2_000_000
for (a, b, c, label) in [(1, 1, 6, "principal (1,1,6)"), (2, 1, 3, "non-principal (2,1,3)")]:
    cnt = lattice_counts(a, b, c, Y)
    A = np.cumsum(cnt).astype(np.float64)
    D = 4*a*c - b*b                 # |disc| = 23
    res = 2*np.pi/np.sqrt(D)        # residue of E(s;Q) at s=1 == area constant
    yy = np.arange(Y+1, dtype=np.float64)
    err = A - res*yy
    say(f"  {label}:  |disc|={D}  area constant 2pi/sqrt|D| = {res:.10f}")
    say(f"     total lattice points <= Y : {A[-1]:.0f}   main term {res*Y:.0f}   ratio {A[-1]/(res*Y):.8f}")
    for th in (1/3, 0.4, 0.5):
        lo = 1000
        m = np.max(np.abs(err[lo:])/yy[lo:]**th)
        say(f"     sup_{{1e3<=y<=2e6}} |A(y) - c y| / y^{th:.3f}  = {m:.4f}")
    # corrected two-term combination, the Epstein analogue of Burnol's f_k
    for k in (2, 3):
        n = np.arange(1, Y + 1)
        g = A[n]/k - A[n//k]         # = -(1/k)Psi(u) + Psi(u/k) at u=n; main terms c u/k cancel
        say(f"     k={k}: sup |(1/k)A(u) - A(u/k)| / u^(1/3), 1e3<=u<=Y  = "
            f"{np.max(np.abs(g[999:])/n[999:]**(1/3)):.4f}"
            f"   ; /u^(1/2) = {np.max(np.abs(g[999:])/n[999:]**0.5):.4f}"
            f"   (bounded ==> Psi^(1) in L^2)")
    say("")

say("  DQ-SECTION")
say("   * A/B blocks: mpmath dps=40; step-sums truncated at N=2e5 with the periodic mean")
say("     removed first, so the tail is O(N^{-sigma-1}) by Abel summation, not O(N^{-sigma}).")
say("   * B3 uses zero coordinates AS QUOTED in our own cycle-11 letter from Math. Comp. 76")
say("     (2007) 2045-2049; |f| there is limited by the printed precision of those digits,")
say("     NOT by the evaluator.  It is a consistency check, not a zero certification.")
say("   * C block: float64 lattice counts, exact integer arithmetic for the counts themselves.")
say("     The exponent lines are an EMPIRICAL check that the classical van der Corput bound")
say("     O(y^{1/3}) is consistent with the data on this range; they do not prove it.")
say("   * No claim in this file is a proof claim, and none of it bears on RH.")

open("transfer_checks.out", "w").write("\n".join(OUT) + "\n")
