from mpmath import mp
mp.dps=120
A=mp.mpf("2.645521411811664489"); B=mp.mpf("-7.4624528767937415788")
RUN=[("0.001","0.05150723818940063653522997"),("0.0011239031932557","0.05461458474016286082927124"),
("0.002","0.07294509283746563691152741"),("0.0035","0.09670183421043065840984313"),
("0.006","0.1270603431867589315365682"),("0.0082667603361","0.149621445957808028913411"),
("0.012","0.1812222345972055203851323"),("0.02","0.236627035028954718936398"),
("0.035","0.3197940308419042261822956"),("0.06","0.434057465263706265691976"),
("0.1","0.5942792183051371124814878")]
E=[mp.mpf(x) for x,_ in RUN]; U=[mp.mpf(y) for _,y in RUN]
R=[(u**2-A*e+B*e**2)/e**3 for e,u in zip(E,U)]
def fitc(E,R,K):
    n=K+1;M=mp.matrix(n,n);rhs=mp.matrix(n,1)
    for i in range(n):
        for j in range(n): M[i,j]=sum(x**(i+j) for x in E)
        rhs[i]=sum(y*x**i for x,y in zip(E,R))
    c=mp.lu_solve(M,rhs); return [c[k] for k in range(n)]
def ev(c,x): return sum(c[k]*x**k for k in range(len(c)))
print("per-point LOO |prediction error| (row 0 = eps 0.001 smallest, row 10 = eps 0.1 largest)")
print("%-4s %-11s %-11s %-11s %-11s"%("i","K=5","K=6","K=7","K=8"))
tab={K:[] for K in (5,6,7,8)}
for i in range(11):
    Ei=[x for j,x in enumerate(E) if j!=i]; Ri=[y for j,y in enumerate(R) if j!=i]
    row=[]
    for K in (5,6,7,8):
        c=fitc(Ei,Ri,K); e=abs(R[i]-ev(c,E[i])); tab[K].append(e); row.append(mp.nstr(e,3))
    print("%-4d %-11s %-11s %-11s %-11s"%(i,*row))
print()
print("INTERIOR-ONLY LOO (drop i=0 and i=10, the design endpoints):")
for K in (5,6,7,8):
    inner=tab[K][1:10]
    rms=mp.sqrt(sum(t**2 for t in inner)/len(inner))
    print("  K=%d  interior LOO max %-11s rms %-11s"%(K,mp.nstr(max(inner),3),mp.nstr(rms,3)))
