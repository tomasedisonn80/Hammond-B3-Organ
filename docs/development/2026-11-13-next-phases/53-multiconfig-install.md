# Assignment 53 — actual multi-config install and unknown-name repair

Actual agent `/root/w09_a53_multiconfig_install`, assignment **53/60**, wave
**9**, 2026-11-13. The initial spawn tool response was aborted but this canonical
worker started once; no duplicate dispatch is counted.

Read the standing instructions, active scopes/status/handoffs, plan, atlas
review, actual install modules, native install acceptance, benchmark/build
contracts and relevant application replay contract. This M9 packaging task
retains the atlas pp. 391–444 and 450 scope; no physical model or runtime sound
was changed.

## Owned paths and concrete result

Initial ownership was this note and
[STANDALONE_MULTICONFIG_INSTALL.md](../../reviews/STANDALONE_MULTICONFIG_INSTALL.md).
After an actual defect was reported, root explicitly expanded this same
assignment to:

- `cmake/InstallStandalone.cmake`
- `apps/standalone/native_tests/test_standalone_install.py`
- [STANDALONE_INSTALL.md](../../STANDALONE_INSTALL.md)

No other production/test/CMake/shared-status/ledger files were edited. Root
owns commit/push, the combined source gate and later notice changes.

The audit began from published `649b12c7d1faa7601fde1019e913347c65a6634a`, tree
`cf63327d857b02029e8c5c6f406cab3d3c6890d1`, with all 842 tracked source blobs
and modes verified. A fresh private SDL local clone verified the pinned
2.32.10 commit. Ninja was not on PATH; an existing versioned executable was
found, hashed and used explicitly without changing shared tools or installing
packages. Fresh `Ninja Multi-Config` Debug and Release builds succeeded.

## Failure retained and repaired

On the actual multi-config project, selecting declared-but-unbuilt Release
correctly returned 1 and created no prefix. Selecting `NotAConfiguration`
instead returned **0**, copied **eight metadata files**, and omitted the
executable. The per-config target/preflight branches did not match, while
metadata installation still ran. The original logs and incomplete inventory
remain in the private evidence directory.

The repair installs an unconditional Standalone-only guard for an actual
multi-config generator before target-dependent rules. It checks the configured
names without case sensitivity and retains custom configurations, component
exclusion and missing selected-input admission. The maintained test now checks
the actual selected build: an unknown multi-config name must preserve fresh
and existing-sentinel destinations; a single-config build must retain its
complete selected payload. No additional generator prerequisite or skipped
test is introduced.

The original source archive and a complete baseline source copy were retained.
Only the three approved files were then overlaid, inventoried and used to
regenerate the install/test rules. All C++ source, headers, profile inputs,
compiler flags and existing binaries remain byte-identical. Frozen repaired
hashes are:

| File | SHA-256 |
| --- | --- |
| Install module | `5a81d2689300a6fb58cf91a232dcd17c9ffbee209f311471fe5ccde8baed7f19` |
| Maintained install test | `5ff17b66593b4b1b63f0aa193786ab7d38db40ebed6db00c46f2f212537ac9c1` |
| Install guide | `4b49aa3babff92869a07bf67798b84fe179039163ca231db62136dc8329bf9b1` |

## Executed qualification

The review retains full commands, exact identities, payload layouts and runtime
counts. The principal gates were:

| Check | Actual result |
| --- | --- |
| Fresh configure | Pass; CMake/CTest 4.4.4, GCC 14.2.0, Ninja `1.13.2.git.kitware.jobserver-pipe-1`; 20.71 seconds |
| Debug / Release selected-input builds | Pass; 48.26 / 76.57 seconds |
| Original install suites | 1/1 and 1/1; three methods each |
| Repaired install suites | **1/1 and 1/1; four methods each**, 2.88 / 3.10 seconds CTest total; no skips/retries |
| Configuration selection | Exact Debug/Release nine-file payloads; `dEbUg` selects Debug bytes; unknown fresh/existing destinations unchanged on failure |
| Custom declared `Audition` | Case-mixed selection admitted the configured name and correctly rejected its unbuilt executable before writes; no custom-config runtime claim |
| Configuration metadata | Debug `ndebug: false`, Release `ndebug: true`; actual compile flags and distinct executable hashes verified; common nominal profile/fingerprint |
| Custom data paths | Derived DATADIR follows changed DATAROOTDIR; explicit DATADIR survives subsequent root changes |
| Component isolation/coexistence | Ordinary install has 23 OfflineTools files, zero Standalone; explicit addition produces 32 files without changing earlier bytes/modes |
| DESTDIR / COPY | Exact nine-file private staged payload |
| Relocated runtime | Six successful invocations across Debug/Release: help, smoke and actual keyboard replay per configuration |

The ordinary component check initially omitted two required offline trace
targets. Its preflight correctly refused installation and left the destination
absent. Building the specifically named missing targets enabled the valid
check. This retained setup failure is not hidden or described as a product
defect, and no unchanged test was retried to seek a pass.

Only private original source/build/SDL/stage paths were moved for relocation.
The installed executables ran from new Unicode working directories with empty
PATH, explicit dummy audio/video and software rendering. All four window runs
had real callbacks/frames/images, zero errors/audio faults/recovery and a
stopped/no-held final state. Both keyboard runs independently matched all nine
expected held-state transitions and final acknowledgment, with 18 delivered
events and four accepted On/four Off commands. No missing state path was
silently saved. Both installed payloads remained unchanged.

## Evidence and next step

Full logs, 39 recorded command invocations, original/fixed inventories, cache
snapshots, actual compiler commands, runtime JSON and BMPs are retained under
`/workspace/scratch/5ba97739b54c/a53-multiconfig-install/`. All 839 tracked
non-overlay files remained unchanged; the final 844-file repaired inventory
also includes two explicitly recorded generated Python bytecode files.

This audit qualifies the original application binaries plus the narrow
installer/test/guide overlays on Linux Ninja Multi-Config. It does not qualify
later timing/concurrency repairs, additional SDL notices or concurrent
calibration additions. Root must run the new single-config test branch from
the combined source, inspect actual hosted platforms and audit final package
bytes. Physical devices, callback deadlines, accessibility, licensing clearance
and release signing remain separate gates. No commit or push was performed by
this worker.
