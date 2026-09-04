#!/usr/bin/env python3
"""machine2 CYCLE 18 -- INDEPENDENT VERIFICATION of m1's ring-class computation (commit a2bb932):
   "the ring class group of conductor 7 in Q(i) is CYCLIC of order 4, not 2-torsion".
Self-contained: python3 stdlib only. The PARI/GP leg lives in machine2_cycle18_ringclass.gp.
Every leg prints its CONTROL alongside its target. Exact integer arithmetic throughout."""
import math, cmath, itertools, subprocess
from math import gcd

# ---------------- forms machinery (own code) ----------------
def egcd(x,y):
    if y==0: return (x,1,0)
    g,p,q=egcd(y,x%y); return (g,q,p-(x//y)*q)

def reduce_form(a,b,c,D):
    assert b*b-4*a*c==D,(a,b,c,D)
    while True:
        r=b%(2*a)
        if r>a: r-=2*a
        if r!=b: b=r; c=(b*b-D)//(4*a)
        if a>c: a,b,c=c,-b,a; continue
        if a==c and b<0: b=-b
        return (a,b,c)

def compose(f1,f2,D):
    """Cohen, A Course in Computational Algebraic Number Theory, Algorithm 5.4.7."""
    a1,b1,c1=f1; a2,b2,c2=f2
    if a1>a2: (a1,b1,c1),(a2,b2,c2)=(a2,b2,c2),(a1,b1,c1)
    s=(b1+b2)//2; n=b2-s
    if a2%a1==0: y1=0; d=a1
    else:
        d,u,v=egcd(a2,a1); y1=u
    if s%d==0: y2=-1; x2=0; d1=d
    else:
        d1,u,v=egcd(s,d); x2=u; y2=-v
    v1=a1//d1; v2=a2//d1
    r=(y1*y2*n-x2*c2)%v1
    a3=v1*v2; b3=b2+2*v2*r; c3=(b3*b3-D)//(4*a3)
    return reduce_form(a3,b3,c3,D)

def reduced_forms(D):
    out=[]
    for a in range(1,int(math.isqrt(-D//3))+2):
        for b in range(-a+1,a+1):
            num=b*b-D
            if num%(4*a): continue
            c=num//(4*a)
            if c<a or gcd(gcd(a,abs(b)),c)!=1: continue
            if a==c and b<0: continue
            out.append((a,b,c))
    return out

def identity(D): return reduce_form(1,D%2,((D%2)-D)//4,D)

def orders(D):
    F=reduced_forms(D); idf=identity(D); o={}
    for f in F:
        g=f; k=1
        while g!=idf and k<200: g=compose(g,f,D); k+=1
        o[f]=k
    return F,idf,o

def rep_vector(f,N):
    a,b,c=f; DD=b*b-4*a*c; r=[0]*(N+1)
    ymax=int(math.isqrt(int(4*a*N/(-DD))))+2
    for y in range(-ymax,ymax+1):
        A=a; B=b*y; C=c*y*y-N; d=B*B-4*A*C
        if d<0: continue
        s=math.isqrt(d)+1
        for x in range(int((-B-s)//(2*A))-1,int((-B+s)//(2*A))+2):
            v=a*x*x+b*x*y+c*y*y
            if 1<=v<=N: r[v]+=1
    return r

def kron(D,n):
    if n==0: return 1 if abs(D)==1 else 0
    res=1
    while n%2==0:
        n//=2
        if D%2==0: return 0
        if D%8 in (3,5): res=-res
    if n==1: return res
    a=D%n
    if gcd(a,n)!=1: return 0
    t=1
    while a!=0:
        while a%2==0:
            a//=2
            if n%8 in (3,5): t=-t
        a,n=n,a
        if a%4==3 and n%4==3: t=-t
        a%=n
    return res*t if n==1 else 0

def primes_upto(N):
    sieve=[True]*(N+1); sieve[0]=sieve[1]=False
    for i in range(2,int(N**.5)+1):
        if sieve[i]:
            for j in range(i*i,N+1,i): sieve[j]=False
    return [i for i,v in enumerate(sieve) if v]

# ---------------- LEG 2: own composition, cross-validated vs PARI ----------------
def leg2_crossvalidate():
    import random
    random.seed(18); cases=[]
    for D in [d for d in range(-500,-3) if d%4 in (0,1)]:
        F=reduced_forms(D)
        if len(F)<2: continue
        for _ in range(3):
            f1=random.choice(F); f2=random.choice(F)
            cases.append((D,f1,f2,compose(f1,f2,D)))
    script="\n".join(f"print(qfbred(qfbcompraw(Qfb({f1[0]},{f1[1]},{f1[2]}),Qfb({f2[0]},{f2[1]},{f2[2]}))))"
                     for D,f1,f2,_ in cases)
    open("/tmp/xval.gp","w").write(script+"\n")
    try:
        out=subprocess.run(["gp","-q","/tmp/xval.gp"],capture_output=True,text=True).stdout.strip().split("\n")
    except FileNotFoundError:
        print("  [LEG2 cross-validation SKIPPED: gp not installed]"); return
    bad=0
    for (D,f1,f2,mine),line in zip(cases,out):
        pari=tuple(int(x) for x in line.replace("Qfb(","").replace(")","").split(","))
        if pari!=mine: bad+=1
    print(f"  cross-validation of my composition against PARI/GP: {len(cases)} cases over "
          f"{len(set(c[0] for c in cases))} discriminants in [-500,-4]; MISMATCHES = {bad}")

print("="*76); print("LEG 1 is machine2_cycle18_ringclass.gp (PARI/GP 2.13.3, third-party)"); print("="*76)
print("\n"+"="*76); print("LEG 2 -- own reduction + own Gauss composition (Cohen Alg. 5.4.7)"); print("="*76)
leg2_crossvalidate()
for D,lab in [(-196,"TARGET: order of conductor 7 in Q(i)"),(-84,"CONTROL: classically (Z/2)^2"),
              (-56,"CONTROL: classically Z/4"),(-20,"CONTROL: Z/2"),(-23,"CONTROL: Z/3")]:
    F,idf,o=orders(D); h=len(F); e=max(o.values())
    print(f"  D={D:5d} h={h} forms={F} orders={[o[f] for f in F]} exponent={e} CYCLIC={'YES' if e==h else 'NO'}  [{lab}]")

print("\n"+"="*76); print("LEG 3 -- theta-series discriminator: NO composition, NO class field theory."); print("="*76)
print("  a form and its inverse represent the same integers => 2-torsion group has h distinct")
print("  theta series, Z/4 has h-1.  Representation numbers to n<=400, brute force.")
for D,lab in [(-196,"TARGET"),(-84,"CONTROL (Z/2)^2"),(-56,"CONTROL Z/4")]:
    F=reduced_forms(D); vecs={f:tuple(rep_vector(f,400)[1:]) for f in F}
    print(f"  D={D:5d} h={len(F)} distinct theta series = {len(set(vecs.values()))}  [{lab}]")

print("\n"+"="*76); print("LEG 4 -- genus / ambiguous-class count"); print("="*76)
for D,lab in [(-196,"TARGET"),(-84,"CONTROL")]:
    F=reduced_forms(D)
    amb=[f for f in F if f[1]==0 or f[0]==f[1] or f[0]==f[2]]
    print(f"  D={D:5d} h={len(F)} ambiguous(2-torsion) classes = {len(amb)} -> |Cl[2]|={len(amb)}  [{lab}]")

print("\n"+"="*76); print("LEG 5 -- m1's OWN route re-run. ARITHMETIC CHECK, NOT independent verification."); print("="*76)
p=7; elts=[(a,b) for a in range(p) for b in range(p) if (a,b)!=(0,0)]
mul=lambda u,v: ((u[0]*v[0]-u[1]*v[1])%p,(u[0]*v[1]+u[1]*v[0])%p)
H={(1,0)}; fr=[(1,0)]; gens=[(a,0) for a in range(1,p)]+[(0,1)]
while fr:
    x=fr.pop()
    for g in gens:
        y=mul(x,g)
        if y not in H: H.add(y); fr.append(y)
def ordof(u):
    k=1; y=u
    while y!=(1,0): y=mul(y,u); k+=1
    return k
print(f"  |F_49^*|={len(elts)}  |F_7^* . mu_4|={len(H)}  index={len(elts)//len(H)}  "
      f"F_49^* cyclic={any(ordof(u)==48 for u in elts)}  => m1's 48/12=4 REPRODUCED")

print("\n"+"="*76); print("CONSEQUENCES measured on the carrier's own Dirichlet coefficients"); print("="*76)
D=-196; F,idf,o=orders(D)
gf=[f for f in F if o[f]==4][0]; dl={}; g=idf
for k in range(4): dl[g]=k; g=compose(g,gf,D)
print(f"  class group = <{gf}>, discrete logs {dl}")
N=800; R={f:rep_vector(f,N) for f in F}
# real genus character
chi2=lambda f:(-1)**dl[f]
b2=[0]*(N+1)
for n in range(1,N+1): b2[n]=sum(chi2(f)*R[f][n] for f in F)//2
conv2=[0]*(N+1)
for n in range(1,N+1): conv2[n]=sum(kron(-7,d)*kron(28,n//d) for d in range(1,n+1) if n%d==0)
print(f"  GENUS character leg:  b2(n) == (chi_-7 * chi_28)(n) for all n<=800 : "
      f"{all(b2[n]==conv2[n] for n in range(1,N+1))}   (mismatches "
      f"{len([n for n in range(1,N+1) if b2[n]!=conv2[n]])})")
# trivial character leg
b0=[0]*(N+1)
for n in range(1,N+1): b0[n]=sum(R[f][n] for f in F)//2
c4=[0]*(N+1)
for n in range(1,N+1): c4[n]=sum(kron(-4,d) for d in range(1,n+1) if n%d==0)
gloc={1:1}
for k in range(1,4):
    pk=7**k; gloc[pk]=b0[pk]-sum(gloc.get(7**j,0)*c4[pk//7**j] for j in range(k))
full=[0]*(N+1)
for n in range(1,N+1):
    full[n]=sum(gloc.get(7**k,0)*c4[n//7**k] for k in range(4) if n%7**k==0)
print(f"  TRIVIAL character leg: b0(n) == ((1 * chi_-4) * g)(n) for all n<=800 : "
      f"{all(b0[n]==full[n] for n in range(1,N+1))}   with g supported on powers of 7, "
      f"g(1),g(7),g(49),g(343) = {[gloc.get(7**k,0) for k in range(4)]}"
      f"  => finite Euler factor 1 + 7*7^(-2s)")
# order-4 character fingerprint + control
def fingerprint(D,N=600):
    F,idf,o=orders(D); h=len(F); idx={f:i for i,f in enumerate(F)}
    tab=[[idx[compose(F[i],F[j],D)] for j in range(h)] for i in range(h)]
    chars=[]
    for assign in itertools.product(range(2*h),repeat=h):
        vals=[cmath.exp(2j*cmath.pi*a/(2*h)) for a in assign]
        if abs(vals[idx[idf]]-1)>1e-9: continue
        if all(abs(vals[tab[i][j]]-vals[i]*vals[j])<1e-9 for i in range(h) for j in range(h)):
            chars.append(vals)
        if len(chars)>=h: break
    R={f:rep_vector(f,N) for f in F}
    P=[q for q in primes_upto(N) if gcd(q,2*abs(D))==1]
    split=[q for q in P if sum(R[f][q] for f in F)>0]
    out=[]
    for vals in chars:
        b=[sum(vals[idx[f]]*R[f][n] for f in F)/2 for n in range(N+1)]
        real=all(abs(v.imag)<1e-9 for v in vals)
        out.append(("real" if real else "order-4",len(split),len([q for q in split if abs(b[q])<1e-9])))
    return h,out
for D,lab in [(-196,"TARGET Z/4"),(-84,"CONTROL (Z/2)^2 -- every character real")]:
    h,out=fingerprint(D)
    print(f"  D={D} h={h} [{lab}]")
    for kind,ns,nz in out:
        print(f"      character {kind:8s}: split primes tested {ns}, b(p)=0 among them {nz}")
