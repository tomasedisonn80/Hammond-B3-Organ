# A18 — MIDI, Session and UI integration acceptance

Actual assignment: `/root/w03_a18_midi_session_acceptance`, wave 3 of the
`2026-11-14-midi-ui` session. Completed 2026-11-14. This is one newly dispatched
worker; no earlier worker or test result is recounted.

## Owned changes and result

Owned paths only:

- `apps/standalone/tests/test_standalone_midi_session.cpp`
- This evidence note.

Added an SDK-free integration executable discovered by the existing CMake test
glob. No production source, shared status/ledger, dependency, parameter identity,
state format or nominal model was modified. No commit or publication was
performed by this worker.

**Result:** the fresh strict-warning Release build succeeded, and the selected
four CTest suites passed. The new executable completed **26 scenarios** through
actual `MidiInbox`, `MidiInput`, `UiModel` and `Session` objects. No production
defect was observed in the tested scope. No compile failure or failing test
preceded this passing result.

The implementation follows [MIDI_INPUT.md](../../MIDI_INPUT.md),
[MIDI_UI_SCOPE.md](../../MIDI_UI_SCOPE.md), the existing Session/UI contracts and
the source/evidence limits in the [current atlas review](../../research/MIDI_UI_ATLAS_REVIEW.md).
The reading included `AGENTS.md`, the current README/status/next steps,
standalone handoff, project plan, atlas review and relevant ownership contracts.
This assignment does not claim another independent full-PDF reading.

## Meaningful observations

| Area | Executed observation |
| --- | --- |
| Repeated anonymous owners | In Upper, Lower and Pedals, identical On/On messages remain held after one ordinary Off; a velocity-zero On releases the remaining owner. Nonzero release velocity is accepted through the decoder and canonicalized, and an extra unmatched Off is harmless. The live Session snapshot remains unchanged until a callback boundary. |
| Independent routes | Configured wire channels Upper 16, Lower 1 and Pedals 9 carry the same pitch 48 into distinct upper/lower keys and PedalId 13. Lower CC123, then upper Off, leave the other division holds intact. Zero-frame application does not advance the clock. |
| Shared UI/MIDI pitch | For each division, a real UiModel keyboard owner survives matching external Off, CC123 and all three scoped retirement commands. The external-only neighboring note releases, proving that surviving UI state is not merely an unprocessed MIDI release. Releasing UI afterward empties the held state. |
| Reverse release order | A MIDI hold survives UI focus release, resize, Help/Audio requests, bank editing, a complete control load and a later physical UI key-up; the matching MIDI release finally clears it. |
| Synthetic disconnect/reopen | With the producer already quiescent, a faulted inbox containing an old On and Off is discarded, decoder admission ends, and the fixed three-command release sequence is posted. A new epoch starts only after a real Session snapshot resolves/applies those commands. UI channel 0 remains held, and the stale neighboring On does not replay. |
| Shared pending controls | Real decoded CCs edit upper/lower B drawbars, a pedal mixture and expression during a captured upper-A drawbar drag. A continues to be edited and selected, Cancel remains active, and MIDI retains the existing focus and drag. The subsequent UI move preserves every external edit. |
| Delayed acknowledgments | The fixture observes an actual old Session publication while edits are queued, renders without observing its acknowledgment, queues another CC/drag sequence, then observes the earlier acknowledgment. Desired controls remain pending until the latest real sequence is applied. Held notes and the frame clock stay unchanged throughout zero-frame control application. |
| Save/dirty state | External edits keep the desired controls dirty; `mark_saved` clears the marker for the admitted complete state, and another decoded CC makes it dirty again. |
| Audio and time | A written physical-event score is processed by an independent real Engine, bypassing the MIDI decoder, UiModel and Session ownership implementation. Every rendered mono sample is compared bit-for-bit with that reference; both Session stereo channels must be equal and finite, buffer sentinels intact, and the published peak/clock/control/hold state accurate. |
| Timestamp/velocity/block partition | At 44.1, 48 and 96 kHz, the same 937-frame score is rendered with whole stage blocks, with subdivisions of 1/7/32/9/64 frames, and with velocity 1 versus 127. Zero, equal, decreasing and near/at-`UINT64_MAX` receipt values preserve arrival order and identical samples. A queued On/Off/On is retained in FIFO order. Event boundaries are fixed across comparisons; metadata does not schedule audio. |

Every Session publication supplied to `UiModel::observe` is read from an actual
Session. No fake Engine state or manufactured Session snapshot stands in for
application or acknowledgment. The separate reference Engine receives explicit
physical transitions and explicit controls, with matched source seed and initial
frame; it is not fed decoded events or copied Session snapshots.

The direct new-test output was:

```text
MIDI/Session/UI acceptance: 26 scenarios, 197 decoded packets, 308 commands, 343 callbacks, 17466 finite stereo samples, 8433 physical-reference sample comparisons, 5622 timestamp/velocity/partition sample comparisons
```

## Exact executed checks and source identity

Working directory for every command:
`/workspace/scratch/cd4bd06ce68f/Hammond-B3-Organ`.

Observed checkout HEAD and local `origin/main` tracking reference:
`7b36cfac2565397191b3df5e07112611e7f1b0e1`; committed tree
`f6fe5ec715fe113d581e188834d51f9a30f52046`. The tested candidate includes the
concurrent uncommitted MIDI/UI work. The historical committed tree alone does
not identify that candidate, and the tracking reference is not a new remote
publication verification.

Toolchain: CMake **4.4.4**, GNU C++ **14.2.0** (`/usr/bin/c++`), configured Python
**3.12.14**. The test compiled as C++20 with
`-O3 -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror`.
Release `CHECK` assertions remain active through `TestSupport.h`.

Executed commands:

```sh
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake -S . -B /workspace/scratch/cd4bd06ce68f/build-midi-a18-release -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake --build /workspace/scratch/cd4bd06ce68f/build-midi-a18-release --target test_standalone_midi_session test_standalone_midi_input test_standalone_external_control test_standalone_session --parallel 2
/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/ctest --test-dir /workspace/scratch/cd4bd06ce68f/build-midi-a18-release -R '^test_standalone_(midi_session|midi_input|external_control|session)$' --output-on-failure --no-tests=error
/workspace/scratch/cd4bd06ce68f/build-midi-a18-release/apps/standalone/test_standalone_midi_session
git diff --check
```

The first configure created a separate, fresh A18 build directory. Core sources,
all standalone support sources including `MidiDevice.cpp`, generated routing and
the nominal profile were rebuilt there before CTest. The four selected suites
passed **4/4**; CTest reported **0.34 seconds** total. The focused integration
suite reported 0.04 seconds in that run; these are observations, not callback
deadline or performance qualification.
Both new owned files also received
`git diff --no-index --check /dev/null <owned-path>`: neither emitted whitespace
diagnostics; each returned 1 because the file is an addition relative to
`/dev/null`.

Before configuring, a Python SHA-256 manifest covered all files beneath `src/`,
`include/`, `data/`, `tools/` and `cmake/` (excluding Python cache files), both
CMakeLists files, `Session`, `UiModel`, `MidiInput`, `MidiDevice` and `StateFiles`
headers/sources, the new test and `tests/TestSupport.h`. All **143** identified
files retained identical bytes after build and test. The sorted, indented JSON
manifest SHA-256 was
`5ec04dfa90a4fb831a5e1c79f103e637149fdb5f3b74beb0d379dd4e74dd4fd0`.
The manifest is a scratch verification aid, not an independently published
artifact or substitute for the integrator's final source freeze.

Key candidate source SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `MidiInput.h` | `00a1e6d43f8db1721f7042b6c37b081f192dd85f55dc1bb999c81ee0a4014038` |
| `MidiInput.cpp` | `32e135e84a870dc0e7d6cd9f5a9804b6c75031d4b2fd8dcfcf4d0959bd210802` |
| `Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| `Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| `UiModel.h` | `fac0dd9bfa1baf77d1efda2fbb8839c5a223d9ab0c3580c10dda184317f7da3c` |
| `UiModel.cpp` | `ac1a381367cfee7cce61e27ebd0b094c76a730806383e9ead609622687993e28` |
| New integration test | `192eb54285407b8460dd41d2e3575f8d69801798a2c4ea0daecc018b0403c2b1` |

The generated fixture is `nominal-unmeasured-v1`, with authoring SHA-256
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
The built `nominal.b3p` SHA-256 is
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`;
the executed `test_standalone_midi_session` binary SHA-256 is
`e9c3411f640677c10a188a312e95235c73780f185eb9c3fcd57f390468ded914`.
It remains synthetic engineering input, without measured timbre or hardware
fidelity implications.

## Limits, bugs and next acceptance

**Bugs:** none observed. No production repair was requested or made.

The indistinguishable anonymous On/On/Off/Off test proves the externally
observable repeated-owner lifetime. With immutable routing and no exposed owner
IDs, it does not identify which indistinguishable internal slot was removed.
The underlying ownership suites retain their own more direct FIFO evidence.

The disconnect fixture executes the required retirement protocol after synthetic
quiescence; it does not exercise `MidiDevice` open/close, actual main-loop
integration, callback join races, a physical controller or hotplug. Receipt
timestamps are not calibrated hardware timing. This single-thread test does not
qualify concurrent producer/consumer safety, the native 32-packet drain bound,
OS/audio-device behavior, an allocation-free callback, sanitizers, other
platforms, native screenshots, visual fidelity or physical sound. A19 owns the
separate allocation/concurrency probe; this assignment intentionally does not
duplicate that instrumentation. The rendered partition comparison preserves
explicit event boundaries and does not promise invariance when real MIDI
arrives on different callback boundaries.

Next: the integrator should rerun this discovered suite against the final frozen
support/core candidate, alongside the independently owned inbox/concurrency and
allocation acceptance. The application/backend workers should demonstrate the
same scoped release and pending-control semantics through the actual drain,
disconnect and restart paths, retaining callback-quiescence and device evidence
separately. Physical-controller qualification still requires an identified
device, OS/backend and observed held-note/hotplug/timing behavior.
