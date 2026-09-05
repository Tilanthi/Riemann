# machine1 verification of m2 da0a601 Part-A falsifier (display-truncated eps in m1-L163 S2)
# y(eps) = (u^2 - r*eps^3)/eps must be exactly linear in eps (algebra: = a + b*eps).
# Row data = m1-L163 r-table verbatim (u 18 digits, r 9 decimals).
# Two eps variants: (i) as displayed in the letter; (ii) true grid literals (heat72_birth_locus).
# Floor per m2: 5e-10*eps^2 + 1e-16. LSQ line over all 11 rows; departure = y_i - line(eps_i).

from mpmath import mp, mpf

mp.dps = 60

A = mpf("2.645521411811664489")   # registered a (19 digits)
B = mpf("7.4624528767937415788")  # registered |b| (21 digits)

rows = [
    # (eps_display_str, eps_true_str, u_str, r_str)
    ("0.001",           "0.001",              "0.051507238189400637", "11.721211198"),
    ("0.0011239",       "0.0011239031932557", "0.054614584740162861", "11.723753018"),
    ("0.002",           "0.002",              "0.072945092837465637", "11.741741999"),
    ("0.0035",          "0.0035",             "0.096701834210430658", "11.772608283"),
    ("0.006",           "0.006",              "0.127060343186758932", "11.824242141"),
    ("0.0082668",       "0.0082667603361",    "0.149621445957808029", "11.871268385"),
    ("0.012",           "0.012",              "0.181222234597205520", "11.949164587"),
    ("0.02",            "0.02",               "0.236627035028954719", "12.118039956"),
    ("0.035",           "0.035",              "0.319794030841904226", "12.442401741"),
    ("0.06",            "0.06",               "0.434057465263706266", "13.008185583"),
    ("0.1",             "0.1",                "0.594279218305137112", "13.991119360"),
]

def run(variant, which):
    eps = [mpf(r[which]) for r in rows]
    u   = [mpf(r[2]) for r in rows]
    r_  = [mpf(r[3]) for r in rows]
    y = [(u[i]**2 - r_[i]*eps[i]**3)/eps[i] for i in range(11)]
    # exact 2-parameter LSQ line y = c0 + c1*eps  (normal equations)
    n = mpf(11)
    Sx = sum(eps); Sy = sum(y)
    Sxx = sum(e*e for e in eps); Sxy = sum(eps[i]*y[i] for i in range(11))
    c1 = (n*Sxy - Sx*Sy)/(n*Sxx - Sx*Sx)
    c0 = (Sy - c1*Sx)/n
    print(f"--- variant ({variant}): line y = {mp.nstr(c0,12)} + {mp.nstr(c1,12)}*eps   (model: {mp.nstr(A,12)} + {mp.nstr(B,12)}*eps)")
    worst_dep = mpf(0); worst_row = -1
    print(f"{'row':>3} {'eps_used':>18} {'departure':>12} {'floor':>10} {'ratio':>10}")
    for i in range(11):
        dep = y[i] - (c0 + c1*eps[i])
        floor = mpf("5e-10")*eps[i]**2 + mpf("1e-16")
        ratio = abs(dep)/floor
        if abs(dep) > abs(worst_dep): worst_dep, worst_row = abs(dep), i+1
        print(f"{i+1:>3} {rows[i][which]:>18} {mp.nstr(dep,5):>12} {mp.nstr(floor,3):>10} {mp.nstr(ratio,4):>10}")
    print(f"worst departure {mp.nstr(worst_dep,5)} at row {worst_row}; rows with ratio>1: "
          f"{[i+1 for i in range(11) if abs(y[i]-(c0+c1*eps[i]))/(mpf('5e-10')*eps[i]**2+mpf('1e-16')) > 1]}")

run("i: eps as displayed in L163", 0)
print()
run("ii: eps true grid literals", 1)
