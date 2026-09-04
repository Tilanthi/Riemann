import sys,os
sys.path.insert(0,'.')
from mpmath import mp, mpf, mpc, zeta, altzeta, nstr, log, pi, sqrt
from machine2_cycle15_epstein_fold import zeta2, set_cut, digits
mp.dps=30; set_cut(30)
def beta(s):
    return mpf(4)**(-s)*(mp.zeta(s,mpf(1)/4)-mp.zeta(s,mpf(3)/4))
print("== N8 entry-gate arithmetic sanity battery (does it compute; do its objects exist) ==")
print("S1  D=1 factorisation  zeta2(s,1) =? 2 zeta(s) beta(s)")
for s in [mpc('1.3'), mpc('0.75'), mpc(mpf(1)/2, 14), mpc(mpf(1)/2,21)]:
    a=zeta2(s,mpf(1)); b=2*zeta(s)*beta(s)
    print("    s=%-22s zeta2=%-26s 2*zeta*beta=%-26s agree %s dig"%(nstr(s,10),nstr(a,12),nstr(b,12),nstr(digits(a,b),6)))
print("S2  parameter involution  zeta2(s,1/D) =? D^{2s} zeta2(s,D)   (=> identical zero sets)")
for D in ['0.1417332396638872','0.14285714285714285714','0.5','0.9']:
    Dm=mpf(D)
    for s in [mpc('1.3'), mpc(mpf(1)/2, 11.3)]:
        a=zeta2(s,1/Dm); b=Dm**(2*s)*zeta2(s,Dm)
        print("    D=%-22s s=%-16s agree %s dig"%(D,nstr(s,8),nstr(digits(a,b),6)))
print("S3  the fixed point of iota is D=1 ; the fold pair {Dstar, 1/Dstar} is one iota-orbit")
DS=mpf('0.1417332396638871913954156850841850236')
print("    Dstar   = %s"%nstr(DS,25))
print("    1/Dstar = %s"%nstr(1/DS,25))
print("    log Dstar = %s   log(1/Dstar) = %s  (u=|log D| coordinate)"%(nstr(log(DS),12),nstr(log(1/DS),12)))
print("S4  sigma_max is iota-invariant BY THE IDENTITY (not by measurement): sigma_max(D)=sigma_max(1/D)")
print("    => sigma_max is a function of u=|log D| alone. u(1/7)=%s, u(1)=0"%nstr(abs(log(mpf(1)/7)),12))
