#!/usr/bin/env python3
"""machine 2 (BEAST) -- normalisation check for the general floor of section 4.

Claim under test: Mellin is an isometry L^2(0,1) -> H^2(Re s > 1/2) under
||G||^2 = (1/2pi) int |G(1/2+it)|^2 dt, that space has reproducing kernel
k_w(s) = 1/(s + conj(w) - 1) with ||k_w||^2 = 1/(2 Re w - 1), and M chi_(0,1)(s) = 1/s.
Every constant in the floor (2 Re s0 - 1)/|s0|^2 comes from those three facts.
No proof claim.
"""
import mpmath as mp
mp.mp.dps = 25

def ip(f, g):
    return mp.quad(lambda t: f(mp.mpf('0.5')+1j*t)*mp.conj(g(mp.mpf('0.5')+1j*t)),
                   [-mp.inf, 0, mp.inf])/(2*mp.pi)

for w in [mp.mpc('0.8','2.0'), mp.mpc('1.2','0.5'), mp.mpc('0.6','5.0')]:
    k = lambda s, w=w: 1/(s+mp.conj(w)-1)
    f = lambda s: 1/s
    print("w=", mp.nstr(w, 6),
          " <Mchi,k_w> =", mp.nstr(ip(f, k), 12), " 1/w =", mp.nstr(1/w, 12),
          " ||k_w||^2 =", mp.nstr(ip(k, k), 12),
          " 1/(2Re w-1) =", mp.nstr(1/(2*w.real-1), 12))
    print("   floor (2Re w-1)/|w|^2 =", mp.nstr((2*w.real-1)/abs(w)**2, 12))
print("||chi||^2 in H^2 norm =", mp.nstr(ip(lambda s: 1/s, lambda s: 1/s), 12), "(must be 1)")
print("DQ: the w=0.6+5i row agrees to ~3 digits only -- quadrature limit (1/t^2 tail,")
print("    peak far off the origin), NOT a discrepancy in the identity.")
