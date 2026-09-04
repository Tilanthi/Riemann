D = -196;
print("PARI/GP version check: ", version());
print("[A] qfbclassno(", D, ") = ", qfbclassno(D));
print("[A] quadclassunit(", D, ") = ", quadclassunit(D));
{
L = List();
amax = floor(sqrt(-D/3));
for(a=1, amax,
  for(b=-a+1, a,
    if((b^2-D)%(4*a)==0,
      c=(b^2-D)/(4*a);
      if(c>=a && gcd([a,b,c])==1 && !(a==c && b<0),
        listput(L,[a,b,c])))));
print("[B] primitive reduced forms of disc ", D, ": ", Vec(L));
print("[B] h by enumeration = ", #L);
}
{
id = qfbred(Qfb(1,0,49));
for(i=1,4,
  v = L[i]; f = Qfb(v[1],v[2],v[3]); g = f; o = 1;
  while(g != id && o < 30, g = qfbred(qfbcompraw(g,f)); o++);
  print("[B] form ", v, " has order ", o));
}
\\ controls: discriminants with KNOWN, DIFFERENT group structures
{
for(k=1,6,
  Dc = [-84,-56,-20,-23,-4,-3][k];
  print("[CTRL] D=", Dc, " classno=", qfbclassno(Dc), " structure=", quadclassunit(Dc)[2]));
}
\\ conductor-formula cross-check, computed independently of m1's arithmetic
{
f = 7; dK = -4; hK = qfbclassno(dK); w = 4; wf = 2;
hf = hK * f / (w/wf) * prod(i=1,1, (1 - kronecker(dK,f)/f));
print("[C] h(order f=7 in Q(i)) via formula = ", hf, "   kronecker(-4,7)=", kronecker(-4,7));
print("[C] disc of order = f^2*dK = ", f^2*dK);
}
\\ ambiguous (2-torsion) classes = genus count
{
amb = 0;
for(i=1,4, v=L[i]; if(v[2]==0 || v[1]==v[2] || v[1]==v[3], amb++));
print("[D] ambiguous reduced forms (2-torsion classes) = ", amb, "  => 2-torsion subgroup order ", amb);
}
