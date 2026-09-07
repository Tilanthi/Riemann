"""P2: literals published ONLY in our commit messages -- the route a text census cannot see."""
import re, subprocess, json, collections, os
R="/shared/rh-exchange-repo/Riemann"
def g(*a): return subprocess.run(["git","-C",R]+list(a),capture_output=True,text=True).stdout
NUM=re.compile(r'(?<![\w.])(\d+)\.(\d+)(?:[eEdD]([+-]?\d+))?(?![\w.])')
def digs(m): return (m.group(1)+m.group(2)).lstrip("0")
# our commits: subject prefix measurement (same rule as the file census)
log=g("log","--format=%H%x1f%B%x1e").split("\x1e")
ours_commits=[]
for e in log:
    e=e.strip()
    if not e: continue
    h,body=e.split("\x1f",1)
    tok=re.split(r"[\s:(\-]", body.strip().lower(), 1)[0]
    if tok in ("machine2","m2","beast","beastagi","beast-agi","atlas"): ours_commits.append((h,body))
print("our commits (by subject-prefix measurement):",len(ours_commits))
# full literal set present in ANY file of the repo, at HEAD and historically (use HEAD + each commit's tree is expensive;
# use: union over all blobs ever, restricted to text) -> cheaper: union over HEAD files + the files touched by each commit at that commit
head_lits=set()
for f in [x for x in g("ls-files").split("\n") if x and not x.lower().endswith(".pdf")]:
    p=os.path.join(R,f)
    if not os.path.isfile(p): continue
    t=open(p,encoding="utf-8",errors="replace").read()
    for m in NUM.finditer(t):
        d=digs(m)
        if len(d)>=10: head_lits.add(d)
print("distinct >=10 s.f. literals present in files at HEAD:",len(head_lits))
missing=collections.defaultdict(list)
for h,body in ours_commits:
    for m in NUM.finditer(body):
        d=digs(m)
        if len(d)>=10 and d not in head_lits:
            missing[d].append((h[:7], m.group(0), body.split("\n")[0][:70]))
print("\n## P2 SCORING")
print("  distinct >=10 s.f. literals in OUR commit messages that appear in NO file at HEAD:",len(missing))
print("  band was [1, 40]  =>", "CONFIRMED" if 1<=len(missing)<=40 else "FALSIFIED")
for d,v in sorted(missing.items(), key=lambda kv:-len(kv[0]))[:40]:
    print("   %-2d s.f.  %-30s  %s  | %s"%(len(d), v[0][1][:30], v[0][0], v[0][2][:60]))
json.dump({k:v[0] for k,v in missing.items()}, open("p2_commitonly.json","w"), indent=0)
