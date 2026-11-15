# Install and move the offline contact reference

`ContactReferenceTools` is an explicit CMake install component containing the
standard-library Python fractional-contact reference, its independent oracle,
the fixed comparison study, and the complete synthetic v1 inputs. Running the
installed package requires Python 3.10 or newer. It needs no compiler, native
executable, audio/MIDI backend, third-party Python package, network access, or
source checkout. Git identity is optional metadata; unavailable Git is recorded
without replacing the explicit source and input hashes.

Every rule is `EXCLUDE_FROM_ALL`: select `--component ContactReferenceTools`
explicitly. An ordinary install and the existing `OfflineTools`, `Standalone`,
`CaptureTools`, `CrossoverTools`, `SourceLeakageTools`, and `NativeVST3`
components do not acquire this payload.

## Complete package layout

The package root is
`${CMAKE_INSTALL_DATADIR}/hammond-b3-organ/contact-reference` below the chosen
prefix (`share/hammond-b3-organ/contact-reference` by default). Its exact 48-file
inventory preserves the source-relative paths:

| Path within the package | Files |
| --- | --- |
| `tools/` | `fractional_contact_reference.py`, `contact_switching_io.py`, `contact_switching_reference.py`, `contact_switching_oracle.py`, `contact_switching_study.py`, `make_contact_switching_fixtures.py` |
| `docs/` | `FRACTIONAL_CONTACT_REFERENCE.md`, `CONTACT_SWITCHING_VALIDATION.md`, `CONTACT_SWITCHING_GUIDE.md`, `CONTACT_REFERENCE_INSTALL.md` |
| `data/contact-switching/reference-v1/` | Every `F00`–`F11` recipe at `44100`, `48000`, and `96000` Hz, named `F00-44100-v1.json` through `F11-96000-v1.json`: 36 files |
| `data/contact-switching/reference-v1/` | `manifest.json` and the independently frozen `probes.json` |

Keep this structure intact. The study finds its root from the parent of `tools`,
then reads the six implementation files and both frozen contracts there. Its
`--fixtures` argument selects the packaged fixture directory. Copying only the
command script, flattening the directories, or rewriting the contracts breaks
source identification or admission. The fixture generator is included for
provenance and reproduction; it produces fixtures and a manifest, not the
independent probe freeze. Use the installed frozen inputs for the v1 study.

The [operating guide](CONTACT_SWITCHING_GUIDE.md) explains output coordinates,
tails, exact edge identities, and interpretation. The
[model contract](FRACTIONAL_CONTACT_REFERENCE.md) and
[validation protocol](CONTACT_SWITCHING_VALIDATION.md) retain their frozen
status text; that text is not a current execution result. Repository-only links
inside these documents refer to source background outside the installed
inventory. The atlas, native binaries, reports, and session records are not
runtime inputs and are not copied.

## Configure and install: POSIX shell

Start in the source checkout. Use an existing configured build when available;
otherwise the following configuration requires CMake 3.21+, Python 3.10+, and
the repository's C++20 toolchain. Configuration detects that compiler, but this
component needs no native target to be built. No dependency download occurs.
Choose fresh sibling paths; run the commands in the same shell:

```sh
set -eu
hammond_source="$(pwd -P)"
hammond_parent="$(dirname "$hammond_source")"
hammond_build="$hammond_parent/build-contact-reference"
hammond_prefix="$hammond_parent/contact-reference-prefix"
hammond_moved="$hammond_parent/contact-reference-moved"
hammond_reports="$hammond_parent/contact-reference-reports"
test ! -e "$hammond_prefix" && test ! -L "$hammond_prefix"
test ! -e "$hammond_moved" && test ! -L "$hammond_moved"
unset DESTDIR CMAKE_INSTALL_MODE
cmake -S "$hammond_source" -B "$hammond_build" \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_ENABLE_MIDI=OFF -DCMAKE_INSTALL_DATADIR=share
cmake --install "$hammond_build" --config Release \
  --component ContactReferenceTools --prefix "$hammond_prefix"
```

When reusing a configured build, assign `hammond_build` to it and omit the
configuration command. Keep its chosen relative `CMAKE_INSTALL_DATADIR` and
adjust the package paths below if it differs from `share`. The Python payload
has no configuration-specific binary; `--config Release` simply makes the
example explicit. Platform and multi-configuration test results still require
their own observed evidence.

Move the complete prefix, then run from a separate report directory outside
the checkout. Python `-B` keeps bytecode caches out of the package:

```sh
mv "$hammond_prefix" "$hammond_moved"
hammond_package="$hammond_moved/share/hammond-b3-organ/contact-reference"
mkdir -p "$hammond_reports"
cd "$hammond_reports"
python3 -B "$hammond_package/tools/contact_switching_reference.py" \
  --input "$hammond_package/data/contact-switching/reference-v1/F02-48000-v1.json" \
  --factor 256 --output "$hammond_reports/F02-48000-L256.json"
```

To execute the complete fixed study, choose a new report filename and preserve
its exit status even when the numerical result is failed or incomplete:

```sh
hammond_status=0
python3 -B "$hammond_package/tools/contact_switching_study.py" \
  --fixtures "$hammond_package/data/contact-switching/reference-v1" \
  --output "$hammond_reports/study-v1.json" || hammond_status=$?
printf 'Study exit status: %s\n' "$hammond_status"
```

## Configure, move, and run: PowerShell

Start in the source checkout with Python 3.10+ available as `python` (or replace
it with `py -3`). The same configure-time prerequisites apply. These commands
use fresh sibling paths and stop on a failed configure, install, move, or render:

```powershell
$ErrorActionPreference = 'Stop'
$HammondSource = (Get-Location).Path
$HammondParent = Split-Path -Parent $HammondSource
$HammondBuild = Join-Path $HammondParent 'build-contact-reference'
$HammondPrefix = Join-Path $HammondParent 'contact-reference-prefix'
$HammondMoved = Join-Path $HammondParent 'contact-reference-moved'
$HammondReports = Join-Path $HammondParent 'contact-reference-reports'
foreach ($HammondPath in @($HammondPrefix, $HammondMoved)) {
    if ($null -ne (Get-Item -LiteralPath $HammondPath -Force -ErrorAction SilentlyContinue)) {
        throw "Choose a fresh path: $HammondPath"
    }
}
Remove-Item Env:DESTDIR -ErrorAction SilentlyContinue
Remove-Item Env:CMAKE_INSTALL_MODE -ErrorAction SilentlyContinue
cmake -S "$HammondSource" -B "$HammondBuild" `
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF `
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF `
  -DHAMMOND_ENABLE_MIDI=OFF -DCMAKE_INSTALL_DATADIR=share
if ($LASTEXITCODE -ne 0) { throw 'Contact reference configuration failed' }
cmake --install "$HammondBuild" --config Release `
  --component ContactReferenceTools --prefix "$HammondPrefix"
if ($LASTEXITCODE -ne 0) { throw 'Contact reference installation failed' }
Move-Item -LiteralPath $HammondPrefix -Destination $HammondMoved
$HammondPackage = Join-Path $HammondMoved 'share/hammond-b3-organ/contact-reference'
New-Item -ItemType Directory -Path $HammondReports -Force | Out-Null
Set-Location -LiteralPath $HammondReports
python -B "$HammondPackage/tools/contact_switching_reference.py" `
  --input "$HammondPackage/data/contact-switching/reference-v1/F02-48000-v1.json" `
  --factor 256 --output "$HammondReports/F02-48000-L256.json"
if ($LASTEXITCODE -ne 0) { throw 'Contact reference render failed' }
python -B "$HammondPackage/tools/contact_switching_study.py" `
  --fixtures "$HammondPackage/data/contact-switching/reference-v1" `
  --output "$HammondReports/study-v1.json"
$HammondStudyStatus = $LASTEXITCODE
Write-Output "Study exit status: $HammondStudyStatus"
```

For an existing configured build, change `$HammondBuild` and omit its configure
command. Neither the source checkout, original prefix, CMake, nor native build
outputs are required by either relocated Python invocation. Record an external
process wall time when qualifying the full study, alongside its internal timing.

## Admission, output, and failure boundaries

`CMAKE_INSTALL_DATADIR` must be nonempty and relative, without `..` components,
drive prefixes, absolute paths, or semicolon list separators. Installation
requires `CMAKE_INSTALL_MODE` unset, empty, or exactly `COPY`; symlink modes and
copy-fallback link modes are rejected. POSIX `DESTDIR` staging uses the same
relative inventory and checks the effective staged prefix. Clear `DESTDIR` for
the ordinary local workflow above.

Before copying any component file, installation checks all 48 required inputs
for existence, nonempty size, and nonsymlink file paths, including ordinary
source directories within the source root. It refuses any existing package
path, including an empty directory or dangling symlink, and rejects file or
symlink ancestors within the chosen prefix, including the prefix itself.
Unrelated ordinary directories in the prefix may exist. System ancestors
outside the source root and chosen prefix are trusted. Installation preserves
input bytes; it does not numerically admit them. The study independently checks
the frozen contracts, fixture manifest, probes, and exact implementation hashes.

Known preflight failures leave destination contents untouched. Copying is not
an atomic transaction: disk exhaustion, permission changes, interruption, or
concurrent mutation after preflight can leave a **partial new installation**.
There is no automatic cleanup or rollback. Retain the error and choose another
fresh prefix; remove an incomplete prefix only after identifying it as your own.
An existing contact-reference package is never merged or replaced.

Create report parents before running and keep reports outside the package. The
single-fixture command returns 0 after writing a complete report and nonzero on
rejection; a successful render can atomically replace an ordinary existing
report, so use distinct filenames to retain experiments. The study always
requires a fresh report path. Its status is 0 for `passed`, 1 for `failed`, and 2
for `incomplete` or rejected execution; inspect a retained report when present.
Missing inputs or an admission failure can reject before a report is created.

The study is the fixed 36-fixture, four-factor experiment with 64 independent
probes per fixture. A successful copy, relocation, or individual render does
not establish convergence or resource acceptance. Unknown resident-memory
measurement cannot satisfy the study's resource gate. Numerical acceptance is
separate from a causal streaming implementation, native Engine integration,
physical contact measurements, and instrument fidelity.
