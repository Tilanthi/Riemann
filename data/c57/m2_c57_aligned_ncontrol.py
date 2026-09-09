#!/usr/bin/env python3
"""m2_c57_aligned_ncontrol.py -- THE c56 REPAIR, APPLIED: align the N-control by EIGENVALUE.

c56 measured that the N-control compares sector rung k at N=100 with sector rung k at N=180, and
that this is a convergence test ONLY IF rung k is the same eigenfunction in both runs -- which at
x=42 it is not (the lowest rung is displaced 5.473 local gaps).  c56 REGISTERED the repair and
deliberately did not apply it, because inventing a rescue for an arm inside the cycle that needs
rescuing is the forbidden move.  c57 applies it, from the prereg, before looking.

METHOD (fixed in m2_c57_prereg.md sec 5, not chosen after seeing the answer):
  offset s* = argmin over s of  sum_{k=1..6} | log10 lam^{100}_k - log10 lam^{180}_{k+s} |
  then the agreeing prefix is recounted on the ALIGNED pairs (k, k+s*).

WHAT THIS PROGRAM MAY NOT DO.  It never computes p1/p2/p3, never calls _first_leave, never builds a
pooled delta sequence.  It reads node counts (which the author has already seen at x=42, disclosed
in the prereg sec 2) only to count AGREEMENTS between two bases -- an instrument quantity.

EVERY FILE IT OPENS IS PINNED: the corpus is derived by CONTENT and then SORTED, and every selection
is asserted to be unique before use (trap #177: a detector that chooses its target by directory
order is not reproducible).
"""
import json, os, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, ".."))
LOWEST = 6            # rungs of the N=100 ladder used to fit the offset (prereg sec 5)
SMAX = 12             # offsets scanned


def _load_all():
    """CORPUS BY CONTENT, then SORTED.  Two populations: stage-A spectra and stage-B node cells."""
    specs, nodes = [], []
    for root, dirs, fs in os.walk(DATA):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in sorted(fs):
            if not f.endswith(".json"):
                continue
            p = os.path.join(root, f)
            try:
                d = json.load(open(p))
            except Exception:
                continue
            if not (isinstance(d, dict) and isinstance(d.get("rungs"), list) and d["rungs"]
                    and isinstance(d["rungs"][0], dict)
                    and all(k in d for k in ("x", "N", "parity"))):
                continue
            r0 = d["rungs"][0]
            if "nu" in r0:
                nodes.append((os.path.relpath(p, DATA), d))
            elif "log10" in r0 and len(d["rungs"]) > 20:
                specs.append((os.path.relpath(p, DATA), d))
    return sorted(specs), sorted(nodes)


def _pick(pop, x, N, par, what):
    """PINNED selection: exactly one member, or the caller is told there is not."""
    hits = sorted([(rel, d) for rel, d in pop
                   if d["x"] == x and d["N"] == N and d["parity"] == par])
    if len(hits) != 1:
        return None, dict(what=what, x=x, N=N, parity=par, candidates=[h[0] for h in hits],
                          status=("ABSENT" if not hits else "AMBIGUOUS -- %d candidates" % len(hits)))
    return hits[0], None


def offset_fit(l100, l180):
    """s* and its mean absolute residual, in log10 units and in local-gap units."""
    n = min(LOWEST, len(l100))
    gap = float(l100[1] - l100[0]) if len(l100) > 1 else 1.0
    best = None
    for s in range(0, SMAX + 1):
        if s + n > len(l180):
            break
        r = sum(abs(float(l100[k] - l180[k + s])) for k in range(n)) / n
        if best is None or r < best[1]:
            best = (s, r)
    return best[0], best[1], best[1] / abs(gap), gap


def main():
    specs, nodecells = _load_all()
    windows = sorted({(d["x"], d["parity"]) for _r, d in specs})
    rows, unpinned = [], []
    for x, par in windows:
        h100, e1 = _pick(specs, x, 100, par, "spectrum")
        h180, e2 = _pick(specs, x, 180, par, "spectrum")
        if h100 is None or h180 is None:
            for e in (e1, e2):
                if e:
                    unpinned.append(e)
            continue
        (r100, d100), (r180, d180) = h100, h180
        l100 = [Decimal(r["log10"]) for r in d100["rungs"] if r.get("log10")]
        l180 = [Decimal(r["log10"]) for r in d180["rungs"] if r.get("log10")]
        s, res, res_gaps, gap = offset_fit(l100, l180)
        below = sum(1 for v in l180 if v < l100[0])

        # ---- agreement counts, index-aligned (the old instrument) and eigenvalue-aligned (new)
        n100, en1 = _pick(nodecells, x, 100, par, "nodes")
        n180, en2 = _pick(nodecells, x, 180, par, "nodes")
        agree_idx = agree_aln = None
        pairs = []
        if n100 is not None and n180 is not None:
            a = n100[1]["rungs"]
            b = n180[1]["rungs"]
            k = 0
            for ra, rb in zip(a, b):
                if ra["nu"] is not None and ra["nu"] == rb["nu"]:
                    k += 1
                else:
                    break
            agree_idx = k
            k = 0
            broke = False
            for i, ra in enumerate(a):
                j = i + s
                if j >= len(b):
                    break
                rb = b[j]
                pairs.append(dict(rung100=ra["rung"], rung180=rb["rung"],
                                  nu100=ra["nu"], nu180=rb["nu"],
                                  both_present=(ra["nu"] is not None and rb["nu"] is not None),
                                  equal=(ra["nu"] is not None and ra["nu"] == rb["nu"])))
                if not broke:
                    if ra["nu"] is not None and ra["nu"] == rb["nu"]:
                        k += 1
                    else:
                        broke = True
            agree_aln = k
        else:
            for e in (en1, en2):
                if e:
                    unpinned.append(e)
        rows.append(dict(x=x, parity=par, spectrum_N100=r100, spectrum_N180=r180,
                         local_gap=round(gap, 4), best_offset_s=s,
                         mean_abs_residual_log10=round(res, 6),
                         residual_in_local_gaps=round(res_gaps, 4),
                         N180_rungs_below_the_N100_floor=below,
                         agree_index_aligned=agree_idx, agree_eigen_aligned=agree_aln,
                         aligned_pairs_with_two_values=sum(1 for p in pairs if p["both_present"]),
                         aligned_pairs_equal=sum(1 for p in pairs if p["equal"]),
                         pairs=pairs))

    # depth = 2*min(agreed sector rungs)-1, c53 P6, under BOTH alignments
    depths = {}
    for x in sorted({r["x"] for r in rows}):
        got = [r for r in rows if r["x"] == x and r["agree_index_aligned"] is not None]
        if len(got) == 2:
            mi = min(r["agree_index_aligned"] for r in got)
            ma = min(r["agree_eigen_aligned"] for r in got)
            depths[str(x)] = dict(index_aligned=(2 * mi - 1 if mi > 0 else 0),
                                  eigen_aligned=(2 * ma - 1 if ma > 0 else 0),
                                  offsets={r["parity"]: r["best_offset_s"] for r in got})
    out = dict(
        cycle=57,
        repair="c56 registered it, c57 applies it: align the N-control by EIGENVALUE, not rung index",
        method=("s* = argmin_s sum_{k=1..%d} |log10 lam100_k - log10 lam180_{k+s}|, s in 0..%d; "
                "then recount the agreeing prefix on the aligned pairs" % (LOWEST, SMAX)),
        corpus_rule="content: json with rungs[] and x/N/parity; node cells carry nu, spectra do not",
        spectra=len(specs), node_cells=len(nodecells),
        selection_discipline="every file pinned: sorted corpus, exactly-one assertion per pick",
        unpinnable=unpinned,
        rows=rows, trusted_depth=depths,
        NOT_COMPUTED="p1, p2, p3, the pooled delta sequence -- no call to _first_leave exists here")
    json.dump(out, open(os.path.join(HERE, "m2_c57_aligned_ncontrol.json"), "w"), indent=1)
    print("%-4s %-6s %-8s %-9s %-9s %-7s %-7s %-7s" % ("x", "parity", "offset", "resid/gap",
                                                       "below", "idxagr", "alnagr", "pairs2"))
    for r in rows:
        print("%-4d %-6s %-8d %-9.4f %-9d %-7s %-7s %-7d"
              % (r["x"], r["parity"], r["best_offset_s"], r["residual_in_local_gaps"],
                 r["N180_rungs_below_the_N100_floor"], r["agree_index_aligned"],
                 r["agree_eigen_aligned"], r["aligned_pairs_with_two_values"]))
    print("\ntrusted depth (2*min(agreed)-1):")
    for x, d in sorted(depths.items(), key=lambda kv: int(kv[0])):
        print("  x=%-4s index-aligned %-4s   eigen-aligned %-4s   offsets %s"
              % (x, d["index_aligned"], d["eigen_aligned"], d["offsets"]))
    if unpinned:
        print("\nUNPINNABLE (absent or ambiguous), reported not swallowed:")
        for e in unpinned:
            print("  %s" % e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
