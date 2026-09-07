"""c38 -- HAND classification of the 39 harvested testimony lines.  Declared: the classes were fixed
in m2_c38_testimony.py's header BEFORE any extraction was read; the ASSIGNMENT below is by hand and
is labelled as such (it is not a measurement).  Two extra MEASURED columns, not hand-set:
  width_recorded  -- the integer width the other party attributes to OUR print, parsed from the line
  direction       -- OURS (their statement is about our print) / THEIRS (about their own)
"""
import csv
CLS = {
 1:("BIND","OURS",28), 2:("OTHER","OURS",28), 3:("ADEQ","OURS",25), 4:("BIND","OURS",19),
 5:("OTHER","AMBIG",22), 6:("OTHER","AMBIG",22), 7:("OTHER","AMBIG",22), 8:("OTHER","AMBIG",22),
 9:("SELF","THEIRS",12), 10:("SELF","THEIRS",12), 11:("SELF","THEIRS",12), 12:("SELF","THEIRS",12),
 13:("SELF","THEIRS",12), 14:("BIND","OURS",83), 15:("BIND","OURS",83), 16:("BIND","OURS",83),
 17:("ADEQ","OURS",0), 18:("BIND","OURS",32), 19:("ADEQ","OURS",24), 20:("ADEQ","OURS",0),
 21:("ADEQ","OURS",25), 22:("OTHER","OURS",0), 23:("OTHER","OURS",0), 24:("OTHER","OURS",0),
 25:("ADEQ","OURS",10), 26:("OTHER","OURS",0), 27:("SELF","THEIRS",17), 28:("OVER","OURS",9),
 29:("SELF","THEIRS",7), 30:("ADEQ","OURS",0), 31:("OTHER","OURS",0), 32:("SELF","THEIRS",0),
 33:("OVER","OURS",7), 34:("OTHER","OURS",27), 35:("OTHER","AMBIG",18), 36:("BIND","OURS",3),
 37:("BIND","OURS",4), 38:("BIND","OURS",20), 39:("ADEQ","OURS",0),
}
rows=list(csv.reader(open('c38_testimony_raw_v2.tsv'), delimiter='\t'))[1:]
out=csv.writer(open('c38_testimony_classified.tsv','w'), delimiter='\t')
out.writerow(["idx","class","direction","width_recorded","file","line","text"])
from collections import Counter
cnt=Counter(); dirn=Counter()
for i,(f,l,t) in enumerate(rows,1):
    c,d,w = CLS[i]; cnt[c]+=1; dirn[d]+=1
    out.writerow([i,c,d,w,f,l,t])
print("harvested lines: %d" % len(rows))
print("class counts (HAND-assigned, classes fixed before extraction):", dict(cnt))
print("direction counts (measured from the sentence's subject):", dict(dirn))
named = sorted({(CLS[i][2], rows[i-1][0]) for i in CLS if CLS[i][0] in ("BIND","ADEQ","OVER")
                and CLS[i][1]=="OURS" and CLS[i][2]>0})
print("\ntestimony rows that state a WIDTH for one of OUR published constants: %d" % len(named))
for w,f in named: print("   width %-3d  %s" % (w,f))
