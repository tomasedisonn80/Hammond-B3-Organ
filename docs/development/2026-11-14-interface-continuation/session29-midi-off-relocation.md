# A29 — Separately compiled MIDI-off runtime and relocation

Actual worker `/root/w05_a29_midi_off_relocation`, assignment **29/60**, logical
wave **5**, 14 November 2026. This assignment qualifies a separately compiled
MIDI-disabled executable and its real installed package. A24's disabled install
fixture used an enabled executable; that earlier fixture remains accurately
scoped in its [note](24-setup-package.md).

**Result: passed.** Three focused CTest suites passed all **44 unittest methods**;
the independent actual 15-file relocation probe passed six native invocations;
one further installed synthetic-MIDI workspace method passed. No installation
defect was observed and A29 changed no production source, package rule, guide,
license, parameter, state, DSP, asset or VST3 file. Root owns integration and
publication; no files were staged or committed by this worker.

## Exact source and build

Checkout: `/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
HEAD remains `5d81199a9822874b55f3b0a124715cbd6eadf0e5`, committed tree
`52b4ec72b77e4442efe2e9e1b089b7b0ea6e638b`. The tested interface is an
uncommitted overlay, identified by the [98 production hashes](reports/a29-source-before.json).
Its sorted path/NUL/hash/LF inventory digest is
`d85e6e28214f15f8b3d47649439baa7d0aa13d7b6d660b14fc48278c98104a19`.

Root cleared CMake after registering A28's scale test. A29 created one reusable
build, `/workspace/scratch/601951e27dc3/build-native-midi-off`, using shared SDL2
source at `/workspace/scratch/7ffc2842608b/SDL2`. CMake/CTest are 4.4.4 under
`/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin`; GCC is 14.2.0,
Python is 3.12.14 and the generator is Unix Makefiles/Release. Standalone and
testing are ON; MIDI, VST3, sanitizers and SDL ALSA are OFF. RtMidi and VST3 root
cache entries are empty. No dependency source was acquired or copied.

The initial build completed as A28 announced its authorized clip-restoration
repair. Its [identity](reports/a29-initial-build.json),
[source](reports/a29-source-initial-before.json) and
[log](reports/a29-build-initial.txt) remain historical; no A29 tests ran against
that binary. After A28 explicitly froze the renderer at
`6b498c9ba2c47acf432216189159b928d2a5d31368ec34c1fe8dc906710e8a67`, A29 verified
that only `InstrumentView.cpp` had changed among the production inputs, deleted
only its own corresponding object, and rebuilt the application. The
[final build log](reports/a29-build.txt) records that recompilation and link.

**Qualified executable SHA-256:**
`20bf16c85d3d29157af5e175919491bae14d3663bdab281e0639dacba5cc28f0`.
The [build identity](reports/a29-build-identity.json) retains 18 generated,
library, executable and configuration hashes. The production support target's
actual flags contain `HAMMOND_HAS_RTMIDI=0`; there is no `_rtmidi` build directory.
The reusable build contains approximately **30.7 MB** of files after testing.
A29 did not use `build-native` or the SDK-free build.

## Executed gates

| Gate | Actual outcome |
| --- | --- |
| `test_standalone_install` | 8 methods passed, 6.14 s; actual MIDI-off package plus strict private install-rule fixtures. |
| `test_standalone_app` | 21 methods passed, 184 native subprocesses, 14.90 s. Includes current workspace/Flat startup and painted-view observations. |
| `test_standalone_midi_cli` | 15 methods passed, 95 native subprocesses, 11.00 s; zero native enumeration errors, nine successful UI replays and two deliberately invalid-channel replays with their expected failures. |
| Independent relocated probe | Six native invocations passed their expected exit codes after real component installation and movement. |
| Installed synthetic owner/navigation replay | One method and one native subprocess passed in 3.326 s, with six accepted packets, zero drops and five accepted Note On/five Note Off commands. |

The [verbose CTest log](reports/a29-ctest.txt) reports **3/3 suites passed in
32.05 s**. The separate [synthetic log](reports/a29-synthetic-workspace.txt)
identifies the same installed executable. Its copied diagnostics identify
`source="synthetic-replay"` while the native backend remains `unavailable`.
Independent UI/MIDI owners survive Play/Rotary/Service changes, Flat, resize and
the UI releases; final release and joined shutdown are checked. This is one
selected existing workspace method, not a claim that A29 repeated all six.

## Actual package and installed operation

The independent [relocation report](reports/a29-relocation.json) contains the
literal 15-path expected inventory and every source/binary SHA-256. It installs
the real `Standalone` component, compares **one executable plus fourteen metadata
files**, moves only its own prefix and executes it from an unrelated directory
outside the checkout. Every guide, notice, manifest and both licenses exactly
matches its source bytes; installed relative guide links resolve. Capabilities
agree with the compiled runtime:

```json
{"enabled": false, "backend": "unavailable", "rtmidi": null}
```

The relocated application passed `--help`, including `--workspace` and `--flat`.
`--list-midi` returned the explicit unavailable-build error with deliberately
invalid SDL drivers and no output-file writes. A 600 ms `--workspace service
--flat` smoke at 960×700 rendered the actual six-card inspector with the embedded
nominal profile and glyph/art resources, observed held/released notes, and left
its absent private control path absent. The retained
[actual Service Flat image](reports/a29-relocated-service-flat.png) was visually
inspected: the complete common header and six cards are visible, CURRENT SNAPSHOT
is explicit, and the footer states MIDI UNAVAILABLE. This is the only retained PNG.

A private noncanonical state4 file then survived Play → Rotary → Rotary Flat →
Service Flat → Play Flat → Play navigation byte-for-byte. Paint observations
followed that exact sequence; the Session frame clock increased without reset,
controls stayed constant, and the held UI note received its original release.
From Service Flat, pointer activation of MIDI, Apply No input, Disconnect and
Close remained usable, followed by computer-key playing. No native discovery
worker started in the disabled build.

An explicit nonexistent exact `--midi-port` request returned 1, reported backend
unavailability, made zero physical open attempts/callbacks, and preserved a valid
existing state file and its applied fixed registrations. Successful runtime
probes recorded zero application/audio errors, stopped/unheld Session state,
quiescent MIDI, stable final diagnostics and no pending discovery after shutdown.
Every installed file and the built executable remained unchanged after all runs.

The final retained prefix is
`/workspace/scratch/601951e27dc3/a29-midi-off-relocation-final/relocated organ Ω`;
its payload is **3,755,050 bytes**. The shared repository and SDK were never
renamed or removed. The source-unavailable private fixture remains a separately
identified install-rule check; relocation does not pretend the shared source was
hidden from these actual runtime processes.

## Reproduction and retained correction

The [source record](reports/a29-source-before.json) retains the exact fresh
configure command. With that configuration and stable source, the focused gate is:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/601951e27dc3/build-native-midi-off \
  --config Release --target hammond_standalone --parallel 3
env PYTHONDONTWRITEBYTECODE=1 \
  /workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/601951e27dc3/build-native-midi-off \
  -C Release --verbose --output-on-failure --no-tests=error \
  -R '^(test_standalone_install|test_standalone_app|test_standalone_midi_cli)$'
```

The retained [probe](reports/a29-qualify-relocation.py) accepts explicit `--source`,
`--build`, `--cmake`, `--sdl`, new absent `--work` and existing `--reports` paths.
Every invocation records its actual command and process output. Its first run
incorrectly expected empty successful-smoke stdout. The application had passed
and correctly printed its documented native summary. The
[first failure](reports/a29-relocation-first.json),
[log](reports/a29-relocation-first.txt) and
[diagnostics](reports/a29-service-flat-first-diagnostics.json) are retained.
The harness correction verifies the exact summary and its callback/frame/image
counters against diagnostics; the final fresh-stage run passed. Only that
reproducible first owned stage and BMP were removed after retaining their hashes.

The [final result](reports/a29-midi-off-relocation.json) links all evidence and
limits. The [after-check](reports/a29-source-after.json) confirms no change in
98 production inputs, seven relevant build/test inputs, 114 protected files,
18 build identities or 15 installed files. Retained A29 evidence before its
summary is approximately 310 KB, including the 92 KB PNG.

## Limits and next action

This is Linux Release qualification with SDL dummy audio/video. No physical
audio/MIDI device, native display/DPI, persistent pointer capture, accessibility,
callback deadline, hosted platform, exact reference equality, measured model,
signing or distribution-rights gate is closed. A29 did not repeat the full core
or native matrix. Root may reuse the new MIDI-off build for its later complete
gate after building the required native test targets. Any later installed-guide
change requires reconfigure/rebuild and a fresh destination for exact package
acceptance. The current full M0–M9 plan and acquisition limits remain in force.
