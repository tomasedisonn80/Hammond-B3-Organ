# Native standalone CI

[The workflow](../.github/workflows/standalone.yml) configures the optional native
application from the exact event commit on pushes to `main`, pull requests and
manual dispatch. It uses `contents: read`, disables persisted checkout credentials,
and reuses the full official action pins from the existing CI workflows. Checkout
must equal `GITHUB_SHA`; tracked changes fail before work and before packaging.

## Native build matrix

| Runner | Compiler / generator | Physical MIDI build | Required compiled SDL backends |
| --- | --- | --- | --- |
| `ubuntu-24.04` | GCC / Unix Makefiles | Enabled, RtMidi ALSA | X11, ALSA, PulseAudio |
| `macos-15` | AppleClang / Unix Makefiles | Enabled, RtMidi CoreMIDI | Cocoa, CoreAudio |
| `windows-2022` | MSVC / Visual Studio 17 2022, x64 | Enabled, RtMidi WinMM | Windows, WASAPI |
| `ubuntu-24.04` | GCC / Unix Makefiles | Disabled, unavailable backend | X11, ALSA, PulseAudio |

All jobs explicitly enable `HAMMOND_BUILD_STANDALONE` and `BUILD_TESTING`, disable
`HAMMOND_BUILD_VST3`, and build/test/install Release. Windows uses the actual
`Release` executable subdirectory and `--config Release` / `-C Release`. The job
has a 40-minute limit; individual CTest tests have their declared timeouts and
a 180-second fallback. No application/font rasterization step is required.
The three existing platform rows now compile their real optional MIDI APIs; one
additional Linux row qualifies the disabled executable, native tests and package
without acquiring RtMidi. MIDI mode appears in job and artifact names. This
does not claim disabled native builds on Windows/macOS were also executed.

## Explicit dependency and runner setup

`tools/acquire_sdl2.py --destination "$RUNNER_TEMP/hammond-sdl2"` acquires the
[locked external SDL2 checkout](STANDALONE_DEPENDENCY.md); `--verify-existing` runs
locally before configure and again after acceptance. CMake never downloads it.
Enabled rows additionally run `tools/acquire_rtmidi.py --destination
"$RUNNER_TEMP/hammond-rtmidi"` and a separate `--verify-existing` check. The
[RtMidi lock and preparation contract](RTMIDI_BUILD.md) pins 6.0.0, commit
`1e5b49925aa60065db52de44c366d446a902547b`, and the exact two-allocation CoreMIDI
initialization correction. Configuration invokes the offline verifier/preparer;
the original checkout is never compiled or modified in place.

After compilation and again after acceptance, the workflow runs
`--verify-existing` with `--prepare-build-copy
build-standalone/apps/standalone/hammond_rtmidi-prepared`. An existing prepared
copy must match; the tool cannot silently repair it. Logs retain the original
checkout/tag/commit verification, full lock, prepared manifest, preparation-tool
hash, exact patch and notice. All three platforms compile the same identified
prepared source; their API definition and system linkage are platform-specific.
Disabled rows receive the explicit absent RtMidi path but never acquire or
prepare that dependency.

Provenance records the source commit/tree and exact source bytes for the SDL and
RtMidi locks, font source/atlas manifests, both DejaVu 2.37 TTF inputs, their
notice and the compiled `FontData.h`, reference manifest, atlas extraction
record, original atlas PDF/JPEG, all three compressed decorative crops, and
authoring/acquisition tools and requirements. Manifest relationships, expected
file lengths and source hashes are checked. The font/reference manifests are
copied into diagnostics; large authoring inputs are identified by hash rather
than duplicated there. These reference pixels remain generated design-concept
decoration with the retained rights limits, not application screenshots or
physical evidence. The generated reference header is built from the verified
crops. Compiled glyph atlases and the embedded nominal profile are application
inputs; Pillow, FreeType and loose font files are not installed-runtime
prerequisites.

Ubuntu installs `pkg-config`, `libasound2-dev`, `libpulse-dev`, `libx11-dev`,
`libxext-dev`, `libxrandr-dev`, `libxcursor-dev`, `libxfixes-dev`, `libxi-dev` and
`libxss-dev` on the runner. This modest X11/audio subset comes from the actual
[pinned SDL Linux guide](https://github.com/libsdl-org/SDL/blob/5d249570393f7a37e037abf22cd6012a4cc56a71/docs/README-linux.md).
The copied guide, apt output, requested packages and complete installed package
versions are retained. These distro packages are not claimed to be immutable.

After configure, the actual generated Release `SDL_config.h` must enable the
native backends above and the explicit dummy test backends. The header, parsed
backend macros and actual C/C++ compiler identity/version records are retained.
Compiled backend availability does not establish a working physical device.
The hosted workflow does not inherit the executor's local `SDL_ALSA=OFF`
workaround. Both Linux rows retain required SDL ALSA, PulseAudio and X11
compilation, including the row whose separate MIDI transport is disabled.

## Configured and compiled MIDI evidence

A CMake File API codemodel query is requested before configuration. After
building the actual acceptance target, the selected **Release** codemodel must
show `HAMMOND_HAS_RTMIDI=1` or `=0` on `hammond_standalone_support` according to
the matrix. An enabled `hammond_rtmidi` must be a static target compiling the
exact prepared `RtMidi.cpp` with solely the selected ALSA, CoreMIDI or WinMM API
definition. Its actual nonempty `.a` or `.lib` output is hashed. The selected
target JSON, codemodel and index are retained; these checks apply to the real
dependency target rather than the independent injected-backend acceptance
fixture.

The config-independent record
`build-standalone/generated/standalone-capabilities.json` must agree with the
matrix and prepared lock/source/patch/notice/manifest identities. Disabled
coverage requires `enabled=false`, `backend="unavailable"`, `rtmidi=null`, no
configured RtMidi target, no prepared directory and no external RtMidi checkout.
The resulting `midi-backend.json` and capabilities are included in provenance.
These records establish build selection; they do not enumerate, open or attest
to a physical port.

## Required acceptance and relocation

The workflow first builds `hammond_standalone_test_inputs`, which collects the
application and all standalone C++ acceptance inputs. It then invokes:

```sh
ctest --test-dir build-standalone -C Release -V --parallel 1 \
  --no-tests=error --timeout 180 -R '^test_standalone_' \
  --output-junit "$GITHUB_WORKSPACE/standalone-ci-logs/ctest.xml"
```

Before execution, CTest JSON discovery must include the MIDI input, Session,
replay, concurrency and injected-backend suites, `test_standalone_midi_cli`,
`test_standalone_native_midi_replay`, `test_standalone_drawing` and
`test_standalone_install`. The recorded discovery
contains the actual test count rather than a historical fixed count. The broad
filter preserves all standalone acceptance, including Session, UI, state files,
concurrent exchange, actual SDL audio, callback allocation, application
CLI/modal behavior, drawing, musical replay/chapel/workflows, benchmark and
installation acceptance.
`SDL_AUDIODRIVER=dummy` and `SDL_VIDEODRIVER=dummy` are selected only for these CI
tests and the relocated smoke. Production driver selection gains no fallback.
MIDI enumeration can report an unavailable service or no ports on a hosted
runner; the native CLI suite distinguishes those observed outcomes. It does
not require a controller or treat a fabricated physical input as acceptance.

After passing tests, the explicit `Standalone` component installs into a fresh
prefix with `bin` / `share` directories. A standard-library inventory requires
exactly the [documented 13 disabled or 17 enabled files](STANDALONE_INSTALL.md), compares every file to
its source bytes, records size/SHA-256/mode, and rejects symlinks, Windows reparse
points, special files, extra files and extra directories. The prefix is moved
and its inventory must remain identical. From an unrelated working directory,
the relocated executable runs `--help` and `--smoke-ms 600` with explicit private
state, BMP and JSON destinations. Actual callbacks/frames, dummy driver identity,
successful screenshot/diagnostics and unchanged installed bytes are required.
Schema-2 MIDI diagnostics must match the installed capability: enabled/native
or disabled/unavailable, no requested/opened port or callback messages, stable
quiescent shutdown and no startup/shutdown failure. The four enabled-only files
are the RtMidi notice, lock, prepared-source manifest and exact correction
patch. They are forbidden extras in a disabled package. The common payload
includes the MIDI/UI runbook, reference manifest, atlas provenance and generated
capability alongside the existing executable and metadata.

## Retained evidence and qualification boundary

Diagnostics upload with `always()`, including after failed gates: source commit
and tree, run/attempt/runner/image, dependency/asset/prepared-source identities,
compiler/configuration/native backend records,
apt/acquisition/configure/build/test/install logs, CTest discovery, JUnit, complete `LastTest.log`,
failure logs, installed inventories and relocated smoke JSON/BMP. Artifact names
include platform, architecture, MIDI mode, exact event SHA and run attempt;
retention is 14 days. Generated capability and prepared metadata paths are also
collected directly when an earlier gate prevents the later provenance step.

Only successful gates upload the intact moved prefix in
`HammondB3-Standalone-Release.tar.gz`, `inventory.json` and `SHA256SUMS`. The archive
is reopened to check its exact file set, bytes, sizes and modes. Its inventory
includes source/run/toolchain/dependency identity and smoke evidence hashes.

This document describes the maintained workflow, not an observed hosted pass.
[A30](development/2026-11-14-midi-ui/30-hosted-ci.md) records the current workflow's
local syntax, source and command checks and their limits. The preceding
[assignment 25](development/2026-11-13-next-phases/25-standalone-ci.md) remains a
dated record of the earlier workflow. Integrators must observe each exact-revision hosted result
and retain failures separately from runner/setup problems. Dummy smoke establishes
software callback/render/relocation behavior; audible hardware, hotplug, latency,
underruns, native accessibility, redistribution notices, runtime dependencies,
project licensing, signed installers and public releases retain separate gates.
