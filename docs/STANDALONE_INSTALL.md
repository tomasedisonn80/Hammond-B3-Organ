# Local standalone installation and relocation

The optional `Standalone` component stages the built native instrument and its
small, fixed documentation/notice payload. It is an explicit local installation
operation; ordinary installation continues to select `OfflineTools` only.
The executable embeds the nominal profile and generated DejaVu glyph atlases.
Installed execution does not read the source checkout, SDL2 source, an SDK,
`nominal.b3p`, TTFs, Python, Pillow or FreeType. Platform runtime libraries and
available SDL drivers still come from the selected build and operating system.

## Build, stage and move

Acquire the pinned SDL2 source as described in `STANDALONE_DEPENDENCY.md`, then
run from the repository root (CMake 3.21+, Python 3.10+, C++20 compiler):

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=/absolute/path/to/SDL2
cmake --build build-native --config Release --target hammond_standalone --parallel 3
cmake --install build-native --config Release --component Standalone \
  --prefix "/absolute/path/staged organ"
mv "/absolute/path/staged organ" "/absolute/path/moved organ"
"/absolute/path/moved organ/bin/hammond_standalone" --help
"/absolute/path/moved organ/bin/hammond_standalone"
```

Use the actual selected configuration with a multi-configuration generator.
An unknown configuration name is rejected before any destination write, including
metadata copies. Names are matched without case sensitivity against the build's
configured names, so declared custom configurations remain supported. A declared
configuration still requires its own built executable; another configuration's
binary cannot satisfy that preflight. Single-configuration generators retain
their configured executable selection regardless of the install `--config` label.
Windows uses `hammond_standalone.exe`. Prefixes may contain spaces and Unicode.
`CMAKE_INSTALL_BINDIR` and `CMAKE_INSTALL_DATADIR` may be nonempty relative paths
without parent traversal or list separators; configure them before staging.
Defaults are `bin` and `share`. Existing destination ancestors must be ordinary
directories. `DESTDIR` staging is honored. `CMAKE_INSTALL_MODE` must be unset,
empty or `COPY`; staging preserves executable bytes and does not strip them.

## Exact payload

There are nine files, with no runtime font/profile or research PDF:

| Installed path (beneath the prefix) | Source |
| --- | --- |
| `bin/hammond_standalone[.exe]` | Selected built target, copied without modification |
| `share/hammond-b3-organ/standalone/STANDALONE_INSTALL.md` | `docs/STANDALONE_INSTALL.md` |
| `share/hammond-b3-organ/standalone/STANDALONE_APP.md` | `docs/STANDALONE_APP.md` |
| `share/hammond-b3-organ/standalone/STANDALONE_MODEL.md` | `docs/STANDALONE_MODEL.md` |
| `share/hammond-b3-organ/standalone/THIRD_PARTY_NOTICES.md` | Root notice file |
| `share/hammond-b3-organ/standalone/LICENSE-SDL2.txt` | Locked SDL2 `LICENSE.txt`, exact bytes |
| `share/hammond-b3-organ/standalone/LICENSE-DejaVu.txt` | `assets/standalone/fonts/LICENSE-DejaVu.txt`, exact bytes |
| `share/hammond-b3-organ/standalone/sdl2-lock.json` | `data/dependencies/sdl2-lock.json` |
| `share/hammond-b3-organ/standalone/font-source-manifest.json` | `assets/standalone/fonts/source-manifest.json` |

Replace `bin`/`share` with the configured relative directories. Guide bodies
remain readable offline; references to other repository documents need the
source checkout. The font manifest identifies authoring inputs, not extra
installed runtime files. SDL2 is the locked 2.32.10 static target; DejaVu is 2.37.

Before any destination write, installation checks the selected executable and
every metadata input for a nonempty ordinary file, rejecting symlinks and
special files. License hashes must match the configured identity records;
those records must still match their configured bytes. Build the chosen target
and retain the source guides/notices before invoking installation.

An existing application binary or dedicated `standalone` metadata directory,
including an empty directory or dangling symlink, fails before copying. Choose
a fresh destination for a new installation. Unrelated prefix contents, including
`OfflineTools` files in the same `bin` and `share/hammond-b3-organ`, can coexist.
This is preflight protection, not an atomic transaction against later disk/I/O
failure or concurrent filesystem mutation.

## Maintained native acceptance

```sh
ctest --test-dir build-native -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_install$'
```

The native-only Python test requires the built application. It stages the real
component, checks the exact file set and source hashes, moves the prefix, then
runs relocated `--help` and a 600 ms actual SDL dummy audio/video smoke from an
unrelated directory with explicit private state and diagnostics paths. Rendering
and nominal-profile diagnostics exercise the embedded glyph/profile path.
It also checks failure preflight against private copied inputs, explicit opt-in,
custom relative paths, missing selected configurations, overwrite refusal and
copy mode. Against the actual configured build, an unknown multi-config name
must preserve fresh and pre-existing destinations, including sentinel bytes and
empty directories. A single-config build instead checks that its selected
executable and all eight metadata files are copied completely. This introduces
no Ninja or other additional generator dependency and no capability skip.
It never renames or damages shared build products. No prerequisite
failure is silently skipped. The registration provides `HAMMOND_TEST_CMAKE`,
`HAMMOND_TEST_BUILD_DIR`, `HAMMOND_TEST_CONFIG`, `HAMMOND_STANDALONE_EXECUTABLE`,
`HAMMOND_SDL2_ROOT`, `HAMMOND_INSTALL_BINDIR` and `HAMMOND_INSTALL_DATADIR`.

This gate establishes local copy/relocation and dummy-backend engineering only.
Native desktop/audio hardware, Windows/macOS packaging, runtime dependency and
all applicable bundled SDL notice inventories, project licensing, branding,
signing, and release distribution remain separate gates. The installed model
guide preserves the nominal/unmeasured dry-organ scope; no installer or license
clearance is claimed. See the dated assignment evidence in the source checkout
at `docs/development/2026-11-13-next-phases/23-standalone-install.md`.
