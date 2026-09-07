"""c38: P4 falsified the 2-channel fit.  Re-fit at N_w=40 with the alias structure written out:
   eps = x * r^N  +  y * (2r)^{2N}     (x = the deviation of c_N from the pure pole value -4*2^N)
Fitted on the two dps-90 points ONLY (R2, R3) -> zero dof; R5 (dps 125) is then a THIRD point the
fit did not see, and a new r_w is an out-of-sample prediction."""
import json, mpmath as mp
mp.mp.dps=60
G={e['label']:e for e in json.load(open('c38_runs.json'))}
eps={k:mp.mpf(G[k]['eps']) for k in G}
r1,r2=mp.mpf("0.04"),mp.mpf("0.045"); N=40
M=mp.matrix([[r1**N,(2*r1)**(2*N)],[r2**N,(2*r2)**(2*N)]])
v=mp.lu_solve(M,mp.matrix([eps["R2"],eps["R3"]]))
x,y=v[0],v[1]
print("fit on R2/R3 (dps 90, 0 dof):  x = %s   y = %s"%(mp.nstr(x,10),mp.nstr(y,10)))
print("   [y is the SECOND-alias coefficient; the pure pole-pair model predicts exactly -4]")
print("   x*r^N at r=0.04 : %s      y*(2r)^2N : %s"%(mp.nstr(x*r1**N,8),mp.nstr(y*(2*r1)**(2*N),8)))
pred_R5=x*r1**N+y*(2*r1)**(2*N)
print("\nTHIRD POINT the fit did not see -- R5 (same r_w, dps 125):")
print("   model %s   measured %s   dev %s (%s %%)"%(mp.nstr(pred_R5,10),mp.nstr(eps['R5'],10),
      mp.nstr(eps['R5']-pred_R5,6), mp.nstr(100*(eps['R5']-pred_R5)/pred_R5,4)))
print("   => a residual precision-dependent term of %s remains at N_w=40, r_w=0.04"%mp.nstr(eps['R5']-eps['R2'],6))
for rw in ["0.035","0.03","0.05"]:
    r=mp.mpf(rw); p=x*r**N+y*(2*r)**(2*N)
    print("\nPREDICTION at r_w=%s, N_w=40: eps = %s   (x-term %s, y-term %s)"
          %(rw,mp.nstr(p,8),mp.nstr(x*r**N,6),mp.nstr(y*(2*r)**(2*N),6)))
