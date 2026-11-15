# Native MIDI recovery and callback ownership review

Actual reviewer: `/root/w08_a47_native_recovery_review`, A47, wave 8,
15 November 2026 UTC. Scope: the current CC120/121 and expression-calibration
paths, transport retirement, discovery, release acknowledgment and exceptional
shutdown. This is an independent source review and evidence admission; A47 did
not configure, build, run CTest, exercise a device or change production/tests.

## Decision and reviewed source

**No new application-level ownership or epoch defect was found in these feature
paths. One source-proven native-close error-observability gap remains:** the
pinned WinMM/CoreMIDI dependency can clear its connection state without reporting
a failed native close. The adapter's entered-callback counter cannot repair that
missing OS lifetime guarantee. This is a concrete next native safety gate,
not an observed use-after-free, driver failure or physical-device result.

At review start, inspected HEAD/tree were `d556da017ea0a5d4f2d231416782dbc5066e58c2` /
`a3150fd2489a50a430b02c01eadd5e0c180bc7f9`. A read-only
`git ls-remote origin refs/heads/main` returned the same commit during this
review. The checkout also contained other workers' uncommitted fixture,
installer, gallery and documentation changes; that remote observation does not
publish those files. The [A47 source receipt](../development/2026-11-15-product-continuation/reports/A47-native-recovery-review.json)
pins the inspected inputs and distinguishes retained results from A47 checks.
During final checks, the integrator advanced local HEAD to
`d8c39f7986746eacc991747153c7dbb012bb9a32`, tree
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`, a child of that starting source.
All fourteen source inputs named in the current native-calibration summary and
the production executable still matched. The earlier remote query is not a
remote verification of this later local commit.

| Critical input | SHA-256 |
| --- | --- |
| `apps/standalone/main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |
| `apps/standalone/MidiDevice.cpp` | `48ee8dbe72a1a243fcc3bc1037df782690894cb26ef2291ba253611b48bfc324` |
| `apps/standalone/MidiInput.cpp` | `4ddd655fb4a21040f2f83228fb23e38f98d0abe21d5bce7f0e28d064b5b7477c` |
| `apps/standalone/Session.cpp` | `256c0ef82e5a6639b3437d01754a0b27673a9d4096fe099a8b66351818ef2ae3` |
| Existing native application, inspected but not executed | `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852` |

This review builds on the accepted [A26 lifecycle note](../development/2026-11-15-product-continuation/notes/A26-native-calibration-lifecycle.md)
and [A38 integration review](PRODUCT_INTEGRATION_REVIEW.md); it does not repeat
their build graph, installer portability or general compatibility audits.

## Ownership and the feature paths

| Boundary inspected | Reasoning and source |
| --- | --- |
| Native acquisition to main | [`MidiDevice.cpp`](../../apps/standalone/MidiDevice.cpp), lines 146–221, gives callbacks a stable `Impl`, an inbox pointer and atomic cells. Input copies complete short packets; error callbacks only close admission/latch faults. The producer flag rejects overlapping wrapper input rather than making a second SPSC writer. No callback accesses calibration, UI, Session or Engine. |
| Inbox publication | [`MidiInput.cpp`](../../apps/standalone/MidiInput.cpp), lines 46–124, publishes payload after a release store and acquires the opposite cursor before reading/reusing a slot. Error reporters change only atomic fault bits. Reset is a separate quiescent operation; a packet that passed a fault check before publication may escape once and is covered by subsequent ownership retirement. This is not transactional lossless fault delivery. |
| Immutable calibration | `MidiInput.cpp`, lines 153–169, validates before mutation and copies route/calibration together only into an inactive decoder. The accessors and all decode calls belong to main. OS callbacks never hold references to these values. Applying changed settings cannot race a callback's calibration read because that read does not exist. |
| CC120 | `MidiInput.cpp`, lines 244–258, creates the distinct scoped command. [`Session.cpp`](../../apps/standalone/Session.cpp), lines 71–80 and 282–321, validates its domain/bus/channel before sequence/slot publication. Lines 490–511 check ideal contacts before reducing it through existing ownership processing. It neither closes a transport nor mutates decoder configuration. |
| CC121 and CC11 | `MidiInput.cpp`, lines 254–271, resets normalized expression directly to 1.0 for CC121, while CC11 alone uses calibration. [`main.cpp`](../../apps/standalone/main.cpp), lines 1671–1692, dispatches each control through `UiModel::external_parameter` before the next packet. Pending UI values share that desired-state path; there is no callback-side control write or new Session producer. |
| Audio ownership | Main alone posts; Session render alone applies queued commands and updates musical ownership. `Session.cpp`, lines 342–390, fixes a callback prefix and publishes recovery afterward. [`AudioDevice.cpp`](../../apps/standalone/AudioDevice.cpp), lines 215–228, closes SDL audio before calling Session stop. The MIDI changes add no Engine thread entry. |

The acquire/release proof above covers application-owned memory under the
declared single-producer and successful native-retirement preconditions. It does
not establish that upstream native parsing is serialized: WinMM/CoreMIDI touch
their own message storage before entering the protected wrapper. Address/undefined
behavior sanitizers also do not constitute a thread-race detector.

## Reopen, discovery and shutdown barriers

`request_midi` validates first, preserves an identical healthy active request,
and otherwise calls `retire_midi` (`main.cpp`, lines 1463–1506). Retirement ends
decoding, closes the device with admission disabled, and calls `reset_quiescent`
only after `is_quiescent` succeeds (lines 1335–1368). It then submits Upper,
Lower and Pedal releases once in order. A partial failure clears the saved final
sequence, records failure and never retries the batch or silently opens a new
input (lines 1370–1380).

`observe_midi_retirement` requires both resolved and actually applied sequence
to reach the final release, a later completed global recovery, or closed audio
plus a prepared/stopped Session (lines 1384–1397). Queue admission or an open but
paused callback is insufficient. `start_pending_midi` consumes one pending
request and refuses nonquiescence, stopped audio and poisoned shutdown before
starting the copied new epoch (lines 1400–1445). Failed activation retires any
admitted prefix. Neither failed opens nor runtime faults reconnect automatically.
Session queue failure retains its declared global recovery scope; it cannot be
advertised as MIDI-only release.

[`MidiDiscovery`](../../apps/standalone/MidiDiscovery.h) owns one worker/result.
The worker publishes its value result with release; main acquires completion
and joins before moving strings/vectors. The query owns no live device, inbox,
UI or Session. Current modal generations and action revisions prevent an old
result replacing new choices or an Apply result (`main.cpp`, lines 1991–2051).
Nonempty Apply requires completed current discovery (lines 2200–2214). Startup
connection precedes event processing. Those constraints serialize first
CoreMIDI singleton initialization despite RtMidi's process-wide client; they
do not turn the separate query into an independent native client.

On ordinary shutdown, MIDI retirement precedes audio close; outstanding discovery
is then joined and any late error retained (lines 653–676). Exception unwinding
also closes MIDI/audio before members disappear; `MidiDiscovery` joins on
destruction, and the enclosing SDL lifetime outlives `Application` (lines
492–498, 2488–2500 and 2644–2668). Blocking native close/discovery calls have no
portable deadline. The adapter's 250 ms guard starts only after native close
returns, so it is not an OS shutdown or UI responsiveness bound.

## A47-N1: native close failures can evade quarantine admission

The source is RtMidi **6.0.0**, commit
`1e5b49925aa60065db52de44c366d446a902547b`. The read-only external `RtMidi.cpp`
hash is `184d775e88e5d73b079897363fb42af155122e879f0bc9254a1c7edae4eadb3c`.
The [lock](../../data/dependencies/rtmidi-lock.json) admits only the two existing
CoreMidiData value-initialization changes, producing prepared hash
`240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a`.
Those changes leave the close paths below unchanged.

- In pinned `MidiInWinMM::closePort`, lines **2910–2934**, `midiInReset`,
  `midiInStop` and the final `midiInClose` return values are ignored. The native
  handle and `connected_` are then cleared. The application's zero-SysEx-buffer
  configuration avoids the intervening buffer loop; it does not check the
  final native result. [Microsoft's close contract](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-midiinclose)
  distinguishes success from errors, including insufficient memory. Queued-buffer
  failure is not asserted reachable in this zero-buffer application.
- In pinned `MidiInCore::closePort`, lines **1274–1288**, endpoint/port disposal
  results are ignored before handles and `connected_` are cleared. Apple's
  [port-disposal API](https://developer.apple.com/documentation/coremidi/midiportdispose(_:).md)
  returns an OSStatus; its documentation does not supply the stronger guarantee
  that this wrapper has observed every callback retire.
- `MidiDevice.cpp`, lines **242–287**, sees only exceptions, its error callback,
  the dependency's stored open flag and `entered_`. A native failure suppressed
  by the dependency therefore need not set `close_fault_`. At a moment with no
  wrapper callback entered, cancellation and `input_.reset()` can follow.
  `is_quiescent` then permits inbox reuse (lines **536–539**).

The specific unsafe interleaving to test is: an active old connection receives
changed calibration; its native close fails but RtMidi clears the stored flag;
the wrapper observes zero entered callbacks and destroys RtMidi; a pending old
native callback subsequently resumes. Actual CoreMIDI and WinMM callbacks first
dereference RtMidi `inputData_`/`apiData_` (pinned lines **988–998** and
**2692–2707**) before they could enter `MidiDevice::input_callback`. Consequently
the wrapper counter cannot protect that earlier access. This interleaving is a
source-supported risk model, **not an executed reproduction**.

There is a related limit on destructor-reported errors: the post-reset check at
`MidiDevice.cpp` lines **281–285** can retain `Impl` and the inbox, but cannot
restore RtMidi storage already destroyed by `input_.reset()`. The ordinary
poison path before cancellation/reset does retain that storage. The app correctly
retains its one inbox with a poisoned device (`main.cpp`, lines 339–346), refuses
replacement/reopen and requires process restart. This distinction matters when
describing exactly which objects a failed-close test protects.

**Narrow next gate/proposal:** use an isolated, source-identified build of the
pinned prepared dependency with platform API fault injection below RtMidi.
Inject failing WinMM close/reset/stop and CoreMIDI disposal results while holding
a callback before wrapper entry. Verify the current behavior, then review a
checked-close change that reports the native failure and preserves the native
handle, callback data, adapter context and inbox before any destructive cleanup.
Require poisoned/no-reopen/no-reset behavior plus successful ordinary teardown
with no leaks. A successful close still needs platform-specific callback-retirement
evidence; merely checking return codes does not supply it. Keep production and
locked dependency sources unchanged until that bounded repair is owned and
reviewed. No new leak exception is proposed.

## What the retained fixtures establish, and what they omit

| Evidence or source | Accepted scope and remaining boundary |
| --- | --- |
| [A26](../development/2026-11-15-product-continuation/reports/A26-root-native-calibration.json) and [A38](../development/2026-11-15-product-continuation/reports/A38-root-native-calibration.json) native lifecycle receipts | Real application, discovery and SDL dummy audio; seven lifecycles, ten subprocesses and two intentionally failed replays. They support calibration/route/port retirement, failed-prefix discard, explicit retry and UI-owner preservation. These are retained executions, not A47 runs. |
| Current [calibration facade](../../apps/standalone/native_tests/fake_calibration/RtMidi.h), lines 181–270, and [acceptance](../../apps/standalone/native_tests/test_standalone_native_calibration.py), lines 152–198 and 322–342 | Facade offers occur synchronously while native API methods run on main; acceptance explicitly requires that fact. Close sends two refused offers before clearing its Boolean. Applied-release and no-Apply-expression assertions are meaningful, but no OS callback can be parked before native parsing or deliver a suppressed OS error here. |
| [Backend lifecycle fixture](../../apps/standalone/backend_tests/test_standalone_midi_backend.cpp), lines 612–666 and 764–850 | A worker invokes the actual wrapper during fake close, which waits for that invocation to finish. Six poison cases inject throws, reported errors or a still-open Boolean. Saved callbacks after device destruction target the retained wrapper directly. They bypass native `inputData_` and do not reproduce A47-N1 or prove upstream storage survives destruction. The six cases also do not exercise the 250 ms entered-callback timeout. |
| [Inbox concurrency fixture](../../apps/standalone/tests/test_standalone_midi_concurrency.cpp), lines 555–786; [discovery fixture](../../apps/standalone/tests/test_standalone_midi_discovery.cpp) | Real worker synchronization checks FIFO reuse and fault races with all workers joined before reset; discovery checks nonblocking polling and joined value delivery. Neither links an OS driver. The threaded packet repertoire uses default calibration/CC123; new CC120/121 behavior has separate Session/calibration acceptance. No combined asynchronous-driver/calibration race pass follows. |
| [Current facade repair receipt](../development/2026-11-15-product-continuation/reports/gcc13-facade-repair.json) | Root's ordinary native calibration gate passed in **20.50 s** after the same-value clear/push-back correction. Its summary still records seven lifecycles, ten subprocesses and two deliberate failed replays. Production hashes match the review. |
| [Original expanded sanitizer failure](../development/2026-11-15-product-continuation/reports/d556-native-sanitizer-build-failure.json) and [A37 coverage review](PRODUCT_SANITIZER_COVERAGE.md) | GCC 13 failed building the test facade at `d556da01`; the 21 selected gates did not execute. Repaired-source hosted execution remains a separate required observation. Even a later ASan/UBSan pass of the fake path does not execute a real MIDI callback race or detect all data races. |

The only existing leak-policy exception remains
`test_standalone_midi_backend_quarantine` in
[`apps/standalone/CMakeLists.txt`](../../apps/standalone/CMakeLists.txt), lines
55–66. Ordinary destruction and the new native-calibration gate retain leak
checking. This review adds no exception, test result or hardware claim.

## Verification performed by A47

Read-only source, existing receipt and live remote inspections; matching hashes
for the reviewed production inputs and executable; in-memory verification of
the locked prepared-source transformation; Python syntax checks on the existing
calibration acceptance/driver-adjacent Python sources; and owned Markdown link,
note-size and whitespace checks. The compact receipt records those actual checks.
No compile, shared build, CTest, native execution or sanitizer run was performed.

The immediate integration gate remains the repaired-source hosted 21-test
selection. The next native recovery gate is A47-N1's below-RtMidi checked-close
and callback-lifetime experiment on named platforms. Physical MIDI/audio timing,
hotplug, deadline and device journeys remain unrun here. The audit changes no
47-parameter/state4/readers1–3 contract, shared source ownership or nominal dry
Engine route, and makes no crossover/Engine integration claim.
