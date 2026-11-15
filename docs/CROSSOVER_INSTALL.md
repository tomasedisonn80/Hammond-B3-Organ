# Install and move the independent crossover tools

`CrossoverTools` is an explicitly selected local CMake component for the
independent Leslie 122 electrical research model. It copies the native probe,
the Python analog reference and its fixed registry, two operating documents and
the existing notices. The installed tools run from an unrelated working
directory, and the complete prefix can be moved without a source checkout.
This component does not add files to the ordinary install, `OfflineTools` or
`Standalone` selections.

## Exact payload and evidence boundary

With the default relative install directories, the complete inventory is:

| Installed path, relative to the prefix | Exact input |
| --- | --- |
| `bin/hammond_crossover_probe` (`.exe` on Windows) | Selected configuration's built `hammond_crossover_probe` target |
| `share/hammond-b3-organ/crossover/tools/crossover_reference.py` | Unchanged `tools/crossover_reference.py` |
| `share/hammond-b3-organ/crossover/data/crossover/leslie-122-ideal-v1.json` | Unchanged fixed registry |
| `share/hammond-b3-organ/crossover/docs/CROSSOVER_INSTALL.md` | This guide |
| `share/hammond-b3-organ/crossover/docs/LESLIE_CROSSOVER_CONTRACT.md` | Frozen electrical and numerical contract |
| `share/hammond-b3-organ/crossover/THIRD_PARTY_NOTICES.md` | Unchanged repository notices |

There are **six files**. The native executable is copied without stripping or
RPATH editing. The script remains beneath `tools/` and the registry beneath
`data/crossover/` within the same package root. Its existing `DEFAULT_REGISTRY`
uses the script's resolved location, so no wrapper, embedded installation prefix,
environment variable, package installation or production-source change is needed.

The [registry](../data/crossover/leslie-122-ideal-v1.json) retains the model ID
`atlas-leslie-122-ideal-crossover-v1` and numerical realization
`physical-trapezoidal-leslie-crossover-v1`. The [contract](LESLIE_CROSSOVER_CONTRACT.md)
identifies the atlas's 1971 Leslie 122 divider **052803**, pages 271–276, with
L2 = 0.0032 H, L3 = 0.0052 H, C16A = 0.0000078 F and C16B = 0.0000125 F.
The default two 16-ohm loads are ideal constant resistors; the floating treble
load remains across A–H. The atlas SHA-256 is
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.

The [reference](../tools/crossover_reference.py) independently compares
series/parallel algebra with a nodal calculation. It checks the fixed registry
and reports its bytes and source hash. It does not read or verify the atlas's
PDF bytes. Manufacturer drawings have not been independently inspected for
this model. The later 113860 assembly remains documentary context, not an
admitted alternative profile.

Winding resistance, capacitor ESR and leakage, actual complex driver
impedances, amplifier source impedance, acoustic polarity, serial applicability
and measurement uncertainty remain explicit null physical fields. Numerical
zero-loss assumptions are not measurements of those unknowns. Neither tool
connects to Engine or establishes acoustic, audible same-Hz or specimen-specific
fidelity. The retained
[same-Hz characterization](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/docs/LESLIE_CROSSOVER_CHARACTERIZATION.md)
separates frequency-warped numerical agreement from ordinary same-Hz error.
The 500-page PDF, plots, acceptance reports and other large evidence are not
installed; they are not runtime inputs.

## Build and select the component

Configuration needs CMake 3.21 or newer, a C++20 toolchain and Python 3.10 or
newer. Running the copied reference needs only that Python version's standard
library. Running the native probe needs an OS/architecture and compiler runtime
compatible with the chosen build; this local component does not collect runtime
DLLs, Python, CMake, SDL, MIDI or plugin SDKs.

From the source checkout, choose a build directory and a **fresh local prefix**:

```sh
cmake -S . -B build-crossover -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build-crossover --config Release --target hammond_crossover_probe
hammond_prefix="$PWD/crossover-prefix"
cmake --install build-crossover --config Release \
  --component CrossoverTools --prefix "$hammond_prefix"
```

Installation does not build a missing target. Keep all five source payload
files available until installation completes. For a multi-configuration
generator, build and install the same configured name with `--config`; an
unknown configuration is rejected before any payload is copied. Configuration
selection is case-insensitive, as in CMake's generated install rules.

`CMAKE_INSTALL_MODE` must be unset, empty or exactly `COPY`. Link modes,
including modes that can fall back to copying, are rejected. Clear a caller's
`DESTDIR` for ordinary local use; on POSIX an intentional `DESTDIR` stages the
same relative payload under that root. No system-wide installation, plugin
registration, signing or installer generation is part of this workflow.

## Run from an unrelated working directory

The examples below use the absolute `hammond_prefix` assigned above and a
separate writable report directory. No `--registry` is needed for the installed
default. Python `-B` keeps bytecode caches out of the package.

```sh
hammond_reports="$PWD/crossover-reports"
cmake -E make_directory "$hammond_reports"
cd "$hammond_reports"
python3 -B "$hammond_prefix/share/hammond-b3-organ/crossover/tools/crossover_reference.py" \
  --output "$hammond_reports/analog-reference.json"
"$hammond_prefix/bin/hammond_crossover_probe" \
  --operation response --sample-rate 48000 --frequencies 0,400,800,1600,20000
"$hammond_prefix/bin/hammond_crossover_probe" \
  --operation sine --sample-rate 48000 --frequency 800 \
  --amplitude 0.25 --warmup-frames 65536 --measurement-frames 8192
```

Successful commands return 0. The reference emits a full JSON report to stdout
when `--output` is omitted or `-`; with a file output, the report is written there
and stdout is empty. A failed analog comparison returns 1. Invalid input or an
I/O error returns 2 with a diagnostic. The probe emits JSON to stdout only after
its computation succeeds and uses exit 2 for rejected arguments or processing.
Save its captured stdout only after checking the exit status; ordinary shell
redirection can create or truncate a file even when a command rejects its input.

The native `response` observes the actual discrete recurrence at the requested
digital frequencies. The analog script evaluates the continuous ideal network.
Their same-Hz values are not expected to be identical. The `sine` report fits
actual processed samples but does not itself certify a transient bound or an
audibility threshold. The frozen contract defines the independent numerical
comparison and its distinct frequency mapping.

Use fresh report names outside the installed package to preserve previous
evidence. The reference atomically replaces an existing ordinary output file
after computation succeeds; its parent directory must already exist. It refuses
an output resolving to its own script or the selected registry. This protection
does not make every other installed file an immutable output destination.
Invalid registry/load input leaves an existing output unchanged. An explicit
`--registry` must still satisfy the exact fixed-model contract; it does not
admit arbitrary circuit edits. Alternative `--treble-ohms` and `--bass-ohms`
values in 1–1024 are identified as resistor experiments, not driver data.

## Move the complete prefix

Stop any running tools, move the complete prefix and use its new absolute paths.
Keep the source-like script/registry subtree together. With the variables above:

```sh
hammond_moved="${hammond_prefix}-moved"
cmake -E rename "$hammond_prefix" "$hammond_moved"
hammond_prefix="$hammond_moved"
python3 -B "$hammond_prefix/share/hammond-b3-organ/crossover/tools/crossover_reference.py" \
  --output "$hammond_reports/analog-reference-after-move.json"
"$hammond_prefix/bin/hammond_crossover_probe" \
  --operation response --sample-rate 48000 --frequencies 0,800,20000
```

No build or original prefix is required during these executions. Moving a
prefix is not cross-platform binary conversion or a clean-machine runtime test.
Keep reports separately; their model/source hashes remain meaningful after a
move without embedding the prefix into the registry.

Custom directories are configured before installation, for example
`-DCMAKE_INSTALL_BINDIR="executables/native tools"` and
`-DCMAKE_INSTALL_DATADIR="resources/reference data"`. Substitute those paths for
`bin` and `share` in every command. Both must be nonempty relative directories;
absolute/drive-prefixed paths, parent traversal and semicolon list separators
are rejected using the shared install-directory validator. The `tools/` and
`data/crossover/` layout within the package is unchanged.

On Windows, use the selected interpreter and native `.exe` explicitly. For an
already built/configured `build-crossover`, PowerShell can use:

```powershell
$hammondPrefix = Join-Path $PWD "crossover prefix"
cmake --install build-crossover --config Release --component CrossoverTools --prefix $hammondPrefix
$hammondReports = Join-Path $PWD "crossover reports"
New-Item -ItemType Directory -Path $hammondReports
Set-Location $hammondReports
python -B (Join-Path $hammondPrefix "share/hammond-b3-organ/crossover/tools/crossover_reference.py") --output "analog-reference.json"
& (Join-Path $hammondPrefix "bin/hammond_crossover_probe.exe") --operation response --sample-rate 48000 --frequencies "0,800,20000"
```

Use `Move-Item` to move the whole prefix to a fresh destination, then set
`$hammondPrefix` to the new absolute path and rerun those commands.

## Failure boundary and acceptance

The installer checks every required input for presence, nonzero size and an
ordinary nonsymlink file before touching destinations. It rejects an existing
probe destination or crossover package leaf, including dangling links, and
rejects known linked/file ancestors within the requested prefix. It preserves
unrelated files in an otherwise usable prefix. Installation is not an atomic
six-file transaction: a later filesystem failure can leave a partial new
installation, which is retained for inspection without automatic recursive
cleanup. These checks assume quiescent inputs and destinations; they are not a
hostile-filesystem sandbox or a rollback protocol.

The focused acceptance uses the selected built probe read-only, private minimal
CMake projects with the real installer modules, and bounded temporary prefixes.
It checks exact inventory/bytes, default registry resolution, move-and-run after
removing private source/build inputs, custom directories, component isolation,
configuration selection, preflight failures and installed output safety. It
never changes the shared build's install manifest or fault-injects into a user's
source or installation. Run it after building the probe:

```sh
ctest --test-dir build-crossover -C Release --output-on-failure \
  --no-tests=error -R '^python_test_crossover_install$'
```

Symlink and POSIX `DESTDIR` cases report a skip on systems that do not support
them; the multi-configuration fixture requires an available multi-config
generator. A test result qualifies the named host, source and native binary.
It does not establish all-platform distribution or physical model acceptance.

The inspected repository has no selected project-wide `LICENSE` file. The
copied [third-party notices](../THIRD_PARTY_NOTICES.md) identify their own scope;
they do not grant a project-wide license or clear research-source redistribution.
Those release decisions remain separate from this local install component.
