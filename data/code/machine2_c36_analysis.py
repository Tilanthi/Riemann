"""machine2 CYCLE 36 -- post-hoc analysis (LABELLED POST-HOC; only P1 and P2 were pre-registered).

(1) Delta_sys, the cross-evaluator difference of the ROOT, extracted properly: m3's Newton
    truncation is not an unknown, it is MEASURED by m3's own published residual, so it can be
    subtracted instead of merely bounded.
(2) The a4/a5 arm re-read against my 45-s.f. published values instead of m3's 20-s.f.
    transcription of them (DERIVATION -- two strings I already hold).
(3) Channel attribution for m3's two real runs against the aliasing scale (2 r_w)^N_w.
"""
import mpmath as mp

mp.mp.dps = 400

# ---- my c34 published constants, 45 s.f. (data: machine2 c34 letter) ----
M2 = {
    "a":  "2.64552141181166286801612612120342539738354204",
    "b":  "-7.46245287679368626753358035162874151331895732",
    "a3": "11.700717320433667601156432487039813849333726",
    "a4": "-20.4755387553904125007058067225760662898269858",
    "a5": "18.2711625011499510374264312726700306984558616",
}
# ---- m3's 20-s.f. transcriptions, verbatim from m3_L171_real_run_a5.py ----
M3_REF = {"a4": "-20.475538755390412501", "a5": "18.271162501149951037"}
# ---- m3's measured values, verbatim from data/results/ ----
M3_RUNA = {"a4": "-20.4755387553904105754015901041862271839908655588978505318629"}
M3_RUNB = {
    "a4": "-20.4755387553904125006269979159639683443945971855235252295226",
    "a5": "18.271162501149950953497895321776842232790188210809652700869",
    "a":  "2.64552141181166286801578167622330739356811981196243300435271",
}
# ---- D* arm ----
M3_DNEW = ("0.141733239663887191395415685084185023623144561955016655942866603946659042189707430"
           "875932704544153491448859401071291155704123242008525016251392377082433")
M3_RESID = ("4.14818457993253249597741047202845430889207042561536883024504736042645118651156774"
            "038010912092306593272407477056931925304607636489137999960106986437164e-119")
M3_FPRIME = ("-37.4819713608428817387593623904468580248697488408325728217061311779766385913905"
             "426802842696260522510376005474554176664760312347805473536765790174362541")
# (my own D* is read back from this cycle's own output file at runtime -- deliberately NOT
#  re-typed here: a hand-typed copy of a 175-digit string is exactly the defect this cycle is about.)

if __name__ == "__main__":
    print("=" * 78)
    print("(1) Delta_sys = D*(m2 evaluator) - D*(m3 evaluator)   [POST-HOC, not preregistered]")
    print("=" * 78)
    # NB: M2_DSTAR_FULL is re-typed from this cycle's own output file; re-read it from disk so a
    # transcription slip cannot enter here.
    import re
    txt = open("/workspace/rh/cycle36/c36_dstar_fullprec.out", encoding="utf-8").read()
    m = re.search(r"\n  (0\.14173\d+)\n", txt)
    D_m2 = mp.mpf(m.group(1))
    print(f"  my D* read back from the run's own output, {len(m.group(1))-2} digits")
    D_new = mp.mpf(M3_DNEW)
    f_res = mp.mpf(M3_RESID)
    fprime = mp.mpf(M3_FPRIME)

    d_total = D_m2 - D_new                       # measured this cycle
    newton = -f_res / fprime                     # = D*(m3) - D_new, from m3's OWN residual
    delta_sys = d_total - newton
    print(f"  D*(m2) - D_new                       = {mp.nstr(d_total, 15)}")
    print(f"  D*(m3) - D_new  (m3's own residual)  = {mp.nstr(newton, 15)}")
    print(f"  Delta_sys = D*(m2) - D*(m3)          = {mp.nstr(delta_sys, 8)}")
    print(f"  Delta_sys relative                   = {mp.nstr(delta_sys / D_m2, 8)}")
    print("  second-order term neglected in 'newton': (f''/2f')*(D_new-D*)^2 ~ "
          f"{mp.nstr(mp.mpf('7.0555') * newton**2, 4)}  (this is the floor of the subtraction)")

    print()
    print("=" * 78)
    print("(2) a4/a5 re-read against my 45-s.f. values  [DERIVATION, not a prediction]")
    print("=" * 78)
    for k in ("a4", "a5"):
        mine = mp.mpf(M2[k])
        ref = mp.mpf(M3_REF[k])
        print(f"  {k}: my published 45 s.f. = {M2[k]}")
        print(f"      m3's hardcoded ref  = {M3_REF[k]}   ({len(M3_REF[k].lstrip('-'))-1} s.f.)")
        print(f"      ref - mine (m3's truncation error) = {mp.nstr(ref - mine, 6)}"
              f"   relative {mp.nstr(abs(ref - mine)/abs(mine), 6)}")
        halfulp = mp.mpf(10) ** (-18) / 2
        print(f"      half-ulp of a 20-s.f. string here  = {mp.nstr(halfulp/abs(mine), 6)} relative")
        if k in M3_RUNB:
            v = mp.mpf(M3_RUNB[k])
            print(f"      QUOTED  rel diff (vs 20-s.f. ref)  = "
                  f"{mp.nstr(abs(v - ref)/abs(ref), 6)}")
            print(f"      CORRECT rel diff (vs 45-s.f. mine) = "
                  f"{mp.nstr(abs(v - mine)/abs(mine), 6)}   <== the measurement")
    v = mp.mpf(M3_RUNA["a4"])
    mine = mp.mpf(M2["a4"])
    print(f"  a4 run A: CORRECT rel diff vs my 45 s.f. = {mp.nstr(abs(v-mine)/abs(mine), 6)}")
    va = mp.mpf(M3_RUNB["a"])
    print(f"  a  run B: CORRECT rel diff vs my 45 s.f. = "
          f"{mp.nstr(abs(va-mp.mpf(M2['a']))/abs(mp.mpf(M2['a'])), 6)}")

    print()
    print("=" * 78)
    print("(3) channel attribution: the aliasing scale (2 r_w)^N_w  [POST-HOC]")
    print("=" * 78)
    r_w = mp.mpf("0.04")
    for tag, N_w in (("run A", 16), ("run B", 20)):
        print(f"  {tag}: (2*{r_w})^{N_w} = {mp.nstr((2*r_w)**N_w, 6)}")
