# Independent fixed-registration VST3 acceptance

A29, `/root/w05_a29_vst3_acceptance`, 2026-11-14. The independent review found
**no new native production defect**. The current selector integration preserves
the declared native boundary. Its validator diagnostics match the preserved
baseline exactly and follow the pinned SDK's conflicting cleanup expectations.
No processor or SDK behavior was changed to remove those messages.

This assignment reviewed **retained executions and exact source**, then ran
independent file, registry and rational-number audits. It performed **zero new
native test invocations**. The [A22 execution](PRESET_VST3_INTEGRATION.md) remains
the source of the actual eight-suite result. The
[A29 execution record](../development/2026-11-14-preset-continuation/29-vst3-acceptance.md)
and [structured audit](../development/2026-11-14-preset-continuation/reports/a29-vst3-acceptance.json)
identify the scope and compared bytes.

## Validator diagnostics: exact baseline comparison

The baseline and A22 logs contain identical ordered diagnostic patterns:

| Retained observation | Count | Exact explanation |
| --- | ---: | --- |
| General `Valid State Transition 32bits` teardown | 1 | The supported-format test completes its final terminate/reinitialize cycle in the inactive state. Its inherited teardown then calls `setActive(false)` again and treats the declared rejection as a cleanup failure. |
| General `Valid State Transition 64bits` teardown | 1 | Setup returns early for unsupported float64 without activating. The run reports unsupported precision and returns success; teardown then tries to deactivate the already inactive instance. |
| Double-precision processing-suite teardown | 14 | The same unsupported-format early return and unconditional deactivation occur for each processing test. These are skipped-format paths, not 14 successful float64 processing cases. |
| Positive unsupported-rate setup diagnostics | 9 | The format test logs the rejected setup attempts but does not return failure for that branch. |
| Final plugin-validator summary | 47 passed / 0 failed | The SDK counts `run()` results before teardown. A teardown diagnostic does not increment its failed-test counter. This count is unrelated to the plugin's 47 exported parameters. |

The fourteen double-precision cases are Process Test; processing in another
thread; Silence Flags; Silence Processing; the three parameter-flush forms;
Variable Block Size; Process Format; Parameter Bypass persistence; stereo and
mono arrangement tests; and block/sample parameter-accuracy tests. The
structured audit retains their exact names and suite context.

The SDK's
[repeated-state test](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/state/repeatidenticalstatetransition.cpp)
explicitly requires a second identical inactive transition to reject. In
contrast, [processing teardown](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/processing/process.cpp)
unconditionally requires deactivation success and returns before the base
cleanup when it fails. The
[valid-transition test](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/state/validstatetransition.cpp)
explains the supported-format inactive ending. The
[validator runner](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/samples/vst-hosting/validator/source/validator.cpp)
explains the counting policy. The project retains the changed-state lifecycle
already documented and independently exercised by its native ABI suite.
The SDK summary alone does not establish complete cleanup, absence of leaks or
successful unsupported-format processing.

The rejected rates are 22,050; 32,000; 88,200; 192,000; 384,000; 1,234.5678;
12,345.678; 123,456.78; and 1,234,567.8 Hz. The log formats the first fractional
rate to 1,234.568 Hz. The
[format test](https://github.com/steinbergmedia/vst3_public_sdk/blob/586dc5e6c8012c3e4b01c79389375cbe96bdb1da/source/vst/testsuite/processing/processformat.cpp)
contains those exact inputs and logs setup rejection without a failing return.
Both retained executions explicitly process 44,100, 48,000 and 96,000 Hz.
Supported precision remains float32; supported rates remain those three values.

## Independent selector-boundary review

| Boundary | Independent finding |
| --- | --- |
| Public identities | The 45 complete historical JSON records equal `b79086f` byte-canonically; their digest remains `13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad`. Only IDs 20480/20481 are appended. |
| Native conversion oracle | All twelve canonical values and eleven thresholds in the native test-only oracle are nearest binary64 to their exact rational values. The audit compares each literal's rational distance with both adjacent representable values and checks even parity on ties, without using production conversion code. |
| Native descriptors | The controller enumerates the shared 47-record table and eleven-step selectors. The processor's queue bound derives from `kParameterCount`; its existing fixed storage, descriptor admission, duplicate-queue rejection and 1,024-record total budget apply to the added IDs. |
| Controller cache | `setParamNormalized` validates through the bridge and retains the original accepted double. Old-bank and new-selector writes do not rewrite each other's cache. Audio cannot mutate this UI-thread array. |
| State projection | `setComponentState` parses a full candidate, derives all 47 values into a temporary array and publishes once. New values use the checked effective selector; old bank values retain remembered A/B identity. Cancel-hidden fixed memory remains in processor state. |
| Automation aliases | HostTimeline, not the native wrapper, owns ordered reconstruction. A22's actual native tests separately cover reverse queue order, absent/empty queues, unchanged discrete plateaus, repeated old-bank points, endpoint carry, four queued restores and same-sample fresh ties. Their expected physical events and native oracle are separate from production mapping. |
| Native streams | Unchanged `StateStream` delegates to current shared state I/O. It preserves the 16 KiB limit, short-transfer/progress checks and destination atomicity. The current writer is state4; readers 1/2/3 remain migrations into `None` fixed modes. This is upgrade compatibility, not a downgrade writer for old plugin versions. |
| Factory and binary boundary | Factory, UUID, Processor and StateStream source bytes match `b79086f`. Both bundle metadata files are byte-identical. The new module binary has its own hash; binary equality or a new binary ABI claim is not inferred. |

The review checked A22's existing independent state literals, raw-cache tests,
all-selector automation, invalid new-queue rollback and subsequent audio
continuations for a missing acceptance case. No concrete untested native risk
requiring another regression was identified. Repeating the same eight suites
would not add an independent oracle, so no redundant native run was added.

## Documentation correction and remaining gates

Updated the current [controller contract](../VST3_CONTROLLER.md) and
[processor contract](../VST3_PROCESSOR.md) to 47 parameters, state4 with legacy
readers, raw/effective selection, cached host values and alias ordering. Their
older 45-parameter qualification counts remain explicitly historical. Supported
precision/rates, lifecycle, UUIDs and capacity meaning are preserved.

A29 matched **72 selected native/core/data inputs** to A22's final source
manifest, including native tests and the fixed-data generator/catalog inputs.
This is a selected-input comparison, not a fresh whole-tree build. Root retains
the final integrated-source/platform gate. DAW behavior, native device timing,
physical fidelity, host-specific cleanup and measured instrument calibration
remain outside this review.
