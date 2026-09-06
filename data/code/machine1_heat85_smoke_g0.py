"""m1 heat85 launch-2 RED -> re-freeze-2: the full-path smoke #143 now demands.

Launch-1 crashed at an import py_compile never executes; launch-2 crashed at a
runtime NameError (fabs, G4 line) that NEITHER py_compile NOR the launch-1-class
import-smoke can see, because it sits in a branch only reached after 21 real
eigensolves.  The amended rule: before any hash is frozen, EXECUTE THE WHOLE
RUNNER with the expensive primitive stubbed, so every branch of main() --
both abort paths and the WROTE path -- runs at least once.

Stub: census.Instrument.eig is replaced (class attribute; the runner builds its
Instrument from the same imported module object, so the patch binds).

  stage A (GATE-FAIL path): eig always returns mpf("1e-11").
      G1 stays green; every founder match fails; G4 not detected ->
      the runner must json.dump the gate dict and sys.exit("GATE FAIL ...").
  stage B (WROTE path): a queue of 52 typed values in the deterministic call
      order (8 controls + 12 founders at their exact census lam values + 1 G4
      defect value + 31 mutants alternating fires/survives) -> the runner must
      reach WROTE, and the dumped JSON must carry gate + 31+9 cells.

Both stages redirect the runner's OUTJ to a scratch path; the real OUTJ is
never touched, seals verify against the real files, and no value produced here
is a measurement -- the stub bypasses the eigensolver entirely.

Receipt stdout is committed as machine1_heat85_smoke_g0.out.
"""
import importlib.util
import json
import os
import sys

from mpmath import mp, mpf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
mp.dps = 45

RUNNER = os.path.join(HERE, "machine1_heat85_charter_pilot_g0.py")
SCRATCH_A = "/tmp/heat85_smoke_g0_stageA.json"
SCRATCH_B = "/tmp/heat85_smoke_g0_stageB.json"


def load_runner():
    spec = importlib.util.spec_from_file_location("heat85mod", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)   # module level only: imports + constants
    return mod


def main():
    mod = load_runner()
    import machine1_heat78c_survivor_census as census
    cj = json.load(open(os.path.normpath(
        os.path.join(HERE, "..", "heat78c_census_result.json"))))["results"]

    # ---- stage A: the GATE-FAIL branch -------------------------------
    census.Instrument.eig = lambda self, KS: ([mpf("1e-11")], None)
    mod.OUTJ = SCRATCH_A
    print("stage A (stub eig = 1e-11 always): expect GATE FAIL + abort json")
    try:
        mod.main()
        print("stage A FAIL: main() returned without abort")
        return 1
    except SystemExit as e:
        print("stage A SystemExit: %r" % (e,))
    j = json.load(open(SCRATCH_A))
    okA = (j.get("aborted") == "gate failure (G2/G3/G4)"
           and j["gate"]["G2_founders_reproduced"] is False
           and j["gate"]["G3_kill_controls_fired"] is False
           and j["gate"]["defect_injection"]["detected"] is False)
    print("stage A abort json: aborted=%r g2=%r g3=%r detected=%r  ->  %s"
          % (j.get("aborted"), j["gate"]["G2_founders_reproduced"],
             j["gate"]["G3_kill_controls_fired"],
             j["gate"]["defect_injection"]["detected"], "PASS" if okA else "FAIL"))
    if not okA:
        return 1

    # ---- stage B: the WROTE branch -----------------------------------
    queue = [mpf("1e-11") for _ in range(8)]                       # G1 k=0..7
    for (k, d) in mod.FOUNDERS_S + mod.FOUNDERS_F:                 # G2/G3 exact
        queue.append(mpf(cj["64/%d/4/%s" % (k, d)]["lam_min"]))
    queue.append(mpf("-1e-6"))                                     # G4: rel ~2e4 > 1e3
    for n in range(len(set(mod.MUTANTS))):                         # 31 mutants
        queue.append(mpf("1e-11") if n % 2 == 0 else mpf("-3e-11"))
    print("stage B (queue of %d typed values): expect WROTE + full json" % len(queue))

    calls = []

    def qeig(self, KS):
        calls.append(1)
        return ([queue[len(calls) - 1]], None)

    census.Instrument.eig = qeig
    mod.OUTJ = SCRATCH_B
    import io
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            mod.main()
    except SystemExit as e:
        print("stage B FAIL: main() aborted: %r" % (e,))
        return 1
    tail = [ln for ln in buf.getvalue().splitlines() if ln.startswith("WROTE")]
    print("stage B stdout tail: %r" % (tail[-1] if tail else "<no WROTE line>"))
    j = json.load(open(SCRATCH_B))
    ncells = len(j.get("cells", {}))
    okB = (bool(tail) and "aborted" not in j
           and j["gate"]["controls_status"] == "GREEN"
           and j["gate"]["G2_founders_reproduced"] is True
           and j["gate"]["G3_kill_controls_fired"] is True
           and j["gate"]["defect_injection"]["detected"] is True
           and j.get("n_mutants") == 31 and ncells == 40)
    print("stage B json: controls=%s g2=%r g3=%r detected=%r n_mutants=%r cells=%d"
          "  ->  %s" % (j["gate"]["controls_status"],
                        j["gate"]["G2_founders_reproduced"],
                        j["gate"]["G3_kill_controls_fired"],
                        j["gate"]["defect_injection"]["detected"],
                        j.get("n_mutants"), ncells, "PASS" if okB else "FAIL"))
    print("eig calls made: %d (queue %d)" % (len(calls), len(queue)))
    return 0 if (okA and okB) else 1


if __name__ == "__main__":
    sys.exit(main())
