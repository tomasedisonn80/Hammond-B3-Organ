# Install and relocate ContactGridConversionTools

`ContactGridConversionTools` is an explicit, copy-only CMake component for the
offline binary64-to-grid converter. It installs **exactly five files** and runs
with Python **3.10 or later**, using only the standard library. It does not
install the native probe or change the original 48-file
[ContactReferenceTools package](CONTACT_REFERENCE_INSTALL.md).

The [conversion contract](CONTACT_GRID_CONVERSION_CONTRACT.md) defines the
finite synthetic trajectory, certificate and refusal policy. Installing this
tool does not connect contact trajectories to Engine audio or establish audio
accuracy, physical calibration or live callback performance.

## Configure and install

From a clean repository checkout, use CMake **3.21 or later** and the normal
repository configuration prerequisites, including a C++20 compiler. No native
target needs to be built for this component:

```sh
cmake -S . -B ../build-contact-grid-conversion \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --install ../build-contact-grid-conversion --config Release \
  --component ContactGridConversionTools \
  --prefix "$PWD/../hammond-contact-grid"
```

An already configured build of this source can also supply the install rules.
The component's script does not build inputs, download dependencies, execute
the converter, or register an application. `--config Release` also works with
multi-configuration builds; the five source payloads are configuration-independent.

Choose a writable prefix whose package directory does not already exist.
Ordinary directories and unrelated files in the prefix can remain in place.
The package itself is never replaced or merged, even if it is empty. Use a new
prefix for another version and retain the original installation when its results
remain evidence.

All rules, including their preflight, have `EXCLUDE_FROM_ALL`. Omitting
`--component ContactGridConversionTools` does not install or validate this
payload. Other components retain their own behavior.

## Exact installed layout

With the default `CMAKE_INSTALL_DATADIR=share`, the package is:

```text
<prefix>/share/hammond-b3-organ/contact-grid-conversion/
```

| Relative file | Purpose |
| --- | --- |
| `tools/contact_grid_conversion.py` | Exact numerical conversion and strict certificate reconstruction |
| `tools/convert_contact_grid.py` | Strict file-to-file command and atomic certificate publication |
| `tools/contact_switching_io.py` | Original input parsing and filesystem admission |
| `tools/fractional_contact_reference.py` | Original canonical case definitions and validation |
| `docs/CONTACT_GRID_CONVERSION_CONTRACT.md` | Admitted conversion contract hashed by the command |

Files are ordinary copies, with the same bytes as the selected source checkout.
The rules use `install(FILES)`, so POSIX payload permissions are normalized to
0644. Invoke Python explicitly. The relative `tools/` and `docs/` layout is
required by the command's imports and contract provenance.

No fixture, native executable, generated certificate, bytecode cache, additional
guide, manifest or unlisted sibling is part of this five-file package. Keep input
fixtures and output certificates outside the installed directory. This guide
remains a repository document and is deliberately not a sixth payload file.

Set `CMAKE_INSTALL_DATADIR` during configuration to choose another **nonempty
relative** data directory. Forward and backward separators are normalized by
the component. Absolute paths, drive-prefixed paths, parent traversal and CMake
list separators are rejected. For example, `resources/contact-data` changes the
package root to `<prefix>/resources/contact-data/hammond-b3-organ/contact-grid-conversion`.
On POSIX systems, `DESTDIR` staging is interpreted before destination preflight.

## Run a retained synthetic input

The repository contains the separate original fixture corpus. Copy an input to
an external working directory before removing or moving the checkout:

```sh
mkdir -p ../contact-grid-work
cp data/contact-switching/reference-v1/F02-48000-v1.json ../contact-grid-work/
python3 -B \
  ../hammond-contact-grid/share/hammond-b3-organ/contact-grid-conversion/tools/convert_contact_grid.py \
  --input ../contact-grid-work/F02-48000-v1.json \
  --output ../contact-grid-work/F02-48000-grid-certificate.json
```

On Windows, use the installed Python 3.10+ interpreter's command name and the
corresponding paths. The CLI requires each of `--input` and `--output` exactly
once; it does not accept stdin/stdout sentinels, abbreviated flags or a help-only
success mode. Create the output's parent directory first.

A successful conversion is silent and exits **0**. It publishes one complete
JSON certificate using the transaction in the contract. A mathematical,
admission or precommit operation refusal exits **2** and emits one bounded JSON
line to an available stdout sink. Precommit interruption exits **130**.
Successful replacement is the commit point and cannot subsequently be reported
as an unpublished refusal. A successful invocation may replace an existing
admitted regular output; choose new names when preserving earlier experiments.

Some original inputs are deliberately refused because rounding changes an event
relationship. In particular, F09 is retained as a refusal at all three rates.
A refusal is not a request to edit the fixture until it passes. The converter
does not produce an audio file or run the native C++ grid probe.

## Relocation and provenance

Move or copy the **complete package**, keeping its internal layout. No original
checkout, build cache or C++ executable is needed at runtime. For example:

```sh
mv ../hammond-contact-grid ../hammond-contact-grid-moved
python3 -B \
  ../hammond-contact-grid-moved/share/hammond-b3-organ/contact-grid-conversion/tools/convert_contact_grid.py \
  --input ../contact-grid-work/F02-48000-v1.json \
  --output ../contact-grid-work/F02-48000-moved-certificate.json
```

The command hashes its actual four source files and contract, and records the
original input byte identity and Python version. Installation does not pin a
global release hash: it copies the selected checkout's bytes, which the
certificate identifies. Retain the corresponding source revision and tests
when using those identities as evidence.

Use a fresh, trusted, unchanged package for a reproducible run. A new component
installation contains no bytecode caches. Python `-B` prevents writing caches
but does **not** prevent reading an existing timestamp-valid cache; adding or
altering cached code can therefore break the correspondence between disk source
hashes and executing code. These hashes are source provenance, not authentication
of a hostile interpreter or modified runtime. The separate pure encoder can
check reconstructed certificate facts, but cannot authenticate original file
bytes that were never supplied to it.

## Preflight and failure behavior

Before the first destination write, the selected component requires all five
source files to be nonempty, nonsymlink file inputs. It checks their ancestors
through the component's source root for ordinary directories. It also rejects
an existing package and linked or file-valued destination ancestors inside the
effective prefix, including the prefix itself. System ancestors outside those
declared roots remain trusted.

`CMAKE_INSTALL_MODE` must be unset, empty or exactly `COPY`. Link-producing and
fallback link modes are rejected. The new component uses its own variable
namespace and does not alter the original reference install rules or inventory.

Preflight failures preserve destination contents. This is not an atomic package
installer: a later disk or copy failure can leave a partial **new** package.
There is no automatic cleanup or rollback, and no claim of protection against
hostile concurrent directory replacement or power-loss durability. Preserve the
diagnostic and inspect the failed new destination before choosing another prefix.

## Executed implementation check and next acceptance

The runtime continuation additionally repairs an observed Windows relocation
failure: direct CLI startup removes automatic empty search-path entries before
importing its dependencies, so a `json.py` in the working directory cannot be
selected through that entry. Its script directory and explicitly configured
search paths retain their normal behavior. The installer regression injects the
same startup entry on every platform and requires the installed certificate to
match the source certificate exactly. The [failure and repair witness](development/2026-11-16-runtime-continuation/reports/windows-cwd-import-repair.json)
retains original failure, repaired success and local affected tests; the current
session records subsequent exact-source hosted qualification separately.

The [A23 authoring smoke](development/2026-11-16-conversion-material/reports/A23-install-smoke.json)
used the real installer inside a small private `LANGUAGES NONE` project. Its
**19 process invocations passed in 2.630 seconds**. It verified every missing
payload against absent and existing prefixes, ordinary/unknown component
isolation, representative symlink and noncopy refusals, exact five-file copying,
preservation of an existing package, and a real relocated F02 conversion with
the private source/build removed. Installed execution left the package unchanged
and reproduced all five expected provenance hashes. All original 48 reference
payloads and their installer matched the initial base throughout this check.

The [reproducer](development/2026-11-16-conversion-material/reports/A23-install-smoke.py)
accepts `--report <fresh-path.json>` and refuses to overwrite evidence. It is an
implementation smoke, separate from A30's planned independent installation test
matrix and root's exact-source hosted qualification. No native build or real
device was involved. Later source changes require affected requalification.
