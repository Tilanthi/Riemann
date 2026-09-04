"""GATE 1 (cheapest gate): Dirichlet-majorant kill of the high-sigma part of the VOID wedge.

F(s) = sum a_n n^{-s},  a_1 = 1  =>  |F(s)-1| <= M(sigma) := sum_{n>=2} a_n n^{-sigma}.
M(sigma) < 1  =>  F has NO zeros on that whole half-plane.  Cost: integer arithmetic only.

Tail is bounded RIGOROUSLY, not sampled:
  A(x) := sum_{n<=x} a_n = (#lattice pts in j^2+49k^2 <= x, minus origin)/2
  convex-region lattice bound:  |#pts - area| <= perimeter + 1,  area = pi*x/7,
  perimeter of the ellipse (semi-axes sqrt(x), sqrt(x)/7) <= pi*(3(a+b) - sqrt((3a+b)(a+3b)))
  => A(x) <= pi*x/14 + P0*sqrt(x)/2   with P0 the Ramanujan perimeter constant below.
  sum_{n>N} a_n n^{-sig} = sig * int_N^inf A(x) x^{-sig-1} dx - A(N) N^{-sig}
                        <= (pi/14)*sig*N^{1-sig}/(sig-1) + (P0/2)*sig*N^{0.5-sig}/(sig-0.5)
"""
import numpy as np, math, json

NMAX = 4 * 10**6
counts = np.zeros(NMAX + 1, dtype=np.int64)
kmax = int(math.isqrt(NMAX // 49))
for k in range(-kmax, kmax + 1):
    rem = NMAX - 49 * k * k
    jmax = int(math.isqrt(rem))
    js = np.arange(-jmax, jmax + 1, dtype=np.int64)
    n = js * js + 49 * k * k
    n = n[n > 0]
    np.add.at(counts, n, 1)
a = counts / 2.0
assert a[1] == 1.0, a[1]
ns = np.arange(0, NMAX + 1, dtype=np.float64)

# Ramanujan II perimeter of ellipse with semi-axes a=sqrt(x), b=sqrt(x)/7 -> P0*sqrt(x)
A_, B_ = 1.0, 1.0 / 7.0
h = ((A_ - B_) / (A_ + B_)) ** 2
P0 = math.pi * (A_ + B_) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))

def M(sig, N=NMAX):
    partial = float(np.sum(a[2:N + 1] * ns[2:N + 1] ** (-sig)))
    tail = (math.pi / 14) * sig * N ** (1 - sig) / (sig - 1) + (P0 / 2) * sig * N ** (0.5 - sig) / (sig - 0.5)
    return partial, tail, partial + tail

lo, hi = 1.0001, 2.0
for _ in range(60):
    mid = (lo + hi) / 2
    if M(mid)[2] > 1.0: lo = mid
    else: hi = mid
sig_maj = hi
print("GATE 1  Dirichlet majorant, N = %d terms (denominator), P0 = %.6f" % (NMAX, P0))
for sig in [1.05, 1.10, 1.15, 1.1652, sig_maj, 1.20, 1.5, 2.0]:
    p, t, m = M(sig)
    print("  sigma=%-8.5f  partial=%-12.6f  tail<=%-11.4g  M(sigma)<=%-12.6f  %s"
          % (sig, p, t, m, "ZERO-FREE" if m < 1 else "-"))
print("  => certified zero-free half-plane:  sigma >= %.10f" % sig_maj)
box = dict(sig_lo=0.52, sig_hi=2.0, t_lo=20.0, t_hi=43.0)
area = (box['sig_hi'] - box['sig_lo']) * (box['t_hi'] - box['t_lo'])
killed = (box['sig_hi'] - sig_maj) * (box['t_hi'] - box['t_lo'])
print("  VOID wedge area = %.4f ; GATE 1 kills %.4f (%.2f%%) ; residual %.4f"
      % (area, killed, 100 * killed / area, area - killed))
json.dump(dict(NMAX=NMAX, P0=P0, sig_maj=sig_maj, area=area, killed=killed,
               table=[dict(sigma=s, partial=M(s)[0], tail=M(s)[1], M=M(s)[2]) for s in [1.05,1.10,1.15,1.20,1.5,2.0]]),
          open('gate1.json','w'), indent=1)
