# m3-L177 build — my own derivation notes (before any code)

Basis on t in [-L/2, L/2], zero elsewhere: phi_0 = 1/sqrt(L), phi_k = sqrt(2/L) cos(w_k t), w_k = 2*pi*k/L, k=1..N.

## 1. Single-function Fourier/Mellin transform phihat_k(r) = INT phi_k(t) e^{i r t} dt

Standard finite-cosine-transform calculation (product-to-sum + evaluate at endpoints +-L/2), using
w_k*L/2 = pi*k so sin(w_k L/2) = sin(pi k) = 0 and cos(w_k L/2) = cos(pi k) = (-1)^k:

  phihat_0(r) = 2 sin(rL/2) / (r sqrt(L))
  phihat_k(r) = sqrt(2/L) * (-1)^k * sin(rL/2) * 2r / (r^2 - w_k^2),   k >= 1

Apparent poles at r = +-w_k cancel against sin(rL/2)=0 there (removable) -- phihat_k is entire, as
expected for the FT of a compactly supported function. This matches the SHAPE of BEAST's own quoted
G(r) = 2 c_0/r + sum c_k 2r/(r^2-w_k^2), c_k = nr_k v_k (-1)^k for the OPTIMAL eigenvector combination
-- consistent, but derived here independently from the basis definition, not copied.

phihat_k is EVEN in r (as an entire function, even on the real line by direct check, hence even
everywhere by the identity theorem) -- phihat_k(-r) = phihat_k(r) for all complex r, in particular
phihat_k(-i/2) = phihat_k(i/2).

## 2. Basis correlation g_jk(t) = INT phi_j(s) phi_k(s+t) ds, t in [0, L)

KEY FACT (used throughout, checked explicitly, not assumed): since BOTH phi_j and phi_k are EVEN
functions (cos and the constant are both even), g_jk(t) is EVEN in t for every (j,k) pair, including
j != k -- this is NOT true for a generic cross-correlation of two arbitrary real functions (only
autocorrelations of a single function are always even in general); it holds here specifically because
the basis elements themselves are even. Proof: g_jk(-t) = INT phi_j(s) phi_k(s-t) ds; substitute
s -> -s (using dt->-dt cancelling the limit flip on the whole-line integral) and phi_j(-s)=phi_j(s),
phi_k(-(s+t))=phi_k(s+t): g_jk(-t) = INT phi_j(-u) phi_k(-u-t) du = INT phi_j(u) phi_k(u+t) du = g_jk(t).
CONSEQUENCE: g_kj(t) = g_jk(-t) [general correlation identity] = g_jk(t) [evenness just shown], so
g_jk = g_kj identically -- M is symmetric with NO extra polarisation trick needed; the one-sided
archimedean rewrite (which assumes an even g) applies DIRECTLY to every g_jk, not just the diagonal.

Derivation by cases (integration range s in [-L/2, L/2-t] for t in [0,L)):

  g_00(t) = 1 - t/L                                                        [rectangle autocorrelation]

  g_0k(t) = g_k0(t) = sqrt(2) * (-1)^{k+1} * sin(w_k t) / (L w_k),  k >= 1

  g_kk(t) = (1/L) * [ cos(w_k t) (L - t)  -  sin(w_k t)/w_k ],  k >= 1

  g_jk(t), j != k, both >= 1, A = w_j - w_k, B = w_j + w_k:
    g_jk(t) = ((-1)^{j+k}/L) * { [sin(w_k t) - sin(w_j t)] / A  -  [sin(w_j t) + sin(w_k t)] / B }

All four cases checked at t=0: g_00(0)=1, g_0k(0)=0, g_kk(0)=1, g_jk(0)=0 (j!=k) -- matches
orthonormality of the basis exactly (g_jk(0) = delta_jk), an EXACT identity, not a numerical
coincidence, since {phi_k} is by construction the standard orthonormal Fourier-cosine basis on the
interval. Used as a free consistency check on the closed form and later, at zero extra cost, as the
exact value entering the pole/archimedean diagonal terms.

## 3. Assembling M_jk = W(g_jk)

pole_jk      = h_jk(i/2) + h_jk(-i/2) - g_jk(0) log(pi),  h_jk(r) := phihat_j(r) phihat_k(r)
             = 2 phihat_j(i/2) phihat_k(i/2) - delta_jk log(pi)
               [using phihat_k(-i/2)=phihat_k(i/2), evenness; and h_jk(r)=phihat_j(r)phihat_k(r) is
                itself a short derivation: FT of a correlation is the product of one FT and the
                CONJUGATE-reflected other FT, which for even real phi_j collapses to a plain product]

arch_jk      = -gammaE * delta_jk
               + 2 * INT_0^infinity [ e^{-2t} delta_jk  -  e^{-t/2} g_jk(t) ] / (1 - e^{-2t}) dt
               [g_jk(t)=0 for t>=L by construction; near t=0 the bracket->0 (removable sing. at t=0,
                confirmed analytically: numerator ~ delta_jk*(1-t/2*...) - delta_jk*(1-t/2*...) type
                cancellation for j=k, and O(t^2) numerator for j!=k since g_jk is even with g_jk(0)=0]

prime_jk     = -2 * SUM over prime powers n <= x of  Lambda(n) * n^{-1/2} * g_jk(log n)

M_jk = pole_jk + arch_jk + prime_jk.  M is real symmetric (all three pieces manifestly symmetric in
j,k, using phihat_j(i/2) real, g_jk(0)=g_kj(0), g_jk(t)=g_kj(t) shown above).

Smallest eigenpair of M (basis already orthonormal, so this is a PLAIN symmetric eigenproblem, no
generalised/mass matrix needed) is lambda_min(x), the quantity to reproduce and then extrapolate.
