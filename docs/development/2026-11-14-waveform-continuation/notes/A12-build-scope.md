# A12 — R4 build, test, install and CI scope

Actual worker `/root/w02_a12_build_scope`, wave 2 of the current waveform
continuation. Owned only this note and
[WAVEFORM_BUILD_PLAN.md](../../../WAVEFORM_BUILD_PLAN.md). No product, CMake,
workflow, fixture, shared build, existing evidence, Git index or commit was
changed. No nested workers were created.

## Source and setup inspected

Observed HEAD: `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`. This includes the
preceding `f9c11a498ecd88886349415205fc5dccc627033e` integration. At inspection,
`RotaryHistory.h`, `RotaryRenderer.h`, `RotaryStreamingPath.cpp`, the R4
contracts and independent reference header were uncommitted; history and
renderer implementations were still pending. Concurrent native
`InstrumentView.cpp` work and other agents' notes were preserved.

Read standing instructions, the complete M0–M9 plan, current waveform
scope/checkpoint/assignments, current status/next-step/log sections, the R4
renderer and numerical acceptance contracts, both new headers and relevant
existing rotary types. Audited root/standalone CMake, the three component install
helpers, all three workflows' build/test/artifact paths, private install source
fixtures, probe/environment conventions, native capture source/build inventories
and the preserved Windows allocation-fixture record. The complete-atlas review
is the preceding six actual workers' evidence; A12 did not claim another full
PDF reading.

The session build cache is Release/Ninja, GCC 14, standalone ON, MIDI OFF,
VST3 OFF and sanitizers OFF. CMake is reused from
`/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake`; the ordinary
PATH omission is a retained setup fact. The locked SDL2 source is reused at
`/workspace/scratch/1bb6ee17ad7e/SDL2`, with `SDL_ALSA=OFF` in the baseline.
A12 read this cache and existing reports only; no shared build was run.

Selected audited file identities, before any integrator applies the plan:

| File | SHA-256 |
| --- | --- |
| `CMakeLists.txt` | `a1865e59816ed4a63c9a0d8ed95c9aaea1951960f969fe209a3309cc3f2f99e7` |
| `tests/test_capture_install.py` | `09b46e89620b7102d1271acec263603c4b0c1e384433605b5a0cad2ac2655d68` |
| `tools/capture_standalone_interface.py` | `92ae0be31a6ef21eb696c87d4f9dacd8ea8a6732d6c1033e0d7457ca3a76d16b` |
| `.github/workflows/ci.yml` | `dff4199953804baf7f6bab50f5642952ef0fb407baec6968a0c5d96396a884c3` |
| `.github/workflows/standalone.yml` | `d43c847855e375936c15b68731031ce37393b93b073173e67b1c8e8f67075610` |
| `.github/workflows/native-vst3.yml` | `2376f41bfd96ff5afa2c821299588de05e5c49221879aef91a82074955649721` |
| `include/hammond/RotaryHistory.h` | `9e6930342a5c83bdcf99102aaeb0dc9b0714e85561bd8205a53155a7fca4a25b` |
| `include/hammond/RotaryRenderer.h` | `5f74af0a7ca629b433fe7f3d72a44a2b39daf90fd2d64afa579aecd26f48ccd0` |
| `tests/reference/rotary_waveform_reference.h` | `3c24792f80f86f903926622f4bf016984caf44d727ad3913e4570738ac9c8f21` |

## Findings delivered

- Core sources and ordinary root behavior tests already use
  `CONFIGURE_DEPENDS` globs. The explicit additions are
  `hammond_rotary_waveform_probe`, its exact per-configuration Python
  environment, the separately invoked full gate and the future A25
  `hammond_rotary_render` target. The integrator supplied these proposed stable
  names during this assignment.
- `PrivateProject` now copies all `tests/probes/`, preserving the earlier fix;
  it still omits `tests/reference/`. The proposed probe lists that oracle header
  explicitly, so copy the reference directory in the same integration change.
  New `src/` and `include/` inputs are already copied. The other install
  fixtures use imported/stub targets and need no R4 source inventory change.
- New history objects and complete rollback snapshots must live on the heap.
  On the common current ABI a waveform plus motion payload alone is 1 MiB,
  before metadata; actual `sizeof` values remain to be recorded. Existing A38
  shows the real preceding fixture's stack pressure and qualified Windows
  failure; increasing `/STACK` would hide the new design issue.
- All new targets retain C++20, strict warnings, sanitizer linkage and portable
  Unicode CLI handling. Record actual floating precision/contraction policy;
  no extra `long double` precision is inferred on MSVC.
- Full acceptance covers 3,801,000 reference frames and six complete native
  block patterns. The recommended fast CTest smoke and explicit full target/job
  prevent redundant million-sample JSON/process work while retaining the entire
  frozen gate. Proposed time limits are visibly unmeasured. Source/executable
  stability, complete grid/failure records and bounded artifact storage are
  part of the runner contract.
- Existing standalone and VST3 workflow filters do not run R4. Keep their
  application qualification separate; the native sanitizer list still contains
  exactly 16 interface targets. No new dependency, Engine route, parameter,
  state field or installer payload is needed.
- Preserve the exact five-tool OfflineTools and 57-file CaptureTools inventories.
  A25's demonstration is a build-tree research tool until its CLI/file policy
  is reviewed. No fabricated future render command or installed-tool claim is
  supplied. Native capture already hashes new core/header files recursively,
  so coherent rebuild and a production-source freeze precede new screenshots.

## Verification and retained limits

This was a source/contract audit and documentation change. Inspection commands
used `rg`, bounded file reads, `git status --short`, `git log`, Python SHA-256
calculations and direct reading of the current build cache. No new compilation,
runtime test, install or hosted job was executed by A12. The final documentation
check verifies local link destinations, trailing whitespace and complete code
fences in the two owned files; it does not qualify the proposed CMake snippets.

Read [baseline.json](../reports/baseline.json): 155/155 tests passed in
152.15 seconds at `2e161dc`, before the new R4 API. Read the unchanged
[remote-integration output](../reports/wave1-remote-integration.txt): 3/3 passed
in 2.80 seconds after `f9c11a4`, specifically
`test_rotary_propagation_allocation`,
`python_test_capture_standalone_interface` and
`python_test_repository_integrity`. These existing observations are not A12
test executions or R4 implementation evidence.

The next concrete integrator action is to freeze the reviewed API, complete the
three production implementations and probe/runner, then apply the root CMake
and private-copy changes together. Build actual consumers before discovering
and running the named CTest gates; run the explicit full comparison separately,
retain its real timing and complete artifacts, then perform the coherent full
suite and platform jobs. A25 supplies the offline input/output policy before
the demo target and its real invocation can be finalized. R5, R6 device
integration and physical M7 remain separate gates.
