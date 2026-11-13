# Local installation of the offline renderer

The `OfflineTools` CMake component installs the existing command-line WAV
renderer and its nominal, unmeasured data into a prefix you choose. It supports
offline file rendering only. Audio-device applications, plugins, signed installers,
runtime-library bundling and redistributable-product qualification remain separate
work; see the [render contract](RENDER_FORMAT.md) and [project plan](PLAN.md).

## Build, install and relocate

The [build prerequisites](BUILD.md) apply: CMake 3.21+, a C++20 compiler and
Python 3.10+ for profile generation. Installation performs no downloads and does
not build missing inputs. Build the renderer for the selected configuration first;
it also generates `nominal.b3p`. A missing executable or profile makes installation
fail with a build-first diagnostic before any component files are copied.

Linux/macOS, from the repository root:

```sh
cmake -S . -B build-offline -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build-offline --config Release --target hammond_render --parallel 2
ctest --test-dir build-offline -C Release -R '^python_test_install$' --output-on-failure
cmake --install build-offline --config Release --component OfflineTools \
  --prefix "$HOME/hammond local"
```

Use a new local prefix, without elevated privileges. `--prefix` overrides the
configured install prefix. CMake's normal install behavior may replace files
already present there; use separate prefixes to retain older installations.

With a Visual Studio generator, run in its developer terminal. The configuration
must match both build and install; CMake selects the executable in `Release/`:

```powershell
cmake -S . -B build-offline -DBUILD_TESTING=ON
cmake --build build-offline --config Release --target hammond_render --parallel 2
ctest --test-dir build-offline -C Release -R '^python_test_install$' --output-on-failure
cmake --install build-offline --config Release --component OfflineTools `
  --prefix "$env:USERPROFILE\hammond local"
```

For single-configuration Ninja on Windows, also configure
`-DCMAKE_BUILD_TYPE=Release`. Neither installation nor rendering needs Python at
runtime. The compiled executable still needs a compatible operating system and
the compiler's runtime libraries; this component does not package those libraries.

## Installed files

The default `GNUInstallDirs` layout contains exactly these eight files:

| Path below the chosen prefix | Contents |
|---|---|
| `bin/hammond_render` (`hammond_render.exe` on Windows) | Offline renderer |
| `share/hammond-b3-organ/nominal.b3p` | Generated nominal compiled profile |
| `share/hammond-b3-organ/fixtures/catalog-v1.json` | Existing fixture identities, settings and expectations |
| `share/hammond-b3-organ/fixtures/a4-fundamental-v1.events` | One-second nominal A4 gesture with surrounding silence |
| `share/hammond-b3-organ/fixtures/two-manual-changes-v1.events` | Both manuals and registration changes |
| `share/hammond-b3-organ/fixtures/low-fold-coherent-v1.events` | Low foldback/coherent source sharing |
| `share/hammond-b3-organ/fixtures/held-bank-cancel-v1.events` | Retained banks and routing-only Cancel |
| `share/hammond-b3-organ/fixtures/high-fold-coherent-v1.events` | High foldback/coherent source sharing |

You may configure relative `CMAKE_INSTALL_BINDIR` and `CMAKE_INSTALL_DATADIR`
values; adjust the paths below accordingly. Absolute directories and parent
traversal are rejected to keep component destinations inside the chosen prefix.
No core archive, headers, benchmark, Python tools, research PDF, external assets
or third-party dependencies are installed.

The catalog is copied unchanged. Its event paths remain relative to the catalog.
Its authoring JSON path records repository provenance; that JSON is not a runtime
dependency and is not installed. Pass the installed compiled profile explicitly.
The renderer does not discover profiles from its executable directory, current
directory, environment or a source/build location.

## Render from the moved prefix

Move the whole prefix to another local directory on a compatible machine/runtime,
then point `--profile` and `--events` at their new locations. For example, after
moving it to `$HOME/hammond moved`, this works from any working directory:

```sh
prefix="$HOME/hammond moved"
mkdir -p "$HOME/hammond output"
"$prefix/bin/hammond_render" \
  --profile "$prefix/share/hammond-b3-organ/nominal.b3p" \
  --events "$prefix/share/hammond-b3-organ/fixtures/a4-fundamental-v1.events" \
  --output "$HOME/hammond output/a4.wav" \
  --sample-rate 48000 --frames 72000 --block-size 127 --seed 2602 \
  --drawbars 008000000 --fail-on-clip
```

The corresponding PowerShell invocation, after moving to `hammond moved`:

```powershell
$prefix = Join-Path $env:USERPROFILE 'hammond moved'
$output = Join-Path $env:USERPROFILE 'hammond output'
New-Item -ItemType Directory -Force $output | Out-Null
& "$prefix\bin\hammond_render.exe" `
  --profile "$prefix\share\hammond-b3-organ\nominal.b3p" `
  --events "$prefix\share\hammond-b3-organ\fixtures\a4-fundamental-v1.events" `
  --output "$output\a4.wav" `
  --sample-rate 48000 --frames 72000 --block-size 127 --seed 2602 `
  --drawbars 008000000 --fail-on-clip
```

Choose a new output filename on later runs. WAV publication preserves existing
outputs and requires a filesystem supporting hard links. The JSON summary reports
the profile identity, peak, RMS and clipping; the WAV contains identical dry stereo
PCM16 channels. These remain synthetic nominal-engine results.

## Relocation acceptance

`python_test_install` uses the actual `cmake --install --component OfflineTools`
command with a temporary prefix containing spaces. It checks the exact payload,
renames the prefix, and invokes the installed executable from an unrelated working
directory with installed profile/events paths. Actual PCM, full WAV bytes and JSON
identity/metrics must match the build renderer using identical catalog settings.

The test clears `HAMMOND_*` variables for renderer subprocesses. It temporarily
changes the installed test profile's declared digest and output gain, requires the
new identity and silent PCM, then verifies that removing the installed profile
fails without an output file. It restores the profile afterward. This synthetic
probe checks explicit data use; it is not a provenance or measurement claim. Source
and build trees are not renamed or modified by the test.

CTest supplies the precise CMake path, build directory, configuration, executable,
profile and install directories, including generator expressions for multi-config
builds. Missing build inputs fail rather than skip. All installs during this test
stay in temporary local directories; no system install is attempted. Local executed
platforms and outstanding qualification are recorded in the
[agent evidence note](development/agent-notes/44-offline-install.md).
