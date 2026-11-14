# Interface CI inventory — A39

**Result: the configured standalone inventory and package declarations agree.**
The only workflow change makes three implemented suites mandatory in the
discovery guard. This is static inspection and read-only CTest discovery, not
a new runtime or hosted pass. The [machine-readable report](../development/2026-11-14-interface-continuation/reports/a39-ci-inventory.json)
records source hashes, exact names, commands and limits.

## Source and test coverage

The inspected published baseline is
`aea58bb85bc66a5feaff66a0b8a388e7c3f9e630`, tree
`19e61b344fc8dfd3146588a6058994ff351d2cc5`. A34/A36 have separate working
changes; A39 did not execute their application. Comparing the complete workflow
to that baseline confirms that only the required-name literal changed.

Read-only discovery in the existing MIDI-on Linux Release `build-native` reports
**147 configured tests, including 38 selected by `^test_standalone_`**. The
required set grows from 18 to 21, with no missing or duplicate registered names:

| Added explicit requirement | Registration and acceptance input |
| --- | --- |
| `test_standalone_workspace_raster` | A25 native target, explicitly appended to the aggregate build target. |
| `test_standalone_workspace_continuity` | A26 ordinary C++ test glob creates its target, registration and aggregate dependency. |
| `test_standalone_scaled_view` | A28 native target, explicitly appended to the aggregate build target. |

These are exactly the three additions since A24's 35-test discovery. A24's eight
new requirements remain present, including the plural
`test_standalone_workspaces_author`. Existing `test_standalone_drawing` and
`test_standalone_preset_raster` each remain one registered suite despite expanded
cases. Both remain selected by the broad filter; drawing already had an explicit
requirement. No duplicate target or test was added.

The workflow still builds `hammond_standalone_test_inputs` before discovery,
requires the literal subset, and runs the complete standalone filter with
`--no-tests=error`, one worker and the existing 180-second default timeout.
Per-test timeouts are unchanged. All three workflow YAML files parse with
PyYAML; six standalone and two VST3 Python blocks parse with `ast.parse`; all
28 shell run blocks pass `bash -n`.

## Platforms and package

| Standalone job | MIDI backend | Exact payload |
| --- | --- | ---: |
| Ubuntu 24.04 / GCC | ALSA | 19 files |
| macOS 15 / AppleClang | CoreMIDI | 19 files |
| Windows 2022 / MSVC x64 | WinMM | 19 files |
| Ubuntu 24.04 / GCC, MIDI disabled | unavailable | 15 files |

The workflow expected mapping, `InstallStandalone.cmake` and independent install
test inventory agree: one executable plus fourteen common metadata files, with
four additional RtMidi records when enabled. Six setup/operation/model guides,
the notices, SDL2 and DejaVu licenses are common; the RtMidi license is conditional.
All guide/notice sources exist and all three license hashes match their locks.
The report lists every path and source hash. The declared names also match A24's
enabled and A29's separately compiled disabled-package records.

All-input metadata preflight, exact file/directory admission, byte/mode and
archive checks, capability/source provenance, dependency re-verification,
always-upload diagnostics and success-only package upload remain unchanged.
The ordinary CI workflow covers its SDK-free Release matrix and Linux
sanitizers. The separate VST3 workflow covers its validator/native filter on
the same three platforms; neither substitutes for standalone qualification.

## Reproduce and qualify

From the repository, discover without configuring, building or executing tests:

```sh
/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/ctest \
  --test-dir ../build-native -C Release --show-only=json-v1
git diff --check -- .github/workflows/standalone.yml
```

[Retained discovery](../development/2026-11-14-interface-continuation/reports/a39-ctest-discovery.json)
contains all names and selected commands/properties. Counts identify this local
configuration only. A24/A29 runtime results retain their earlier overlay and
binary identities; changed guides or executables require fresh package acceptance.
The eleven successful hosted jobs at `5d81199` qualify the platform repair only.
A39 did not inspect or dispatch `aea58` jobs. A48/A58 own later hosted evidence;
physical devices, accessibility, deadlines, signing and fidelity remain separate.
