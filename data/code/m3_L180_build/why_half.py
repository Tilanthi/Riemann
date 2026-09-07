"""
m3-L180 build: why-1/2 lane. Read-only against Mac's frozen heat78c construction (imported for its
helper definitions ONLY -- module-level function/class definitions, main() never called, nothing
executed, nothing re-run, nothing written). Own data loading (own hash check), own derivative
extension (U', U''), own perturbation-theory assembly, own validation gate before trusting anything.
"""
import sys, os, hashlib, json, importlib.util
sys.path.insert(0, '.')
from mpmath import mp, mpf, mpc, exp, quad, zetazero, re as mpre, im as mpim, conj, fabs

mp.dps = 45  # match the frozen construction's working precision exactly

HEREDIR = os.path.dirname(os.path.abspath(__file__))
FROZEN_SCRIPT = os.path.join(HEREDIR, '..', 'machine1_heat78c_survivor_census.py')
GEN = os.path.join(HEREDIR, '..', 'machine1_heat70_genomes_m8_m64.json')
IDT = os.path.join(HEREDIR, '..', '..', 'machine1_heat72k_identity_target_m8.json')
K64 = os.path.join(HEREDIR, '..', '..', 'machine1_heat78a_m64_kernel.json')
CENSUS_JSON = os.path.join(HEREDIR, '..', '..', 'heat78c_census_result.json')

EXPECTED_HASHES = {
    GEN: "1065fd370fd9370807ea61f19708cbf1d16be77179f279760864386d299da56b",
    IDT: "12b81d093a0eb9d76709a61a9e22015af81a646e18faab722443efc0b03f87ff",
    K64: "f992234913440a6af50cccf6016af260afc0be0fdcac417500d94b47331e3c51",
}


def verify_seals():
    for path, want in EXPECTED_HASHES.items():
        h = hashlib.sha256(open(path, 'rb').read()).hexdigest()
        status = "OK" if h == want else "MISMATCH"
        print(f"  seal {os.path.basename(path)}: {status}", flush=True)
        if h != want:
            raise SystemExit(f"SEAL MISMATCH on {path}: got {h} want {want}")


# --- import Mac's frozen module for its DEFINITIONS ONLY (main() is guarded, never called) ---
spec = importlib.util.spec_from_file_location('heat78c_frozen', FROZEN_SCRIPT)
heat78c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(heat78c)  # loads defs only; the file's main() sits behind `if __name__=='__main__'`
make_phi = heat78c.make_phi
HALF = heat78c.HALF
THRESH = heat78c.THRESH


class InstrumentExt:
    """Own class: reproduces gram/quad_ex/eig from the frozen definitions (re-typed here, checked
    against the sealed output below), PLUS the new U'/U'' derivative extension for the perturbation
    calculation -- the part that does not exist in the frozen script at all."""

    def __init__(self, M, K, G, phis, edges):
        self.M, self.K, self.G, self.phis, self.edges = M, K, G, phis, edges
        self.Uc, self.Uc1, self.Uc2 = {}, {}, {}

    def U(self, i, s):
        key = str(s)
        if (i, key) not in self.Uc:
            self.Uc[(i, key)] = quad(lambda t: self.phis[i](t) * exp(s * t), self.edges[i])
        return self.Uc[(i, key)]

    def U1(self, i, s):
        """dU_i/ds(s) = INT t*phi_i(t)*e^{st} dt."""
        key = str(s)
        if (i, key) not in self.Uc1:
            self.Uc1[(i, key)] = quad(lambda t: t * self.phis[i](t) * exp(s * t), self.edges[i])
        return self.Uc1[(i, key)]

    def U2(self, i, s):
        """d^2U_i/ds^2(s) = INT t^2*phi_i(t)*e^{st} dt."""
        key = str(s)
        if (i, key) not in self.Uc2:
            self.Uc2[(i, key)] = quad(lambda t: t * t * self.phis[i](t) * exp(s * t), self.edges[i])
        return self.Uc2[(i, key)]

    def gram(self, g0):
        uv = [self.U(i, mpc(HALF, g0)) for i in range(self.M)]
        Mx = mp.matrix(self.M, self.M)
        for i in range(self.M):
            for j in range(self.M):
                Mx[i, j] = 2 * mpre(uv[i] * conj(uv[j]))
        return Mx

    def quad_ex(self, g0, d):
        p, q = mpc(HALF + d, g0), mpc(HALF - d, g0)
        up = [self.U(i, p) for i in range(self.M)]
        uq = [self.U(i, q) for i in range(self.M)]
        Mx = mp.matrix(self.M, self.M)
        for i in range(self.M):
            for j in range(self.M):
                Mx[i, j] = 2 * mpre(up[i] * conj(uq[j]) + up[j] * conj(uq[i]))
        return Mx

    def A2_hessian(self, g0):
        """d^2 quad_ex / d(delta)^2 at delta=0, via the closed-form derivative formula
        (derivation_notes.md Step 2), NOT via finite differences -- this is the object under test."""
        s0 = mpc(HALF, g0)
        u0 = [self.U(i, s0) for i in range(self.M)]
        u1 = [self.U1(i, s0) for i in range(self.M)]
        u2 = [self.U2(i, s0) for i in range(self.M)]
        Mx = mp.matrix(self.M, self.M)
        for i in range(self.M):
            for j in range(self.M):
                Mx[i, j] = (4 * mpre(u2[i] * conj(u0[j])) + 4 * mpre(u0[i] * conj(u2[j]))
                            - 8 * mpre(u1[i] * conj(u1[j])))
        return Mx

    def eig(self, F):
        Gm = self.G
        L = mp.cholesky(Gm)
        Li = mp.inverse(L)
        B = Li * F * Li.T
        B = (B + B.T) / 2
        E, V = mp.eigsy(B)
        idx = sorted(range(self.M), key=lambda i: E[i])
        vals = [E[i] for i in idx]
        # un-whitened, G-normalized eigenvectors: v = L^-T w  (w orthonormal in eigsy's output)
        vecs = [Li.T * mp.matrix([V[r, i] for r in range(self.M)]) for i in idx]
        return vals, vecs


def build_instruments():
    verify_seals()
    gdata = json.load(open(GEN))["genomes"]
    idt = json.load(open(IDT))["seeds"]["s1/M8"]
    k64 = json.load(open(K64))

    insts = {}
    for M, (src, ph) in ((8, (idt, "s1/M8")), (64, (k64, "s1/M64"))):
        genomes = gdata[ph]
        phis, edges = zip(*[make_phi(g) for g in genomes])
        K = mp.matrix(M, M)
        G = mp.matrix(M, M)
        for i in range(M):
            for j in range(M):
                K[i, j] = mpf(src["K_T200"][i][j])
                G[i, j] = mpf(src["G_raw"][i][j])
        insts[M] = InstrumentExt(M, K, G, phis, edges)
    return insts


def get_zeros(n=26):
    return [mpf(str(mpim(zetazero(k)))) for k in range(1, n + 1)]


def g_of(zeros, k, phi8):
    return zeros[k] + (zeros[k + 1] - zeros[k]) * mpf(phi8) / 8
