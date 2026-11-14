# Local installation of capture tools

This is the frozen project-proposed **capture-tools-install-v1** contract. The
`CaptureTools` CMake component copies the offline capture pipeline, its complete
local Python dependency closure, five shape schemas, declared examples and
operating documentation into one movable directory. It does not build or install
the native renderer, standalone application or VST3 plugin. The existing
23-file `OfflineTools` component retains its own inventory and behavior.

This contract was written before installation grading. The assignment evidence
and independent acceptance are retained separately in the calibration session.
The package prepares reproducible M0/M8 engineering work. Installation, successful
replay and synthetic examples establish no acquisition, calibration, permission,
untouched holdout, physical fidelity or production-release qualification.

## Prerequisites and scope

An installed tool needs **Python 3.10 or newer and its standard library**. Invoke
the copied scripts with that interpreter; there is no package installer, native
extension, audio device, network request or source-checkout fallback. Use `-B`
to keep Python from creating bytecode caches inside the installed package.
The source-observing job, study and replay tools require their associated `.py`
files to remain ordinary readable files beside the other copied modules.

Creating the package through the repository's ordinary configuration also needs
**CMake 3.21 or newer and a working C++20 compiler**, because the existing project
configures native targets. `CaptureTools` itself uses no target output and needs
no `cmake --build` step. Configuration and installation do not fetch dependencies.
Keep the selected source checkout quiescent during installation. Using the
optional native SDKs or building any target is a separate choice.

## Configure and install

From the repository root, choose a build directory and a writable local prefix:

```sh
cmake -S . -B build-capture-tools -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --install build-capture-tools --config Release --component CaptureTools --prefix "$HOME/hammond capture"
```

The explicit `--component CaptureTools` selection is required. Every rule in
this component is excluded from an ordinary unqualified `cmake --install`.
Selecting `OfflineTools`, `NativeStandalone` or `NativeVST3` does not select
`CaptureTools`; selecting `CaptureTools` does not select those other components.
No elevated privileges or system prefix is needed.

PowerShell, from a configured compiler environment:

```powershell
cmake -S . -B build-capture-tools -DBUILD_TESTING=ON -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_BUILD_STANDALONE=OFF
cmake --install build-capture-tools --config Release --component CaptureTools --prefix "$env:USERPROFILE\hammond capture"
```

A single-configuration Windows generator also takes
`-DCMAKE_BUILD_TYPE=Release`. The copied payload is configuration independent:
the component has no configuration-filtered target files. `--config Release`
keeps these commands consistent with the surrounding project; it does not
build a Release executable. Different selected configurations copy the same
source/data bytes. This component does not certify a compiler or native runtime.

The package root is:

```text
<prefix>/<CMAKE_INSTALL_DATADIR>/hammond-b3-organ/capture-tools
```

The ordinary `GNUInstallDirs` data directory is `share`. A custom nonempty
relative `CMAKE_INSTALL_DATADIR`, for example `assets/reference`, is supported;
adjust the commands below to that actual directory. The existing project helper
rejects absolute paths, drive prefixes, parent traversal, empty values and CMake
list separators. Ordinary spaces and Unicode in a prefix are supported. The
prefix and package contain no embedded original source/build path needed for
runtime execution. The install script itself still reads its configured source
files while creating the package.

Leave `CMAKE_INSTALL_MODE` unset or set it to `COPY`. Other values are rejected
before component writes; symlink install modes would not create an independent
movable source set. CMake's ordinary `DESTDIR` staging is honored on platforms
where CMake supports it. The presence check uses the same staged destination.
The runtime examples below use the actual final package root, without `DESTDIR`.

## Exact 57-file payload

All names below are relative to the package root. Every source file is copied
unchanged; only the root `README.md` is generated from fixed text by the CMake
module. The lists are explicit: installing the component does not discover new
files through a glob, copy an entire source directory, or include a test/cache.

### Ten Python modules

| Installed path | Role |
| --- | --- |
| `tools/validate_capture.py` | Unchanged capture-v1 declaration admission and optional original file checks. |
| `tools/capture_common.py` | Shared bounded strict JSON and no-clobber report publication. |
| `tools/capture_audio.py` | Complete bounded WAV/raw audio inspection and selected windows. |
| `tools/capture_corpus.py` | Whole-corpus file/audio admission and lineage/split audit. |
| `tools/compare_capture.py` | Numerical comparison and fixed original-byte policy evaluation APIs. |
| `tools/capture_job.py` | One complete fixed file-comparison job. |
| `tools/capture_readiness.py` | Declaration gaps without reading artifact/evidence locators. |
| `tools/capture_study.py` | Ordered bounded study retaining complete job outcomes. |
| `tools/make_capture_demo.py` | Exclusive deterministic creation of the synthetic archive. |
| `tools/verify_capture_report.py` | Full canonical job/study report replay. |

These ten files include all project-local imports of the installed tools. Other
imports are from Python's standard library. Files are copied as ordinary data;
invoke `python3 -B <script>` or the corresponding Windows interpreter explicitly.
There are no interpreter-path wrappers or executable-discovery assumptions.

### Eight schema and declaration files

```text
data/capture.schema.json
data/capture-corpus.schema.json
data/capture-policy.schema.json
data/capture-job.schema.json
data/capture-study.schema.json
data/capture-planned-example.json
data/corpus-planned-example.json
data/capture-policy-synthetic-example.json
```

Schemas describe shapes, not all semantic, byte-identity or physical conditions.
The runtime validators perform their documented additional checks without a
third-party schema library. The planned corpus retains its original relative
binding to the planned capture. It is intentionally inconclusive.

### Sixteen unchanged synthetic demo files

```text
examples/capture-demo/README.md
examples/capture-demo/EXPECTED.json
examples/capture-demo/study.json
examples/capture-demo/job-pass.json
examples/capture-demo/job-inconclusive.json
examples/capture-demo/job-fail.json
examples/capture-demo/policy-pass.json
examples/capture-demo/policy-inconclusive.json
examples/capture-demo/policy-fail.json
examples/capture-demo/corpus/corpus.json
examples/capture-demo/corpus/reference.json
examples/capture-demo/corpus/quarter.json
examples/capture-demo/corpus/half.json
examples/capture-demo/corpus/audio/reference.f32
examples/capture-demo/corpus/audio/quarter.f32
examples/capture-demo/corpus/audio/half.f32
```

This subtree retains exactly 16 files, 32,831 bytes and its original hierarchy.
Every manifest/index/policy/job/study binding continues to refer to its original
bytes. Its three streams contain the literal reference, quarter-offset and
half-offset vectors. The date, operator/session/group identifiers and other
required metadata remain explicitly constructed fixture labels. `EXPECTED.json`
is a literal oracle with `execution: "not_run"`; installation does not execute
or replace it with a report. The actual expected outcomes are listed below.

### Twenty-one documentation files

```text
docs/CAPTURE_FORMAT.md
docs/CAPTURE_PROTOCOL.md
docs/CAPTURE_VALIDATION.md
docs/CAPTURE_COMMON.md
docs/CAPTURE_AUDIO_CONTRACT.md
docs/CAPTURE_AUDIO.md
docs/CAPTURE_CORPUS_CONTRACT.md
docs/CAPTURE_CORPUS.md
docs/CAPTURE_COMPARISON_CONTRACT.md
docs/CAPTURE_COMPARISON.md
docs/CAPTURE_POLICY.md
docs/CAPTURE_JOB_CONTRACT.md
docs/CAPTURE_JOB.md
docs/CAPTURE_READINESS.md
docs/CAPTURE_STUDY.md
docs/CAPTURE_DEMO.md
docs/CAPTURE_REPLAY.md
docs/CAPTURE_TOOLS_INSTALL.md
docs/PLAN.md
docs/CALIBRATION_SCOPE.md
docs/CAPTURE_JOB_REVIEW.md
```

The same repository-shaped layout keeps the operational cross-links between
these documents, copied data and tools useful after moving the package. Historical
development notes, research references and other project links in unchanged
source documents still require the complete repository; this component is not
the complete research archive. Those links do not become runtime dependencies.

### Two root files

`README.md` is a deterministic installed entry point with relative command paths,
the deliberately nonzero example exits and links to the copied guides.
`THIRD_PARTY_NOTICES.md` is copied unchanged from the project. Neither installation
nor retaining notices selects a project-wide license or clears redistribution,
research-source, branding or instrument-acquisition rights. There is no PDF,
native SDK, compiled profile, native binary, test suite or complete development
history in this component.

## Preflight and failure behavior

The component checks **every one of the 57 payload inputs before the first
component destination write**. Each must exist, be nondirectory, have positive
size and not be a symlink as observed by CMake. A missing, empty, directory or
observed symlink input rejects with the offending path. The checks are ordinary
CMake filesystem observations, not a promise to recognize every native reparse
variant or defeat a hostile changing filesystem. A nonregular object with no
positive regular-file payload is not a valid source input.

The complete destination `capture-tools` leaf must be absent at preflight,
including absence of an existing file, directory or dangling symlink. Other
files under the selected prefix and other installed Hammond components may
already exist and are left alone. Reinstalling to the same completed package
root rejects; use another prefix or data directory to retain another version.
All input checks and the destination check precede copying. No generated file is
written under the source checkout; the fixed README is prepared in the build
directory at configuration time.

After successful preflight, the install log announces that copying begins and
that a later failure can retain a partial package without automatic cleanup.
The copy is **not an atomic multi-file transaction**. A later I/O failure may
leave a new partial package; CMake's nonzero result and diagnostics must be kept,
and the partial directory must be inspected before reuse. The installer does
not recursively remove it or attempt to undo copied files. A write that races
after preflight is outside the quiescent-directory contract; ordinary CMake copy
semantics cannot guarantee nonreplacement against every concurrent creator.
Keep the sources and destination quiescent, and never treat a failed command or
the mere presence of a directory as a complete installation.

The generated install manifest records copied paths. It is not a signed release
manifest, proof that all bytes were executed, or a substitute for independent
inventory and relocation acceptance. A cancelled install may leave a partial
new package and must not be reported as successful.

## Execute from a moved package

Move the complete `capture-tools` directory or its containing prefix. Keep all
ten modules together; an individual copied CLI file is not the dependency
closure. Use the actual new root in `hammond_capture`, and choose an existing
separate writable directory for fresh reports:

```sh
hammond_capture="$HOME/hammond moved/share/hammond-b3-organ/capture-tools"
hammond_reports="$HOME/hammond reports"
mkdir -p "$hammond_reports"
python3 -B "$hammond_capture/tools/validate_capture.py" --input "$hammond_capture/data/capture-planned-example.json"
python3 -B "$hammond_capture/tools/capture_readiness.py" --input "$hammond_capture/data/capture-planned-example.json"
python3 -B "$hammond_capture/tools/capture_corpus.py" --input "$hammond_capture/data/corpus-planned-example.json"
python3 -B "$hammond_capture/tools/capture_corpus.py" --input "$hammond_capture/examples/capture-demo/corpus/corpus.json" --check-files --check-audio
```

Expected exits are respectively **0, 3, 3, 0**. Readiness of a plan stays planned;
an unassigned corpus with no acquired stream stays inconclusive. Run these
commands separately or record each expected code in a harness. A nonzero outcome
must not disappear behind a success-only shell chain.

Execute the fixed three jobs and mixed-result study with fresh output names:

```sh
python3 -B "$hammond_capture/tools/capture_job.py" --input "$hammond_capture/examples/capture-demo/job-pass.json" --output "$hammond_reports/pass.json"
python3 -B "$hammond_capture/tools/capture_job.py" --input "$hammond_capture/examples/capture-demo/job-inconclusive.json" --output "$hammond_reports/inconclusive.json"
python3 -B "$hammond_capture/tools/capture_job.py" --input "$hammond_capture/examples/capture-demo/job-fail.json" --output "$hammond_reports/failed.json"
python3 -B "$hammond_capture/tools/capture_study.py" --input "$hammond_capture/examples/capture-demo/study.json" --output "$hammond_reports/study.json"
```

Expected exits are **0, 3, 1, 1**. Every valid completed result remains a complete
report. The study preserves one pass, one inconclusive and one failure. The
deliberate failure verifies retained outcomes; no bound should be relaxed to
make it pass. Report publication requires an existing parent and a filesystem
supporting hard links. Existing output files are preserved.

Replay the failed result and the mixed study under the same coherent sources
and runtime:

```sh
python3 -B "$hammond_capture/tools/verify_capture_report.py" --kind job --input "$hammond_capture/examples/capture-demo/job-fail.json" --report "$hammond_reports/failed.json" --output "$hammond_reports/failed-replay.json"
python3 -B "$hammond_capture/tools/verify_capture_report.py" --kind study --input "$hammond_capture/examples/capture-demo/study.json" --report "$hammond_reports/study.json" --output "$hammond_reports/study-replay.json"
```

Both are expected to exit **0** with `status: "match"`, while retaining the
underlying `failed` engineering status. A different Python/platform/source
identity may produce `mismatch`; the original report remains unchanged. Replay
requires original canonical report bytes, complete original inputs and quiescent
sources. It does not authenticate when or how an earlier report was produced.

To create another independent copy of the declared synthetic input archive,
choose a nonexistent child under an existing parent:

```sh
python3 -B "$hammond_capture/tools/make_capture_demo.py" --output "$hammond_reports/new-demo"
```

This exits 0 and returns an inventory with `execution: "not_run"`. The installed
demo already exists, so generating into its directory must reject. Inventory
creation is not job execution. The unchanged retained demo can be read directly.

PowerShell uses the same script arguments and paths, for example:

```powershell
$hammondCapture = Join-Path $env:USERPROFILE 'hammond moved\share\hammond-b3-organ\capture-tools'
$hammondReports = Join-Path $env:USERPROFILE 'hammond reports'
New-Item -ItemType Directory -Force $hammondReports | Out-Null
python -B "$hammondCapture\tools\capture_study.py" --input "$hammondCapture\examples\capture-demo\study.json" --output "$hammondReports\study.json"
```

The study's expected `$LASTEXITCODE` is 1. Invoke the replay command separately
with `--kind study`, the same original input and that report. Normal JSON output
is UTF-8 with LF through the tools' binary stream writers; use explicit
`--output` when retaining a report to avoid a shell's text-redirection encoding.

## Independent installation acceptance and continuation

Acceptance should configure a coherent source, install this component without
building native targets, check the exact 57-file inventory and every copied
source/data byte, move the package, make its original private source/build paths
unavailable, and execute installed tools from a foreign working directory.
Remove source/build/test Python-path environment assumptions. Check the literal
vectors, complete report fields and all deliberately nonzero outcomes rather
than treating producer statuses as the only oracle.

Also exercise a custom relative data directory, ordinary Unicode/space paths,
repeated configuration, explicitly selected configurations, COPY/unset versus
rejected link modes, missing/empty/directory/observed-link payloads, and an
existing destination. Preflight rejects must preserve all existing prefix
contents. Fault probes must mutate private source copies, never live shared
inputs. Independently confirm the unchanged 23-file `OfflineTools` component
and its own maintained relocation check. Native platform checks remain separate
from Linux pathname/stream simulations.

Record exact source/inventory hashes, CMake/Python versions, actual commands,
results, failures and unrun gates. Later source edits change the identities
observed in job/study/replay reports and require the affected checks again.
Root integrates accepted evidence into current status, next steps, handoff and
the actual session ledger, then commits and publishes under the standing
non-force workflow. Local packaging alone establishes no hosted CI, native
device/host, permission, physical measurement or full-release pass.
