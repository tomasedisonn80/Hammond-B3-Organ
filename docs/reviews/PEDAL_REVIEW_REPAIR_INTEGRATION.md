# Independent review repair checkpoint

## Initial Python-repair source freeze and unchanged compiled inputs

Root archived staged tree `a8817841a0a348b6b742dfeb6668249aa9692a54` into
`checkpoint-w09/source`. It includes all accepted assignments 49–54 and the
completed future-agent handoff review 55. The frozen manifest records **55
complete, three running and two planned** slots: 58 distinct dispatched workers,
nine complete waves and the first accepted assignment in the final wave.
Ongoing final-wave reports and later actual states are outside this checkpoint.

An exact Git comparison with fully qualified wave-8 source
`5370890e32045a556cb61a88cdb1f04fb5a18f7e` shows only Markdown changes,
`docs/development/2026-11-13-pedals/assignments.json` and these two Python files:

- `tools/native_bundle_inventory.py`
- `tests/test_native_bundle_inventory.py`

All CMake inputs, C++ sources/headers/tests, SDK lock/notices, profile, routing,
parameter data and runtime fixtures are byte-identical. The wave-8 **71/71
SDK-free** and **8/8 native** local executions retain their exact source scope;
this checkpoint does not claim another complete C++ build or native execution.
Root configured the repaired source separately and generated its nominal
profile before the focused Python checks below.

## Concrete defect and independently observed repair

The [tools audit](PEDAL_TOOLS_EVIDENCE_FINAL.md) demonstrated that ordinary
file/directory mode checks could admit Windows junctions and other reparse
points. The repair reads fresh path metadata before root resolution, directory
traversal and regular-file access, rejecting the reparse attribute explicitly.
Existing symlink/special-file, identity, stability, size, header and no-clobber
publication guards remain unchanged. The old-tool negative control failed all
three intended metadata counterexamples. The repaired tool preserves the exact
inventory bytes of the actual local Linux bundle.

The new regression contains independent root/directory/file metadata cases and
a direct metadata-file reader case. On Windows it additionally creates two
real directory junctions and requires rejection while preserving both targets.
The Linux run explicitly says those native junction operations are not applicable;
local synthetic metadata probes do not establish a Windows pass.

## Actual integrator checks

Three explicit source-archive CLI checks passed:

```sh
python3 tools/check_repository.py --expected-agents 60
python3 tools/check_continuation.py --expected-complete 60
python3 tools/check_pedal_session.py --expected-complete 55
```

The first two retain their own original/console-session scopes. They provide no
completion credit to the new pedal session. The final command validates the
actual frozen 55-complete records.

With the task-local CMake/CTest executables on PATH:

```sh
cmake -S checkpoint-w09/source -B checkpoint-w09/build-python -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build checkpoint-w09/build-python --target hammond_profile
ctest --test-dir checkpoint-w09/build-python -C Release -V --no-tests=error --output-on-failure -R '^python_test_(native_bundle_inventory|pedal_session)$' --output-junit checkpoint-w09/focused-ctest.xml
```

The focused run passed **2/2 CTest suites in 1.62 seconds**, zero failures,
disabled tests or skips: **20 inventory methods plus 24 session-checker methods**.
The actual initial regex also listed `repository` and `continuation` alternatives;
those are not registered under those exact Python names, so it selected only
the two suites shown here. No four-suite pass is claimed. The repository and
preceding-session gates were executed explicitly as the separate CLI commands
above. Full exact arguments, exits and process timings are retained in
`checkpoint-w09/focused-results.json`.

| Retained local evidence | SHA-256 |
| --- | --- |
| ctest.log | `7f6bed292ba9e34dbe4d82915793f4d17f5c3547c719c486e2c6cab9c715a0fd` |
| focused-ctest.xml | `da94d187dd940b7861a09d84b7616ae5d778ba7dfc02c33ae2bfa929b8d57795` |

That initial publication was prepared but held before updating `main` while
the previously requested macOS retries completed. The successful core retry
and concrete native test-build failure below required one additional test-only
repair. The manifest and both repaired Python files retain the exact bytes
qualified above; the final source delta is explicitly extended below.

## Actual macOS retry and test-harness repair

At wave-8 commit `d601eb166ea3206748f8e012b20a463ff365c0b1`, core retry job
[131867709274](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681825/job/131867709274)
passed **71/71 suites and 548 Python methods**, zero failures, disabled tests
or skips, in 57.99 seconds. Native retry job
[131867718865](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43417681882/job/131867718865)
acquired a real runner but failed compilation: its Apple standard library does
not provide `std::jthread` and `std::stop_token`, used by the concurrency test.
It did not reach native CTest, inventory or bundle publication. The failure
diagnostic artifact is 14034960204; its ZIP SHA-256 is
`ad398d869dccef4cf895ac57725446d10d4fb6bfeec0fa794876fecb8b24a3a4`.

The repair changes only `plugins/vst3/tests/test_native_concurrency.cpp` among
C++ files. A nonmoving test-local thread owner keeps an atomic stop flag alive
until its worker is joined. Destruction requests cooperative stop and joins;
ordinary explicit joins and all production/workload/oracle boundaries remain
unchanged. An exception-unwind probe verifies that the worker observes stop and
has finished when destruction returns. No production processor, core, SDK,
CMake, profile or fixture input changes.

The exact repaired source is Git tree
`81a1c466efdec3efe5c1d9af1e1663eb101dacde`: the initial qualified tree above
plus the single test blob `a9503d93c30a0f4fc75c2f83e3c0586a0f73417f`.
Root independently compared all **549 tracked file bytes and modes** with the
fresh build's source. Two generated Python caches appeared after configuration;
they were separately hashed and retained, not counted as tracked source.
The repaired C++ file is 27,431 bytes, SHA-256
`d261ad69d0199cd5da4a9b2f050a7416b2c515c7838f8f26d3a036c9c8b8f0cc`.

Assignment 59 performed a fresh GCC 14.2/CMake 3.31.6 native configuration,
built the concurrency executable and all required dependencies, then ran:

```sh
ctest --test-dir a59-final-platform-audit/repair/build -C Release -V --no-tests=error --timeout 240 -R '^test_native_concurrency$' --output-junit a59-final-platform-audit/repair/ctest.xml
```

Actual result: **1/1 passed in 0.33 seconds**, zero failures, disabled tests or
skips. The cleanup probe printed `stop_observed=1 worker_joined=1`; the existing
three-rate workload completed 24 controlled rounds, 3,072 accepted stress loads,
3,072 publication-only saves, 96 reader-pause callbacks and 6,168 future frames,
with maximum audio error zero. This execution compared 64,207 audible frames;
stress scheduling counters are observations, not fixed timing guarantees.

| Additional retained local evidence | SHA-256 |
| --- | --- |
| Native repair configure.log | `c766d561081cb227a1f61fcb0478ed99cceeb47de785806b52a28c9fadc72f69` |
| Native repair build.log | `b10c5de29a5c267ef53701856cbf88fc62821a111d5381560d14017fa9af1478` |
| Native repair ctest.log | `2f79b1776352afd1eed619cb2d43848eb8df101c4f6ac2a2ee2c6b5ca123c9ab` |
| Native repair ctest.xml | `2dccfe00910d959cd6c3488d1cbf2fd7f413791b20e08d0f095a088d41419c9f` |

Root's source-proof setup first attempted to construct a Git tree before storing
the already identified blob, then initially rejected the two generated caches
under an overly strict file-set assertion. Both stops occurred before any root
test execution. Storing the exact blob and preserving/hashing the caches
separately allowed the full tracked-source proof to pass. Receipts are retained
in `checkpoint-w09/mac-repair-source-proof.json`; no source was silently removed.

Final publication differs from tree `81a1c466…` only in Markdown result records.
Publication uses an expected-parent reference update and fetched exact-tree
verification. The changed Python regression and test helper still require
their actual Windows and macOS hosted executions at the published revision.

## Platform and final handoff gates

The [wave-8 hosted audit](PEDAL_HOSTED_WAVE8_FINAL.md) records successful actual
Linux/Windows core and native execution, sanitizers and downloaded artifacts.
Its initial two macOS jobs failed hosted-runner acquisition and executed no
steps. Root subsequently requested one targeted retry each; their actual core
success and native compilation failure are recorded above. The new repair
publication requires its own observed results.

For this repaired source, inspect the actual Windows JUnit/log output for:

```text
reparse probes: root/directory/file metadata and 2 actual Windows junctions
```

The next exact-source hosted audit must retain every actual job/artifact outcome,
including unexecuted or cancelled jobs. Complete the remaining final reviews,
run the new session's explicit sixty-complete gate only after acceptance of all
sixty real workers, and publish the final current status/next-task handoff.
The [scanner gate](../M3_REMAINING_AND_SCANNER_GATE.md) remains the first next
product task; no scanner runtime or physical calibration is claimed here.
