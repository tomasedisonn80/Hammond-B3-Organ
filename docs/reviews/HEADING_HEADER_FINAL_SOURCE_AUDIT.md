# Heading/header integration: final source and CI audit

**A51, 17 November 2026: the named source preserves the admitted musical and
saved-state boundaries. The additive hosted-test patch is admitted for
execution; a combined native or hosted pass is not claimed.** Root retains
merge, configuration, execution, acceptance and publication ownership.

The [independent receipt](../development/2026-11-16-heading-title-continuation/reports/a51-final-source-audit.json)
contains all 213 per-path comparisons, the exact two-hunk application diff,
parameter checks, source identities and CI mapping. Comparisons use immutable
Git blobs because root is reconciling concurrent work in the working tree.

| Audited source | Identity |
| --- | --- |
| Original heading-session base | `113c29b7b14c8fde0859bc405ef8e4141a131ea6` |
| Published T2 | `6047723b595259de355c74342e48a8ae2ee1e228` |
| Local recovery containing H1 and replay/Load corrections | `045c95d769b197d05b6596901508c160fd62fb35` |
| Concurrent published UI-delivery source | `9d60dbf462a90fe422fd4e69757fe202264acb7c` |
| Root's corrected additive standalone workflow | SHA-256 `b572d1e34d891657964d8ca6f5882fbaf157ab91ddbb309fd183af89fbdfac6e`; 70,886 bytes |

## Protected source and compatibility

I reproduced every byte count and SHA-256 in the original
[A09 inventory](../development/2026-11-16-heading-title-continuation/reports/a09-compatibility-baseline.json)
against its original Git blob, then compared T2, local recovery and concurrent
remote sources. All **213** remote protected files equal T2. The local recovery
differs from those sources only in the separately admitted `main.cpp`. Relative
to the original base, that same main exception contains the earlier UI trace
and later selective paint boundary. All other protected files are exact.

The [A38 compatibility review](HEADING_HEADER_COMPATIBILITY_REVIEW.md) remains
valid at its named pre-replay-repair inputs. Rechecking its critical source
identities likewise finds only `main.cpp` changed. Its assertion that all 213
paths match pre-H1/H1 receipts must not be relabeled as a current-source claim.
This supplement documents the later exception instead of changing A38's bytes.

The unchanged core keeps 91 shared free-running sources, two 61-key manuals,
25 pedals, four retained banks and a nominal dry Engine. State serialization
still writes `B3CONTROLS4` and retains legacy readers 1–3. Source, Session,
AudioDevice, parser, state and plugin files introduce no new musical route,
public parameter, migration or callback behavior through this change.

I independently parsed all **47** native parameter descriptors and matched
their ID, path, kind, unit, maximum, default, step count and engine event's type,
manual and index against the registry. All fields match. The unchanged plugin
class IDs remain processor `19F9ADC0-533F42B4-B96BD51D-6547E838` and controller
`0DEE76AB-26BC475A-BF64F138-C89FB0E0`. This is source compatibility evidence,
not a fresh ABI, DAW, platform or physical-device execution.

## Application exception and observation semantics

The local main is
`361ae03aa9e1a369a8fd8d125c21b10e40841d08d768a4c5637b2a3ecf0232f3`.
Its difference from T2 main `89b24fde…237c4` has exactly two hunks: the loop
comment and the successful replay-marker acknowledgment branch. The branch
continues eager pumping only when an existing actual painted frame agrees with
current workspace, presentation and overlay. Dimensions and musical controls
are deliberately excluded. A changed semantic view reaches the ordinary paint
before the next prefix; resize-only prefixes preserve eager draining. No
synthetic observation, extra render call, allocation, parser expansion or longer
drain is introduced. Normal operation without an input script bypasses it.

The complete guarded musical-observation suffix is byte-identical across the
original base, T2 and local recovery, SHA-256
`43a0234454ff6204fca949cbabeaf0e92089b156062fb84059252d734ed4b4be`.
The entire `replay_acknowledged()` method likewise remains exact,
`ee11dab51af1478358c30f28c5b89c5993d8e58aee7da78f8442b5bb639bbe6d`.
The receipt defines the precise extraction delimiters. The 256-action/event
limits, 512-entry history and existing 2000 ms drain retain their meanings.

The earlier schema-3 addition of `ui_observation_capacity`,
`ui_observations_truncated` and `ui_observations` remains an intentional
external exact-key-consumer boundary. The later paint repair adds no schema
member. The separate [Load observation clarification](STARTER_LOAD_OBSERVATION_DIAGNOSIS.md)
changes only its test's copied-state chronology oracle; it neither changes
Session nor supplies an exact callback timestamp. Full edited state remains
mandatory. Root's [repair qualification](../development/2026-11-16-heading-title-continuation/reports/replay-load-link-repair-qualification.json)
retains original failures and separate changed-test execution.

## Hosted coverage admitted

The concurrent remote already contains thirty sanitizer CTests backed by
twenty-nine targets. Root preserved that coverage and added the following
three mappings. Normal hosted discovery now requires **44 named tests**, up
from 41, while still executing every `test_standalone_*` test serially.

| Added CTest | Instrumented native target | CTest timeout, ordinary / sanitizer | Python child timeout, ordinary / sanitizer |
| --- | --- | ---: | ---: |
| `test_standalone_header_statistics` | `test_standalone_header_material` | 90 / 240 s | 20 / 60 s |
| `test_standalone_header_grain_bounds` | `test_standalone_header_grain_bounds` | 30 / 90 s | Direct native process |
| `test_standalone_replay_paint_boundary` | `hammond_standalone` | 60 / 90 s | 12 / 30 s |

The resulting sanitizer selection is exactly **33 distinct tests / 31 distinct
build targets**. Statistics reuse the existing real-header fixture. Grain adds
one fixture target; the replay regression adds the real application target,
separate from the substituted-MIDI calibration probe. All build, provenance,
instrumentation, discovery and uniqueness assertions now use the appropriate
test or target count. No earlier selected test is removed.

The three new test files and the replay's `test_standalone_workflows.py` helper
join the sanitizer source-hash inventory. Existing app and MIDI-replay helpers
were already present. Both header fixtures include the real painter once;
the grain target's compiled-source set must be exactly its fixture translation
unit. The real application must compile both `main.cpp` and `InstrumentView.cpp`.
The linked `hammond_standalone_support` target must have `HAMMOND_HAS_RTMIDI=0`;
CMake marks this definition private, so it need not appear on main or painter.
The calibration probe retains its explicit `=1` and fake-header ordering checks.

The first proposed inspection incorrectly required the private definition on
the application target. Final source tracing caught that assumption before any
native execution. The receipt retains the original draft bytes and the explicit
correction. Changing CMake to add a redundant application flag would conceal the
bad oracle; the inspected target must instead be the support library. Root made
that sole target-name substitution, which I verified byte for byte against the
retained first workflow. The [correction receipt](../development/2026-11-16-heading-title-continuation/reports/ci-private-midi-definition-correction.json)
preserves its source evidence; no CMake flag or runtime behavior changed.

The new application joins the existing sanitizer compile-flag, object-existence,
link-flag and runtime checks. Both real entry paths must link the same six
instrumented core/support/drawing/audio/replay/SDL archives. The two new Python
commands must have exactly seven arguments, the named script and executable,
and explicit sanitizer child limits 60 and 30; grain remains a single native
command. These checks are structural source admission, not a fabricated
CTest-discovery result.

The sanitizer job's environment and policy block remain byte-identical to the
remote: ASan `detect_leaks=1:halt_on_error=1`, UBSan
`print_stacktrace=1:halt_on_error=1`, and LSan `exitcode=23`. Per-test sanitizer
overrides and disabled required tests are still rejected. Existing workloads,
limits, fallback instrumentation, source reverification and artifact collection
remain intact. All eleven inline Python blocks parse as Python source. The
workflow stayed byte-identical throughout this read-only check.

## Source-specific qualification still required

Root must configure/build the reconciled source, inspect actual CTest commands
and run its coherent gates. Then publish with the fresh expected remote parent,
verify the published tree, and observe each hosted job at that exact source.
The remote's `RUN_SERIAL` smoke scheduling change is distinct from the admitted
replay repair; it does not turn the retained installed 600 ms failure into a pass.

The H1 gallery and paired matrix name painter `0bf731a6…` and application
`bfe8e36d…`. The later replay-qualified application is `2c64e585…`; its identity
comes from root's receipt, not a new native run by A51. Keeping painter bytes
does not let anyone rewrite a captured executable identity. Old T2 hosted
passes likewise do not qualify the new combined source. Original 237/240
failures remain retained alongside targeted repairs.

No real display/DPI/input, native accessibility, callback deadline/retirement,
hardware, measured fidelity or signed distribution gate closes here. Literal
whole-interface 1:1 remains unmet and unwaived, and all M0–M9 exits remain binding.
