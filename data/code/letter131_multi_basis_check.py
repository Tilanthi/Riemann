import sys, time
sys.path.insert(0,'/tmp')
from scalar_identity_check import load_genome, u_of_s, prime_side_scalar, zero_side_scalar, arch_side_scalar

fns = load_genome('s1/M8', 8)
for idx in [0, 1, 2, 3]:
    f = fns[idx]
    print(f'--- basis {idx} --- supp: {f.supp_lo:.3f},{f.supp_hi:.3f}  phi(0)={f.phi(0):.6f}', flush=True)
    t0=time.time()
    u1 = u_of_s(f, 1.0+0j)
    endpoint = u1.real
    prime, nterms = prime_side_scalar(f)
    zero, nz = zero_side_scalar(f, T=150)
    arch = arch_side_scalar(f, t_max=100)
    rhs = endpoint - prime + arch
    gap = rhs - zero
    print(f'  Endpoint={endpoint:.6f} Prime={prime:.6f} Arch={arch} Zero(T150,{nz}zeros)={zero:.6f}', flush=True)
    print(f'  RHS={rhs}  gap=RHS-Zero={gap}  gap/phi0={gap/f.phi(0) if f.phi(0)!=0 else float("nan")}  [{time.time()-t0:.1f}s]', flush=True)
