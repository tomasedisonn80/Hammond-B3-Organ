# Assignment 43 — identify the removed output

Actual agent `/root/w08_a43_audio_removal`, assignment 43/60, wave 8. A resumed
turn continued this same assignment; it did not create another agent. Owned
`apps/standalone/AudioDevice.h`, `AudioDevice.cpp`, only the removal condition in
`main.cpp`, [the contract](../../STANDALONE_DEVICE_REMOVAL.md), and this note.
No core, state, callback/lifecycle body, CMake, shared record or commit was edited.

Read AGENTS, current plan/status/next steps and standalone/scanner handoffs,
atlas review and M9 scope, and the pinned SDL source. Waited for root's source
staging authorization before editing. Root published/fetched baseline
`5b8e2419d23fe27c51709d717812060eafd44dcc`, tree
`880682248c467a51cce14d920189cf0009b68d22`, before the owned source repair.

## Defect and change

SDL 2.32.10's `SDL_RemoveAudioDevice` posts output-removal events with ID zero
for unopened devices. `SDL_OpenedAudioDeviceDisconnected` posts an open handle.
The old main condition checked only event type, output flag and whether any
device was open, incorrectly closing playback for both zero and unrelated IDs.

Added `device_id()` and pure `is_removed_by(const SDL_AudioDeviceEvent&) noexcept`
main-thread queries. The latter checks REMOVED type, zero capture flag, a nonzero
current handle and exact ID equality. Main now invokes it behind the existing
type guard. There is no new data member, public parameter, saved-state version,
diagnostics field or callback work. Existing matched-removal cleanup is unchanged.
Stop retains the handle; close clears it; an open can reuse a prior integer.

## Coherent author execution

Created a private `git archive` of baseline 5b8e241 in
`/workspace/scratch/5ba97739b54c/a43-removal/source`. Toolchain: Linux x86-64,
GCC 14.2.0, CMake/CTest 4.4.4, Python 3.12.14, Release, pinned SDL 2.32.10.
Configured a fresh sibling `build` with these actual arguments:

```sh
cmake -S source -B build -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/5ba97739b54c/SDL2
cmake --build build --target hammond_removal_probe hammond_standalone \
  test_standalone_audio_device test_standalone_callback_allocation --parallel 2
```

`hammond_removal_probe` is a scratch-only target compiling the actual app sources
with `SDL_WaitEventTimeout=hammond_probe_wait_event_timeout`. Its 1,324-byte shim
undefines that alias in its own source, delegates the real SDL wait, then uses
`SDL_PushEvent` once after 150 ms. Mode selects output REMOVED/zero, output
REMOVED/UINT32_MAX, capture REMOVED/zero or output ADDED/zero. No private SDL
API, internal object access, device-loss simulation or production CLI was added.

Ran four baseline processes, copied only the three frozen repaired sources into
that private archive, rebuilt the same targets, then ran four repaired probes
and one ordinary unshimmed application. Every process used explicit dummy video/
audio and software rendering, `--smoke-ms 600`, a private missing state path and
a new diagnostics path. All nine processes retained full JSON and stderr.

| Case | Before | After | Repaired callbacks / frames |
| --- | --- | --- | --- |
| Unopened output, ID zero | Exit 1, closed, two errors | Exit 0, open/running, zero errors | 56 / 28672 |
| Output, UINT32_MAX | Exit 1, closed, two errors | Exit 0, open/running, zero errors | 57 / 29184 |
| Capture, ID zero | Exit 0, open/running | Exit 0, open/running, zero errors | 57 / 29184 |
| Added output, index zero | Exit 0, open/running | Exit 0, open/running, zero errors | 58 / 29696 |
| Ordinary app, no shim | Not part of before probe | Exit 0, open/running, zero errors | 61 / 31232 |

The before/after oracle required each injected event to be accepted once and
the expected old failure/new success. Every repaired run also required observed
hold/release, final note-off acknowledgment, finite positive peak, zero unexpected
render/format/nonfinite/overrange/session faults, joined stopped/no-held shutdown
and absence of state creation. Repaired last
applied/resolved command sequences were 3/4; one normal shutdown release was
discarded. No callback count or elapsed wall time is a hardware deadline result.

The existing `test_standalone_audio_device` and calibrated
`test_standalone_callback_allocation` suites passed **2/2**, zero failures,
**2.88 seconds**, using `ctest --test-dir build -R
'^test_standalone_(audio_device|callback_allocation)$' --no-tests=error
--output-on-failure --parallel 2`. The fresh configure/build and repaired rebuild
completed successfully. No producer or fixture correction followed those passes.

## Qualification identities

| Artifact | SHA-256 |
| --- | --- |
| Repaired AudioDevice.h | `75ac25e462afb85c64b0298bf4e8c30d4979d3d30f231edec75c8ba41818673a` |
| Repaired AudioDevice.cpp | `3565139241941d108b18289b176f25732e0c9bf4d36a60844a297ba92499f2b0` |
| Repaired main.cpp | `3190e9a3f4a4c156f6d54ae7ddc7efa675a99d86cf2703a57af2badd443e9dbe` |
| Scratch injection shim | `29e115be33a47d6ef2237882946552dfdf5ee9788d6c9ae40b026ce299b97f00` |
| Baseline probe executable | `4be00ed74686a87e479f9536633ba45ba12c389162ae4405f7a2c8044449cc41` |
| Repaired probe executable | `5c8a04999a82687b53ecfb97545cfa0a586c668c849fbd850ebed75b260b352d` |
| Ordinary repaired executable | `f07c1d59c0241dd52079da9f14a64fe56e4ad2730aadd4250c5bd5ea19e21bfb` |
| Baseline result JSON | `e6f9f0f668fe5d2c2e04d6f49cca7804d1b9aa88af2818a12ba69cbd8cfa1d43` |
| Repaired result JSON | `3131be3bd70f835b75feb56abb5047173d194b643a49d712be116de558297a11` |
| Two-suite CTest log | `3d3e730588f140dc9106c43716e591045258fab22ebb2b2bf13931fbf278594a` |
| Pinned SDL_audio.c | `e4ff1836b449f9b00d5eb5d73487fa92ee06afa4df9b2bae76b0f0811e6b7644` |
| Pinned SDL_events.h | `ceb7bc717342e652e2c432fd1dd08a5508575cea6bd8615fb4ddea63c071ddc4` |

Scratch scripts/sources, configure/build/test logs, private probe source, all
diagnostics and `identities.json` remain under `../a43-removal` for coordinator
inspection. They do not replace the maintained independent acceptance suite.

## Handoff

Shared the exact API and frozen hashes with assignment 44 before its independent
tests. Its [acceptance](../../STANDALONE_DEVICE_REMOVAL_ACCEPTANCE.md) supplies
separate actual-ID, queue, musical-state and lifecycle evidence. Root owns the
canonical test registration, combined frozen-source gate, hosted runs, shared
status/manifest, commit and verified push. This worker made no publication claim.
Real devices, rapid disconnect/reopen queue ordering, native backends and hardware
latency remain separate gates. The adapter cannot infer historical generations
from reused SDL IDs; the contract states that boundary explicitly.
