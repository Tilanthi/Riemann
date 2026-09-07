import subprocess, collections, json, re
R="/shared/rh-exchange-repo/Riemann"
def g(*a): return subprocess.run(["git","-C",R]+list(a),capture_output=True,text=True).stdout
files=[f for f in g("ls-files").split("\n") if f]
d=json.load(open("filelab.json")); subj=d["subj"]
def by_subject(f):
    s=subj.get(f,"").lower().lstrip("*# ")
    tok=re.split(r"[\s:(\-]",s,1)[0]
    if tok in ("machine2","m2","beast","beast-agi","beastagi","atlas"): return "m2"
    if tok in ("machine1","m1"): return "m1"
    if tok in ("machine3","m3","astra","astra-pa"): return "m3"
    if s.startswith("letter"): return "m3"   # astra-pa letter series
    return "?"
def by_name(f):
    b=f.split("/")[-1].lower()
    if re.match(r"(machine2|m2)[_\-]",b) or b.startswith("beast") or "_m2_" in b or b.startswith("c3") : return "m2"
    if re.match(r"(machine1|m1)[_\-]",b) or "_m1_" in b: return "m1"
    if re.match(r"(machine3|m3|astra)[_\-]",b) or b.startswith("letter"): return "m3"
    return "?"
rows=[]
for f in files:
    a,b=by_subject(f),by_name(f)
    rows.append((f,a,b))
agree=collections.Counter((a,b) for _,a,b in rows)
print("subject x name matrix:")
for k,v in sorted(agree.items(), key=lambda x:-x[1]): print("  subj=%-3s name=%-3s : %d"%(k[0],k[1],v))
OURS=sorted(f for f,a,b in rows if a=="m2" or b=="m2")
CONFLICT=[(f,a,b) for f,a,b in rows if {a,b}>= {"m2"} and (a in("m1","m3") and b=="m2" or b in("m1","m3") and a=="m2")]
print("\nOURS (union, over-approximation):", len(OURS))
print("conflicting signals:", len(CONFLICT))
for f,a,b in CONFLICT[:20]: print("   ",f[:70],a,b)
UNK=[f for f,a,b in rows if a=="?" and b=="?"]
print("\nboth-signals-unknown:",len(UNK))
for f in UNK[:20]: print("   ",f[:80],"|",subj.get(f,"")[:60])
open("ours.txt","w").write("\n".join(OURS))
