"""m2 response to m1-L164 leg 2, part C: is the K-ladder's falling residual a FLOOR statement
or a DEGREES-OF-FREEDOM statement?

11 points, K+1 free coefficients:  K=5 -> 5 dof, K=6 -> 4, K=7 -> 3, K=8 -> 2.
Our shared "no stall" claim (3.13e-10 / 1.94e-10 / 7.95e-11 at K=6/7/8) reads a falling in-sample
residual as evidence that nothing structural is left above ~1e-10.  But in-sample residual falls
when dof falls, whether or not the model is right.  Two controls that separate the two:

  LOO  leave-one-out prediction error: fit on 10, predict the held-out point.  Overfitting shows
       up as LOO error RISING while in-sample residual falls.
  JK   jackknife spread of a3 over the 11 leave-one-out fits: an error bar built from the data's
       own support for a3, rather than from the spread of a nested model family (which is blind
       to any error common to the whole family -- the defect that made my +/-5e-10 wrong).

No sealed-runner quantity appears anywhere in this file.
"""
from mpmath import mp

mp.dps = 120

A_U1 = mp.mpf("2.645521411811664489")
B_U2 = mp.mpf("-7.4624528767937415788")
A_REG = mp.mpf("2.645521411811663")
B_REG = mp.mpf("-7.46245287679")
A3_KAPPA = mp.mpf("11.700717320435114")

RUN = [("0.001", "0.05150723818940063653522997"),
       ("0.0011239031932557", "0.05461458474016286082927124"),
       ("0.002", "0.07294509283746563691152741"),
       ("0.0035", "0.09670183421043065840984313"),
       ("0.006", "0.1270603431867589315365682"),
       ("0.0082667603361", "0.149621445957808028913411"),
       ("0.012", "0.1812222345972055203851323"),
       ("0.02", "0.236627035028954718936398"),
       ("0.035", "0.3197940308419042261822956"),
       ("0.06", "0.434057465263706265691976"),
       ("0.1", "0.5942792183051371124814878")]


def rvals(a, b):
    E = [mp.mpf(x) for x, _ in RUN]
    U = [mp.mpf(y) for _, y in RUN]
    return E, [(u ** 2 - a * e + b * e ** 2) / e ** 3 for e, u in zip(E, U)]


def fitc(E, R, K):
    n = K + 1
    M = mp.matrix(n, n)
    rhs = mp.matrix(n, 1)
    for i in range(n):
        for j in range(n):
            M[i, j] = sum(x ** (i + j) for x in E)
        rhs[i] = sum(y * x ** i for x, y in zip(E, R))
    c = mp.lu_solve(M, rhs)
    return [c[k] for k in range(n)]


def ev(c, x):
    return sum(c[k] * x ** k for k in range(len(c)))


for tag, a, b in (("rung-3 constants (19/21 d)", A_U1, B_U2),
                  ("registered constants (16/12 d)", A_REG, B_REG)):
    E, R = rvals(a, b)
    print("=" * 88)
    print("  %s" % tag)
    print("=" * 88)
    print("%-3s %-5s %-12s %-12s %-12s %-22s %-11s" %
          ("K", "dof", "in-sample", "LOO max", "LOO rms", "a3 (full fit)", "a3 JK spread"))
    for K in (4, 5, 6, 7, 8):
        c = fitc(E, R, K)
        ins = max(abs(y - ev(c, x)) for x, y in zip(E, R))
        loo = []
        a3s = []
        for i in range(len(E)):
            Ei = [x for j, x in enumerate(E) if j != i]
            Ri = [y for j, y in enumerate(R) if j != i]
            ci = fitc(Ei, Ri, K)
            loo.append(abs(R[i] - ev(ci, E[i])))
            a3s.append(ci[0])
        rms = mp.sqrt(sum(t ** 2 for t in loo) / len(loo))
        print("%-3d %-5d %-12s %-12s %-12s %-22s %-11s" %
              (K, len(E) - (K + 1), mp.nstr(ins, 3), mp.nstr(max(loo), 3), mp.nstr(rms, 3),
               mp.nstr(c[0], 18), mp.nstr(max(a3s) - min(a3s), 3)))
    print()

print("=" * 88)
print("  a3 under the BEST-SUPPORTED K, with a jackknife bar, vs the contour rung a3^kappa")
print("=" * 88)
E, R = rvals(A_U1, B_U2)
for K in (5, 6, 7):
    c = fitc(E, R, K)
    a3s = []
    for i in range(len(E)):
        Ei = [x for j, x in enumerate(E) if j != i]
        Ri = [y for j, y in enumerate(R) if j != i]
        a3s.append(fitc(Ei, Ri, K)[0])
    n = len(E)
    mean = sum(a3s) / n
    jk_se = mp.sqrt((n - 1) * sum((t - mean) ** 2 for t in a3s) / n)
    print("K=%d  a3 = %s  jackknife SE %-11s  |a3 - a3^kappa| = %s"
          % (K, mp.nstr(c[0], 18), mp.nstr(jk_se, 3), mp.nstr(abs(c[0] - A3_KAPPA), 4)))
