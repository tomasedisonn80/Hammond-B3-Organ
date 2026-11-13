# Local installation of the offline tools

The `OfflineTools` CMake component installs the WAV renderer, console and pedal
diagnostics, console trace plotter and nominal data into a prefix you choose.
It contains 22 files and supports offline file workflows. The separate
[NativeVST3 component](VST3_LOCAL_INSTALL.md) stages the actual optional plugin
bundle in a local prefix. Audio-device applications, signed installers,
runtime-library bundling and binary redistribution qualification remain separate
work; see the [project plan](PLAN.md).

## Build, install and relocate

The [build prerequisites](BUILD.md) apply: CMake 3.21+, a C++20 compiler and
Python 3.10+. Installation performs no downloads and does not build missing
inputs. Build all five native tools for the selected configuration first. The
renderer and trace targets also generate `nominal.b3p`. Before copying component
files, installation checks that all five executables, the profile, plot script,
three catalogs and twelve scores exist as files. A missing input fails before
any component destination is changed, with a build-first or missing-file diagnostic.

Linux/macOS, from the repository root:

```sh
cmake -S . -B build-offline -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build-offline --config Release --parallel 2 \
  --target hammond_render hammond_model_info hammond_parameter_info \
  hammond_console_trace hammond_pedal_trace
ctest --test-dir build-offline -C Release -R '^python_test_install$' --output-on-failure
cmake --install build-offline --config Release --component OfflineTools \
  --prefix "$HOME/hammond local"
```

Use a new local prefix, without elevated privileges. `--prefix` overrides the
configured install prefix. CMake's normal install behavior can replace files
already present there; use separate prefixes to retain older installations.

With a Visual Studio generator, run in its developer terminal. The configuration
must match both build and install; CMake selects executables in `Release/`:

```powershell
cmake -S . -B build-offline -DBUILD_TESTING=ON
cmake --build build-offline --config Release --parallel 2 `
  --target hammond_render hammond_model_info hammond_parameter_info `
  hammond_console_trace hammond_pedal_trace
ctest --test-dir build-offline -C Release -R '^python_test_install$' --output-on-failure
cmake --install build-offline --config Release --component OfflineTools `
  --prefix "$env:USERPROFILE\hammond local"
```

For single-configuration Ninja on Windows, also configure
`-DCMAKE_BUILD_TYPE=Release`. The five native tools do not need Python at runtime.
The installed plot script requires a Python 3.10+ interpreter and only its standard
library. Invoke it explicitly with that interpreter on every platform. Native
executables still need a compatible operating system and compiler runtime; this
component does not bundle those runtime libraries.

## Installed files

The default `GNUInstallDirs` layout contains exactly these **22 files**. Native
executable names have the `.exe` suffix on Windows.

| Path below the chosen prefix | Contents |
| --- | --- |
| `bin/hammond_render` | Offline stereo PCM16 WAV renderer |
| `bin/hammond_model_info` | Actual compiled console and pedal factory metadata |
| `bin/hammond_parameter_info` | All 45 compiled internal parameter mappings |
| `bin/hammond_console_trace` | Sample-by-sample nominal console CSV diagnostics |
| `bin/hammond_pedal_trace` | Nominal pedal unmute, overlap and routing CSV diagnostics |
| `bin/plot_console_trace.py` | Standalone bounded CSV-to-SVG plotter |
| `share/hammond-b3-organ/nominal.b3p` | Generated nominal compiled source profile |
| `share/hammond-b3-organ/fixtures/catalog-v1.json` | Original fixture identities, settings and expectations |
| `share/hammond-b3-organ/fixtures/a4-fundamental-v1.events` | Nominal A4 gesture with surrounding silence |
| `share/hammond-b3-organ/fixtures/two-manual-changes-v1.events` | Both manuals and registration changes |
| `share/hammond-b3-organ/fixtures/low-fold-coherent-v1.events` | Low foldback and coherent source sharing |
| `share/hammond-b3-organ/fixtures/held-bank-cancel-v1.events` | Retained banks and routing-only Cancel |
| `share/hammond-b3-organ/fixtures/high-fold-coherent-v1.events` | High foldback and coherent source sharing |
| `share/hammond-b3-organ/fixtures/console/console-catalog-v1.json` | Nominal console scenario identities and model controls |
| `share/hammond-b3-organ/fixtures/console/console-travel-v1.events` | Independent contact travel on both manuals |
| `share/hammond-b3-organ/fixtures/console/console-percussion-legato-v1.events` | Shared readiness, legato and finite recovery |
| `share/hammond-b3-organ/fixtures/console/console-routing-mask-v1.events` | Upper-B eligibility, masking and route transitions |
| `share/hammond-b3-organ/fixtures/pedals/pedal-catalog-v1.json` | Pedal fixture identities, map hashes, controls and expectations |
| `share/hammond-b3-organ/fixtures/pedals/pedal-mixtures-v1.events` | Two nominal pedal mixtures and control changes |
| `share/hammond-b3-organ/fixtures/pedals/pedal-shared-source-v1.events` | Manual/pedal sharing of free-running sources |
| `share/hammond-b3-organ/fixtures/pedals/pedal-held-routing-v1.events` | Held pedal notes, registration and routing changes |
| `share/hammond-b3-organ/fixtures/pedals/pedal-phrase-v1.events` | Original three-second two-manual/pedal gesture |

Relative `CMAKE_INSTALL_BINDIR` and `CMAKE_INSTALL_DATADIR` values can customize
this layout. Adjust example paths accordingly. Absolute directories and parent
traversal, empty values and CMake list separators are rejected to keep destinations
inside the chosen prefix. Leave `CMAKE_INSTALL_MODE` unset or set it to `COPY`;
symlink install modes are rejected because they defeat relocation. No core
archive, headers, benchmark, other Python tools, research PDF, external assets or
third-party dependencies are installed.

All three catalogs and all twelve event files are copied unchanged. The preceding
16-file payload retains its names and data bytes; the pedal executable and five
pedal data files are additions. Event paths remain
relative to their own catalog. Authoring JSON paths record repository provenance;
that JSON is not a runtime dependency and is not installed. Pass the installed
compiled profile explicitly to rendering and tracing. Those tools do not discover
profiles through their executable directory, working directory, environment or
source/build location. Metadata exporters report compiled factories and control
mappings without loading any source profile or JSON file.

## Render from a moved prefix

Move the whole prefix to another local directory on a compatible machine/runtime,
then point `--profile` and `--events` at their new locations. After moving it to
`$HOME/hammond moved`, this works from an unrelated working directory:

```sh
hammond_prefix="$HOME/hammond moved"
hammond_output="$HOME/hammond output"
mkdir -p "$hammond_output"
"$hammond_prefix/bin/hammond_render" \
  --profile "$hammond_prefix/share/hammond-b3-organ/nominal.b3p" \
  --events "$hammond_prefix/share/hammond-b3-organ/fixtures/a4-fundamental-v1.events" \
  --output "$hammond_output/a4.wav" \
  --sample-rate 48000 --frames 72000 --block-size 127 --seed 2602 \
  --drawbars 008000000 --fail-on-clip
```

For the nominal contact/percussion fixture, use its catalog's explicit settings:

```sh
"$hammond_prefix/bin/hammond_render" \
  --profile "$hammond_prefix/share/hammond-b3-organ/nominal.b3p" \
  --events "$hammond_prefix/share/hammond-b3-organ/fixtures/console/console-percussion-legato-v1.events" \
  --output "$hammond_output/console-legato.wav" \
  --sample-rate 48000 --frames 42000 --block-size 127 --seed 2624 \
  --drawbars 000000000 --contacts nominal --percussion second \
  --percussion-volume normal --percussion-decay fast --fail-on-clip
```

The equivalent PowerShell form for the original A4 example is:

```powershell
$hammondPrefix = Join-Path $env:USERPROFILE 'hammond moved'
$hammondOutput = Join-Path $env:USERPROFILE 'hammond output'
New-Item -ItemType Directory -Force $hammondOutput | Out-Null
& "$hammondPrefix\bin\hammond_render.exe" `
  --profile "$hammondPrefix\share\hammond-b3-organ\nominal.b3p" `
  --events "$hammondPrefix\share\hammond-b3-organ\fixtures\a4-fundamental-v1.events" `
  --output "$hammondOutput\a4.wav" `
  --sample-rate 48000 --frames 72000 --block-size 127 --seed 2602 `
  --drawbars 008000000 --fail-on-clip
```

Use a new output filename for later runs. WAV publication preserves existing files
and requires a filesystem supporting hard links. The JSON summary reports actual
float metrics; the WAV has identical dry stereo PCM16 channels. These outputs
remain synthetic nominal-model evidence.

## Inspect and plot the nominal console

Metadata JSON is written to stdout; the shell manages a redirected destination.
The model exporter describes compiled factories, not the parameters or histories
of an arbitrary running Engine. The parameter exporter reports the 45 compiled
internal mappings, including the two pedal controls. Its output alone does not
qualify native host exports; those have a separate
[actual VST3 ABI gate](VST3_ABI_ACCEPTANCE.md).

```sh
"$hammond_prefix/bin/hammond_model_info" > "$hammond_output/console-models.json"
"$hammond_prefix/bin/hammond_parameter_info" --normalized 0.5 \
  > "$hammond_output/parameters.json"
"$hammond_prefix/bin/hammond_console_trace" \
  --profile "$hammond_prefix/share/hammond-b3-organ/nominal.b3p" \
  --scenario partial --sample-rate 48000 --seed 0 \
  --output "$hammond_output/partial.csv"
python3 "$hammond_prefix/bin/plot_console_trace.py" \
  --input "$hammond_output/partial.csv" --output "$hammond_output/partial.svg"
```

In PowerShell, use `hammond_console_trace.exe` and your Python 3.10+ interpreter:

```powershell
& "$hammondPrefix\bin\hammond_console_trace.exe" `
  --profile "$hammondPrefix\share\hammond-b3-organ\nominal.b3p" `
  --scenario partial --sample-rate 48000 --seed 0 --output "$hammondOutput\partial.csv"
python "$hammondPrefix\bin\plot_console_trace.py" `
  --input "$hammondOutput\partial.csv" --output "$hammondOutput\partial.svg"
```

The [trace contract](CONSOLE_TRACE.md) fixes the three 120 ms scenarios and their
same-frame timing. The plotter consumes the retained CSV and requires no source
checkout or native executable. CSV/SVG publication preserves existing outputs;
parents must already exist. The SVG retains the CSV hash and labels the nominal
model. [Plot documentation](CONSOLE_TRACE_PLOTS.md) explains validation and drawing
reductions. A valid trace or plot does not authenticate physical measurements.

## Render and inspect the nominal pedals

This bounded example uses the installed pedal catalog's first score and its
explicit settings. The score itself sets expression; no source authoring JSON or
external recording is needed:

```sh
"$hammond_prefix/bin/hammond_render" \
  --profile "$hammond_prefix/share/hammond-b3-organ/nominal.b3p" \
  --events "$hammond_prefix/share/hammond-b3-organ/fixtures/pedals/pedal-mixtures-v1.events" \
  --output "$hammond_output/pedal-mixtures.wav" \
  --sample-rate 48000 --frames 48000 --block-size 127 --seed 2701 \
  --drawbars 000000000 --pedal-drawbars 40 --contacts ideal --percussion off \
  --percussion-volume normal --percussion-decay slow --fail-on-clip
"$hammond_prefix/bin/hammond_pedal_trace" \
  --profile "$hammond_prefix/share/hammond-b3-organ/nominal.b3p" \
  --scenario overlap --sample-rate 48000 --seed 2705 \
  --output "$hammond_output/pedal-overlap.csv"
```

`hammond_pedal_trace` accepts `unmute`, `overlap` and `routing`. Each scenario is
120 ms; supported rates are 44100, 48000 and 96000 Hz. Its CSV records the model,
profile and routing-map identities along with pedal controls, contact state,
mixtures and audio. Existing output paths are rejected. The installed console
plotter accepts console CSV; this component does not yet include a pedal plotter.
See [PEDAL_TRACE.md](PEDAL_TRACE.md) and
[PEDAL_AUDIO_ACCEPTANCE.md](PEDAL_AUDIO_ACCEPTANCE.md) for the behavioral contracts and limits.

## Relocation acceptance and evidence scope

`python_test_install` runs actual `cmake --install --component OfflineTools` into a
temporary prefix containing spaces. It checks all 22 files and unchanged data/script
bytes, renames the prefix, then runs every installed tool from an unrelated working
directory with all `HAMMOND_*` variables removed. Missing inputs fail rather than
skip. The parent test still has source/build paths for the independent comparison;
installed tools receive only explicit moved-prefix inputs. The test does not move
or modify the source and build directories.

The original A4, nominal percussion and pedal-mixture fixtures must produce identical full WAV
bytes, PCM and metrics in build and installed executions. Both metadata exporters
must match their same-build originals. The pedal catalog's profile/map/model and
parameter identities must agree with the installed metadata, render summary and
all three pedal CSV scenarios. All catalog score hashes are checked. Actual
build/installed console and pedal traces must be byte-identical, and the installed
Python script must produce the same bounded console SVG
as the source script for that retained trace, including its trace hash. These
checks establish exercised relocation and same-build equivalence, not physical
model fidelity or cross-compiler binary/audio identity.

The test preserves the original installed-profile mutation probe: a changed
synthetic declared digest and zero output gain must affect identity and produce
silence. Removing the installed profile must then make rendering and both trace tools
fail without output. The original bytes are restored afterward. This checks explicit
input use; it is not an instrument calibration or provenance-authentication test.
The additional preflight test generates the same install module's rules in a
private minimal project. It exercises unbuilt tools and separately missing copies
of each tool, the profile, plot script, original catalog, console score, pedal
catalog and pedal score. These failures must preserve unrelated prefix contents
and an older installed executable. Absolute, parent-traversing and empty install
directories are rejected. No shared build input is renamed or removed by a test.

CTest supplies exact executable, CMake, build, profile and relative install paths,
including the selected configuration for multi-config generators. All test installs
are temporary local directories; no system installation is attempted. The expanded
component's actual local results and precise source snapshot are recorded in
[pedal assignment 38](development/2026-11-13-pedals/38-install-packages.md).
The integrator records its new combined publication and hosted qualification.

The earlier eight-file component passed hosted Linux, macOS, Windows Release and
Linux sanitizer relocation checks in
[run 43365901429 at 6c3dd8b](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43365901429).
The previous 16-file console extension is recorded in
[continuation assignment 44](development/2026-11-13-continuation/44-offline-packaging.md).
Neither historical result substitutes for qualification of this 22-file component.
The new local Linux result is a same-machine relocation check; it is not a Windows,
macOS, clean-OS, compiler-runtime bundling or signing result. Native staging has a
separate [relocated bundle acceptance test](VST3_LOCAL_INSTALL.md).
