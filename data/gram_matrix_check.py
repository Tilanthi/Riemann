import mpmath as mp
import time

mp.mp.dps = 40

# ============================================================
# Independent re-coding of Mac's Gram-matrix mutation (route 1 eigenvalue ladder)
# using MY Burnol prime-side+archimedean split, as a disjoint cross-check.
# Basis: dilated Gaussians phi_j(u) = g(u/a_j), g(u)=exp(-(ln u)^2/2).
# phihat_j(s) = a_j^s * ghat(s), ghat(s) = sqrt(2pi) e^{s^2/2}.
# K_N[j,k] = sum_rho phihat_j(rho) phihat_k(1-rho)
#          = phihat_j(0)phihat_k(1) + phihat_j(1)phihat_k(0) - [sum_p W_p(h_jk) + W_r(h_jk)]
# with h_jk = phi_j * phi_k^tau (multiplicative convolution).
# ============================================================

def ghat(s):
    return mp.sqrt(2*mp.pi) * mp.e**(s**2/2)

def phihat(j_a, s):
    return j_a**s * ghat(s)

# phi_j(u) = g(u/a_j); phi_j^tau(x) = phi_j(1/x)/x = g(1/(a_j x))/x
# h_jk(u) = (phi_j * phi_k^tau)(u) = int phi_j(t) phi_k^tau(u/t) dt/t
# Direct closed form via the same Gaussian-completion-of-square trick as before,
# generalized for two different dilations a_j, a_k. Let's derive:
#   phi_j(t) = exp(-(ln t - ln a_j)^2/2),  phi_k^tau(x) = phi_k(1/x)/x = exp(-(ln(1/x)-ln a_k)^2/2)/x
#            = exp(-(ln x + ln a_k)^2/2)/x
# h_jk(u) = int_0^inf phi_j(t) phi_k^tau(u/t) dt/t
# sub t=e^x: = int exp(-(x-Lj)^2/2) * exp(-(ln(u)-x+Lk)^2/2) * (t/u) dx   [phi_k^tau(u/t)=exp(-(ln(u/t)+Lk)^2/2)*(t/u)]
# where Lj=ln(a_j), Lk=ln(a_k), Lu=ln(u).
# = (1/u) int exp(-(x-Lj)^2/2 - (Lu-x+Lk)^2/2 + x) dx
def h_closed(u, Lj, Lk):
    u = mp.mpf(u)
    Lu = mp.log(u)
    # exponent: -(x-Lj)^2/2 - (Lu-x+Lk)^2/2 + x, expand and complete the square in x
    # Let A = Lu+Lk. -(x-Lj)^2/2-(A-x)^2/2+x
    # = -[x^2-2Ljx+Lj^2 + A^2-2Ax+x^2]/2 + x = -[2x^2-2(Lj+A)x+Lj^2+A^2]/2+x
    # = -x^2+(Lj+A)x-(Lj^2+A^2)/2+x = -x^2+(Lj+A+1)x-(Lj^2+A^2)/2
    A = Lu+Lk
    B_coef = Lj+A+1
    C_coef = (Lj**2+A**2)/2
    # int exp(-x^2+B x - C) dx = sqrt(pi) exp(B^2/4 - C)
    integral = mp.sqrt(mp.pi)*mp.e**(B_coef**2/4 - C_coef)
    return integral/u

def primes_upto(N):
    sieve = bytearray([1])*(N+1)
    sieve[0]=sieve[1]=0
    for i in range(2,int(N**0.5)+1):
        if sieve[i]:
            for j in range(i*i,N+1,i):
                sieve[j]=0
    return [i for i in range(2,N+1) if sieve[i]]

PRIMES = primes_upto(300000)

def prime_side_sum(hfunc, K_max=10):
    total = mp.mpf(0)
    for p in PRIMES:
        p = mp.mpf(p)
        for k in range(1, K_max+1):
            total += mp.log(p) * hfunc(p**k)
            total += mp.log(p) * (1/p**k) * hfunc(1/p**k)
    return total

def V_r(func):
    euler_gamma = mp.euler
    term1 = (mp.log(mp.pi)+euler_gamma)/2 * func(1)
    term2 = mp.quad(lambda t: func(t)/t, [1, 2, 10, 100, mp.inf], maxdegree=10)
    g1 = func(1)
    def integrand3(t):
        if abs(t-1) < mp.mpf('1e-15'):
            return mp.diff(func, 1)/2
        return (func(t)-g1)/(t**2-1)/t
    term3 = mp.quad(integrand3, [1, mp.mpf('1.0001'), 2, 10, 100, mp.inf], maxdegree=10)
    return term1+term2+term3

def K_entry_burnol(a_j, a_k):
    Lj, Lk = mp.log(a_j), mp.log(a_k)
    hfunc = lambda u: h_closed(u, Lj, Lk)
    zero_part = phihat(a_j,0)*phihat(a_k,1) + phihat(a_j,1)*phihat(a_k,0)
    ps = prime_side_sum(hfunc, K_max=10)
    # h_jk is generally NOT symmetric under tau (h^tau != h unless j=k), so W_r != 2*V_r in general.
    # W_r(h) = V_r(h) + V_r(h^tau).  h^tau(x) = h(1/x)/x -- compute directly.
    def h_tau(x):
        return hfunc(1/mp.mpf(x))/mp.mpf(x)
    Wr = V_r(hfunc) + V_r(h_tau)
    return zero_part - ps - Wr

# Independent cross-check side: direct zero-sum (using zetazero, same as Mac would)
def K_entry_zeroside(a_j, a_k, n_zeros=30):
    total = mp.mpf(0)
    for n in range(1, n_zeros+1):
        rho = mp.mpf('0.5') + 1j*mp.zetazero(n).imag
        total += 2*mp.re(phihat(a_j,rho)*phihat(a_k,1-rho))
    return total

if __name__ == '__main__':
    # Small basis: 3 dilated Gaussians at different log-scales
    A = [mp.mpf('1.0'), mp.mpf('2.0'), mp.mpf('0.5')]
    N = len(A)
    print("Building K_N via Burnol prime+archimedean split (disjoint from zero-side)...")
    K_burnol = [[None]*N for _ in range(N)]
    for j in range(N):
        for k in range(N):
            t0=time.time()
            K_burnol[j][k] = K_entry_burnol(A[j], A[k])
            print(f"  K[{j}][{k}] (a_j={A[j]}, a_k={A[k]}) = {K_burnol[j][k]}  [{time.time()-t0:.1f}s]", flush=True)

    print("\nCross-checking against direct zero-side sum...")
    for j in range(N):
        for k in range(N):
            zs = K_entry_zeroside(A[j], A[k])
            diff = K_burnol[j][k]-zs
            print(f"  K[{j}][{k}]: burnol={K_burnol[j][k]}  zeroside={zs}  diff={diff}")

    # eigenvalues of the (should-be-symmetric-ish) matrix
    Kmat = mp.matrix(N,N)
    for j in range(N):
        for k in range(N):
            Kmat[j,k] = mp.re(K_burnol[j][k])
    print("\nK_N matrix:")
    print(Kmat)
    E = mp.eigsy(Kmat, eigvals_only=True) if False else None
