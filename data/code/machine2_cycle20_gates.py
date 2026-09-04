"""machine 2 (beast-atlas) -- cycle 20 -- CHEAP GATES, run before the expensive stage.

Gate A : a_1 != 0 after normalisation (else the reciprocal Dirichlet series does not exist and the
         triangular inversion the NB family relies on is empty).
Gate P : pole order at s=1 must be <= 1 (the cycle-19 instrument kills a simple pole with the one
         linear condition g(1)=0; a double pole needs two and is out of scope THIS cycle).
Gate E : two independent computations of the carrier must agree to >= 12 digits at 3 probe points.
         Leg 1 = the analytic evaluator actually used in the distance run.
         Leg 2 = the DIRICHLET SERIES of the carrier's own claimed coefficients, summed at a real
         point where it converges absolutely (this checks the evaluator AND the coefficient claim,
         including the genus identity for K10, in one shot).
Every gate prints PASS/KILL and the kill counts are published.
"""
import json, sys
from mpmath import mp, mpf, mpc, sqrt, zeta, nstr
sys.path.insert(0, '.')
from machine2_cycle20_carriers import (CARRIERS, carrier_eval, form_coeffs, char_coeffs,
                                       convolve_coeffs, dh_kappa, Lfun, residue_at_1)

mp.dps = 30
NMAX = 4000          # Dirichlet-series truncation for Gate E
PROBES = [mpf(6), mpf(8), mpf(10)]  # real points; truncation tail at n=4000 is < 2e-19 at s=6


def coeffs_for(key, nmax=NMAX):
    """Claimed Dirichlet coefficients a_n of the NORMALISED carrier (a_1 = 1)."""
    one = [mp.zero] * (nmax + 1)
    one[1] = mpf(1)
    if key == "K1_zeta":
        return [mp.zero] + [mpf(1)] * nmax
    if key == "K2_zeta_synth":
        z = [mp.zero] + [mpf(1)] * nmax
        # (1 - 2^{0.55} * 2^{-s}) : coefficients 1 at n=1, -2^{0.55} at n=2
        f = [mp.zero] * (nmax + 1)
        f[1] = mpf(1)
        f[2] = -mpf(2) ** mpf('0.55')
        return convolve_coeffs(z, f, nmax)
    if key == "K3_epstein_D7":
        return form_coeffs(1, 0, 49, nmax)
    if key == "K4_epstein_Dsqrt50":
        return form_coeffs(1, 0, 50, nmax)
    if key == "K5_Lm4":
        return char_coeffs(-4, nmax)
    if key == "K6_zeta_L5":
        return convolve_coeffs([mp.zero] + [mpf(1)] * nmax, char_coeffs(5, nmax), nmax)
    if key == "K7_Lm4_L5":
        return convolve_coeffs(char_coeffs(-4, nmax), char_coeffs(5, nmax), nmax)
    if key == "K8_epstein_D1":
        return form_coeffs(1, 0, 1, nmax)          # (1/2)#{j^2+k^2=n} = 2 at n=1 -> normalise below
    if key == "K9_DH":
        k = dh_kappa()
        per = [mpf(1), k, -k, mpf(-1), mp.zero]
        return [mp.zero] + [per[(n - 1) % 5] for n in range(1, nmax + 1)]
    if key == "K10_Lm7_L28":
        return convolve_coeffs(char_coeffs(-7, nmax), char_coeffs(28, nmax), nmax)
    if key == "K11_form_disc23":
        return form_coeffs(2, 1, 3, nmax)
    if key == "K12_zeta_squared":
        z = [mp.zero] + [mpf(1)] * nmax
        return convolve_coeffs(z, z, nmax)
    raise ValueError(key)


def dirichlet_sum(a, s, nmax=NMAX):
    tot = mp.zero
    for n in range(nmax, 0, -1):
        if a[n] != 0:
            tot += a[n] * mpf(n) ** (-s)
    return tot


def main():
    report = {"gates": [], "kills": {"A": 0, "P": 0, "E": 0}}
    for key, (label, has_pole, deg, off, note) in CARRIERS.items():
        row = {"key": key, "label": label, "pole": has_pole, "degree": deg,
               "offline_zeros": off, "note": note}
        a = coeffs_for(key)
        a1 = a[1]
        row["a1_raw"] = nstr(a1, 12)
        # ---- Gate A
        if a1 == 0:
            row["gateA"] = "KILL"
            report["kills"]["A"] += 1
            report["gates"].append(row)
            print(f"{key:22s} A=KILL (a_1 = 0) -- no evaluation attempted")
            continue
        row["gateA"] = "PASS"
        norm = a1
        a = [x / norm for x in a]
        # ---- Gate P (pole order; all carriers here are pole order 0 or 1 by construction, checked
        #      by the residue diagnostic: (s-1)F(s) -> finite, (s-1)^2 F(s) -> 0)
        eps = mpf('1e-8')
        v1 = (eps) * carrier_eval(key, 1 + eps)
        v2 = (eps) ** 2 * carrier_eval(key, 1 + eps)
        row["pole_probe_(s-1)F"] = nstr(v1, 10)
        row["gateP"] = "PASS" if abs(v2) < mpf('1e-6') else "KILL"
        if row["gateP"] == "KILL":
            report["kills"]["P"] += 1
            report["gates"].append(row)
            print(f"{key:22s} A=PASS P=KILL (pole order >= 2: (s-1)^2 F = {nstr(v2,6)})")
            continue
        # ---- Gate E
        digs = []
        for s in PROBES:
            leg1 = carrier_eval(key, s)
            leg2 = dirichlet_sum(a, s)
            rel = abs(leg1 - leg2) / abs(leg1)
            digs.append(float(-mp.log10(rel)) if rel > 0 else 99.0)
        row["gateE_digits"] = [round(d, 2) for d in digs]
        row["gateE"] = "PASS" if min(digs) >= 12 else "KILL"
        if row["gateE"] == "KILL":
            report["kills"]["E"] += 1
        report["gates"].append(row)
        print(f"{key:22s} A={row['gateA']} P={row['gateP']} E={row['gateE']} digits={row['gateE_digits']}")

    # ---- extra structural checks that feed the letter
    extra = {}
    # (i) K8 really is the normalised Epstein carrier at Delta=1
    from eval_epstein import F as EF
    s = mpc(mpf('0.5'), mpf('7.3'))
    lhs = EF(s, 1) / 2
    rhs = zeta(s) * Lfun(s, -4)
    extra["K8_epstein_identity_reldiff"] = nstr(abs(lhs - rhs) / abs(rhs), 6)
    # (ii) the genus identity behind K10, at coefficient level, disc -196
    nm = 800
    c0 = form_coeffs(1, 0, 49, nm)
    c2 = form_coeffs(2, 2, 25, nm)
    c1 = form_coeffs(5, 2, 10, nm)
    c3 = form_coeffs(5, -2, 10, nm)
    genus = [c0[n] + c2[n] - c1[n] - c3[n] for n in range(nm + 1)]
    prod = convolve_coeffs(char_coeffs(-7, nm), char_coeffs(28, nm), nm)
    mism = [n for n in range(1, nm + 1) if abs(genus[n] - prod[n]) > mpf('1e-20')]
    extra["K10_genus_identity_mismatches_to_800"] = len(mism)
    extra["K10_first_mismatches"] = mism[:5]
    extra["K10_c1_equals_c3_(inverse pair)"] = all(c1[n] == c3[n] for n in range(1, nm + 1))
    # (iii) residues (diagnostic only)
    extra["residues_measured_as_(s-1)F(1+1e-8)"] = {r["key"]: r.get("pole_probe_(s-1)F") for r in report["gates"]}
    report["extra"] = extra
    print(json.dumps(extra, indent=1))
    json.dump(report, open("machine2_cycle20_gates.json", "w"), indent=1)
    print("KILLS:", report["kills"])


if __name__ == "__main__":
    main()
