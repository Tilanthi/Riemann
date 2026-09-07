"""Build the CYCLE-37 published-constants manifest (the artefact the C7 row closes on)."""
import json, math, os
rows=json.load(open("census2.json"))
def half_ulp_rel(w):
    # a decimal string carrying w significant figures: worst-case relative half-ulp = 5e-w
    return 5.0*10**(-w)
out=[]
for r in rows:
    ow=r["ourW"]; tw=r["theirW"]
    binding = "OURS" if ow<tw else ("THEIRS" if ow>tw else "EQUAL")
    out.append({
      "our_widest_string": r["wide_our"], "our_W_sf": ow,
      "our_W_in_letters_md": r["ourW_md"], "our_W_in_data_files": r["ourW_data"],
      "their_widest_string": r["wide_their"], "their_W_sf": tw,
      "their_file": r["their_file"],
      "comparison_resolution_rel": "%.1e"%half_ulp_rel(min(ow,tw)),
      "our_half_ulp_rel": "%.1e"%half_ulp_rel(ow),
      "binding_side": binding,
      "letter_narrower_than_our_own_data": bool(r["ourW_md"] and r["ourW_data"] and r["ourW_md"]<r["ourW_data"]),
      "n_occurrences_ours": r["n_our"], "n_occurrences_theirs": r["n_their"],
      "our_letter_example": (r["md_ex"][2] if r["md_ex"] else None),
      "working_precision_at_publication": "UNMEASURED",
    })
out.sort(key=lambda x:(x["binding_side"]!="OURS", -(x["their_W_sf"]-x["our_W_sf"])))
json.dump(out, open("m2_published_constants_census.json","w"), indent=1)
# compact TSV
with open("m2_published_constants_census.tsv","w") as f:
    f.write("our_string\tourW\tourW_md\tourW_data\ttheir_string\ttheirW\tbinding\tcomparison_res_rel\tour_half_ulp_rel\ttheir_file\n")
    for e in out:
        f.write("\t".join([e["our_widest_string"],str(e["our_W_sf"]),str(e["our_W_in_letters_md"]),
                str(e["our_W_in_data_files"]),e["their_widest_string"],str(e["their_W_sf"]),
                e["binding_side"],e["comparison_resolution_rel"],e["our_half_ulp_rel"],e["their_file"]])+"\n")
print("rows:",len(out))
for k in ("OURS","THEIRS","EQUAL"):
    print("  binding %-7s %d"%(k,sum(1 for e in out if e["binding_side"]==k)))
print("  letter narrower than our own data file:",sum(1 for e in out if e["letter_narrower_than_our_own_data"]))
print("sizes:", os.path.getsize("m2_published_constants_census.json"), os.path.getsize("m2_published_constants_census.tsv"))
