# Install and use the source-leakage tools

`SourceLeakageTools` is an explicit, relocatable local package for compiling,
inspecting and auditioning **synthetic** static source coupling. It contains
the actual offline organ renderer, native leakage probe, bounded benchmark,
standard-library Python compiler, nominal organ profile and two authoring
fixtures. The standalone/VST3 defaults, 47 musical parameters and
`B3CONTROLS4` state remain unchanged.

This layer applies `y[d] = x[d] + sum(gain[d,s] * x[s])` to the same 91 original
source values before contacts and every organ consumer. Its invented fixture
coefficients are dimensionless amplitude ratios, not acquired pickup leakage.
The dry organ still lacks connected scanner, AO-28 and Leslie audio. Packaging
does not establish physical fidelity, whole-interface 1:1 equality, device
deadlines or signed distribution.

## Build and install

Building requires CMake 3.21+, Python 3.10+ and a C++20 compiler. This component
requires no SDL, MIDI or VST3 SDK. From a checkout of the repository, a fresh
Linux/macOS build can be prepared with:

```sh
cmake -S . -B build-leakage -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build-leakage --config Release --parallel 3 \
  --target hammond_render hammond_source_leakage_probe hammond_source_leakage_benchmark
ctest --test-dir build-leakage -C Release --output-on-failure \
  --no-tests=error -R '^python_test_source_leakage_install$'
cmake --install build-leakage --config Release --component SourceLeakageTools \
  --prefix "$PWD/../source-leakage-tools"
```

`hammond_render` builds its `hammond_profile` dependency, producing `nominal.b3p`.
For an existing coordinated development build, its integrator builds those
three targets once and runs the selected CTest. Workers do not start competing
builds. The test configures small private `LANGUAGES NONE` install fixtures from
the actual installers and already-built artifacts; it performs no compilation,
never alters the primary build and uses only temporary installation prefixes.

On Windows, use a developer PowerShell with a supported C++ compiler. The
following commands also work with a multi-configuration generator:

```powershell
cmake -S . -B build-leakage -DCMAKE_BUILD_TYPE=Release `
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build-leakage --config Release --parallel 3 `
  --target hammond_render hammond_source_leakage_probe hammond_source_leakage_benchmark
ctest --test-dir build-leakage -C Release --output-on-failure `
  --no-tests=error -R '^python_test_source_leakage_install$'
cmake --install build-leakage --config Release --component SourceLeakageTools `
  --prefix "$((Get-Location).Path)/../source-leakage-tools"
```

Install the configuration that was built. An unknown multi-configuration name
is rejected before copying metadata. Installation never builds missing inputs,
downloads dependencies or registers a plug-in. Ordinary installation and the
`OfflineTools`/`Standalone` components retain their existing inventories;
`SourceLeakageTools` is `EXCLUDE_FROM_ALL` and must be selected explicitly.

## Exact installed payload

With default install directories, the package has exactly nine regular files:

| Relative to the chosen prefix | Purpose |
| --- | --- |
| `bin/hammond_render` | Actual dry-organ renderer with explicit leakage options |
| `bin/hammond_source_leakage_probe` | Native compiled-profile inspection and one algebra observation |
| `bin/hammond_source_leakage_benchmark` | Bounded optional-path cost characterization |
| `share/hammond-b3-organ/source-leakage/profiles/nominal.b3p` | Compiled nominal organ profile |
| `share/hammond-b3-organ/source-leakage/tools/compile_source_leakage.py` | Self-contained author compiler |
| `share/hammond-b3-organ/source-leakage/data/source-leakage.schema.json` | Authoring schema |
| `share/hammond-b3-organ/source-leakage/data/source-leakage/synthetic-pair-demo-v1.json` | Two signed synthetic coupling edges |
| `share/hammond-b3-organ/source-leakage/data/source-leakage/synthetic-identity-v1.json` | Empty graph for a gain-matched comparison |
| `share/hammond-b3-organ/source-leakage/docs/SOURCE_LEAKAGE_INSTALL.md` | This operating guide |

Windows native executables have `.exe` suffixes. Custom `CMAKE_INSTALL_BINDIR`
and `CMAKE_INSTALL_DATADIR` are supported when both are nonempty relative paths
without parent traversal or list separators. Substitute those configured
directories in the commands below. No source checkout, CMake installation or
build tree is needed to run the relocated payload. Running requires Python
3.10+ for the compiler and the native platform's ordinary C/C++ runtime; this
is not a cross-platform binary archive or a bundle of runtime libraries.

The repository's demonstration builder is not installed: it requires additional
repository sources, contracts and manifests. The following direct installed
workflow needs only these nine files and an empty writable output directory.

## Compile, inspect and render after relocation

The whole prefix can be moved or copied to another ordinary directory on the
same supported platform. Use its new absolute path; commands never infer the
profile or graph from the current working directory. Keep generated WAVs,
compiled graphs and reports outside the installed package.

The POSIX example below uses paths with spaces. Set `leakage_prefix` to the
actual moved directory and choose a new output-directory name:

```sh
leakage_prefix="/absolute/path/Source Leakage Tools"
leakage_package="$leakage_prefix/share/hammond-b3-organ/source-leakage"
mkdir "leakage audition"
cd "leakage audition"

python3 -I -B -S "$leakage_package/tools/compile_source_leakage.py" \
  --input "$leakage_package/data/source-leakage/synthetic-pair-demo-v1.json" \
  --output pair.b3leakage
python3 -I -B -S "$leakage_package/tools/compile_source_leakage.py" \
  --input "$leakage_package/data/source-leakage/synthetic-identity-v1.json" \
  --output identity.b3leakage
"$leakage_prefix/bin/hammond_source_leakage_probe" --input pair.b3leakage

"$leakage_prefix/bin/hammond_render" \
  --profile "$leakage_package/profiles/nominal.b3p" --output pair.wav \
  --frames 96000 --sample-rate 48000 --block-size 64 --seed 1939 \
  --drawbars 008000000 --note 48 --contacts ideal --percussion off \
  --source-leakage pair.b3leakage --leakage-input-gain 0.75 --fail-on-clip
"$leakage_prefix/bin/hammond_render" \
  --profile "$leakage_package/profiles/nominal.b3p" --output identity.wav \
  --frames 96000 --sample-rate 48000 --block-size 64 --seed 1939 \
  --drawbars 008000000 --note 48 --contacts ideal --percussion off \
  --source-leakage identity.b3leakage --leakage-input-gain 0.75 --fail-on-clip
```

For Windows PowerShell, set absolute package/output paths and use the call
operator for native tools:

```powershell
$leakagePrefix = 'C:/Audio Tools/Source Leakage Tools'
$leakagePackage = "$leakagePrefix/share/hammond-b3-organ/source-leakage"
New-Item -ItemType Directory -Path 'leakage audition' -ErrorAction Stop
Set-Location 'leakage audition'
python -I -B -S "$leakagePackage/tools/compile_source_leakage.py" `
  --input "$leakagePackage/data/source-leakage/synthetic-pair-demo-v1.json" `
  --output pair.b3leakage
python -I -B -S "$leakagePackage/tools/compile_source_leakage.py" `
  --input "$leakagePackage/data/source-leakage/synthetic-identity-v1.json" `
  --output identity.b3leakage
& "$leakagePrefix/bin/hammond_source_leakage_probe.exe" --input pair.b3leakage
foreach ($graph in @('pair', 'identity')) {
  & "$leakagePrefix/bin/hammond_render.exe" `
    --profile "$leakagePackage/profiles/nominal.b3p" --output "$graph.wav" `
    --frames 96000 --sample-rate 48000 --block-size 64 --seed 1939 `
    --drawbars 008000000 --note 48 --contacts ideal --percussion off `
    --source-leakage "$graph.b3leakage" --leakage-input-gain 0.75 --fail-on-clip
  if ($LASTEXITCODE -ne 0) { throw "Render failed for $graph" }
}
```

Both WAVs have the same gain, note, seed, registration and duration. The pair
fixture couples source 37 into destination 25 at `+0.0625`, and source 25 into
destination 37 at `-0.03125`. The selected fundamental route for note 48 exposes
destination 25 while the donor's own key is unheld. The pair and empty-graph
files should therefore differ without changing their source-input gain. Listen
to both at the same player level; this is a synthetic demonstration, not an
instrument comparison.

Compiler stdout reports the SHA-256 of exact authoring input and compiled bytes.
The native probe reports the canonical two edges, 91 row sums and one fixed
original-input/output frame. Its authoring digest is explicitly
`file-supplied-unverified`: inspection alone cannot authenticate absent JSON.
The renderer reports schema 5, selected graph identity, explicit gain, row sum,
guarded source bound and output clipping. Retain these receipts alongside file
hashes when reporting an experiment; shell stdout redirection can overwrite an
existing report, so choose new report paths deliberately.

Selecting leakage always requires both `--source-leakage` and
`--leakage-input-gain`, each once. Unsafe headroom rejects before WAV creation;
no gain is silently reduced. `0.75` is safe for the supplied pair, whose maximum
row sum is `0.0625`. For any admitted graph, `0.5` is a conservative example;
the exact mathematical boundary can fail because admission reserves rounding
headroom. Per-source headroom does not prevent every polyphonic output from
clipping, so keep `--fail-on-clip` in comparison commands. An empty graph with
gain `1` is the byte-exact legacy identity path. Omitting both options retains
the existing schema-3/default dry render.

## Optional bounded characterization

After relocation, run:

```sh
"$leakage_prefix/bin/hammond_source_leakage_benchmark" \
  --profile "$leakage_package/profiles/nominal.b3p" \
  --sample-rate 48000 --blocks 256 --repetitions 5 --seed 739
```

PowerShell uses `& "$leakagePrefix/bin/hammond_source_leakage_benchmark.exe"`
with the same options and `"$leakagePackage/profiles/nominal.b3p"`. Its 19 cases
compare core and Engine workloads, including unconfigured, empty, pair and
728-edge paths. Bounds are 1–512 blocks of 64 frames and 1–9 repetitions, with
a cooperative 50-second budget. Reduce the workload if that budget rejects.
JSON identifies the compiled toolchain, workload, checksums and observations.
Timing is machine/load-dependent; there is no CTest timing threshold, measured
callback-deadline claim, stack high-water measurement or historical-build
overhead claim. The installation test uses a tiny functional invocation only.

## Failure protection and continuation

Before its first destination write, installation checks every selected native
executable, nominal profile and source payload for a nonempty nonsymlink file.
It also rejects any existing executable destination or source-leakage package
directory, including files, directories, symlinks and dangling links. A linked
prefix or obstructed/linked destination ancestor inside it is rejected. Existing
ordinary ancestor directories and unrelated files are preserved. Use a fresh
prefix when updating or when `OfflineTools` has already installed
`hammond_render`; this component never overwrites that shared executable name.

Leave `CMAKE_INSTALL_MODE` unset/empty or set it to `COPY`. Link-based modes are
rejected. On POSIX, `DESTDIR` stages the same checks/copies under its combined
prefix. No automatic cleanup occurs: a later I/O failure during copying can
leave a partial new package. Inspect that newly chosen prefix and preserve any
needed evidence before removing only its failed payload and retrying elsewhere.
The preflight is not a transactional installer against concurrent filesystem
writers; use a locally owned destination without concurrent mutation.

Author compilation and WAV publication also refuse existing outputs, including
aliases; retain input JSON/profile/graph files and choose new output names.
Compilation requires an existing writable output parent and a filesystem that
supports the compiler's exclusive hard-link publication. Missing/malformed
inputs reject without publishing a new graph or WAV.

For future development, read repository `AGENTS.md`, the full `docs/PLAN.md`
and the current audio-continuation checkpoint before changing this component.
The next packaging acceptance is the same focused installation suite on each
supported native platform and selected configuration, retaining actual logs and
source/executable/data identities. A passing local suite qualifies those exact
inputs only. Preserve the separate harmonic-composition, physical-acquisition,
UI-reference and signed-release gates. The broader contracts are available in
the repository as `docs/SOURCE_LEAKAGE_CONTRACT.md` and
`docs/SOURCE_LEAKAGE_AUDITION_CONTRACT.md`; this installed guide contains the
complete operating workflow without requiring those files at runtime.
