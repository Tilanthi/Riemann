from mpmath import mp, mpmathify as M, nstr, log, pi, mpf
mp.dps=60
def cmp(name, ours_s, m3_s):
    o=M(ours_s); m=M(m3_s)
    # how many leading significant digits agree
    if o==m: n=len(ours_s.replace('0.','').replace('.','').lstrip('-'))
    rel=abs((m-o)/m) if m!=0 else abs(m-o)
    print("  %-28s ours(pub)=%-30s  m3=%s"%(name,ours_s,m3_s[:len(ours_s)+8]))
    print("  %-28s |rel diff| = %s   (our published width = %d s.f.)"
          %("",nstr(rel,6), len(ours_s.split('e')[0].replace('.','').replace('-','').lstrip('0'))))
print("=== KAT-1 arm A (s=0.2) : our README 7A spec vs m3's kat1_gate_output.txt ===")
cmp("W formula side","0.01859045044076295597727455","0.018590450440762955977274555141105163095024203033301")
cmp("Z zero side","0.01859045044076295597727456","0.018590450440762955977274555141105163095024240234062")
cmp("prime component","-0.00241645242748","-0.0024164524274830623352210108875128337805374356464876")
print()
print("=== KAT-1 arm B (s=1) ===")
cmp("Z zero side","2.070970413701769232754477e-43","2.070970413701769232754477296205666944227328124486e-43")
cmp("prime component","-2.68196739383","-2.6819673938269101365228133810592532997578923629871")
print()
print("=== the log(pi) bookkeeping claim, checked at full published width ===")
lp=log(pi); print("  log(pi) =", nstr(lp,15))
for nm,ours,m3 in [("armA pole","1.00767712046","-0.13705276539165901823169530881640614983617323872177"),
                   ("armA arch","-0.986670217589","0.15805966825990503654419087484502414671173487740155"),
                   ("armB pole","5.68076390362","4.5360340177739720266719449993906226262540238311654"),
                   ("armB arch","-2.9987965098","-1.8540666239470618901491316183313666910179029918293")]:
    d=M(m3)-M(ours)
    print("  %-10s m3 - ours = %-20s   vs -+log(pi) = %s   match to %s"
          %(nm, nstr(d,12), nstr(lp,12), nstr(abs(abs(d)-lp),3)))
print()
print("=== arm B residual: is it checkable from our spec? ===")
ourW=M("2.617429714635e-33"); m3W=M("2.6354782284763490853071815283848441031592914267826e-33")
print("  ours 2.617429714635e-33 vs m3 2.63547822847e-33 -> ratio", nstr(m3W/ourW,10), "(%.2f%% apart)"%float((m3W/ourW-1)*100))
print("  our spec printed its arm-B components to 12 s.f.; the residual sits at 2.6e-33 against O(5) terms,")
print("  i.e. 33 decades below them => the residual is fixed by component digits 13..34, WHICH WE NEVER PRINTED.")
print("  => arm B as specified in README 7A is NOT falsifiable from the artefact. Self-charge.")
