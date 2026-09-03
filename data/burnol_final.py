import mpmath as mp
mp.mp.dps = 60

def g(u):
    u = mp.mpf(u)
    return mp.e**(-(mp.log(u))**2/2)

def ghat_closed(s):
    return mp.sqrt(2*mp.pi) * mp.e**(s**2/2)

def h(u):
    u = mp.mpf(u)
    L = mp.log(u)
    return (mp.sqrt(mp.pi)/u) * mp.e**((-L**2+2*L+1)/4)

def zero_side_sum(n_zeros=30):
    total = mp.mpf(0)
    for n in range(1, n_zeros+1):
        rho = mp.mpf('0.5') + 1j*mp.zetazero(n).imag
        term = ghat_closed(rho) * ghat_closed(1-rho)
        total += 2*mp.re(term)
    return total

Z_h = 2*ghat_closed(0)*ghat_closed(1) - zero_side_sum(30)

euler_gamma = mp.euler
def V_r_precise(func):
    term1 = (mp.log(mp.pi)+euler_gamma)/2 * func(1)
    term2 = mp.quad(lambda t: func(t)/t, [1, 2, 10, 100, mp.inf], maxdegree=10)
    g1 = func(1)
    def integrand3(t):
        if abs(t-1) < mp.mpf('1e-15'):
            fprime = mp.diff(func, 1)
            return fprime/2
        return (func(t)-g1)/(t**2-1)/t
    term3 = mp.quad(integrand3, [1, mp.mpf('1.0001'), 2, 10, 100, mp.inf], maxdegree=10)
    return term1+term2+term3

Vr_h = V_r_precise(h)

def primes_upto(N):
    sieve = bytearray([1])*(N+1)
    sieve[0]=sieve[1]=0
    for i in range(2,int(N**0.5)+1):
        if sieve[i]:
            for j in range(i*i,N+1,i):
                sieve[j]=0
    return [i for i in range(2,N+1) if sieve[i]]

def prime_side_sum(P_max, K_max=10):
    total = mp.mpf(0)
    for p in primes_upto(P_max):
        p = mp.mpf(p)
        for k in range(1, K_max+1):
            total += mp.log(p) * h(p**k)
            total += mp.log(p) * (1/p**k) * h(1/p**k)
    return total

ps = prime_side_sum(300000, K_max=10)

print("Z(h) [zero side]         =", Z_h)
print("Sum_p W_p(h)             =", ps)
print("2*V_r(h)                 =", 2*Vr_h)
RHS = ps + 2*Vr_h
print("RHS total (prime+arch)   =", RHS)
print("Z(h) - RHS                =", Z_h-RHS)
print("relative                  =", abs(Z_h-RHS)/abs(Z_h))
