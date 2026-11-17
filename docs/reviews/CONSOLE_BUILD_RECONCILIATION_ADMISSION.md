# Console build and CI reconciliation admission

**A46, wave 8 — source-only GO for root review and application.** The complete
proposed [standalone CMake file](../development/2026-11-16-console-completion/reports/A46-merged-CMakeLists.txt)
and [native workflow](../development/2026-11-16-console-completion/reports/A46-merged-standalone.yml)
retain the existing union of console library/P1 work and the published H1/native
paint work. No configure, build, native execution, CTest discovery, test-suite
rerun, index mutation or publication was performed by this worker. The
[machine-readable audit](../development/2026-11-16-console-completion/reports/A46-build-reconciliation.json)
contains the exact mappings, properties, source lists and all 27 source checks.

## Exact inputs and outputs

Base is `9d60dbf462a90fe422fd4e69757fe202264acb7c`; remote is
`03c70c103a4a0dd72b323529416b909c19a4e139`. Base and remote bytes were compared
with their exact Git objects. Ours is the immutable `reconciliation-prep` snapshot
of unpublished console work, not an invented committed revision. Shared CMake,
workflow, build and index remain root-owned.

| File version | Standalone CMake SHA-256 | Native workflow SHA-256 |
| --- | --- | --- |
| Base 9d60dbf | `246acf9b259824d07a9aa9fc8a5177734b65e0e89de3b8f378bd7de609b0d897` | `59423f01dc5811d2f8146e06cb939fd9f96295c0e818a74c387519f7fe824e9c` |
| Unpublished console snapshot | `c2da131f35b6f8e3827f8cef93244d997f0921c60de9235ad4e88775702cf690` | `c949a1d20debec4970cff0f5a2bdaa0e54e01b358eb600a8bb241522dffd34ca` |
| Remote 03c70c1 | `642655110b803592e0943d6bb1aa367cd74c81d72b6ebef0b3f1058916157a96` | `af5cf9421c5cdbae37b5f0d26e1bf3d96c8a5b26491f89b6518db0ca0e1cc319` |
| Proposed union | `927f48c1feba27889a63c73d7b8223b40b33c8851a07ac3b7feec9a88e713e07` | `d298ac55d78ae242b97c5de73be138b4a87c4d4fb343872e58a5c0bd5dc08659` |

## Derived union

| Source inventory | Base | Ours | Remote | Proposed union |
| --- | ---: | ---: | ---: | ---: |
| Mandatory native-platform names | 41 | 51 | 45 | **55** |
| Selected sanitizer CTest names | 30 | 37 | 34 | **41** |
| Distinct selected sanitizer executable targets | 29 | 35 | 31 | **37** |
| Sanitizer provenance sources | 36 | 58 | 41 | **63** |
| Embedded Python assertion statements | 119 | 136 | 125 | **142** |

These are parsed source inventories, not observed CTest discovery or execution
counts. The platform selection still includes every `test_standalone_` test plus
the three named Python comparator/capture suites; the 55 names are its mandatory
subset. The sanitizer selection is the exact anchored 41-name set.

The five library tests continue through the existing SDK-free CMake glob and
shared test loop. `LibraryModel.cpp` occurs once in the support-library source
list. Header material, header grain and P1 each declare exactly one fixture
translation unit, whose inspected source includes the real painter once; none
also adds `InstrumentView.cpp` as a target source. Python wrappers map header
statistics to the header fixture, title density to the footage fixture, P1
numerical to the P1 fixture, both paint boundaries to the real application, and
native calibration to its existing substituted-MIDI probe.

The CMake semantic statement/context inventory equals the exact additive parent
union, including registrations, commands, labels, properties and conditional
deadlines. All five remote `RUN_SERIAL TRUE` additions remain: MIDI CLI, native
calibration, native MIDI replay, workspace replay and starter Load. The original
application smoke's serial property also remains.

## Deadlines and selection

| Gate | Ordinary CTest seconds | Sanitizer CTest seconds | Child seconds, ordinary / sanitizer |
| --- | ---: | ---: | ---: |
| Header material | 180 | 480 | — |
| Header statistics | 90 | 240 | 20 / 60 |
| Header grain bounds | 30 | 90 | — |
| Replay paint boundary | 60 | 90 | 12 / 30 |
| Semantic paint boundary | 60 | 90 | 12 / 30 |
| P1 fixture | 180 | 480 | — |
| P1 numerical | 180 | 480 | 60 / 60, unchanged comparator default |
| Title density | 90 | 240 | 20 / 20 |
| Native calibration | 90 | 180 | 15 / 15 |

The five library gates retain their existing absence of explicit timeout/label
properties; both CI executions retain the global `--timeout 180`. Every other
parent timeout and label is preserved. Native-platform jobs retain 40 minutes;
the sanitizer job retains the remote **35-minute** budget. Both discovery
commands remain read-only `--show-only=json-v1 --no-tests=error`; their selections
are reused for execution with `--no-tests=error` and `--parallel 1`. No required
gate is disabled or removed. The sanitizer selection still excludes the existing
intentional-quarantine test and preserves leak checking for every selected gate.

## Instrumentation and integrity

All 11 embedded Python blocks parse. Every assertion expression from both parents
is present after adjusting only the derived 41/37 cardinalities. The build title,
shell target count, provenance checks, discovery cardinalities and final status
text all agree. Provenance sources, required compiled-source sets and sanitizer
limits are exact unions without duplicate names.

The proposal preserves instrumented/nonempty object checks; ASan/UBSan symbols
in all selected archives; sanitizer linker flags and loaded runtimes for every
selected executable; MIDI-off support and fake-MIDI-on calibration definitions;
include precedence; the apron fault seam; the exact grain fixture source set;
and the P1 painter inclusion check. Both the real application and calibration
probe must link all six instrumented production archives. Library tests retain
their core/support link check, and P1 retains drawing/support/core/SDL checks.
All wrapper script paths, executable paths, argument shapes, child-timeout probes,
disabled-test refusals and per-test sanitizer-override refusals remain. Leak,
address and undefined-behavior policies, platform matrix, action pins, dependency
pins and other step metadata are unchanged.

## Admission boundary and next action

Root can review and apply these two complete files after preserving the immutable
inputs. Painter, fixture and comparator source-identity reconciliation remains a
separate root gate; this proposal changes no source pin or numerical threshold.
Root then configures and builds coherent merged inputs, observes actual discovery,
runs the affected qualification and obtains exact-source hosted outcomes. Earlier
passes remain evidence for their own pre-merge sources. This admission claims no
merged runtime pass, whole-interface equality, platform/device acceptance or
physical fidelity.
