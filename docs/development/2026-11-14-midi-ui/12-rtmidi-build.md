# A12 — locked RtMidi acquisition and prepared build

Actual worker: `w02_a12_rtmidi_build`, wave 2 of the separate requested
`2026-11-14-midi-ui` session. This note records only this assignment.

## Owned scope and source

Owned paths: `tools/acquire_rtmidi.py`, `cmake/VerifyRtMidi.cmake`,
`data/dependencies/rtmidi-lock.json`,
`assets/standalone/midi/LICENSE-RtMidi.txt`, `docs/RTMIDI_BUILD.md`, and this note.
No root/app CMake, shared status, other worker files or commits were authored.
Repository HEAD observed during this work:
`7b36cfac2565397191b3df5e07112611e7f1b0e1`; the concurrent worktree was not a frozen
whole-project qualification snapshot.

Read `AGENTS.md`, `MIDI_UI_SCOPE.md`, `MIDI_BACKEND.md`, current
README/status/next-step/log entry points, plan, atlas review and standalone
handoff. The dependency authority was the local clean upstream checkout at
`/workspace/scratch/cd4bd06ce68f/rtmidi`, HEAD and tag `6.0.0` both resolving to
`1e5b49925aa60065db52de44c366d446a902547b`. Source inspection covered its actual
license, header version/API definitions, native API compile/link requirements,
and both CoreMIDI allocation sites. No atlas physical value is introduced.

## Implemented result

The explicit `--destination` acquisition command requires a new external path
and verifies the reviewed upstream commit/tag and exact source/header/license
identities. The offline `--verify-existing` path rejects dirty, hidden-index,
partial/promisor and unexpected-file checkouts. Configure cannot acquire a
dependency: its helper invokes only verification plus optional preparation.

Preparation verifies the original bytes, requires the exact two original
CoreMIDI allocations, and writes the reviewed value-initialization correction
into a separate build copy. It records the full lock, prepared file identities,
exact diff and tool SHA-256 in a deterministic manifest. Repeated preparation
does not rewrite a matching output; unexpected output fails without repair.
The original checkout remains untouched.

`hammond_add_rtmidi(target, root)` compiles just the prepared C++ source into a
static target with one platform API: Linux ALSA, Windows WinMM or macOS CoreMIDI.
It does not enter upstream CMake or discover JACK. Unsupported enabled targets
and missing native prerequisites fail configuration. The root integrator owns
`HAMMOND_ENABLE_MIDI=OFF`, `HAMMOND_RTMIDI_ROOT`, adapter compilation and private
linkage. The packaged upstream notice is supplied for later install integration.

## Frozen identities

| File | SHA-256 |
|---|---|
| Original `RtMidi.cpp` | `184d775e88e5d73b079897363fb42af155122e879f0bc9254a1c7edae4eadb3c` |
| `RtMidi.h` | `74f98ca172243b0b9c0c59f53c4e20285d879ffa86b3d61692109b013f4606f9` |
| Upstream and retained license | `7fa091d9c1aa492ebfcafa9f919d27bbce61e4f048ece2dfc3b7f93181e9e364` |
| Prepared `RtMidi.cpp` | `240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a` |
| Exact two-hunk patch | `80aedddee9affe1c9ab305b605c6ca1f5c2209fd5d23da843c8c3f325426c4ad` |
| Tested preparation tool | `b5b436be15a7a1aa807ec342793741eaefbbc2df0dbe5f315fc7f97a690809bf` |
| Tested CMake helper | `fe2f76f57ca3384aedf05da1afbe0cc3fd3989bee29120bbb252249368bbccdd` |
| Tested dependency lock | `4e2923a57abfaa98d68d7b339ea9a39c420f40dc3b175a339be108eaf0a987aa` |
| Generated preparation manifest | `481095a20040ffe8c824200b3b20663ebc4c392f1fc535ead7f6e679f3a5b2ae` |

The patch has 728 bytes; the prepared C++ source has 168,216 bytes. Patch format
and its exact before/after statements are specified in
[RTMIDI_BUILD.md](../../RTMIDI_BUILD.md).

## Executed verification

Toolchain: Python 3.12.14 in the CMake invocation, CMake 4.4.4 at
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin/cmake`,
GCC 14.2.0 on Linux. The caller's `python3` also ran syntax compilation and the
CLI checks. ALSA 1.2.14 development inputs came from
`/workspace/scratch/641ca55ce6de/native-sysroot/usr`; no system package was
installed or changed.

| Check | Observed result |
|---|---|
| CLI `--verify-existing` on pinned checkout | Pass; exact commit/tag and three file identities; `network_used=false`. |
| Prepare, then prepare again | Pass; second result reports reuse and all five files keep identical bytes and nanosecond modification times. |
| Original vs. prepared allocation count | Pass; original retains two `new CoreMidiData;` statements; prepared has exactly two `new CoreMidiData{};` statements. |
| Append a byte to prepared source | Rejected with size/SHA-256 mismatch; corrupt output preserved, not repaired. |
| Alter locked patch occurrence count | Rejected as an unreviewed lock. |
| Request output beneath the locked checkout | Rejected; no output directory created there. |
| Corrupt source in a separate local clone | Rejected as modified tracked input. |
| Isolated CMake option OFF | Pass with no RtMidi root; disabled ALSA/Python package lookup flags unused because the helper did no work. |
| Isolated CMake option ON / ALSA | Configure, static-library compile and executable link pass. |
| Run compiled API smoke | Pass: `RtMidi 6.0.0: exactly one API, alsa`; no native client constructed. |
| Repeat enabled CMake configuration | Pass; reports existing prepared copy reuse. |
| Enabled synthetic `CMAKE_SYSTEM_NAME=FreeBSD` configure | Expected failure explicitly naming the unsupported target; no dummy selection. |
| Final original checkout inspection | Clean `git status --short`; original source/header/license hashes unchanged. |
| `python3 -m py_compile tools/acquire_rtmidi.py` | Pass. |

Temporary local checks were run under
`/workspace/scratch/cd4bd06ce68f/rtmidi-build-check-a12`. The smoke project uses
`include(.../cmake/VerifyRtMidi.cmake)`, calls
`hammond_add_rtmidi(hammond_rtmidi "${HAMMOND_RTMIDI_ROOT}")` only when enabled,
and privately links an executable that requires `getCompiledApi()` to return
exactly `RtMidi::LINUX_ALSA` and `getVersion()` to equal `6.0.0`.

Commands from the project root, with `cmake` denoting the executable above:

```sh
python3 tools/acquire_rtmidi.py --verify-existing ../rtmidi
python3 tools/acquire_rtmidi.py --verify-existing ../rtmidi \
  --prepare-build-copy ../rtmidi-build-check-a12/prepared
python3 tools/acquire_rtmidi.py --verify-existing ../rtmidi \
  --prepare-build-copy ../rtmidi-build-check-a12/prepared

cmake -S ../rtmidi-build-check-a12/smoke-project \
  -B ../rtmidi-build-check-a12/off -DHAMMOND_ENABLE_MIDI=OFF \
  -DCMAKE_DISABLE_FIND_PACKAGE_ALSA=TRUE \
  -DCMAKE_DISABLE_FIND_PACKAGE_Python3=TRUE
cmake -S ../rtmidi-build-check-a12/smoke-project \
  -B ../rtmidi-build-check-a12/on -DHAMMOND_ENABLE_MIDI=ON \
  -DHAMMOND_RTMIDI_ROOT=/workspace/scratch/cd4bd06ce68f/rtmidi \
  -DALSA_INCLUDE_DIR=/workspace/scratch/641ca55ce6de/native-sysroot/usr/include \
  -DALSA_LIBRARY=/workspace/scratch/641ca55ce6de/native-sysroot/usr/lib/x86_64-linux-gnu/libasound.so.2.0.0 \
  -DCMAKE_BUILD_TYPE=Release
cmake --build ../rtmidi-build-check-a12/on -j2
../rtmidi-build-check-a12/on/rtmidi_api_smoke
```

## Remaining gates and handoff

The root/app CMake integration, disabled/enabled adapter implementation tests,
notice installation and full native application build belong to subsequent
integrated acceptance. Windows/macOS compilation and execution, actual controller
input, shutdown/hotplug behavior and physical timing were **not run** by this
assignment. The explicit network acquisition command was authored and inspected;
verification used the already available pinned checkout, not a claimed fresh
network clone. The Linux API smoke does not open an ALSA client or attest to an
available sequencer/device.

Next integrate the optional target privately with the adapter, preserve an SDK-free
default configuration, add the retained notice to MIDI-containing packages, and
qualify those behaviors on one coherent source snapshot. Preserve the documented
CoreMIDI correction and distinguish its source-level fix from platform lifetime
evidence. No publication or physical-fidelity gate is closed by this note.
