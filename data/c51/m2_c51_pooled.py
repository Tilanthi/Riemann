#!/usr/bin/env python3
"""m2_c51_pooled.py -- PRESENTATION ONLY. Not sealed, scores nothing, decides nothing.

It merges this cycle's two sector cells per window into the pooled ladder c50's letter tabulated,
and applies c50's completeness certificate: holding the k smallest of EACH sector certifies the
pooled ORDERING only up to T = min(lambda_even[k], lambda_odd[k]); rungs above T are printed but
marked UNCERTIFIED. Every verdict in this cycle is the sealed grader's (m2_c51_score.py); this file
exists so the letter's tables are generated rather than typed.

usage: m2_c51_pooled.py
"""
import json, os, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
WINDOWS = [(5, 100, 5), (13, 100, 7), (13, 180, 5), (19, 100, 5)]


def main():
    lines = []
    for X, N, K in WINDOWS:
        cells = {}
        for par in ("even", "odd"):
            fn = os.path.join(HERE, "m2_c51_nodes_%s_x%d_N%d_k%d.json" % (par, X, N, K))
            if not os.path.exists(fn):
                break
            cells[par] = json.load(open(fn))
        if len(cells) != 2:
            lines.append("x=%d N=%d k=%d: cells missing, skipped" % (X, N, K))
            continue
        pool = []
        for par, c in cells.items():
            for r in c["rungs"]:
                pool.append((Decimal(r["log10"]), par, r))
        pool.sort()
        # completeness certificate: T = min over sectors of the LAST computed eigenvalue
        T = min(Decimal(cells[p]["rungs"][-1]["log10"]) for p in ("even", "odd"))
        lines.append("")
        lines.append("x=%d  N=%d  k=%d per sector   certificate T = log10 lambda %s "
                     "(pooled order certified at or below T)" % (X, N, K, T))
        lines.append("  pooled | sector | sector rung | log10 lambda | nodes | m-1 | pooled defect | "
                     "admitted | certified")
        order = []
        for i, (lg, par, r) in enumerate(pool):
            m = i + 1
            cert = lg <= T
            order.append(par[0])
            lines.append("  %6d | %-6s | %11d | %12s | %5s | %3d | %13s | %8s | %9s"
                         % (m, par, r["rung"], str(lg)[:12], r["nu"], m - 1,
                            ("" if r["nu"] is None else r["nu"] - (m - 1)),
                            r["admitted"], cert))
        certified_prefix = sum(1 for (lg, p, r) in pool if lg <= T)
        adm_cert = sum(1 for (lg, p, r) in pool if lg <= T and r["admitted"])
        lines.append("  pooled parity order: %s" % "".join(order))
        lines.append("  certified pooled prefix: %d of %d computed; of those admitted: %d"
                     % (certified_prefix, len(pool), adm_cert))
    out = "\n".join(lines)
    print(out)
    open(os.path.join(HERE, "m2_c51_pooled.out"), "w").write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
