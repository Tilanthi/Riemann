vals = {
 "buggy_dps250":  "3.7208997416671221202881772152411083196157325547661749479087140031",
 "fixed_dps250":  "3.7208997416671239357914347660945406940913856191406195228312934724",
 "sanity_dps150": "3.72089974166712393579143476609454069409138562",
 "committed150":  "3.720899741667123935791434766094540694091",
}
def common(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]: n += 1
    return n
print("fixed extends committed150:", vals["fixed_dps250"].startswith(vals["committed150"]))
print("fixed extends sanity150:   ", vals["fixed_dps250"].startswith(vals["sanity_dps150"][:42]))
print("buggy vs fixed common digits:", common(vals["buggy_dps250"], vals["fixed_dps250"]))
print("sanity vs committed150 common:", common(vals["sanity_dps150"], vals["committed150"]), "(= committed width, exact)")
d = vals["fixed_dps250"]
print("fixed literal s.f. count:", len(d), "(digit '3.' + ", len(d)-1, "mantissa digits -> total s.f. =", len(d), ")")
