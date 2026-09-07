import re,os,json,collections,subprocess
R="/shared/rh-exchange-repo/Riemann"
ours=set(l for l in open("ours.txt").read().split("\n") if l)
allf=[f for f in subprocess.run(["git","-C",R,"ls-files"],capture_output=True,text=True).stdout.split("\n") if f]
theirs=[f for f in allf if f not in ours and not f.lower().endswith(".pdf")]
NUM=re.compile(r'(?<![\w.])(\d+)\.(\d+)(?:[eEdD]([+-]?\d+))?(?![\w.])')
def scan(fl):
    out=[]
    for f in fl:
        p=os.path.join(R,f)
        if not os.path.isfile(p): continue
        try: txt=open(p,encoding="utf-8",errors="replace").read()
        except Exception: continue
        for ln,line in enumerate(txt.split("\n"),1):
            for m in NUM.finditer(line):
                d=(m.group(1)+m.group(2)).lstrip("0")
                if len(d)>=10: out.append((f,ln,m.group(0),d,line.strip()[:170]))
    return out
O=scan(sorted(ours)); T=scan(theirs)
def key(d): return d[:12]
oidx=collections.defaultdict(list); tidx=collections.defaultdict(list)
for r in O: oidx[key(r[3])].append(r)
for r in T: tidx[key(r[3])].append(r)
shared=sorted(set(oidx)&set(tidx))
rows=[]
for k in shared:
    om=[r for r in oidx[k] if r[0].endswith(".md")]
    od=[r for r in oidx[k] if not r[0].endswith(".md")]
    tm=tidx[k]
    W=lambda L: max((len(r[3]) for r in L), default=0)
    r={"key":k,"ourW_md":W(om),"ourW_data":W(od),"ourW":W(oidx[k]),"theirW":W(tm),
       "n_our":len(oidx[k]),"n_their":len(tm),
       "md_ex":(om[0][2],om[0][0],om[0][4]) if om else None,
       "wide_our":max(oidx[k],key=lambda r:len(r[3]))[2],
       "wide_their":max(tm,key=lambda r:len(r[3]))[2],
       "their_file":max(tm,key=lambda r:len(r[3]))[0]}
    rows.append(r)
json.dump(rows,open("census2.json","w"),indent=0)
print("distinct shared constants (>=12 leading sig digits agree):",len(rows))
capping=[r for r in rows if r["ourW"]<r["theirW"]]
theircap=[r for r in rows if r["ourW"]>r["theirW"]]
eq=[r for r in rows if r["ourW"]==r["theirW"]]
print("  OUR widest print is the BINDING limit (ourW < theirW): %d"%len(capping))
print("  THEIR width binding (ourW > theirW):                    %d"%len(theircap))
print("  equal width:                                            %d"%len(eq))
letter_gap=[r for r in rows if r["ourW_md"] and r["ourW_data"] and r["ourW_md"]<r["ourW_data"]]
print("\n  constants where OUR LETTER prints NARROWER than our own committed data file: %d"%len(letter_gap))
for r in sorted(letter_gap,key=lambda r:r["ourW_data"]-r["ourW_md"],reverse=True)[:25]:
    print("   md=%-3d data=%-3d gap=%-3d  %-28s | %s"%(r["ourW_md"],r["ourW_data"],r["ourW_data"]-r["ourW_md"],r["md_ex"][0][:28],r["md_ex"][2][:70]))
print("\n--- OUR PRINT BINDING, sorted by digits hidden (theirW-ourW) ---")
for r in sorted(capping,key=lambda r:r["theirW"]-r["ourW"],reverse=True)[:25]:
    print("   ourW=%-3d theirW=%-3d  ours=%-26s their=%s"%(r["ourW"],r["theirW"],r["wide_our"][:26],r["wide_their"][:34]))
