# Fixed-registration adapter impact audit

A11 reviewed the unchanged production source at
`b79086f6bb0c42b97130c721c5c73c7c97a13887` against the
[selection contract](PRESET_SELECTION_CONTRACT.md),
[core API](PRESET_CORE_API.md) and
[state/parameter contract](PRESET_STATE_PARAMETER_CONTRACT.md).
This is an implementation map and acceptance specification. It does not claim
that the new adapters are implemented or that runtime gates have passed.
The [worker record](development/2026-11-14-preset-continuation/11-adapter-audit.md)
retains the inspected source and actual checks.

## Required implementation ownership

Assign each row to one implementation owner; tests may have separate acceptance
owners. Core types, state4 and the 47 descriptors must be available before a
coherent adapter build. Do not link an older core against the enlarged snapshot.

| Owner boundary | Exact production files | Required change |
|---|---|---|
| Core publication | `src/StateExchange.cpp` | Change the registry assertion to 47; encode/decode both **raw fixed modes**; check 0-9 before narrowing; correct the descriptor-order comment. `include/hammond/StateExchange.h` already derives capacity as `kParameterCount + 3`. |
| Performance admission | `src/PerformanceInput.cpp`, `include/hammond/PerformanceInput.h` | Add `SelectPreset` to the control allowlist and documented alternatives. Keep Engine responsible for complete payload validation and retain the existing all-or-nothing ownership transaction. |
| Standalone publication/admission | `apps/standalone/Session.cpp` | Add `SelectPreset` to `admitted_command_shape`; extend `pack` and `unpack` together with explicit masks and shape/range assertions. Preserve FIFO command order, sequence accounting and queue recovery. |
| Host timeline | `src/HostTimeline.cpp`, `include/hammond/HostTimeline.h` | Add a `SelectPreset` case to `snapshot_anchors` using `control_preset_selection`; update count/threshold documentation. Preserve the existing curve reconstruction, explicit-point dispatch, carry budget and transactional commit. |
| Native controller | `plugins/vst3/Controller.cpp`, `plugins/vst3/Controller.h` | Add effective-selector extraction to `snapshot_plain`; update the 45-descriptor and Cancel comments. Keep `setComponentState` atomic and preserve raw accepted `setParamNormalized` values. |
| Native UI | `apps/standalone/UiModel.cpp`, `apps/standalone/UiModel.h`, `apps/standalone/InstrumentView.cpp` | Add new semantic preset controls and `apply_parameter` handling, parameter mapping, layout/focus/activation and the 47-count assertion. Derive applied selection, bank highlights and percussion eligibility from copied applied controls. The separate UI contract owns exact geometry. |
| Standalone diagnostics | `apps/standalone/main.cpp`, `apps/standalone/benchmark.cpp` | Extend `write_controls_json` and `write_controls` with raw fixed modes. Any effective selector diagnostic must be separately named and derived; remembered banks remain present. Update the corresponding exact report schemas/expectations deliberately. |
| CLI events and parameter diagnostics | `tools/render.cpp`, `tools/parameter_info.cpp`, `tools/render_fixture.py`, `tools/verify_render.py` | Admit `select_preset` consistently: either manual, index 0, finite integer value 0-11. Add the diagnostic event spelling and update 45-count help. Retain ordering, bounds, rejection and old event syntax. |
| Registry/state dependencies | `include/hammond/ParameterBridge.h`, `src/ParameterBridge.cpp`, `data/parameter-registry.json`, `tools/validate_parameters.py`, `include/hammond/ControlStateIO.h`, `src/ControlStateIO.cpp` | Separately owned implementation of the frozen append-only 47 records, literal selector conversion and canonical state4 grammar. All adapters consume these contracts rather than duplicate conversion or parsing. |

The inspected `plugins/vst3/Processor.cpp`/`.h` already size queues by
`kParameterCount`, validate IDs through the descriptor API, pass complete copied
restores to HostTimeline and publish the resulting full snapshot. Its
`setState`/`getState` paths need acceptance with new values, not a second selector
implementation. `plugins/vst3/StateStream.cpp`/`.h` and
`apps/standalone/StateFiles.cpp`/`.h` delegate to the shared parser/serializer and
need no preset-specific grammar. Preserve stream bounds, short transfer/error
handling and existing file publication behavior.

`src/InputProcessor.cpp` is deliberately note-only. `ScriptedInput.*` transports
ordinary keyboard/pointer events and needs no new musical parser. `MidiInput.*`
retains its permanent B-bank CC targets: a MIDI drawbar edit must neither select
B nor clear a sounding fixed mode. No new MIDI program or note mapping follows
from the new selectors. Preserve `plugins/vst3/PluginIds.h` unchanged.

## Publication layout and lost-field hazards

The core exchange can keep its existing count formula, yielding 50 cells:

| Cells | Payload |
|---|---|
| 0-35 | Four retained drawbar banks, unchanged order |
| 36 | Expression binary64 bits, including signed zero |
| 37-38 | Remembered upper/lower bank |
| 39-42 | Four percussion values |
| 43-44 | Two pedal positions |
| 45-46 | Raw upper/lower `FixedRegistration`, 0-9 |
| 47-48 | Upper/lower route bits |
| 49 | Acknowledged sequence |

Cells 45/46 are **not** the values of parameter IDs 20480/20481. For example,
cancelled upper C# stores fixed mode 1 and route false while its effective
selector is 0. Storing only 0 destroys the remembered C#; storing only a fixed
selector also cannot recover the remembered adjustable bank.

Standalone currently packs 36 drawbar bytes into words 0-4 and uses 22 words
total. Word 4 bits 32-63 are unused. One bounded layout is raw fixed bytes at
word 4 shifts 32 and 40, each masked with `0xff`, keeping the current 22-word
size. Assert the existing 2 manuals x 2 banks x 9 positions shape before relying
on those free bytes, and assert that fixed values 0-9 fit the chosen field.
Do not overlap word 5: it already holds bank/route/percussion/pedal fields.
An explicitly added payload word is also valid if encode/decode/count change
together; the chosen layout needs its own exhaustive round-trip evidence.

Both omissions can evade superficial testing. StateExchange's pending-save
path returns `latest_accepted_` intact, but its acknowledged-save path decodes
atomic cells. Test both. Session's Engine can keep sounding a fixed row while
its published UI copy falls back to None; after acknowledgment `UiModel::observe`
adopts that copy, and a later unrelated whole-snapshot UI edit can erase the
audio mode. Exercise the complete post/render/read/observe/edit sequence.

## Raw host anchors and applied selection

`HostTimeline::process` already has the required command behavior. Descriptor
iteration is numeric-ID order; restores occur first, parameter controls precede
notes, carried same-ID zero points precede fresh zero points, and equal-time
points within a queue are last-wins. Preserve these exact properties.

Old bank IDs 8208/8209 and new selector IDs 20480/20481 are interacting commands.
When both emit at one sample, the higher-ID selector acts last, regardless of
the host's queue enumeration order. Direct Engine and standalone FIFO events
retain their supplied order instead. A repeated explicit old bank-B point must
leave fixed mode and reconnect B even if its normalized value is unchanged.
The core dependency is `src/Engine.cpp`'s old `SelectBank` no-op guard: it must
consider fixed mode before skipping `ControlState::select_bank`.

Keep `CurveCursor::active`, the raw-anchor update and the `explicit_point`
exceptions. An absent or empty queue does not issue a cached selector command;
an unchanged interpolated plateau does not reassert a route. Explicit points
still dispatch even when plain and normalized values match their prior values.

`normalized_anchor` reports the last rendered raw normalized value for that
parameter. It is not an applied-routing query. For example, old upper-bank
anchor 0.6 selects B; a new fixed key changes the route while the old anchor
remains bitwise 0.6. An explicit later old-bank point at 0.6 selects B again.
Whole-state restore intentionally resets all anchors: old IDs from remembered
banks, new IDs from the effective Cancel/fixed/bank helper. **Never recalculate
or quantize all anchors from Engine after every callback.**

The controller's `values_` has the same distinction. `setComponentState` should
load Cancel as normalized 0 for new IDs, while old bank IDs still show the
remembered bank. `setParamNormalized` continues caching the accepted raw value
and does not acknowledge processor execution. Applied native labels must use
`view.applied.controls`, with fixed mode included in the upper-B eligibility
rule. C/Cancel returns visually to rest while cancelled status remains visible.

## Current47 versus historical45; state4 versus old inputs

Do not replace every literal 45 or 3. Current descriptor enumeration is 47 and
new serialization is state4; old inventories and old documents remain evidence.

| Exact test files | Required distinction or additional coverage |
|---|---|
| `tests/test_parameters.py`, `tests/test_parameter_bridge.cpp`, `tests/test_parameter_bridge.py` | Add the two exact IDs/records, registry schema4/model, 46 discrete parameters, new boundaries and canonical values. Retain old39/old43 guards and add the full old45 digest. Extend unknown-ID-hole coverage through 20482. |
| `tests/test_host_timeline.cpp` | Keep the old45 threshold fixture as a named legacy test or extend it with a separate new-selector oracle. Current `id >= 0x4000` classification wrongly treats new 0x5000/0x5001 as eight-step pedals. Add a current47 reverse-enumerated queue test and alias/carry/rollback cases. |
| `plugins/vst3/tests/test_native_abi.cpp`, `test_native_controller.cpp`, `test_native_behavior.cpp`, `test_native_automation.cpp`, `test_native_concurrency.cpp` | Update current export/array/out-of-range tests to 47 and boundary index47. Add literal new targets. Automation's `physical_control` currently treats every index >=43 as a pedal; extend it explicitly. Preserve old45 score coverage, raw host cache checks and UUID expectations. |
| `tests/test_control_io.cpp`, `tests/test_pedal_controls.cpp`, `tests/test_state_exchange.cpp`, `apps/standalone/tests/test_standalone_state_files.cpp` | Retain literal v1/v2/v3 inputs, add independent canonical v4 output and migration from a destination containing fixed modes. `test_control_io.cpp::same_snapshot` enumerates fields and must add fixed modes. Pattern generators in exchange/session tests must actually vary them. |
| `plugins/vst3/tests/test_native_controller.cpp` | `old_state` currently manufactures legacy input from the current writer by changing the version/removing pedals and percussion. State4 also has catalog/fixed tokens: replace this dependency with retained independent legacy inputs. A bare/malformed state4 still rejects; unsupported-version coverage should separately use a genuinely unsupported version. |
| `tests/test_pedal_catalog.py`, `tests/test_install.py` | They currently require the active registry to equal the historical pedal catalog's v3/count45. Preserve `examples/fixtures/pedals/pedal-catalog-v1.json`; compare its frozen old45 records/digest with the corresponding subset of current47. Installed CLI enumeration must expect 47. |
| `apps/standalone/tests/test_standalone_ui.cpp`, `test_standalone_external_control.cpp`, `test_standalone_session.cpp`, `test_standalone_concurrency.cpp` | Update current parameter coverage and exercise raw-mode publication, effective applied selection, pending/rejected snapshots, repeated old-bank selection and fixed-state equality/dirty tracking. |
| `apps/standalone/native_tests/test_standalone_app.py`, `test_standalone_workflows.py`, `test_standalone_midi_replay.py`, `test_standalone_chapel.py`; `apps/standalone/tests/test_standalone_benchmark.py` | Add fixed-mode fields to exact diagnostic shapes/dictionaries. Keep legacy input bytes intact; update actual Save expectations to independent state4 bytes. No-Save tests must still prove old input files are unchanged. |

The old45 record digest is
`13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad`.
Compare complete records sorted by numeric ID using compact sorted-key ASCII
JSON, not only IDs or first-array-position assumptions.

`tools/chapel_controls.py` is an explicit legacy B3CONTROLS3 **bank-copy audition**
producer with its own documented contract. Do not silently turn it into fixed
selection or rewrite retained chapel demonstration files. Its native acceptance
currently expects Ctrl+S bytes to equal the original v3 export; separate the
unchanged legacy input oracle from the new state4 save oracle. If the integrator
chooses to advance that producer's output grammar, assign its writer, validator,
`tests/test_chapel_controls.py` and documentation together while retaining old
input fixtures. State4's version number does not automatically change the
independent render/report schema version 3.

## Acceptance targets before adapter closure

1. **Both publication paths:** all 100 fixed-mode pairs x 16 remembered-bank/
   route combinations, other fields preserved, signed expression zero intact.
   Cover pending and acknowledged save, multiple queued restores, invalid hidden
   enums, queue-full/rejection, exhaustion and concurrent read/write patterns.
2. **Control ingress:** admit SelectPreset through PerformanceInput and Session;
   reject invalid manual/index/fraction/range/nonfinite values with the existing
   transaction guarantees. Cover zero-frame dispatch and stable mixed-note ties.
3. **Host aliases:** same-sample old/new controls in reversed queue enumeration,
   explicit repeated B while fixed, Cancel with retained fixed memory, empty/
   absent queues, interpolation plateaus, endpoint carry, restore-plus-carry,
   fresh-over-carried ties, callback partitions and full rejection continuation.
   Assert raw fractional anchors independently of effective routing.
4. **Native controller/processor:** actual 47 descriptor exports, index47
   rejection, both new conversion laws, raw cache preservation, effective restored
   selectors, state1-4 input, exact state4 output, malformed catalog/short streams,
   queued state/automation precedence, stable UUIDs and held-note history.
5. **Standalone/UI/CLI:** real post/render/read/observe flow; fixed selection
   survives unrelated editing and MIDI B-bank drawbar edits; applied labels and
   eligibility are correct; preset release creates no note-off or owner.
   Exercise all three score validators and actual parameter-info output, plus
   native Load/Save and exact diagnostic fields.
6. **Callback constraints:** extend `tests/test_realtime.cpp`,
   `tests/test_realtime_console.cpp`, `tests/test_performance_acceptance.cpp`,
   `plugins/vst3/tests/test_native_realtime.cpp` and
   `apps/standalone/native_tests/test_standalone_callback_allocation.cpp` with
   affected selector/publication paths as appropriate. Keep existing lifetime,
   allocation, timing and source-coherence qualifications distinct.

Build tests from one coherent source before running their named CTest targets
with `--output-on-failure --no-tests=error`. Core/standalone support tests are
available without a native SDK; actual VST3 and SDL tests require the existing
documented enabled configurations. This audit ran source inspection and identity
checks only. Physical latches, loaded gains, real-device/DAW qualification and
literal visual equality remain separate gates.
