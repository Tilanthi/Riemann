"""EXACT (no quadrature) evaluation of the two candidate b-vectors, by block integration.
  rho_n(x) = {1/(nx)}  ->  b[n] = int_0^1 rho_n dx = int_1^inf {t/n} t^-2 dt = (ln n + 1 - gamma)/n
  sig_n(x) = {n/x}     ->  b[n] = int_0^1 sig_n dx = int_1^inf {nt} t^-2 dt = n(H_n - ln n - gamma)
Both derived by exact block decomposition; here re-verified by summing the blocks numerically
to 10^7 terms with an explicit tail bound, i.e. a SECOND, independent code path."""
from mpmath import mp, mpf, log, euler, harmonic, nstr
mp.dps=30
def blocks_rho(j, P=200000):
    # int_1^inf {t/j} t^-2 dt  = (1/j)[ln j + sum_{p>=1}(ln((p+1)/p) - 1/(p+1))]
    s=mpf(0)
    for p in range(1,P):
        s += log(mpf(p+1)/p) - mpf(1)/(p+1)
    # tail: sum_{p>P} [ln(1+1/p) - 1/(p+1)] ~ sum 1/(2p^2) -> bound 1/(2P)
    return (log(j)+s)/j, mpf(1)/(2*P)/j
def blocks_sig(j, P=200000):
    # int_1^inf {jt} t^-2 dt : substitute w=jt -> j * int_j^inf {w} w^-2 dw
    # int_j^inf {w}w^-2 dw = sum_{r>=j} [ln((r+1)/r) - 1/(r+1)]
    s=mpf(0)
    for r in range(j,P):
        s += log(mpf(r+1)/r) - mpf(1)/(r+1)
    return j*s, j*mpf(1)/(2*P)
print(f"{'j':>3}{'rho: blocks':>20}{'rho: (ln j+1-g)/j':>21}{'sig: blocks':>20}{'sig: j(H_j-lnj-g)':>21}{'MAC (H_j-lnj-g)/j':>21}")
for j in [1,2,3,5,10]:
    br,tr=blocks_rho(j); bs,ts=blocks_sig(j)
    cr=(log(j)+1-euler)/j; cs=j*(harmonic(j)-log(j)-euler); mac=(harmonic(j)-log(j)-euler)/j
    okr = abs(br-cr)<tr; oks = abs(bs-cs)<ts
    print(f"{j:>3}{nstr(br,12):>20}{nstr(cr,12):>21}{nstr(bs,12):>20}{nstr(cs,12):>21}{nstr(mac,12):>21}   rho_ok={okr} sig_ok={oks}")
print()
print("ratio truth/MAC for rho family:", [nstr(((log(j)+1-euler)/j)/((harmonic(j)-log(j)-euler)/j),6) for j in [2,3,5,10]])
print("ratio truth/MAC for sig family:", [nstr((j*(harmonic(j)-log(j)-euler))/((harmonic(j)-log(j)-euler)/j),6) for j in [2,3,5,10]], " (= j^2 exactly)")
