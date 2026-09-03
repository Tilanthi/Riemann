from mpmath import mp, mpf, mpc, quad, zeta, floor, nstr, inf, findroot
mp.dps=30
rho=lambda u: u-floor(u)
def M_over_0_1(s):   # int_0^1 rho_1(x) x^{s-1} dx  with rho_1(x)={1/x}   == int_1^inf {u} u^{-s-1} du
    return quad(lambda u: rho(u)*u**(-s-1), [1]+[mpf(k) for k in range(2,60)]+[inf])
def M_over_0_inf(s): # int_0^inf {1/(a x)} x^{s-1} dx at a=1  == int_0^inf {u} u^{-s-1} du
    return quad(lambda u: rho(u)*u**(-s-1), [0,1]+[mpf(k) for k in range(2,60)]+[inf])
def M_fk(s,k):       # int_0^1 f_k x^{s-1} dx  = (k^-1 - k^-s) zeta(s)/s
    return (mpf(1)/k - mpf(k)**(-s))*zeta(s)/s
for s in [mpf('0.7'), mpc('0.7','3.0')]:
    a=M_over_0_1(s); b=M_over_0_inf(s)
    print("s=",s)
    print("  int_0^1 rho_1 x^{s-1}dx  =", nstr(a,12), " | claim 1/(s-1)-zeta(s)/s =", nstr(1/(s-1)-zeta(s)/s,12))
    print("  int_0^inf rho_1 x^{s-1}dx=", nstr(b,12), " | claim -zeta(s)/s          =", nstr(-zeta(s)/s,12))
# at a HYPOTHETICAL zero s0 with Re>1/2 the functional must kill every basis element.
# take the first actual zeta zero (on the line) as a stand-in to show the ALGEBRA, not to assume RH:
s0=mpc('0.5','14.134725141734693790')
print("\nAt s0 = 1/2 + 14.1347i  (zeta(s0)=",nstr(zeta(s0),6),"):")
print("  Mellin_{(0,1)} of f_2  =", nstr(M_fk(s0,2),8), "  -> 0 (annihilated)")
print("  Mellin_{(0,1)} of rho_1=", nstr(1/(s0-1)-zeta(s0)/s0,8), "  -> 1/(s0-1) != 0  (NOT annihilated)")
print("  Mellin_{(0,inf)} of rho_1=", nstr(-zeta(s0)/s0,8), " -> 0 (annihilated)")
