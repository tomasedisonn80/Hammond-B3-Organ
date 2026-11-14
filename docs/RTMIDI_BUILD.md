# Optional locked RtMidi build

The MIDI input dependency is **RtMidi 6.0.0**, upstream tag `6.0.0`, commit
`1e5b49925aa60065db52de44c366d446a902547b`. The
[lock](../data/dependencies/rtmidi-lock.json),
[acquisition/preparation tool](../tools/acquire_rtmidi.py), and
[CMake module](../cmake/VerifyRtMidi.cmake) identify the complete compiled input.
The [backend contract](MIDI_BACKEND.md) owns device lifetime, API selection and
the limits of native qualification. The [session scope](MIDI_UI_SCOPE.md)
preserves the ordinary build and the core's independence from native SDKs.

The dependency module, root options and adapter wiring are implemented. Ordinary
builds compile the unavailable backend; explicitly enabled builds compile the
selected prepared native backend. The [A12 evidence note](development/2026-11-14-midi-ui/12-rtmidi-build.md)
records the dependency checks, and the [A14 implementation note](development/2026-11-14-midi-ui/14-midi-backend.md)
records adapter compilation and the actual no-device ALSA result. These checks
do not claim a physical-controller or hardware-audio run.

## Acquire explicitly, verify locally

Run from the project source root with Python 3.10 or newer and Git available.
The acquisition destination's parent must already exist. The dependency checkout
must remain outside the project source tree.

```sh
python3 tools/acquire_rtmidi.py --destination ../rtmidi-6.0.0
python3 tools/acquire_rtmidi.py --verify-existing ../rtmidi-6.0.0
```

Only `--destination` invokes a network-capable clone, from the pinned upstream
repository. It requires a new path, does not update an existing checkout, forces
LF checkout bytes and does not initialize submodules. A failed new checkout is
retained for inspection. A tag that moves away from the reviewed commit fails
verification; it does not change the lock.

`--verify-existing` never fetches or repairs. It requires the exact Git root,
HEAD and tag, a complete ordinary index, no tracked modifications, no extra
untracked or ignored files, and the locked SHA-256 and byte length of the source,
header and license. Partial/promisor clones are rejected. Git inspection disables
protocols, lazy fetching, replacement objects, optional index writes and fsmonitor
hooks, and ignores inherited Git worktree/index/object overrides. CMake invokes
only this offline path, optionally with build-copy preparation.

An alternate `--lock` must match the same reviewed identity and correction. A
dependency upgrade requires a deliberate change and review of both the tool's
accepted identity and the versioned lock.

## Prepared source and required correction

Do not compile or edit the external checkout in place. The original CoreMIDI
input and output initializers leave members of `CoreMidiData` indeterminate;
the backend contract identifies the resulting handle-read problem. Preparation
checks the original source hash and then replaces exactly **two** occurrences:

```cpp
CoreMidiData *data = (CoreMidiData *) new CoreMidiData;
```

with:

```cpp
CoreMidiData *data = (CoreMidiData *) new CoreMidiData{};
```

No other upstream bytes change. The correction applies to the separately
prepared source on every build platform so that the prepared source has one
identity. It addresses this initialization defect; it does not qualify callback
shutdown, physical input, driver failures or measured timing.

| Input or generated output | Bytes | SHA-256 |
|---|---:|---|
| Original `RtMidi.cpp` | 168,212 | `184d775e88e5d73b079897363fb42af155122e879f0bc9254a1c7edae4eadb3c` |
| Original and copied `RtMidi.h` | 27,901 | `74f98ca172243b0b9c0c59f53c4e20285d879ffa86b3d61692109b013f4606f9` |
| Original and copied `LICENSE` | 1,349 | `7fa091d9c1aa492ebfcafa9f919d27bbce61e4f048ece2dfc3b7f93181e9e364` |
| Prepared `RtMidi.cpp` | 168,216 | `240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a` |
| `rtmidi-coremidi-zero-init.patch` | 728 | `80aedddee9affe1c9ab305b605c6ca1f5c2209fd5d23da843c8c3f325426c4ad` |

The patch is UTF-8/LF unified diff, three context lines, with filenames
`original/RtMidi.cpp` and `prepared/RtMidi.cpp`; those exact bytes define its hash.
The generated `prepared-source.json` includes the full lock, every prepared
file's identity, and the preparation tool's current SHA-256. It contains no
machine-specific paths or timestamps.

For an explicit preparation outside CMake:

```sh
cmake -E make_directory build-midi-preparation
python3 tools/acquire_rtmidi.py --verify-existing ../rtmidi-6.0.0 \
  --prepare-build-copy build-midi-preparation/source
```

Preparation creates five files: `RtMidi.cpp`, `RtMidi.h`, `LICENSE`, the patch
and the manifest. Repeating the command verifies the exact same bytes and leaves
their modification times alone. An existing copy with any changed, missing,
extra or symlinked entry fails without repair. Preparing inside the original
checkout, or at one of its ancestors, is rejected. If a reviewed tool update
changes its manifest identity, use a fresh build directory or remove only the
old generated preparation directory before reconfiguring. Do not change the
locked dependency to make an old build copy pass.

## CMake integration contract

The root integration owns these options, with MIDI disabled by default:

```cmake
option(HAMMOND_ENABLE_MIDI "Enable the optional pinned physical MIDI backend" OFF)
set(HAMMOND_RTMIDI_ROOT "" CACHE PATH "Separately acquired, locked RtMidi checkout")
```

Inside the enabled adapter branch, after its target exists:

```cmake
include(cmake/VerifyRtMidi.cmake)
hammond_add_rtmidi(hammond_rtmidi "${HAMMOND_RTMIDI_ROOT}")
target_link_libraries(hammond_standalone_support PRIVATE hammond_rtmidi)
```

The adapter's own enabled/disabled compilation selection belongs beside that
wiring. Merely including the module performs no verification or package lookup;
the function must be called only for an explicitly enabled dependency. The
ordinary default build needs no RtMidi checkout or native MIDI SDK. A read-only
check is also available as `hammond_verify_rtmidi("${HAMMOND_RTMIDI_ROOT}")`.

`hammond_add_rtmidi` creates a static target from
`${CMAKE_CURRENT_BINARY_DIR}/<target>-prepared/RtMidi.cpp`. It does not execute
upstream CMake, build the upstream C wrapper or examples, or add upstream install
rules. Native API definitions and system libraries are private to that target;
the adapter consumes it with `PRIVATE` linkage. The prepared header is a system
include for that consumer and does not become a public core dependency. CMake
tracks the tool, lock, original files and prepared outputs as configure inputs
so ordinary changes trigger re-verification before compilation.

| Target system | Sole selected definition/API | Required system dependency |
|---|---|---|
| Linux, excluding Android | `__LINUX_ALSA__` / ALSA | ALSA development headers/library and threads |
| Windows desktop | `__WINDOWS_MM__` / WinMM | Windows SDK `winmm` |
| macOS | `__MACOSX_CORE__` / CoreMIDI | CoreServices, CoreAudio, CoreMIDI, CoreFoundation |

Missing required platform dependencies or an unsupported enabled target fail
configuration. No JACK discovery, automatic fallback or dummy backend is
provided. The target properties `HAMMOND_RTMIDI_BACKEND` and
`HAMMOND_RTMIDI_PREPARED_ROOT` expose the selected backend name and generated
directory for inspection. Runtime admission must still check RtMidi's compiled
API list and actual selected API as required by the backend contract.

For a Linux installation with a separate development sysroot, CMake accepts the
standard `ALSA_INCLUDE_DIR` and `ALSA_LIBRARY` cache inputs. Do not hard-code the
development machine's paths in project sources. Windows and macOS branches need
their own native build/run evidence; a Linux build does not qualify them.

## Notice and evidence

The unmodified upstream notice is retained at
[`LICENSE-RtMidi.txt`](../assets/standalone/midi/LICENSE-RtMidi.txt), and copied
into each prepared directory. It is the MIT-style RtMidi notice with an expressly
nonbinding request to send modifications upstream. Distributions containing the
linked dependency must include this notice; standalone package integration owns
that install rule.

Primary source identity is the
[pinned upstream tree](https://github.com/thestk/rtmidi/tree/1e5b49925aa60065db52de44c366d446a902547b).
The dependency checks establish source and build identity. Actual MIDI devices,
hotplug/close behavior, driver permissions, latency, callback ownership and
platform release qualification remain separate acceptance gates in
[MIDI_BACKEND.md](MIDI_BACKEND.md).
