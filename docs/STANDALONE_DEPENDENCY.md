# Pinned SDL2 dependency for the native standalone

SDL2 supplies the optional standalone's window, input and audio transport. It
does not enter the SDK-free core or replace the separately pinned VST3 SDK.
The [standalone scope](STANDALONE_SCOPE.md) keeps the instrument's current dry
model and existing control/state identities authoritative.

## Reviewed source identity

The [lock](../data/dependencies/sdl2-lock.json) and
[acquisition tool](../tools/acquire_sdl2.py) admit exactly this release:

| Field | Reviewed value |
| --- | --- |
| Official repository | `https://github.com/libsdl-org/SDL.git` |
| Version/tag | `2.32.10` / `release-2.32.10` |
| Commit | `5d249570393f7a37e037abf22cd6012a4cc56a71` |
| Primary license | Zlib; `LICENSE.txt`, 884 bytes |
| License SHA-256 | `97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127` |

The local source's commit, exact release tag and license bytes were inspected.
The [official release directory](https://www.libsdl.org/release/) lists SDL2
2.32.10, and the [official licensing page](https://www.libsdl.org/license.php)
identifies SDL 2 and later as Zlib-licensed. The selected release is a fixed
reviewed dependency, not a claim about the newest available SDL release.

## Explicit acquisition and read-only verification

From the Hammond repository root, with Python 3.10+ and Git installed:

```sh
# Network acquisition is an explicit action. The parent directory must exist;
# the destination itself must not exist, even as an empty directory or symlink.
python3 tools/acquire_sdl2.py --destination ../SDL2

# This is local and read-only: no fetch, reset, checkout, clean or repair.
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
```

Acquisition clones the locked official tag into a new external directory,
with LF checkout settings and no submodule recursion, then verifies it. The
tool never reuses an existing destination or deletes a failed new checkout.
Choose another new path or inspect a failed attempt yourself. Existing source
configuration and files are not repaired automatically.

Verification resolves the source path and requires its own Git checkout root
outside this project. A child directory inheriting its parent's repository is
rejected. `HEAD` and the named local release tag must both resolve to the
locked commit. The tool checks tracked modifications, index flags that could
hide modifications, every untracked/ignored file, required source files and
the primary notice's exact size/SHA-256. Keep build output outside the SDL2
checkout, including otherwise ignored generated files. Shallow clones are
supported; sparse and partial/promisor checkouts are not admitted. Empty
untracked directories have no source content and are ignored.

The `--lock` option supports an explicit lock location, but cannot select a
different repository, release or notice. Unknown/duplicate fields, wrong
types and substituted identities fail before acquisition or verification.
Upgrading SDL2 requires a new source/license review and coordinated updates to
the lock and the tool's reviewed constants. Local remote names/URLs are not an
identity substitute: verification does not contact or rewrite remotes.

Successful commands print one JSON result containing the resolved root,
version, repository, tag, commit, primary license count and `network_used`.
Local verification reports `false`; successful explicit acquisition reports
`true`. Invalid usage returns 2; rejected identity/acquisition returns 1.

## Optional CMake integration contract

[VerifySdl2.cmake](../cmake/VerifySdl2.cmake) provides
`hammond_verify_sdl2(root)`. It finds the Python interpreter and invokes only
`--verify-existing` with this repository's own lock. It resolves the tool and
lock beside the module, so an enclosing project's `project()` cannot select
another verifier. CMake configuration never acquires SDL2.

The top-level standalone integration owns `HAMMOND_BUILD_STANDALONE` (default
OFF), `HAMMOND_SDL2_ROOT`, and the optional `add_subdirectory` call. It must
verify the supplied source before evaluating SDL2's CMake code. Enable the C
language only in that optional branch: the pinned upstream starts with
`project(SDL2 C)` and builds C source. The ordinary C++ core/VST3 configuration
must not acquire an SDL2 dependency or require a C compiler solely for SDL2.

The inspected upstream option/target names are:

| Setting | Standalone integration value/reason |
| --- | --- |
| `SDL_SHARED=OFF`, `SDL_STATIC=ON` | Build the selected source as a static dependency; link `SDL2::SDL2-static`. |
| `SDL_TEST=OFF`, `SDL_TESTS=OFF` | Do not build the upstream test support library or test applications by default. |
| `SDL2_DISABLE_INSTALL=ON` | Keep upstream installation out of the project's installation rules. The pinned release does **not** define `SDL_INSTALL`. |
| External binary directory | Pass an explicit build-tree directory to `add_subdirectory`; use `EXCLUDE_FROM_ALL`. |

These names come from the pinned upstream
[CMakeLists.txt](https://github.com/libsdl-org/SDL/blob/5d249570393f7a37e037abf22cd6012a4cc56a71/CMakeLists.txt)
and [CMake documentation](https://github.com/libsdl-org/SDL/blob/5d249570393f7a37e037abf22cd6012a4cc56a71/docs/README-cmake.md).
`SDL2::SDL2main` is a separate upstream target; the application owns its
platform entry-point decision. Do not apply Hammond's strict C++ target
warning policy globally to this external C project.

## Backends and observed Linux limitation

Upstream offers platform-dependent audio/video drivers, including X11,
Wayland, ALSA, PulseAudio, PipeWire and JACK on Linux. Requested CMake options
are not proof that development headers were found or that a driver compiled.
Inspect the generated `SDL_config.h`, configure report and runtime driver
enumeration for the actual artifact.

The integrating agent's existing local static build at
`/workspace/scratch/5ba97739b54c/sdl2-build` was inspected on 2026-11-13.
Its generated `include-config-release/SDL2/SDL_config.h` enables **dummy and
offscreen video**, and **disk, dummy and OSS audio**. X11, Wayland, ALSA,
PulseAudio and PipeWire were not compiled in this environment despite their
requested cache options. The required development headers are absent.

Dummy callbacks and offscreen/software rendering can exercise the adapter.
They do not establish a visible native desktop window, audible hardware
playback, real-device latency or reliable device reopening. A later hosted
setup must supply the selected desktop/audio development packages, build the
same pin, retain the resulting backend inventory, and execute actual window
and audio-device checks. Dependency verification does not close those gates.

## Notices and distribution boundary

Preserve the primary Zlib notice when distributing SDL source, keep source
origin accurate, and identify any altered versions. Acknowledgment in product
documentation is appreciated by the upstream notice. No SDL2 source or binary
is newly vendored by this dependency setup.

The primary license check is not a complete distribution notice inventory.
The pinned tree also contains `src/hidapi/LICENSE.txt` with its alternative
license choices and `src/video/yuv2rgb/LICENSE` with a BSD-style notice that
requires notice retention for binary distribution. Preserve applicable
bundled notices and record the chosen HIDAPI license and compiled backend
dependencies when packaging an actual standalone artifact. These upstream
files remain covered by the source pin and cleanliness check; this helper
hashes the primary `LICENSE.txt` explicitly. Project licensing, third-party
binary notices, platform signing and release packaging remain separate work.

The [assignment evidence](development/2026-11-13-next-phases/08-sdl-dependency.md)
records executed checks and their scope.
