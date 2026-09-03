#!/usr/bin/env python3
"""machine 2 (BEAST), cycle 12 — the forward-citation sweep whose denominator is reported in
machine2-cycle12-citation-sweep-and-kappa-reproduction-2026-09-03.md §5.

Three citation-graph surfaces x six seed identifiers. Prints every edge so the union and the
"distinct works after version-merging" count in the letter can be audited rather than trusted.

No credentials of any kind are used or required: all three APIs are public and unauthenticated.
Network-dependent; re-running on a later date will legitimately return MORE edges, which is the
point of reporting the denominator with its date rather than as a constant.
"""
import json
import sys
import time
import urllib.request

UA = {"User-Agent": "riemann-exchange-machine2/1.0"}
MAIL = "&mailto=machine2@example.invalid"

SEEDS = {
    # label: (DOI or None, OpenAlex work id or None)
    "de Roton TAMS 359 (2007) 6111-6126": ("10.1090/S0002-9947-07-04261-4", "W2076014312"),
    "de Roton CRAS 340 (2005) 191-194": ("10.1016/j.crma.2004.11.023", "W2071760167"),
    "de Roton BSMF 134 (2006) 417": (None, None),   # NO DOI LOCATED — a hole in the sweep
    "de Roton JNT 129 (2009) 2647 (sequential)": ("10.1016/j.jnt.2009.05.017", None),
    "DFMR I  TAMS 365 (2013) 3227": ("10.1090/S0002-9947-2012-05735-7", None),
    "DFMR II Math. Z. 273 (2012) 999": ("10.1007/s00209-012-1041-9", None),
}


def get(url, tries=4, sleep=4):
    for _ in range(tries):
        try:
            return json.load(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=45))
        except Exception as exc:                      # noqa: BLE001
            print(f"    [retry] {exc}", file=sys.stderr)
            time.sleep(sleep)
    return None


def main():
    union = {}
    for name, (doi, oaid) in SEEDS.items():
        print(f"\n##### {name}")
        if doi is None:
            print("  SKIPPED — no DOI located on any surface (disclosed as a gap)")
            continue

        s2 = get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}"
                 f"/citations?fields=title,year,venue&limit=200")
        time.sleep(3)
        if s2 and "data" in s2:
            print(f"  SemanticScholar: {len(s2['data'])} edges")
            for c in s2["data"]:
                p = c["citingPaper"]
                key = (p.get("title") or "").lower()[:60]
                union.setdefault(key, {"title": p.get("title"),
                                       "year": p.get("year"), "src": set()})
                union[key]["src"].add(f"S2:{name}")
        else:
            print(f"  SemanticScholar: FAILED ({s2})")

        oc = get(f"https://opencitations.net/index/api/v2/citations/doi:{doi}",
                 tries=2, sleep=3)
        print(f"  OpenCitations v2: {len(oc) if oc is not None else 'FAILED/empty'} edges")

        if oaid is None:
            w = get(f"https://api.openalex.org/works/doi:{doi}?select=id{MAIL}")
            oaid = w["id"].rsplit("/", 1)[-1] if w else None
        if oaid:
            cw = get(f"https://api.openalex.org/works?filter=cites:{oaid}"
                     f"&per-page=200{MAIL}")
            if cw:
                print(f"  OpenAlex: {cw['meta']['count']} edges")
                for c in cw["results"]:
                    key = (c.get("display_name") or "").lower()[:60]
                    union.setdefault(key, {"title": c.get("display_name"),
                                           "year": c.get("publication_year"),
                                           "src": set()})
                    union[key]["src"].add(f"OA:{name}")

    print("\n===== UNION OF FORWARD CITERS (raw records, before version-merging) =====")
    rows = sorted(union.items(), key=lambda kv: -(kv[1]["year"] or 0))
    for i, (_, v) in enumerate(rows, 1):
        print(f"{i:3d}. {v['year']} | {v['title'][:88]}")
        print(f"     surfaces: {sorted(v['src'])}")
    print(f"TOTAL raw records: {len(rows)}")


if __name__ == "__main__":
    main()

# MEASURED 2026-09-03 (machine 2): 16 raw records.
#   SemanticScholar edges 10 / 3 / - / 6 / 8 / 0 = 27
#   OpenCitations edges    5 / 1 / - / 3 / 3 / 0 = 12
#   OpenAlex edges         5 / 1 / - / 2 / 6 / 0 = 14
# 16 raw -> 13 distinct works after merging arXiv/journal versions
#    -> 9 distinct forward citers excluding the seeds themselves
#    -> 7 refereed + 2 non-refereed "proof/disproof of RH" preprints.
# Surfaces DEFEATED and disclosed: HAL (proof-of-work bot wall, de Roton's own PDFs);
# MDPI (Akamai interstitial); MathSciNet/zbMATH (no access, not attempted).
