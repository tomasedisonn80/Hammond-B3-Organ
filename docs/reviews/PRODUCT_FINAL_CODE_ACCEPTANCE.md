# Product final code acceptance — A55

Actual reviewer: /root/w10_a55_code_acceptance, wave 10, 15 November 2026 UTC.
This independent review covers the implemented M9 subset, independent M6
crossover and later record/report-admission tools. A55 inspected source, diffs,
test oracles and retained executions. No build, runtime test, numerical sweep
or shared-build operation was repeated.

## Decision and exact boundary

**Accept the inspected implementation and admission repairs for the
integrator's final publication gate. No additional code blocker was found.**
This does not certify an unpublished final tree, complete the actual worker
ledger, or accept a physical device, DAW, acoustic model or whole-interface 1:1
match. The below-RtMidi close-error/callback-retirement gap remains an explicit
native qualification gate.

| Identity | Reviewed observation |
| --- | --- |
| Local HEAD/tree | d8c39f7986746eacc991747153c7dbb012bb9a32 / edf67b978f93e8dbea6537ce92d3928c171bc1f3; parent d556da017ea0a5d4f2d231416782dbc5066e58c2. |
| Live remote | Read-only git ls-remote origin refs/heads/main returned the same d8 commit. This does not publish concurrent working files. |
| Later code | A46's checker/test and CI progress step, plus A48's plot-admission repair/test. Exact hashes are in the [A55 receipt](../development/2026-11-15-product-continuation/reports/A55-code-acceptance.json). |
| Coherent local evidence | All **366** code/test/build/data inputs in the [wave-8 receipt](../development/2026-11-15-product-continuation/reports/wave8-coherent-build.json) still match. Its original log executes the relevant named tests, including both new Python modules, within **180/180 in 507.55 s**. Configuration: GCC 14.2 Release, standalone ON, physical MIDI OFF, VST3 OFF, dummy SDL. |
| Published platform evidence | Primary [Linux](PRODUCT_LINUX_HOSTED_REVIEW.md), [Windows](PRODUCT_WINDOWS_HOSTED_REVIEW.md), [macOS](PRODUCT_MACOS_HOSTED_REVIEW.md) and [VST3](PRODUCT_VST3_HOSTED_REVIEW.md) audits qualify d8, including the repaired 21-test native sanitizer execution. They do not qualify the later A46/A48 overlay. |

The production application remains
7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852, painter
3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567, and crossover probe
da09640f7520cd887a836961658ed8a79d6b6bff28f0e33a0ce44cf76f992eac.
Hash agreement identifies retained inputs; it is not independent compilation
attestation or new execution evidence.

## Compatibility at the intended interfaces

A55 compared existing files at pre-feature af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d
with current bytes: all **52 existing core/header files**, **20 VST3 files**,
**30 existing data files**, and four UiModel/StateFiles files are identical.
This independently extends [A29's source comparison](../PRODUCT_COMPATIBILITY.md)
to the inspected checkout. The added crossover source and registry retain their
separate identities.

The registry still contains exactly 47 schema-4 records. ControlStateIO writes
B3CONTROLS4 and reads versions 1–4; Engine retains 91 shared sources and unchanged
nominal dry processing. No LeslieCrossover use appears in Engine, Session,
native main or VST3 sources. Its four-rate research API does not extend the
Engine/VST3 44.1/48/96 kHz set. Plugin identifiers, automation, serializer and
input timeline remain unchanged; d8's separate plugin validator/ABI results
supply the platform execution that A29's earlier native-only run could not.

Intentional internal changes still require coherent rebuilding. SessionCommand
appends ScopedSoundOff, while MidiInput::begin_epoch gains a defaulted
calibration argument and fixed decoder state. These preserve earlier source
call sites and variant indices, not a cross-version C++ adapter ABI. Native
diagnostics add selected/configured/active/pending observations to schema 3;
exact-member consumers must adopt them. Neither is a musical-state migration
or a new VST3 MIDI/calibration interface.

## Source-to-evidence acceptance

| Accepted behavior | Implementation and matching regression oracle |
| --- | --- |
| CC120 addresses MIDI ownership in an ideal-contact Session | MidiInput::decode constructs the distinct command. Session's admitted_command_shape rejects invalid scope before sequence reservation; apply checks ContactMode::Ideal before the existing ownership reduction. test_standalone_channel_modes compares against independently specified physical Engine events, including percussion and surviving owners. test_standalone_channel_acceptance adds full queues, sequence endpoints, invalid scopes and continued audio. |
| CC121 preserves pending edits and bypasses inversion | The decoder emits expression ID 8192 value 1.0 directly; native dispatch uses UiModel::external_parameter. cc121_across_partial_acknowledgments interleaves Upper/Lower/pedal edits, stale/partial acknowledgments and later scoped commands, then requires complete expected controls and owners. Repeated reset generates no duplicate control action. |
| Calibration stays immutable within an epoch | map_midi_expression validates before arithmetic/output assignment; begin_epoch validates before copying settings/history. mapping_boundaries checks every representable endpoint pair, all raw values, bit-exact default division and representative saturation/direction cases. immutable_epochs_and_controller_scope checks rejected epoch calls, timestamp history and CC11-only calibration. |
| Changed settings retire old input before new activation | main.cpp's request_midi, retire_midi, observe_midi_retirement and start_pending_midi carry a copied request and require applied releases, later recovery or joined/stopped audio. The real-main fixture checks identical Apply, changed calibration/route/port, no-input configuration, failed activation and explicit retry. Its transition oracle requires inactive/pending observations, the final applied release sequence and no Apply-generated expression update before subsequent CC11. |
| Musical state excludes adapter calibration | Serializer and StateFiles are unchanged. test_standalone_expression_diagnostics checks retained musical controls and exact original state-file bytes across modal/configuration/decoder changes. Calibration is process-local configuration. |
| Crossover state, ports and block rejection are transactional | LeslieCrossover.cpp implements signed KCL and floating A–H treble/W–B bass ports. Preparation stages operators; rate change preserves physical coordinates/prior input. Block processing validates every interval before deterministic output replay. Lifecycle tests independently evaluate charge/flux/energy/ports, all ordered rate pairs, partitions, boundaries and continuation. Author/allocation fixtures prove a third-interval numerical failure after two successful scalar intervals while the block commits no prefix. |
| Numerical acceptance qualifies the declared recurrence | Independent Python nodal reference and actual native sine/response producer retain four-rate/six-load experiments, warped-frequency budgets and separate same-Hz differences. Matching local and d8 hosted logs execute response, lifecycle and allocation gates. No same-Hz electrical, audible or physical threshold follows. |

The [local execution log](../development/2026-11-15-product-continuation/reports/wave8-full-ctest.txt)
contains the named CTest entries. The [A21 note](../development/2026-11-15-product-continuation/notes/A21-channel-acceptance.md),
[A25 note](../development/2026-11-15-product-continuation/notes/A25-crossover-allocation.md)
and [A38 review](PRODUCT_INTEGRATION_REVIEW.md) retain their original independent
oracles and source-specific results. These are retained executions, not A55 runs.

## Failure semantics that must survive later work

**MIDI validation and transport failure differ.** Invalid selection rejects
before changing the active transport or configured settings, while reporting
an error. Healthy identical Apply preserves the epoch. A valid changed request
intentionally retires the old connection and MIDI owners; failed reopening
leaves the new configuration inactive until explicit retry. It does not restore
the old live connection or replay held notes. The native fixture checks
discarded failed-open prefixes and survival of an independently owned UI note.

Session queue overflow and command failure retain **global recovery**. A
saturated batch is discarded when overflow requests recovery; its regression
checks original applied controls and fresh audio continuation. The scoped CC120
promise does not extend across transport failure, and Session gains no general
whole-batch control rollback. A future non-ideal-contact Session would reject
sound-off and invoke existing recovery; its public current preparation cannot
execute that future case.

**Crossover block rollback is a separate guarantee.** All intervals validate
before destination writes; identical replay commits state at its end. This
requires externally serialized access and valid, immutable, nonoverlapping
spans. Tests preserve NaN-payload/signed-zero sentinels, reject late invalid
input/numerical failure and compare next-valid-call twins. Calibrated allocation
observation includes first calls and rejection paths. Zero observed current-thread
C++ allocations/frees does not measure C allocation, other threads or deadlines.

**Installation preflight is not atomic multi-file rollback.** The actual
InstallCrossoverTools.cmake checks six inputs and fresh destinations before
copying, uses numeric while(1) in the generated script and explicitly reports
that later copy failure may leave a partial new installation. Windows borrowed
environment-string and stdout newline repairs remain fixture-only. D8 primary
results qualify those repaired platform paths; no new all-files rollback or
runtime-library collection guarantee is introduced.

## Admission-tool acceptance

### A46: actual-record consistency

The [checker](../../tools/check_product_session.py) defaults to strict mode:
exact session/schema, A01–A60, canonical distinct worker identities, ten correct
six-worker waves, accepted states, usable ownership and substantive
SHA-256-matching notes. Progress mode always declines completion, even with a
complete set. Missing or contradictory accepted evidence is not skipped.
Bounded reads reject unsafe links/special files and detected input changes.

The [regressions](../../tests/test_product_session.py) explicitly use synthetic
temporary records for strict success/incomplete failure, duplicates, schema/type
coercion, missing/tampered notes, raw-byte CRLF hashes, unsafe paths, narrative
floors and changing files. The original 19-method result and later coherent
CTest result match current hashes. CI's seven-line addition uses pipefail,
retains JSON and currently invokes progress mode. Actual strict closure and
the strict CI invocation remain integrator actions. A manifest cannot attest
tool dispatch, substantive acceptance or product readiness.

### A48: complete numerical-report admission

The [plotter](../../tools/plot_crossover_characterization.py) requires the exact
six source identities, valid binary digest, complete v1 fields, unchanged
budgets and complete response/sine families. It reconciles counts/group maxima
with summaries, validates strict scalar types and decaying sine bounds, rejects
duplicate/nonfinite/malformed/oversized JSON, and relates nominal
magnitude/phase metrics to complex error. It neither launches the probe nor
changes the electrical model.

The [11-method regression module](../../tests/test_plot_crossover_characterization.py)
preserves the three demonstrated incomplete/contradictory admissions as negative
cases, checks inclusive budget boundaries and reordered complete positives, and
requires invalid CLI admission to precede rendering while preserving existing
output. This does not promise atomic cleanup after an unrelated renderer or
filesystem failure. Matching hashes and consistent JSON cannot authenticate
invented observations or prove compilation; original execution evidence remains
necessary. The [A48 review](PRODUCT_NUMERICAL_ADMISSION_REVIEW.md) and root's
separate [plot refresh](../development/2026-11-15-product-continuation/reports/crossover-plot-admission-refresh.json)
preserve the numerical report and exactly unchanged decoded pixels.

## Resolved contradiction and required next gates

**A55-D1 — resolved:** the calibration contract still described implementation
and independent acceptance as pending. Root replaced that sentence with a
frozen-contract description and current evidence links. The
[amendment receipt](../development/2026-11-15-product-continuation/reports/contract-status-amendment.json)
and A55's hash check confirm the complete suffix beginning “This is adapter
configuration” is identical. No behavior, criteria or code changed.

**A47-N1 remains open.** The [native recovery review](PRODUCT_NATIVE_RECOVERY_REVIEW.md)
shows pinned WinMM/CoreMIDI paths can suppress native close/disposal errors
before clearing connection state. Native callback parsing can touch RtMidi
storage before the wrapper's entered-callback counter. This is a source-proven
observability gap and unreproduced risk model, not an observed hardware failure
or use-after-free. Later sanitizer success uses synchronous dependency offers
and does not close that gate. The old named quarantine leak exception remains
confined to its fixture.

1. Accept remaining actual workers, run the product checker strictly, switch CI
   to strict and retain the real completion result. This review preaccepts no
   other worker and substitutes no historical ledger.
2. Publish the coherent accepted final tree and inspect its own required hosted
   outcomes, including python_test_product_session,
   python_test_plot_crossover_characterization and the strict record step.
   Preserve d8 and local overlay results under their original identities.
3. Inject failed OS close/disposal below pinned prepared RtMidi while holding a
   callback before wrapper entry. Review checked close preserving native handle,
   dependency storage, adapter context and inbox, poisoned no-reopen/no-reset
   behavior and ordinary leak-free teardown. Successful close also requires
   platform-specific callback-retirement evidence.
4. Freeze the M6 same-Hz protocol/floors before a separately identified numerical
   candidate. Preserve v1, scanner G5's unresolved same-Hz failure, independent
   R4 ownership and R5/R6 integration gates. Acquired electrical/cabinet data,
   actual displays/devices/DAWs, accessibility, deadlines and distribution
   remain outside this acceptance.

The [A55 receipt](../development/2026-11-15-product-continuation/reports/A55-code-acceptance.json)
records hashes, protected comparisons, matching original logs, the remote
observation and documentation-only checks. A55 changed no production/test/build/
workflow file, index, commit or remote. Future source changes require affected
acceptance against their own inputs.
