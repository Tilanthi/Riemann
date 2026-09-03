"""What does a d_N measurement actually CERTIFY about zeta zeros?
Ransford et al. Thm 3 proof gives, for any zero s with Re s>1/2:  d_N^2 >= (2 Re s - 1)/|s|^2.
Contrapositive: NO zero satisfies  2*Re s - 1 > d_N^2 * |s|^2.
Write s = 1/2 + eps + i t. The certified statement at height t is:
      no zero with Re s > 1/2 + eps(t),   eps solving  2 eps = D * (t^2 + (1/2+eps)^2),  D = d_N^2.
Solve the quadratic exactly:  D*eps^2 + (D - 2) eps + D(t^2 + 1/4) = 0."""
import math
C=0.0461914179
def eps_of(D,t):
    a=D; b=D-2.0; c=D*(t*t+0.25)
    disc=b*b-4*a*c
    if disc<0: return None
    return (-b-math.sqrt(disc))/(2*a)
def D_of_n(n): return C/math.log(n)
print("MEASURED d_N (this cycle / published), and the zero-free region it certifies\n")
print(f"{'N':>12}{'d_N':>10}{'D=d^2':>12}   eps(t) = certified margin above 1/2, at height t")
print(f"{'':>34}{'t=14.13':>12}{'t=25':>10}{'t=50':>10}{'t=100':>10}")
for n,d in [(70,0.1056158),(20000,None),(1e6,None),(1e12,None),(1.19e20,None)]:
    D=D_of_n(n) if d is None else d*d
    dd=math.sqrt(D)
    row=''.join(f"{eps_of(D,t):>10.4f}  " if eps_of(D,t) is not None else f"{'none':>10}  " for t in [14.1347,25,50,100])
    tag=" (MEASURED)" if d else ""
    print(f"{n:>12.4g}{dd:>10.5f}{D:>12.6f}   {row}{tag}")
print()
print("Inverse question: what N is needed to certify 'no zero with Re s > 1/2 + eps' at t = 14.1347?")
t=14.1347
for eps in [0.5,0.25,0.1,0.05,0.01]:
    D=2*eps/(t*t+(0.5+eps)**2)
    n=math.exp(C/D)
    print(f"   eps={eps:<5} -> D={D:.3e}  d_N={math.sqrt(D):.5f}  N >= e^{C/D:.1f} = 10^{(C/D)/math.log(10):.2f}")
