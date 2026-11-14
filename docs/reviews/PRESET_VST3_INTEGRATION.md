# Fixed-registration VST3 integration

Author qualification by A22, `/root/w04_a22_vst3_integration`, 2026-11-14.
The native adapter now consumes the frozen
[selection](../PRESET_SELECTION_CONTRACT.md) and
[state/parameter](../PRESET_STATE_PARAMETER_CONTRACT.md) contracts. The final
fresh Linux Release configuration passed **8/8 selected CTest suites** in
**2.52 seconds**. This is implementation-owner evidence; the continuation's
later independent native acceptance and publication remain separate.

The checked source is a copied, uncommitted integration snapshot over checkout
HEAD `35554c068492fe2b20c1f8a602d8354ae762dc42`, not that commit alone. The
[A22 record](../development/2026-11-14-preset-continuation/22-vst3-integration.md)
retains exact commands, source and artifact hashes, initial failures, test
counters and the pinned SDK identity.

## Production change and preserved boundaries

`Controller::snapshot_plain` now handles `EventType::SelectPreset` through the
checked `control_preset_selection` helper. `setComponentState` prepares all 47
normalized values before one cache assignment. The new selector reflects Cancel
for a disabled route, the fixed key when present, or bank A/B otherwise. The old
bank parameters continue to reflect the remembered adjustable bank. A cancelled
fixed mode therefore remains present in processor state even though its new
controller selector displays zero.

`setParamNormalized` still stores the exact accepted host value, including a
fractional normalized value or negative zero. Writing an old bank parameter
does not rewrite the new selector's cache, and writing a selector does not
rewrite the old bank cache. Audio execution does not acknowledge or replace the
controller's host values. Explicit `setComponentState` remains the operation
that refreshes every cache value from restored controls.

The native controller exposes **47 parameters**. The appended identities are
20480/20481, `manual.upper.preset_selection` and
`manual.lower.preset_selection`, with `preset-key-index` units, plain range
0–11, default 11 and eleven steps. Existing pedal controls remain eight-step
controls. Current enumeration rejects index 47; all first 45 records and their
meanings remain governed by the append-only bridge contract.

No Processor, StateStream, factory, UUID, root CMake or plugin CMake algorithm
was changed by A22. Processor already sizes its queues from `kParameterCount`,
admits identities through the shared bridge, submits whole restores to
HostTimeline, and publishes full snapshots. StateStream continues to delegate
the grammar to shared control I/O with its existing 16 KiB limit and short-stream
handling. The real module exercised those paths with the new fields. No second
selector implementation or state parser was introduced into the adapter.

The preserved processor class is `19F9ADC0-533F-42B4-B96B-D51D6547E838`; the
controller class is `0DEE76AB-26BC-475A-BF64-F138C89FB0E0`. Actual factory and
component-interface checks retained the independent expected identifiers.

## Native evidence

| Suite | Observed final result | Relevant coverage |
|---|---|---|
| `test_native_controller` | Pass; 138,215 checks; 3,984 threshold cases; 411 string round trips; 469 rejected streams; 1,600 selector restores | Independent literal 47-record inventory; eleven-step selectors versus eight-step pedals; all four standard rounding modes; canonical values; exact state4 output; literal state1/2/3 migration; raw host caches; transactional rejection and silent component-handler behavior. |
| `test_native_abi` | Pass; 47 descriptors; 2,140 conversions; 1,673 accepted callbacks; 3,207 state round trips | Actual dynamically loaded module and unchanged UUIDs; all 1,600 fixed/bank/route combinations through pending and acknowledged saves; new restored selector versus old retained bank; exact legacy-to-state4 bytes; lifecycle and audio checks. |
| `test_native_behavior` | Pass; 1,066 accepted and 75 rejected callbacks; 62 rollback cases; 618,550 bitwise channel samples | Reverse-enumerated current47 targets, independent literal legacy input, queued fixed restores while notes remain held, invalid new selector queues, future continuation after rejection, original ownership/output/curve cases. |
| `test_native_automation` | Pass; zero maximum audio error; 204,312 bitwise channel samples | Original six legacy45 curve scores retained; 72 new selector commands, 198 new threshold cases, three alias cases, three fixed restore/carry cases and nine new curve-partition cases across 44.1/48/96 kHz. |
| `test_native_concurrency` | Pass; zero maximum audio error; 3,072 stress loads and 3,072 publication-only saves | Raw fixed fields vary in both UI and audio generations; all 47 explicit control queues populate each audio generation; pending and acknowledged publication preserve full snapshots under the existing thread stress. |
| `test_native_realtime` | Pass; 193 measured native call regions; zero observed C++ allocations or deallocations | 54 accepted selector-specific callbacks, 90 fresh selector/alias records, three carried records and 24 queued restores; invalid selector rollback plus all previous enabled/dense/maximum/output/lifecycle probes. |
| `hammond_vst3_validator` | Pass; **47 SDK internal checks**, zero counted failures | Actual native module, metadata, processing and state checks. These 47 SDK checks are a different count from 47 exported parameters. |
| `test_native_install` | Pass; two Python methods; four-file installed payload; relocated ABI suite passed | Installed module/metadata/notices match the built bundle; actual relocated module repeats the ABI qualification, including 47 exports and 3,207 state round trips. |

The SDK validator's separate **build-time selftest ran 51 checks with zero
failures**. It is neither the plugin's 47-check validator run nor another CTest
suite. Required discovery used `^(test_native_|hammond_vst3_)` with
`--no-tests=error`, after building `hammond_vst3_test_inputs`; all eight discovered
tests actually ran and none were skipped.

### Selection, aliases and history

The automation suite names and preserves its original 45-control score. Its
independent physical-target dispatcher now explicitly maps positions 45/46 to
upper/lower `SelectPreset`, and restricts the pedal branch to positions 43/44.
The new selector expectations come from test-only literal canonical values and
thresholds in `NativePresetOracle.h`, separate from production ParameterBridge.
The independent parameter-oracle owner supplies the separate rational proof of
those values; this native test does not claim another rational derivation.

Every selector value 0–11 on each manual reaches the actual processor while
upper/lower notes and pedals remain held. Exact thresholds and both adjacent
binary64 values also reach the module. Reverse queue enumeration proves that
old bank IDs act before the higher new selector IDs at one sample. Absent and
empty queues leave the applied route alone. Changed normalized values on an
unchanged old-bank or new-selector plateau do not reassert their route before
an explicit endpoint. The carried endpoint does reassert it on a zero-frame
callback. Repeated old bank B leaves fixed mode and reconnects a cancelled route.

New Cancel retains the raw fixed mode and remembered bank. A separate real curve
primes both a carried selector and a carried note; four queued state4 restores
then precede carried and fresh commands. Fresh duplicate selector points are
last-wins, controls precede notes, and a carried press followed by a fresh
release leaves no extra owner. Zero-frame processing does not advance the direct
reference clock. The actual native audio and subsequent continuation match the
continuously running direct Engine bit for bit. No internal native phase or
contact diagnostic was substituted for these actual module/audio checks.

The old bank's fractional anchor is tested indirectly through subsequent native
curve timing and alias behavior. The controller cache is tested directly:
accepted values 0.6, 0.12345678901234567 and negative zero survive processor
automation and state activity. Explicit controller state refresh then yields
the effective fixed/Cancel values while preserving remembered bank B.

### State and publication

The ABI suite exercises 100 fixed-mode pairs times all 16 remembered-bank and
route-bit combinations through the real component. It compares pending save
bytes with the supplied state4, processes a zero-frame acknowledgment, compares
the decoded save bytes again, and restores the actual native controller.
The controller suite independently checks the same 1,600 effective-selector
combinations against remembered-bank values. These are different paths through
the same valid input space, not 3,200 distinct valid snapshots.

The controller's former `old_state(current_writer_output, version)` helper has
been replaced with literal state1/2/3 inputs. The behavior suite had a second
writer-derived legacy fixture; it now uses independent legacy grammar too.
Legacy input remains legacy input. Current output is checked against separately
spelled state4 records, including catalog identity, raw `fixed_registration`
tokens, both remembered banks and both route bits. Legacy reads into a snapshot
containing nonzero hidden fixed modes clear them to None. Malformed catalog,
numeric fixed token, truncation, unsupported version, stream faults and oversize
input preserve controller values.

### Allocation, concurrency and validator diagnostics

The allocation test retains its Linux ELF isolation/interposition proof and
12/12 overload calibration. The selector path adds accepted zero-frame and
positive callbacks, four-state restores, old/new conflicts, carry/fresh ties,
same-value legacy reassertion, and invalid selector continuation. All **193**
measured regions reported zero calling-thread global C++ `new`/`delete` activity.
The test does not measure every allocator family, another thread's activity,
operating-system deadlines or a physical audio device.

Concurrency counters depend on scheduling. The recorded final run observed
1,453 callbacks, 17,218 successful saves, 51 bounded busy saves and 66,651 exact
audio frames, with fixed-mode patterns varied. These observations qualify that
run; the stable scenario counts are the three supported rates, 24 coordinated
rounds, 3,072 accepted stress loads, 3,072 publication-only saves and 96 reader
pause callbacks.

The SDK plugin validator returned success while retaining **16** `Failed to
teardown test!` lines and **nine** unsupported-rate `setupProcessing` errors.
The unsupported-rate probes were 22050, 32000, 88200, 192000, 384000, 1234.568,
12345.678, 123456.780 and 1234567.800 Hz. It reported successful 44100, 48000 and
96000 Hz processing and unsupported 64-bit processing. These diagnostics are
retained alongside the SDK's final “47 tests passed, 0 tests failed” result;
success is not described as a diagnostic-free validator run or support for
additional rates/precisions.

## Initial failures and correction

The first configure attempt selected Ninja, which was unavailable. It failed
before compilation. A separate new Unix Makefiles build configured and compiled
successfully with the supplied CMake 4.4.4 and GCC 14.2.0. Neither preserved
`build-baseline` nor preserved `build-native` was reconfigured or rebuilt.

The first native CTest run passed **7/8** in **3.03 seconds**. Only the new
controller migration expectation failed: its fixture construction replaced
17 bytes for the 18-byte literal `pedal drawbars 7 3`, retaining a stray digit.
The state reader and native module had already passed the other suites. The
test-only correction uses `std::string_view::size()` for literal replacement
lengths. Only that test target recompiled; the native module and all production
source remained unchanged. The final executed eight-suite run passed as recorded
above. The original log and source-manifest identities remain in the A22 record.

## Remaining acceptance

The integrator owns later independent native acceptance, complete coherent
application/CLI integration, shared status and setup documentation, publication
and hosted gates. A22 did not run sanitizers, macOS, Windows, a DAW, a hardware
MIDI controller, a physical audio device or the standalone UI. The generic VST3
controller still has no custom editor. The fixed table remains a documentary
nominal registration model; no physical multi-latch, contact/loading, measured
gain, organ/Leslie fidelity or full M9 release claim follows from these tests.
