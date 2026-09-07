import re, os, json, subprocess, collections, sys
R="/shared/rh-exchange-repo/Riemann"
ours=[l for l in open("ours.txt").read().split("\n") if l]
# numeric literal: mantissa with a decimal point, optional exponent. Require a '.' -> excludes integers/counts/years.
NUM=re.compile(r'(?<![\w.])(\d+)\.(\d+)(?:[eEdD]([+-]?\d+))?(?![\w.])')
def sigfigs(ip,fp):
    s=(ip+fp).lstrip("0")
    if s=="": return 0
    return len(s.rstrip() ) if False else len(s)
recs=[]
skipped_bin=[]
for f in ours:
    p=os.path.join(R,f)
    if f.lower().endswith((".pdf",)) or not os.path.isfile(p): skipped_bin.append(f); continue
    try: txt=open(p,encoding="utf-8",errors="replace").read()
    except Exception: skipped_bin.append(f); continue
    for ln,line in enumerate(txt.split("\n"),1):
        # skip obvious date lines? no - handled by sigfig + context filters later
        for m in NUM.finditer(line):
            ip,fp,ex=m.group(1),m.group(2),m.group(3)
            sf=sigfigs(ip,fp)
            recs.append({"file":f,"line":ln,"lit":m.group(0),"sf":sf,"exp":ex,"ctx":line.strip()[:160]})
print("files scanned:",len(ours)-len(skipped_bin),"skipped(binary/missing):",len(skipped_bin))
print("total decimal literals:",len(recs))
h=collections.Counter(r["sf"] for r in recs)
print("sig-fig distribution (sf: count):")
tot=0
for k in sorted(h):
    tot+=h[k]
    print("  %2d : %6d"%(k,h[k]), end="")
    if k%4==3: print()
print()
cum=0
for thr in (10,12,14,16,18,20,25,30,40,45,60,80,100):
    c=sum(v for k,v in h.items() if k>=thr); print("  >= %3d s.f. : %d"%(thr,c))
json.dump(recs,open("lits.json","w"))
