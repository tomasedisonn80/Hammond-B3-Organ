# Native standalone CI

[The workflow](../.github/workflows/standalone.yml) configures the optional native
application from the exact event commit on pushes to `main`, pull requests and
manual dispatch. It uses `contents: read`, disables persisted checkout credentials,
and reuses the full official action pins from the existing CI workflows. Checkout
must equal `GITHUB_SHA`; tracked changes fail before work and before packaging.

## Native build matrix

| Runner | Compiler / generator | Required compiled SDL backends |
| --- | --- | --- |
| `ubuntu-24.04` | GCC / Unix Makefiles | X11, ALSA, PulseAudio |
| `macos-15` | AppleClang / Unix Makefiles | Cocoa, CoreAudio |
| `windows-2022` | MSVC / Visual Studio 17 2022, x64 | Windows, WASAPI |

All jobs explicitly enable `HAMMOND_BUILD_STANDALONE` and `BUILD_TESTING`, disable
`HAMMOND_BUILD_VST3`, and build/test/install Release. Windows uses the actual
`Release` executable subdirectory and `--config Release` / `-C Release`. The job
has a 40-minute limit; individual CTest tests have their declared timeouts and
a 180-second fallback. No application/font rasterization step is required.

## Explicit dependency and runner setup

`tools/acquire_sdl2.py --destination "$RUNNER_TEMP/hammond-sdl2"` acquires the
[locked external SDL2 checkout](STANDALONE_DEPENDENCY.md); `--verify-existing` runs
locally before configure and again after acceptance. CMake never downloads it.
The workflow retains the SDL lock, font source manifest and their SHA-256 values.
Compiled glyph atlases and the embedded nominal profile are application inputs;
Pillow, FreeType and loose font files are not installed-runtime prerequisites.

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

## Required acceptance and relocation

The workflow first builds `hammond_standalone_test_inputs`, which collects the
application and all standalone C++ acceptance inputs. It then invokes:

```sh
ctest --test-dir build-standalone -C Release -V --parallel 1 \
  --no-tests=error --timeout 180 -R '^test_standalone_' \
  --output-junit "$GITHUB_WORKSPACE/standalone-ci-logs/ctest.xml"
```

The filter covers Session, UI, state files, concurrent exchange, actual SDL audio,
calibrated callback allocation, application CLI/smoke and installation acceptance.
`SDL_AUDIODRIVER=dummy` and `SDL_VIDEODRIVER=dummy` are selected only for these CI
tests and the relocated smoke. Production driver selection gains no fallback.

After passing tests, the explicit `Standalone` component installs into a fresh
prefix with `bin` / `share` directories. A standard-library inventory requires
exactly the [documented nine files](STANDALONE_INSTALL.md), compares every file to
its source bytes, records size/SHA-256/mode, and rejects symlinks, Windows reparse
points, special files, extra files and extra directories. The prefix is moved
and its inventory must remain identical. From an unrelated working directory,
the relocated executable runs `--help` and `--smoke-ms 600` with explicit private
state, BMP and JSON destinations. Actual callbacks/frames, dummy driver identity,
successful screenshot/diagnostics and unchanged installed bytes are required.

## Retained evidence and qualification boundary

Diagnostics upload with `always()`, including after failed gates: source commit
and tree, run/attempt/runner/image, dependency identities, compiler/configuration,
apt/acquisition/configure/build/test/install logs, JUnit, complete `LastTest.log`,
failure logs, installed inventories and relocated smoke JSON/BMP. Artifact names
include platform, architecture, exact event SHA and run attempt; retention is 14 days.

Only successful gates upload the intact moved prefix in
`HammondB3-Standalone-Release.tar.gz`, `inventory.json` and `SHA256SUMS`. The archive
is reopened to check its exact file set, bytes, sizes and modes. Its inventory
includes source/run/toolchain/dependency identity and smoke evidence hashes.

This document describes the maintained workflow, not an observed hosted pass.
[Assignment 25](development/2026-11-13-next-phases/25-standalone-ci.md) records local
syntax/source checks. Integrators must observe each exact-revision hosted result
and retain failures separately from runner/setup problems. Dummy smoke establishes
software callback/render/relocation behavior; audible hardware, hotplug, latency,
underruns, native accessibility, redistribution notices, runtime dependencies,
project licensing, signed installers and public releases retain separate gates.
