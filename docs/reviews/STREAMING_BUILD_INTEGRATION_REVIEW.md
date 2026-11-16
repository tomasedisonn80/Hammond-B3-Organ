# Streaming/material build integration review

**A36, wave 6, 16 November 2026.** CMake correctly wires six causal-grid suites
and the Upper-rack fixture. Root repaired missing-probe setup and the native
sanitizer selection after this review. Source acceptance is distinct from
pending runtime/hosted qualification; initial gaps remain recorded below.

## Evidence and boundary

Read AGENTS/full M0–M9 plan, scope/checkpoint, A09 map, coherent receipt, CMake
and all three workflows. This is a working overlay on
`4aac394cde4da40906b615573a8779aee2d9a37a`, not that commit's unchanged tree. The
[audit receipt](../development/2026-11-15-streaming-continuation/reports/A36-build-audit.json)
binds inspected inputs, discovered commands, setup observations and job selection.

Read-only `ctest --test-dir ../build-native -C Release --show-only=json-v1`
found 210 entries, including all seven additions; generated Ninja corroborates
dependencies. Initially all 505 inputs matched root's coherent inventory. Its
210/210 result in 191.89 s is prior Linux GCC 14.2.0 Release/dummy-SDL evidence,
with MIDI/VST3/sanitizers off. A36 did not configure, build, rerun suites, install
or query hosted results. Six direct `setUpClass` calls exercised missing-input
setup only, without test bodies or native subprocesses.

## Build and discovery

- Root appends `src/research/CausalContactGrid.cpp` after the nonrecursive glob,
  placing it in the static core and complete source inventory.
- `hammond_causal_contact_grid_probe` links that core and receives the common
  C++20/warning/sanitizer settings. Its ordinary `main(int,char*[])` needs no
  MinGW `wmain`/`-municode` option; arguments are only ASCII help or rejection.
- Top-level globs register `test_causal_contact_grid`,
  `test_causal_contact_grid_lifecycle`, `test_causal_contact_grid_resources`,
  and Python CLI, differential and reference suites, with causal labels and
  90-second limits. Native tests and the probe are `check` dependencies.
- Each causal Python entry receives
  `HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE=$<TARGET_FILE:hammond_causal_contact_grid_probe>`.
  Discovery resolves this build's executable; the expression handles `.exe` and
  configuration subdirectories. CTest itself does not build inputs.
- The Upper-rack fixture compiles its CPP plus `InstrumentView.cpp`, links
  drawing/support, defines `SDL_MAIN_HANDLED`, and enters the standalone aggregate
  and root `check`. Limits are 90 s ordinary/240 s sanitizer; prior local time 11.35 s.
- The benchmark explicitly includes the nested research header as well as the
  appended CPP. Both appear with matching hashes in its actual 81-entry manifest.
  `ContactReferenceTools` remains the explicit 48-file copy-only package: its
  module and all 48 payloads match the base; no grid header/archive/probe is installed.

## Thirteen hosted jobs and actual selection

These source-defined names are not queried protection settings or outcomes.
“Grid” means all six causal tests; “rack” means the new raster fixture. Every
group rebuilds the core archive; that alone does not execute research code.

| Workflow/job | Grid | Rack |
| --- | --- | --- |
| CI: Release (Linux GCC) | Yes | No: SDL off |
| CI: Release (macOS AppleClang) | Yes | No: SDL off |
| CI: Release (Windows MSVC) | Yes | No: SDL off |
| CI: Linux GCC ASan + UBSan + leaks | Yes | No: SDL off |
| CI: Complete R4 waveform qualification (Linux GCC) | No | No |
| Native VST3 (Linux GCC) | No | No |
| Native VST3 (macOS AppleClang) | No | No |
| Native VST3 (Windows MSVC x64) | No | No |
| Native standalone (Linux GCC, MIDI ON) | No | Yes |
| Native standalone (macOS AppleClang, MIDI ON) | No | Yes |
| Native standalone (Windows MSVC x64, MIDI ON) | No | Yes |
| Native standalone (Linux GCC, MIDI OFF) | No | Yes |
| Native standalone (Linux GCC ASan + UBSan + leaks) | No | Yes after gate-22 repair |

Core jobs build all targets/run all tests; R4 runs its full-waveform target.
VST3 builds its aggregate/selects `^(hammond_vst3_validator|test_native_)`;
standalone Release builds its aggregate/selects `^test_standalone_`. Native
sanitizer uses an exact gate set. Hosted Python is 3.12; project minimum is 3.10.

## Concrete findings and repair acceptance

**A36-F1 — missing direct probe.** Both native-consuming suites initially
raised `SkipTest` for unset variables; differential also skipped an empty string.
Missing paths failed. CTest supplied a valid generated path: no CTest skip or
native failure was observed. To meet A09's fail-on-absence requirement, use
`RuntimeError` for unset/empty values and update the guide, preserving old receipts.

**A36-F2 — sanitizer selection.** Initially the exact 21-gate native job omitted
the rack fixture. Recommended and verified repair: add gate 22; update six count
guards, two step labels and one diagnostic; retain its provenance CPP, required
fixture/painter objects and existing 240-second budget; require Release discovery.
Existing checks cover instrumentation, link/runtime dependencies, exact commands
and sanitizer overrides. Every previous gate/threshold is preserved.

**A36-F3 — documentation.** Build/benchmark inventory wording omitted the nested
CPP/header. Root now names both and separates historical 54/current configured
81 entries, retaining the original measurement.

## Portability and remaining runtime gates

Guarded Windows `_O_BINARY` setup precedes input, preserving raw CRLF/Ctrl-Z
for the 131,072-byte ceiling and trailing-data tests. Output tests accept Windows
newlines. MSVC `/W4 /WX`, link and transport execution need the hosted job.
Resource hooks pair `_aligned_malloc/_aligned_free` on MSVC and
`posix_memalign/free` on Unix/Apple; large test storage is on the heap.

Core arithmetic uses standard fixed-width integers and explicit widening, with
no `__int128` or extended-floating dependency. AppleClang/libc++ must still execute
rational/lifecycle/allocation gates. The raster's software surface/`SDL_Init(0)`
qualifies no physical display, controller or audio device.

Python subprocesses inherit sanitizer settings. Native flags instrument core/probe;
the native job additionally instruments SDL C. Keep fixed timeouts and reject
sanitizer stderr, including deliberate invalid-input cases. C++ allocation hooks
establish no system-allocation, thread-lifetime or callback-deadline claim. Root
must retain affected repair checks and all thirteen exact-source hosted outcomes.

### Final source reinspection

Three workflow YAMLs and thirteen embedded Python blocks parse. The matrix still
expands to thirteen jobs. All 21 old sanitizer mappings/budgets survive; only the
rack fixture is added. All 22 names are locally registered. Setup branches now
raise `RuntimeError` for absent/empty probes. The receipt binds exact patched
bytes. Root owns post-repair runtime checks and publication; no current-source
Windows, AppleClang or sanitizer runtime result was observed by A36.
