# Native VST3 CI and bundle evidence

The separate [Native VST3 workflow](../.github/workflows/native-vst3.yml) enables
the optional native build on pushes to `main`, pull requests and manual dispatch.
The ordinary [core workflow](../.github/workflows/ci.yml) and default SDK-free
configuration keep their existing scope. Native CI requires an explicitly
acquired, verified SDK; CMake never fetches it. See [VST3_BUILD.md](VST3_BUILD.md)
for the build contract and [VST3_SPIKE_CONTRACT.md](VST3_SPIKE_CONTRACT.md) for
the supported instrument and host behavior.

## Jobs and dependency boundary

| Runner | Native compiler/configuration | Architecture evidence |
| --- | --- | --- |
| `ubuntu-24.04` | GCC, Unix Makefiles, Release | Actual runner architecture plus ELF header |
| `macos-15` | AppleClang, Unix Makefiles, Release | Actual runner architecture plus Mach-O header/slices |
| `windows-2022` | Visual Studio 2022 MSVC, Release, explicit `-A x64` | Actual runner architecture plus PE DLL header |

The matrix uses `fail-fast: false`, a 35-minute job timeout, read-only repository
contents permission and a separate concurrency group. Checkout retains no Git
credentials. Checkout, Python setup and artifact upload use the same reviewed,
immutable action commits as the core workflow; no new action is introduced.
Python 3.12 runs the repository helpers. The native input aggregate builds with
two parallel jobs; each selected CTest has a 300-second timeout.

The acquisition step calls `tools/acquire_vst3_sdk.py --destination` with a new
`hammond-vst3-sdk` directory under the existing `RUNNER_TEMP` parent, outside the
checkout. It then calls `--verify-existing` on that exact path. The helper checks
the [SDK lock](../data/dependencies/vst3-sdk-lock.json), all five checkout
identities, parent gitlinks, checkout cleanliness, five primary license texts
and the embedded parser identity. SDK source and build output stay separate.
The configure step passes that verified path and `HAMMOND_BUILD_VST3=ON`.
No SDK checkout or third-party source archive is uploaded as a workflow artifact.

## One complete native validation run

CI first builds `hammond_vst3_test_inputs`, the maintained aggregate for the
bundle, validator and every registered native test. It then runs one verbose
CTest pass:

```sh
cmake --build build-native --config Release \
  --target hammond_vst3_test_inputs --parallel 2 --verbose
ctest --test-dir build-native -C Release -V --no-tests=error --timeout 300 \
  -R '^(hammond_vst3_validator|test_native_)' \
  --output-junit /absolute/path/to/native-ci-logs/ctest.xml
```

The ordinary `check_vst3` target remains available for local use. CI's build-only
aggregate allows one CTest invocation to own both verbose output and JUnit,
without maintaining a second list of executable targets. Adding a mandatory
native test requires registering it in the native CMake hooks and preserving
the `test_native_` naming contract. Direct CTest execution does not build missing
executables. An absent selected test set fails through `--no-tests=error`.

The shell uses `set -euo pipefail`; piping through `tee` retains the actual
configure, build or test exit status. Logs are not filtered for selected words,
warnings or successful test summaries. Successful compilation alone does not
qualify a module, and inventory generation does not substitute for validation.

### Read the validator's full result

The first locally built Linux module returned exit 0 with the SDK summary
**47 passed, zero failed**. The same retained output contains nine
`ERROR`-labelled `setupProcessing` rejections at unsupported rates and sixteen
nonfatal teardown diagnostics. Both the summary and these messages are part of
the result; it is not a warning-free SDK gate. The unsupported rates are 22050,
32000, 88200, 192000, 384000, 1234.5678, 12345.678, 123456.78 and 1234567.8 Hz.
The pinned SDK does not add those rejected setup attempts to its failed-test
count. The wrapper's explicit supported rates remain 44100, 48000 and 96000 Hz.

The teardown diagnostics arise from differing SDK test expectations for repeated
deactivation, including skipped float64 processing cases. Preserve the
float32-only/lifecycle contract and all log text; do not modify SDK sources or
expand DSP behavior to silence the harness. The independent
[ABI tests](VST3_ABI_ACCEPTANCE.md) and
[behavior tests](VST3_BEHAVIOR_ACCEPTANCE.md) exercise the actual loaded module
under the declared contract. Their results and source identity must be assessed
alongside the SDK result, as documented in [VST3_BUILD.md](VST3_BUILD.md).

## Retained artifacts

Artifacts have a 14-day retention period. Their names include runner image,
actual runner architecture, Release configuration, source commit and run
attempt. The `diagnostics` artifact retains, when produced:

- Actual checked-out commit/tree, event/run/attempt identifiers, runner and
  image metadata, actual platform/Python identity and configuration.
- The exact selected SDK lock, complete acquisition/verification output,
  CMake/CTest/Python/Git versions, Unix compiler version and compiler identity
  from CMake configuration/cache on every platform.
- Complete configure/build/verbose CTest output, JUnit, CMake cache/configuration
  diagnostics, CTest's last-test/failure logs and the generated bundle path.
- The original build bundle's byte inventory.

The diagnostics upload runs after success or failure when the job has not been
cancelled. A runner acquisition failure or cancelled job may produce no files;
there is no artifact guarantee for work that never ran.

The separate `bundle` artifact is uploaded only after all preceding job steps
succeed. It contains `HammondB3-Release.tar.gz`, `inventory.json` and
`archive.sha256`. Before archiving, CI inventories the build bundle, copies it
to a new temporary staging directory with `copy2`, inventories that copy and
requires identical inventory bytes. The tar archive preserves native file modes
and carries the bundle's module-info data, `VST3_SDK_LICENSE.txt` and component
notices. The archive digest identifies that particular archive; gzip/tar bytes
are not promised to be reproducible across runs. Packaging does not install or
register a plugin in a user or system plugin directory.

PR checkout provenance is the actual event revision, which can be GitHub's
synthetic merge commit. It is not relabelled as the contributor's head commit.
The workflow requires `git rev-parse HEAD` to equal `GITHUB_SHA` before building
and before packaging, and records the source tree. A caller-provided commit in
an inventory is a label with explicitly declared provenance, not independent
binary-to-source attestation.

## Inventory CLI

The stdlib-only [inventory helper](../tools/native_bundle_inventory.py) records
each actual regular file's relative path, size, SHA-256 and mode. It also records
the selected configuration, SDK lock identity, source identity, actual execution
environment and native module header facts. It does not load a plugin.

```sh
python3 tools/native_bundle_inventory.py \
  --bundle /absolute/path/to/HammondB3.vst3 \
  --output /existing/output/directory/inventory.json \
  --configuration Release \
  --source-commit ACTUAL_LOWERCASE_40_HEX_COMMIT
```

For a local archive-plus-overlay build, replace `--source-commit` with
`--source-manifest /absolute/path/to/source-overlay.json`. The report records
the bounded manifest's raw size and SHA-256 without inventing a clean commit
for uncommitted source. `--sdk-lock` and `--project-notices` can explicitly select
the corresponding source inputs; their defaults are this repository's files.

Inputs must be quiescent. The bundle must be a real directory named
`HammondB3.vst3`. Windows reparse points, including directory junctions, reject
at root admission, before descendant traversal and before regular-file reads.
All descendant symlinks, including links that stay inside the
bundle, and all special files reject. The helper rejects case-colliding paths,
unsupported path characters, excessive bounds, missing/empty required resources,
license or notice mismatches and a missing, multiple or unsupported module path.
Additional regular resource files are included in the inventory rather than
silently dropped. This is not a release payload allowlist.

| Bound | Maximum |
| --- | ---: |
| Entries, including directories | 512 |
| Relative path components | 12 |
| UTF-8 relative path bytes | 1024 |
| Individual file | 128 MiB |
| Total regular file bytes | 256 MiB |
| Each required resource, lock, notice or source manifest | 128 KiB |
| Serialized inventory | 1 MiB |

Supported layouts are the SDK's directory bundles: Linux module files under
`Contents/x86_64-linux/` or `Contents/aarch64-linux/`, Windows module files under
`Contents/x86_64-win/` or `Contents/arm64-win/`, and the macOS module at
`Contents/MacOS/HammondB3`. Flat Windows `.vst3` DLLs are outside this contract;
the project's CMake explicitly enables Windows directory bundles. ELF64, PE32+
DLL and thin/universal 64-bit Mach-O headers provide platform/CPU facts; they
must agree with the selected module path. Universal Mach-O slices have bounded,
nonoverlapping extents with matching CPU identities.

The pinned SDK's module-info writer emits trailing commas. Its output is retained
as opaque, byte-identified metadata, not parsed as strict JSON or rewritten to a
different grammar. The SDK lock itself is strict JSON with duplicate/nonfinite
fields rejected; the inventory's small lock checks supplement the full SDK
verifier rather than replacing it.

The output must be a new file outside the bundle, with an existing parent.
Publication writes and flushes a temporary file, then links the complete report
into place without replacing an existing destination. Files, directories and
broken symlinks already at the output path are preserved. A filesystem without
the required hard-link operation fails without a partial output. Before/after
file checks detect ordinary concurrent changes, but do not provide a hostile
filesystem race-proof sandbox.

## Current evidence and next operation

[Assignment 36](development/2026-11-13-pedals/36-native-ci.md) records the actual
local checks: sixteen SDK-free Python methods, CMake test discovery, a separate
successful SDK acquisition/verification, YAML/shell/embedded-Python checks and
inventory/copy/tar checks of the existing Linux module. Synthetic PE/Mach-O
fixtures test parsing and bounds; they are not Windows/macOS plugin runs.

The native workflow had not run when assignment 36 froze; that is its historical
scope. Subsequent [ABI](VST3_ABI_ACCEPTANCE.md), [behavior](VST3_BEHAVIOR_ACCEPTANCE.md),
[automation](VST3_AUTOMATION_REVIEW.md), [concurrency](VST3_CONCURRENCY.md) and
[allocation](VST3_REALTIME.md) gates now execute the actual module. The
[portability review](reviews/PEDAL_NATIVE_PORTABILITY.md) retains the first
platform failures and observed repairs; the [wave-8 hosted audit](reviews/PEDAL_HOSTED_WAVE8_FINAL.md)
identifies the exact later jobs, complete logs and downloaded artifacts. Its
Linux/Windows jobs passed; the initial macOS jobs failed hosted-runner acquisition
with zero execution. Root subsequently requested one targeted retry per job.
A pending or cancelled runner is not an executed compiler/test result.

The new reparse/junction inventory regression belongs to the later wave-9 source.
Inspect its actual Windows output and payload before closing that repair's
platform gate. For every subsequent code checkpoint, observe the separate core
and native jobs and retain exact source/run/artifact identity. The earlier
core-only macOS acquisition failure and successful targeted retry remain in
[PEDAL_RUNNER_AVAILABILITY.md](reviews/PEDAL_RUNNER_AVAILABILITY.md); those events
do not qualify changed native code. Preserve the configured platform coverage
and distinguish runner acquisition from project execution.

These artifacts establish software and payload evidence for the exact tested
revision. Actual DAW compatibility, device deadlines, custom UI, signing,
distribution/runtime dependencies, project-wide rights clearance and measured
instrument fidelity retain their separate gates.
