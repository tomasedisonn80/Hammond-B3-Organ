# A37 — Product sanitizer CI coverage

**Actual worker:** `/root/w07_a37_sanitizer_ci_coverage`; wave 7, assignment 37/60.

**Owned:** `.github/workflows/standalone.yml`,
`docs/reviews/PRODUCT_SANITIZER_COVERAGE.md`, this note, and only the approved
sanitizer timeout addition in `apps/standalone/CMakeLists.txt`.

**Basis:** base `b9d352a82ac1afdec70c76ec5b1987785a37762e`, tree
`b3b8b68e4c1f8312d46962924b5096f4ea10c4d2`. Read AGENTS, active checkpoint,
assignments, M0–M9 plan, current navigation and actual test/build wiring.

**Changes:** explicit 21-entry CTest-to-build-target mapping preserves all sixteen
previous native sanitizer gates and adds channel modes, expression calibration,
channel acceptance, product visual and native calibration. The Python lifecycle
suite maps to `hammond_standalone_calibration_probe`; instrumentation now requires
its real entry/adapter sources and audio/replay archives. Discovery verifies
actual command paths and rejects sanitizer overrides. Retained lifecycle evidence
must match the instrumented probe hash, ten subprocesses, seven scenarios and two
deliberate application failures. Captured stderr must contain no sanitizer
diagnostics. A38 caught and I corrected the draft failure-count expectation.

Release required-presence grows 24→31. Native calibration receives only the
approved sanitizer-specific 180-second aggregate limit; ordinary 90 seconds and
per-process 15 seconds remain. Existing product visual 240 seconds, raster budgets,
20-minute job ceiling, leak policy and named core quarantine exception remain.

**Verification:** parsed three YAML workflows, 42 Bash blocks and 13 embedded
Python blocks. Read-only CTest discovery found 48 existing Release registrations;
all 31 required names and 21 mapped commands matched. Existing Release compile
commands/objects confirmed 240 selected translation units, eight new required
source groups, probe define/include ordering and six archive paths. Exact summary
checker accepted retained A26 evidence and rejected six mutations covering count,
hash, missing scenario and ASan/UBSan/LSan diagnostics. Review records exact hashes
and commands. Integrator's concurrent MinGW fixture link option was preserved.

**Boundary/next:** no configure, build, application run, leak-disabled execution,
shared build operation, commit or publication by A37. Existing ptrace/empty-main
failures remain; no local sanitizer pass is claimed. Root publishes the reviewed
workflow and later auditors must retain exact-source instrumentation plus all
21 hosted leak-enabled passes and native evidence before accepting expanded
sanitizer coverage. Physical MIDI and asynchronous driver races remain separate.
