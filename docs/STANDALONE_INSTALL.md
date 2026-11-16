# Local standalone installation and relocation

The optional `Standalone` component stages the built native instrument and its
fixed documentation, capability and notice payload. Ordinary installation
continues to select `OfflineTools` only. A fresh standalone destination contains
**17 files with MIDI disabled, or 21 with MIDI enabled**.

The executable embeds the nominal profile, generated DejaVu glyph atlases and
the historical three decorative regions and separate masked lower apron from
the supplied atlas reference. Installed execution
does not read a source checkout, SDL2/RtMidi source, an SDK, `nominal.b3p`, TTFs,
the atlas PDF/JPEG, Python, Pillow or FreeType. Platform runtime libraries,
SDL drivers and any enabled native MIDI service still come from the selected
build and operating system. This local staging operation does not collect or
qualify those external runtimes.

## Use an already staged instrument

Keep the complete installed directory together; it can be moved without changing
its files. With the default layout, the executable is
`bin/hammond_standalone` (`bin/hammond_standalone.exe` on Windows), and this guide
is in `share/hammond-b3-organ/standalone`.

```sh
"/absolute/path/moved organ/bin/hammond_standalone" --help
"/absolute/path/moved organ/bin/hammond_standalone"
```

The installed [interface runbook](INTERFACE_RUNBOOK.md),
[preset/build runbook](PRESET_RUNBOOK.md), [application guide](STANDALONE_APP.md),
[MIDI mapping/setup guide](MIDI_UI_RUNBOOK.md),
[expression calibration guide](MIDI_EXPRESSION_GUIDE.md) and
[model scope](STANDALONE_MODEL.md), plus the adjacent
`THIRD_PARTY_NOTICES.md`, remain readable without a source checkout. Relative
links between these guides resolve to those exact adjacent filenames.
Repository URLs in the guides lead to source contracts, code, captures and
retained evidence; those references require network access and are not extra
installed files. Provenance paths inside manifests are also source references.
The exact payload below is the complete inventory. The application does not
require network access to start or play.

Read `standalone-capabilities.json` beside this guide to identify this build.
`midi.enabled=false`, `midi.backend="unavailable"` and `midi.rtmidi=null` mean that
no physical MIDI transport was compiled. Keyboard/pointer operation and explicit
synthetic replay remain available. An enabled build names exactly `ALSA`, `WinMM`
or `CoreMIDI` and retains its dependency and prepared-correction identities.
That record does not claim that a MIDI service, accessible input port or physical
controller is present. No port is opened automatically at ordinary startup.
Use the installed runbook for explicit `--list-midi`, exact-name selection and
expected unavailable-service/device outcomes.

### Calibrate expression in the installed application

Choose writable session paths outside the installed prefix so relocation keeps
the application payload separate from saved controls and diagnostics. The
following uses an already installed MIDI-enabled build; substitute its new
absolute prefix after a move. The port name and endpoint values are examples,
not measured values for a physical controller:

```sh
hammond_prefix="/absolute/path/moved organ"
hammond_session="/absolute/path/organ session"
mkdir -p "$hammond_session"
"$hammond_prefix/bin/hammond_standalone" --list-midi
"$hammond_prefix/bin/hammond_standalone" \
  --midi-port "EXACT NAME FROM --list-midi" \
  --midi-upper-channel 1 --midi-lower-channel 2 --midi-pedal-channel 3 \
  --expression-min 20 --expression-max 100 --expression-invert \
  --state "$hammond_session/my-controls.b3controls" \
  --diagnostics "$hammond_session/physical-session.json"
```

The pair must satisfy `0 <= minimum < maximum <= 127`. Open **MIDI / Ctrl+M**
to edit **EXPRESSION MIN**, **EXPRESSION MAX** and **EXPRESSION DIRECTION**, then
Apply explicitly. Read the displayed selected, configured, active and pending
states: a valid configuration or a pending reconnect does not prove that input
is active. A changed calibration releases the previous MIDI owners before a
fresh epoch opens; play fresh notes after reconnecting. Apply itself does not
change musical expression. The next admitted CC11 uses the new mapping.

**Save/Load retains musical expression, but not calibration, port or channels.**
Those adapter settings last only for the running process. Repeat the same CLI
arguments at the next launch, or configure them in MIDI again. The adjacent
[expression guide](MIDI_EXPRESSION_GUIDE.md) explains direction, the eleven
dialog focus stops, CC120/121/123, failed-open recovery and the full diagnostics.

On Windows use the installed `.exe` with PowerShell's call operator, for example:

```powershell
$hammondPrefix = "C:\path\moved organ"
$hammondSession = "C:\path\organ session"
New-Item -ItemType Directory -Force $hammondSession | Out-Null
& (Join-Path $hammondPrefix "bin/hammond_standalone.exe") --list-midi
& (Join-Path $hammondPrefix "bin/hammond_standalone.exe") `
  --midi-port "EXACT NAME FROM --list-midi" `
  --midi-upper-channel 1 --midi-lower-channel 2 --midi-pedal-channel 3 `
  --expression-min 20 --expression-max 100 --expression-invert `
  --state (Join-Path $hammondSession "my-controls.b3controls") `
  --diagnostics (Join-Path $hammondSession "physical-session.json")
```

### Check the moved instrument without physical MIDI

This bounded reproduction also works with MIDI disabled. In a fresh writable
session directory, save the following as `expression.b3midi`; keep
`unused.b3controls` absent:

```text
B3MIDIREPLAY1
duration_ms 800
0 connect
100 bytes 90 3C 64
200 bytes B0 0B 28
500 bytes 80 3C 00
```

Using the absolute variables above, run from any working directory:

```sh
SDL_AUDIODRIVER=dummy SDL_VIDEODRIVER=dummy \
  "$hammond_prefix/bin/hammond_standalone" \
  --state "$hammond_session/unused.b3controls" \
  --midi-script "$hammond_session/expression.b3midi" \
  --expression-min 20 --expression-max 100 --expression-invert \
  --diagnostics "$hammond_session/inverted.json"
```

Exit **0** and `midi_replay.passed=true` indicate completion. Raw hexadecimal
`28` is CC11 value 40, so `midi_replay.before_shutdown.controls.expression` is
**0.75**. Both `midi.expression_calibration.configured` and
`.pre_shutdown_active` retain minimum 20, maximum 100 and inverted `true`;
`.active` is `null` after shutdown. `midi.generation` and
`midi.device.callback_messages` remain zero because no native MIDI transport
opens. No controls file is saved implicitly, and reports belong outside the
installed payload. The [expression guide](MIDI_EXPRESSION_GUIDE.md#bounded-reproduction-without-physical-midi)
gives the full expected diagnostics, Normal and CC121 variants, and the
PowerShell dummy-driver setup. This is a local synthetic check, not a physical
controller, audio-device or latency qualification.

## Build, stage and move

These developer commands run from a source checkout with CMake 3.21+, Python
3.10+ and a C++20 compiler. Acquire SDL2 explicitly using the
[locked SDL2 setup](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/STANDALONE_DEPENDENCY.md).
The default native build leaves physical MIDI disabled:

```sh
cmake -S . -B build-native -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=/absolute/path/to/SDL2 \
  -DHAMMOND_ENABLE_MIDI=OFF
cmake --build build-native --config Release --target hammond_standalone --parallel 3
cmake --install build-native --config Release --component Standalone \
  --prefix "/absolute/path/staged organ"
mv "/absolute/path/staged organ" "/absolute/path/moved organ"
"/absolute/path/moved organ/bin/hammond_standalone" --help
```

For physical MIDI, explicitly acquire the pinned source using the
[RtMidi preparation guide](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/RTMIDI_BUILD.md),
install the platform's required native development inputs, and configure a
separate enabled build:

```sh
python3 tools/acquire_rtmidi.py --destination ../rtmidi-6.0.0
cmake -S . -B build-native-midi -DCMAKE_BUILD_TYPE=Release \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=/absolute/path/to/SDL2 \
  -DHAMMOND_ENABLE_MIDI=ON -DHAMMOND_RTMIDI_ROOT=/absolute/path/to/rtmidi-6.0.0
cmake --build build-native-midi --config Release --target hammond_standalone --parallel 3
cmake --install build-native-midi --config Release --component Standalone \
  --prefix "/absolute/path/staged MIDI organ"
```

Configuration verifies the existing dependency and prepares the identified
correction; it does not fetch an SDK or select a fallback API. Installation
consumes already configured metadata and never loads a MIDI SDK, enumerates
ports, probes a device or acquires a dependency. MIDI-disabled builds need no
RtMidi checkout or native MIDI development package.

Use the actual selected configuration with a multi-configuration generator.
An unknown configuration name is rejected before any destination write,
including metadata copies. Names are matched without case sensitivity against
the configured names, including declared custom configurations. A declared
configuration requires its own built executable; another configuration's binary
cannot satisfy preflight. A single-configuration generator retains its
configured executable selection regardless of the install `--config` label.

Prefixes may contain spaces and Unicode. `CMAKE_INSTALL_BINDIR` and
`CMAKE_INSTALL_DATADIR` may be nonempty relative paths without parent traversal
or list separators; configure them before staging. Defaults are `bin` and
`share`. Existing destination ancestors must be ordinary directories. `DESTDIR`
staging is honored where CMake supports it. `CMAKE_INSTALL_MODE` must be unset,
empty or `COPY`; staging preserves executable bytes without stripping or changing
its RPATH.

## Exact payload

The common payload contains the executable plus sixteen metadata files.
In the table, `metadata/` means `share/hammond-b3-organ/standalone/`; replace
`bin` and `share` with the configured relative directories.

| Installed path | Exact source or identity |
| --- | --- |
| `bin/hammond_standalone[.exe]` | Selected built target, copied without modification |
| `metadata/STANDALONE_INSTALL.md` | `docs/STANDALONE_INSTALL.md` |
| `metadata/STANDALONE_APP.md` | `docs/STANDALONE_APP.md` |
| `metadata/STANDALONE_MODEL.md` | `docs/STANDALONE_MODEL.md` |
| `metadata/MIDI_UI_RUNBOOK.md` | `docs/MIDI_UI_RUNBOOK.md` |
| `metadata/PRESET_RUNBOOK.md` | `docs/PRESET_RUNBOOK.md` |
| `metadata/INTERFACE_RUNBOOK.md` | `docs/INTERFACE_RUNBOOK.md` |
| `metadata/THIRD_PARTY_NOTICES.md` | Root notice file, including reference-art provenance and use-rights limits |
| `metadata/LICENSE-SDL2.txt` | Locked SDL2 `LICENSE.txt`, exact bytes |
| `metadata/LICENSE-DejaVu.txt` | `assets/standalone/fonts/LICENSE-DejaVu.txt`, exact bytes |
| `metadata/sdl2-lock.json` | `data/dependencies/sdl2-lock.json` |
| `metadata/font-source-manifest.json` | `assets/standalone/fonts/source-manifest.json` |
| `metadata/reference-source-manifest.json` | `assets/standalone/reference/manifest.json` |
| `metadata/atlas-reference.json` | `docs/design/atlas-reference.json` |
| `metadata/standalone-capabilities.json` | Configure-generated capability and dependency/asset identities; independent of build configuration name |
| `metadata/MIDI_EXPRESSION_GUIDE.md` | `docs/MIDI_EXPRESSION_GUIDE.md`; current calibration and channel-mode operator workflow |
| `metadata/reference-apron-manifest.json` | `assets/standalone/reference-apron-v1/manifest.json`; separate masked apron identity, pixels, authoring and rights limits |

MIDI-enabled installations add exactly four files:

| Installed path | Exact source or identity |
| --- | --- |
| `metadata/LICENSE-RtMidi.txt` | Verified prepared RtMidi `LICENSE`, identical to the locked upstream notice |
| `metadata/rtmidi-lock.json` | `data/dependencies/rtmidi-lock.json` |
| `metadata/rtmidi-prepared-source.json` | Prepared `prepared-source.json`, including full lock, prepared file hashes and preparation-tool hash |
| `metadata/rtmidi-coremidi-zero-init.patch` | Exact reviewed two-allocation correction from the prepared build copy |

SDL2 is the locked 2.32.10 static target; the glyph inputs are DejaVu 2.37.
An enabled RtMidi target is pinned to 6.0.0 and uses the recorded prepared
source, including the correction on every platform. The font and reference
manifests describe authoring inputs; their listed source paths are provenance,
not additional runtime files. No source font, source artwork, PDF, raw crop,
RtMidi source/header or dependency checkout is installed. Embedded-art
publication rights remain unresolved as stated in the retained notices.

Capability schema 1 retains `reference_art` for the historical three-crop package
and adds `reference_apron` for `standalone-reference-apron-v1`. Each separately
binds its installed manifest hash, the unchanged atlas provenance/source hash
and the common unresolved-rights notice. The additional record changes no
runtime asset loading or physical-evidence claim. Earlier 16/20-file installation
results retain their historical payload identities.

## Preflight and destination preservation

Before any destination write, installation checks and reads the selected
executable and every metadata input as a nonempty ordinary file. It rejects
missing/unreadable files, symlinks, directories and special files. All metadata
must still match its configured bytes; license and correction hashes must also
match their reviewed identity records. The generated capability record is
covered by the same checks. This prevents a partially populated payload when
any required notice, provenance record, guide or optional MIDI record is absent
or changed.

Metadata inputs are registered as CMake configure dependencies. After an
intentional guide/notice change, rebuild or explicitly reconfigure before
staging. Direct installation of stale configured inputs fails before copying;
it does not repair source inputs or silently admit changed records. Retain the
selected executable, configured metadata, SDL2 notice and, when enabled, the
prepared RtMidi notice/record/patch until installation completes.

An existing application binary or dedicated `standalone` metadata directory,
including an empty directory or dangling symlink, fails before copying. Choose
a fresh destination for a new installation. Unrelated prefix contents, including
`OfflineTools` and `CrossoverTools` files in the same `bin` and
`share/hammond-b3-organ`, can coexist.
Destination parents cannot be symlinks or ordinary files. These are read-only
preflight protections, not an atomic transaction against later disk/I/O failure
or concurrent filesystem mutation.

The components remain separate selections. `--component Standalone` adds
neither the 23-file `OfflineTools` payload nor the six-file `CrossoverTools`
payload; ordinary installation still excludes Standalone and CrossoverTools.
Select those components explicitly when their own inputs have been built, then
move the complete shared prefix. The
[offline install guide](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/OFFLINE_INSTALL.md)
is a repository document and is not in either component's installed inventory.
The [crossover install guide](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/CROSSOVER_INSTALL.md)
is installed only with CrossoverTools, at
`share/hammond-b3-organ/crossover/docs/CROSSOVER_INSTALL.md` under the default
layout. Its registry/reference subtree stays together; it does not supply a
profile or audio route to the standalone instrument.

## Maintained native acceptance

After building the selected application:

```sh
ctest --test-dir build-native -C Release --output-on-failure --no-tests=error \
  -R '^test_standalone_install$'
```

Run the same suite against a separately configured MIDI-enabled build to qualify
that actual executable and its optional payload. The suite stages the real
component, checks every expected file and exact source hash, validates capability
identities and installed guide links, moves the prefix, then runs relocated
`--help` and a 600 ms actual SDL dummy audio/video smoke from an unrelated
directory. Private state/diagnostics paths and image/profile checks exercise
embedded resources. Runtime MIDI diagnostics must agree with the configured
capability without selecting or opening a port; no physical MIDI device is
needed for this acceptance.

The custom-directory fixture additionally removes its private source, build
and dependency copies, then runs the installed 800 ms inverted-CC11 example
from a separate session directory. It requires expression 0.75, the configured
and pre-shutdown active calibration, an inactive final epoch and zero native
transport callbacks. Exact hashes before and after execution include sentinels
in OfflineTools and CrossoverTools paths. These are namespace-preservation
checks; the other components retain their own native install/execution gates.

Private copied-input fixtures retain missing selected-configuration rejection,
all-input preflight, explicit component opt-in, custom relative directories,
overwrite refusal and copy-mode checks. They also exercise the disabled MIDI
inventory without a dependency checkout, and fail on changed/invalid reference,
capability and enabled MIDI metadata. Against the actual configured build, an
unknown multi-config name must preserve fresh and pre-existing destinations,
sentinels and empty directories. A single-config build must copy the complete
selected payload. Fixtures do not rename or damage shared build products, and
prerequisite failures are not silently skipped.

CTest provides `HAMMOND_TEST_CMAKE`, `HAMMOND_TEST_BUILD_DIR`,
`HAMMOND_TEST_CONFIG`, `HAMMOND_STANDALONE_EXECUTABLE`, `HAMMOND_SDL2_ROOT`,
`HAMMOND_INSTALL_BINDIR`, `HAMMOND_INSTALL_DATADIR`, `HAMMOND_TEST_ENABLE_MIDI`
and `HAMMOND_STANDALONE_CAPABILITIES`. Enabled builds also provide
`HAMMOND_RTMIDI_PREPARED_ROOT` and `HAMMOND_RTMIDI_BACKEND` from the actual target
properties. The separate fixture payload tests identify install-rule behavior;
the relocated actual application establishes its own runtime capability match.

This gate establishes local copying, preservation and relocation with dummy
SDL drivers. Native desktop/audio hardware, physical MIDI input, platform
runtime/dependency inventories, project and artwork licensing, branding,
signing and release distribution remain separate gates. Source-specific results
are retained in the
[interface packaging evidence](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-14-interface-continuation/24-setup-package.md).
The earlier [MIDI packaging evidence](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/development/2026-11-14-midi-ui/26-midi-packaging.md)
and nine-file staging results remain dated history with their original payloads.
