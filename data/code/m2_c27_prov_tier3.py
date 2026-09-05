"""TIER-3: the tier-2 filter was EXACT-STRING and therefore counted a correct ROUNDING as an orphan.
Re-run repo-wide, rounding-aware: a prose token is SOURCED if any number anywhere in the repo agrees
with it to the token's own precision, in a file other than the one it was written in."""
import json, os, re
from decimal import Decimal, InvalidOperation
REPO="/shared/rh-exchange-repo/Riemann"
NUM=re.compile(r"(?<![\w.])[-+]?\d+\.\d+(?:[eE][-+]?\d+)?(?![0-9.])|(?<![\w.])[-+]?\d+(?:\.\d*)?[eE][-+]?\d+(?![0-9.])")
def sd(t):
    s=t.lstrip("+-").split("e")[0].split("E")[0].replace(".","").lstrip("0")
    return len(s.rstrip("0")) if s.rstrip("0") else 0
corpus={}
for root,dirs,files in os.walk(REPO):
    dirs[:]=[d for d in dirs if d not in (".git","__pycache__")]
    for f in files:
        if f.endswith((".py",".out",".md",".json",".log",".txt")):
            p=os.path.join(root,f)
            try: corpus[p]=set(NUM.findall(open(p,errors="replace").read()))
            except Exception: pass
print("corpus files:",len(corpus),"distinct numeric tokens:",len(set().union(*corpus.values())))
tri=json.load(open("c27_provenance_triage.json"))
res=[]
for o in tri["orphans"]:
    tok=o["token"]; v=Decimal(tok); n=sd(tok); tol=Decimal(10)**(-(n-1))
    hits=[]
    for p,toks in corpus.items():
        if os.path.basename(p)==o["script"]: continue
        for w in toks:
            try: u=Decimal(w)
            except InvalidOperation: continue
            if u==0: continue
            if abs((u-v)/v)<tol: hits.append((os.path.basename(p),w)); break
        if len(hits)>=3: break
    res.append({"script":o["script"],"token":tok,"sourced":bool(hits),"examples":hits[:3]})
    print("%-38s %-14s %s"%(o["script"],tok,("SOURCED: "+", ".join("%s:%s"%h for h in hits[:2])) if hits else "STILL ORPHAN"))
json.dump(res,open("c27_provenance_tier3.json","w"),indent=1)
print("\nstill-orphan after rounding-aware repo search: %d of %d"%(sum(1 for r in res if not r["sourced"]),len(res)))
