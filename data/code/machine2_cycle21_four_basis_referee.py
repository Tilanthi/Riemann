"""Referee R part 3 (rewritten for cost): m3's four bases (their genome), MY OWN quadrature
(fixed Gauss-Legendre panels, vectorised numpy -- no scipy.quad, no mpmath.quad), MY OWN kernel.
Scores m1's L132 sect1.3 Arch targets and m3's L131 table."""
import sys, json, numpy as np
sys.path.insert(0, '/shared/rh-exchange-repo/Riemann/data/code')
from scipy import special
import mpmath as mp
from identity_check_fast import TestFn

G = json.load(open('/shared/rh-exchange-repo/Riemann/data/code/machine1_heat70_genomes_m8_m64.json'))
BASES = G['genomes']['s1/M8']

def gl_panels(lo, hi, npan, nnode=24):
    x, w = np.polynomial.legendre.leggauss(nnode)
    edges = np.linspace(lo, hi, npan + 1)
    X = np.concatenate([(e1 - e0) / 2 * x + (e0 + e1) / 2 for e0, e1 in zip(edges[:-1], edges[1:])])
    W = np.concatenate([(e1 - e0) / 2 * w for e0, e1 in zip(edges[:-1], edges[1:])])
    return X, W

def K_sum(s):  return 0.5*special.digamma(s/2) + 0.5*special.digamma((1-s)/2) - np.log(np.pi)
def K_diff(s): return 0.5*special.digamma(s/2) - 0.5*special.digamma((1-s)/2)

def legs(fi, tmax=150.0, T=300.0):
    X, W = gl_panels(fi.supp_lo, fi.supp_hi, 400, 24)      # 9600 x-nodes
    P = np.array([fi.phi(x) for x in X])
    U1 = float(np.sum(W * P * np.exp(X)))                   # u(1)
    # prime side
    hi = max(abs(fi.supp_lo), abs(fi.supp_hi)); N = int(np.exp(hi)) + 10
    sieve = np.ones(N+1, bool); sieve[:2] = False
    for p in range(2, int(N**0.5)+1):
        if sieve[p]: sieve[p*p::p] = False
    tot = 0.0; nt = 0
    for p in np.nonzero(sieve)[0]:
        lp = np.log(p); q = int(p)
        while np.log(q) <= hi + 1e-12:
            a = fi.phi(np.log(q)); b = fi.phi(-np.log(q))
            if a or b: tot += lp*(a + b/q); nt += 1
            q *= int(p)
    Prime = tot
    # zero side
    g = np.array([float(mp.im(mp.zetazero(k))) for k in range(1, 200)])
    g = g[g <= T]
    Ez = np.exp(np.outer(g, X)*1j)                          # e^{i gamma x}
    base = W * P * np.exp(0.5*X)
    Z = float(np.sum(2*np.real(Ez @ base)))
    # arch, my own panels
    Tt, Wt = gl_panels(-tmax, tmax, 1200, 16)               # 19200 t-nodes
    Et = np.exp(np.outer(Tt, X)*1j)
    baseM = W * P * np.exp(-0.5*X)
    U = Et @ baseM                                          # u(-1/2+it)
    s = -0.5 + 1j*Tt
    A_ok  = float(np.sum(Wt*np.real(K_sum(s)*U)))/(2*np.pi)
    A_bad = float(np.sum(Wt*np.real(K_diff(s)*U)))/(2*np.pi)
    A_rr  = float(np.sum(Wt*np.real(K_sum(s))*np.real(U)))/(2*np.pi)
    return U1, Prime, Z, A_ok, A_bad, A_rr, len(g), nt

M1T = {0:0.102851814149, 1:-0.559823222, 2:-0.028490956, 3:0.321824777}
M3  = {0:(-32.1155,-32.4668,-0.2553), 1:(3.2370,2.6307,-0.6479),
       2:(9.6793,9.6484,-0.0292), 3:(0.1979,0.5003,-0.2683)}
print("basis | u(1)          Prime         Zero(T300)    Arch_mine    target=P-u1+Z   closure   "
      "| m1 L132 target  dev | Arch(m3 DIFF kernel)  m3 printed | Arch(Re*Re)")
for bi in range(4):
    fi = TestFn(BASES[bi])
    U1, P, Z, Aok, Abad, Arr, nz, nt = legs(fi)
    tgt = P - U1 + Z
    e3, p3, a3 = M3[bi]
    print("%d | %13.7f %13.7f %13.8f %12.8f %13.8f  %9.2e | %13.9f %8.1e | %12.7f  %8.4f | %10.6f"
          % (bi, U1, P, Z, Aok, tgt, abs(Aok-tgt), M1T[bi], abs(M1T[bi]-tgt), Abad, a3, Arr))
    print("     [m3 L131 printed End %8.4f Prime %8.4f ; my u(1) dev %.1e, my Prime dev %.1e ; "
          "%d zeros, %d prime terms]" % (e3, p3, abs(U1-e3), abs(P-p3), nz, nt))
