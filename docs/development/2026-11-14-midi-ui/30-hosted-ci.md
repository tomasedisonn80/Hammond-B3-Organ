# A30 — hosted MIDI and reference-interface CI

Actual worker: `w05_a30_hosted_ci`, wave 5 of the separate requested
`2026-11-14-midi-ui` session. This note records this assignment only. No earlier
session workers or results are counted again.

## Owned scope and source boundary

Owned files:

- `.github/workflows/standalone.yml`
- `docs/STANDALONE_CI.md`, added to this worker's ownership explicitly by root
- This evidence note

Read the standing agent instructions, current MIDI/UI scope and session,
dependency/preparation and installation contracts, A26's completed staging note,
the existing hosted workflow, actual root/application CMake, backend selection,
native tests and exact font/reference records. Root owns shared CMake,
README/status/log, whole-source qualification, actual hosted results and
publication. No other workflow needed a change. No commits, subagents, shared
build mutations or production changes were made by this worker.

Observed repository HEAD was `e09107414896c2c53dad124a74f60c8043fadfe4`, tree
`1f117a17cf561fae8978adeb612abf9ad29d7b64`, with concurrent uncommitted work.
That commit does not identify the subsequent worktree additions or this
workflow. Local configurations used private source copies and the inventories
below, not an assumption that HEAD already contained the tested changes.

| Owned/input identity | SHA-256 |
| --- | --- |
| Previous committed `standalone.yml` | `b7f8c70ff9a4ee38d36427999efdbfd39b8c6a06a2e4921c5196e3b8604b5eba` |
| Final `standalone.yml` | `6a40b88bfc41000ce83b23830cf268067d5989863f500da63e8fd22972743b6f` |
| Final `STANDALONE_CI.md` | `6e6b121fb10b74fb52efbd310ee2d568be5a02cd626a2d2e7b73f92526d88696` |
| `tools/acquire_rtmidi.py` | `b5b436be15a7a1aa807ec342793741eaefbbc2df0dbe5f315fc7f97a690809bf` |
| `cmake/VerifyRtMidi.cmake` | `fe2f76f57ca3384aedf05da1afbe0cc3fd3989bee29120bbb252249368bbccdd` |

## Maintained hosted contract

The existing three operating-system rows now explicitly enable MIDI and compile
their actual native backend. One additional Linux row covers the disabled
application, test and package branches without multiplying every platform by
both modes.

| Runner | Compiler/generator | MIDI selection | Required compiled SDL backends |
| --- | --- | --- | --- |
| `ubuntu-24.04` | GCC / Unix Makefiles | ON, ALSA | X11, ALSA, PulseAudio |
| `macos-15` | AppleClang / Unix Makefiles | ON, CoreMIDI | Cocoa, CoreAudio |
| `windows-2022` | MSVC / Visual Studio 17 2022 x64 | ON, WinMM | Windows, WASAPI |
| `ubuntu-24.04` | GCC / Unix Makefiles | OFF, unavailable | X11, ALSA, PulseAudio |

All four rows retain Release, `BUILD_TESTING=ON`, native standalone enabled,
VST3 disabled, dummy audio/video backends for explicit test execution, the
40-minute job guard, serial CTest, individual test timeouts and the existing
180-second fallback. The requested Ubuntu development packages, installed
package inventory, static locked SDL build, actual compiler identity checks and
native SDL macro gates remain. **No `SDL_ALSA=OFF` option is present in the
hosted workflow.** The local executor workaround is not a hosted qualification
policy.

All existing full action SHA pins, exact-event checkout assertions,
`contents: read`, disabled persisted credentials, source reverification,
strict test/package gates, always-collected diagnostics and success-only
packages remain. Job and artifact names now include MIDI mode, avoiding the
otherwise colliding enabled/disabled Linux artifacts.

### Explicit RtMidi acquisition and real target evidence

Enabled jobs call the existing acquisition tool with `--destination` into a new
external `$RUNNER_TEMP/hammond-rtmidi`, then run the separate offline
`--verify-existing` path. CMake receives the actual
`HAMMOND_ENABLE_MIDI` / `HAMMOND_RTMIDI_ROOT` options and prepares the reviewed
source through the existing module. It never executes upstream RtMidi CMake or
adds a dummy/fallback API. Disabled jobs receive the explicit absent path and
do not acquire or prepare RtMidi.

After building `hammond_standalone_test_inputs`, the workflow verifies the
original checkout and the existing prepared directory with the provided
`--prepare-build-copy` operation. Its existing-copy semantics require exact
bytes; it cannot silently repair a changed prepared tree. The same verification
runs again after acceptance.

A CMake File API query requested before configuration retains the actual
**Release** codemodel. The gate checks the production support target's
`HAMMOND_HAS_RTMIDI=1` or `=0`. An enabled `hammond_rtmidi` must be a static
target with the exact prepared `RtMidi.cpp` as its sole compiled source and
exactly the selected native API definition among RtMidi's supported APIs. It
hashes the actual nonempty built `.a` or `.lib`. It does not substitute the
separate injected-backend test target for production dependency evidence.

The gate checks the config-independent
`build-standalone/generated/standalone-capabilities.json` against the matrix,
lock, preparation manifest, source, patch and license. It retains target JSON,
codemodel/index, capability, prepared manifest/patch/notice and
`midi-backend.json`, incorporating the latter into package provenance.
Disabled coverage requires no configured RtMidi target, no prepared copy, no
external checkout and the exact unavailable capability. Native compilation is
separate from usable MIDI services and physical ports.

| Locked or prepared input | SHA-256 |
| --- | --- |
| RtMidi 6.0.0 lock, commit `1e5b49925aa60065db52de44c366d446a902547b` | `4e2923a57abfaa98d68d7b339ea9a39c420f40dc3b175a339be108eaf0a987aa` |
| Original `RtMidi.cpp`, 168,212 bytes | `184d775e88e5d73b079897363fb42af155122e879f0bc9254a1c7edae4eadb3c` |
| Prepared `RtMidi.cpp`, 168,216 bytes | `240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a` |
| Original/copied `RtMidi.h`, 27,901 bytes | `74f98ca172243b0b9c0c59f53c4e20285d879ffa86b3d61692109b013f4606f9` |
| Original/copied `LICENSE`, 1,349 bytes | `7fa091d9c1aa492ebfcafa9f919d27bbce61e4f048ece2dfc3b7f93181e9e364` |
| Exact two-allocation CoreMIDI patch, 728 bytes | `80aedddee9affe1c9ab305b605c6ca1f5c2209fd5d23da843c8c3f325426c4ad` |
| Actual prepared manifest, including the preparation-tool hash | `481095a20040ffe8c824200b3b20663ebc4c392f1fc535ead7f6e679f3a5b2ae` |

### Reference and font source evidence

The initial provenance step now identifies 21 source files: six lock/provenance
manifests; both DejaVu 2.37 source TTFs and their notice; the compiled font
header; the original atlas PDF and extracted JPEG; all three compressed
decorative crops; and the two acquisition tools, two authoring tools and two
authoring-requirements files. Expected lengths and hashes are checked where the
retained manifests provide them. Font source-to-atlas and PDF/JPEG-to-reference
relationships are checked explicitly. These are source identity checks, not a
new rasterization or unmeasured pixel-fidelity claim.

The manifests are copied into diagnostics; large authoring sources are
identified without duplication. The generated reference header continues to
come from the existing verified build-time crop compiler. No font, PDF, raw
artwork or source checkout is added to the installed package.

| Reference/font input | SHA-256 |
| --- | --- |
| Source atlas PDF, original cover/page 409 | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Original embedded JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| `assets/standalone/reference/manifest.json` | `bf1bec09c0dd15d09ab0129f950ccb5370532f92cb9217e347ba69e96d24bc87` |
| `docs/design/atlas-reference.json` | `896b09b07b794ecb02d9b3be350b3166a22136fa920432c99dc7a73904c3dc50` |
| Font source manifest | `8bc668338513949846f758db5acd170dc6f73977fc14b8ba5f113a062740d4eb` |
| Font atlas manifest | `8b9413cc6acdf32f40ba272f04d0b984f9909772c295ca8c35f88f85bceb0469` |
| `DejaVuSans.ttf` | `57f73e11f51999432bf7ab22ce55b6f945d5eca1bf824404cfa9ec2e3718c84e` |
| `DejaVuSerif.ttf` | `8cb29f7db250ebb2551a6ce2c1e0bfd5a0eb520e9e233370db0493e82e1f36f7` |
| `FontData.h` | `f1a3121a2707a03a3b2e025c399e68c553ce9498f4b002ec13b18f512e334802` |

### Acceptance and exact installed payload

CTest JSON discovery is retained before the unchanged broad
`^test_standalone_` execution filter. Discovery must contain the MIDI
input/Session/replay/concurrency/backend tests, CLI/modal acceptance, drawing,
installation and the distinct new `test_standalone_native_midi_replay` name.
The SDK-free C++ replay test remains `test_standalone_midi_replay`; the two
names are not conflated. Missing required registrations fail even when other
standalone tests exist. The workflow discovers its count instead of embedding
an obsolete total. `--no-tests=error` and every existing standalone test remain.

The archive gate replaces the obsolete nine-file expectation with exactly
**13 disabled / 17 enabled files**, matching A26's installation contract. It
includes the common MIDI/UI runbook, reference manifest, atlas provenance and
generated capability. Enabled mode adds exactly the RtMidi notice, lock,
prepared manifest and patch; disabled artifacts reject these as extras. Every
installed file is compared to its actual configured source, then the moved
prefix and reopened archive are checked for exact paths, bytes, modes and
ordinary file kinds.

Relocated 600 ms dummy smoke must emit schema-2 diagnostics matching the
installed MIDI capability. No port may have been requested/opened, no device
messages may have arrived, and shutdown must be quiescent/stable without
startup or shutdown failures. The capability hash and parsed content must
also equal the earlier compiled-backend record. The existing help, audio
callback/frame, screenshot, state-preservation and payload-preservation
assertions remain. The generated capability has **no configuration suffix**.

## Executed local validation

Toolchain: Linux, GCC/G++ 14.2.0, Python 3.12.14, PyYAML 6.0.3 and CMake/CTest
4.4.4. CMake tools were read from
`/home/agent/.cache/uv/archive-v0/kvsqq5-iHdbf13RC/cmake/data/bin`.
All private work is under
`/workspace/scratch/cd4bd06ce68f/a30-hosted-ci-check`.

| Executed check | Observed result |
| --- | --- |
| YAML parsing, four exact matrix tuples and preserved full action pins | Pass. |
| Every final workflow shell block through `bash -n` | **12/12 pass.** |
| Every final Python heredoc through Python AST parsing | **6/6 pass.** |
| Actual source-identity portion of the workflow provenance script | Pass; 21 files admitted and six manifests retained. |
| Existing pinned RtMidi verification and new private prepared copy | Pass; exact commit, source/header/license, patch and manifest identities above; `network_used=false`. |
| Fresh private full-project native configurations, MIDI ON and OFF | Both configure successfully with actual pinned SDL/RtMidi inputs and absent disabled RtMidi path. |
| Actual enabled `hammond_rtmidi` build | Pass; real ALSA static library, 103,458 bytes. |
| Unchanged new workflow MIDI evidence Python against both real CMake codemodels | Both pass, including actual enabled library hash and disabled absence checks. |
| Final strict discovery after root's new native replay registration | **24 tests discovered in each configuration; required-name checks pass.** This is discovery, not 24 executed tests. |
| Final owned-file whitespace check | `git diff --check` passes. |

The native configurations leave SDL options at their actual defaults; no local
SDL ALSA disablement was used for these configuration checks. Only the RtMidi
library was compiled here. This worker did not build the full native SDL
application or run the complete CTest/package/smoke workflow locally; the
executor's known SDL/ALSA header incompatibility is not promoted to a hosted
pass or silently waived gate.

The effective private configuration commands used `-S . -B build-standalone`
from the respective `source-on` and `source-off` copies, with:

```sh
cmake -S . -B build-standalone -G 'Unix Makefiles' \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2 \
  -DCMAKE_INSTALL_BINDIR=bin -DCMAKE_INSTALL_DATADIR=share \
  -DALSA_INCLUDE_DIR=/workspace/scratch/641ca55ce6de/native-sysroot/usr/include \
  -DALSA_LIBRARY=/workspace/scratch/641ca55ce6de/native-sysroot/usr/lib/x86_64-linux-gnu/libasound.so \
  -DHAMMOND_ENABLE_MIDI=ON \
  -DHAMMOND_RTMIDI_ROOT=/workspace/scratch/cd4bd06ce68f/rtmidi
cmake --build build-standalone --config Release \
  --target hammond_rtmidi --parallel 2 --verbose
```

The separate disabled configure used the same common options with
`HAMMOND_ENABLE_MIDI=OFF` and
`HAMMOND_RTMIDI_ROOT=/workspace/scratch/cd4bd06ce68f/a30-hosted-ci-check/runner-off/hammond-rtmidi`,
which did not exist. The sysroot flags are local prerequisites only and are
absent from the hosted workflow. Prepared verification actually ran as:

```sh
python3 tools/acquire_rtmidi.py \
  --verify-existing /workspace/scratch/cd4bd06ce68f/rtmidi \
  --prepare-build-copy build-standalone/apps/standalone/hammond_rtmidi-prepared
ctest --test-dir build-standalone -C Release --show-only=json-v1 \
  -R '^test_standalone_'
```

The exact extracted workflow Python blocks are retained as `step-10-0.py`
(MIDI evidence) and `step-11-0.py` (required discovery), with their actual
per-mode outputs under each private source copy's `standalone-ci-logs`.
Configure/build logs are `configure-on.log`, `configure-off.log`,
`build-rtmidi.log` and the final reconfiguration logs. `final-syntax.json`
records the final workflow hash and parsed step names. The initial identity
assertions ran without the hosted checkout/run environment assertions; no
synthetic GitHub run identity was asserted.

| Actual local result | SHA-256 |
| --- | --- |
| Built `libhammond_rtmidi.a` | `d3dd768f60e5e8db9dcba86c39ae4931e31296cfeed092b3cb66f698a536a4ff` |
| Enabled capability JSON | `57ccbbb25c2f868db64ff7aa17cf691e9fd92917b2e640b4fd1d5a623edcbc48` |
| Disabled capability JSON | `0aa7e692d1986def4e8f5f31f0104e49ec1e50dca162fb2a14343f458a6bb204` |
| Initial 1,164-file source inventory | `daf3aae40e08ba76b55474fd79d807cc8cef5ebecd91d95666467eea5a80f74d` |
| Four-file discovery overlay inventory | `50183c413d57a40259af7bbf1b767450a8d12145772a6c3efdaf73ec814c2b6e` |
| Final 1,165-file source inventory | `6ed19415f87acce9f87b011648d15a2555d3b667298d32618b43fe1500e18e58` |

The only intentional snapshot overlay was the final owned workflow/CI guide,
root's stable application-CMake registration and the new Python replay test
file needed for discovery. No compiled RtMidi input changed. Both private
source copies were rechecked against the final inventory. The Python replay
test itself was not executed by this worker; A31/root own its timing and
substantive acceptance. Earlier discovery observed 23 names before that
registration, and final discovery observed 24. A first local overlay helper
incorrectly derived the Python filename from the distinct CTest name and
stopped with `FileNotFoundError`; inspection of the actual registration
corrected the helper to `native_tests/test_standalone_midi_replay.py`. This was
a private verification-helper mistake, not a workflow or application failure.

## Limits and integrator handoff

`actionlint` and `shellcheck` were unavailable in this executor; YAML, Bash and
Python parsing are the specifically executed syntax checks. The workflow's
network acquisition commands were inspected and retained but not executed
locally: existing verified checkouts supplied this worker's dependencies.
No Windows/WinMM or macOS/CoreMIDI compilation, GitHub-hosted run, native
desktop/audio device, physical MIDI controller, hotplug/latency qualification,
signing or redistribution clearance is claimed. The exact package gate and
all four hosted jobs remain to be executed at the published coherent revision.
Reference-art publication rights retain the project's unresolved gate.

Root should freeze and qualify the completed source, recheck repository links
after this note exists, publish through the standing guarded workflow, and
observe all four exact-SHA standalone matrix results. Retain acquisition/setup
failures separately from compiler, test or artifact failures. For successful
jobs inspect the native SDL macros, production RtMidi target/source/API/library
evidence, final required-test discovery, JUnit/full CTest log, capability and
13/17-file byte inventories. Verify the mode-specific package and archive
hashes and relocated runtime evidence. An uploaded artifact or workflow
dispatch alone is not a hosted pass. Shared status and platform handoff should
name only the completed observed results of that exact publication.
