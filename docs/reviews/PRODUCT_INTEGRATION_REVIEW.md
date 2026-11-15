# Product integration and portable fixture review

Actual reviewer: `/root/w07_a38_integration_review`, A38, wave 7,
15 November 2026 UTC. This review inspected the integrated target graph,
generated build inventory, feature boundaries and retained failures. Root
authorized two narrow fixture repairs after the hosted failures were observed;
root retained exclusive configure/build/CTest ownership.

## Decision and source boundary

The component and native fixture have the intended separation from the shipped
application. Three observed portability failures needed correction: the
installer's policy-dependent ancestor loop, borrowed SDL environment strings in
the calibration driver, and a Windows stdout/file newline comparison. Those
repairs preserve the existing negative and lifecycle assertions. A further
source-only MinGW startup omission was corrected by root. No production MIDI,
Engine, painter, reference-model or saved-state source changed in these repairs.

Root's rebuilt local repair gate passed **2/2 in 21.92 seconds**: crossover
installation in 1.47 seconds and native calibration in 20.44 seconds. This is
Linux GCC 14.2 Release with CMake 4.4.5, MIDI OFF and SDL dummy devices. It does
not replace Windows or CMake 3.31.6 execution. The
[focused CTest log](../development/2026-11-15-product-continuation/reports/wave7-portability-repair-ctest.txt)
and [native summary](../development/2026-11-15-product-continuation/reports/A38-root-native-calibration.json)
retain the actual result.

The reviewed base is published
`b9d352a82ac1afdec70c76ec5b1987785a37762e`, tree
`b3b8b68e4c1f8312d46962924b5096f4ea10c4d2`, plus the following inspected
wave-7 source overlay. These hashes identify the reviewed overlay, not a claim
that it was already committed or hosted-qualified.

| Source | SHA-256 |
| --- | --- |
| `CMakeLists.txt` | `36c17341aae955e55a482f6434ee563d4646a76027252797d53945e470d48aa2` |
| `apps/standalone/CMakeLists.txt` | `772f75acd307d955cd632afc01ec7c5221859aa997aa97bd4d108a69deafc94c` |
| `.github/workflows/standalone.yml` | `8049819e4383dfa13e28622678a7d457e6d1165198ca4b6579173b4c174b1d59` |
| `cmake/InstallCrossoverTools.cmake` | `20ee5ff15a55e3ba2d652da4360aa647adfa8ca55a7f947a1f127ade98bc7844` |
| `tests/test_crossover_install.py` | `8daf656ad24f812d9d11920c35c846ec46d344e4b7fc78ed330ae9f764ffcd03` |
| `apps/standalone/native_tests/calibration_lifecycle_driver.cpp` | `e33b17f3f9642d17e21e5d645f8f3d82a176ca030b78164521af2e530ce57dd6` |
| `apps/standalone/native_tests/fake_calibration/RtMidi.h` | `0cdd03fdca2bf65bad6ff1b0d5043a85950fe841b5bc76cb5bb8e2df8402710f` |
| `apps/standalone/native_tests/test_standalone_native_calibration.py` | `e4d2d86501582d9ee612b7c110144b595b0bbe85427c86000403a7a955f98e85` |

The feature source `ff41d412` retains its separate 176/176 local result and 13
successful hosted job statuses. Those results do not qualify the later b9
fixture/install additions or the repaired overlay. Original b9 failures remain
preserved below.

## Concrete findings and repairs

### A38-1: installer ancestor guard depended on an unset policy

The b9 Linux Release job `132659897764` used CMake 3.31.6 and failed one of 155
CTest entries. Its three failing installation subcases exposed actual writes
through a linked binary parent/prefix or mutation before rejection of a file
package parent. The [primary excerpt](../development/2026-11-15-product-continuation/reports/b9-linux-crossover-install-failure.txt)
shows `while(TRUE)` skipped with CMP0012/CMP0130 diagnostics in generated
`cmake_install.cmake`. Configure-time `cmake_minimum_required` did not establish
that install script's policy scope.

Root changed only the loop truth value to numeric `while(1)` and explained the
scope distinction. Numeric 1 is accepted by both old and new CMP0012 behavior;
the parent traversal, refusal predicates, stop-at-prefix/root conditions and
all 14 fixture tests remain intact. The earlier
[repair record](../development/2026-11-15-product-continuation/reports/crossover-install-policy-repair.json)
retains the original 14/14 CMake 4.4.5 recheck in 1.370 seconds separately from
the later combined repair gate. A pass on CMake 4.4.5 cannot reproduce the old
unset-policy behavior; replacement hosted execution remains required.

### A38-2: native calibration fixture retained invalidatable SDL pointers

The b9 Windows native job `132659898014` failed one of 48 standalone CTest
entries: eight of nine calibration fixture cases returned exit 2 before app
startup. The [retained failure](../development/2026-11-15-product-continuation/reports/b9-windows-native-fixture-failure.json)
contains the scenario/trace refusal and actual case list.

The driver obtained `selected` and then `trace` as borrowed `SDL_getenv`
pointers. In pinned SDL2 2.32.10's `src/stdlib/SDL_getenv.c`, the Windows fallback
returns shared reallocating `SDL_envmem`. The second call can overwrite or
invalidate `selected`; subsequent application environment reads can invalidate
`trace` before final trace output. Inspected dependency-source SHA-256:
`8a994b90496382d4b23084269e53bcba876d4218852724318c40b98e9a7519a9`.

Under root's expanded ownership, A38 now copies each result immediately into
`std::string`, before the next environment lookup, and retains both owners
through `guarded_application` and trace writing. Missing, empty and unknown
scenario refusal remains unchanged. Production `main.cpp`, `MidiDevice.cpp`
and the fake dependency are untouched. The repaired local probe SHA-256 is
`16da718ff92bdd940a6e457f100b08b54098dbd4183fd149f9a4b137460b4335`.

### A38-3: installation test compared different text-stream representations

The b9 Windows core job `132659897861` had the same three install-policy
failures plus an LF-versus-CRLF report assertion. The
[retained excerpt](../development/2026-11-15-product-continuation/reports/b9-windows-install-newline-failure.json)
shows 14 fixture cases, four failing subcases and one POSIX DESTDIR skip.

The reference's atomic writer explicitly uses `newline="\n"`; redirected
Python text stdout uses Windows line endings. A38 changed only the fixture's
comparison: on Windows, replace stdout CRLF pairs with LF before comparing
the exact report bytes. Other platforms retain the original byte comparison.
This preserves JSON text, ordering, values, escaping and the complete report;
it does not reduce the assertion to a subset of fields. All output protection,
no-partial-report, unchanged-input and destination-preservation assertions remain.
The reference itself retains SHA-256
`33eaa88da2534e52f88c044b5fbabf19828655bacb357dc55bbeb6510b580ec5`.

### A38-4: calibration probe lacked the existing MinGW wide-entry option

Source inspection found that the fixture defines `wmain` under `_WIN32`, while
only the production application received `-municode`. Root added the same
conditional link option specifically to `hammond_standalone_calibration_probe`.
The change was observed in the reviewed CMake hash above. This is a source
correction; no MinGW compiler execution or new supported-platform claim follows.

## Actual target and test inventory

A38 read `CMakeCache.txt`, `compile_commands.json`, `build.ninja` and CTest's
JSON inventory in `/workspace/scratch/5b7d983ac078/build-native`. The configured
tree uses Ninja, Release, `BUILD_TESTING=ON`, standalone ON, VST3 OFF, MIDI OFF,
sanitizers OFF, and SDL X11/Wayland/ALSA OFF. Read-only discovery used:

```sh
/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/5b7d983ac078/build-native \
  -C Release --show-only=json-v1
```

It discovered **178 entries**: 48 `test_standalone_` names, 74 `python_` names
and 56 other entries. Discovery is not a 178-test execution result. The two
new entries are `python_test_crossover_install` and
`test_standalone_native_calibration`; both are enabled. Their ordinary Release
timeouts are respectively 120 and 90 seconds. A37's native calibration timeout
of 180 seconds applies only to sanitizer configurations.

| Build surface | Integrated contract and observed separation |
| --- | --- |
| Default core/support | The core and independent crossover probe need no SDL, RtMidi or VST3 SDK. Host-independent standalone support links core and `Threads::Threads`; its desktop fake-backend tests need no physical MIDI SDK. All optional product/backend flags default OFF. |
| Ordinary native app | SDL enters only with standalone ON. The app compiles `main.cpp` and `InstrumentView.cpp` and links audio, replay, drawing and support archives. Its generated compile commands contain no calibration fake include. MIDI OFF compiles the support `MidiDevice.cpp` with `HAMMOND_HAS_RTMIDI=0`. |
| Calibration test input | Only standalone + testing on desktop Linux, Windows or Darwin creates the probe. It recompiles the unchanged adapter with a private, first-priority fake include and `HAMMOND_HAS_RTMIDI=1`. The driver includes unchanged `main.cpp` under renamed entry points. Its linked real audio/replay/drawing/support/core/SDL archives match the generated graph. Thread support is inherited through the support library's public dependency. |
| Required build aggregates | `hammond_standalone_test_inputs` and root `check` include the calibration probe and profile. Root `check` also builds the crossover probe needed by its Python install gate. The app has no dependency on either calibration fixture source or its executable. |
| Manual paint measurement | `hammond_standalone_paint_benchmark` is a separate native target. It is not a CTest timing gate and does not establish a callback deadline or interactive frame rate. |
| Optional VST3 | The SDK lock and explicit flag still guard the native module. `hammond_vst3_test_inputs` builds module, validator and ABI inputs; no calibration fake or standalone backend is introduced into that plugin target. |

The production app remained
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`;
the crossover probe remained
`da09640f7520cd887a836961658ed8a79d6b6bff28f0e33a0ce44cf76f992eac`.
These are identities, not substitutes for execution evidence. No calibration
fixture or fake-backend payload appears in the four component installers.

## What the native calibration fixture actually covers

The shared fake state has a bounded 4096-event log. Both discovery and live
clients access that state under one mutex; the installed shared pointer is set
before application startup and reset only after application destruction has
joined discovery and stopped audio. Final trace traversal therefore occurs
after those clients finish. The original production `MidiDiscovery` join and
`MidiDevice` close/cancel paths remain in use.

Callback offers run synchronously inside fake native API calls on the app
thread. The tests explicitly require that fact, require real worker-thread
discovery, and require nonzero actual SDL dummy audio callbacks and rendered
images. This exercises the native lifecycle across real app/audio threads, but
does not simulate an asynchronous operating-system MIDI callback race.

The repaired summary contains nine tests, ten actual subprocesses and seven
native lifecycles: identical Apply; changed calibration; changed route; changed
exact port; no-input configuration followed by connection; failed reopen with
explicit retry; and runtime fault with explicit retry. Both negative replays
deliberately return failure and retain their history. The suite observes
selected/configured/pending/active distinctions, three-owner release
acknowledgment before reopening, no Apply-generated expression change, the next
CC11 result, discarded failed prefixes and survival of the unrelated UI owner.
Every opened client closes, cancels and is destroyed in the required order;
close-time offers are counted but refused by retired admission.

Failed-close quarantine, real driver scheduling, physical devices, thread-race
instrumentation and callback deadlines are outside this fixture. The existing
separate backend quarantine gate retains its named leak exception; the new
calibration gate introduces none.

## Install preflight and component isolation

[`InstallCrossoverTools.cmake`](../../cmake/InstallCrossoverTools.cmake) follows
the shared relative-directory validator and makes every install rule explicit
`CrossoverTools` + `EXCLUDE_FROM_ALL`. The payload is exactly the selected
executable plus reference script, registry, two documents and notices. Default,
OfflineTools, Standalone, CaptureTools and NativeVST3 dispatch do not acquire
this payload. The private test's unrelated components are sentinels; its
component-dispatch proof is supplemented by direct inspection of the real
component declarations, not described as a complete reinstall of every product.

The remaining generated crossover conditions use explicit filesystem predicates,
numeric size/configuration comparisons and string comparisons. No second
CMP0012-dependent truth literal was found there. Multi-config admission precedes
all unconditional metadata; selected generator expressions identify the actual
probe. All six nonempty nonsymlink inputs and both destination leaves/ancestors
are checked before copying. Relative-directory validation rejects parent
traversal, absolute/drive-prefixed paths and list separators; DESTDIR is included
in the inspected prefix. Unknown multi-config names cannot leave metadata-only
packages. Existing package/probe destinations are refused instead of merged.

The suite checks copies, exact inventory, source-independent relocated native
and reference execution, custom paths, negative input/destination cases and
component isolation. It intentionally uses private copies of the selected
Release artifact for multi-config dispatch; that is not a Debug compilation.
Symlink availability, POSIX DESTDIR and generator availability have explicit
platform skip boundaries. These preflight checks assume quiescent paths and
do not supply atomic six-file rollback or runtime-library collection, as the
[install contract](../CROSSOVER_INSTALL.md) states.

## Feature, Engine and plugin compatibility

Direct byte comparisons against pre-feature `af006b0a` confirmed unchanged
`Engine.cpp/.h`, `ParameterBridge.cpp/.h`, `ControlStateIO.cpp`, plugin IDs and
the nominal profile. The feature delta introduces the standalone typed command,
decoder/settings behavior and independent `LeslieCrossover` source; it changes
no plugin source or generic core note-event action.

The [channel-mode contract](../MIDI_CHANNEL_MODE_CONTRACT.md) remains bounded:
CC120 addresses mapped ownership and checks ideal contacts before lowering to
existing releases; it advertises no finite-travel or shared-tail behavior.
CC121 sends expression ID 8192 value 1.0 directly, bypassing endpoint calibration.
CC123 retains its established accepted-value policy. Calibration is copied
with an epoch, applies only to CC11, and remains outside musical serialization.
All 47 parameter identities, the `B3CONTROLS4` writer and readers 1–3 retain
their meanings. Native feature tests do not imply VST3 channel-mode support.

The crossover is compiled into the core archive as an independent module and
used by its probe/tests; there is no Engine call or audio-route insertion.
Scanner same-Hz failure, crossover same-Hz/physical gaps, R4 ownership and
R5/R6 integration gates remain unchanged. Passing these integration fixtures
does not establish literal interface equality or physical organ/cabinet fidelity.

## Practical remaining integration gate

The local 2/2 repair check is sufficient to admit these narrow fixes for a
source-identified hosted rerun. Before claiming portable acceptance, publish
the reviewed source and require the existing core Release/sanitizer jobs on
CMake 3.31.6 plus Windows core/native and the native macOS/Linux jobs. Inspect
their actual install and calibration results, including skips, rather than
carrying forward `ff41d412` or b9 statuses. Windows must complete all seven
lifecycle scenarios and the exact-content report comparison; the older CMake
jobs must reject the three previously bypassed destinations without mutation.

Root `check`, `check_vst3` and hosted filtered executions use
`--no-tests=error`. A37's reviewed workflow also requires the new ordinary
native gate names and maps exactly 21 sanitizer CTest names to their built
inputs. Its native probe requires six instrumented archives and the actual
Python launch command. The final trace assertion must retain ten subprocesses,
seven lifecycles and **two** deliberate failed replays; A38 identified an initial
one-replay assertion and A37 corrected it. These are admission requirements;
the expanded sanitizer job has not yet been observed passing this overlay.

A38 executed only read-only discovery, source/diff/hash inspections and a Python
AST parse, plus owned whitespace/link checks. Root performed the documented
rebuild and focused CTest run. A coherent final configured inventory/full gate
belongs to root after the remaining source freezes; no redundant broad run,
local sanitizer pass, MinGW execution or later hosted success is claimed here.
