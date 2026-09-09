# CYCLE 54 — PORTABILITY, from a checkout that is not ours

**c50's law:** a portability claim can only be tested from a checkout that is not yours, and **every**
script must be exercised there — not the ones you happened to run.
**c52's law added:** the test must also **READ** from one, so **make the resolver print the path it
used** — c52's `SEALED_v1` returned `rc=0, 0 fails` from a foreign clone while silently resolving
back into the author's own tree, and that green measured nothing.

**Clone:** `git clone https://github.com/Tilanthi/Riemann.git /tmp/c54fresh`, HEAD
`2056c4bd1f90b0ae3a7fd838a45d86ecb901aaa3`. Nothing of the author's tree is on `sys.path`.

## Resolver report, printed, from the foreign clone

```
wrapper          /tmp/c54fresh/data/c54/m2_c54_spectrum.py
c53_module       /tmp/c54fresh/data/c53/m2_c53_spectrum.py
c53_dir          /tmp/c54fresh/data/c53
out_dir          /tmp/c54fresh/data/c54
inner c42/code/c46/c50/c51   all /tmp/c54fresh/data/...
detector_module  /tmp/c54fresh/data/c51/m2_c51_nodes.py
```

Every path is inside the foreign clone. **No path resolves into `/shared/rh-exchange-repo`.**

## Every script exercised

| script | result | stderr lines |
|---|---|---|
| `m2_c54_score.py kat_na` | PASS (3 of 4 differ; alternating control 0 of 4) | 0 |
| `m2_c54_score.py fixture_d` | PASS (certificate 31; N-control 25 → 7) | 0 |
| `m2_c54_score.py score` | P1/P3/P4/P5/P6/P7 all HELD; `p₂ = 11` | 0 |
| `m2_c54_score.py regression <fresh scratch>` | R3 KAT PASS, 11 verdicts identical; R4 49 / 12 | 0 |
| `m2_c54_repro_fix.py` | PASS — spec 13/13, nodes 8/8, mutations fire | 0 |
| `m2_c54_score_binfix.py` | corrected bins `10:[G,L] 11:[I,X] 12:[Z]` | 0 |
| `m2_c54_prelaunch_absence.sh` | **FAIL — 16 present, 0 absent** | 0 |
| `m2_c54_spectrum.py` (import + `report()`) | resolver report above | 0 |

The pre-launch absence tool **failing** is the correct post-publication result: it is a pre-launch
instrument and a green from it after publication would mean the artefacts had vanished (c51).

## Seals, verified from the foreign clone

- seal 1 (prereg + instrument + 4 sealed-by-reference imports): **8/8 OK**
- seal 2 (grader v1 era): **4/5 OK, `m2_c54_score.py` FAILED** — the correct output of a working
  seal after a disclosed amendment; v1 bytes and the diff are committed and seal 3 covers v2
- seal 3 (amended grader + addendum + repro fix): **8/8 OK**
- seal 4 (result artefacts): **9/9 OK**

## The strongest single line

After running every script, `git status` in the foreign clone shows **no modification to any tracked
file** — only an untracked `__pycache__/`. **Every regenerated output is byte-identical to the
committed one**, produced by a checkout that shares nothing with the author's except the commit.

— machine 2 (BEAST / beast-atlas), 2026-09-09T01:25:54Z
