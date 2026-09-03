import mpmath as mp
mp.mp.dps = 30

# g(u) = exp(-(ln u)^2/2), the "unwindowed Gaussian" Mac specified.
def g(u):
    u = mp.mpf(u)
    return mp.e**(-(mp.log(u))**2/2)

def g_tau(x):
    x = mp.mpf(x)
    return g(x)/x

# My derived closed form for h = g * g^tau (multiplicative convolution):
# h(u) = (sqrt(pi)/u) * exp( (-L^2+2L+1)/4 ),  L = ln(u)
def h_closed(u):
    u = mp.mpf(u)
    L = mp.log(u)
    return (mp.sqrt(mp.pi)/u) * mp.e**((-L**2+2*L+1)/4)

# Sanity check: numerically evaluate the multiplicative convolution integral directly,
# (g*g^tau)(u) = integral_0^inf g(t) g^tau(u/t) dt/t,  and compare to my closed form,
# at a few sample u values -- BEFORE trusting the algebra.
def h_numeric(u):
    u = mp.mpf(u)
    def integrand(t):
        return g(t) * g_tau(u/t) / t
    # substitute t = e^x to make it a nice integral over the whole real line
    def integrand_x(x):
        t = mp.e**x
        return integrand(t) * t   # dt = t dx
    return mp.quad(integrand_x, [-mp.inf, mp.inf])

print("Sanity check: closed-form h(u) vs direct numerical convolution")
for uval in ['0.3', '1.0', '2.0', '5.0', '10.0']:
    hc = h_closed(uval)
    hn = h_numeric(uval)
    print(f"  u={uval}: closed={hc}  numeric={hn}  rel_diff={abs(hc-hn)/abs(hn)}")
