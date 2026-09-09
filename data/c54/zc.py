from mpmath import mp, zetazero, pi
import json
mp.dps = 30
out = {}
for x in (13, 17, 19, 25):
    T = 2 * pi * x
    k = 0
    while True:
        g = zetazero(k + 1).imag
        if g > T:
            break
        k += 1
    out[str(x)] = dict(T_star=mp.nstr(T, 20), n=k,
                       gamma_k=mp.nstr(zetazero(k).imag, 20),
                       gamma_k_plus_1=mp.nstr(zetazero(k + 1).imag, 20))
    print(x, "n =", k, " gamma_n =", mp.nstr(zetazero(k).imag, 15),
          " < T* =", mp.nstr(T, 15), " < gamma_{n+1} =", mp.nstr(zetazero(k + 1).imag, 15), flush=True)
json.dump(dict(counts=out, convention="n = #{gamma : 0 < gamma <= 2*pi*x}, MEASURED from mpmath "
                                      "zetazero with the bracketing ordinates printed, never cited"),
          open("m2_c54_zerocount.json", "w"), indent=1)
