# A31 — Independent native MIDI replay acceptance

Actual worker: `/root/w06_a31_native_midi_acceptance`, A31, logical wave 6 of
the `2026-11-14-midi-ui` session. Completed 2026-11-14 UTC. This is one actual
new assignment; no preceding worker or result is recounted.

## Owned result and conclusion

Owned paths are
[`apps/standalone/native_tests/test_standalone_midi_replay.py`](../../../apps/standalone/native_tests/test_standalone_midi_replay.py)
and this note. Root owns production source, CMake, shared records, coordinated
builds and publication. This worker made no production edit, configured or built
no shared directory, spawned no additional worker, and made no commit or push.

**The final independent suite passed 11/11 test methods, launching 12 actual
native application processes in 18.121 seconds.** Eleven application exits were
successful; the deliberate interrupted replay returned the required failure
while still joining shutdown and clearing owners. These are actual
`hammond_standalone --midi-script` runs, with paired `--input-script` where UI
ownership or controls matter. They use the real inbox, decoder, main loop,
UiModel, Session, Engine and SDL dummy audio callback.

The first complete suite had one test-fixture observation-margin failure.
The application had produced the correct musical outcome, but the test required
an acknowledgment within an unnecessarily short 90 ms window. That original
failure, its unchanged musical/counter expectations, the targeted repair check
and the final complete run are retained below. **No production defect was found
by this assignment.**

Inputs read included `AGENTS.md`, the current README/status/next-steps and latest
development-log entry, `PLAN.md`, the atlas review and MIDI/UI atlas summary,
[`MIDI_UI_SCOPE.md`](../../MIDI_UI_SCOPE.md),
[`MIDI_INPUT.md`](../../MIDI_INPUT.md),
[`MIDI_REPLAY.md`](../../MIDI_REPLAY.md), and
[A23's author implementation/probe note](23-native-midi-replay.md). The actual
main-loop dispatch, retirement, acknowledgment, modal and diagnostic code was
inspected. Existing native app, workflow, replay-boundary and MIDI CLI tests
provided strict JSON and finite-process patterns. This is not a new complete
reading of the 500-page atlas, a repetition of A23's author-only coverage, or a
physical MIDI qualification.

## Acceptance construction

Every invocation names a private state path and separate MIDI/UI/report files,
sets both `SDL_AUDIODRIVER=dummy` and `SDL_VIDEODRIVER=dummy`, captures stdout and
stderr, disables inherited stdin, and has a **9-second subprocess timeout**.
The longest successful plan is 2450 ms. Paths include Unicode and spaces. Input
scripts and any supplied `B3CONTROLS3` state must remain unchanged; absent state
must stay absent, and the native run may not leave unexpected files.

The suite imports only the existing native test's strict JSON key/type checker,
duplicate-member/nonfinite rejection helpers and common schema declaration.
It imports no production parser, serializer, decoder, UiModel, transport or
Engine. Musical pitches, PedalIds, drawbar values, expected ownership and
pointer positions are literal test oracles. Missing
`HAMMOND_STANDALONE_EXECUTABLE` is a failed prerequisite, not a skip.

Schema 2 is validated with exact keys and types, including both optional replay
objects, every observation, numeric finiteness, distinct ascending held-note
lists, and the two manual/pedal ranges. Boolean values cannot satisfy integer
fields. Successful paired runs must give identical common musical observations
and acknowledgment fields in the UI and MIDI replay objects.

The common successful-run contract requires all records delivered, an empty
inbox, no pending open or retirement, final sequence/control acknowledgment,
real positive audio callback/frame counts, no audio/session/submission errors,
and no held notes or running Session after joined shutdown. The musical final
state is asserted **before** cleanup, so shutdown cannot hide an omitted Off or
incorrect owner release. The limited post-close discard allowance is at most
three redundant MIDI scoped releases plus one UI release per audio start;
pre-close performance delivery still needs full acknowledgment.

Packet conservation is checked independently at the quiescent boundary:

- Accepted inbox packets equal popped plus discarded packets.
- Decoder packets equal popped packets and the sum of decoder dispositions.
- Offered packets equal inbox receive attempts; accepted/rejected counters agree
  across the inbox and replay diagnostic objects.
- For completed plans, scheduled packets equal offered plus closed packets, and
  also equal decoded plus total dropped packets.
- Total drops equal closed packets plus rejected pushes plus discarded queue
  packets. Invalid-size and post-fault push counters must remain zero for these
  admitted replay fixtures.

The tests also require explicit synthetic source and receipt-clock labels,
`arrival_time_is_sample_time: false`, and an unopened native device with zero
generation and zero native callback counters. Compiled ALSA availability is not
treated as an actual MIDI connection.

## Final observed cases

The following rows describe the final 12 processes. Counts are actual native
diagnostic observations and assertions. Upper/Lower values are MIDI pitches;
pedals are one-based PedalIds.

| Test method / process | Actual observation |
| --- | --- |
| Division/channel/range routing, defaults 1/2/3 | Both manuals retain endpoints 36 and 96; pedals retain IDs 1 and 25. Of 23 scheduled packets, one is dropped while closed and 22 decode into 6 actions, 6 unsupported, 2 unmapped, 6 out-of-range and 2 malformed outcomes. Controls remain exactly unchanged. |
| Same routing test, configured 16/1/2 | The same musical and disposition expectations pass with Upper on wire channel 16 and Lower on wire channel 1. Unsupported CC64/120/121, Program Change, realtime input, unsupported pedal CC18, wrong channels, adjacent pitch endpoints and malformed packets cannot alter controls or manufacture notes. |
| Repeated owners, velocity-zero release and both UI/MIDI release orders | Repeated On/On followed by one Off keeps the repeated Lower and Pedal owners held; final Off removes them. Upper UI/MIDI overlap remains held after MIDI releases, then after a later UI-first release until its MIDI Off. Nonzero release velocity and unmatched release are admitted. Exact totals are 9 Ons and 10 Offs; the final state is empty. |
| CC11/B-bank edits while UI controls are pending | Seventeen mapped CC messages join actual UI edits. Upper A remains selected and Cancelled, Lower A remains selected, and Upper A's first drawbar ends at 1. Upper B ends `[0,1,8,0,0,0,0,0,8]`, Lower B's first drawbar is 4, pedals become `[0,8]`, and expression is exactly 64/127. Upper 60 remains held. Values 7 and 8 exercise the adjacent first discrete threshold without replacing the existing normalization law. |
| Scoped CC123 with UI holds in all divisions | Three external CC123 commands successively release Upper, Lower and pedal device owners. Unrelated divisions and same-note UI owners remain held at each acknowledgment. Final UI ownership is Upper 60, Lower 62 and PedalId 5; the source stays active. There are 9 Ons, no ordinary Offs, and only the final shutdown retirement. |
| Backend fault, stale discard and fresh epoch barriers | An initial closed packet and a closed backend fault are counted honestly. An active fault discards a queued Lower 65 On and preceding Lower 64 Off; neither stale nor closed input reappears. The held Upper UI 60 survives all retirements. Four epochs, two explicit pending-open barriers, two observed barrier wait turns, two discarded queue packets and three closed drops lead to final Upper 60 / PedalId 25. |
| Exact inbox capacity and bounded drain | A 256-packet On/Off burst is accepted completely, decoded completely, and drained with an actual maximum of **32 packets per turn**. There are 128 Ons and 128 Offs, zero drops, zero overflow, zero Session recovery and an empty musical final state. |
| Real overflow and explicit reconnect | A 600-packet burst fills the real 256-packet ring. The 257th attempt faults; exactly 256 queued stale packets are discarded, one push is rejected, and 343 remaining burst packets plus one later closed packet are ignored. The whole plan has 605 packets: 4 decoded + 256 discarded + 1 rejected + 344 closed = 605. The producer reaches its actual **512-record turn bound** and records budget exhaustion. Upper UI 60 survives; only a later explicit connection admits Lower 69. |
| Focus loss, resize, Help and MIDI Apply | Focus loss releases UI Upper 60 while MIDI Upper 67, Lower 64 and PedalId 1 survive. They remain held through a 960×700 resize, Help open/close and MIDI modal Apply after a proposed channel edit. Script routing remains 1/2/3, native device counters stay zero, and there is only one synthetic epoch. |
| Global Panic | Panic clears UI Upper 60 and all three external divisions, retires the MIDI epoch and drops later input until an explicit connect. The old physical UI press stays suppressed until its release; a fresh press works. Final state is Upper 60 / Lower 65, with 6 Ons, two epochs and two total release batches including shutdown. |
| Audio restart | Opening Audio releases UI ownership while external Upper 64, Lower 67 and PedalId 1 remain held. Applying actual 96000 Hz / 128-frame settings retires MIDI and clears notes; acknowledged expression 64/127 survives. Closed input is ignored; explicit reconnect and a fresh UI press yield Upper 60 / Lower 69. Two real audio starts and two synthetic epochs are observed. |
| Interrupted paired replay | A UI Quit before future UI/MIDI events yields native exit 1, incomplete/failed replay flags and exactly one reported execution failure. The later MIDI record is not delivered. Pre-shutdown Upper UI 60 / Lower MIDI 64 are visible, then native shutdown joins and clears both. This is an expected negative acceptance case, not a successful replay. |

The pending-control test explicitly selects 44100 Hz / 2048 frames to make
unacknowledged batches observable without changing production code. In the final
run it retained pending snapshots at **519, 653 and 831 ms**, with respective
last-applied/submitted sequences **7/11, 11/15 and 15/19**. These four-command
gaps and the preserved final controls support the pending-state acceptance;
equal scheduled UI/MIDI times alone are not used to claim a globally merged
ordering or exact audio-frame dispatch.

State-transition checks require an actual fully acknowledged observation in a
quiet interval between intended stages. The test does not infer a new state by
carrying an earlier observation forward. Observed callback counts, renderer
frame counts and elapsed milliseconds are retained as evidence, not turned into
hardware latency or deadline promises.

## Original failure, correction and process accounting

The first complete run executed all **11 methods / 12 native processes** in
**17.757 seconds**. Ten methods passed. The FIFO method failed its test assertion
`No acknowledged musical observation in [900, 990) ms`. Its original diagnostic
sequence showed the release submitted at 940 ms, the correct empty state
acknowledged at **998 ms**, the next UI press submitted at 1043 ms, and the later
MIDI On at 1098 ms. Its application returned 0, reported successful replay,
finished empty and retained the expected **9 Ons / 10 Offs**.

The fixture had scheduled successive ownership stages only 100 ms apart and
then further narrowed one observation window to 90 ms. It was corrected by
spacing those later stages by approximately 300 ms, extending that plan from
1900 to 2450 ms. No expected note set, ownership rule, command count, decoder
count, completion requirement or production source was changed. Root received
the original failure and the correction rationale before the fixture spacing
was corrected; there was no production bug to conceal.

The affected FIFO method then passed alone: **1 method / 1 native process,
2.638 seconds**. The final complete suite passed **11/11 methods / 12 native
processes, 18.121 seconds**. Total actual native invocations by this worker were
therefore **25 = 12 + 1 + 12**, including two deliberate interrupted processes
across the two full runs. Python orchestration and source/hash checks are not
counted as additional native application tests.

Scratch evidence is under
`/workspace/scratch/cd4bd06ce68f/a31-native-midi-acceptance/`. It contains the
frozen executable, `identity.json`, the complete `first-run.log`,
`corrected-fifo.log`, `final-run.log` and `final-summary.json`. The `first-run/`,
`corrected-fifo/` and `final-run/` directories retain each exact input, original
schema-2 report and `process.json` command/environment/stdout/stderr/exit record.
Optional `HAMMOND_STANDALONE_MIDI_EVIDENCE` enables that copy. Independently of
the optional directory, test failures copy bounded input/diagnostic evidence
into the assertion before private temporary files are removed.

| Retained execution record | SHA-256 |
| --- | --- |
| `first-run.log` | `3fef35fb0383171a271283ea99cc63379bc1cc0b8587c0365ab18db76c95917d` |
| `corrected-fifo.log` | `676e99c8604fbbc110ffb44027d7c08767502895ddfd032f61d347ac8e99024f` |
| `final-run.log` | `5d7218a60b9eb85a979a5568b74835e28daf45b429c03cbe2458d5ae4f0b9f44` |
| `final-summary.json` | `eeeec5d1ec3ba42caab0a5b39abf88088651e479fe7f8235266de156a56432fe` |

## Reproduction and CMake handoff

Working directory for all authored checks:
`/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.

The executable was copied only after root confirmed its coordinated build was
ready. The exact final suite command was equivalent to:

```sh
PYTHONDONTWRITEBYTECODE=1 \
HAMMOND_STANDALONE_EXECUTABLE=/workspace/scratch/cd4bd06ce68f/a31-native-midi-acceptance/hammond_standalone \
HAMMOND_STANDALONE_MIDI_EVIDENCE=/workspace/scratch/cd4bd06ce68f/a31-native-midi-acceptance/final-run \
python3 apps/standalone/native_tests/test_standalone_midi_replay.py
```

The targeted correction used the same command and its own evidence directory,
adding
`NativeMidiReplayAcceptance.test_repeated_fifo_owners_velocity_zero_and_both_release_orders`.
The first full run used the original test fixture and `first-run` evidence
directory. Each native command explicitly contains `--midi-script`,
`--diagnostics` and its private `--state`; paired cases add `--input-script`.
The tests themselves set the two dummy-driver environment variables.

Python AST parsing reported exactly 11 authored test methods. The executable
hash was checked unchanged after each suite. `git diff --check` passed for the
owned test before handoff. No native rebuild was performed by this worker.

The SDK-free C++ target already occupies CTest name
`test_standalone_midi_replay`. The exact distinct native wiring sent to root is:

```cmake
add_test(NAME test_standalone_native_midi_replay
    COMMAND "${CMAKE_COMMAND}" -E env
        "HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>"
        "${Python3_EXECUTABLE}"
        "${CMAKE_CURRENT_SOURCE_DIR}/native_tests/test_standalone_midi_replay.py")
set_tests_properties(test_standalone_native_midi_replay PROPERTIES
    TIMEOUT 90 LABELS "standalone;native;midi")
```

This belongs inside the existing native application/testing condition. No
physical MIDI backend is required for synthetic input. Root owns integration;
the focused handoff command was:

```sh
ctest --test-dir /workspace/scratch/cd4bd06ce68f/build-native \
  --output-on-failure --no-tests=error \
  -R '^test_standalone_native_midi_replay$'
```

Root subsequently reported and retained a **1/1 passing focused CTest gate in
18.43 seconds** against the finalized test. A31 read
`/workspace/scratch/cd4bd06ce68f/native-midi-replay-ctest.log` and the accompanying
`native-midi-replay-junit.xml`: the discovered native test passed in 18.4212 s,
and its captured output identifies the newer refined executable as
`33728f0df9688ed82e8e5e9446465ff98acbef60ca2d5438b1f22de4db1de4bb`.
This is a separately attributed root integration result, not an additional A31
execution or a replacement for the worker's earlier frozen-binary identity.
The root gate is not included in the worker's 25-process count. Hosted CI still
must discover the distinct native test as well as the existing C++
parser/decoder target.

## Exact qualified identities

Observed repository HEAD was `e09107414896c2c53dad124a74f60c8043fadfe4` with
concurrent uncommitted MIDI/UI work. The named HEAD alone is not the tested
candidate. Root's Release configuration had `HAMMOND_BUILD_STANDALONE=ON`,
`HAMMOND_ENABLE_MIDI=ON`, GNU C++ **14.2.0**, prepared RtMidi/ALSA support, and
**SDL 2.32.10** reported by the running application. Its local SDL configuration
has `SDL_ALSA=OFF`; all of these processes deliberately use dummy audio. Native
MIDI backend diagnostics report compiled ALSA availability while every physical
port/device counter remains zero.

| Qualified file | SHA-256 |
| --- | --- |
| Frozen native executable | `a2b2deb4da098bb2219c2d9ce43c407e504563275a138de9eb1da8fc5f5d137e` |
| Final authored Python test | `667e7009305128dd8a4365ae48753211837e0f9fc859fe679ddb20e8a71d62ed` |
| `apps/standalone/main.cpp` | `22719975ed910b0b23db841617446e492890d89f2106cc04279fc9e46824f42e` |
| `apps/standalone/MidiReplay.cpp` | `a61047fcb0da050eae35a10e86205a496d13ea7d00fb8b113c8682d1556a88db` |
| `apps/standalone/MidiReplay.h` | `c0a62c0d33e7b0c3b90237e82cf631222d3d5274bb6b45fa797906e1e77a3948` |
| `apps/standalone/MidiInput.cpp` | `32e135e84a870dc0e7d6cd9f5a9804b6c75031d4b2fd8dcfcf4d0959bd210802` |
| `apps/standalone/MidiInput.h` | `00a1e6d43f8db1721f7042b6c37b081f192dd85f55dc1bb999c81ee0a4014038` |
| `apps/standalone/UiModel.cpp` | `ac1a381367cfee7cce61e27ebd0b094c76a730806383e9ead609622687993e28` |
| `apps/standalone/Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| `apps/standalone/ScriptedInput.cpp` | `7c143db56b1eda113886a3e2cd63ec3570483921adc2b57e1a4c8f0ef6235531` |
| `apps/standalone/Drawing.cpp` when root declared the build ready | `8fc8b8745f789de89a5bea4c60986f330445154280983cb4af46392db362c952` |

All recorded MIDI/main/UI/Session source identities remained unchanged at the
post-run check. `Drawing.cpp` advanced concurrently after the executable was
frozen; root was notified. This note qualifies the frozen binary and its
recorded renderer input, not the later drawing source. The table is a set of
relevant file identities, not a claim of a separately frozen complete repository
tree or published revision.

## Limits and next gate

This suite closes the assigned independent native synthetic acceptance for
these finite musical/lifecycle cases. It does not open a physical device,
exercise a real backend callback producer, measure hardware latency/hotplug or
dropout, compare waveform fidelity, prove sample-accurate timing, or qualify
Windows/macOS/native accessibility. Positive audio peaks establish that the
nominal renderer produced samples in representative cases, not calibrated
organ gain or acoustic fidelity.

The suite deliberately avoids redoing every decoder byte/value permutation or
the parser's complete malformed-file boundary matrix. Its largest plan is 607
records; the 2048-record grammar maximum remains separate parser coverage. A
deliberate Session-queue emergency and cancellation of a pending connection by
Panic racing an acknowledgment are not forced by these native fixtures. The
ordinary global Panic, actual restart and explicit sequential reconnect paths
are observed; no stronger race claim follows. The main-thread synthetic source
cannot establish physical backend callback-close quiescence.

The finalized test and root's focused CTest discovery/execution are ready for
the next integrated checkpoint. Root should include the test in hosted native
jobs and bind those results to the final source/publication record. Real MIDI
controller and platform qualification
continue to require their own named devices, backend, OS and retained playing,
disconnect/reconnect and timing observations.
