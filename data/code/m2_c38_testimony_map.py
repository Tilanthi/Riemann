"""c38 section 7: how much of the working_precision_at_publication column can TESTIMONY actually
reach?  Measured, not asserted: for each harvested testimony line, look for a >=8-digit decimal
literal and ask whether it matches (as a prefix, either direction) any `our_string` in the committed
c37 census of 486 transported constants."""
import csv, re
cen = list(csv.DictReader(open('/shared/rh-exchange-repo/Riemann/data/m2_c37_published_constants_census.tsv'),
                          delimiter='\t'))
ours = [row['our_string'].lstrip('-') for row in cen]
print("census rows (constants measurably transported into m1/m3 artefacts): %d" % len(cen))
rows = list(csv.DictReader(open('c38_testimony_classified.tsv'), delimiter='\t'))
LIT = re.compile(r"\d+\.\d{7,}|\d{9,}")
hit = 0; hits = []
for r in rows:
    lits = [l.lstrip('-').replace('.','') for l in LIT.findall(r['text'])]
    m = None
    for l in lits:
        for o in ours:
            oo = o.replace('.','').lstrip('0')
            ll = l.lstrip('0')
            if len(ll) >= 8 and (oo.startswith(ll[:12]) or ll.startswith(oo[:12])):
                m = o; break
        if m: break
    if m:
        hit += 1; hits.append((r['idx'], r['class'], r['width_recorded'], m[:24]))
print("harvested testimony lines: %d ; lines carrying a >=8-digit literal that matches a census constant: %d"
      % (len(rows), hit))
for h in hits: print("   idx %-3s %-5s width=%-3s  census constant %s..." % h)
print()
print("=> testimony reaches %d of %d census rows = %.2f%% of the column."
      % (len(set(h[3] for h in hits)), len(cen), 100.0*len(set(h[3] for h in hits))/len(cen)))
