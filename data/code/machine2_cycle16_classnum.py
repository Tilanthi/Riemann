"""FORM class number vs FIELD class number for every discriminant machine 2 has cited in this lane.
The two readings of the Davenport-Heilbronn hypothesis are inequivalent exactly when D is
NON-FUNDAMENTAL, and every discriminant we have cited is non-fundamental."""
import math, json

def reduced_forms(D):
    """primitive reduced positive-definite forms (a,b,c), b^2-4ac = D < 0."""
    out = []
    b = D % 2
    while b * b <= abs(D) / 3.0:
        for bb in ({b} if b == 0 else {b, -b}):
            n = bb * bb - D
            if n % 4: continue
            ac = n // 4
            a = max(1, abs(bb))
            while a * a <= ac:
                if ac % a == 0:
                    c = ac // a
                    if abs(bb) <= a <= c and math.gcd(math.gcd(a, abs(bb)), c) == 1:
                        if not (abs(bb) == a or a == c) or bb >= 0:
                            out.append((a, bb, c))
                a += 1
        b += 2
    return sorted(set(out))

def fundamental(D):
    """fundamental discriminant D0 and conductor f with D = D0 f^2."""
    f = 1
    while True:
        g = 2
        moved = False
        for g in range(2, int(abs(D) ** 0.5) + 2):
            if D % (g * g) == 0:
                D0 = D // (g * g)
                if D0 % 4 in (0, 1) and D0 < 0:
                    D = D0; f *= g; moved = True; break
        if not moved:
            return D, f

FIELD_H = {-4: 1, -8: 1, -3: 1, -7: 1, -11: 1, -20: 2, -23: 3, -24: 2, -100: None}
rows = []
print("%-8s %-22s %-6s %-8s %-8s %-8s" % ("D", "reduced primitive forms", "h_form", "D0(fund)", "cond f", "h_field(Q(sqrt D))"))
for D in [-196, -200, -400, -1600, -20, -23, -4, -8]:
    rf = reduced_forms(D)
    D0, f = fundamental(D)
    hf = FIELD_H.get(D0, "?")
    print("%-8d %-22s %-6d %-8d %-8d %s" % (D, str(rf[:3]) + ("..." if len(rf) > 3 else ""), len(rf), D0, f, hf))
    rows.append(dict(D=D, forms=rf, h_form=len(rf), D0=D0, cond=f, h_field=hf))
json.dump(rows, open("classnum.json", "w"), indent=1)
print()
print("D = -196: forms =", reduced_forms(-196))
print("  => Q(sqrt(-196)) = Q(sqrt(-4)) = Q(i), h_field = 1;  h_form = 4  (order of conductor 7 in Z[i])")
